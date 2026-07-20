#!/usr/bin/env python3
"""Freeze Winner-v10 R2 condition 1 without running behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "winner_v10_r2_condition1_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v10_r2_condition1.py"
V10_NOMINAL_PREREG = ANALYSIS / "winner_v10_nominal_behavior_preregistration.json"
V10_NOMINAL_RESULT = ANALYSIS / "winner_v10_nominal_behavior_result.json"
R2_MATRIX = ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise FileExistsError("Winner-v10 R2 condition-1 preregistration exists")
    nominal_prereg = json.loads(V10_NOMINAL_PREREG.read_text(encoding="utf-8"))
    nominal_result = json.loads(V10_NOMINAL_RESULT.read_text(encoding="utf-8"))
    r2_matrix = json.loads(R2_MATRIX.read_text(encoding="utf-8"))
    if nominal_result["status"] != "PASS_WINNER_V10_NOMINAL_BEHAVIOR":
        raise ValueError("Winner-v10 nominal behavior is not passed")
    condition = r2_matrix["conditions_in_strict_order"][0]
    if condition != {"id": "FLOOR_FRICTION_LO", "override": {"floor_friction": 0.5}}:
        raise ValueError("R2 first condition is not the frozen floor-friction endpoint")
    input_paths = {
        "runner": RUNNER,
        "v10_nominal_runner": ROOT / "tools/run_winner_v10_nominal_behavior.py",
        "v9_nominal_helper": ROOT / "tools/run_winner_v9_nominal_behavior.py",
        "v7_readback_helper": ROOT
        / "tools/run_winner_v7_full_behavior_revalidation.py",
        "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
        "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
        "actuator_model": ROOT / "tools/actuator_bridge_model.py",
        "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
        "v10_nominal_result": V10_NOMINAL_RESULT,
        "r2_matrix": R2_MATRIX,
        "r2_evaluator_contract": ANALYSIS
        / "ground_up_robustness_r2_evaluator_contract.json",
        "r2_reporting_contract": ANALYSIS
        / "ground_up_robustness_r2_reporting_contract.json",
        "current_contract": ANALYSIS
        / "winner_v3_current_gate_application_contract.json",
        "reference_feature_table": ANALYSIS
        / "ground_up_projected_reference_feature_table.npz",
        "fit_p30": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
        "fit_p31_34": ANALYSIS
        / "fixed_target_p31_34_actuator_fit_20260712.json",
    }
    policy_paths = {
        "half": args.policy_half.resolve(),
        "final": args.policy_final.resolve(),
    }
    payload = {
        "schema_version": "open_duck_mini.winner_v10_r2_condition1_preregistration.v1",
        "status": "FROZEN_WINNER_V10_R2_CONDITION1_NOT_RUN",
        "causal_question": "Does Winner-v10 preserve its complete behavior and protection gate at the first frozen isolated dynamics endpoint, floor friction 0.5?",
        "condition_index": 0,
        "condition": condition,
        "input_hashes": {name: sha256(path) for name, path in input_paths.items()},
        "policy_hashes": {name: sha256(path) for name, path in policy_paths.items()},
        "playground": nominal_prereg["playground"],
        "matrix": nominal_prereg["matrix"],
        "behavior_gates": nominal_prereg["behavior_gates"],
        "protection_gate": nominal_prereg["protection_gate"],
        "pass_rule": [
            "all frozen inputs, both unchanged policy hashes, and the one-step-inward physical Playground are exact",
            "exactly 16 complete 600-tick cells cover both checkpoints, both measured fits, and all four commands",
            "all x=0 and moving behavior gates pass",
            "every joint tick passes unchanged peak-current, decimal peak-torque, measured-rate-vector, and overcurrent-duration gates",
            "every evaluation requests floor friction 0.5 and returns a nonempty exact readback for that one axis",
            "CPU only; no later condition, training, GPU, runtime, robot, torque, motion, or Gate 5 work occurs",
        ],
        "no_retry_or_tuning": "A failed result stops Winner-v10 R2 at condition 1. Do not change policy, XML, fit, command, seed, duration, endpoint, gate, tolerance, simulator, or population.",
        "pass_authorizes_only": "write a separate Winner-v10 R2 condition-2 preregistration for floor friction 1.0",
        "authority": {
            "one_cpu_condition1_run": True,
            "condition2_or_later_execution": False,
            "training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"PREREGISTRATION={OUTPUT}")
    print(f"PREREGISTRATION_SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
