#!/usr/bin/env python3
"""Run the frozen 16-cell winner-v10 nominal behavior/protection gate."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
from typing import Any

from aggregate_ground_up_robustness_r1 import summarize
from evaluate_ground_up_policy import evaluate
from run_winner_v9_nominal_behavior import (
    eval_args,
    git_head,
    sha256,
    trace_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v10_nominal_behavior_preregistration.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
FIT_PATHS = {
    "p30": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json",
}
FROZEN_PATHS = {
    "runner": Path(__file__),
    "v9_nominal_helper": ROOT / "tools/run_winner_v9_nominal_behavior.py",
    "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
    "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
    "actuator_model": ROOT / "tools/actuator_bridge_model.py",
    "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
    "v10_contract_result": ANALYSIS
    / "winner_v10_inward_torque_contract_result.json",
    "current_contract": ANALYSIS / "winner_v3_current_gate_application_contract.json",
    "reference_feature_table": REFERENCE,
    "fit_p30": FIT_PATHS["p30"],
    "fit_p31_34": FIT_PATHS["p31_34"],
}


def flatten(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for fit in payload["matrices"].values() for row in fit.values()]


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
        raise FileExistsError("winner-v10 nominal output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {name: sha256(path) for name, path in FROZEN_PATHS.items()}
    if observed_hashes != prereg["input_hashes"]:
        raise ValueError("winner-v10 nominal frozen input mismatch")
    policy_paths = {
        "half": args.policy_half.resolve(),
        "final": args.policy_final.resolve(),
    }
    observed_policy_hashes = {
        name: sha256(path) for name, path in policy_paths.items()
    }
    if observed_policy_hashes != prereg["policy_hashes"]:
        raise ValueError("winner-v10 policy hash mismatch")
    observed_commit = git_head(playground)
    if observed_commit != prereg["playground"]["required_commit"]:
        raise ValueError("winner-v10 Playground commit mismatch")
    observed_files = {
        path: sha256(playground / path)
        for path in prereg["playground"]["required_file_hashes"]
    }
    if observed_files != prereg["playground"]["required_file_hashes"]:
        raise ValueError("winner-v10 Playground file mismatch")

    protection_gate = prereg["protection_gate"]
    matrix = prereg["matrix"]
    matrices: dict[str, Any] = {}
    all_traces = []
    for fit_id, fit_path in FIT_PATHS.items():
        matrices[fit_id] = {}
        for label, policy_path in policy_paths.items():
            block = work_root / "blocks" / fit_id / label
            block.mkdir(parents=True)
            eval_path = block / "eval.json"
            trace_dir = block / "traces"
            trace_dir.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                evaluation = evaluate(
                    eval_args(
                        policy_path,
                        playground,
                        fit_path,
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
                    f"x{command:.3f}_seed{matrix['seed']}_{policy_path.stem}.jsonl"
                )
                row = trace_summary(trace_path, protection_gate)
                row["command_x"] = command
                traces.append(row)
                all_traces.append(row)
            matrices[fit_id][label] = {
                "behavior": behavior,
                "protection_pass": all(row["pass"] for row in traces),
                "traces": traces,
                "dynamics_override_disabled": all(
                    (run.get("dynamics_override") or {}).get("enabled") is False
                    for run in evaluation["runs"]
                ),
                "eval_path": str(eval_path),
                "eval_sha256": sha256(eval_path),
            }

    blocks = flatten({"matrices": matrices})
    checks = {
        "frozen_input_hashes_exact": observed_hashes == prereg["input_hashes"],
        "policy_hashes_exact": observed_policy_hashes == prereg["policy_hashes"],
        "playground_commit_and_files_exact": observed_commit
        == prereg["playground"]["required_commit"]
        and observed_files == prereg["playground"]["required_file_hashes"],
        "exactly_16_complete_contiguous_cells": len(all_traces) == 16
        and all(
            row["rows"] == 600 and row["ticks_contiguous"] for row in all_traces
        ),
        "all_four_behavior_matrices_pass": all(
            row["behavior"]["matrix_pass"] for row in blocks
        ),
        "all_current_torque_duration_and_full_vector_gates_pass": all(
            row["protection_pass"] for row in blocks
        ),
        "all_dynamics_overrides_disabled": all(
            row["dynamics_override_disabled"] for row in blocks
        ),
        "cpu_only_no_training_or_reward_selection": os.environ["JAX_PLATFORMS"]
        == "cpu"
        and os.environ["CUDA_VISIBLE_DEVICES"] == ""
        and os.environ["HIP_VISIBLE_DEVICES"] == "",
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V10_NOMINAL_BEHAVIOR"
        if not failed
        else "HOLD_WINNER_V10_NOMINAL_BEHAVIOR"
    )
    result = {
        "schema_version": "open_duck_mini.winner_v10_nominal_behavior_result.v1",
        "status": status,
        "decision": "AUTHORIZE_WINNER_V10_SEQUENTIAL_ROBUSTNESS_PREREGISTRATION_ONLY"
        if not failed
        else "CLOSE_WINNER_V10_POLICY_ROUTE",
        "preregistration_sha256": sha256(PREREG),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": observed_hashes,
        "policy_hashes": observed_policy_hashes,
        "playground_commit": observed_commit,
        "playground_file_hashes": observed_files,
        "matrices": matrices,
        "authority": {
            "robustness_preregistration_design": not failed,
            "behavior_retry_training_gpu_colab": False,
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
