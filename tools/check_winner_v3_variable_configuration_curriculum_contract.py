#!/usr/bin/env python3
"""Validate the frozen winner-v3 coupled curriculum before CPU training."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RECURRENT_CONTRACT = ANALYSIS / "winner_v3_recurrent_adapter_cpu_contract.json"
PREOUTCOME = ANALYSIS / "winner_v3_variable_configuration_curriculum_preoutcome_contract.json"
IMPLEMENTATION = ROOT / "patches/winner_v3_variable_configuration.py"
INTEGRATION_PATCH = ROOT / "patches/ground_up_winner_v3_variable_configuration.patch"
COMPOSER = ROOT / "tools/compose_winner_v3_playground.py"
OUT_JSON = ANALYSIS / "winner_v3_variable_configuration_curriculum_contract.json"
OUT_MD = ANALYSIS / "WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_CONTRACT_20260719.md"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
PYTHON = Path("/home/lsd/robots/envs/open-duck-playground/bin/python")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def as_bool(value: Any) -> bool:
    return bool(np.asarray(value).item())


def _configure_env(joystick, winner_v3=None):
    cfg = joystick.default_config()
    cfg.nominal_reference_bootstrap = True
    cfg.reference_feature_table_path = str(REFERENCE)
    cfg.recurrent_hidden_dim = 64
    cfg.ground_up_hard_vector_command_support = True
    cfg.ground_up_command_support_range = [0.074, 0.080]
    cfg.ground_up_action_velocity_limits_rad_s = [
        1.0, 0.75, 1.5, 1.5, 1.5, 0.5, 0.5,
        0.5, 0.5, 0.5, 0.75, 1.25, 1.0, 1.25,
    ]
    cfg.ground_up_measured_actuator_bridge = True
    cfg.ground_up_applied_target_observation = True
    cfg.noise_config.level = 0.0
    cfg.noise_config.action_min_delay = 0
    cfg.noise_config.action_max_delay = 1
    cfg.noise_config.imu_min_delay = 0
    cfg.noise_config.imu_max_delay = 1
    cfg.push_config.enable = False
    if winner_v3 is not None:
        cfg.winner_v3_variable_configuration = True
        cfg.winner_v3_deviation_scale = 1.0
        cfg.noise_config.level = 1.0
        cfg.noise_config.action_max_delay = 3
        cfg.noise_config.imu_max_delay = 3
    return cfg


def trace_worker(playground: Path, output: Path) -> int:
    os.chdir(playground)
    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash", config=_configure_env(joystick)
    )
    reset = jax.jit(env.reset)
    step = jax.jit(env.step)
    state = reset(jax.random.PRNGKey(167931544))
    rows: dict[str, list[np.ndarray]] = {
        "qpos": [], "qvel": [], "ctrl": [], "obs": [], "reward": [],
        "done": [], "motor_targets": [], "applied_targets": [],
        "last_act": [], "phase": [], "command": [],
    }
    actions = [
        jnp.zeros(14, dtype=jnp.float32),
        jnp.linspace(-0.2, 0.2, 14, dtype=jnp.float32),
        jnp.linspace(0.1, -0.1, 14, dtype=jnp.float32),
    ]
    for action in actions:
        rows["qpos"].append(np.asarray(state.data.qpos))
        rows["qvel"].append(np.asarray(state.data.qvel))
        rows["ctrl"].append(np.asarray(state.data.ctrl))
        rows["obs"].append(np.asarray(state.obs["state"]))
        rows["reward"].append(np.asarray(state.reward))
        rows["done"].append(np.asarray(state.done))
        rows["motor_targets"].append(np.asarray(state.info["motor_targets"]))
        rows["applied_targets"].append(
            np.asarray(state.info["ground_up_actuator_bridge_applied_targets"])
        )
        rows["last_act"].append(np.asarray(state.info["last_act"]))
        rows["phase"].append(np.asarray(state.info["imitation_phase"]))
        rows["command"].append(np.asarray(state.info["command"]))
        state = step(state, action)
    np.savez(output, **{name: np.asarray(values) for name, values in rows.items()})
    return 0


def run_trace_worker(playground: Path, output: Path) -> dict[str, Any]:
    command = [
        str(PYTHON), str(Path(__file__).resolve()), "--trace-worker",
        "--playground-root", str(playground), "--trace-output", str(output),
    ]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(playground)
    completed = subprocess.run(
        command,
        cwd=playground,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1200,
        check=False,
    )
    log_path = output.with_suffix(".log")
    log_path.write_text(completed.stdout)
    if completed.returncode != 0:
        raise RuntimeError(
            f"default-off trace worker failed for {playground}:\n{completed.stdout[-4000:]}"
        )
    return {
        "path": str(output),
        "sha256": sha256(output),
        "log_sha256": sha256(log_path),
    }


def compare_npz(left: Path, right: Path) -> tuple[bool, float, dict[str, float]]:
    a = np.load(left)
    b = np.load(right)
    if set(a.files) != set(b.files):
        return False, float("inf"), {}
    errors: dict[str, float] = {}
    exact = True
    for name in sorted(a.files):
        exact &= a[name].dtype == b[name].dtype and a[name].shape == b[name].shape
        exact &= np.array_equal(a[name], b[name])
        errors[name] = float(
            np.max(np.abs(a[name].astype(np.float64) - b[name].astype(np.float64)))
        )
    return exact, max(errors.values(), default=0.0), errors


def path_name(path: tuple[Any, ...]) -> str:
    return "/".join(
        str(getattr(entry, "key", getattr(entry, "idx", entry))).lstrip(".")
        for entry in path
    )


def changed_model_leaves(model, randomized) -> set[str]:
    changed: set[str] = set()
    for (path, nominal), (_, sampled) in zip(
        jax.tree_util.tree_flatten_with_path(model)[0],
        jax.tree_util.tree_flatten_with_path(randomized)[0],
        strict=True,
    ):
        nominal_array = np.asarray(nominal)
        sampled_array = np.asarray(sampled)
        expected = np.broadcast_to(nominal_array, sampled_array.shape)
        if not np.array_equal(sampled_array, expected):
            changed.add(path_name(path))
    return changed


def independent_quantize(obs: np.ndarray, home: np.ndarray) -> np.ndarray:
    values = np.asarray(obs, dtype=np.float32)
    result = values.copy()
    gyro_lsb = np.float32(math.pi / (180.0 * 16.0))
    accel_lsb = np.float32(0.01)
    position_lsb = np.float32(2.0 * math.pi / 4096.0)
    velocity_lsb = np.float32((2.0 * math.pi / 4095.0) * 0.05)
    offsets = np.asarray(
        [0.0844, 0.0721, -0.0890, 0.0371, -0.0767, 0.0245, 0.0,
         -0.0890, -0.0399, 0.0951, -0.0476, 0.0660, 0.0798, 0.1887],
        dtype=np.float32,
    )
    origin = (home.astype(np.float32) + offsets + np.float32(math.pi)).astype(np.float32)
    result[0:3] = np.round(values[0:3] / gyro_lsb) * gyro_lsb
    result[3:6] = np.round(values[3:6] / accel_lsb) * accel_lsb
    result[13:27] = (
        np.round((values[13:27] + origin) / position_lsb) * position_lsb - origin
    )
    result[27:41] = np.round(values[27:41] / velocity_lsb) * velocity_lsb
    return result.astype(np.float32)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--trace-worker", action="store_true")
    parser.add_argument("--trace-output", type=Path)
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    if args.trace_worker:
        if args.trace_output is None:
            raise ValueError("trace worker requires --trace-output")
        return trace_worker(playground, args.trace_output.resolve())
    if args.baseline_root is None or args.work_root is None:
        raise ValueError("formal checker requires --baseline-root and --work-root")
    baseline = args.baseline_root.resolve()
    work = args.work_root.resolve()
    if work.exists():
        raise FileExistsError(f"no reuse/retry of contract work root: {work}")
    work.mkdir(parents=True)

    input_paths = {
        "preregistration": PREREG,
        "recurrent_cpu_contract": RECURRENT_CONTRACT,
        "implementation": IMPLEMENTATION,
        "integration_patch": INTEGRATION_PATCH,
        "composer": COMPOSER,
        "checker": Path(__file__).resolve(),
    }
    input_hashes = {name: sha256(path) for name, path in input_paths.items()}
    prereg = json.loads(PREREG.read_text())
    recurrent = json.loads(RECURRENT_CONTRACT.read_text())
    preoutcome = json.loads(PREOUTCOME.read_text()) if PREOUTCOME.exists() else None
    preoutcome_exact = bool(
        preoutcome
        and preoutcome.get("status") == "PASS_WINNER_V3_CURRICULUM_PREOUTCOME_CONTRACT"
        and preoutcome.get("input_hashes") == input_hashes
        and preoutcome.get("formal_training_steps_executed") == 0
        and preoutcome.get("formal_behavior_cells_executed") == 0
    )

    baseline_trace = work / "baseline_default_off.npz"
    patched_trace = work / "patched_default_off.npz"
    baseline_trace_meta = run_trace_worker(baseline, baseline_trace)
    patched_trace_meta = run_trace_worker(playground, patched_trace)
    default_exact, default_error, default_errors = compare_npz(
        baseline_trace, patched_trace
    )

    sys.path.insert(0, str(playground))
    os.chdir(playground)
    from playground.common import winner_v3_variable_configuration as winner_v3
    from playground.open_duck_mini_v2 import joystick

    devices = [str(device) for device in jax.devices()]
    cpu_only = bool(jax.devices()) and all(device.platform == "cpu" for device in jax.devices())
    env = joystick.Joystick(task="flat_terrain_backlash", config=joystick.default_config())
    model = env.mjx_model
    torso_id = int(env.mj_model.body(winner_v3.TORSO_BODY_NAME).id)
    sample_count = 4096
    keys = jax.random.split(jax.random.PRNGKey(100), sample_count)

    scale_results: dict[str, Any] = {}
    full_randomized = None
    for scale in (0.0, 0.25, 0.5, 1.0):
        randomized, in_axes = winner_v3.make_winner_v3_configuration_randomizer(
            torso_body_id=torso_id, deviation_scale=scale
        )(model, keys)
        if scale == 1.0:
            full_randomized = randomized
        body_mass = np.asarray(randomized.body_mass)
        body_ipos = np.asarray(randomized.body_ipos)
        floor = np.asarray(randomized.geom_friction)[:, winner_v3.FLOOR_GEOM_ID, 0]
        friction = np.asarray(randomized.dof_frictionloss)
        armature = np.asarray(randomized.dof_armature)
        nominal_mass = np.asarray(model.body_mass)
        non_torso = np.asarray(
            [index for index, value in enumerate(nominal_mass) if value > 0.0 and index != torso_id]
        )
        link_scales = body_mass[:, non_torso] / nominal_mass[non_torso]
        expected_floor_low = 1.0 - 0.5 * scale
        changed = changed_model_leaves(model, randomized)
        scale_results[str(scale)] = {
            "changed_model_leaves": sorted(changed),
            "in_axes_dynamic": sorted(
                path_name(path)
                for path, value in jax.tree_util.tree_flatten_with_path(in_axes)[0]
                if value == 0
            ),
            "floor_min_max": [float(floor.min()), float(floor.max())],
            "link_scale_min_max": [float(link_scales.min()), float(link_scales.max())],
            "torso_mass_min_max": [float(body_mass[:, torso_id].min()), float(body_mass[:, torso_id].max())],
            "com_offset_min": np.min(body_ipos[:, torso_id] - np.asarray(model.body_ipos[torso_id]), axis=0).tolist(),
            "com_offset_max": np.max(body_ipos[:, torso_id] - np.asarray(model.body_ipos[torso_id]), axis=0).tolist(),
            "bounds_pass": bool(
                floor.min() >= expected_floor_low - 2e-7
                and floor.max() <= 1.0 + 2e-7
                and link_scales.min() >= 1.0 - 0.1 * scale - 2e-7
                and link_scales.max() <= 1.0 + 0.1 * scale + 2e-7
                and body_mass[:, torso_id].min() >= (
                    float(model.body_mass[torso_id]) * (1.0 - 0.1 * scale) - 0.1 * scale - 2e-7
                )
                and body_mass[:, torso_id].max() <= (
                    float(model.body_mass[torso_id]) * (1.0 + 0.1 * scale) + 0.1 * scale + 2e-7
                )
                and np.max(np.abs(body_ipos[:, torso_id] - np.asarray(model.body_ipos[torso_id]))) <= 0.05 * scale + 2e-7
                and np.all(np.isfinite(friction))
                and np.all(np.isfinite(armature))
            ),
        }

    assert full_randomized is not None
    tensor_jax = jax.vmap(
        lambda quat, inertia: winner_v3.reconstruct_relative_inertia_tensor(
            model.body_iquat[torso_id], quat, inertia
        )
    )(
        full_randomized.body_iquat[:, torso_id],
        full_randomized.body_inertia[:, torso_id],
    )
    tensors = np.asarray(tensor_jax)
    eigenvalues = np.linalg.eigvalsh(tensors)
    diagonals = np.diagonal(tensors, axis1=1, axis2=2)
    products = tensors[:, [0, 0, 1], [1, 2, 2]]
    inertia_pass = bool(
        np.all(eigenvalues > 0.0)
        and np.all(eigenvalues[:, 2] < eigenvalues[:, 0] + eigenvalues[:, 1])
        and np.all(diagonals >= np.asarray(winner_v3.TORSO_INERTIA_DIAGONAL_BOUNDS)[:, 0] - 2e-7)
        and np.all(diagonals <= np.asarray(winner_v3.TORSO_INERTIA_DIAGONAL_BOUNDS)[:, 1] + 2e-7)
        and np.max(np.abs(products)) <= float(winner_v3.TORSO_INERTIA_PRODUCT_LIMIT) + 2e-7
    )

    episode_results: dict[str, Any] = {}
    for scale in (0.0, 0.25, 0.5, 1.0):
        episode = jax.vmap(
            lambda key: winner_v3.sample_episode_contract(key, scale)
        )(keys)
        gain = np.asarray(episode["actuator_gain_ratio"])
        tau = np.asarray(episode["actuator_tau_s"])
        delays = np.asarray(episode["actuator_delay_ticks"])
        action_delay = np.asarray(episode["additional_action_delay_ticks"])
        imu_delay = np.asarray(episode["imu_delay_ticks"])
        native = np.asarray(episode["native_quantization"])
        noise = np.asarray(episode["sensor_noise_scales"])
        p30_gain = np.asarray(winner_v3.P30_GAIN_RATIO)
        other_gain = np.asarray(winner_v3.P31_34_GAIN_RATIO)
        p30_tau = np.asarray(winner_v3.P30_TAU_S)
        other_tau = np.asarray(winner_v3.P31_34_TAU_S)
        gain_low = p30_gain + scale * (np.minimum(p30_gain, other_gain) - p30_gain)
        gain_high = p30_gain + scale * (np.maximum(p30_gain, other_gain) - p30_gain)
        tau_low = p30_tau + scale * (np.minimum(p30_tau, other_tau) - p30_tau)
        tau_high = p30_tau + scale * (np.maximum(p30_tau, other_tau) - p30_tau)
        max_delay = int(math.floor(2.0 * scale + 1e-6))
        episode_results[str(scale)] = {
            "action_delay_values": np.unique(action_delay).tolist(),
            "imu_delay_values": np.unique(imu_delay).tolist(),
            "native_true_count": int(native.sum()),
            "native_probability": float(np.asarray(episode["native_quantization_probability"])[0]),
            "bounds_pass": bool(
                np.all(gain >= gain_low - 2e-7)
                and np.all(gain <= gain_high + 2e-7)
                and np.all(tau >= tau_low - 2e-7)
                and np.all(tau <= tau_high + 2e-7)
                and np.array_equal(delays, np.broadcast_to(np.asarray(winner_v3.P30_DELAY_TICKS), delays.shape))
                and np.all((action_delay >= 0) & (action_delay <= max_delay))
                and np.all((imu_delay >= 0) & (imu_delay <= max_delay))
                and np.allclose(noise, np.asarray(winner_v3.SENSOR_NOISE_MAXIMUM_SCALES) * scale, rtol=0.0, atol=0.0)
                and np.all(np.asarray(episode["deviation_scale"]) == np.float32(scale))
            ),
        }

    rng = np.random.Generator(np.random.PCG64(100))
    home = np.asarray(env._default_actuator, dtype=np.float32)
    quant_errors = []
    unchanged = []
    for _ in range(64):
        obs = rng.uniform(-1.0, 1.0, 115).astype(np.float32)
        expected = independent_quantize(obs, home)
        actual = np.asarray(
            winner_v3.native_quantize_observation(jnp.asarray(obs), home_rad=jnp.asarray(home))
        )
        quant_errors.append(float(np.max(np.abs(expected.astype(float) - actual.astype(float)))))
        unchanged.append(
            np.array_equal(obs[6:13], actual[6:13])
            and np.array_equal(obs[41:115], actual[41:115])
        )

    bridge_cfg = _configure_env(joystick, winner_v3)
    bridge_env = joystick.Joystick(task="flat_terrain_backlash", config=bridge_cfg)
    episode_one = winner_v3.sample_episode_contract(jax.random.PRNGKey(712), 1.0)
    sent = bridge_env._default_actuator + jnp.linspace(-0.08, 0.08, 14)
    bridge_info = {
        "ground_up_actuator_bridge_target_history": jnp.tile(sent, 4),
        "ground_up_actuator_bridge_applied_targets": bridge_env._default_actuator,
        "winner_v3_actuator_delay_ticks": episode_one["actuator_delay_ticks"],
        "winner_v3_actuator_tau_s": episode_one["actuator_tau_s"],
        "winner_v3_actuator_gain_ratio": episode_one["actuator_gain_ratio"],
    }
    actual_bridge = np.asarray(
        bridge_env._apply_ground_up_measured_actuator_bridge(bridge_info, sent)
    )
    desired = np.asarray(bridge_env._default_actuator) + np.asarray(
        episode_one["actuator_gain_ratio"]
    ) * (np.asarray(sent) - np.asarray(bridge_env._default_actuator))
    alpha = 1.0 - np.exp(-float(bridge_env.dt) / np.asarray(episode_one["actuator_tau_s"]))
    expected_bridge = np.asarray(bridge_env._default_actuator) + alpha * (
        desired - np.asarray(bridge_env._default_actuator)
    )
    max_step = np.asarray(winner_v3.CONSERVATIVE_VELOCITY_LIMITS_RAD_S) * float(bridge_env.dt)
    expected_bridge = np.clip(
        expected_bridge,
        np.asarray(bridge_env._default_actuator) - max_step,
        np.asarray(bridge_env._default_actuator) + max_step,
    )
    bridge_error = float(np.max(np.abs(actual_bridge - expected_bridge)))

    joystick_source = (playground / "playground/open_duck_mini_v2/joystick.py").read_text()
    state_block = joystick_source.split("state_parts = [", 1)[1].split("state = jp.hstack", 1)[0]
    readback_names = (
        "winner_v3_actuator_gain_ratio", "winner_v3_actuator_tau_s",
        "winner_v3_actuator_delay_ticks", "winner_v3_additional_action_delay_ticks",
        "winner_v3_imu_delay_ticks", "winner_v3_native_quantization",
        "winner_v3_native_quantization_probability", "winner_v3_sensor_noise_scales",
        "winner_v3_deviation_scale",
    )
    allowed_model_leaves = {
        "geom_friction", "dof_frictionloss", "dof_armature", "body_mass",
        "body_ipos", "body_inertia", "body_iquat",
    }
    full_changed = set(scale_results["1.0"]["changed_model_leaves"])
    scale_zero_changed = set(scale_results["0.0"]["changed_model_leaves"])
    checks = {
        "preoutcome_contract_hashes_exact": preoutcome_exact or args.development,
        "preregistration_still_exact": sha256(PREREG) == "79ed8e765be72b035d94958c106758d170cb740379abab88d5582ddd7735a96b",
        "recurrent_cpu_contract_passed": recurrent.get("status") == "PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT",
        "cpu_only_jax": cpu_only,
        "default_off_trace_bit_exact": default_exact and default_error == 0.0,
        "scale_zero_model_tree_bit_exact": not scale_zero_changed,
        "full_randomizer_changes_only_allowed_model_fields": bool(full_changed) and full_changed <= allowed_model_leaves,
        "all_stage_model_bounds_pass": all(row["bounds_pass"] for row in scale_results.values()),
        "full_inertia_positive_triangle_and_bounds": inertia_pass,
        "all_stage_episode_bounds_pass": all(row["bounds_pass"] for row in episode_results.values()),
        "scale_zero_episode_is_exact_p30_nominal": (
            episode_results["0.0"]["action_delay_values"] == [0]
            and episode_results["0.0"]["imu_delay_values"] == [0]
            and episode_results["0.0"]["native_true_count"] == 0
        ),
        "full_delay_support_observed": (
            episode_results["1.0"]["action_delay_values"] == [0, 1, 2]
            and episode_results["1.0"]["imu_delay_values"] == [0, 1, 2]
        ),
        "native_quantizer_matches_independent_float32": max(quant_errors) <= 1e-7,
        "native_quantizer_untargeted_slices_bit_exact": all(unchanged),
        "home_relative_gain_tau_bridge_equation_exact": bridge_error <= 2e-7,
        "per_episode_readback_fields_complete": all(name in joystick_source for name in readback_names),
        "true_configuration_not_appended_to_actor_observation": "winner_v3_" not in state_block,
        "fixed_episode_action_and_imu_delays_are_consumed": (
            'state.info["winner_v3_additional_action_delay_ticks"]' in joystick_source
            and 'info["winner_v3_imu_delay_ticks"]' in joystick_source
        ),
        "formal_training_steps_zero": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_CONTRACT"
        if not failed
        else "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v3.variable_configuration_curriculum_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": input_hashes,
        "devices": devices,
        "baseline_composed_manifest_sha256": sha256(baseline / "WINNER_V3_COMPOSED_SOURCE_MANIFEST.json"),
        "winner_v3_composed_manifest_sha256": sha256(playground / "WINNER_V3_COMPOSED_SOURCE_MANIFEST.json"),
        "default_off_trace": {
            "baseline": baseline_trace_meta,
            "patched": patched_trace_meta,
            "bit_exact": default_exact,
            "max_abs_error": default_error,
            "per_field_max_abs_error": default_errors,
        },
        "model_randomizer": {
            "sample_count_per_stage": sample_count,
            "stages": scale_results,
            "full_inertia": {
                "minimum_eigenvalue": float(eigenvalues.min()),
                "minimum_triangle_margin": float(np.min(eigenvalues[:, 0] + eigenvalues[:, 1] - eigenvalues[:, 2])),
                "diagonal_min": np.min(diagonals, axis=0).tolist(),
                "diagonal_max": np.max(diagonals, axis=0).tolist(),
                "maximum_absolute_products": np.max(np.abs(products), axis=0).tolist(),
            },
        },
        "episode_randomizer": {
            "sample_count_per_stage": sample_count,
            "stages": episode_results,
        },
        "native_quantizer": {
            "vectors": len(quant_errors),
            "max_abs_error": max(quant_errors),
        },
        "bridge": {"max_abs_error_rad": bridge_error},
        "formal_training_steps_executed": 0,
        "formal_behavior_cells_executed": 0,
        "authority": {
            "single_cpu_curriculum_after_pass": not failed,
            "hosted_or_colab": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "runtime_or_gate5": False,
            "robot_clearance": False,
        },
    }
    output_json = work / "development_contract.json" if args.development else OUT_JSON
    output_md = work / "DEVELOPMENT_CONTRACT.md" if args.development else OUT_MD
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    output_md.write_text(f"""# Winner-v3 Variable-Configuration Curriculum Contract — 2026-07-19

Status: `{status}`

- JAX devices: `{devices}`
- model/episode samples per stage: `{sample_count}`
- default-off maximum trace error: `{default_error}`
- full-domain minimum inertia eigenvalue: `{float(eigenvalues.min())}` kg m^2
- full-domain minimum inertia triangle margin: `{float(np.min(eigenvalues[:, 0] + eigenvalues[:, 1] - eigenvalues[:, 2]))}` kg m^2
- native quantizer maximum independent error: `{max(quant_errors)}`
- fitted bridge equation maximum error: `{bridge_error}` rad
- formal training steps / behavior cells: `0 / 0`
- failed checks: `{failed}`

This is a pre-training implementation contract. A pass authorizes only the
single seed-100, no-retry CPU curriculum already frozen by the replacement
preregistration. It is not policy behavior evidence, a selected graph, a
supported-configuration envelope, runtime acceptance, Gate 5, deployment, or
robot clearance. No hosted allocation, GPU/iGPU, RDK-X5, robot, serial, torque,
or motion is authorized.
""")
    print(status)
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
