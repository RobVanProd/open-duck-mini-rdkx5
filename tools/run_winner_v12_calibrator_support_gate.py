#!/usr/bin/env python3
"""Run the frozen 124-cell support/context gate for two Winner-v12 checkpoints."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(PATCHES))
sys.path.insert(0, str(TOOLS))

import run_winner_v12_calibrator_cpu_smoke as smoke  # noqa: E402
import run_winner_v12_full_calibrator_training as full_training  # noqa: E402
import winner_v12_calibrator_training as training  # noqa: E402


PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
)
CALIBRATOR_DESIGN = (
    ROOT / "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
)
DOMAIN = (
    ROOT
    / "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
)
CHECKPOINTS = (("half", 50), ("final", 100))
TICKS = 250
SOFT_OFFSETS_RAD = np.asarray(
    [
        0.0844,
        0.0721,
        -0.0890,
        0.0371,
        -0.0767,
        0.0245,
        0.0,
        -0.0890,
        -0.0399,
        0.0951,
        -0.0476,
        0.0660,
        0.0798,
        0.1887,
    ],
    dtype=np.float32,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(b"\0")
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(b"\0")
    digest.update(array.tobytes())
    return digest.hexdigest()


def native_quantize_observation(observation: np.ndarray) -> np.ndarray:
    values = np.asarray(observation, dtype=np.float32)
    if values.shape != (115,):
        raise ValueError("native quantization requires one 115-D observation")
    result = values.copy()
    gyro_lsb = np.float32(math.pi / (180.0 * 16.0))
    accel_lsb = np.float32(0.01)
    position_lsb = np.float32(2.0 * math.pi / 4096.0)
    velocity_lsb = np.float32((2.0 * math.pi / 4095.0) * 0.05)
    origin = smoke.HOME_RAD.astype(np.float32) + SOFT_OFFSETS_RAD + np.float32(math.pi)
    result[0:3] = np.round(values[0:3] / gyro_lsb) * gyro_lsb
    result[3:6] = np.round(values[3:6] / accel_lsb) * accel_lsb
    result[13:27] = (
        np.round((values[13:27] + origin) / position_lsb) * position_lsb - origin
    )
    result[27:41] = np.round(values[27:41] / velocity_lsb) * velocity_lsb
    return result.astype(np.float32)


class ObservationTransport:
    """Apply exactly one frozen sensor/transport condition to raw 115-D input."""

    def __init__(
        self,
        condition: Mapping[str, Any] | None,
        rng: np.random.Generator | None,
    ) -> None:
        self.condition = dict(condition or {})
        self.rng = rng
        self.imu_history = np.zeros((3, 6), dtype=np.float32)
        allowed = {
            "id",
            "native_quantization",
            "sensor_noise_scales",
            "additional_action_delay_ticks",
            "imu_delay_ticks",
        }
        if set(self.condition) - allowed:
            raise ValueError("support-gate transport condition schema changed")
        self.imu_delay = int(self.condition.get("imu_delay_ticks", 0))
        if self.imu_delay not in (0, 1, 2):
            raise ValueError("support-gate IMU delay is outside 0..2")

    def observe(self, raw: np.ndarray) -> np.ndarray:
        value = np.asarray(raw, dtype=np.float32).copy()
        if value.shape != (115,) or not np.all(np.isfinite(value)):
            raise ValueError("support-gate raw observation is invalid")
        scales = self.condition.get("sensor_noise_scales")
        if scales is not None:
            if self.rng is None:
                raise ValueError("sensor-noise condition lacks its frozen PRNG")
            expected = {
                "accelerometer",
                "ankle_pos_rad",
                "gravity",
                "gyro_rad_s",
                "hip_pos_rad",
                "joint_vel_rad_s",
                "knee_pos_rad",
                "linvel_m_s",
            }
            if set(scales) != expected:
                raise ValueError("declared sensor-noise scale schema changed")
            value[0:3] += self.rng.uniform(-1.0, 1.0, 3).astype(
                np.float32
            ) * np.float32(scales["gyro_rad_s"])
            value[3:6] += self.rng.uniform(-1.0, 1.0, 3).astype(
                np.float32
            ) * np.float32(scales["accelerometer"])
            position_scale = np.zeros((14,), dtype=np.float32)
            for index, name in enumerate(smoke.JOINT_NAMES):
                if "hip" in name:
                    position_scale[index] = np.float32(scales["hip_pos_rad"])
                elif "knee" in name:
                    position_scale[index] = np.float32(scales["knee_pos_rad"])
                elif "ankle" in name:
                    position_scale[index] = np.float32(scales["ankle_pos_rad"])
            value[13:27] += (
                self.rng.uniform(-1.0, 1.0, 14).astype(np.float32) * position_scale
            )
            value[27:41] += self.rng.uniform(-1.0, 1.0, 14).astype(
                np.float32
            ) * np.float32(scales["joint_vel_rad_s"] * 0.05)
        self.imu_history = np.roll(self.imu_history, 1, axis=0)
        self.imu_history[0] = value[0:6]
        value[0:6] = self.imu_history[self.imu_delay]
        if self.condition.get("native_quantization") is True:
            value = native_quantize_observation(value)
        if not np.all(np.isfinite(value)):
            raise FloatingPointError(
                "support-gate transported observation is nonfinite"
            )
        return value


class DelayedActionQueue:
    def __init__(self, delay_ticks: int) -> None:
        if delay_ticks not in (0, 1, 2):
            raise ValueError("support-gate action delay is outside 0..2")
        self.delay_ticks = delay_ticks
        self.history = [np.zeros((14,), dtype=np.float32) for _ in range(3)]

    def push(self, action: np.ndarray) -> np.ndarray:
        value = np.asarray(action, dtype=np.float32)
        if value.shape != (14,) or not np.all(np.isfinite(value)):
            raise ValueError("support-gate delayed action is invalid")
        self.history = [value.copy(), *self.history[:2]]
        return self.history[self.delay_ticks].copy()


def step_episode(
    episode: Any, requested_action: np.ndarray, delayed_action: np.ndarray
) -> tuple[bool, np.ndarray | None, dict[str, Any]]:
    requested = np.asarray(requested_action, dtype=np.float32)
    delayed = np.asarray(delayed_action, dtype=np.float32)
    if not np.array_equal(
        requested, smoke.bounded_action_numpy(requested, episode.previous_action)
    ):
        raise ValueError("support-gate ONNX action violates graph boundary")
    sent_target = smoke.HOME_RAD + delayed.astype(np.float64) * smoke.ACTION_SCALE_RAD
    applied_target = episode.bridge.step(sent_target, smoke.CONTROL_DT_S)
    observed_target = episode.observer.step(sent_target, smoke.CONTROL_DT_S)
    if not np.all(np.isfinite(applied_target)) or not np.all(
        np.isfinite(observed_target)
    ):
        raise FloatingPointError("support-gate bridge or observer target is nonfinite")
    episode.maximum_observer_physical_separation_rad = max(
        episode.maximum_observer_physical_separation_rad,
        float(np.max(np.abs(observed_target - applied_target))),
    )
    episode.data.ctrl[:] = applied_target
    for _ in range(smoke.PHYSICS_SUBSTEPS):
        episode.mujoco.mj_step(episode.model, episode.data)
    valid, evidence = episode._validity()
    evidence.update(
        {
            "requested_action_sha256": array_sha256(requested),
            "delayed_action_sha256": array_sha256(delayed),
            "sent_target_sha256": array_sha256(sent_target),
            "physical_applied_target_sha256": array_sha256(applied_target),
            "fixed_p30_observer_target_sha256": array_sha256(observed_target),
        }
    )
    if not valid:
        return False, None, evidence
    episode.history = [requested.copy(), *episode.history[:3]]
    episode.valid_ticks += 1
    return True, episode.observation(), evidence


def nominal_configuration(mujoco: Any, scene: Path) -> dict[str, Any]:
    model = mujoco.MjModel.from_xml_path(str(scene))
    body_id = 2
    if model.body(body_id).name != "trunk_assembly":
        raise ValueError("support-gate nominal torso identity changed")
    inertia = np.diag(np.asarray(model.body_inertia[body_id], dtype=np.float64))
    return {
        "id": "NOMINAL_MODEL",
        "sampling_role": "sensor_transport_nominal_only",
        "all_link_mass_scale": 1.0,
        "torso_mass_add_kg": 0.0,
        "torso_com_offset_m": [0.0, 0.0, 0.0],
        "torso_inertia_tensor_kg_m2": inertia.tolist(),
    }


def support_pass(summary: Mapping[str, Any]) -> bool:
    return bool(
        summary["valid_ticks"] == TICKS
        and summary["initial_contacts"] == [1, 1]
        and summary["minimum_base_z_m"] >= smoke.MINIMUM_BASE_Z_M
        and summary["maximum_abs_tilt_rad"] <= smoke.MAXIMUM_ABS_TILT_RAD
        and summary["maximum_torque_nm"] <= smoke.TORQUE_LIMIT_NM
        and summary["maximum_current_a"] <= smoke.CURRENT_LIMIT_A
        and summary["maximum_overcurrent_streak_ticks"] < smoke.OVERCURRENT_TRIP_TICKS
        and summary["maximum_final_window_gyro_xy_norm_rad_s"]
        <= smoke.FINAL_GYRO_LIMIT_RAD_S
    )


def run_cell(
    *,
    mujoco: Any,
    scene: Path,
    configuration: Mapping[str, Any],
    plant: str,
    calibrator_design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    session: Any,
    parameters: Mapping[str, Any],
    target_mean: np.ndarray,
    target_std: np.ndarray,
    condition: Mapping[str, Any] | None = None,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    import jax.numpy as jnp

    episode = smoke.Episode(
        mujoco,
        scene,
        configuration,
        plant,
        calibrator_design,
        observer_type,
        canonical_fit,
    )
    if episode.initial_contacts != (1, 1):
        raise ValueError("support-gate cell does not start with both feet loaded")
    transport = ObservationTransport(condition, rng)
    action_delay = DelayedActionQueue(
        int((condition or {}).get("additional_action_delay_ticks", 0))
    )
    observation = transport.observe(episode.observation())
    previous_action = np.zeros((14,), dtype=np.float32)
    h_in = np.zeros((64,), dtype=np.float32)
    observations = []
    actions = []
    predictions = []
    hidden = []
    normalized_squared_errors = []
    baseline_normalized_squared_errors = []
    maximum_jax_onnx_hidden_error = 0.0
    previous_action_chain_exact = True
    terminal = None
    for tick in range(TICKS):
        outputs = session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {
                "obs": observation[None, :],
                "previous_action": previous_action[None, :],
                "h_in": h_in[None, :],
            },
        )
        action = np.asarray(outputs[0][0], dtype=np.float32)
        previous_out = np.asarray(outputs[1][0], dtype=np.float32)
        h_out = np.asarray(outputs[2][0], dtype=np.float32)
        previous_action_chain_exact &= np.array_equal(previous_out, action)
        jax_h, prediction = training.response_step(
            parameters,
            jnp.asarray(observation),
            jnp.asarray(previous_action),
            jnp.asarray(h_in),
            jnp.asarray(action),
        )
        prediction_np = np.asarray(prediction, dtype=np.float32)
        maximum_jax_onnx_hidden_error = max(
            maximum_jax_onnx_hidden_error,
            float(np.max(np.abs(np.asarray(jax_h, dtype=np.float32) - h_out))),
        )
        delayed = action_delay.push(action)
        valid, next_raw, evidence = step_episode(episode, action, delayed)
        observations.append(observation.copy())
        actions.append(action.copy())
        predictions.append(prediction_np.copy())
        hidden.append(h_out.copy())
        if not valid:
            terminal = {"tick": tick, **evidence}
            break
        if next_raw is None:
            raise AssertionError("valid support-gate transition lacks next observation")
        next_observation = transport.observe(next_raw)
        target = next_observation[training.AUXILIARY_INDICES]
        normalized_squared_errors.append(
            np.square((prediction_np - target) / target_std)
        )
        baseline_normalized_squared_errors.append(
            np.square((target_mean - target) / target_std)
        )
        observation = next_observation
        previous_action = action
        h_in = h_out
    summary = episode.summary()
    learned_mse = (
        float(np.mean(np.asarray(normalized_squared_errors, dtype=np.float64)))
        if normalized_squared_errors
        else math.inf
    )
    baseline_mse = (
        float(np.mean(np.asarray(baseline_normalized_squared_errors, dtype=np.float64)))
        if baseline_normalized_squared_errors
        else math.inf
    )
    arrays = {
        "observations": np.asarray(observations, dtype=np.float32),
        "actions": np.asarray(actions, dtype=np.float32),
        "predictions": np.asarray(predictions, dtype=np.float32),
        "hidden": np.asarray(hidden, dtype=np.float32),
    }
    return {
        "configuration_id": configuration["id"],
        "configuration_sha256": canonical_sha256(configuration),
        "plant": plant,
        "condition": None if condition is None else dict(condition),
        "terminal": terminal,
        "episode": summary,
        "support_pass": support_pass(summary) and terminal is None,
        "previous_action_chain_exact": bool(previous_action_chain_exact),
        "maximum_jax_onnx_hidden_error": maximum_jax_onnx_hidden_error,
        "learned_normalized_prediction_mse": learned_mse,
        "constant_normalized_prediction_mse": baseline_mse,
        "final_h_out": h_in.astype(float).tolist(),
        "trace_hashes": {name: array_sha256(value) for name, value in arrays.items()},
        "_arrays": arrays,
    }


def public_cell(cell: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in cell.items() if key != "_arrays"}


def repeated_exact(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return public_cell(left) == public_cell(right) and all(
        np.array_equal(left["_arrays"][key], right["_arrays"][key])
        for key in left["_arrays"]
    )


def checkpoint_paths(work_root: Path, label: str) -> tuple[Path, Path]:
    return (
        work_root / f"winner_v12_calibrator_{label}.npz",
        work_root / f"winner_v12_calibrator_{label}.onnx",
    )


def load_calibrator_design(
    full_training_preregistration: Mapping[str, Any],
) -> dict[str, Any]:
    """Load the Episode plant design, not the distinct full-training plan."""

    source = full_training_preregistration.get("sources", {}).get(
        "calibrator_design_preregistration", {}
    )
    if (
        source.get("path")
        != "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
        or source.get("hash_mode") != "lf"
        or source.get("sha256") != smoke.lf_sha256(CALIBRATOR_DESIGN)
    ):
        raise ValueError("calibrator-design provenance changed")
    design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    if (
        design.get("status") != "PREREGISTERED_IMPLEMENTATION_NOT_RUN"
        or "hidden_configuration_domain" not in design
        or "continuous_training_domain"
        not in design["hidden_configuration_domain"]
    ):
        raise ValueError("calibrator-design hidden configuration domain changed")
    return design


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-gate-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.formal_gate_authorized:
        raise PermissionError(
            "support gate requires --offline-cpu-only --formal-gate-authorized"
        )
    if args.output.exists():
        raise FileExistsError(
            f"refusing to overwrite support-gate result: {args.output}"
        )
    import jax
    import mujoco
    import onnxruntime as ort

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("support gate requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = load_calibrator_design(preregistration)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    gate = preregistration["future_frozen_support_gate"]
    if (
        gate["cells_per_checkpoint"] != 124
        or gate["checkpoint_labels"] != ["half", "final"]
        or gate["duration_ticks"] != TICKS
    ):
        raise ValueError("frozen support-gate dimensions changed")
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"]
        + matrix["discovery_samples"]
        + matrix["heldout_samples"]
    )
    if len(configurations) != 56:
        raise ValueError("support-gate model configuration population changed")
    heldout_ids = {row["id"] for row in matrix["heldout_samples"]}
    conditions = gate["sensor_transport_population"]
    if canonical_sha256(conditions) != gate["sensor_transport_population_sha256"]:
        raise ValueError("support-gate sensor/transport population changed")
    scene = (
        args.playground_root
        / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    )
    if not scene.is_file():
        raise FileNotFoundError(scene)
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    nominal = nominal_configuration(mujoco, scene)
    session_options = ort.SessionOptions()
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1
    session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    checkpoint_results = []
    for checkpoint_index, (label, update) in enumerate(CHECKPOINTS):
        checkpoint_path, graph_path = checkpoint_paths(args.training_work_root, label)
        snapshot = full_training.load_snapshot(checkpoint_path)
        full_training.validate_resume(snapshot)
        if (
            snapshot["metadata"]["stage"] != "stage2"
            or snapshot["metadata"]["completed_updates"] != update
        ):
            raise ValueError(f"{label} checkpoint boundary changed")
        parameters = snapshot["parameters"]
        target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
        target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
        session = ort.InferenceSession(
            str(graph_path),
            sess_options=session_options,
            providers=["CPUExecutionProvider"],
        )
        core_cells = []
        repeated_cells = []
        heldout_by_configuration: dict[str, dict[str, dict[str, Any]]] = {}
        for configuration in configurations:
            for plant in smoke.PLANTS:
                cell = run_cell(
                    mujoco=mujoco,
                    scene=scene,
                    configuration=configuration,
                    plant=plant,
                    calibrator_design=calibrator_design,
                    observer_type=observer_type,
                    canonical_fit=args.canonical_fit,
                    session=session,
                    parameters=parameters,
                    target_mean=target_mean,
                    target_std=target_std,
                )
                core_cells.append(public_cell(cell))
                if configuration["id"] in heldout_ids:
                    repeat = run_cell(
                        mujoco=mujoco,
                        scene=scene,
                        configuration=configuration,
                        plant=plant,
                        calibrator_design=calibrator_design,
                        observer_type=observer_type,
                        canonical_fit=args.canonical_fit,
                        session=session,
                        parameters=parameters,
                        target_mean=target_mean,
                        target_std=target_std,
                    )
                    repeated_cells.append(
                        {
                            "configuration_id": configuration["id"],
                            "plant": plant,
                            "bit_exact": repeated_exact(cell, repeat),
                            "first_trace_hashes": cell["trace_hashes"],
                            "repeat_trace_hashes": repeat["trace_hashes"],
                        }
                    )
                    heldout_by_configuration.setdefault(configuration["id"], {})[
                        plant
                    ] = cell
        sensor_cells = []
        for condition_index, condition in enumerate(conditions):
            for plant_index, plant in enumerate(smoke.PLANTS):
                sequence = np.random.SeedSequence(
                    [120120, 3, checkpoint_index, condition_index, plant_index]
                )
                rng = np.random.Generator(np.random.PCG64(sequence))
                cell = run_cell(
                    mujoco=mujoco,
                    scene=scene,
                    configuration=nominal,
                    plant=plant,
                    calibrator_design=calibrator_design,
                    observer_type=observer_type,
                    canonical_fit=args.canonical_fit,
                    session=session,
                    parameters=parameters,
                    target_mean=target_mean,
                    target_std=target_std,
                    condition=condition,
                    rng=rng,
                )
                public = public_cell(cell)
                public["prng"] = {
                    "algorithm": "NumPy PCG64",
                    "seed_sequence_entropy": [
                        120120,
                        3,
                        checkpoint_index,
                        condition_index,
                        plant_index,
                    ],
                    "seed_sequence_state_u32": sequence.generate_state(4)
                    .astype(int)
                    .tolist(),
                }
                sensor_cells.append(public)
        context = []
        for configuration in matrix["heldout_samples"]:
            pair = heldout_by_configuration[configuration["id"]]
            left = pair[smoke.PLANTS[0]]
            right = pair[smoke.PLANTS[1]]
            separation = float(
                np.max(
                    np.abs(
                        np.asarray(left["final_h_out"], dtype=np.float32)
                        - np.asarray(right["final_h_out"], dtype=np.float32)
                    )
                )
            )
            context.append(
                {
                    "configuration_id": configuration["id"],
                    "final_h_out_linf_separation": separation,
                    "separation_above_1e_7": separation > 1.0e-7,
                }
            )
        prediction_by_plant = {}
        for plant in smoke.PLANTS:
            rows = [
                heldout_by_configuration[configuration["id"]][plant]
                for configuration in matrix["heldout_samples"]
            ]
            learned = float(
                np.mean([row["learned_normalized_prediction_mse"] for row in rows])
            )
            baseline = float(
                np.mean([row["constant_normalized_prediction_mse"] for row in rows])
            )
            prediction_by_plant[plant] = {
                "learned_normalized_prediction_mse": learned,
                "constant_normalized_prediction_mse": baseline,
                "learned_strictly_below_constant": learned < baseline,
            }
        all_cells = core_cells + sensor_cells
        checks = {
            "exact_124_main_cells": len(all_cells) == 124,
            "all_support_cells_pass": all(row["support_pass"] for row in all_cells),
            "all_previous_action_chains_exact": all(
                row["previous_action_chain_exact"] for row in all_cells
            ),
            "all_jax_onnx_hidden_errors_at_most_1e_7": all(
                row["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for row in all_cells
            ),
            "all_32_heldout_repeats_bit_exact": len(repeated_cells) == 32
            and all(row["bit_exact"] for row in repeated_cells),
            "all_16_heldout_contexts_separate": len(context) == 16
            and all(row["separation_above_1e_7"] for row in context),
            "learned_prediction_beats_constant_per_plant": all(
                row["learned_strictly_below_constant"]
                for row in prediction_by_plant.values()
            ),
        }
        checkpoint_results.append(
            {
                "label": label,
                "update": update,
                "checkpoint_sha256": sha256(checkpoint_path),
                "onnx_sha256": sha256(graph_path),
                "core_model_plant_cells": core_cells,
                "sensor_transport_plant_cells": sensor_cells,
                "heldout_repeatability": repeated_cells,
                "heldout_context_separation": context,
                "heldout_prediction": prediction_by_plant,
                "checks": {name: bool(value) for name, value in checks.items()},
                "failed_checks": sorted(
                    name for name, passed in checks.items() if not passed
                ),
            }
        )
    checks = {
        "both_checkpoints_evaluated": [row["label"] for row in checkpoint_results]
        == ["half", "final"],
        "all_248_main_cells_pass": all(
            not row["failed_checks"] for row in checkpoint_results
        ),
        "formal_cell_count_exact": sum(
            len(row["core_model_plant_cells"])
            + len(row["sensor_transport_plant_cells"])
            for row in checkpoint_results
        )
        == 248,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v12.calibrator_support_gate_result.v1",
        "status": (
            "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
            if not failed
            else "HOLD_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
        ),
        "decision": (
            "AUTHORIZE_RESPONSE_CONDITIONED_LOCOMOTION_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        ),
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "sources": {
            "preregistration_lf_sha256": smoke.lf_sha256(PREREGISTRATION),
            "calibrator_design_lf_sha256": smoke.lf_sha256(CALIBRATOR_DESIGN),
            "domain_lf_sha256": smoke.lf_sha256(DOMAIN),
            "training_runner_lf_sha256": smoke.lf_sha256(
                ROOT / "tools/run_winner_v12_full_calibrator_training.py"
            ),
            "gate_runner_lf_sha256": smoke.lf_sha256(Path(__file__)),
        },
        "checkpoint_results": checkpoint_results,
        "execution": {
            "formal_support_cells": 248,
            "heldout_repeat_cells": 64,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate response-conditioned locomotion-training preregistration",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
