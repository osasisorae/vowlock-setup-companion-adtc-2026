"""Pinned llama.cpp server integration for development experiments.

The server binds to loopback, holds one GGUF in memory, and returns text only.
It has no device-control tools and cannot authorize a state transition.
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class LocalModelError(RuntimeError):
    """Raised when the pinned local runtime cannot serve a response."""


@dataclass(frozen=True)
class GenerationResult:
    content: str
    elapsed_seconds: float
    prompt_tokens: int | None
    completion_tokens: int | None
    prompt_tokens_per_second: float | None
    completion_tokens_per_second: float | None
    exceeded_attempt_time_limit: bool


def build_user_message(sanitized: dict[str, Any]) -> str:
    """Render the shared user input without labels or hidden fixture fields."""
    return (
        f"Novice question:\nPlease explain this checkpoint: {sanitized['title']}\n\n"
        "Sanitized fact packet:\n"
        + json.dumps(sanitized, sort_keys=True, separators=(",", ":"))
    )


def parse_json_object(content: str) -> dict[str, Any]:
    """Parse exactly one JSON object; Markdown fences are intentionally invalid."""
    stripped = content.strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise LocalModelError("INVALID_JSON") from exc
    if not isinstance(value, dict):
        raise LocalModelError("INVALID_RESPONSE_CONTRACT")
    return value


class LlamaServer:
    """Manage one CPU-only llama-server process and its loopback API."""

    def __init__(
        self,
        *,
        binary: Path,
        model: Path,
        port: int,
        protocol: dict[str, Any],
        log_path: Path,
    ) -> None:
        self.binary = binary
        self.model = model
        self.port = port
        self.protocol = protocol
        self.log_path = log_path
        self.process: subprocess.Popen[bytes] | None = None
        self._log_handle = None
        self.load_seconds: float | None = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def command(self) -> list[str]:
        runtime = self.protocol["runtime"]
        return [
            str(self.binary),
            "--model", str(self.model),
            "--host", "127.0.0.1",
            "--port", str(self.port),
            "--threads", str(runtime["threads"]),
            "--threads-batch", str(runtime["threads"]),
            "--ctx-size", str(runtime["context_tokens"]),
            "--batch-size", str(runtime["batch_size"]),
            "--parallel", "1",
            "--gpu-layers", "0",
            "--jinja",
            "--reasoning", "off",
            "--reasoning-budget", "0",
            "--metrics",
        ]

    def start(self) -> float:
        if self.process is not None:
            raise LocalModelError("server already started")
        if not self.binary.is_file():
            raise LocalModelError(f"llama-server not found: {self.binary}")
        if not self.model.is_file():
            raise LocalModelError(f"model not found: {self.model}")

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log_handle = self.log_path.open("wb")
        started = time.perf_counter()
        self.process = subprocess.Popen(
            self.command(),
            stdin=subprocess.DEVNULL,
            stdout=self._log_handle,
            stderr=subprocess.STDOUT,
        )
        deadline = started + self.protocol["resource_gates"]["max_model_load_seconds"]
        while time.perf_counter() < deadline:
            if self.process.poll() is not None:
                return_code = self.process.returncode
                self.stop()
                raise LocalModelError(f"llama-server exited {return_code} during load")
            try:
                with urllib.request.urlopen(f"{self.base_url}/health", timeout=1) as response:
                    if response.status == 200:
                        self.load_seconds = time.perf_counter() - started
                        return self.load_seconds
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.1)
        self.stop()
        raise LocalModelError("model load exceeded the frozen time limit")

    def generate(
        self,
        *,
        system_prompt: str,
        user_message: str,
        response_schema: dict[str, Any] | None = None,
    ) -> GenerationResult:
        if self.process is None or self.process.poll() is not None:
            raise LocalModelError("server is not running")
        runtime = self.protocol["runtime"]
        generation = self.protocol["generation"]
        payload = {
            "model": self.model.name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": generation["max_tokens_per_attempt"],
            "temperature": runtime["temperature"],
            "top_p": runtime["top_p"],
            "seed": runtime["seed"],
            "stream": False,
        }
        if response_schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"schema": response_schema},
            }
        request = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        attempt_limit = generation["max_seconds_per_attempt"]
        try:
            with urllib.request.urlopen(
                request,
                # The protocol gate remains attempt_limit. The longer transport
                # window exists only to retain the completed over-budget output.
                timeout=generation["adaptive_max_seconds"],
            ) as response:
                body = json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise LocalModelError("generation request failed") from exc
        elapsed = time.perf_counter() - started
        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LocalModelError("runtime returned an invalid response envelope") from exc
        usage = body.get("usage", {})
        timings = body.get("timings", {})
        return GenerationResult(
            content=content,
            elapsed_seconds=elapsed,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            prompt_tokens_per_second=timings.get("prompt_per_second"),
            completion_tokens_per_second=timings.get("predicted_per_second"),
            exceeded_attempt_time_limit=elapsed > attempt_limit,
        )

    def stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.process = None
        if self._log_handle is not None:
            self._log_handle.close()
            self._log_handle = None

    def __enter__(self) -> "LlamaServer":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()
