#!/usr/bin/env python3
"""Fit and freeze the preregistered affine oracle COM residual on CPU."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim
from evaluate_ground_up_policy import emergence_evidence
from oracle_phase_com_controller import CONTACT_MODES, CORRECTED_JOINT_INDICES, FEATURE_NAMES


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "outputs/analysis/oracle_phase_com_corrective_authority.json"
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
FIT = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
CONTROLLER = ROOT / "outputs/analysis/oracle_phase_com_controller.json"
FIT_RESULT = ROOT / "outputs/analysis/oracle_phase_com_controller_fit.json"
POLICIES = (
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
)
ENDPOINTS = (("X_NEG", -0.05), ("X_POS", 0.05))
SCALES = (0.25, 0.5, 0.75, 1.0)
MAX_ACTION_DELTA = [.41919997, .41919997, .12, .12, .12, .41919997, .41919997, .41919997, .41919997, .41919997, .41919997, .10, .08, .10]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fitted_payload(authority: dict[str, Any], selected_scale: float) -> tuple[dict[str, Any], dict[str, Any]]:
    banks: dict[str, dict[str, list[list[float]]]] = {}
    normalization: dict[str, dict[str, dict[str, list[float]]]] = {}
    fit_details = {}
    for sign, condition in (("negative", "X_NEG"), ("positive", "X_POS")):
        banks[sign] = {}
        normalization[sign] = {}
        for mode in CONTACT_MODES:
            rows = [
                row for row in authority["screen_states"]
                if row["condition"] == condition and row["contact_mode"] == mode
            ]
            if not rows:
                coefficients = np.zeros((6, len(FEATURE_NAMES)), dtype=np.float64)
                mean = np.zeros(len(FEATURE_NAMES), dtype=np.float64)
                scale = np.ones(len(FEATURE_NAMES), dtype=np.float64)
                rank = 0
            else:
                x = np.asarray([row["oracle_features"] for row in rows], dtype=np.float64)
                y = np.asarray(
                    [
                        np.asarray(row["selected_residual_action"], dtype=np.float64)[
                            np.asarray(CORRECTED_JOINT_INDICES, dtype=int)
                        ]
                        for row in rows
                    ],
                    dtype=np.float64,
                )
                mean = np.mean(x, axis=0)
                scale = np.std(x, axis=0)
                mean[0] = 0.0
                scale[0] = 1.0
                scale[scale < 1e-9] = 1.0
                xn = x.copy()
                xn[:, 1:] = (xn[:, 1:] - mean[1:]) / scale[1:]
                xn[:, 0] = 1.0
                regularizer = 1e-3 * np.eye(xn.shape[1], dtype=np.float64)
                coefficients = np.linalg.solve(xn.T @ xn + regularizer, xn.T @ y).T
                rank = int(np.linalg.matrix_rank(xn))
            banks[sign][mode] = coefficients.tolist()
            normalization[sign][mode] = {"mean": mean.tolist(), "scale": scale.tolist()}
            fit_details[f"{sign}/{mode}"] = {
                "samples": len(rows),
                "design_rank": rank,
                "coefficient_max_abs": float(np.max(np.abs(coefficients))),
            }
    payload = {
        "schema_version": "oracle_phase_com_controller.v1",
        "status": "FROZEN_ORACLE_PHASE_COM_CONTROLLER",
        "feature_names": list(FEATURE_NAMES),
        "contact_modes": list(CONTACT_MODES),
        "corrected_joint_indices": list(CORRECTED_JOINT_INDICES),
        "residual_normalized_limit": 0.08,
        "residual_target_limit_rad": 0.02,
        "actual_centered_guard_rad": 0.2,
        "max_action_delta": MAX_ACTION_DELTA,
        "selected_global_scale": selected_scale,
        "feature_normalization": normalization,
        "coefficient_banks": banks,
        "fit_method": {"name": "deterministic_ridge", "lambda": 0.001, "dtype": "float64"},
        "source_authority_sha256": sha256(AUTHORITY),
    }
    return payload, fit_details


def run_design(controller: Path, scale: float, fit: dict[str, Any]) -> dict[str, Any]:
    cells = []
    for policy in POLICIES:
        for condition, offset in ENDPOINTS:
            result = run_closed_loop_sim(
                ClosedLoopConfig(
                    policy_path=policy, fit=fit, playground_root=PLAYGROUND,
                    command_x=0.077, duration_s=12.0, bridge_mode="fitted",
                    expected_observation_dim=115, expected_action_dim=14,
                    task="flat_terrain_backlash", seed=167931544,
                    eval_role="candidate", reset_mode="home-support",
                    reference_feature_table_path=REFERENCE, reference_start_phase=0,
                    policy_state_input_names=("previous_action",),
                    policy_state_output_names=("previous_action_out",),
                    policy_applied_target_observation=True,
                    eval_dynamics_override={"torso_com_offset_m": [offset, 0.0, 0.0]},
                    oracle_phase_com_controller_json=controller,
                )
            )
            mode = (result.get("modes") or {}).get("fitted") or {}
            gate = result.get("candidate_gate") or {}
            metrics = gate.get("metrics") or {}
            emergence = emergence_evidence(result, 0.077, 12.0, 1.08)
            cells.append({
                "scale": scale, "policy": policy.stem, "condition": condition,
                "status": result.get("status"),
                "termination_reason": mode.get("termination_reason"),
                "samples": mode.get("samples"),
                "tracking_p95_rad": metrics.get("max_pitch_tracking_p95_rad"),
                "rate_excess_rad_s": metrics.get("max_sent_target_velocity_limit_excess_rad_s"),
                "rate_max_excess_rad_s": metrics.get("max_sent_target_velocity_max_limit_excess_rad_s"),
                "saturation_pct": metrics.get("max_action_saturation_pct"),
                "mean_vx_m_s": ((mode.get("forward_motion") or {}).get("mean_velocity_x_m_s")),
                "bilateral_transitions": bool(
                    (emergence.get("left_contact_transition_count") or 0) > 0
                    and (emergence.get("right_contact_transition_count") or 0) > 0
                ),
                "command_consistent_forward": bool(
                    isinstance((mode.get("forward_motion") or {}).get("mean_velocity_x_m_s"), (int, float))
                    and float((mode.get("forward_motion") or {})["mean_velocity_x_m_s"]) > 0.0
                ),
                "dynamics_readback": ((result.get("insertion_point") or {}).get("dynamics_override")),
            })
            print(f"scale={scale:.2f} {policy.stem} {condition}: {mode.get('termination_reason')} {mode.get('samples')} ticks", flush=True)
    numeric_tracking = [float(row["tracking_p95_rad"]) for row in cells if isinstance(row["tracking_p95_rad"], (int, float))]
    rank = (
        sum(row["termination_reason"] == "duration_complete" for row in cells),
        sum(isinstance(row["tracking_p95_rad"], (int, float)) and float(row["tracking_p95_rad"]) <= 0.2 for row in cells),
        sum(row["rate_excess_rad_s"] == 0.0 and row["rate_max_excess_rad_s"] == 0.0 for row in cells),
        sum(row["bilateral_transitions"] for row in cells),
        sum(row["command_consistent_forward"] for row in cells),
        1,
        -max(numeric_tracking, default=float("inf")),
        -scale,
    )
    return {"scale": scale, "cells": cells, "rank": list(rank)}


def main() -> int:
    authority = json.loads(AUTHORITY.read_text())
    if authority.get("status") != "PASS_ORACLE_PHASE_COM_CORRECTIVE_AUTHORITY":
        raise ValueError("passing corrective-authority result required")
    fit = json.loads(FIT.read_text())
    scale_results = []
    provisional_paths = []
    fit_details = None
    for scale in SCALES:
        payload, details = fitted_payload(authority, scale)
        fit_details = details
        path = ROOT / f"outputs/analysis/oracle_phase_com_controller_scale_{scale:.2f}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        provisional_paths.append(path)
        scale_results.append(run_design(path, scale, fit))
    selected = max(scale_results, key=lambda row: tuple(row["rank"]))
    selected_path = provisional_paths[SCALES.index(float(selected["scale"]))]
    CONTROLLER.write_bytes(selected_path.read_bytes())
    for path in provisional_paths:
        path.unlink()
    controller = json.loads(CONTROLLER.read_text())
    checks = {
        "authority_passed": authority["status"] == "PASS_ORACLE_PHASE_COM_CORRECTIVE_AUTHORITY",
        "four_scales_exact": [row["scale"] for row in scale_results] == list(SCALES),
        "six_corrected_joints_exact": controller["corrected_joint_indices"] == list(CORRECTED_JOINT_INDICES),
        "residual_limit_exact": controller["residual_normalized_limit"] == 0.08,
        "selected_scale_from_frozen_set": controller["selected_global_scale"] in SCALES,
        "all_design_readbacks_body2_x": all(
            cell["dynamics_readback"].get("key") == "torso_com_offset_m"
            and cell["dynamics_readback"].get("readback", {}).get("body_id") == 2
            for row in scale_results for cell in row["cells"]
        ),
    }
    failed = sorted(key for key, value in checks.items() if not value)
    payload = {
        "schema_version": "oracle_phase_com_controller_fit.v1",
        "status": "PASS_ORACLE_PHASE_COM_CONTROLLER_FROZEN" if not failed else "FAIL_ORACLE_PHASE_COM_CONTROLLER_FIT",
        "checks": checks, "failed_checks": failed,
        "fit_details": fit_details, "scale_results": scale_results,
        "selected_scale": selected["scale"], "selected_rank": selected["rank"],
        "controller_path": str(CONTROLLER), "controller_sha256": sha256(CONTROLLER),
        "source_hashes": {"authority": sha256(AUTHORITY), "tool": sha256(Path(__file__))},
        "execution": {"cpu_only": True, "training": False, "formal_matrix_cells": 0, "robot_or_rdk": False},
    }
    FIT_RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "selected_scale": selected["scale"], "selected_rank": selected["rank"], "controller_sha256": payload["controller_sha256"]}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
