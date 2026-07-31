#!/usr/bin/env python3
"""Attribute the closed winner-v8 contract hold without reclassifying it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RESULT = ANALYSIS / "winner_v8_physical_envelope_contract_result.json"
PREREG = ANALYSIS / "winner_v8_physical_envelope_contract_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v8_numeric_hold_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V8_NUMERIC_HOLD_ATTRIBUTION_20260720.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("winner-v8 numeric attribution already exists")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    full_delta = np.asarray(result["max_action_delta"], dtype=np.float32)
    safe_delta = np.asarray(result["safe_max_action_delta"], dtype=np.float32)
    safe_excesses = [
        max(
            float(row["stress"]["maximum_safe_delta_excess"]),
            float(row["moving_chain"]["maximum_safe_delta_excess"]),
        )
        for row in result["policies"]
    ]
    minimum_inward_headroom = float(np.min(full_delta - safe_delta))
    maximum_safe_excess = max(safe_excesses)
    stored_bound_excess_upper_bound = max(
        maximum_safe_excess - minimum_inward_headroom, 0.0
    )
    epsilon = float(np.finfo(np.float32).eps)
    checks = {
        "formal_result_remains_hold": result["status"]
        == "HOLD_WINNER_V8_PHYSICAL_ENVELOPE_CONTRACT",
        "only_internal_safe_delta_checks_failed": result["failed_checks"]
        == [
            "all_8192_stress_cases_strictly_bounded",
            "both_256_tick_moving_chains_strictly_bounded",
        ],
        "both_checkpoint_excesses_identical": len(safe_excesses) == 2
        and safe_excesses[0] == safe_excesses[1],
        "safe_excess_below_one_float32_epsilon": maximum_safe_excess < epsilon,
        "safe_excess_smaller_than_inward_headroom": maximum_safe_excess
        < minimum_inward_headroom,
        "stored_full_measured_bound_has_zero_proven_excess": stored_bound_excess_upper_bound
        == 0.0,
        "xml_and_graph_identity_checks_passed": all(
            result["checks"][name]
            for name in (
                "all_14_actuators_inherit_physical_force_limit",
                "both_abis_exact",
                "both_256_tick_x0_chains_exact_zero",
                "frozen_inputs_exact",
                "only_two_rate_initializers_changed",
                "xml_only_force_range_changed",
            )
        ),
        "v8_close_rule_present": "closes this exact two-factor transform"
        in prereg["no_retry_or_tuning"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    attributed = not failed
    stored_delta = np.nextafter(full_delta, np.float32(-np.inf))
    internal_safe_delta = np.nextafter(
        stored_delta - np.float32(4.0) * np.finfo(np.float32).eps,
        np.float32(-np.inf),
    )
    payload = {
        "schema_version": "open_duck_mini.winner_v8_numeric_hold_attribution.v1",
        "status": "PASS_WINNER_V8_HOLD_ATTRIBUTED_TO_INTERNAL_FLOAT32_ASSERTION"
        if attributed
        else "HOLD_WINNER_V8_NUMERIC_ATTRIBUTION",
        "decision": "PREREGISTER_DISTINCT_WINNER_V9_STORED_BOUND_CONTRACT_ONLY"
        if attributed
        else "STOP_WINNER_V8_FAMILY_PENDING_REVIEW",
        "winner_v8_remains_closed": True,
        "winner_v8_reclassified_or_retried": False,
        "checks": checks,
        "failed_checks": failed,
        "numeric_evidence": {
            "checkpoint_safe_delta_excess": safe_excesses,
            "float32_epsilon": epsilon,
            "minimum_internal_inward_headroom": minimum_inward_headroom,
            "maximum_safe_delta_excess": maximum_safe_excess,
            "stored_full_bound_excess_upper_bound": stored_bound_excess_upper_bound,
        },
        "distinct_v9_hypothesis": {
            "stored_max_action_delta": stored_delta.tolist(),
            "internal_safe_max_action_delta": internal_safe_delta.tolist(),
            "stored_delta_equation": "nextafter(float32(rate*0.02/0.25), -infinity)",
            "internal_delta_equation": "nextafter(stored_delta - 4*float32_epsilon, -infinity)",
            "assertion": "compare final output to stored_max_action_delta with zero tolerance; the smaller internal delta is implementation headroom, not the public physical boundary",
            "why_distinct": "both named delta initializers differ from the closed winner-v8 graph and the public stored bound is analytically rounded inward",
            "tolerance_or_rate_change": False,
            "first_gate": "new zero-behavior CPU graph/XML contract only",
        },
        "inputs": {
            "result": {"path": str(RESULT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(RESULT)},
            "preregistration": {"path": str(PREREG.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PREREG)},
        },
        "authority": {
            "winner_v9_preregistration_design": attributed,
            "winner_v9_run_behavior_training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "# Winner-v8 Numeric Hold Attribution\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"- maximum internal-safe excess: `{maximum_safe_excess}` normalized action\n"
        f"- minimum internal headroom to the stored measured bound: `{minimum_inward_headroom}`\n"
        f"- proven stored-bound excess upper bound: `{stored_bound_excess_upper_bound}`\n\n"
        "Winner-v8 remains closed. The distinct v9 hypothesis changes both stored delta tensors by analytic inward rounding and checks the public stored boundary rather than the private implementation headroom. No behavior, training, runtime, robot access, torque, motion, Gate 5, or clearance is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"OUTPUT_SHA256={sha256(OUTPUT_JSON)}")
    return 0 if attributed else 2


if __name__ == "__main__":
    raise SystemExit(main())
