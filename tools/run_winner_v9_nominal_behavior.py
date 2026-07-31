#!/usr/bin/env python3
"""Run the frozen 16-cell winner-v9 nominal behavior/current/torque gate."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from aggregate_ground_up_robustness_r1 import summarize
from evaluate_ground_up_policy import evaluate


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v9_nominal_behavior_preregistration.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
FIT_PATHS = {
    "p30": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json",
}
FROZEN_PATHS = {
    "runner": Path(__file__),
    "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
    "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
    "actuator_model": ROOT / "tools/actuator_bridge_model.py",
    "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
    "v9_contract_result": ANALYSIS / "winner_v9_stored_bound_contract_result.json",
    "current_contract": ANALYSIS / "winner_v3_current_gate_application_contract.json",
    "reference_feature_table": REFERENCE,
    "fit_p30": FIT_PATHS["p30"],
    "fit_p31_34": FIT_PATHS["p31_34"],
}
CURRENT_NM_PER_A = 0.784532


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def max_consecutive(mask: np.ndarray) -> int:
    longest = current = 0
    for value in mask.tolist():
        current = current + 1 if value else 0
        longest = max(longest, current)
    return longest


def trace_summary(path: Path, gate: dict[str, Any]) -> dict[str, Any]:
    forces = []
    full_rate_excess = []
    ticks = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("mode") != "fitted":
                continue
            forces.append(row["actuator_force_nm"])
            full_rate_excess.append(row["conservative_rate_excess_rad_s"])
            ticks.append(int(row["tick"]))
    torque = np.abs(np.asarray(forces, dtype=np.float64))
    rate_excess = np.asarray(full_rate_excess, dtype=np.float64)
    if torque.ndim != 2 or torque.shape[1] != 14 or rate_excess.shape != torque.shape:
        raise ValueError(f"invalid winner-v9 trace shape: {path}")
    current = torque / CURRENT_NM_PER_A
    peak_torque = np.max(torque, axis=0)
    peak_current = np.max(current, axis=0)
    consecutive = np.asarray(
        [
            max_consecutive(
                current[:, index] > gate["strict_overcurrent_threshold_a"]
            )
            for index in range(14)
        ]
    )
    passed = bool(
        np.all(peak_torque <= gate["per_joint_peak_torque_nm_max"])
        and np.all(peak_current <= gate["per_joint_peak_current_a_max"])
        and np.all(consecutive <= gate["strict_overcurrent_max_consecutive_ticks"])
        and np.max(rate_excess) == 0.0
    )
    force_limit = float(gate["per_joint_peak_torque_nm_max"])
    return {
        "path": str(path),
        "sha256": sha256(path),
        "rows": len(ticks),
        "ticks_contiguous": ticks == list(range(len(ticks))),
        "worst_peak_torque_nm": float(np.max(peak_torque)),
        "worst_peak_current_a": float(np.max(peak_current)),
        "worst_rated_current_p95_a_diagnostic": float(np.max(np.percentile(current, 95, axis=0))),
        "maximum_consecutive_ticks_above_2a": int(np.max(consecutive)),
        "maximum_full_measured_vector_excess_rad_s": float(np.max(rate_excess)),
        "force_limit_hit_ticks": int(
            np.sum(np.abs(torque - force_limit) <= 1e-7)
        ),
        "pass": passed,
    }


def eval_args(
    policy: Path,
    playground: Path,
    fit: Path,
    eval_path: Path,
    trace_dir: Path,
    matrix: dict[str, Any],
) -> SimpleNamespace:
    return SimpleNamespace(
        policy=str(policy),
        playground_root=str(playground),
        fit=str(fit),
        reference_feature_table=str(REFERENCE),
        reference_start_phase=0,
        expected_observation_dim=115,
        policy_state_input_names="previous_action",
        policy_state_output_names="previous_action_out",
        policy_applied_target_observation=True,
        policy_observer_fit=None,
        policy_reset_com_estimator_input=False,
        trace_dir=trace_dir,
        trace_full_obs=False,
        trace_com_accelerometer_map_ticks="",
        commands=",".join(str(item) for item in matrix["commands_x"]),
        seeds=str(matrix["seed"]),
        duration_s=matrix["duration_ticks"] / matrix["frequency_hz"],
        minimum_emergence_duration_s=1.08,
        task="flat_terrain_backlash",
        eval_dynamics_override_json=None,
        reset_mode="home-support",
        policy_action_rate_limit_rad_s=None,
        policy_action_rate_limit_joint_indices="0,1,2,3,4,5,6,7,8,9,10,11,12,13",
        policy_action_rate_limit_values="",
        output_json=str(eval_path),
        output_md=None,
    )


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
        raise FileExistsError("winner-v9 nominal output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {name: sha256(path) for name, path in FROZEN_PATHS.items()}
    if observed_hashes != prereg["input_hashes"]:
        raise ValueError("winner-v9 nominal frozen input mismatch")
    policy_paths = {"half": args.policy_half.resolve(), "final": args.policy_final.resolve()}
    observed_policy_hashes = {name: sha256(path) for name, path in policy_paths.items()}
    if observed_policy_hashes != prereg["policy_hashes"]:
        raise ValueError("winner-v9 policy hash mismatch")
    observed_commit = git_head(playground)
    if observed_commit != prereg["playground"]["required_commit"]:
        raise ValueError("winner-v9 playground commit mismatch")
    observed_files = {
        path: sha256(playground / path)
        for path in prereg["playground"]["required_file_hashes"]
    }
    if observed_files != prereg["playground"]["required_file_hashes"]:
        raise ValueError("winner-v9 playground file mismatch")

    current_gate = prereg["protection_gate"]
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
                payload = evaluate(
                    eval_args(
                        policy_path, playground, fit_path, eval_path, trace_dir, matrix
                    )
                )
            eval_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            behavior = summarize(eval_path, prereg["behavior_gates"]["x0"], matrix["seed"])
            traces = []
            for command in matrix["commands_x"]:
                trace_path = trace_dir / (
                    f"x{command:.3f}_seed{matrix['seed']}_{policy_path.stem}.jsonl"
                )
                row = trace_summary(trace_path, current_gate)
                row["command_x"] = command
                traces.append(row)
                all_traces.append(row)
            matrices[fit_id][label] = {
                "behavior": behavior,
                "protection_pass": all(row["pass"] for row in traces),
                "traces": traces,
                "dynamics_override_disabled": all(
                    (run.get("dynamics_override") or {}).get("enabled") is False
                    for run in payload["runs"]
                ),
                "eval_path": str(eval_path),
                "eval_sha256": sha256(eval_path),
            }
    flat = [row for fit in matrices.values() for row in fit.values()]
    checks = {
        "frozen_input_hashes_exact": observed_hashes == prereg["input_hashes"],
        "policy_hashes_exact": observed_policy_hashes == prereg["policy_hashes"],
        "playground_commit_and_files_exact": observed_commit == prereg["playground"]["required_commit"] and observed_files == prereg["playground"]["required_file_hashes"],
        "exactly_16_complete_contiguous_cells": len(all_traces) == 16 and all(row["rows"] == 600 and row["ticks_contiguous"] for row in all_traces),
        "all_four_behavior_matrices_pass": all(row["behavior"]["matrix_pass"] for row in flat),
        "all_current_torque_duration_and_full_vector_gates_pass": all(row["protection_pass"] for row in flat),
        "all_dynamics_overrides_disabled": all(row["dynamics_override_disabled"] for row in flat),
        "cpu_only_no_training_or_reward_selection": os.environ["JAX_PLATFORMS"] == "cpu" and os.environ["CUDA_VISIBLE_DEVICES"] == "" and os.environ["HIP_VISIBLE_DEVICES"] == "",
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_WINNER_V9_NOMINAL_BEHAVIOR" if not failed else "HOLD_WINNER_V9_NOMINAL_BEHAVIOR"
    result = {
        "schema_version": "open_duck_mini.winner_v9_nominal_behavior_result.v1",
        "status": status,
        "decision": "AUTHORIZE_WINNER_V9_SEQUENTIAL_ROBUSTNESS_PREREGISTRATION_ONLY" if not failed else "CLOSE_WINNER_V9_POLICY_ROUTE",
        "preregistration_sha256": sha256(PREREG),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": observed_hashes,
        "policy_hashes": observed_policy_hashes,
        "playground_commit": observed_commit,
        "playground_file_hashes": observed_files,
        "matrices": matrices,
        "authority": {"robustness_preregistration_design": not failed, "behavior_retry_training_gpu_colab": False, "runtime_robot_torque_motion_gate5": False, "robot_clearance": False},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
