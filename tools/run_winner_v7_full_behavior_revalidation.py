#!/usr/bin/env python3
"""Run the frozen winner-v7 128-cell CPU behavior revalidation."""

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
import onnx

from aggregate_ground_up_robustness_r1 import summarize
from evaluate_ground_up_policy import evaluate
from run_winner_v7_inward_projection_contract import transform


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v7_full_behavior_revalidation_preregistration.json"
V7_RESULT = ANALYSIS / "winner_v7_inward_projection_contract_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
FIT_PATHS = {
    "p30": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json",
}
POLICY_SOURCE_PATHS = {
    "half": ANALYSIS / "ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    "final": ANALYSIS / "ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
}
FROZEN_PATHS = {
    "runner": Path(__file__),
    "composer": ROOT / "tools/compose_winner_v7_playground.py",
    "transformer": ROOT / "tools/run_winner_v7_inward_projection_contract.py",
    "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
    "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
    "actuator_model": ROOT / "tools/actuator_bridge_model.py",
    "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
    "v7_preregistration": ANALYSIS / "winner_v7_inward_projection_preregistration.json",
    "v7_result": V7_RESULT,
    "r2_preregistration": ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json",
    "r2_evaluator_contract": ANALYSIS / "ground_up_robustness_r2_evaluator_contract.json",
    "r2_reporting_contract": ANALYSIS / "ground_up_robustness_r2_reporting_contract.json",
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


def composed_playground_hashes(playground: Path, prereg: dict[str, Any]) -> dict[str, str]:
    return {
        name: sha256(playground / name)
        for name in prereg["playground"]["required_composed_file_hashes"]
    }


def max_consecutive(mask: np.ndarray) -> int:
    best = run = 0
    for value in mask.tolist():
        run = run + 1 if value else 0
        best = max(best, run)
    return best


def current_trace_summary(path: Path, gate: dict[str, Any]) -> dict[str, Any]:
    forces = []
    ticks = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("mode") != "fitted":
                continue
            forces.append(row["actuator_force_nm"])
            ticks.append(int(row["tick"]))
    currents = np.abs(np.asarray(forces, dtype=np.float64)) / CURRENT_NM_PER_A
    if currents.ndim != 2 or currents.shape[1] != 14:
        raise ValueError(f"invalid current trace shape: {path}: {currents.shape}")
    per_joint_peak = np.max(currents, axis=0)
    consecutive = np.asarray(
        [
            max_consecutive(currents[:, index] > gate["strict_overcurrent_threshold_a"])
            for index in range(14)
        ],
        dtype=int,
    )
    p95 = np.percentile(currents, 95, axis=0)
    passed = bool(
        np.all(per_joint_peak <= gate["per_joint_peak_current_a_max"])
        and np.all(consecutive <= gate["strict_overcurrent_max_consecutive_ticks"])
    )
    return {
        "path": str(path),
        "sha256": sha256(path),
        "rows": len(ticks),
        "ticks_contiguous": ticks == list(range(len(ticks))),
        "worst_peak_current_a": float(np.max(per_joint_peak)),
        "worst_rated_current_p95_a_diagnostic": float(np.max(p95)),
        "maximum_consecutive_ticks_above_2a": int(np.max(consecutive)),
        "pass": passed,
    }


def exact_override_readback(payload: dict[str, Any], override: Any) -> bool:
    if override is None:
        return all(
            (row.get("dynamics_override") or {}).get("enabled") is False
            for row in payload["runs"]
        )
    key, expected = next(iter(override.items()))
    for row in payload["runs"]:
        report = row.get("dynamics_override") or {}
        if report.get("enabled") is not True or report.get("key") != key:
            return False
        actual = report.get("value")
        if key == "joint_qpos0_offset_rad" and isinstance(expected, (int, float)):
            value_ok = isinstance(actual, list) and len(actual) == 14 and all(
                float(item) == float(expected) for item in actual
            )
        else:
            value_ok = actual == expected
        if not value_ok or not isinstance(report.get("readback"), dict) or not report["readback"]:
            return False
    return True


def eval_args(
    policy: Path,
    playground: Path,
    fit: Path,
    override: Any,
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
        eval_dynamics_override_json=None if override is None else json.dumps(override),
        reset_mode="home-support",
        policy_action_rate_limit_rad_s=None,
        policy_action_rate_limit_joint_indices="2,3,4,11,12,13",
        policy_action_rate_limit_values="",
        output_json=str(eval_path),
        output_md=None,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists() or output.exists():
        raise FileExistsError("winner-v7 behavior output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    observed_hashes = {name: sha256(path) for name, path in FROZEN_PATHS.items()}
    if observed_hashes != prereg["input_hashes"]:
        raise ValueError("frozen winner-v7 behavior input hash mismatch")
    observed_playground_commit = git_head(playground)
    if observed_playground_commit != prereg["playground"]["required_commit"]:
        raise ValueError("playground commit mismatch")
    observed_playground_files = composed_playground_hashes(playground, prereg)
    if observed_playground_files != prereg["playground"]["required_composed_file_hashes"]:
        raise ValueError("composed 115-D Playground file hash mismatch")

    policy_paths = {}
    transformed_hashes = {}
    for row in prereg["policies"]:
        label = row["label"]
        source_path = POLICY_SOURCE_PATHS[label]
        policy_path = work_root / "policies" / f"winner_v7_{label}.onnx"
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        onnx.save(transform(onnx.load(source_path)), policy_path)
        observed = sha256(policy_path)
        if observed != row["transformed_sha256"]:
            raise ValueError(f"transformed policy hash mismatch: {label}")
        policy_paths[label] = policy_path
        transformed_hashes[label] = observed

    x0_gate = prereg["behavior_gates"]["x0"]
    current_gate = prereg["current_gate"]
    matrix = prereg["matrix"]
    condition_rows = []
    all_trace_rows = []
    for condition in matrix["conditions_in_order"]:
        condition_id = condition["id"]
        matrices = {}
        for fit_id, fit_path in FIT_PATHS.items():
            matrices[fit_id] = {}
            for label, policy_path in policy_paths.items():
                block = work_root / "blocks" / condition_id / fit_id / label
                block.mkdir(parents=True, exist_ok=True)
                eval_path = block / "eval.json"
                trace_dir = block / "traces"
                trace_dir.mkdir(parents=True, exist_ok=True)
                with contextlib.redirect_stdout(io.StringIO()):
                    payload = evaluate(
                        eval_args(
                            policy_path,
                            playground,
                            fit_path,
                            condition["override"],
                            eval_path,
                            trace_dir,
                            matrix,
                        )
                    )
                eval_path.write_text(
                    json.dumps(payload, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                behavior = summarize(eval_path, x0_gate, matrix["seed"])
                traces = []
                for command in matrix["commands_x"]:
                    trace_path = trace_dir / (
                        f"x{command:.3f}_seed{matrix['seed']}_{policy_path.stem}.jsonl"
                    )
                    current = current_trace_summary(trace_path, current_gate)
                    current["command_x"] = command
                    traces.append(current)
                    all_trace_rows.append(current)
                current_pass = all(row["pass"] for row in traces)
                matrices[fit_id][label] = {
                    "behavior": behavior,
                    "current": {
                        "pass": current_pass,
                        "worst_peak_current_a": max(
                            row["worst_peak_current_a"] for row in traces
                        ),
                        "worst_rated_current_p95_a_diagnostic": max(
                            row["worst_rated_current_p95_a_diagnostic"] for row in traces
                        ),
                        "maximum_consecutive_ticks_above_2a": max(
                            row["maximum_consecutive_ticks_above_2a"] for row in traces
                        ),
                        "traces": traces,
                    },
                    "override_and_readbacks_exact": exact_override_readback(
                        payload, condition["override"]
                    ),
                    "eval_path": str(eval_path),
                    "eval_sha256": sha256(eval_path),
                }
        flat = [item for fit in matrices.values() for item in fit.values()]
        behavior_pass = all(item["behavior"]["matrix_pass"] for item in flat)
        current_pass = all(item["current"]["pass"] for item in flat)
        readback_pass = all(item["override_and_readbacks_exact"] for item in flat)
        expected_outcome = (
            behavior_pass
            if condition["expected"] == "PASS"
            else not any(item["behavior"]["matrix_pass"] for item in flat)
        )
        condition_rows.append({
            "id": condition_id,
            "expected": condition["expected"],
            "override": condition["override"],
            "behavior_expectation_pass": expected_outcome,
            "all_current_protection_pass": current_pass,
            "all_override_readbacks_exact": readback_pass,
            "matrices": matrices,
        })

    checks = {
        "frozen_input_hashes_exact": observed_hashes == prereg["input_hashes"],
        "playground_commit_exact": observed_playground_commit
        == prereg["playground"]["required_commit"],
        "composed_115d_playground_files_exact": observed_playground_files
        == prereg["playground"]["required_composed_file_hashes"],
        "transformed_policy_hashes_exact": transformed_hashes
        == {row["label"]: row["transformed_sha256"] for row in prereg["policies"]},
        "exactly_128_cells": len(condition_rows) == 8
        and len(all_trace_rows) == matrix["total_cells"],
        "all_trace_ticks_contiguous": all(row["ticks_contiguous"] for row in all_trace_rows),
        "all_conditions_match_frozen_behavior_expectation": all(
            row["behavior_expectation_pass"] for row in condition_rows
        ),
        "all_current_protection_gates_pass": all(
            row["all_current_protection_pass"] for row in condition_rows
        ),
        "all_dynamics_override_readbacks_exact": all(
            row["all_override_readbacks_exact"] for row in condition_rows
        ),
        "cpu_only": os.environ["CUDA_VISIBLE_DEVICES"] == ""
        and os.environ["HIP_VISIBLE_DEVICES"] == ""
        and os.environ["JAX_PLATFORMS"] == "cpu",
        "no_training_or_reward_selection": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V7_FULL_BEHAVIOR_REVALIDATION"
        if not failed
        else "HOLD_WINNER_V7_FULL_BEHAVIOR_REVALIDATION"
    )
    result = {
        "schema_version": "winner_v7.full_behavior_revalidation_raw_result.v1",
        "status": status,
        "decision": (
            "AUTHORIZE_DISTINCT_WINNER_V7_AUTOMATIC_CALIBRATION_INTERFACE_PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_WINNER_V7_PROTECTED_BASE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "preregistration_sha256": sha256(PREREGISTRATION),
        "input_hashes": observed_hashes,
        "playground_commit": observed_playground_commit,
        "composed_playground_file_hashes": observed_playground_files,
        "transformed_policy_hashes": transformed_hashes,
        "conditions": condition_rows,
        "authority": {
            "automatic_calibration_interface_preregistration_design": not failed,
            "training_ppo_colab_gpu": False,
            "runtime_or_gate5": False,
            "rdkx5_robot_torque_motion_deployment": False,
            "robot_clearance": False,
        },
    }
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
