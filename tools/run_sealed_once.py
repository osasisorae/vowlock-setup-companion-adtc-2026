#!/usr/bin/env python3
"""Run the frozen selected model on the sealed fixtures exactly once."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from companion.local_model import LlamaServer
from companion.model_experiment import run_model_experiment


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"
START_MARKER = RESULTS / "sealed-run-started.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_inputs(model: Path) -> dict:
    selection = json.loads((ROOT / "benchmarks/model-selection.json").read_text())
    expected_model_hash = selection["candidate"]["sha256"]
    actual_model_hash = sha256(model)
    if actual_model_hash != expected_model_hash:
        raise SystemExit(
            f"selected model hash mismatch: expected {expected_model_hash}, found {actual_model_hash}"
        )

    prompt_manifest = json.loads((ROOT / "prompts/MANIFEST.json").read_text())
    for item in prompt_manifest["files"]:
        path = ROOT / item["path"]
        actual = sha256(path)
        if actual != item["sha256"]:
            raise SystemExit(f"frozen prompt hash mismatch: {item['path']}")

    sealed_manifest = json.loads((ROOT / "fixtures/sealed-manifest.json").read_text())
    sealed_dir = ROOT / "fixtures/sealed"
    actual_names = sorted(path.name for path in sealed_dir.glob("*.json"))
    expected_names = sorted(item["path"] for item in sealed_manifest["files"])
    if actual_names != expected_names:
        raise SystemExit("local sealed fixture names do not match the frozen manifest")
    for item in sealed_manifest["files"]:
        if sha256(sealed_dir / item["path"]) != item["sha256"]:
            raise SystemExit(f"sealed fixture hash mismatch: {item['path']}")

    return {
        "model_sha256": actual_model_hash,
        "prompt_manifest_sha256": sha256(ROOT / "prompts/MANIFEST.json"),
        "sealed_manifest_sha256": sha256(ROOT / "fixtures/sealed-manifest.json"),
        "sealed_aggregate_sha256": sealed_manifest["aggregate_sha256"],
        "sealed_case_count": sealed_manifest["case_count"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=ROOT / "model/selected-model.gguf")
    parser.add_argument("--output", type=Path, default=RESULTS / "q4-sealed-once.json")
    parser.add_argument("--server", required=True, type=Path)
    parser.add_argument("--port", type=int, default=32901)
    args = parser.parse_args()

    if START_MARKER.exists():
        raise SystemExit(
            f"sealed evaluation has already started; refusing a second run: {START_MARKER}"
        )

    verified = verify_frozen_inputs(args.model)
    RESULTS.mkdir(parents=True, exist_ok=True)
    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = "unavailable"

    marker = {
        "status": "started",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "output": str(args.output),
        **verified,
    }
    START_MARKER.write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n")

    protocol = json.loads((ROOT / "experiment-protocol.json").read_text())
    prompts = {
        "ordinary_one_shot": (ROOT / "prompts/ordinary-one-shot-v1.txt").read_text(),
        "bounded_one_shot": (ROOT / "prompts/bounded-one-shot-v1.txt").read_text(),
        "adaptive_repair": (ROOT / "prompts/adaptive-repair-v1.txt").read_text(),
    }
    response_schema = json.loads((ROOT / "schemas/explanation.schema.json").read_text())
    log_path = RESULTS / f"server-{args.model.stem}-sealed.log"

    with LlamaServer(
        binary=args.server,
        model=args.model,
        port=args.port,
        protocol=protocol,
        log_path=log_path,
    ) as server:
        result = run_model_experiment(
            server=server,
            fixture_target=ROOT / "fixtures/sealed",
            prompts=prompts,
            response_schema=response_schema,
            checkpoint_path=args.output,
            required_split="sealed",
        )

    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    marker.update(
        {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "output_sha256": sha256(args.output),
            "summary": result["summary"],
        }
    )
    START_MARKER.write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 1 if (
        result["summary"]["ordinary_terminal_failures"]
        or not result["summary"]["adaptive_automatic_safety_gate_passed"]
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main())
