#!/usr/bin/env python3
"""Create an opaque, seed-private synthetic holdout without evaluating it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import secrets
from pathlib import Path
from typing import Any

from companion.evaluator import STATE_EXTRA_REQUIREMENTS, STATE_REQUIREMENT, STATES


ROOT = Path(__file__).resolve().parents[1]
SEALED_DIR = ROOT / "fixtures" / "sealed"
SEED_PATH = ROOT / "fixtures" / ".sealed-seed"
MANIFEST_PATH = ROOT / "fixtures" / "sealed-manifest.json"


def _required_evidence(state: str) -> list[str]:
    required: list[str] = []
    for current in STATES[: STATES.index(state) + 1]:
        required.extend(STATE_EXTRA_REQUIREMENTS.get(current, ()))
        required.append(STATE_REQUIREMENT[current])
    return required


def _observed(key: str, alias: str) -> str | bool:
    values: dict[str, str | bool] = {
        "device_identity": alias,
        "selection_unique": True,
        "authorization": True,
        "original_verifier_baseline": "synthetic-baseline-captured",
        "eligible_clean_device": True,
        "google_certification": True,
        "artifact_digest": "sha256:synthetic-artifact",
        "apk_install_result": "synthetic-install-passed",
        "device_owner_status": "synthetic-owner-assigned",
        "verifier_restoration_match": True,
        "play_protect_scan_result": "synthetic-scan-passed",
        "post_reboot_verifier_match": True,
        "post_reboot_owner_status": "synthetic-owner-retained",
        "observation_export_digest": "sha256:synthetic-observation",
    }
    return values[key]


def _evidence(keys: list[str], alias: str, overrides: dict[str, str] | None = None) -> list[dict[str, Any]]:
    overrides = overrides or {}
    records = []
    for key in keys:
        status = overrides.get(key, "verified")
        observed: Any = _observed(key, alias)
        if status in {"missing", "unknown"}:
            observed = None
        elif status == "mismatch":
            observed = False if isinstance(observed, bool) else "synthetic-mismatch"
        elif status == "failed":
            observed = "synthetic-failure"
        records.append({
            "key": key,
            "status": status,
            "source": "synthetic_fixture",
            "observed": observed,
        })
    return records


def _case(
    number: int,
    state: str,
    evidence: list[dict[str, Any]],
    expected: tuple[str, str, list[str]],
    *,
    known_state: bool = True,
    consequential: bool = True,
    known_failure: dict[str, str] | None = None,
) -> dict[str, Any]:
    scenario: dict[str, Any] = {
        "schema_version": "1.0",
        "scenario_id": f"sealed_{number:03d}",
        "split": "sealed",
        "title": f"Opaque synthetic holdout case {number:03d}",
        "current_state": state,
        "known_state": known_state,
        "consequential": consequential,
        "evidence": evidence,
        "expected_outcome": {
            "decision": expected[0],
            "reason_code": expected[1],
            "missing_evidence": expected[2],
        },
    }
    if known_failure:
        scenario["known_failure"] = known_failure
    return scenario


def build_cases(rng: random.Random) -> list[dict[str, Any]]:
    """Build labels from predeclared case families; never call evaluate_scenario."""
    specs: list[tuple[str, dict[str, Any]]] = []

    for state in STATES:
        specs.append(("verified", {"state": state}))

    for state in rng.sample(list(STATES[1:]), 6):
        required = _required_evidence(state)
        count = 2 if len(required) >= 5 and rng.random() < 0.5 else 1
        missing = sorted(rng.sample(required, count), key=required.index)
        statuses = {key: rng.choice(["missing", "unknown"]) for key in missing}
        specs.append(("missing", {"state": state, "missing": missing, "statuses": statuses}))

    for state in rng.sample(list(STATES), 4):
        key = rng.choice(_required_evidence(state))
        specs.append(("mismatch", {"state": state, "key": key}))

    specs.extend([
        ("repairable_install", {"state": "APK_INSTALLED"}),
        ("terminal_authorization", {"state": "DEVICE_OWNER_ASSIGNED"}),
        ("unclassified_owner", {"state": "DEVICE_OWNER_ASSIGNED"}),
        ("unknown", {"state": rng.choice(STATES)}),
        ("unknown", {"state": rng.choice(STATES)}),
    ])
    rng.shuffle(specs)

    cases: list[dict[str, Any]] = []
    for number, (family, spec) in enumerate(specs, start=1):
        state = spec["state"]
        alias = f"SIM-{rng.getrandbits(40):010X}"
        required = _required_evidence(state)
        if family == "verified":
            expected = ("STOP", "EXPERIMENT_COMPLETE", []) if state == "OBSERVATION_COMPLETE" else (
                "CONTINUE", "STATE_VERIFIED", []
            )
            cases.append(_case(number, state, _evidence(required, alias), expected, consequential=state != "TARGET_IDENTIFIED"))
        elif family == "missing":
            cases.append(_case(
                number,
                state,
                _evidence(required, alias, spec["statuses"]),
                ("WAIT", "MISSING_EVIDENCE", spec["missing"]),
            ))
        elif family == "mismatch":
            cases.append(_case(
                number,
                state,
                _evidence(required, alias, {spec["key"]: "mismatch"}),
                ("STOP", "EVIDENCE_CONTRADICTION", []),
            ))
        elif family == "repairable_install":
            cases.append(_case(
                number,
                state,
                _evidence(required, alias, {"apk_install_result": "failed"}),
                ("RETRY_KNOWN_STEP", "KNOWN_REPAIRABLE_FAILURE", []),
                consequential=False,
                known_failure={"category": "INSTALL_REJECTION", "evidence_key": "apk_install_result"},
            ))
        elif family == "terminal_authorization":
            cases.append(_case(
                number,
                state,
                _evidence(["authorization"], alias, {"authorization": "failed"}),
                ("STOP", "TERMINAL_KNOWN_FAILURE", []),
                known_failure={"category": "AUTHORIZATION_REVOKED", "evidence_key": "authorization"},
            ))
        elif family == "unclassified_owner":
            cases.append(_case(
                number,
                state,
                _evidence(["device_owner_status"], alias, {"device_owner_status": "failed"}),
                ("STOP", "UNCLASSIFIED_FAILURE", []),
            ))
        else:
            cases.append(_case(number, state, [], ("STOP", "UNKNOWN_STATE", []), known_state=False))
    return cases


def _load_or_create_seed() -> str:
    if SEED_PATH.exists():
        seed = SEED_PATH.read_text(encoding="utf-8").strip()
        if len(seed) != 64 or any(char not in "0123456789abcdef" for char in seed):
            raise ValueError("invalid private sealed seed")
        return seed
    seed = secrets.token_hex(32)
    SEED_PATH.write_text(seed + "\n", encoding="utf-8")
    os.chmod(SEED_PATH, 0o600)
    return seed


def _canonical(case: dict[str, Any]) -> bytes:
    return (json.dumps(case, indent=2, sort_keys=True) + "\n").encode("utf-8")


def create(*, force: bool) -> dict[str, Any]:
    seed = _load_or_create_seed()
    SEALED_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(SEALED_DIR.glob("*.json"))
    if existing and not force:
        raise FileExistsError("sealed fixtures already exist; use --force only before any sealed evaluation")
    for path in existing:
        path.unlink()

    cases = build_cases(random.Random(int(seed, 16)))
    records = []
    for index, case in enumerate(cases, start=1):
        name = f"sealed_{index:03d}.json"
        payload = _canonical(case)
        (SEALED_DIR / name).write_bytes(payload)
        records.append({"path": name, "sha256": hashlib.sha256(payload).hexdigest()})

    aggregate = hashlib.sha256("".join(item["sha256"] for item in records).encode("ascii")).hexdigest()
    manifest = {
        "manifest_version": "1.0",
        "protocol_version": "1.0",
        "created_at": "2026-08-14",
        "split": "sealed",
        "case_count": len(records),
        "contents_committed": False,
        "seed_committed": False,
        "limitations": "Synthetic seed-private holdout; not independently collected ground truth.",
        "aggregate_sha256": aggregate,
        "files": records,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace the local seal before it has ever been evaluated")
    args = parser.parse_args()
    manifest = create(force=args.force)
    print(json.dumps({
        "case_count": manifest["case_count"],
        "aggregate_sha256": manifest["aggregate_sha256"],
        "contents_committed": False,
        "seed_committed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
