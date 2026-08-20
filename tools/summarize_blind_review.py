#!/usr/bin/env python3
"""Validate and unblind a completed local Q4/Q8 review."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KEY = ROOT / "review" / "local" / "blind-review-key.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("response", type=Path)
    parser.add_argument("--key", type=Path, default=DEFAULT_KEY)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "human-review-results.json")
    args = parser.parse_args()

    response = load(args.response)
    key = load(args.key)
    require(response.get("review_version") == key.get("review_version") == "1.0", "review versions do not match")
    require(response.get("blind") is True, "response is not marked blind")
    require(bool((response.get("reviewer") or {}).get("name", "").strip()), "reviewer name is required")
    require(set(response.get("cases", {})) == set(key.get("cases", {})), "review case IDs do not match the key")

    totals = {
        model: {"factual_points": 0, "clarity": [], "helpfulness": [], "factual_flags": 0}
        for model in ("q4", "q8")
    }
    preferences: Counter[str] = Counter()
    per_case = []
    for case_id in sorted(key["cases"]):
        blind = response["cases"][case_id]
        require(blind.get("preference") in {"A", "B", "Tie"}, f"{case_id}: preference is incomplete")
        unblinded = {}
        for label in ("A", "B"):
            model = key["cases"][case_id][label]
            rating = (blind.get("responses") or {}).get(label, {})
            factual = rating.get("factual")
            clarity = rating.get("clarity")
            helpfulness = rating.get("helpfulness")
            require(factual in {0, 1, 2}, f"{case_id}/{label}: factual rating is invalid")
            require(clarity in {1, 2, 3, 4, 5}, f"{case_id}/{label}: clarity rating is invalid")
            require(helpfulness in {1, 2, 3, 4, 5}, f"{case_id}/{label}: helpfulness rating is invalid")
            totals[model]["factual_points"] += factual
            totals[model]["clarity"].append(clarity)
            totals[model]["helpfulness"].append(helpfulness)
            totals[model]["factual_flags"] += int(factual < 2)
            unblinded[model] = rating
        preference = blind["preference"]
        winner = "tie" if preference == "Tie" else key["cases"][case_id][preference]
        preferences[winner] += 1
        per_case.append({
            "scenario_id": case_id,
            "ratings": unblinded,
            "preference": winner,
            "note": blind.get("note", ""),
        })

    summaries = {}
    for model, values in totals.items():
        summaries[model] = {
            "factual_points": values["factual_points"],
            "factual_points_available": 22,
            "factual_flags": values["factual_flags"],
            "mean_clarity": round(sum(values["clarity"]) / len(values["clarity"]), 3),
            "mean_helpfulness": round(sum(values["helpfulness"]) / len(values["helpfulness"]), 3),
            "preference_wins": preferences[model],
        }

    result = {
        "result_version": "1.0",
        "completed_at": response["completed_at"],
        "review_was_blind": True,
        "reviewer": response["reviewer"],
        "review_type": response.get("review_type", "unspecified"),
        "methodology_note": response.get("methodology_note", ""),
        "source_hashes": key["source_hashes"],
        "cases_reviewed": len(per_case),
        "summary": summaries,
        "ties": preferences["tie"],
        "per_case": per_case,
        "sealed_cases_opened": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    print(f"ties={result['ties']} output={args.output}")


if __name__ == "__main__":
    main()
