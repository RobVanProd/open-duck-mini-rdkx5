#!/usr/bin/env python3
"""Closed-loop Open Duck policy eval with optional actuator bridge.

Imports for JAX, MuJoCo, ONNX Runtime, and Open Duck Playground stay inside
runtime functions so normal tool compilation and help output do not require the
training environment.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from actuator_bridge_model import (
    ActuatorBridgeModel,
    JOINT_NAMES,
    PITCH_CHAIN_JOINTS,
    JointActuatorParams,
    params_from_fit,
    passthrough_params,
    stress_params,
)


REAL_X008_REFERENCE = {
    "pitch_chain_p95_tracking_error_rad": [0.12, 0.17],
    "effective_lag_ticks": [3, 4],
    "target_velocity_p95_rad_s": [3.09, 5.22],
    "action_saturation_pct": {
        "right_hip_pitch": 2.01,
        "right_ankle": 0.13,
    },
}


@dataclass
class ClosedLoopConfig:
    policy_path: Path
    fit: Mapping[str, Any]
    playground_root: Path
    command_x: float
    duration_s: float
    bridge_mode: str
    expected_observation_dim: int = 101
    expected_action_dim: int = 14
    task: str = "flat_terrain"
    seed: int = 0
    eval_role: str = "reproduction"


@contextlib.contextmanager
def temporary_cwd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def finite(value) -> bool:
    return value is not None and not (
        isinstance(value, float) and (math.isnan(value) or math.isinf(value))
    )


def percentile(values: Sequence[float], pct: float):
    values = sorted(float(value) for value in values if finite(value))
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - k) + values[hi] * (k - lo)


def signed_stats(values: Iterable[float]) -> dict | None:
    data = np.asarray([float(value) for value in values if finite(value)], dtype=float)
    if data.size == 0:
        return None
    return {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "p50": percentile(data, 50),
        "p95": percentile(data, 95),
        "p99": percentile(data, 99),
        "max": float(np.max(data)),
    }


def abs_stats(values: Iterable[float]) -> dict | None:
    data = np.asarray([abs(float(value)) for value in values if finite(value)], dtype=float)
    return signed_stats(data)


def vector_abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros_like(values)
    vel = np.abs(np.diff(values, axis=0) / max(float(dt_s), 1e-9))
    return np.vstack([np.zeros((1, values.shape[1])), vel])


def best_lag(target: np.ndarray, actual: np.ndarray, dt_s: float, max_lag_ticks: int = 12) -> dict:
    best = None
    for lag in range(-max_lag_ticks, max_lag_ticks + 1):
        pairs = []
        for index, target_value in enumerate(target):
            actual_index = index + lag
            if 0 <= actual_index < len(actual):
                pairs.append((target_value, actual[actual_index]))
        if len(pairs) < 20:
            continue
        rmse = math.sqrt(sum((left - right) ** 2 for left, right in pairs) / len(pairs))
        if best is None or rmse < best["rmse"]:
            best = {"ticks": lag, "rmse": rmse, "samples": len(pairs)}
    if best is None:
        return {"ticks": None, "ms": None, "rmse": None, "samples": 0}
    best["ms"] = best["ticks"] * float(dt_s) * 1000.0
    return best


def quat_wxyz_to_pitch(quat: Sequence[float]) -> float:
    w, x, y, z = [float(value) for value in quat]
    sin_pitch = 2.0 * (w * y - z * x)
    return math.asin(max(-1.0, min(1.0, sin_pitch)))


def policy_metadata(session, policy_path: Path) -> dict:
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    return {
        "path": str(policy_path),
        "input_name": inputs[0].name if inputs else None,
        "input_shape": inputs[0].shape if inputs else None,
        "input_type": inputs[0].type if inputs else None,
        "output_name": outputs[0].name if outputs else None,
        "output_shape": outputs[0].shape if outputs else None,
        "output_type": outputs[0].type if outputs else None,
    }


def mode_params(mode: str, fit: Mapping[str, Any]) -> list[JointActuatorParams]:
    if mode == "vanilla":
        return passthrough_params(len(JOINT_NAMES))
    if mode == "fitted":
        return params_from_fit(fit, JOINT_NAMES)
    if mode == "stress":
        return stress_params(JOINT_NAMES)
    raise ValueError(f"unsupported bridge mode {mode}")


def available_modes(requested: str) -> list[str]:
    if requested == "all":
        return ["vanilla", "fitted", "stress"]
    return [requested]


def per_joint_mode_summary(records: list[dict], dt_s: float) -> dict:
    if not records:
        return {}
    actions = np.asarray([record["action"] for record in records], dtype=float)
    sent = np.asarray([record["sent_target_rad"] for record in records], dtype=float)
    pre_rate = np.asarray([record["target_pre_rate_limit_rad"] for record in records], dtype=float)
    applied = np.asarray([record["applied_target_rad"] for record in records], dtype=float)
    actual = np.asarray([record["actual_position_rad"] for record in records], dtype=float)

    action_delta = np.vstack([np.zeros((1, actions.shape[1])), np.diff(actions, axis=0)])
    sent_velocity = vector_abs_velocity(sent, dt_s)
    applied_velocity = vector_abs_velocity(applied, dt_s)
    bridge_tracking = np.abs(sent - applied)
    joint_tracking = np.abs(sent - actual)
    rate_limit_delta = np.abs(pre_rate - sent)

    joints = {}
    for index, joint in enumerate(JOINT_NAMES):
        joints[joint] = {
            "action": signed_stats(actions[:, index]),
            "action_abs": abs_stats(actions[:, index]),
            "action_saturation_pct": float(np.mean(np.abs(actions[:, index]) >= 0.98) * 100.0),
            "action_delta_abs": abs_stats(action_delta[:, index]),
            "sent_target_velocity_rad_s": abs_stats(sent_velocity[:, index]),
            "applied_target_velocity_rad_s": abs_stats(applied_velocity[:, index]),
            "rate_limiter_activation_pct": float(np.mean(rate_limit_delta[:, index] > 1e-8) * 100.0),
            "bridge_tracking_error_rad": abs_stats(bridge_tracking[:, index]),
            "joint_target_tracking_error_rad": abs_stats(joint_tracking[:, index]),
            "estimated_lag_sent_to_applied": best_lag(sent[:, index], applied[:, index], dt_s),
            "estimated_lag_sent_to_actual": best_lag(sent[:, index], actual[:, index], dt_s),
        }
    return joints


def pitch_chain_summary(joints: Mapping[str, Mapping[str, Any]]) -> dict:
    output = {}
    bridge_p95 = []
    joint_p95 = []
    lag_ticks = []
    velocity_p95 = []
    saturation = []
    for joint in PITCH_CHAIN_JOINTS:
        item = joints.get(joint, {})
        bridge = (item.get("bridge_tracking_error_rad") or {}).get("p95")
        tracking = (item.get("joint_target_tracking_error_rad") or {}).get("p95")
        lag = (item.get("estimated_lag_sent_to_applied") or {}).get("ticks")
        velocity = (item.get("sent_target_velocity_rad_s") or {}).get("p95")
        sat = item.get("action_saturation_pct")
        if finite(bridge):
            bridge_p95.append(float(bridge))
        if finite(tracking):
            joint_p95.append(float(tracking))
        if finite(lag):
            lag_ticks.append(float(lag))
        if finite(velocity):
            velocity_p95.append(float(velocity))
        if finite(sat):
            saturation.append(float(sat))
    output["bridge_tracking_p95_rad"] = signed_stats(bridge_p95)
    output["joint_target_tracking_p95_rad"] = signed_stats(joint_p95)
    output["estimated_lag_ticks"] = signed_stats(lag_ticks)
    output["sent_target_velocity_p95_rad_s"] = signed_stats(velocity_p95)
    output["action_saturation_pct"] = signed_stats(saturation)
    return output


def classify_closed_loop(modes: Mapping[str, Mapping[str, Any]]) -> str:
    fitted = modes.get("fitted")
    if not fitted:
        return "HOLD_SIM_RUNTIME_ERROR"
    summary = fitted.get("pitch_chain_summary", {})
    bridge_p95 = (summary.get("bridge_tracking_p95_rad") or {}).get("p50")
    lag = (summary.get("estimated_lag_ticks") or {}).get("p50")
    velocity = (summary.get("sent_target_velocity_p95_rad_s") or {}).get("p50")
    if not all(finite(value) for value in [bridge_p95, lag, velocity]):
        return "HOLD_MODEL_DOES_NOT_REPRODUCE"

    real_tracking_lo, real_tracking_hi = REAL_X008_REFERENCE["pitch_chain_p95_tracking_error_rad"]
    real_lag_lo, real_lag_hi = REAL_X008_REFERENCE["effective_lag_ticks"]
    real_vel_lo, real_vel_hi = REAL_X008_REFERENCE["target_velocity_p95_rad_s"]
    tracking_ok = real_tracking_lo * 0.5 <= bridge_p95 <= real_tracking_hi * 1.75
    lag_ok = real_lag_lo - 2 <= abs(lag) <= real_lag_hi + 4
    velocity_ok = real_vel_lo * 0.4 <= velocity <= real_vel_hi * 1.8
    if tracking_ok and lag_ok and velocity_ok:
        return "PASS_CLOSED_LOOP_REPRODUCTION"
    return "HOLD_MODEL_DOES_NOT_REPRODUCE"


def max_finite(values: Iterable[float]) -> float | None:
    data = [float(value) for value in values if finite(value)]
    return max(data) if data else None


def classify_candidate_gate(modes: Mapping[str, Mapping[str, Any]]) -> dict:
    """Classify a candidate policy directly instead of asking it to reproduce failure."""
    thresholds = {
        "max_action_saturation_pct": 1.0,
        "max_pitch_tracking_p95_rad": 0.08,
        "max_sent_target_velocity_p95_rad_s": 2.5,
        "max_abs_body_pitch_p95_rad": 0.25,
        "min_base_height_m": 0.12,
        "min_reward_mean": 0.30,
        "min_forward_command_tracking_ratio": 0.25,
    }
    if not modes:
        return {"status": "HOLD_CANDIDATE_NO_EVAL", "thresholds": thresholds}

    terminations = {
        name: mode.get("termination_reason") for name, mode in modes.items()
    }
    incomplete = {
        name: reason
        for name, reason in terminations.items()
        if reason != "duration_complete"
    }

    pitch_tracking = []
    sent_velocity = []
    action_saturation = []
    body_pitch_abs = []
    base_height_min = []
    reward_mean = []
    command_x_values = []
    forward_ratios = []
    forward_velocity_errors = []
    for mode in modes.values():
        body = mode.get("body_pitch_rad") or {}
        height = mode.get("base_height_m") or {}
        reward = mode.get("reward") or {}
        forward = mode.get("forward_motion") or {}
        command = mode.get("command") or []
        command_x = command[0] if command else forward.get("command_x_m_s")
        if finite(command_x):
            command_x_values.append(float(command_x))
        if finite(body.get("p95")):
            body_pitch_abs.append(abs(float(body["p95"])))
        if finite(height.get("min")):
            base_height_min.append(float(height["min"]))
        if finite(reward.get("mean")):
            reward_mean.append(float(reward["mean"]))
        if finite(forward.get("command_tracking_ratio")):
            forward_ratios.append(float(forward["command_tracking_ratio"]))
        if finite(forward.get("velocity_error_m_s")):
            forward_velocity_errors.append(abs(float(forward["velocity_error_m_s"])))
        for joint in PITCH_CHAIN_JOINTS:
            item = (mode.get("joints") or {}).get(joint, {})
            tracking = (item.get("joint_target_tracking_error_rad") or {}).get("p95")
            velocity = (item.get("sent_target_velocity_rad_s") or {}).get("p95")
            saturation = item.get("action_saturation_pct")
            if finite(tracking):
                pitch_tracking.append(float(tracking))
            if finite(velocity):
                sent_velocity.append(float(velocity))
            if finite(saturation):
                action_saturation.append(float(saturation))

    metrics = {
        "max_action_saturation_pct": max_finite(action_saturation),
        "max_pitch_tracking_p95_rad": max_finite(pitch_tracking),
        "max_sent_target_velocity_p95_rad_s": max_finite(sent_velocity),
        "max_abs_body_pitch_p95_rad": max_finite(body_pitch_abs),
        "min_base_height_m": min(base_height_min) if base_height_min else None,
        "min_reward_mean": min(reward_mean) if reward_mean else None,
        "min_forward_command_tracking_ratio": (
            min(forward_ratios) if forward_ratios else None
        ),
        "max_abs_forward_velocity_error_m_s": max_finite(forward_velocity_errors),
        "terminations": terminations,
    }
    command_x = command_x_values[0] if command_x_values else 0.0
    requires_forward_tracking = abs(command_x) >= 0.02
    if incomplete:
        status = "HOLD_CANDIDATE_FALL_OR_TERMINATION"
    elif not finite(metrics["max_action_saturation_pct"]):
        status = "HOLD_CANDIDATE_NO_METRICS"
    elif requires_forward_tracking and not finite(
        metrics["min_forward_command_tracking_ratio"]
    ):
        status = "HOLD_CANDIDATE_NO_FORWARD_TRACKING"
    elif (
        requires_forward_tracking
        and metrics["min_forward_command_tracking_ratio"]
        < thresholds["min_forward_command_tracking_ratio"]
    ):
        status = "HOLD_CANDIDATE_LOW_FORWARD_PROGRESS"
    elif metrics["max_action_saturation_pct"] > thresholds["max_action_saturation_pct"]:
        status = "HOLD_CANDIDATE_ACTION_SATURATION"
    elif metrics["max_pitch_tracking_p95_rad"] > thresholds["max_pitch_tracking_p95_rad"]:
        status = "HOLD_CANDIDATE_TRACKING"
    elif (
        metrics["max_sent_target_velocity_p95_rad_s"]
        > thresholds["max_sent_target_velocity_p95_rad_s"]
    ):
        status = "HOLD_CANDIDATE_TARGET_VELOCITY"
    elif metrics["max_abs_body_pitch_p95_rad"] > thresholds["max_abs_body_pitch_p95_rad"]:
        status = "HOLD_CANDIDATE_POSTURE"
    elif metrics["min_base_height_m"] < thresholds["min_base_height_m"]:
        status = "HOLD_CANDIDATE_BASE_HEIGHT"
    elif metrics["min_reward_mean"] < thresholds["min_reward_mean"]:
        status = "HOLD_CANDIDATE_LOW_REWARD"
    else:
        status = "PASS_CANDIDATE_SIM_GATE"
    return {"status": status, "thresholds": thresholds, "metrics": metrics}


def run_closed_loop_sim(config: ClosedLoopConfig) -> dict:
    if config.bridge_mode not in {"vanilla", "fitted", "stress", "all"}:
        return {
            "status": "HOLD_SIM_RUNTIME_ERROR",
            "error": f"unsupported bridge mode {config.bridge_mode}",
        }
    if not config.playground_root.exists():
        return {
            "status": "HOLD_ENV_NOT_READY",
            "error": f"playground path missing: {config.playground_root}",
        }
    if not config.policy_path.exists():
        return {
            "status": "HOLD_SIM_RUNTIME_ERROR",
            "error": f"policy missing: {config.policy_path}",
        }

    try:
        import jax
        import jax.numpy as jp
        import onnxruntime as ort
        from mujoco_playground._src import mjx_env
        from mujoco_playground._src.collision import geoms_colliding
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "status": "HOLD_ENV_NOT_READY",
            "error": f"{type(exc).__name__}: {exc}",
        }

    sys.path.insert(0, str(config.playground_root))
    try:
        from playground.open_duck_mini_v2 import joystick
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "status": "HOLD_ENV_NOT_READY",
            "error": f"{type(exc).__name__}: {exc}",
        }

    command = jp.asarray([config.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    overrides = {
        "push_config.enable": False,
        "lin_vel_x": [config.command_x, config.command_x],
        "lin_vel_y": [0.0, 0.0],
        "ang_vel_yaw": [0.0, 0.0],
        "neck_pitch_range": [0.0, 0.0],
        "head_pitch_range": [0.0, 0.0],
        "head_yaw_range": [0.0, 0.0],
        "head_roll_range": [0.0, 0.0],
        "noise_config.level": 0.0,
        "noise_config.action_min_delay": 0,
        "noise_config.action_max_delay": 1,
        "noise_config.imu_min_delay": 0,
        "noise_config.imu_max_delay": 1,
    }

    try:
        with temporary_cwd(config.playground_root):
            env = joystick.Joystick(task=config.task, config_overrides=overrides)
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "status": "HOLD_SIM_RUNTIME_ERROR",
            "error": f"env init failed: {type(exc).__name__}: {exc}",
        }

    try:
        session = ort.InferenceSession(str(config.policy_path), providers=["CPUExecutionProvider"])
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "status": "HOLD_ENV_NOT_READY",
            "error": f"ONNX Runtime session failed: {type(exc).__name__}: {exc}",
        }
    policy = policy_metadata(session, config.policy_path)
    input_name = policy["input_name"]
    output_name = policy["output_name"]
    if not input_name or not output_name:
        return {"status": "HOLD_SIM_RUNTIME_ERROR", "error": "policy IO metadata missing"}

    if int(env.action_size) != config.expected_action_dim:
        return {
            "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
            "error": f"env action_size {env.action_size} != {config.expected_action_dim}",
        }
    if list(env.observation_size.get("state", ())) != [config.expected_observation_dim]:
        return {
            "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
            "error": f"env state obs {env.observation_size.get('state')} != {config.expected_observation_dim}",
        }
    if list(env.actuator_names) != JOINT_NAMES:
        return {
            "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
            "error": "env actuator order does not match policy/runtime order",
            "env_actuator_names": list(env.actuator_names),
            "expected": JOINT_NAMES,
        }

    def refresh_obs(state):
        state.info["command"] = command
        contact = jp.array(
            [
                geoms_colliding(state.data, geom_id, env._floor_geom_id)
                for geom_id in env._feet_geom_id
            ]
        )
        obs = env._get_obs(state.data, state.info, contact)
        return state.replace(obs=obs)

    def prepare_step(state, action):
        state.info["command"] = command
        if joystick.USE_IMITATION_REWARD:
            state.info["imitation_i"] += 1
            state.info["imitation_i"] = state.info["imitation_i"] % env.PRM.nb_steps_in_period
            state.info["imitation_phase"] = jp.array(
                [
                    jp.cos(
                        (state.info["imitation_i"] / env.PRM.nb_steps_in_period)
                        * 2
                        * jp.pi
                    ),
                    jp.sin(
                        (state.info["imitation_i"] / env.PRM.nb_steps_in_period)
                        * 2
                        * jp.pi
                    ),
                ]
            )
            state.info["current_reference_motion"] = env.PRM.get_reference_motion(
                command[0], command[1], command[2], state.info["imitation_i"]
            )
        else:
            state.info["imitation_i"] = 0
            state.info["current_reference_motion"] = jp.zeros(0)

        state.info["rng"], action_delay_rng = jax.random.split(state.info["rng"])
        action_history = (
            jp.roll(state.info["action_history"], env._actuators)
            .at[: env._actuators]
            .set(action)
        )
        state.info["action_history"] = action_history
        action_idx = jax.random.randint(
            action_delay_rng,
            (1,),
            minval=env._config.noise_config.action_min_delay,
            maxval=env._config.noise_config.action_max_delay,
        )
        action_w_delay = action_history.reshape((-1, env._actuators))[action_idx[0]]
        pre_rate_limit = env._default_actuator + action_w_delay * env._config.action_scale
        if joystick.USE_MOTOR_SPEED_LIMITS:
            prev_motor_targets = state.info["motor_targets"]
            sent_target = jp.clip(
                pre_rate_limit,
                prev_motor_targets - env._config.max_motor_velocity * env.dt,
                prev_motor_targets + env._config.max_motor_velocity * env.dt,
            )
        else:
            sent_target = pre_rate_limit
        return state, action_w_delay, pre_rate_limit, sent_target

    def apply_motor_target(state, action, sent_target, applied_target):
        data = mjx_env.step(env.mjx_model, state.data, applied_target, env.n_substeps)
        state.info["motor_targets"] = sent_target
        contact = jp.array(
            [
                geoms_colliding(data, geom_id, env._floor_geom_id)
                for geom_id in env._feet_geom_id
            ]
        )
        contact_filt = contact | state.info["last_contact"]
        first_contact = (state.info["feet_air_time"] > 0.0) * contact_filt
        state.info["feet_air_time"] += env.dt
        p_f = data.site_xpos[env._feet_site_id]
        p_fz = p_f[..., -1]
        state.info["swing_peak"] = jp.maximum(state.info["swing_peak"], p_fz)
        obs = env._get_obs(data, state.info, contact)
        done = env._get_termination(data)
        rewards = env._get_reward(
            data, action, state.info, state.metrics, done, first_contact, contact
        )
        rewards = {
            key: value * env._config.reward_config.scales[key]
            for key, value in rewards.items()
        }
        reward = jp.clip(sum(rewards.values()) * env.dt, 0.0, 10000.0)
        state.info["push"] = jp.array([0.0, 0.0])
        state.info["step"] += 1
        state.info["push_step"] += 1
        state.info["last_last_last_act"] = state.info["last_last_act"]
        state.info["last_last_act"] = state.info["last_act"]
        state.info["last_act"] = action
        state.info["command"] = command
        state.info["feet_air_time"] *= ~contact
        state.info["last_contact"] = contact
        state.info["swing_peak"] *= ~contact
        for key, value in rewards.items():
            scale = env._config.reward_config.scales[key]
            if scale != 0:
                if scale > 0:
                    state.metrics[f"reward/{key}"] = value
                else:
                    state.metrics[f"cost/{key}"] = -value
        state.metrics["swing_peak"] = jp.mean(state.info["swing_peak"])
        done = done.astype(reward.dtype)
        return state.replace(data=data, obs=obs, reward=reward, done=done)

    refresh_obs_jit = jax.jit(refresh_obs)
    prepare_step_jit = jax.jit(prepare_step)
    apply_motor_target_jit = jax.jit(apply_motor_target)

    modes = {}
    sim_steps = max(1, int(round(config.duration_s / float(env.dt))))
    insertion_point = {
        "type": "target_stage_direct",
        "description": (
            "The runner mirrors Joystick.step through action delay, "
            "target = home + delayed_action * action_scale, and the built-in "
            "max_motor_velocity rate limit. The actuator bridge is inserted "
            "after that rate limit and before mjx_env.step. state.info['motor_targets'] "
            "keeps the sent target so obs[83:97] remains commanded target history."
        ),
        "double_rate_limit": False,
        "push_disabled": True,
        "noise_disabled": True,
        "action_delay_disabled": True,
        "command_pinned": [config.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    }

    for mode in available_modes(config.bridge_mode):
        start = time.monotonic()
        records: list[dict] = []
        params = mode_params(mode, config.fit)
        state = env.reset(jax.random.PRNGKey(config.seed))
        state.info["command"] = command
        state = refresh_obs_jit(state)
        initial_target = np.asarray(jax.device_get(state.info["motor_targets"]), dtype=float)
        bridge = ActuatorBridgeModel(params, initial_target=initial_target)
        termination_reason = None

        for tick in range(sim_steps):
            obs = np.asarray(jax.device_get(state.obs["state"]), dtype=np.float32)
            if obs.shape != (config.expected_observation_dim,):
                return {
                    "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
                    "error": f"obs shape {obs.shape} != {(config.expected_observation_dim,)}",
                }
            action = session.run([output_name], {input_name: obs[None, :]})[0][0]
            action = np.asarray(action, dtype=np.float32)
            if action.shape != (config.expected_action_dim,):
                return {
                    "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
                    "error": f"action shape {action.shape} != {(config.expected_action_dim,)}",
                }
            state, action_w_delay, pre_rate, sent_target = prepare_step_jit(
                state, jp.asarray(action)
            )
            pre_np = np.asarray(jax.device_get(pre_rate), dtype=float)
            sent_np = np.asarray(jax.device_get(sent_target), dtype=float)
            applied_np = (
                sent_np.copy()
                if mode == "vanilla"
                else bridge.step(sent_np, float(env.dt))
            )
            state = apply_motor_target_jit(
                state,
                jp.asarray(action),
                sent_target,
                jp.asarray(applied_np),
            )
            actual = np.asarray(
                jax.device_get(env.get_actuator_joints_qpos(state.data.qpos)),
                dtype=float,
            )
            qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
            base_addr = int(env._floating_base_qpos_addr)
            quat = qpos[base_addr + 3 : base_addr + 7]
            contacts = np.asarray(jax.device_get(state.info["last_contact"]), dtype=bool)
            done = bool(np.asarray(jax.device_get(state.done)))
            reward = float(np.asarray(jax.device_get(state.reward)))
            records.append(
                {
                    "tick": tick,
                    "time_s": tick * float(env.dt),
                    "obs0_6": obs[:6].astype(float).tolist(),
                    "command": [config.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "action": action.astype(float).tolist(),
                    "action_w_delay": np.asarray(
                        jax.device_get(action_w_delay), dtype=float
                    ).tolist(),
                    "target_pre_rate_limit_rad": pre_np.tolist(),
                    "sent_target_rad": sent_np.tolist(),
                    "applied_target_rad": applied_np.tolist(),
                    "actual_position_rad": actual.tolist(),
                    "body_pitch_rad": quat_wxyz_to_pitch(quat),
                    "base_x_m": float(qpos[base_addr]),
                    "base_y_m": float(qpos[base_addr + 1]),
                    "base_height_m": float(qpos[base_addr + 2]),
                    "foot_contacts": contacts.astype(int).tolist(),
                    "reward": reward,
                    "done": done,
                }
            )
            if done:
                termination_reason = "fall_or_nan"
                break

        wall_clock = time.monotonic() - start
        joints = per_joint_mode_summary(records, float(env.dt))
        body_pitch = signed_stats([record["body_pitch_rad"] for record in records])
        base_x = signed_stats([record["base_x_m"] for record in records])
        base_y = signed_stats([record["base_y_m"] for record in records])
        base_height = signed_stats([record["base_height_m"] for record in records])
        reward_stats = signed_stats([record["reward"] for record in records])
        if len(records) >= 2:
            elapsed_s = max(
                float(records[-1]["time_s"]) - float(records[0]["time_s"]),
                float(env.dt),
            )
            progress_x = float(records[-1]["base_x_m"]) - float(records[0]["base_x_m"])
            progress_y = float(records[-1]["base_y_m"]) - float(records[0]["base_y_m"])
            mean_vx = progress_x / elapsed_s
            ratio = (
                mean_vx / float(config.command_x)
                if abs(float(config.command_x)) >= 1e-9
                else None
            )
            velocity_error = mean_vx - float(config.command_x)
        else:
            elapsed_s = 0.0
            progress_x = None
            progress_y = None
            mean_vx = None
            ratio = None
            velocity_error = None
        contact_counts = (
            np.sum(np.asarray([record["foot_contacts"] for record in records]), axis=0).tolist()
            if records
            else [0, 0]
        )
        modes[mode] = {
            "status": "PASS_MODE_EVALUATED" if records else "HOLD_NO_SAMPLES",
            "samples": len(records),
            "requested_steps": sim_steps,
            "termination_reason": termination_reason or "duration_complete",
            "wall_clock_s": wall_clock,
            "command": [config.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "body_pitch_rad": body_pitch,
            "base_x_m": base_x,
            "base_y_m": base_y,
            "base_height_m": base_height,
            "forward_motion": {
                "elapsed_s": elapsed_s,
                "progress_x_m": progress_x,
                "progress_y_m": progress_y,
                "mean_velocity_x_m_s": mean_vx,
                "command_x_m_s": float(config.command_x),
                "velocity_error_m_s": velocity_error,
                "command_tracking_ratio": ratio,
            },
            "reward": reward_stats,
            "foot_contact_counts": {
                "left": int(contact_counts[0]) if len(contact_counts) > 0 else 0,
                "right": int(contact_counts[1]) if len(contact_counts) > 1 else 0,
            },
            "joints": joints,
            "pitch_chain_summary": pitch_chain_summary(joints),
        }

    candidate_gate = None
    if config.eval_role == "candidate":
        candidate_gate = classify_candidate_gate(modes)
        status = candidate_gate["status"]
    else:
        status = classify_closed_loop(modes) if "fitted" in modes else "PASS_CLOSED_LOOP_REPRODUCTION"
    return {
        "status": status,
        "eval_role": config.eval_role,
        "candidate_gate": candidate_gate,
        "policy": policy,
        "env": {
            "playground_root": str(config.playground_root),
            "env_class": "playground.open_duck_mini_v2.joystick.Joystick",
            "task": config.task,
            "action_size": int(env.action_size),
            "observation_size": {
                key: list(value) for key, value in env.observation_size.items()
            },
            "actuator_names": list(env.actuator_names),
            "mjcf": {
                "nu": int(env.mj_model.nu),
                "nq": int(env.mj_model.nq),
                "nv": int(env.mj_model.nv),
                "home_ctrl_len": int(len(env.mj_model.keyframe("home").ctrl)),
            },
            "ctrl_dt": float(env.dt),
            "sim_dt": float(env.sim_dt),
            "n_substeps": int(env.n_substeps),
            "action_scale": float(env._config.action_scale),
            "max_motor_velocity": float(env._config.max_motor_velocity),
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "insertion_point": insertion_point,
        "real_x008_reference": REAL_X008_REFERENCE,
        "modes": modes,
    }
