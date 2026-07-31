#!/usr/bin/env python3
"""Attribute the recorded v6b hold and derive a distinct v7 graph hypothesis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v6b_zero_ppo_cpu_contract_result.json"
PREREGISTRATION = ANALYSIS / "winner_v6b_zero_ppo_cpu_contract_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v6b_numeric_hold_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V6B_NUMERIC_HOLD_ATTRIBUTION_20260720.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    chains = result["protected_physical_chains"]
    excesses = [float(row["maximum_delta_excess"]) for row in chains]
    epsilon = float(np.finfo(np.float32).eps)
    inward_margin = float(np.float32(4.0) * np.finfo(np.float32).eps)
    checks = {
        "formal_result_remains_hold": result["status"]
        == "HOLD_WINNER_V6B_ZERO_PPO_CPU_SOFTWARE_CONTRACT",
        "only_physical_chain_check_failed": result["failed_checks"]
        == ["protected_physical_chains_hold_full_action_contract"],
        "both_checkpoint_excesses_identical": len(excesses) == 2
        and excesses[0] == excesses[1],
        "maximum_excess_below_two_float32_epsilons": max(excesses) < 2.0 * epsilon,
        "protected_identity_remained_exact": result["checks"][
            "default_off_arbitrary_input_identity_bit_exact"
        ],
        "enabled_adapter_bounds_passed": result["checks"][
            "enabled_adapter_arbitrary_input_bounds_hold"
        ],
        "all_other_software_contract_checks_passed": all(
            passed
            for name, passed in result["checks"].items()
            if name != "protected_physical_chains_hold_full_action_contract"
        ),
        "v6b_preregistered_close_rule_present": (
            "closes winner-v6 dynamic calibration"
            in preregistration["no_retry_or_tuning"]
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    attributed = not failed
    payload = {
        "schema_version": "winner_v6b.numeric_hold_attribution.v1",
        "status": (
            "PASS_V6B_HOLD_ATTRIBUTED_TO_FLOAT32_BOUNDARY"
            if attributed
            else "HOLD_V6B_FAILURE_NOT_NUMERICALLY_ATTRIBUTED"
        ),
        "decision": (
            "PREREGISTER_DISTINCT_V7_INWARD_PROJECTION_TRANSFORM_ONLY"
            if attributed
            else "STOP_POLICY_WORK_PENDING_REVIEW"
        ),
        "winner_v6_dynamic_calibration_closed": True,
        "winner_v6_or_v6b_retry_authorized": False,
        "completed_results_reclassified": False,
        "checks": checks,
        "failed_checks": failed,
        "numeric_evidence": {
            "checkpoint_maximum_delta_excess": excesses,
            "float32_epsilon": epsilon,
            "excess_over_epsilon_ratio": max(excesses) / epsilon,
            "frozen_v6b_tolerance": preregistration["numeric_tolerance"],
            "proposed_inward_margin_normalized_action": inward_margin,
            "margin_derivation": "4 * float32 machine epsilon",
            "margin_target_rad": inward_margin * 0.25,
            "margin_rate_rad_s": inward_margin * 0.25 / 0.02,
        },
        "distinct_v7_hypothesis": {
            "change": (
                "Create a new protected-base graph whose final output, after the "
                "actual-centered guard and deadband, is projected with each stored "
                "winner-v2 delta reduced inward by exactly four float32 epsilons."
            ),
            "why_distinct": (
                "This changes the protected graph output and therefore cannot be a "
                "v6/v6b default-off identity retry. It requires its own graph contract "
                "and full behavior revalidation before any response calibrator."
            ),
            "tolerance_change": False,
            "post_outcome_margin_tuning": False,
            "fixed_analytic_margin": inward_margin,
            "first_gate": "CPU graph transformation contract only",
            "after_first_gate": (
                "separately preregister complete x=0, nominal, actuator-fit, current, "
                "and robustness behavior revalidation; do not attach or train a calibrator"
            ),
        },
        "inputs": {
            "result": {
                "path": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(RESULT),
            },
            "preregistration": {
                "path": str(PREREGISTRATION.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(PREREGISTRATION),
            },
        },
        "authority": {
            "v7_transform_contract_preregistration": attributed,
            "v7_transform_contract_run": False,
            "behavior_evaluation": False,
            "dynamic_calibrator_or_training": False,
            "colab_gpu_runtime_robot_torque_motion": False,
            "robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    output_sha = sha256(OUTPUT_JSON)
    OUTPUT_MD.write_text(
        "# Winner-v6b Numeric Hold Attribution\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"JSON SHA-256: `{output_sha}`\n\n"
        f"Both protected checkpoints missed the frozen `1e-7` delta assertion by "
        f"`{max(excesses)}` normalized action, or `{max(excesses) / epsilon}` "
        "float32 epsilon. Every other v6b check passed. The v6/v6b route remains "
        "closed and is not retried.\n\n"
        "The next hypothesis changes the protected graph itself: a final inward-rounded "
        "projection with a fixed analytic margin of four float32 epsilons. It must pass "
        "a new graph contract and later full behavior revalidation before any calibrator "
        "work. No training, Colab, GPU, runtime, or robot action is authorized.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": output_sha}, sort_keys=True))
    return 0 if attributed else 1


if __name__ == "__main__":
    raise SystemExit(main())
