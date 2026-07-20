#!/usr/bin/env python3
"""Run frozen Winner-v10 R2 condition 1: floor friction 0.5."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

from aggregate_ground_up_robustness_r1 import summarize
from evaluate_ground_up_policy import evaluate
from run_winner_v7_full_behavior_revalidation import (
    eval_args,
    exact_override_readback,
)
from run_winner_v9_nominal_behavior import git_head, sha256, trace_summary


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v10_r2_condition1_preregistration.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
FIT_PATHS = {
    "p30": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json",
}
FROZEN_PATHS = {
    "runner": Path(__file__),
    "v10_nominal_runner": ROOT / "tools/run_winner_v10_nominal_behavior.py",
    "v9_nominal_helper": ROOT / "tools/run_winner_v9_nominal_behavior.py",
    "v7_readback_helper": ROOT
    / "tools/run_winner_v7_full_behavior_revalidation.py",
    "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
    "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
    "actuator_model": ROOT / "tools/actuator_bridge_model.py",
    "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
    "v10_nominal_result": ANALYSIS / "winner_v10_nominal_behavior_result.json",
    "r2_matrix": ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json",
    "r2_evaluator_contract": ANALYSIS
    / "ground_up_robustness_r2_evaluator_contract.json",
    "r2_reporting_contract": ANALYSIS
    / "ground_up_robustness_r2_reporting_contract.json",
    "current_contract": ANALYSIS
    / "winner_v3_current_gate_application_contract.json",
    "reference_feature_table": REFERENCE,
    "fit_p30": FIT_PATHS["p30"],
    "fit_p31_34": FIT_PATHS["p31_34"],
}


def flatten(matrices: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for fit in matrices.values() for row in fit.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists() or output.exists():
        raise FileExistsError("Winner-v10 R2 condition-1 output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {name: sha256(path) for name, path in FROZEN_PATHS.items()}
    if observed_hashes != prereg["input_hashes"]:
        raise ValueError("Winner-v10 R2 condition-1 frozen input mismatch")
    policies = {
        "half": args.policy_half.resolve(),
        "final": args.policy_final.resolve(),
    }
    observed_policy_hashes = {name: sha256(path) for name, path in policies.items()}
    if observed_policy_hashes != prereg["policy_hashes"]:
        raise ValueError("Winner-v10 R2 condition-1 policy mismatch")
    observed_commit = git_head(playground)
    observed_files = {
        name: sha256(playground / name)
        for name in prereg["playground"]["required_file_hashes"]
    }
    if (
        observed_commit != prereg["playground"]["required_commit"]
        or observed_files != prereg["playground"]["required_file_hashes"]
    ):
        raise ValueError("Winner-v10 R2 condition-1 Playground mismatch")

    condition = prereg["condition"]
    override = condition["override"]
    matrix = prereg["matrix"]
    protection_gate = prereg["protection_gate"]
    matrices: dict[str, Any] = {}
    all_traces = []
    for fit_id, fit_path in FIT_PATHS.items():
        matrices[fit_id] = {}
        for label, policy in policies.items():
            block = work_root / "blocks" / fit_id / label
            block.mkdir(parents=True)
            eval_path = block / "eval.json"
            trace_dir = block / "traces"
            trace_dir.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                evaluation = evaluate(
                    eval_args(
                        policy,
                        playground,
                        fit_path,
                        override,
                        eval_path,
                        trace_dir,
                        matrix,
                    )
                )
            eval_path.write_text(
                json.dumps(evaluation, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            behavior = summarize(
                eval_path, prereg["behavior_gates"]["x0"], matrix["seed"]
            )
            traces = []
            for command in matrix["commands_x"]:
                trace_path = trace_dir / (
                    f"x{command:.3f}_seed{matrix['seed']}_{policy.stem}.jsonl"
                )
                trace = trace_summary(trace_path, protection_gate)
                trace["command_x"] = command
                traces.append(trace)
                all_traces.append(trace)
            matrices[fit_id][label] = {
                "behavior": behavior,
                "protection_pass": all(trace["pass"] for trace in traces),
                "traces": traces,
                "override_and_readbacks_exact": evaluation["inputs"].get(
                    "eval_dynamics_override"
                )
                == override
                and exact_override_readback(evaluation, override),
                "eval_path": str(eval_path),
                "eval_sha256": sha256(eval_path),
            }

    blocks = flatten(matrices)
    evaluator_contract = json.loads(
        FROZEN_PATHS["r2_evaluator_contract"].read_text(encoding="utf-8")
    )
    reporting_contract = json.loads(
        FROZEN_PATHS["r2_reporting_contract"].read_text(encoding="utf-8")
    )
    checks = {
        "frozen_input_hashes_exact": observed_hashes == prereg["input_hashes"],
        "policy_hashes_exact": observed_policy_hashes == prereg["policy_hashes"],
        "playground_commit_and_files_exact": observed_commit
        == prereg["playground"]["required_commit"]
        and observed_files == prereg["playground"]["required_file_hashes"],
        "existing_r2_evaluator_and_reporting_contracts_passed": evaluator_contract[
            "status"
        ]
        == "PASS_ROBUSTNESS_R2_EVALUATOR_CONTRACT"
        and reporting_contract["status"]
        == "PASS_ROBUSTNESS_R2_REPORTING_CONTRACT",
        "exact_frozen_first_condition": condition["id"] == "FLOOR_FRICTION_LO"
        and override == {"floor_friction": 0.5},
        "exactly_16_complete_contiguous_cells": len(all_traces) == 16
        and all(
            trace["rows"] == 600 and trace["ticks_contiguous"]
            for trace in all_traces
        ),
        "all_four_behavior_matrices_pass": all(
            block["behavior"]["matrix_pass"] for block in blocks
        ),
        "all_current_torque_duration_and_full_vector_gates_pass": all(
            block["protection_pass"] for block in blocks
        ),
        "all_requested_overrides_and_readbacks_exact": all(
            block["override_and_readbacks_exact"] for block in blocks
        ),
        "cpu_only_no_training_or_reward_selection": os.environ["JAX_PLATFORMS"]
        == "cpu"
        and os.environ["CUDA_VISIBLE_DEVICES"] == ""
        and os.environ["HIP_VISIBLE_DEVICES"] == "",
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V10_R2_CONDITION1_FLOOR_FRICTION_LO"
        if not failed
        else "HOLD_WINNER_V10_R2_CONDITION1_FLOOR_FRICTION_LO"
    )
    result = {
        "schema_version": "open_duck_mini.winner_v10_r2_condition1_result.v1",
        "status": status,
        "decision": "AUTHORIZE_WINNER_V10_R2_CONDITION2_PREREGISTRATION_ONLY"
        if not failed
        else "STOP_WINNER_V10_R2_AT_FIRST_FAILED_CONDITION",
        "preregistration_sha256": sha256(PREREG),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": observed_hashes,
        "policy_hashes": observed_policy_hashes,
        "playground_commit": observed_commit,
        "playground_file_hashes": observed_files,
        "condition": condition,
        "matrices": matrices,
        "authority": {
            "condition2_preregistration_design": not failed,
            "later_condition_execution": False,
            "training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
