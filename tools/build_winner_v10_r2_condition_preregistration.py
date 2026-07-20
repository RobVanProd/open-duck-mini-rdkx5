#!/usr/bin/env python3
"""Freeze one sequential Winner-v10 R2 condition after the previous pass."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RUNNER = ROOT / "tools/run_winner_v10_r2_condition.py"
IMPORTER = ROOT / "tools/import_winner_v10_r2_condition.py"
V10_NOMINAL_PREREG = ANALYSIS / "winner_v10_nominal_behavior_preregistration.json"
R2_MATRIX = ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def status_name(prefix: str, index: int, condition_id: str) -> str:
    return f"{prefix}_WINNER_V10_R2_CONDITION{index + 1}_{condition_id}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition-index", type=int, required=True)
    parser.add_argument("--previous-result", type=Path, required=True)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError("Winner-v10 R2 preregistration already exists")
    if args.condition_index <= 0:
        raise ValueError("generic R2 builder is for condition 2 or later")
    nominal_prereg = json.loads(V10_NOMINAL_PREREG.read_text(encoding="utf-8"))
    r2_matrix = json.loads(R2_MATRIX.read_text(encoding="utf-8"))
    conditions = r2_matrix["conditions_in_strict_order"]
    if args.condition_index >= len(conditions):
        raise ValueError("R2 condition index is out of range")
    condition = conditions[args.condition_index]
    previous_condition = conditions[args.condition_index - 1]
    previous_path = args.previous_result.resolve()
    previous = json.loads(previous_path.read_text(encoding="utf-8"))
    required_previous_status = status_name(
        "PASS", args.condition_index - 1, previous_condition["id"]
    )
    required_previous_decision = (
        f"AUTHORIZE_WINNER_V10_R2_CONDITION{args.condition_index + 1}_PREREGISTRATION_ONLY"
    )
    if (
        previous["status"] != required_previous_status
        or previous["decision"] != required_previous_decision
    ):
        raise ValueError("previous R2 result does not authorize this preregistration")
    try:
        previous_relative = previous_path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("previous result must be an imported repository artifact") from exc
    input_paths = {
        "runner": RUNNER,
        "builder": Path(__file__),
        "importer": IMPORTER,
        "v10_nominal_runner": ROOT / "tools/run_winner_v10_nominal_behavior.py",
        "v9_nominal_helper": ROOT / "tools/run_winner_v9_nominal_behavior.py",
        "v7_readback_helper": ROOT
        / "tools/run_winner_v7_full_behavior_revalidation.py",
        "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
        "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
        "actuator_model": ROOT / "tools/actuator_bridge_model.py",
        "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
        "v10_nominal_result": ANALYSIS / "winner_v10_nominal_behavior_result.json",
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
        "previous_result": previous_path,
    }
    policies = {
        "half": args.policy_half.resolve(),
        "final": args.policy_final.resolve(),
    }
    next_condition = (
        conditions[args.condition_index + 1]
        if args.condition_index + 1 < len(conditions)
        else None
    )
    payload = {
        "schema_version": "open_duck_mini.winner_v10_r2_condition_preregistration.v1",
        "status": f"FROZEN_WINNER_V10_R2_CONDITION{args.condition_index + 1}_NOT_RUN",
        "condition_index": args.condition_index,
        "condition": condition,
        "next_condition": next_condition,
        "causal_question": f"Does Winner-v10 preserve its complete behavior and protection gate at isolated R2 condition {args.condition_index + 1}, {condition['id']}?",
        "previous_result": {
            "path": str(previous_relative).replace("\\", "/"),
            "sha256": sha256(previous_path),
            "required_status": required_previous_status,
            "required_decision": required_previous_decision,
        },
        "input_hashes": {name: sha256(path) for name, path in input_paths.items()},
        "policy_hashes": {name: sha256(path) for name, path in policies.items()},
        "playground": nominal_prereg["playground"],
        "matrix": nominal_prereg["matrix"],
        "behavior_gates": nominal_prereg["behavior_gates"],
        "protection_gate": nominal_prereg["protection_gate"],
        "result_status": {
            "pass": status_name("PASS", args.condition_index, condition["id"]),
            "hold": status_name("HOLD", args.condition_index, condition["id"]),
        },
        "result_decision": {
            "pass": (
                f"AUTHORIZE_WINNER_V10_R2_CONDITION{args.condition_index + 2}_PREREGISTRATION_ONLY"
                if next_condition is not None
                else "AUTHORIZE_WINNER_V10_R3_CONTRACT_PREREGISTRATION_ONLY"
            ),
            "hold": "STOP_WINNER_V10_R2_AT_FIRST_FAILED_CONDITION",
        },
        "pass_rule": [
            "the prior imported condition result exactly authorizes this preregistration and run",
            "all frozen inputs, unchanged policy hashes, and the one-step-inward physical Playground are exact",
            "exactly 16 complete 600-tick cells cover both checkpoints, both measured fits, and all four commands",
            "all x=0 and moving behavior gates and all current, torque, duration, and measured-rate gates pass",
            "every evaluation requests only the exact frozen condition override and returns a nonempty exact readback",
            "CPU only; no later condition, training, GPU, runtime, robot, torque, motion, or Gate 5 work occurs",
        ],
        "no_retry_or_tuning": f"A failed result stops Winner-v10 R2 at condition {args.condition_index + 1}. Do not change policy, XML, fit, command, seed, duration, endpoint, gate, tolerance, simulator, or population.",
        "pass_authorizes_only": (
            f"write a separate condition-{args.condition_index + 2} preregistration"
            if next_condition is not None
            else "write a separate R3 evaluator-contract preregistration"
        ),
        "authority": {
            "one_cpu_condition_run": True,
            "next_condition_or_stage_execution": False,
            "training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"PREREGISTRATION={output}")
    print(f"PREREGISTRATION_SHA256={sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
