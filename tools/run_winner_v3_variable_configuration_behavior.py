#!/usr/bin/env python3
"""Contract or execute the frozen winner-v3 1,024-cell CPU behavior matrix."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from actuator_bridge_model import (  # noqa: E402
    ActuatorBridgeModel,
    JOINT_NAMES,
    JointActuatorParams,
)
from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim  # noqa: E402
from evaluate_ground_up_policy import emergence_evidence  # noqa: E402


PREREG = ROOT / "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
TRANSFORM_CONTRACT = ROOT / "outputs/analysis/winner_v3_variable_configuration_eval_policy_transform_contract.json"
CURRICULUM_CONTRACT = ROOT / "outputs/analysis/winner_v3_variable_configuration_curriculum_contract.json"
TRAINING_CHECK = ROOT / "outputs/analysis/winner_v3_recurrent_adapter_training_artifact_check.json"
POLICY_ROOT = ROOT / "outputs/analysis/winner_v3_variable_configuration_eval_policies"
PLAYGROUND = Path("/tmp/winner_v3_variable_config_formal_9ed4109")
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
RUNNER_CONTRACT = ROOT / "outputs/analysis/winner_v3_variable_configuration_behavior_runner_contract.json"
RUNNER_CONTRACT_MD = ROOT / "outputs/analysis/WINNER_V3_VARIABLE_CONFIGURATION_BEHAVIOR_RUNNER_CONTRACT_20260719.md"
CELLS = ROOT / "outputs/analysis/winner_v3_variable_configuration_cells"
TRACES = ROOT / "outputs/analysis/winner_v3_variable_configuration_traces"
CONDITIONS = ROOT / "outputs/analysis/winner_v3_variable_configuration_conditions"
RESULT_JSON = ROOT / "outputs/analysis/winner_v3_variable_configuration_result.json"
RESULT_MD = ROOT / "outputs/analysis/WINNER_V3_VARIABLE_CONFIGURATION_RESULT_20260719.md"
STEPS = (1_003_520, 2_007_040)
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
COMMANDS = (0.0, 0.074, 0.077, 0.080)
CURRENT_NM_PER_A = 0.784532
TRACKING_MAX_RAD = 0.20
CURRENT_MAX_A = 0.65
NUMERICAL_TOLERANCE = 1.0e-5
EXPECTED_TRANSFORMED_HASHES = {
    1_003_520: "c8e03dd4afed4e7a96507e5089116944a048ac1d682210408a68cca1b8b6af7c",
    2_007_040: "dfdd01bf4563e3d377ffcbe70515681e75a0d87797f3b6b9e4486d1b40ad569c",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def policy_path(step: int) -> Path:
    return POLICY_ROOT / f"R64_ZERO_INIT_RECURRENT_ADAPTER_{step}.onnx"


def actuator_fit(prereg: Mapping[str, Any], plant: str) -> dict[str, Any]:
    if plant not in PLANTS:
        raise ValueError(f"unknown actuator plant {plant}")
    fit_key = "fit_p30" if plant == "P30_ALL_JOINT" else "fit_p31_34"
    joints = {}
    for name in JOINT_NAMES:
        row = prereg["actuator_domain"]["per_joint"][name][fit_key]
        joints[name] = {
            "series": {"amplitude_ratio": float(row["gain_ratio"])},
            "combined": {
                "delay_ticks": int(row["delay_ticks"]),
                "tau_s": float(row["tau_s"]),
                "velocity_limit_rad_s": float(row["velocity_limit_rad_s"]),
            },
        }
    return {
        "schema_version": "winner_v3.frozen_actuator_plant.v1",
        "plant": plant,
        "primary": {"joints": joints},
    }


def zero_transport() -> dict[str, Any]:
    return {
        "sensor_noise_scales": None,
        "native_quantization": False,
        "additional_action_delay_ticks": 0,
        "imu_delay_ticks": 0,
    }


def condition_plan(prereg: Mapping[str, Any]) -> list[dict[str, Any]]:
    matrix = prereg["evaluation_matrix"]
    conditions: list[dict[str, Any]] = []
    for seed in matrix["nominal_seeds"]:
        conditions.append(
            {
                "group": "NOMINAL",
                "id": f"NOMINAL_SEED_{int(seed)}",
                "seed": int(seed),
                "configuration": None,
                "transport": zero_transport(),
            }
        )
    for group, key in (
        ("FIXED_ANCHOR", "fixed_anchors"),
        ("DISCOVERY", "discovery_samples"),
        ("HELDOUT", "heldout_samples"),
    ):
        for row in matrix[key]:
            conditions.append(
                {
                    "group": group,
                    "id": row["id"],
                    "seed": int(matrix["other_seed"]),
                    "configuration": row,
                    "transport": zero_transport(),
                }
            )
    for row in matrix["sensor_transport_conditions"]:
        transport = zero_transport()
        if row.get("native_quantization"):
            transport["native_quantization"] = True
        if "sensor_noise_scales" in row:
            transport["sensor_noise_scales"] = dict(row["sensor_noise_scales"])
        if "additional_action_delay_ticks" in row:
            transport["additional_action_delay_ticks"] = int(
                row["additional_action_delay_ticks"]
            )
        if "imu_delay_ticks" in row:
            transport["imu_delay_ticks"] = int(row["imu_delay_ticks"])
        conditions.append(
            {
                "group": "SENSOR_TRANSPORT",
                "id": row["id"],
                "seed": int(matrix["other_seed"]),
                "configuration": None,
                "transport": transport,
            }
        )
    return conditions


def matrix_plan(prereg: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for condition in condition_plan(prereg):
        for step in STEPS:
            for plant in PLANTS:
                for command in COMMANDS:
                    rows.append(
                        {
                            "condition_group": condition["group"],
                            "condition_id": condition["id"],
                            "seed": condition["seed"],
                            "configuration": condition["configuration"],
                            "transport": condition["transport"],
                            "step": step,
                            "plant": plant,
                            "command_x_m_s": command,
                            "duration_ticks": 600,
                        }
                    )
    return rows


def cell_stem(row: Mapping[str, Any]) -> str:
    return (
        f"{row['condition_group'].lower()}_{row['condition_id'].lower()}_"
        f"step{row['step']}_{row['plant'].lower()}_"
        f"x{float(row['command_x_m_s']):.3f}_seed{row['seed']}"
    )


def finite_tree(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(item) for item in value)
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    return True


def expected_sensor_scales(transport: Mapping[str, Any]) -> dict[str, float]:
    names = (
        "hip_pos_rad",
        "knee_pos_rad",
        "ankle_pos_rad",
        "joint_vel_rad_s",
        "gravity",
        "linvel_m_s",
        "gyro_rad_s",
        "accelerometer",
    )
    source = transport.get("sensor_noise_scales")
    return {
        name: 0.0 if source is None else float(source[name]) for name in names
    }


def readback_checks(
    row: Mapping[str, Any],
    result: Mapping[str, Any],
    prereg: Mapping[str, Any],
) -> dict[str, bool]:
    env = result.get("env") or {}
    configuration = env.get("winner_v3_configuration_readback") or {}
    transport = env.get("winner_v3_actuator_sensor_transport_readback") or {}
    expected_configuration = row["configuration"]
    requested = configuration.get("requested") or {}
    actual = configuration.get("actual") or {}
    nominal = configuration.get("nominal") or {}
    scale = (
        1.0
        if expected_configuration is None
        else float(expected_configuration["all_link_mass_scale"])
    )
    add = (
        0.0
        if expected_configuration is None
        else float(expected_configuration["torso_mass_add_kg"])
    )
    offset = np.asarray(
        [0.0, 0.0, 0.0]
        if expected_configuration is None
        else expected_configuration["torso_com_offset_m"],
        dtype=float,
    )
    requested_tensor = np.asarray(
        requested.get("torso_inertia_tensor_kg_m2", []), dtype=float
    )
    planned_tensor = (
        np.diag(np.asarray(nominal.get("torso_principal_inertia_kg_m2", [])))
        if expected_configuration is None
        else np.asarray(expected_configuration["torso_inertia_tensor_kg_m2"], dtype=float)
    )
    nominal_masses = np.asarray(nominal.get("all_body_mass_kg", []), dtype=float)
    actual_masses = np.asarray(actual.get("all_body_mass_kg", []), dtype=float)
    expected_masses = nominal_masses * scale
    if expected_masses.size > 2:
        expected_masses[2] += add
    expected_actuator = prereg["actuator_domain"]["per_joint"]
    fit_key = "fit_p30" if row["plant"] == PLANTS[0] else "fit_p31_34"
    parameters = ((transport.get("actuator_fit") or {}).get("parameters") or [])
    actuator_exact = len(parameters) == 14
    if actuator_exact:
        for index, name in enumerate(JOINT_NAMES):
            expected = expected_actuator[name][fit_key]
            observed = parameters[index]
            actuator_exact &= bool(
                int(observed["delay_ticks"]) == int(expected["delay_ticks"])
                and abs(float(observed["time_constant_s"]) - float(expected["tau_s"]))
                <= 1.0e-12
                and abs(float(observed["gain_ratio"]) - float(expected["gain_ratio"]))
                <= 1.0e-12
                and abs(
                    float(observed["velocity_limit_rad_s"])
                    - float(expected["velocity_limit_rad_s"])
                )
                <= 1.0e-12
            )
    planned_transport = row["transport"]
    return {
        "body_identity_exact": configuration.get("body_name") == "trunk_assembly"
        and int(configuration.get("body_id", -1)) == 2,
        "configuration_enabled_exact": bool(configuration.get("enabled"))
        == (expected_configuration is not None),
        "requested_scale_add_offset_exact": abs(
            float(requested.get("all_link_mass_scale", math.nan)) - scale
        )
        <= 1.0e-12
        and abs(float(requested.get("torso_mass_add_kg", math.nan)) - add)
        <= 1.0e-12
        and np.allclose(
            np.asarray(requested.get("torso_com_offset_m", []), dtype=float),
            offset,
            rtol=0.0,
            atol=1.0e-12,
        ),
        "requested_inertia_tensor_exact": requested_tensor.shape == (3, 3)
        and planned_tensor.shape == (3, 3)
        and np.allclose(requested_tensor, planned_tensor, rtol=0.0, atol=1.0e-12),
        "all_body_mass_readback_exact": nominal_masses.shape == actual_masses.shape
        and nominal_masses.size > 2
        and np.allclose(actual_masses, expected_masses, rtol=0.0, atol=2.0e-7),
        "torso_com_readback_exact": np.allclose(
            np.asarray(actual.get("torso_body_ipos_m", []), dtype=float),
            np.asarray(nominal.get("torso_body_ipos_m", []), dtype=float) + offset,
            rtol=0.0,
            atol=2.0e-7,
        ),
        "full_inertia_readback_exact": np.allclose(
            np.asarray(
                actual.get("torso_inertia_tensor_nominal_frame_kg_m2", []),
                dtype=float,
            ),
            planned_tensor,
            rtol=0.0,
            atol=2.0e-8,
        ),
        "actuator_readback_exact": actuator_exact,
        "transport_readback_exact": int(
            transport.get("additional_action_delay_ticks", -1)
        )
        == int(planned_transport["additional_action_delay_ticks"])
        and int(transport.get("imu_delay_ticks", -1))
        == int(planned_transport["imu_delay_ticks"])
        and bool(transport.get("native_quantization"))
        == bool(planned_transport["native_quantization"])
        and transport.get("sensor_noise_scales")
        == expected_sensor_scales(planned_transport),
    }


def trace_audit(path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    required = {
        "obs_state",
        "obs_state_pre_transport",
        "obs_state_post_imu_delay",
        "policy_state_input",
        "policy_state_output",
        "action",
        "sent_target_rad",
        "applied_target_rad",
        "actual_position_rad",
        "actuator_force_nm",
        "tracking_error_rad",
        "foot_contacts",
        "conservative_rate_excess_rad_s",
        "actual_centered_guard_excess_rad",
    }
    first = rows[0] if rows else {}
    first_state = first.get("policy_state_input") or {}
    h0 = np.asarray(first_state.get("h_in", []), dtype=float)
    a0 = np.asarray(first_state.get("previous_action", []), dtype=float)
    try:
        reported_path = str(path.relative_to(ROOT))
    except ValueError:
        reported_path = str(path)
    return {
        "path": reported_path,
        "sha256": sha256(path),
        "rows": len(rows),
        "ticks_contiguous": all(int(row.get("tick", -1)) == index for index, row in enumerate(rows)),
        "required_fields_every_tick": all(required <= set(row) for row in rows),
        "all_values_finite": all(finite_tree(row) for row in rows),
        "reset_h_exact_zero": h0.shape == (1, 64) and np.array_equal(h0, np.zeros_like(h0)),
        "reset_previous_action_exact_zero": a0.shape == (1, 14)
        and np.array_equal(a0, np.zeros_like(a0)),
    }


def cell_metrics(result: Mapping[str, Any]) -> dict[str, Any]:
    mode = ((result.get("modes") or {}).get("fitted") or {})
    joints = mode.get("joints") or {}
    tracking = {
        name: float(joints[name]["joint_target_tracking_error_rad"]["p95"])
        for name in JOINT_NAMES
        if name in joints
    }
    current = {
        name: float(joints[name]["current_a"]["p95"])
        for name in JOINT_NAMES
        if name in joints
    }
    saturation = {
        name: float(joints[name]["action_saturation_pct"])
        for name in JOINT_NAMES
        if name in joints
    }
    clearance = mode.get("foot_clearance") or {}
    feet = clearance.get("feet") or {}
    forward = mode.get("forward_motion") or {}
    gate = result.get("candidate_gate") or {}
    gate_metrics = gate.get("metrics") or {}
    return {
        "samples": int(mode.get("samples", 0)),
        "termination_reason": mode.get("termination_reason"),
        "candidate_gate_status": gate.get("status"),
        "mean_local_vx_m_s": forward.get("mean_velocity_x_m_s"),
        "left_contact_transition_count": int(
            (feet.get("left") or {}).get("contact_transition_count", 0)
        ),
        "right_contact_transition_count": int(
            (feet.get("right") or {}).get("contact_transition_count", 0)
        ),
        "tracking_p95_rad_by_joint": tracking,
        "worst_tracking_p95_rad": max(tracking.values(), default=math.inf),
        "current_p95_a_by_joint": current,
        "worst_current_p95_a": max(current.values(), default=math.inf),
        "saturation_pct_by_joint": saturation,
        "worst_saturation_pct": max(saturation.values(), default=math.inf),
        "max_conservative_rate_excess_rad_s": float(
            mode.get("max_conservative_rate_excess_rad_s", math.inf)
        ),
        "max_actual_centered_guard_excess_rad": float(
            mode.get("max_actual_centered_guard_excess_rad", math.inf)
        ),
        "body_pitch_p95_abs_rad": gate_metrics.get("max_abs_body_pitch_p95_rad"),
        "minimum_base_height_m": gate_metrics.get("min_base_height_m"),
        "body_pitch_rate_p95_abs_rad_s": (
            (mode.get("body_pitch_rate_abs_rad_s") or {}).get("p95")
        ),
        "body_roll_rate_p95_abs_rad_s": (
            (mode.get("body_roll_rate_abs_rad_s") or {}).get("p95")
        ),
        "accelerometer_norm_p95_m_s2": (
            (mode.get("accelerometer_norm_m_s2") or {}).get("p95")
        ),
    }


def classify_cell(
    row: Mapping[str, Any],
    result: Mapping[str, Any],
    trace: Mapping[str, Any],
    readback: Mapping[str, bool],
) -> tuple[bool, list[str], dict[str, Any]]:
    metrics = cell_metrics(result)
    command = float(row["command_x_m_s"])
    failures = []
    checks = {
        "duration_complete_600": metrics["samples"] == 600
        and metrics["termination_reason"] == "duration_complete",
        "candidate_gate_pass": metrics["candidate_gate_status"]
        == "PASS_CANDIDATE_SIM_GATE",
        "bilateral_transitions": command == 0.0
        or (
            metrics["left_contact_transition_count"] > 0
            and metrics["right_contact_transition_count"] > 0
        ),
        "positive_command_consistent_motion": command == 0.0
        or (
            metrics["mean_local_vx_m_s"] is not None
            and float(metrics["mean_local_vx_m_s"]) > 0.0
        ),
        "tracking_p95_at_most_0p20": metrics["worst_tracking_p95_rad"]
        <= TRACKING_MAX_RAD,
        "current_p95_at_most_0p65": metrics["worst_current_p95_a"] <= CURRENT_MAX_A,
        "zero_saturation": metrics["worst_saturation_pct"] == 0.0,
        "zero_rate_excess": metrics["max_conservative_rate_excess_rad_s"] == 0.0,
        "zero_envelope_excess": metrics["max_actual_centered_guard_excess_rad"]
        == 0.0,
        "zero_command_velocity": command != 0.0
        or (
            metrics["mean_local_vx_m_s"] is not None
            and abs(float(metrics["mean_local_vx_m_s"])) <= 0.02
        ),
        "zero_command_pitch": command != 0.0
        or (
            metrics["body_pitch_p95_abs_rad"] is not None
            and float(metrics["body_pitch_p95_abs_rad"]) <= 0.25
        ),
        "zero_command_base_height": command != 0.0
        or (
            metrics["minimum_base_height_m"] is not None
            and float(metrics["minimum_base_height_m"]) >= 0.12
        ),
        "trace_contract": trace["rows"] == 600
        and trace["ticks_contiguous"]
        and trace["required_fields_every_tick"]
        and trace["all_values_finite"]
        and trace["reset_h_exact_zero"]
        and trace["reset_previous_action_exact_zero"],
        "per_run_readback_exact": all(readback.values()),
        "cpu_only": ((result.get("env") or {}).get("jax_backend")) == "cpu"
        and all("CpuDevice" in value for value in (result.get("env") or {}).get("jax_devices", [])),
    }
    failures.extend(name for name, passed in checks.items() if not passed)
    metrics["checks"] = checks
    return not failures, failures, metrics


def default_off_actuator_test(prereg: Mapping[str, Any]) -> dict[str, Any]:
    fit = actuator_fit(prereg, PLANTS[0])
    rows = fit["primary"]["joints"]
    params = [
        JointActuatorParams(
            delay_ticks=int(rows[name]["combined"]["delay_ticks"]),
            tau_s=float(rows[name]["combined"]["tau_s"]),
            velocity_limit_rad_s=float(rows[name]["combined"]["velocity_limit_rad_s"]),
        )
        for name in JOINT_NAMES
    ]
    initial = np.linspace(-0.4, 0.4, 14)
    bridge = ActuatorBridgeModel(params, initial_target=initial)
    queues = [
        [float(initial[index])] * (param.delay_ticks + 1)
        for index, param in enumerate(params)
    ]
    expected = initial.copy()
    rng = np.random.default_rng(20260719)
    exact = True
    max_error = 0.0
    for _ in range(128):
        target = rng.uniform(-1.0, 1.0, 14)
        next_expected = expected.copy()
        for index, param in enumerate(params):
            queues[index].append(float(target[index]))
            while len(queues[index]) > param.delay_ticks + 1:
                queues[index].pop(0)
            delayed = queues[index][0]
            alpha = 1.0 - math.exp(-0.02 / param.tau_s) if param.tau_s > 0 else 1.0
            desired = expected[index] + alpha * (delayed - expected[index])
            delta = desired - expected[index]
            limit = param.velocity_limit_rad_s * 0.02
            delta = max(-limit, min(limit, delta))
            next_expected[index] = expected[index] + delta
        actual = bridge.step(target, 0.02)
        error = float(np.max(np.abs(actual - next_expected)))
        exact &= np.array_equal(actual, next_expected)
        max_error = max(max_error, error)
        expected = next_expected
    return {"bit_exact": exact, "max_abs_error": max_error, "steps": 128}


def nonformal_smoke(prereg: Mapping[str, Any]) -> dict[str, Any]:
    condition = prereg["evaluation_matrix"]["discovery_samples"][5]
    transport = {
        "sensor_noise_scales": prereg["evaluation_matrix"]["sensor_transport_conditions"][1]["sensor_noise_scales"],
        "native_quantization": True,
        "additional_action_delay_ticks": 2,
        "imu_delay_ticks": 2,
    }
    row = {
        "condition_group": "NONFORMAL_CONTRACT",
        "condition_id": "NONFORMAL_INTERIOR_2_TICKS",
        "seed": 2_026_071_901,
        "configuration": condition,
        "transport": transport,
        "step": STEPS[0],
        "plant": PLANTS[0],
        "command_x_m_s": 0.076,
        "duration_ticks": 2,
    }
    trace_path = Path("/tmp/winner_v3_nonformal_contract_trace.jsonl")
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy_path(STEPS[0]),
                fit=actuator_fit(prereg, PLANTS[0]),
                playground_root=PLAYGROUND,
                command_x=0.076,
                duration_s=0.04,
                bridge_mode="fitted",
                expected_observation_dim=115,
                task="flat_terrain_backlash",
                seed=row["seed"],
                eval_role="candidate",
                reset_mode="home-support",
                policy_state_input_names=("h_in", "previous_action"),
                policy_state_output_names=("h_out", "previous_action_out"),
                policy_applied_target_observation=True,
                reference_feature_table_path=REFERENCE,
                reference_start_phase=0,
                trace_jsonl=trace_path,
                trace_full_obs=True,
                winner_v3_configuration_override=condition,
                winner_v3_sensor_noise_scales=transport["sensor_noise_scales"],
                winner_v3_native_quantization=True,
                winner_v3_additional_action_delay_ticks=2,
                winner_v3_imu_delay_ticks=2,
                winner_v3_home_relative_actuator_gain=True,
            )
        )
    audit = trace_audit(trace_path)
    readback = readback_checks(row, result, prereg)
    mode = ((result.get("modes") or {}).get("fitted") or {})
    return {
        "formal": False,
        "command_x_m_s": 0.076,
        "seed": row["seed"],
        "ticks": 2,
        "status_recorded_not_gating": result.get("status"),
        "samples": mode.get("samples"),
        "termination_reason": mode.get("termination_reason"),
        "cpu_only": ((result.get("env") or {}).get("jax_backend")) == "cpu",
        "trace": audit,
        "readback_checks": readback,
        "pass": mode.get("samples") == 2
        and mode.get("termination_reason") == "duration_complete"
        and audit["rows"] == 2
        and audit["ticks_contiguous"]
        and audit["required_fields_every_tick"]
        and audit["all_values_finite"]
        and audit["reset_h_exact_zero"]
        and audit["reset_previous_action_exact_zero"]
        and all(readback.values())
        and ((result.get("env") or {}).get("jax_backend")) == "cpu",
    }


def plan_contract() -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text())
    transform = json.loads(TRANSFORM_CONTRACT.read_text())
    curriculum = json.loads(CURRICULUM_CONTRACT.read_text())
    training = json.loads(TRAINING_CHECK.read_text())
    plan = matrix_plan(prereg)
    conditions = condition_plan(prereg)
    runner = Path(__file__).resolve()
    actuator_default_off = default_off_actuator_test(prereg)
    smoke = nonformal_smoke(prereg)
    unique = {
        (
            row["condition_group"],
            row["condition_id"],
            row["seed"],
            row["step"],
            row["plant"],
            row["command_x_m_s"],
        )
        for row in plan
    }
    group_counts = {
        group: sum(1 for row in plan if row["condition_group"] == group)
        for group in {row["condition_group"] for row in plan}
    }
    checks = {
        "preregistration_exact": prereg["status"] == "PREREGISTERED_CPU_CONTRACT_FIRST",
        "transform_contract_passed_zero_outcome": transform["status"]
        == "PASS_WINNER_V3_VARIABLE_CONFIGURATION_EVAL_POLICY_TRANSFORM_CONTRACT"
        and int(transform["formal_behavior_cells_executed"]) == 0,
        "curriculum_contract_passed": curriculum["status"]
        == "PASS_WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_CONTRACT",
        "training_artifact_check_passed": training["status"]
        == "PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK",
        "two_policy_hashes_exact": all(
            policy_path(step).exists()
            and sha256(policy_path(step)) == EXPECTED_TRANSFORMED_HASHES[step]
            for step in STEPS
        ),
        "condition_count_exact_64": len(conditions) == 64,
        "matrix_count_exact_1024": len(plan) == 1024 and len(unique) == 1024,
        "matrix_group_counts_exact": group_counts
        == {
            "NOMINAL": 32,
            "FIXED_ANCHOR": 384,
            "DISCOVERY": 256,
            "HELDOUT": 256,
            "SENSOR_TRANSPORT": 96,
        },
        "matrix_axes_exact": {row["step"] for row in plan} == set(STEPS)
        and {row["plant"] for row in plan} == set(PLANTS)
        and {row["command_x_m_s"] for row in plan} == set(COMMANDS)
        and all(row["duration_ticks"] == 600 for row in plan),
        "playground_and_reference_exist": PLAYGROUND.exists() and REFERENCE.exists(),
        "actuator_default_off_bit_exact": actuator_default_off["bit_exact"],
        "nonformal_full_stack_smoke_passed": smoke["pass"],
        "formal_output_roots_absent": not any(
            path.exists() for path in (CELLS, TRACES, CONDITIONS, RESULT_JSON, RESULT_MD)
        ),
        "formal_behavior_cells_zero": True,
        "cpu_environment_exact": os.environ["CUDA_VISIBLE_DEVICES"] == ""
        and os.environ["JAX_PLATFORMS"] == "cpu",
    }
    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema_version": "winner_v3.variable_configuration_behavior_runner_contract.v1",
        "status": (
            "PASS_WINNER_V3_VARIABLE_CONFIGURATION_BEHAVIOR_RUNNER_CONTRACT"
            if not failed
            else "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_BEHAVIOR_RUNNER_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "formal_behavior_cells_executed": 0,
        "matrix_cells": len(plan),
        "condition_count": len(conditions),
        "group_counts": group_counts,
        "matrix_plan_sha256": canonical_sha256(plan),
        "runner_path": str(runner.relative_to(ROOT)),
        "runner_sha256": sha256(runner),
        "supporting_tool_hashes": {
            "closed_loop_sim_eval.py": sha256(TOOLS / "closed_loop_sim_eval.py"),
            "actuator_bridge_model.py": sha256(TOOLS / "actuator_bridge_model.py"),
            "evaluate_ground_up_policy.py": sha256(TOOLS / "evaluate_ground_up_policy.py"),
        },
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "transform_contract": sha256(TRANSFORM_CONTRACT),
            "curriculum_contract": sha256(CURRICULUM_CONTRACT),
            "training_artifact_check": sha256(TRAINING_CHECK),
            "reference_feature_table": sha256(REFERENCE),
            **{f"policy_{step}": sha256(policy_path(step)) for step in STEPS},
        },
        "actuator_default_off": actuator_default_off,
        "nonformal_full_stack_smoke": smoke,
        "environment": {
            "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"],
            "JAX_PLATFORMS": os.environ["JAX_PLATFORMS"],
            "robot_or_rdk_access": False,
        },
        "authority": {
            "one_frozen_1024_cell_cpu_execution": not failed,
            "retry": False,
            "training": False,
            "gpu_or_igpu": False,
            "hosted_or_colab": False,
            "rdkx5_or_robot": False,
            "runtime_or_gate5": False,
        },
    }
    RUNNER_CONTRACT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Winner-v3 Variable-Configuration Behavior Runner Contract",
        "",
        f"status: `{payload['status']}`",
        "",
        "Formal behavior cells executed: `0`.",
        "",
    ]
    lines.extend(
        f"- `{name}`: `{'PASS' if passed else 'FAIL'}`"
        for name, passed in checks.items()
    )
    lines.extend(
        [
            "",
            f"Frozen matrix SHA-256: `{payload['matrix_plan_sha256']}`.",
            "",
            "A pass authorizes one execution of the exact 1,024-cell CPU matrix. "
            "The two-tick x=0.076 smoke is non-formal and has no selection weight.",
            "",
            "No retry, training, accelerator, hosted allocation, RDK-X5, robot, "
            "runtime, Gate 5, motion, or deployment is authorized.",
            "",
        ]
    )
    RUNNER_CONTRACT_MD.write_text("\n".join(lines))
    return payload


def execute_cell(
    row: Mapping[str, Any], prereg: Mapping[str, Any]
) -> dict[str, Any]:
    stem = cell_stem(row)
    trace_path = TRACES / f"{stem}.jsonl"
    transport = row["transport"]
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy_path(int(row["step"])),
                fit=actuator_fit(prereg, str(row["plant"])),
                playground_root=PLAYGROUND,
                command_x=float(row["command_x_m_s"]),
                duration_s=12.0,
                bridge_mode="fitted",
                expected_observation_dim=115,
                task="flat_terrain_backlash",
                seed=int(row["seed"]),
                eval_role="candidate",
                reset_mode="home-support",
                policy_state_input_names=("h_in", "previous_action"),
                policy_state_output_names=("h_out", "previous_action_out"),
                policy_applied_target_observation=True,
                reference_feature_table_path=REFERENCE,
                reference_start_phase=0,
                trace_jsonl=trace_path,
                trace_full_obs=True,
                winner_v3_configuration_override=row["configuration"],
                winner_v3_sensor_noise_scales=transport["sensor_noise_scales"],
                winner_v3_native_quantization=bool(transport["native_quantization"]),
                winner_v3_additional_action_delay_ticks=int(
                    transport["additional_action_delay_ticks"]
                ),
                winner_v3_imu_delay_ticks=int(transport["imu_delay_ticks"]),
                winner_v3_home_relative_actuator_gain=True,
            )
        )
    audit = trace_audit(trace_path)
    readback = readback_checks(row, result, prereg)
    passed, failures, metrics = classify_cell(row, result, audit, readback)
    payload = {
        "schema_version": "winner_v3.variable_configuration_cell.v1",
        "status": "PASS_WINNER_V3_VARIABLE_CONFIGURATION_CELL"
        if passed
        else "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_CELL",
        "pass": passed,
        "failure_reasons": failures,
        "identity": dict(row),
        "policy": {
            "path": str(policy_path(int(row["step"])).relative_to(ROOT)),
            "sha256": sha256(policy_path(int(row["step"]))),
        },
        "actuator_plant_sha256": canonical_sha256(
            actuator_fit(prereg, str(row["plant"]))
        ),
        "metrics": metrics,
        "readback_checks": readback,
        "model_readback": (result.get("env") or {}).get(
            "winner_v3_configuration_readback"
        ),
        "actuator_sensor_transport_readback": (result.get("env") or {}).get(
            "winner_v3_actuator_sensor_transport_readback"
        ),
        "candidate_gate": result.get("candidate_gate"),
        "trace": audit,
        "training_or_simulator_reward_selection_weight": 0,
        "robot_clearance": False,
    }
    path = CELLS / f"{stem}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    payload["cell_path"] = str(path.relative_to(ROOT))
    payload["cell_sha256"] = sha256(path)
    return payload


def write_condition(condition: Mapping[str, Any], cells: list[Mapping[str, Any]]) -> dict[str, Any]:
    stem = f"{condition['group'].lower()}_{condition['id'].lower()}"
    summary = {
        "schema_version": "winner_v3.variable_configuration_condition.v1",
        "status": "PASS_WINNER_V3_VARIABLE_CONFIGURATION_CONDITION"
        if len(cells) == 16 and all(cell["pass"] for cell in cells)
        else "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_CONDITION",
        "pass": len(cells) == 16 and all(cell["pass"] for cell in cells),
        "condition": dict(condition),
        "cells": [
            {
                "step": cell["identity"]["step"],
                "plant": cell["identity"]["plant"],
                "command_x_m_s": cell["identity"]["command_x_m_s"],
                "pass": cell["pass"],
                "failure_reasons": cell["failure_reasons"],
                "worst_tracking_p95_rad": cell["metrics"]["worst_tracking_p95_rad"],
                "worst_current_p95_a": cell["metrics"]["worst_current_p95_a"],
                "mean_local_vx_m_s": cell["metrics"]["mean_local_vx_m_s"],
                "cell_path": cell["cell_path"],
                "cell_sha256": cell["cell_sha256"],
                "trace_path": cell["trace"]["path"],
                "trace_sha256": cell["trace"]["sha256"],
            }
            for cell in cells
        ],
    }
    json_path = CONDITIONS / f"{stem}.json"
    md_path = CONDITIONS / f"{stem}.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    lines = [
        f"# Winner-v3 Condition — {condition['id']}",
        "",
        f"status: `{summary['status']}`",
        "",
        "| checkpoint | plant | command x | pass | tracking p95 | current p95 | mean vx | failures |",
        "|---:|---|---:|---|---:|---:|---:|---|",
    ]
    for cell in summary["cells"]:
        lines.append(
            f"| {cell['step']} | `{cell['plant']}` | {cell['command_x_m_s']:.3f} | "
            f"`{cell['pass']}` | {cell['worst_tracking_p95_rad']:.9f} | "
            f"{cell['worst_current_p95_a']:.9f} | {cell['mean_local_vx_m_s']} | "
            f"{', '.join(cell['failure_reasons']) or 'none'} |"
        )
    lines.extend(["", "Training and simulator reward have zero selection weight.", ""])
    md_path.write_text("\n".join(lines))
    return {
        "id": condition["id"],
        "group": condition["group"],
        "pass": summary["pass"],
        "json_path": str(json_path.relative_to(ROOT)),
        "json_sha256": sha256(json_path),
        "md_path": str(md_path.relative_to(ROOT)),
        "md_sha256": sha256(md_path),
    }


def execute() -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text())
    contract = json.loads(RUNNER_CONTRACT.read_text())
    runner = Path(__file__).resolve()
    if contract["status"] != "PASS_WINNER_V3_VARIABLE_CONFIGURATION_BEHAVIOR_RUNNER_CONTRACT":
        raise RuntimeError("behavior runner contract is not passing")
    if int(contract["formal_behavior_cells_executed"]) != 0:
        raise RuntimeError("behavior runner contract is not zero-outcome")
    if contract["runner_sha256"] != sha256(runner):
        raise RuntimeError("behavior runner changed after contract")
    for name, expected in contract["supporting_tool_hashes"].items():
        if sha256(TOOLS / name) != expected:
            raise RuntimeError(f"supporting tool changed after contract: {name}")
    if any(path.exists() for path in (CELLS, TRACES, CONDITIONS, RESULT_JSON, RESULT_MD)):
        raise RuntimeError("formal output already exists; retry/resume/overwrite is forbidden")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise RuntimeError("formal execution requires a clean worktree")
    plan = matrix_plan(prereg)
    if canonical_sha256(plan) != contract["matrix_plan_sha256"]:
        raise RuntimeError("formal matrix differs from the contracted plan")

    CELLS.mkdir(parents=True)
    TRACES.mkdir(parents=True)
    CONDITIONS.mkdir(parents=True)
    cells: list[dict[str, Any]] = []
    condition_rows = condition_plan(prereg)
    started = time.time()
    for index, condition in enumerate(condition_rows):
        condition_cells = []
        rows = [
            row
            for row in plan
            if row["condition_group"] == condition["group"]
            and row["condition_id"] == condition["id"]
            and row["seed"] == condition["seed"]
        ]
        for row in rows:
            cell = execute_cell(row, prereg)
            cells.append(cell)
            condition_cells.append(cell)
        write_condition(condition, condition_cells)
        print(
            json.dumps(
                {
                    "completed_conditions": index + 1,
                    "total_conditions": len(condition_rows),
                    "completed_cells": len(cells),
                    "passing_cells": sum(1 for cell in cells if cell["pass"]),
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )

    unique = {
        (
            cell["identity"]["condition_group"],
            cell["identity"]["condition_id"],
            cell["identity"]["seed"],
            cell["identity"]["step"],
            cell["identity"]["plant"],
            cell["identity"]["command_x_m_s"],
        )
        for cell in cells
    }
    validity = {
        "all_1024_cells_present_unique": len(cells) == 1024 and len(unique) == 1024,
        "all_cell_and_trace_contracts_complete": all(
            cell["trace"]["rows"] == 600
            and cell["trace"]["ticks_contiguous"]
            and cell["trace"]["required_fields_every_tick"]
            and cell["trace"]["all_values_finite"]
            and all(cell["readback_checks"].values())
            for cell in cells
        ),
        "all_policy_hashes_exact": all(
            cell["policy"]["sha256"]
            == EXPECTED_TRANSFORMED_HASHES[int(cell["identity"]["step"])]
            for cell in cells
        ),
        "all_cpu_only": all(cell["metrics"]["checks"]["cpu_only"] for cell in cells),
        "no_training_or_simulator_reward_selection": all(
            int(cell["training_or_simulator_reward_selection_weight"]) == 0
            for cell in cells
        ),
    }
    failed_validity = [name for name, passed in validity.items() if not passed]
    per_checkpoint = {}
    for step in STEPS:
        subset = [cell for cell in cells if int(cell["identity"]["step"]) == step]
        per_checkpoint[str(step)] = {
            "cells": len(subset),
            "passing_cells": sum(1 for cell in subset if cell["pass"]),
            "all_512_cells_pass": len(subset) == 512
            and all(cell["pass"] for cell in subset),
            "worst_tracking_p95_rad": max(
                cell["metrics"]["worst_tracking_p95_rad"] for cell in subset
            ),
            "worst_current_p95_a": max(
                cell["metrics"]["worst_current_p95_a"] for cell in subset
            ),
            "minimum_moving_mean_vx_m_s": min(
                float(cell["metrics"]["mean_local_vx_m_s"])
                for cell in subset
                if float(cell["identity"]["command_x_m_s"]) > 0.0
                and cell["metrics"]["mean_local_vx_m_s"] is not None
            ),
            "policy_sha256": EXPECTED_TRANSFORMED_HASHES[step],
        }
    both_pass = all(row["all_512_cells_pass"] for row in per_checkpoint.values())
    if failed_validity:
        decision = prereg["advancement"]["invalid_token"]
        status = "INVALID_WINNER_V3_VARIABLE_CONFIGURATION_RESULT"
    elif both_pass:
        decision = prereg["advancement"]["pass_token"]
        status = "PASS_WINNER_V3_VARIABLE_CONFIGURATION_RESULT"
    else:
        decision = prereg["advancement"]["fail_token"]
        status = "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_RESULT"
    failures_by_reason: dict[str, int] = {}
    failures_by_group: dict[str, int] = {}
    for cell in cells:
        if cell["pass"]:
            continue
        group = cell["identity"]["condition_group"]
        failures_by_group[group] = failures_by_group.get(group, 0) + 1
        for reason in cell["failure_reasons"]:
            failures_by_reason[reason] = failures_by_reason.get(reason, 0) + 1
    result = {
        "schema_version": "winner_v3.variable_configuration_result.v1",
        "status": status,
        "decision": decision,
        "selected_policy": (
            {
                "family": "R64_ZERO_INIT_RECURRENT_ADAPTER",
                "required_checkpoints": [
                    {
                        "step": step,
                        "path": str(policy_path(step).relative_to(ROOT)),
                        "sha256": EXPECTED_TRANSFORMED_HASHES[step],
                    }
                    for step in STEPS
                ],
            }
            if decision == prereg["advancement"]["pass_token"]
            else None
        ),
        "validity_checks": validity,
        "failed_validity_checks": failed_validity,
        "cells": len(cells),
        "passing_cells": sum(1 for cell in cells if cell["pass"]),
        "failing_cells": sum(1 for cell in cells if not cell["pass"]),
        "per_checkpoint": per_checkpoint,
        "failures_by_group": dict(sorted(failures_by_group.items())),
        "failures_by_reason": dict(sorted(failures_by_reason.items())),
        "matrix_plan_sha256": contract["matrix_plan_sha256"],
        "runner_sha256": sha256(runner),
        "runner_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "runner_contract_sha256": sha256(RUNNER_CONTRACT),
        "preregistration_sha256": sha256(PREREG),
        "transform_contract_sha256": sha256(TRANSFORM_CONTRACT),
        "wall_seconds": time.time() - started,
        "training_or_simulator_reward_selection_weight": 0,
        "no_closest_promotion": True,
        "authority": {
            "policy_asset_and_clearance_commit_sequence": decision
            == prereg["advancement"]["pass_token"],
            "robot_clearance": False,
            "runtime_or_gate5": False,
            "rdkx5_or_robot": False,
            "training_or_retry": False,
        },
    }
    RESULT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Winner-v3 Variable-Configuration Result",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        "",
        f"Cells: `{result['passing_cells']}/{result['cells']}` pass.",
        "",
        "| checkpoint | cells | passing | all pass | worst tracking p95 | worst current p95 | minimum moving vx |",
        "|---:|---:|---:|---|---:|---:|---:|",
    ]
    for step in STEPS:
        item = per_checkpoint[str(step)]
        lines.append(
            f"| {step} | {item['cells']} | {item['passing_cells']} | "
            f"`{item['all_512_cells_pass']}` | {item['worst_tracking_p95_rad']:.9f} | "
            f"{item['worst_current_p95_a']:.9f} | {item['minimum_moving_mean_vx_m_s']:.9f} |"
        )
    lines.extend(["", "## Failure counts", ""])
    if failures_by_reason:
        lines.extend(f"- `{name}`: `{count}`" for name, count in sorted(failures_by_reason.items()))
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "Both persistent checkpoints must pass all 512 cells. No sibling, closest "
            "configuration, aggregate score, training reward, or simulator reward can "
            "promote a failure.",
            "",
            "This CPU result does not itself authorize RDK-X5/robot access, runtime "
            "adoption, Gate 5, torque, motion, or deployment.",
            "",
        ]
    )
    RESULT_MD.write_text("\n".join(lines))
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan-only", action="store_true")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if args.plan_only:
        result = plan_contract()
        print(json.dumps({"status": result["status"], "failed_checks": result["failed_checks"]}))
        return 0 if not result["failed_checks"] else 1
    result = execute()
    print(json.dumps({"status": result["status"], "decision": result["decision"]}))
    return 0 if not result["failed_validity_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
