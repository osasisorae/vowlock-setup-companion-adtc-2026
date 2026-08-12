"""Pure deterministic evaluation of synthetic provisioning scenarios.

The evaluator never reads fixture labels while deciding. Labels exist only so the
test harness can compare an independently specified expectation with the result.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

EVALUATOR_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"

STATES = (
    "TARGET_IDENTIFIED",
    "BASELINE_CAPTURED",
    "DEVICE_ELIGIBLE",
    "APK_INSTALLED",
    "DEVICE_OWNER_ASSIGNED",
    "BASELINE_RESTORED",
    "SCAN_PASSED",
    "REBOOT_VERIFIED",
    "OBSERVATION_COMPLETE",
)

EVIDENCE_KEYS = (
    "device_identity",
    "selection_unique",
    "authorization",
    "original_verifier_baseline",
    "eligible_clean_device",
    "google_certification",
    "artifact_digest",
    "apk_install_result",
    "device_owner_status",
    "verifier_restoration_match",
    "play_protect_scan_result",
    "post_reboot_verifier_match",
    "post_reboot_owner_status",
    "observation_export_digest",
)

EVIDENCE_STATUSES = {"verified", "missing", "mismatch", "failed", "unknown"}
DECISIONS = {"CONTINUE", "WAIT", "RETRY_KNOWN_STEP", "STOP"}

STATE_REQUIREMENT = {
    "TARGET_IDENTIFIED": "authorization",
    "BASELINE_CAPTURED": "original_verifier_baseline",
    "DEVICE_ELIGIBLE": "google_certification",
    "APK_INSTALLED": "apk_install_result",
    "DEVICE_OWNER_ASSIGNED": "device_owner_status",
    "BASELINE_RESTORED": "verifier_restoration_match",
    "SCAN_PASSED": "play_protect_scan_result",
    "REBOOT_VERIFIED": "post_reboot_owner_status",
    "OBSERVATION_COMPLETE": "observation_export_digest",
}

STATE_EXTRA_REQUIREMENTS = {
    "TARGET_IDENTIFIED": ("device_identity", "selection_unique"),
    "DEVICE_ELIGIBLE": ("eligible_clean_device",),
    "APK_INSTALLED": ("artifact_digest",),
    "REBOOT_VERIFIED": ("post_reboot_verifier_match",),
}

FACTS = {
    "UNKNOWN_STATE": "The supplied state is outside the approved synthetic state vocabulary.",
    "EVIDENCE_CONTRADICTION": "Supplied evidence contradicts a required safety condition.",
    "UNCLASSIFIED_FAILURE": "A failed observation has no approved repair classification.",
    "TERMINAL_KNOWN_FAILURE": "The known failure is classified as terminal and cannot be retried.",
    "MISSING_EVIDENCE": "A transition cannot be authorized until the listed evidence is present.",
    "KNOWN_REPAIRABLE_FAILURE": "A known step failure may be retried without advancing state.",
    "STATE_VERIFIED": "All evidence required for the current synthetic state is verified.",
    "EXPERIMENT_COMPLETE": "The observation is complete; activation is outside this experiment.",
}

# Fixtures may report one of these categories, but they cannot define what the
# category permits. Repairability and retry state are evaluator-owned policy.
FAILURE_POLICIES = {
    "INSTALL_REJECTION": {
        "evidence_key": "apk_install_result",
        "repairability": "repairable",
        "state": "APK_INSTALLED",
        "consequential": False,
    },
    "AUTHORIZATION_REVOKED": {
        "evidence_key": "authorization",
        "repairability": "terminal",
        "state": "DEVICE_OWNER_ASSIGNED",
        "consequential": True,
    },
}


class ScenarioContractError(ValueError):
    """Raised when a scenario violates the executable input contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ScenarioContractError(message)


def validate_scenario(scenario: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "scenario_id",
        "split",
        "title",
        "current_state",
        "known_state",
        "consequential",
        "evidence",
        "expected_outcome",
    }
    allowed = required | {"known_failure"}
    _require(isinstance(scenario, dict), "scenario must be an object")
    _require(required <= scenario.keys(), f"missing scenario fields: {sorted(required - scenario.keys())}")
    _require(not (scenario.keys() - allowed), f"unknown scenario fields: {sorted(scenario.keys() - allowed)}")
    _require(scenario["schema_version"] == SCHEMA_VERSION, "unsupported schema_version")
    _require(isinstance(scenario["scenario_id"], str) and scenario["scenario_id"], "scenario_id must be non-empty")
    _require(scenario["split"] in {"development", "sealed"}, "invalid split")
    _require(isinstance(scenario["title"], str) and scenario["title"], "title must be non-empty")
    _require(scenario["current_state"] in STATES, "invalid current_state")
    _require(type(scenario["known_state"]) is bool, "known_state must be boolean")
    _require(type(scenario["consequential"]) is bool, "consequential must be boolean")
    _require(isinstance(scenario["evidence"], list), "evidence must be an array")

    seen: set[str] = set()
    for item in scenario["evidence"]:
        _require(isinstance(item, dict), "each evidence item must be an object")
        _require({"key", "status", "source"} <= item.keys(), "evidence item is missing a required field")
        _require(not (item.keys() - {"key", "status", "source", "observed"}), "evidence item has an unknown field")
        _require(item["key"] in EVIDENCE_KEYS, f"invalid evidence key: {item['key']}")
        _require(item["key"] not in seen, f"duplicate evidence key: {item['key']}")
        seen.add(item["key"])
        _require(item["status"] in EVIDENCE_STATUSES, f"invalid evidence status: {item['status']}")
        _require(item["source"] == "synthetic_fixture", "only synthetic fixture evidence is allowed")
        _require(isinstance(item.get("observed"), (str, int, float, bool, type(None))), "observed must be scalar")

    expected = scenario["expected_outcome"]
    _require(isinstance(expected, dict), "expected_outcome must be an object")
    _require(set(expected) == {"decision", "reason_code", "missing_evidence"}, "invalid expected_outcome fields")
    _require(expected["decision"] in DECISIONS, "invalid expected decision")
    _require(isinstance(expected["reason_code"], str), "expected reason_code must be a string")
    _require(isinstance(expected["missing_evidence"], list), "expected missing_evidence must be an array")

    failure = scenario.get("known_failure")
    if failure is not None:
        _require(isinstance(failure, dict), "known_failure must be an object")
        _require(set(failure) == {"category", "evidence_key"}, "invalid known_failure fields")
        _require(failure["category"] in FAILURE_POLICIES, "failure category is not in evaluator policy")
        _require(failure["evidence_key"] in EVIDENCE_KEYS, "invalid known failure evidence_key")
        policy = FAILURE_POLICIES[failure["category"]]
        _require(failure["evidence_key"] == policy["evidence_key"], "failure evidence does not match evaluator policy")
        _require(scenario["current_state"] == policy["state"], "failure state does not match evaluator policy")
        _require(scenario["consequential"] is policy["consequential"], "failure consequence class does not match evaluator policy")
        failure_evidence = [item for item in scenario["evidence"] if item["key"] == failure["evidence_key"]]
        _require(len(failure_evidence) == 1, "known failure must reference supplied evidence")
        _require(failure_evidence[0]["status"] == "failed", "known failure evidence must have failed status")


