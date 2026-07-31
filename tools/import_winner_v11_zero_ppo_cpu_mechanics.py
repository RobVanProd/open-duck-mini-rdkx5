#!/usr/bin/env python3
"""Import one external Winner-v11 zero-PPO CPU mechanics result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V11_ZERO_PPO_CPU_MECHANICS_RESULT_20260720.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate_frozen_checks(
    checks: object, expected_names: list[str]
) -> list[str]:
    """Reject omitted, added, or non-boolean result checks before import."""

    if not isinstance(checks, dict) or not all(
        isinstance(name, str) and isinstance(value, bool)
        for name, value in checks.items()
    ):
        raise ValueError("raw result checks must be named booleans")
    if set(checks) != set(expected_names) or len(checks) != len(expected_names):
        raise ValueError("raw result check names do not match the frozen contract")
    return sorted(name for name, value in checks.items() if not value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--contract-commit", required=True)
    args = parser.parse_args()
    raw_path = args.raw_result.resolve()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v11 formal result has already been imported")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    preregistration_sha = sha256_lf(PREREGISTRATION)
    if raw["preregistration_sha256"] != preregistration_sha:
        raise ValueError("raw result does not match the frozen Winner-v11 contract")
    statuses = {
        "PASS_WINNER_V11_ZERO_PPO_CPU_MECHANICS",
        "HOLD_WINNER_V11_ZERO_PPO_CPU_MECHANICS",
    }
    if raw["status"] not in statuses:
        raise ValueError(f"unexpected raw result status: {raw['status']}")
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
        "default_off_expansions",
        "default_off_x0_chains",
        "enabled_stress",
        "protected_physical_chains",
        "observed_test_population",
        "temporary_artifacts",
        "execution_counts",
        "authority",
        "limitations",
    }
    if set(raw) != expected_top_level:
        raise ValueError("raw result schema fields do not match the frozen importer")
    if raw["schema_version"] != "winner_v11.zero_ppo_cpu_mechanics_result.v1":
        raise ValueError("raw result schema version is not frozen Winner-v11 v1")
    expected_sources = {
        label: row["sha256"]
        for label, row in preregistration["sources"].items()
    }
    if raw["source_hashes"] != expected_sources:
        raise ValueError("raw result source hashes do not match the preregistration")
    expected_policies = {
        label: row["sha256"]
        for label, row in preregistration["protected_policies"].items()
    }
    if raw["protected_policy_hashes"] != expected_policies:
        raise ValueError("raw result protected policies do not match Winner-v10")
    if raw["execution_counts"] != {"optimizer_steps": 0, "formal_behavior_cells": 0}:
        raise ValueError("raw result exceeded the zero-PPO authority boundary")
    if raw["observed_test_population"] != preregistration["test_population"]:
        raise ValueError("raw result test population differs from the frozen population")
    if not raw["devices"] or not all(
        "cpu" in str(device).lower()
        and "gpu" not in str(device).lower()
        and "cuda" not in str(device).lower()
        for device in raw["devices"]
    ):
        raise ValueError("raw result is not CPU-only")
    observed_failed = validate_frozen_checks(
        raw["checks"], preregistration["expected_result_checks"]
    )
    if raw["failed_checks"] != observed_failed:
        raise ValueError("raw failed_checks do not match the check booleans")
    passed = raw["status"] == "PASS_WINNER_V11_ZERO_PPO_CPU_MECHANICS"
    expected_decision = (
        "AUTHORIZE_SEPARATE_WINNER_V11_TRAINING_PREREGISTRATION_ONLY"
        if passed
        else "STOP_WINNER_V11_AND_REVIEW_MECHANICS_FAILURE"
    )
    if raw["decision"] != expected_decision:
        raise ValueError("raw decision is inconsistent with its status")
    if passed != (not observed_failed):
        raise ValueError("PASS requires every frozen check to be true")
    expected_authority = {
        "separate_training_preregistration_design": passed,
        "training_or_optimizer": False,
        "colab_hosted_gpu_or_igpu": False,
        "runtime_implementation": False,
        "rdkx5_robot_torque_motion_gate5_deployment": False,
        "robot_clearance": False,
    }
    if raw["authority"] != expected_authority:
        raise ValueError("raw result authority exceeds the mechanics-only boundary")
    payload = dict(raw)
    payload["repository_attribution"] = {
        "contract_commit": args.contract_commit,
        "preregistration_path": str(PREREGISTRATION.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "preregistration_sha256": preregistration_sha,
        "raw_result_filename": raw_path.name,
        "raw_result_sha256": sha256(raw_path),
    }
    OUTPUT_JSON.write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    OUTPUT_MD.write_bytes(
        (
            "# Winner-v11 Zero-PPO CPU Mechanics Result\n\n"
            f"Status: `{payload['status']}`\n\n"
            f"Decision: `{payload['decision']}`\n\n"
            f"Imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n\n"
            f"- failed checks: `{payload['failed_checks']}`\n"
            f"- calibrator chain action/hidden error: "
            f"`{payload['calibration_chain']['max_action_error']}` / "
            f"`{payload['calibration_chain']['max_hidden_error']}`\n"
            f"- default-off identity: "
            f"`{payload['checks']['default_off_arbitrary_input_identity_bit_exact']}`\n"
            f"- exact x=0 chain: "
            f"`{payload['checks']['default_off_x0_exact_zero_and_identity']}`\n"
            f"- enabled strict stored bounds: "
            f"`{payload['checks']['enabled_graphs_strict_stored_bounds']}`\n"
            f"- physical-chain strict bounds: "
            f"`{payload['checks']['protected_physical_chains_strict_and_exact']}`\n"
            f"- invalid handoffs rejected: "
            f"`{len(payload['fail_closed']['rejected_cases'])}/"
            f"{len(payload['fail_closed']['invalid_cases'])}`\n\n"
            "This is mechanics-only evidence: zero optimizer steps and zero behavior "
            "cells. A pass authorizes only a separately reviewed training "
            "preregistration—not training, runtime implementation, hardware, motion, "
            "Gate 5, deployment, or robot clearance.\n"
        ).encode("utf-8")
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
