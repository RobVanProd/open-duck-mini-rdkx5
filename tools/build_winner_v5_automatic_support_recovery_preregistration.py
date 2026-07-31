#!/usr/bin/env python3
"""Freeze the prospective winner-v5 automatic support-recovery validation."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v5_automatic_support_recovery_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V5_AUTOMATIC_SUPPORT_RECOVERY_PREREGISTRATION_20260720.md"
BASIS_PATH = "outputs/analysis/winner_v3_supported_configuration_basis.json"
V3_PREREG_PATH = "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
V4_RESULT_PATH = "outputs/analysis/winner_v4_response_identifiability_result.json"
RESET_AUDIT_PATH = "outputs/analysis/winner_v4_response_support_reset_causal_audit.json"
JOB_PATH = "tools/run_winner_v5_automatic_support_recovery_cpu.py"
BROAD_SEED = 0xA51C0DED
NEGATIVE_EDGE_SEED = 0xE6D9A20F


def source_bytes(relative_path: str) -> bytes:
    path = ROOT / relative_path
    if path.is_file():
        return path.read_bytes()
    completed = subprocess.run(
        ["git", "show", f"HEAD:{relative_path}"], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if completed.returncode:
        raise FileNotFoundError(
            f"cannot read {relative_path}: {completed.stderr.decode(errors='replace')}"
        )
    return completed.stdout


def source_json(relative_path: str) -> dict[str, Any]:
    return json.loads(source_bytes(relative_path))


def source_record(relative_path: str) -> dict[str, str]:
    return {
        "path": relative_path,
        "sha256": hashlib.sha256(source_bytes(relative_path)).hexdigest(),
    }


def valid_inertia(tensor: np.ndarray) -> bool:
    values = np.linalg.eigvalsh(tensor)
    return bool(np.all(values > 0.0) and values[2] < values[0] + values[1])


def make_sample_set(
    *, name: str, seed: int, count: int, basis: dict[str, Any],
    x_bounds: tuple[float, float] | None = None,
) -> list[dict[str, Any]]:
    domain = basis["frozen_continuous_domain"]
    inertia = domain["torso_inertia"]
    nominal = np.asarray(basis["compiled_torso"]["principal_inertia_kg_m2"], dtype=float)
    diagonal_bounds = np.asarray(
        [
            inertia["principal_component_bounds_kg_m2"][axis]
            for axis in ("ixx", "iyy", "izz")
        ],
        dtype=float,
    )
    product = float(inertia["product_additive_allowance_abs_kg_m2"])
    bounds = np.asarray(
        [
            domain["all_link_mass_scale"],
            domain["torso_mass_add_kg"],
            domain["torso_com_offset_m"]["x"] if x_bounds is None else x_bounds,
            domain["torso_com_offset_m"]["y"],
            domain["torso_com_offset_m"]["z"],
            diagonal_bounds[0], diagonal_bounds[1], diagonal_bounds[2],
            [-product, product], [-product, product], [-product, product],
        ],
        dtype=float,
    )
    rng = np.random.Generator(np.random.PCG64(seed))
    unit = np.empty((count, len(bounds)), dtype=float)
    for column in range(unit.shape[1]):
        unit[:, column] = (rng.permutation(count) + 0.5) / count
    raw = bounds[:, 0] + unit * (bounds[:, 1] - bounds[:, 0])
    torso_mass = float(basis["compiled_torso"]["mass_kg"])
    rows: list[dict[str, Any]] = []
    for index, values in enumerate(raw):
        diagonal = values[5:8].copy()
        products = values[8:11].copy()
        contractions = 0
        while True:
            tensor = np.asarray(
                [
                    [diagonal[0], products[0], products[1]],
                    [products[0], diagonal[1], products[2]],
                    [products[1], products[2], diagonal[2]],
                ]
            )
            if valid_inertia(tensor):
                break
            diagonal = nominal + 0.5 * (diagonal - nominal)
            products *= 0.5
            contractions += 1
            if contractions > 16:
                raise RuntimeError("could not produce a valid coupled inertia sample")
        rows.append(
            {
                "id": f"{name}_{index:03d}",
                "sampling_role": name,
                "sampling_seed": seed,
                "all_link_mass_scale": float(values[0]),
                "torso_mass_add_kg": float(values[1]),
                "resulting_torso_mass_kg": float(torso_mass * values[0] + values[1]),
                "torso_com_offset_m": values[2:5].tolist(),
                "torso_inertia_tensor_kg_m2": tensor.tolist(),
                "inertia_validity_contractions": contractions,
                "optional_configuration_semantics": "aggregate_optional_non_locomotion_configuration",
            }
        )
    return rows


def dynamic_signature(row: dict[str, Any]) -> str:
    selected = {
        key: row[key]
        for key in (
            "all_link_mass_scale", "torso_mass_add_kg", "torso_com_offset_m",
            "torso_inertia_tensor_kg_m2",
        )
    }
    encoded = json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    basis = source_json(BASIS_PATH)
    v3_prereg = source_json(V3_PREREG_PATH)
    v4_result = source_json(V4_RESULT_PATH)
    reset_audit = source_json(RESET_AUDIT_PATH)
    if basis["decision"] != "PASS_VARIABLE_CONFIGURATION_DOMAIN_BASIS_CURRENT_CANDIDATE_HELD":
        raise ValueError("winner-v3 configuration basis is not passed")
    if v4_result["status"] != "HOLD_RESPONSE73_PRETRAINING_FALSIFICATION_FAILED":
        raise ValueError("winner-v4 response result is not the completed failure")
    if reset_audit["status"] != "PASS_RESPONSE_SUPPORT_RESET_CAUSAL_AUDIT":
        raise ValueError("support-reset causal audit is not passed")

    broad = make_sample_set(
        name="PROSPECTIVE_BROAD", seed=BROAD_SEED, count=64, basis=basis
    )
    negative_edge = make_sample_set(
        name="PROSPECTIVE_NEGATIVE_X_EDGE", seed=NEGATIVE_EDGE_SEED,
        count=32, basis=basis, x_bounds=(-0.05, -0.025),
    )
    validation = broad + negative_edge
    historical = (
        v3_prereg["evaluation_matrix"]["fixed_anchors"]
        + v3_prereg["evaluation_matrix"]["discovery_samples"]
        + v3_prereg["evaluation_matrix"]["heldout_samples"]
    )
    historical_signatures = {dynamic_signature(row) for row in historical}
    validation_signatures = [dynamic_signature(row) for row in validation]
    if len(set(validation_signatures)) != len(validation_signatures):
        raise ValueError("prospective validation population contains duplicates")
    if historical_signatures.intersection(validation_signatures):
        raise ValueError("prospective validation overlaps the exploratory population")

    actuator = {
        "fit_order": ["fit_p30", "fit_p31_34"],
        "per_joint": v3_prereg["actuator_domain"]["per_joint"],
    }
    gyro_step = math.pi / (180.0 * 16.0)
    result = {
        "schema_version": "winner_v5.automatic_support_recovery_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V5_AUTOMATIC_SUPPORT_RECOVERY_NOT_RUN",
        "decision": "AUTHORIZE_ONE_ZERO_PPO_CPU_SUPPORT_RECOVERY_VALIDATION",
        "causal_question": (
            "Can a fixed, deployable, automatic 20 ms feet-loaded IMU decision catch the "
            "unsupported negative-X configurations without destabilizing unseen assemblies, "
            "under both measured actuator fits and bounded gyro quantization/bias?"
        ),
        "authority": {
            "cpu_only": True,
            "training_or_ppo": False,
            "policy_architecture_implementation": False,
            "runtime_implementation": False,
            "robot_rdk_torque_or_motion": False,
            "robot_clearance": False,
            "next_step_if_pass": "response-profile redesign contract only",
        },
        "completed_result_treatment": {
            "winner_v4_response73_result_sha256": source_record(V4_RESULT_PATH)["sha256"],
            "retry_or_reclassification": False,
            "response73_status": "closed",
            "reason": (
                "The reset bug invalidated the simulator realization but fixing it does not "
                "make the -0.05 m endpoint supported. This is a new prospective procedure."
            ),
        },
        "exploratory_design_evidence": {
            "selection_population": "the pre-existing 24 fixed, 16 discovery, and 16 held-out winner-v3 configurations",
            "validation_weight": 0,
            "warning": "All controller constants were selected after inspecting this population; it cannot validate them.",
            "observed_passive_falls": 4,
            "selected_rule_outcome_cells": 112,
            "selected_rule_outcome_failures": 0,
            "blind_always-recover_outcome_failures": 92,
        },
        "experiment": {
            "backend": "MuJoCo 3.9.0 CPU double precision",
            "control_period_s": 0.02,
            "physics_substeps_per_tick": 10,
            "nominal_settle_ticks": 250,
            "tick_count": 250,
            "configuration_count": len(validation),
            "actuator_fit_count": 2,
            "sensor_case_count": 5,
            "cell_count": len(validation) * 2 * 5,
            "reset": (
                "correct-order mj_setConst on default MjData, followed by one shared "
                "nominal two-foot settled qpos loaded into every prospective configuration"
            ),
        },
        "controller": {
            "decision_tick": 1,
            "decision_semantics": "read after exactly one passive 20 ms loaded-contact tick",
            "gyro_quantization_step_rad_s": gyro_step,
            "pitch_trigger_rad_s": -0.042,
            "lateral_trigger_rad_s": -0.020,
            "sagittal_target_delta_rad": {
                "2": 0.25, "3": 0.125, "4": 0.25,
                "11": 0.25, "12": 0.125, "13": 0.25,
            },
            "lateral_target_delta_rad": {"1": -0.25, "10": 0.25},
            "untriggered_target": "exact frozen home",
            "triggered_target": "hold fixed recovery target for the remaining population",
            "transition": "exact selected measured home-relative gain/delay/tau/velocity plant",
            "manual_measurement_or_configuration_identity": False,
        },
        "sensor_cases": [
            {"id": "NOMINAL_QUANTIZED", "gyro_bias_rad_s_xy": [0.0, 0.0]},
            {"id": "BIAS_X_NEG_Y_NEG", "gyro_bias_rad_s_xy": [-0.002, -0.002]},
            {"id": "BIAS_X_NEG_Y_POS", "gyro_bias_rad_s_xy": [-0.002, 0.002]},
            {"id": "BIAS_X_POS_Y_NEG", "gyro_bias_rad_s_xy": [0.002, -0.002]},
            {"id": "BIAS_X_POS_Y_POS", "gyro_bias_rad_s_xy": [0.002, 0.002]},
        ],
        "actuator_plants": actuator,
        "validation_population": validation,
        "validation_population_contract": {
            "broad": {"seed": BROAD_SEED, "count": 64, "x_bounds_m": [-0.05, 0.05]},
            "negative_x_edge": {"seed": NEGATIVE_EDGE_SEED, "count": 32, "x_bounds_m": [-0.05, -0.025]},
            "sampler": "independent per-dimension Latin-hypercube PCG64 with positive-definite triangle-valid inertia contraction",
            "overlap_with_exploratory_population": 0,
            "outcomes_seen_before_freeze": False,
        },
        "pass_requirements": {
            "minimum_base_z_m": 0.10,
            "maximum_abs_tilt_rad": 0.35,
            "two_foot_contact_failure_ticks": 0,
            "final_window_ticks": 50,
            "maximum_final_gyro_rad_s": 0.05,
            "all_cells_must_pass": True,
        },
        "stop_rules": [
            "any source/hash/shape/order mismatch",
            "any validation cell violates a pass requirement",
            "any interrupted or nonfinite run",
            "no threshold, target, sensor case, population, or bound changes after outcome",
            "no retry",
        ],
        "sources": {
            "domain_basis": source_record(BASIS_PATH),
            "winner_v3_preregistration": source_record(V3_PREREG_PATH),
            "winner_v4_result": source_record(V4_RESULT_PATH),
            "reset_causal_audit": source_record(RESET_AUDIT_PATH),
            "job": source_record(JOB_PATH),
            "playground": {
                "repository": "https://github.com/apirrone/Open_Duck_Playground.git",
                "commit": "b9be205ac64488c23504ca42e5ec790337adeec3",
                "scene": "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml",
                "scene_sha256": "65324e27a3a84e2e42d1073bfc636f9cdbf6bef7b1f20c1b5a886b8fd58fcc71",
            },
        },
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract_sha = hashlib.sha256(OUTPUT_JSON.read_bytes()).hexdigest()
    OUTPUT_MD.write_text(
        "# Winner-v5 Automatic Support-Recovery Preregistration\n\n"
        f"status: `{result['status']}`\n\n"
        f"contract SHA-256: `{contract_sha}`\n\n"
        "This is a new zero-PPO CPU validation, not a retry of response73. It "
        "freezes a 20 ms feet-loaded IMU decision and recovery target against 96 "
        "previously unseen configurations, both measured actuator fits, native gyro "
        "quantization, and five bounded bias cases. Manual mass, center-of-mass, or "
        "component measurements are forbidden. Every one of 960 cells must pass.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "sha256": contract_sha, "cells": result["experiment"]["cell_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