def load_scenario(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        scenario = json.load(handle)
    validate_scenario(scenario)
    return scenario


def _decision(
    scenario_id: str,
    decision: str,
    reason_code: str,
    *,
    next_state: str | None = None,
    missing_evidence: list[str] | None = None,
    extra_facts: list[str] | None = None,
) -> dict[str, Any]:
    facts = [FACTS[reason_code]]
    if extra_facts:
        facts.extend(extra_facts)
    return {
        "schema_version": SCHEMA_VERSION,
        "evaluator_version": EVALUATOR_VERSION,
        "scenario_id": scenario_id,
        "decision": decision,
        "reason_code": reason_code,
        "next_state": next_state,
        "missing_evidence": missing_evidence or [],
        "facts": facts,
        "source": "deterministic_evaluator",
    }


def _required_evidence(current_state: str) -> list[str]:
    required: list[str] = []
    for state in STATES[: STATES.index(current_state) + 1]:
        required.extend(STATE_EXTRA_REQUIREMENTS.get(state, ()))
        required.append(STATE_REQUIREMENT[state])
    return required


def evaluate_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic decision without consulting expected_outcome."""
    validate_scenario(scenario)
    scenario_id = scenario["scenario_id"]

    if not scenario["known_state"]:
        return _decision(scenario_id, "STOP", "UNKNOWN_STATE")

    evidence = {item["key"]: item for item in scenario["evidence"]}
    failure = scenario.get("known_failure")
    failure_policy = FAILURE_POLICIES[failure["category"]] if failure else None

    if failure_policy and failure_policy["repairability"] == "terminal":
        return _decision(scenario_id, "STOP", "TERMINAL_KNOWN_FAILURE", extra_facts=[failure["category"]])

    mismatches = [key for key, item in evidence.items() if item["status"] == "mismatch"]
    if mismatches:
        return _decision(
            scenario_id,
            "STOP",
            "EVIDENCE_CONTRADICTION",
            extra_facts=[f"Contradictory evidence: {', '.join(mismatches)}."],
        )

    failures = [key for key, item in evidence.items() if item["status"] == "failed"]
    if failures:
        if (
            failure_policy
            and failure_policy["repairability"] == "repairable"
            and failures == [failure["evidence_key"]]
        ):
            return _decision(
                scenario_id,
                "RETRY_KNOWN_STEP",
                "KNOWN_REPAIRABLE_FAILURE",
                next_state=failure_policy["state"],
                extra_facts=[failure["category"]],
            )
        return _decision(
            scenario_id,
            "STOP",
            "UNCLASSIFIED_FAILURE",
            extra_facts=[f"Failed evidence: {', '.join(failures)}."],
        )

    required = _required_evidence(scenario["current_state"])
    missing = [
        key
        for key in required
        if key not in evidence or evidence[key]["status"] in {"missing", "unknown"}
    ]
    if missing:
        return _decision(scenario_id, "WAIT", "MISSING_EVIDENCE", missing_evidence=missing)

    if scenario["current_state"] == "OBSERVATION_COMPLETE":
        return _decision(scenario_id, "STOP", "EXPERIMENT_COMPLETE")

    next_state = STATES[STATES.index(scenario["current_state"]) + 1]
    return _decision(scenario_id, "CONTINUE", "STATE_VERIFIED", next_state=next_state)


def label_matches(scenario: dict[str, Any], result: dict[str, Any]) -> bool:
    expected = scenario["expected_outcome"]
    return all(result[key] == expected[key] for key in ("decision", "reason_code", "missing_evidence"))


def _scenario_paths(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(target.rglob("*.json"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Scenario JSON file or directory")
    parser.add_argument("--check-label", action="store_true", help="Fail if a result differs from its fixture label")
    args = parser.parse_args(argv)

    records = []
    failed = False
    for path in _scenario_paths(args.target):
        scenario = load_scenario(path)
        result = evaluate_scenario(copy.deepcopy(scenario))
        match = label_matches(scenario, result)
        records.append({"fixture": str(path), "label_match": match, "result": result})
        failed = failed or (args.check_label and not match)

    print(json.dumps(records, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
