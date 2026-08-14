#!/usr/bin/env python3
"""Run one bounded smoke test against a development fixture only."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from companion.evaluator import evaluate_scenario, load_scenario
from companion.experiment import sanitize_case, score_explanation
from companion.local_model import LlamaServer, build_user_message, parse_json_object
from companion.model_experiment import bind_response_schema


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument(
        "--server",
        type=Path,
        default=Path("/Users/Macintosh/.adtc-tooling/llama.cpp/build/bin/llama-server"),
    )
    parser.add_argument("--port", type=int, default=32900)
    args = parser.parse_args()

    scenario = load_scenario(args.fixture)
    if scenario["split"] != "development":
        parser.error("smoke_model.py accepts development fixtures only")

    protocol = json.loads((ROOT / "experiment-protocol.json").read_text(encoding="utf-8"))
    response_schema = json.loads((ROOT / "schemas/explanation.schema.json").read_text(encoding="utf-8"))
    system_prompt = (ROOT / "prompts/bounded-one-shot-v1.txt").read_text(encoding="utf-8")
    decision = evaluate_scenario(copy.deepcopy(scenario))
    sanitized = sanitize_case(scenario, decision)
    log_path = ROOT / "benchmarks" / "results" / f"server-{args.model.stem}.log"

    with LlamaServer(
        binary=args.server,
        model=args.model,
        port=args.port,
        protocol=protocol,
        log_path=log_path,
    ) as server:
        generation = server.generate(
            system_prompt=system_prompt,
            user_message=build_user_message(sanitized),
            response_schema=bind_response_schema(
                response_schema,
                sanitized,
                variant="bounded_one_shot",
            ),
        )
        load_seconds = server.load_seconds

    parsed = parse_json_object(generation.content)
    score = score_explanation(scenario, decision, parsed, provenance="local_model")
    print(json.dumps({
        "model": args.model.name,
        "fixture": str(args.fixture),
        "load_seconds": load_seconds,
        "generation_seconds": generation.elapsed_seconds,
        "prompt_tokens": generation.prompt_tokens,
        "completion_tokens": generation.completion_tokens,
        "prompt_tokens_per_second": generation.prompt_tokens_per_second,
        "completion_tokens_per_second": generation.completion_tokens_per_second,
        "exceeded_attempt_time_limit": generation.exceeded_attempt_time_limit,
        "response": parsed,
        "score": score,
    }, indent=2, sort_keys=True))
    return 1 if score["hard_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
