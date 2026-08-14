#!/usr/bin/env python3
"""Run the frozen model variants on development fixtures only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from companion.local_model import LlamaServer
from companion.model_experiment import run_development_experiment


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--fixtures", type=Path, default=ROOT / "fixtures" / "development")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--server",
        type=Path,
        default=Path("/Users/Macintosh/.adtc-tooling/llama.cpp/build/bin/llama-server"),
    )
    parser.add_argument("--port", type=int, default=32900)
    args = parser.parse_args()

    protocol = json.loads((ROOT / "experiment-protocol.json").read_text(encoding="utf-8"))
    prompts = {
        "ordinary_one_shot": (ROOT / "prompts/ordinary-one-shot-v1.txt").read_text(encoding="utf-8"),
        "bounded_one_shot": (ROOT / "prompts/bounded-one-shot-v1.txt").read_text(encoding="utf-8"),
        "adaptive_repair": (ROOT / "prompts/adaptive-repair-v1.txt").read_text(encoding="utf-8"),
    }
    response_schema = json.loads((ROOT / "schemas/explanation.schema.json").read_text(encoding="utf-8"))
    log_path = ROOT / "benchmarks" / "results" / f"server-{args.model.stem}.log"
    with LlamaServer(
        binary=args.server,
        model=args.model,
        port=args.port,
        protocol=protocol,
        log_path=log_path,
    ) as server:
        result = run_development_experiment(
            server=server,
            fixture_target=args.fixtures,
            prompts=prompts,
            response_schema=response_schema,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 1 if (
        result["summary"]["ordinary_terminal_failures"]
        or not result["summary"]["adaptive_automatic_safety_gate_passed"]
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main())
