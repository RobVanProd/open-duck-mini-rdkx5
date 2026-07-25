#!/usr/bin/env python3
"""Run the preregistered two-cell V131 two-fit oracle CPU contract."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v103_response_conditioned_behavior import REFERENCE  # noqa: E402
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v131_two_fit_oracle_cpu_preregistration.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v131_two_fit_oracle_cpu_contract.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V131_TWO_FIT_ORACLE_CPU_CONTRACT_20260724.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location(
        "closed_loop_sim_eval_v131_two_fit", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load V131 evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    evaluator_root = args.evaluator_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V131: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v130_result": sha256(
            ANALYSIS / "winner_v130_oracle_correction_feature_audit.json"
        ),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "composer": sha256(
            ROOT / "tools/compose_winner_v131_two_fit_oracle_evaluator.py"
        ),
        "two_fit_projector": sha256(
            ROOT / "tools/exact_torque_oracle_two_fit.py"
        ),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V131_TWO_FIT_ORACLE_CPU_CONTRACT"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or manifest.get("status")
        != "PASS_WINNER_V131_TWO_FIT_EVALUATOR_COMPOSITION"
    ):
        raise ValueError("V131 CPU preregistration changed")
    evaluator = load_evaluator(evaluator_path)
    policy_spec = next(
        item
        for item in v126["policies"]
        if item["id"] == "V121_TRAIN_MATCHED_FINAL"
    )
    policy = (
        Path(v126["external_inputs"]["policy_root"])
        / policy_spec["filename"]
    )
    if sha256(policy) != policy_spec["sha256"]:
        raise ValueError("V131 source policy changed")
    playground = Path(v126["external_inputs"]["playground"])
    rows = [
        row
        for row in v126["matrix"]["rows"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_FINAL"
        and float(row["command_x_m_s"]) == 0.08
    ]
    if len(rows) != 2:
        raise ValueError("V131 CPU matrix must contain two x=.08 cells")
    action_delta = tuple(
        float(value) for value in v126["oracle"]["action_delta"]
    )
    run_root.mkdir(parents=True)
    cell_results = []
    for row in rows:
        active = str(row["plant"])
        shadow = (
            "P31_34_PITCH_WITH_P30_NONPITCH"
            if active == "P30_ALL_JOINT"
            else "P30_ALL_JOINT"
        )
        trace_path = run_root / f"{active.lower()}.jsonl"
        with contextlib.redirect_stdout(io.StringIO()):
            result = evaluator.run_closed_loop_sim(
                evaluator.ClosedLoopConfig(
                    policy_path=policy,
                    fit=actuator_fit(base_prereg, active),
                    playground_root=playground,
                    command_x=0.08,
                    duration_s=64 * 0.02,
                    bridge_mode="fitted",
                    expected_observation_dim=115,
                    task="flat_terrain_backlash",
                    seed=int(row["seed"]),
                    eval_role="candidate",
                    reset_mode="home-support",
                    policy_obs_input_name="obs",
                    policy_action_output_name="continuous_actions",
                    policy_state_input_names=("h_in", "previous_action"),
                    policy_state_output_names=("h_out", "previous_action_out"),
                    policy_graph_authoritative_output=True,
                    policy_applied_target_observation=True,
                    reference_feature_table_path=REFERENCE,
                    reference_start_phase=0,
                    trace_jsonl=trace_path,
                    trace_full_obs=True,
                    winner_v3_home_relative_actuator_gain=True,
                    exact_torque_oracle_enabled=True,
                    exact_torque_oracle_limit_nm=1.91229675,
                    exact_torque_oracle_guard_rad=0.165,
                    exact_torque_oracle_action_delta=action_delta,
                    exact_torque_oracle_force_tolerance_nm=5.0e-6,
                    exact_torque_oracle_monotonicity_tolerance_nm=5.0e-6,
                    exact_torque_oracle_grid_points=9,
                    exact_torque_oracle_bisection_iterations=32,
                    exact_torque_oracle_maximum_coordinate_passes=14,
                    exact_torque_oracle_schedule_ticks=None,
                    exact_torque_oracle_shadow_fit=actuator_fit(
                        base_prereg, shadow
                    ),
                    exact_torque_oracle_maximum_fit_passes=14,
                )
            )
        trace_rows = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        oracle_rows = [
            item["exact_torque_oracle"]
            for item in trace_rows
            if isinstance(item.get("exact_torque_oracle"), dict)
        ]
        robust_rows = [
            item for item in oracle_rows if "robust_safe" in item
        ]
        mode = ((result.get("modes") or {}).get("fitted") or {})
        oracle_summary = mode.get("exact_torque_oracle") or {}
        cell_results.append(
            {
                "active_plant": active,
                "shadow_plant": shadow,
                "simulator_status": result.get("status"),
                "samples": mode.get("samples"),
                "termination_reason": mode.get("termination_reason"),
                "trace_path": str(trace_path),
                "trace_sha256": sha256(trace_path),
                "trace_rows": len(trace_rows),
                "robust_rows": len(robust_rows),
                "robust_safe_rows": sum(
                    bool(item["robust_safe"]) for item in robust_rows
                ),
                "empty_intersection_events": sum(
                    len(item["empty_intersection_joint_indices"])
                    for item in robust_rows
                ),
                "projected_joint_events": sum(
                    len(item["projected_joint_indices"])
                    for item in robust_rows
                ),
                "maximum_clip_linf": max(
                    (
                        float(item["clip_linf"])
                        for item in robust_rows
                    ),
                    default=0.0,
                ),
                "oracle_summary": oracle_summary,
            }
        )
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "two_cells_exact": len(cell_results) == 2,
        "both_duration_complete_64": all(
            row["samples"] == 64
            and row["termination_reason"] == "duration_complete"
            and row["trace_rows"] == 64
            for row in cell_results
        ),
        "all_128_rows_use_two_fit_oracle": all(
            row["robust_rows"] == 64 for row in cell_results
        ),
        "all_two_fit_rows_robust_safe": all(
            row["robust_safe_rows"] == 64 for row in cell_results
        ),
        "zero_common_intersection_failures": all(
            row["empty_intersection_events"] == 0
            for row in cell_results
        ),
        "at_least_one_shared_projection": sum(
            row["projected_joint_events"] for row in cell_results
        )
        > 0,
        "primary_prediction_exact": all(
            bool(row["oracle_summary"].get("prediction_exact"))
            and int(
                row["oracle_summary"].get("prediction_mismatches", -1)
            )
            == 0
            for row in cell_results
        ),
        "zero_primary_nonempty_residual_violations": all(
            int(
                row["oracle_summary"].get(
                    "nonempty_residual_violations", -1
                )
            )
            == 0
            for row in cell_results
        ),
        "formal_behavior_cells_zero": True,
        "hosted_compute_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v131.two_fit_oracle_cpu_contract.v1",
        "status": (
            "PASS_WINNER_V131_TWO_FIT_ORACLE_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V131_TWO_FIT_ORACLE_CPU_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "cells": cell_results,
        "decision": (
            "EARN_ONE_V131_FINAL_TEACHER_8_CELL_PREREGISTRATION"
            if not failed
            else "NO_TWO_FIT_ORACLE_BEHAVIOR_SCREEN"
        ),
        "authority": {
            "final_teacher_behavior_preregistration": not failed,
            "formal_behavior": False,
            "training": False,
            "hosted_training": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V131 two-fit oracle CPU contract\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Decision: `{payload['decision']}`\n"
        f"- Projected events: "
        f"`{sum(row['projected_joint_events'] for row in cell_results)}`.\n"
        "- Two nonformal 64-tick CPU cells; no training or behavior gate.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
