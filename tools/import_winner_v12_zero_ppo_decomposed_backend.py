#!/usr/bin/env python3
"""Import the one frozen Winner-v12 decomposed-backend CPU result."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v12_zero_ppo_decomposed_backend_preregistration.json"
)
OUTPUT_JSON = ANALYSIS / "winner_v12_zero_ppo_decomposed_backend_result.json"
OUTPUT_MD = (
    ANALYSIS / "WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_RESULT_20260720.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate_frozen_checks(checks: object, expected: list[str]) -> list[str]:
    if not isinstance(checks, dict) or not all(
        isinstance(name, str) and isinstance(value, bool)
        for name, value in checks.items()
    ):
        raise ValueError("raw result checks must be named booleans")
    if set(checks) != set(expected) or len(checks) != len(expected):
        raise ValueError("raw result check names do not match the frozen contract")
    return sorted(name for name, value in checks.items() if not value)


def validate_legacy_record_only(rows: object) -> None:
    """Require both closed Winner-v11 observations without making them gates."""

    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("legacy record-only evidence must contain two rows")
    expected_keys = {
        "protected_label",
        "max_action_error",
        "max_hidden_error",
        "gating",
        "reason",
    }
    if [row.get("protected_label") for row in rows if isinstance(row, dict)] != [
        "half",
        "final",
    ]:
        raise ValueError("legacy record-only evidence must cover half and final")
    for row in rows:
        if set(row) != expected_keys or row["gating"] is not False:
            raise ValueError("legacy Winner-v11 quantities must remain non-gating")
        if row["reason"] != (
            "closed Winner-v11 quantity; protected ONNX is authoritative"
        ):
            raise ValueError("legacy record-only reason changed")
        for name in ("max_action_error", "max_hidden_error"):
            value = row[name]
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or value < 0.0
            ):
                raise ValueError("legacy record-only errors must be finite nonnegative")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--contract-commit", required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v12 formal result has already been imported")
    raw_path = args.raw_result.resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    prereg_sha = sha256_lf(PREREGISTRATION)
    expected_top_level = {
        "schema_version",
        "status",
        "decision",
        "checks",
        "failed_checks",
        "preregistration_sha256",
        "source_hashes",
        "protected_policy_hashes",
        "devices",
        "versions",
        "boundary_identity",
        "step_zero",
        "auxiliary_trainability",
        "calibration_chain",
        "sequence_and_handoff",
        "fail_closed",
        "default_off_identities",
        "default_off_x0_chains",
        "protected_physical_chains",
        "response_branch_default",
        "response_branch_enabled_stress",
        "full_authoritative_onnx_stress",
        "deployable_export_byte_identity",
        "legacy_full_protected_jax_onnx_record_only",
        "observed_test_population",
        "temporary_artifacts",
        "execution_counts",
        "authority",
        "limitations",
    }
    if set(raw) != expected_top_level:
        raise ValueError("raw result schema fields do not match the frozen importer")
    if raw["schema_version"] != (
        "winner_v12.zero_ppo_decomposed_backend_result.v1"
    ):
        raise ValueError("raw result schema is not frozen Winner-v12 v1")
    if raw["preregistration_sha256"] != prereg_sha:
        raise ValueError("raw result does not match the frozen Winner-v12 contract")
    expected_sources = {
        name: row["sha256"] for name, row in prereg["sources"].items()
    }
    if raw["source_hashes"] != expected_sources:
        raise ValueError("raw result source hashes differ from the preregistration")
    expected_policies = {
        name: row["sha256"]
        for name, row in prereg["protected_policies"].items()
    }
    if raw["protected_policy_hashes"] != expected_policies:
        raise ValueError("raw result protected policy hashes changed")
    if raw["observed_test_population"] != prereg["test_population"]:
        raise ValueError("raw result population differs from the preregistration")
    if raw["execution_counts"] != {"optimizer_steps": 0, "formal_behavior_cells": 0}:
        raise ValueError("raw result exceeded the zero-PPO boundary")
    if not raw["devices"] or not all(
        "cpu" in str(device).lower()
        and "gpu" not in str(device).lower()
        and "cuda" not in str(device).lower()
        for device in raw["devices"]
    ):
        raise ValueError("raw result is not CPU-only")
    failed = validate_frozen_checks(
        raw["checks"], prereg["expected_result_checks"]
    )
    if raw["failed_checks"] != failed:
        raise ValueError("raw failed_checks differ from the check booleans")
    passed = raw["status"] == (
        "PASS_WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_MECHANICS"
    )
    statuses = {
        "PASS_WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_MECHANICS",
        "HOLD_WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_MECHANICS",
    }
    if raw["status"] not in statuses:
        raise ValueError("raw result status is not a frozen Winner-v12 status")
    decision = (
        "AUTHORIZE_SEPARATE_WINNER_V12_TRAINING_PREREGISTRATION_ONLY"
        if passed
        else "STOP_WINNER_V12_AND_REVIEW_DECOMPOSED_MECHANICS_FAILURE"
    )
    if raw["decision"] != decision or passed != (not failed):
        raise ValueError("raw status, decision, and frozen checks are inconsistent")
    authority = {
        "separate_training_preregistration_design": passed,
        "training_or_optimizer": False,
        "behavior_evaluation": False,
        "runtime_implementation": False,
        "robot_rdk_torque_motion_gate5_deployment": False,
        "robot_clearance": False,
    }
    if raw["authority"] != authority:
        raise ValueError("raw authority exceeds the Winner-v12 mechanics boundary")
    if raw["deployable_export_byte_identity"] != {"half": True, "final": True}:
        raise ValueError("deployable Winner-v12 bytes differ from Winner-v11")
    validate_legacy_record_only(
        raw["legacy_full_protected_jax_onnx_record_only"]
    )

    payload = dict(raw)
    payload["repository_attribution"] = {
        "contract_commit": args.contract_commit,
        "preregistration_path": str(PREREGISTRATION.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "preregistration_sha256": prereg_sha,
        "raw_result_filename": raw_path.name,
        "raw_result_sha256": sha256(raw_path),
    }
    OUTPUT_JSON.write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    OUTPUT_MD.write_bytes(
        (
            "# Winner-v12 Decomposed-Backend CPU Result\n\n"
            f"Status: `{payload['status']}`\n\n"
            f"Decision: `{payload['decision']}`\n\n"
            f"Imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n\n"
            f"Failed checks: `{payload['failed_checks']}`\n\n"
            "Winner-v11 remains closed. This result contains no training or behavior "
            "evaluation and cannot authorize runtime, hardware, motion, Gate 5, "
            "deployment, or robot clearance.\n"
        ).encode("utf-8")
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
