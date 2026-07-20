#!/usr/bin/env python3
"""Freeze the post-result full measured-vector causal audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "winner_v7_full_measured_vector_attribution_preregistration.json"
AUDIT = ROOT / "tools" / "audit_winner_v7_full_measured_vector_attribution.py"
INPUTS = {
    "winner_v7_result": ANALYSIS / "winner_v7_full_behavior_revalidation_result.json",
    "force_limit_attribution": ANALYSIS / "winner_v7_actuator_force_limit_attribution.json",
    "current_gate_contract": ANALYSIS / "winner_v3_current_gate_application_contract.json",
    "measured_all_joint_envelope": ANALYSIS / "winner_v5_automatic_support_recovery_preregistration.json",
    "runtime_policy_contract": ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719/policy_contract.json",
    "winner_v7_graph_contract": ANALYSIS / "winner_v7_inward_projection_contract_result.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source(path: Path) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    closed = json.loads(INPUTS["winner_v7_result"].read_text(encoding="utf-8"))
    force_hold = json.loads(INPUTS["force_limit_attribution"].read_text(encoding="utf-8"))
    if closed["decision"] != "CLOSE_WINNER_V7_PROTECTED_BASE":
        raise ValueError("winner-v7 source is not closed")
    if force_hold["decision"] != "CLOSE_PHYSICAL_FORCE_LIMIT_ATTRIBUTION_ROUTE":
        raise ValueError("simple force-limit route is not closed")
    payload = {
        "schema_version": "open_duck_mini.winner_v7_full_measured_vector_attribution_preregistration.v1",
        "status": "FROZEN_WINNER_V7_FULL_MEASURED_VECTOR_ATTRIBUTION",
        "source_commit": args.source_commit,
        "causal_question": "Did the source graph's pitch-only measured projection leave eight non-pitch joints at the legacy 5.24 rad/s allowance, causing the moving-only current and torque failures attributed incompletely by the closed force-ceiling route?",
        "frozen_inputs": {
            **{name: source(path) for name, path in INPUTS.items()},
            "audit_tool_sha256": sha256(AUDIT),
        },
        "analysis_contract": {
            "population": "all 128 hash-bound winner-v7 traces",
            "numeric_tolerance": 1e-9,
            "causal_prior_window_ticks": 6,
            "window_basis": "the measured all-joint profiles contain 2-3 tick delay and head/neck tau up to 0.12 s, equal to six 50-Hz ticks",
            "replay": [
                "derive the 14-element conservative vector from the frozen P30/P31 actuator evidence",
                "compare it field-by-field with the graph-authoritative vector in the runtime handoff",
                "recompute both recorded rate-excess fields from sent_target_velocity_rad_s",
                "recompute every per-joint peak-current and peak-torque failure",
                "measure whether each failing joint's peak follows a same-joint full-vector violation in the fixed six-tick window",
            ],
        },
        "selection_rule": {
            "all_checks_required": [
                "source_winner_v7_remains_closed",
                "source_population_complete",
                "recorded_rate_fields_replay_exactly",
                "partial_graph_vector_has_exactly_eight_relaxed_nonpitch_joints",
                "all_moving_traces_violate_full_measured_vector",
                "no_zero_trace_violates_full_measured_vector",
                "graph_vector_reports_zero_excess_for_all_traces",
                "all_moving_traces_fail_current_and_torque",
                "no_zero_trace_fails_current_or_torque",
                "every_gate_failing_joint_is_in_relaxed_vector_subset",
                "at_least_95pct_failure_peaks_follow_same_joint_violation_within_six_ticks",
            ],
            "pass_decision": "SELECT_DISTINCT_FULL_MEASURED_VECTOR_GRAPH_CONTRACT",
            "fail_decision": "CLOSE_FULL_MEASURED_VECTOR_CAUSAL_ROUTE",
        },
        "pass_authorizes_only": [
            "freeze a separately named zero-behavior CPU graph-transform contract",
            "replace both source and final-projection deltas with the complete measured conservative vector",
            "require arbitrary stress, x=0, physically chained, graph identity, and both current and torque checks before any behavior run",
        ],
        "closed_routes_not_reopened": [
            "winner-v7 protected base",
            "simple XML force-ceiling attribution",
            "winner-v6/v6b dynamic-calibrator contracts",
        ],
        "authority": {
            "read_only_cpu_analysis": True,
            "policy_or_simulator_mutation": False,
            "training_behavior_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE={OUTPUT}")
    print(f"SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
