#!/usr/bin/env python3
"""Closed-loop Open Duck policy eval with optional actuator bridge.

Imports for JAX, MuJoCo, ONNX Runtime, and Open Duck Playground stay inside
runtime functions so normal tool compilation and help output do not require the
training environment.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
import json
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
    command_y: float = 0.0
    command_yaw: float = 0.0
    expected_observation_dim: int = 101
    expected_action_dim: int = 14
    task: str = "flat_terrain"
    seed: int = 0
    eval_role: str = "reproduction"
    mjx_step_loop_mode: str = "default"
    policy_action_gain: float = 1.0
    max_motor_velocity_override_rad_s: float | None = None
    forward_diagnostic_required_ratio: float = 0.5
    forward_diagnostic_deadband: float = 0.02
    reward_overrides: Mapping[str, Any] | None = None
    trace_jsonl: Path | None = None
    trace_full_obs: bool = False
    policy_obs_input_name: str | None = None
    policy_action_output_name: str | None = None
    policy_state_input_names: tuple[str, ...] = ()
    policy_state_output_names: tuple[str, ...] = ()
    eval_push_enable: bool = False
    eval_push_interval_min_s: float | None = None
    eval_push_interval_max_s: float | None = None
    eval_push_magnitude_min: float | None = None
    eval_push_magnitude_max: float | None = None
    push_recovery_window_s: float = 0.5
    push_recovery_max_abs_pitch_rad: float = 0.8
    push_recovery_min_base_height_m: float = 0.08


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


def push_recovery_summary(
    records: Sequence[Mapping[str, Any]],
    dt_s: float,
    recovery_window_s: float,
    max_abs_pitch_rad: float,
    min_base_height_m: float,
) -> dict:
    push_indices = [
        index
        for index, record in enumerate(records)
        if float(record.get("push_magnitude", 0.0) or 0.0) > 1e-9
    ]
    window_steps = max(1, int(round(float(recovery_window_s) / max(float(dt_s), 1e-9))))
    results = []
    for index in push_indices:
        window = records[index : min(len(records), index + window_steps + 1)]
        if not window:
            continue
        terminated = any(bool(record.get("done")) for record in window)
        max_abs_pitch = max(
            abs(float(record.get("body_pitch_rad", 0.0) or 0.0)) for record in window
        )
        min_height = min(
            float(record.get("base_height_m", 0.0) or 0.0) for record in window
        )
        fully_observed = len(window) >= window_steps + 1
        recovered = (
            not terminated
            and max_abs_pitch <= float(max_abs_pitch_rad)
            and min_height >= float(min_base_height_m)
            and fully_observed
        )
        results.append(
            {
                "tick": int(records[index].get("tick", index)),
                "time_s": float(records[index].get("time_s", index * dt_s)),
                "push": list(records[index].get("push", [])),
                "push_magnitude": float(records[index].get("push_magnitude", 0.0)),
                "window_samples": len(window),
                "full_recovery_window_observed": bool(fully_observed),
                "terminated_in_window": bool(terminated),
                "max_abs_pitch_rad": float(max_abs_pitch),
                "min_base_height_m": float(min_height),
                "recovered": bool(recovered),
            }
        )
    recovered_count = sum(1 for item in results if item["recovered"])
    push_magnitudes = [item["push_magnitude"] for item in results]
    return {
        "enabled": bool(push_indices),
        "event_count": len(results),
        "recovered_count": int(recovered_count),
        "success_rate": (
            float(recovered_count / len(results)) if results else None
        ),
        "window_s": float(recovery_window_s),
        "max_abs_pitch_rad_threshold": float(max_abs_pitch_rad),
        "min_base_height_m_threshold": float(min_base_height_m),
        "push_magnitude": signed_stats(push_magnitudes),
        "events": results,
    }


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


def quat_wxyz_to_roll(quat: Sequence[float]) -> float:
    w, x, y, z = [float(value) for value in quat]
    return math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))


def quat_wxyz_to_yaw(quat: Sequence[float]) -> float:
    w, x, y, z = [float(value) for value in quat]
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


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
        "inputs": [
            {"name": item.name, "shape": item.shape, "type": item.type}
            for item in inputs
        ],
        "outputs": [
            {"name": item.name, "shape": item.shape, "type": item.type}
            for item in outputs
        ],
    }


def _node_by_name(nodes: Sequence[Any], name: str):
    for node in nodes:
        if node.name == name:
            return node
    raise ValueError(f"ONNX IO name not found: {name}")


def _shape_to_zeros(shape: Sequence[Any]) -> np.ndarray:
    dims: list[int] = []
    for index, dim in enumerate(shape):
        if isinstance(dim, int) and dim > 0:
            dims.append(dim)
        elif index == 0:
            dims.append(1)
        else:
            raise ValueError(f"dynamic or unknown non-batch hidden dimension: {shape}")
    return np.zeros(tuple(dims), dtype=np.float32)


def init_policy_io_state(session, config: ClosedLoopConfig) -> dict:
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    input_names = [item.name for item in inputs]
    output_names = [item.name for item in outputs]
    obs_input_name = config.policy_obs_input_name or (input_names[0] if input_names else None)
    action_output_name = config.policy_action_output_name or (
        output_names[0] if output_names else None
    )
    if not obs_input_name or not action_output_name:
        raise ValueError("policy IO metadata missing")
    if obs_input_name not in input_names:
        raise ValueError(f"obs input {obs_input_name!r} not in ONNX inputs {input_names}")
    if action_output_name not in output_names:
        raise ValueError(
            f"action output {action_output_name!r} not in ONNX outputs {output_names}"
        )
    if bool(config.policy_state_input_names) != bool(config.policy_state_output_names):
        raise ValueError("state input and output names must both be set or both be empty")
    if len(config.policy_state_input_names) != len(config.policy_state_output_names):
        raise ValueError("state input/output name counts differ")

    hidden_state: dict[str, np.ndarray] = {}
    hidden_shapes: dict[str, list[Any]] = {}
    for name in config.policy_state_input_names:
        node = _node_by_name(inputs, name)
        hidden_state[name] = _shape_to_zeros(node.shape)
        hidden_shapes[name] = list(node.shape)
    for name in config.policy_state_output_names:
        _node_by_name(outputs, name)

    return {
        "obs_input_name": obs_input_name,
        "action_output_name": action_output_name,
        "state_input_names": list(config.policy_state_input_names),
        "state_output_names": list(config.policy_state_output_names),
        "state_input_shapes": hidden_shapes,
        "hidden_state": hidden_state,
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


REWARD_SCALE_OVERRIDES = {
    "tracking_lin_vel_scale": "tracking_lin_vel",
    "tracking_ang_vel_scale": "tracking_ang_vel",
    "target_rate_scale": "target_rate",
    "actuator_tracking_scale": "actuator_tracking",
    "forward_progress_scale": "forward_progress",
    "forward_shortfall_scale": "forward_shortfall",
    "forward_overshoot_scale": "forward_overshoot",
    "forward_wrong_direction_scale": "forward_wrong_direction",
    "command_progress_scale": "command_progress",
    "command_progress_shortfall_scale": "command_progress_shortfall",
    "command_progress_failure_scale": "command_progress_failure",
    "action_rate_scale": "action_rate",
    "action_magnitude_scale": "action_magnitude",
    "stand_still_scale": "stand_still",
    "orientation_scale": "orientation",
    "base_height_scale": "base_height",
    "forward_pitch_scale": "forward_pitch",
    "forward_pitch_rate_scale": "forward_pitch_rate",
    "forward_contact_support_scale": "forward_contact_support",
    "forward_single_support_scale": "forward_single_support",
    "forward_double_support_scale": "forward_double_support",
    "forward_contact_transition_scale": "forward_contact_transition",
    "forward_double_support_dwell_scale": "forward_double_support_dwell",
    "alive_scale": "alive",
    "imitation_scale": "imitation",
}


REWARD_CONFIG_OVERRIDES = {
    "tracking_sigma",
    "forward_progress_deadband",
    "forward_shortfall_required_ratio",
    "forward_overshoot_allowed_ratio",
    "forward_wrong_direction_allowed_reverse_ratio",
    "command_progress_required_ratio",
    "command_progress_warmup_steps",
    "command_progress_failure_enable",
    "command_progress_failure_min_ratio",
    "command_progress_failure_warmup_steps",
    "reward_clip_min",
    "reward_clip_max",
    "forward_contact_support_no_contact_weight",
    "forward_contact_support_asymmetry_weight",
    "forward_contact_transition_min_progress_ratio",
    "forward_double_support_dwell_grace_steps",
    "action_rate_huber_delta",
    "action_magnitude_huber_delta",
    "target_rate_huber_delta",
    "actuator_tracking_huber_delta",
    "forward_shortfall_huber_delta",
    "forward_overshoot_huber_delta",
    "forward_wrong_direction_huber_delta",
    "forward_pitch_huber_delta",
    "forward_pitch_rate_huber_delta",
    "command_progress_shortfall_huber_delta",
}


def apply_reward_overrides(env_config, overrides: Mapping[str, Any] | None) -> dict:
    """Apply training reward overrides to an eval env config.

    The closed-loop eval inserts the actuator bridge manually, so normal
    Playground runner CLI overrides are not available here. This function accepts
    the same snake_case keys emitted by staged-curriculum phase JSON payloads.
    """

    applied: dict[str, Any] = {}
    if not overrides:
        return applied
    reward_config = env_config.reward_config
    for override_key, scale_key in REWARD_SCALE_OVERRIDES.items():
        value = overrides.get(override_key)
        if value is None:
            continue
        reward_config.scales[scale_key] = value
        applied[override_key] = value
    for key in REWARD_CONFIG_OVERRIDES:
        value = overrides.get(key)
        if value is None:
            continue
        reward_config[key] = value
        applied[key] = value
    return applied


def block_tree(jax_module, value):
    """Materialize a JAX pytree without importing JAX at module import time."""
    return jax_module.tree_util.tree_map(
        lambda leaf: leaf.block_until_ready()
        if hasattr(leaf, "block_until_ready")
        else leaf,
        value,
    )


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


def reward_term_summary(records: list[dict]) -> dict:
    keys = sorted(
        {
            key
            for record in records
            for key in (record.get("reward_terms") or {}).keys()
        }
    )
    return {
        key: signed_stats(
            [
                (record.get("reward_terms") or {}).get(key)
                for record in records
                if finite((record.get("reward_terms") or {}).get(key))
            ]
        )
        for key in keys
    }


def append_trace_records(path: Path, mode: str, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        for record in records:
            payload = {"mode": mode, **record}
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def forward_shortfall_diagnostic(
    local_vx_values: Sequence[float],
    command_x: float,
    *,
    required_ratio: float,
    deadband: float,
) -> dict:
    """Compute a reward-config-independent forward progress diagnostic.

    Candidate gates may instantiate the Playground with default reward scales,
    so reward-term summaries do not necessarily include a training-time
    `cost/forward_shortfall` metric. This diagnostic keeps the standstill
    failure visible using only the commanded x velocity and measured local
    forward velocity.
    """
    if not finite(command_x):
        return {
            "status": "MISSING_COMMAND",
            "required_ratio": required_ratio,
            "deadband": deadband,
        }
    command_x = float(command_x)
    required_ratio = float(required_ratio)
    deadband = float(deadband)
    values = [float(value) for value in local_vx_values if finite(value)]
    needs_progress = abs(command_x) > deadband
    if not needs_progress:
        return {
            "status": "NO_FORWARD_COMMAND",
            "required_ratio": required_ratio,
            "deadband": deadband,
            "command_x_m_s": command_x,
        }
    if not values:
        return {
            "status": "MISSING_VELOCITY",
            "required_ratio": required_ratio,
            "deadband": deadband,
            "command_x_m_s": command_x,
        }

    target_speed = max(abs(command_x), 1.0e-9)
    sign = 1.0 if command_x >= 0.0 else -1.0
    signed = np.asarray(values, dtype=float) * sign
    progress_ratio = signed / target_speed
    clipped_progress_ratio = np.clip(progress_ratio, 0.0, 1.0)
    required_speed = target_speed * required_ratio
    shortfall_m_s = np.clip(required_speed - signed, 0.0, None)
    normalized_shortfall = shortfall_m_s / target_speed
    shortfall_cost = np.square(normalized_shortfall)
    return {
        "status": "PASS_DIAGNOSTIC",
        "required_ratio": required_ratio,
        "deadband": deadband,
        "command_x_m_s": command_x,
        "required_speed_m_s": required_speed,
        "progress_ratio": signed_stats(progress_ratio),
        "clipped_progress_ratio": signed_stats(clipped_progress_ratio),
        "shortfall_m_s": signed_stats(shortfall_m_s),
        "normalized_shortfall": signed_stats(normalized_shortfall),
        "shortfall_cost": signed_stats(shortfall_cost),
    }


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


def pitch_chain_velocity_limits_from_fit(fit: Mapping[str, Any]) -> dict[str, float]:
    """Return corrected fitted velocity limits for pitch-chain gate checks."""

    root = fit.get("primary", fit)
    joints = root.get("joints", {}) if isinstance(root, Mapping) else {}
    limits: dict[str, float] = {}
    for joint in PITCH_CHAIN_JOINTS:
        combined = (joints.get(joint) or {}).get("combined") or {}
        value = combined.get("velocity_limit_rad_s")
        if finite(value):
            limits[joint] = float(value)
    return limits


def classify_candidate_gate(
    modes: Mapping[str, Mapping[str, Any]],
    fit: Mapping[str, Any] | None = None,
) -> dict:
    """Classify a candidate policy directly instead of asking it to reproduce failure."""
    velocity_limits = pitch_chain_velocity_limits_from_fit(fit or {})
    thresholds = {
        "max_action_saturation_pct": 1.0,
        "max_pitch_tracking_p95_rad": 0.20,
        "max_sent_target_velocity_limit_excess_rad_s": 0.0,
        "pitch_chain_velocity_limits_rad_s": velocity_limits,
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
    forward_shortfall_cost_means = []
    per_joint_sent_velocity_p95: dict[str, float] = {}
    per_joint_velocity_violations = []
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
        shortfall = mode.get("forward_shortfall_diagnostic") or {}
        shortfall_cost = shortfall.get("shortfall_cost") or {}
        if finite(shortfall_cost.get("mean")):
            forward_shortfall_cost_means.append(float(shortfall_cost["mean"]))
        for joint in PITCH_CHAIN_JOINTS:
            item = (mode.get("joints") or {}).get(joint, {})
            tracking = (item.get("joint_target_tracking_error_rad") or {}).get("p95")
            velocity = (item.get("sent_target_velocity_rad_s") or {}).get("p95")
            saturation = item.get("action_saturation_pct")
            if finite(tracking):
                pitch_tracking.append(float(tracking))
            if finite(velocity):
                velocity_value = float(velocity)
                sent_velocity.append(velocity_value)
                per_joint_sent_velocity_p95[joint] = max(
                    per_joint_sent_velocity_p95.get(joint, -math.inf),
                    velocity_value,
                )
                limit = velocity_limits.get(joint)
                if finite(limit) and velocity_value > float(limit):
                    per_joint_velocity_violations.append(
                        {
                            "joint": joint,
                            "velocity_p95_rad_s": velocity_value,
                            "limit_rad_s": float(limit),
                            "excess_rad_s": velocity_value - float(limit),
                        }
                    )
            if finite(saturation):
                action_saturation.append(float(saturation))
    max_velocity_excess = max_finite(
        item["excess_rad_s"] for item in per_joint_velocity_violations
    )

    metrics = {
        "max_action_saturation_pct": max_finite(action_saturation),
        "max_pitch_tracking_p95_rad": max_finite(pitch_tracking),
        "max_sent_target_velocity_p95_rad_s": max_finite(sent_velocity),
        "per_joint_sent_target_velocity_p95_rad_s": per_joint_sent_velocity_p95,
        "pitch_chain_velocity_violations": per_joint_velocity_violations,
        "max_sent_target_velocity_limit_excess_rad_s": max_velocity_excess or 0.0,
        "max_abs_body_pitch_p95_rad": max_finite(body_pitch_abs),
        "min_base_height_m": min(base_height_min) if base_height_min else None,
        "min_reward_mean": min(reward_mean) if reward_mean else None,
        "min_forward_command_tracking_ratio": (
            min(forward_ratios) if forward_ratios else None
        ),
        "max_abs_forward_velocity_error_m_s": max_finite(forward_velocity_errors),
        "max_forward_shortfall_cost_mean": max_finite(forward_shortfall_cost_means),
        "terminations": terminations,
    }
    command_x = command_x_values[0] if command_x_values else 0.0
    requires_forward_tracking = abs(command_x) >= 0.02
    if incomplete:
        status = "HOLD_CANDIDATE_FALL_OR_TERMINATION"
    elif not finite(metrics["max_action_saturation_pct"]):
        status = "HOLD_CANDIDATE_NO_METRICS"
    elif not velocity_limits:
        status = "HOLD_CANDIDATE_NO_VELOCITY_LIMITS"
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
        metrics["max_sent_target_velocity_limit_excess_rad_s"]
        > thresholds["max_sent_target_velocity_limit_excess_rad_s"]
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
    if config.mjx_step_loop_mode not in {
        "default",
        "scan",
        "python",
        "python_block_each",
    }:
        return {
            "status": "HOLD_SIM_RUNTIME_ERROR",
            "error": f"unsupported mjx step loop mode {config.mjx_step_loop_mode}",
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
        from mujoco import mjx
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

    command = jp.asarray(
        [config.command_x, config.command_y, config.command_yaw, 0.0, 0.0, 0.0, 0.0]
    )
    overrides = {
        "push_config.enable": bool(config.eval_push_enable),
        "lin_vel_x": [config.command_x, config.command_x],
        "lin_vel_y": [config.command_y, config.command_y],
        "ang_vel_yaw": [config.command_yaw, config.command_yaw],
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
    if config.max_motor_velocity_override_rad_s is not None:
        overrides["max_motor_velocity"] = float(
            config.max_motor_velocity_override_rad_s
        )
    if (
        config.eval_push_interval_min_s is not None
        or config.eval_push_interval_max_s is not None
    ):
        overrides["push_config.interval_range"] = [
            (
                5.0
                if config.eval_push_interval_min_s is None
                else float(config.eval_push_interval_min_s)
            ),
            (
                10.0
                if config.eval_push_interval_max_s is None
                else float(config.eval_push_interval_max_s)
            ),
        ]
    if (
        config.eval_push_magnitude_min is not None
        or config.eval_push_magnitude_max is not None
    ):
        overrides["push_config.magnitude_range"] = [
            (
                0.1
                if config.eval_push_magnitude_min is None
                else float(config.eval_push_magnitude_min)
            ),
            (
                1.0
                if config.eval_push_magnitude_max is None
                else float(config.eval_push_magnitude_max)
            ),
        ]

    try:
        with temporary_cwd(config.playground_root):
            env_config = joystick.default_config()
            applied_reward_overrides = apply_reward_overrides(
                env_config, config.reward_overrides
            )
            env = joystick.Joystick(
                task=config.task, config=env_config, config_overrides=overrides
            )
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
    try:
        policy_io = init_policy_io_state(session, config)
    except ValueError as exc:
        return {"status": "HOLD_POLICY_IO_CONTRACT", "error": str(exc), "policy": policy}
    input_name = policy_io["obs_input_name"]
    output_name = policy_io["action_output_name"]
    state_input_names = tuple(policy_io["state_input_names"])
    state_output_names = tuple(policy_io["state_output_names"])

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

        state.info["rng"], push1_rng, push2_rng, action_delay_rng = jax.random.split(
            state.info["rng"], 4
        )
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
        push_theta = jax.random.uniform(push1_rng, maxval=2 * jp.pi)
        push_magnitude = jax.random.uniform(
            push2_rng,
            minval=env._config.push_config.magnitude_range[0],
            maxval=env._config.push_config.magnitude_range[1],
        )
        push_direction = jp.array([jp.cos(push_theta), jp.sin(push_theta)])
        push = push_direction * (
            jp.mod(state.info["push_step"] + 1, state.info["push_interval_steps"]) == 0
        )
        push *= env._config.push_config.enable
        push_impulse = push * push_magnitude
        qvel = state.data.qvel
        qvel = qvel.at[
            env._floating_base_qvel_addr : env._floating_base_qvel_addr + 2
        ].set(
            push_impulse
            + qvel[
                env._floating_base_qvel_addr : env._floating_base_qvel_addr + 2
            ]
        )
        state = state.replace(data=state.data.replace(qvel=qvel))
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
        return state, action_w_delay, pre_rate_limit, sent_target, push, push_impulse

    def step_mjx_host_loop(data, ctrl, block_each: bool):
        for _ in range(int(env.n_substeps)):
            data = data.replace(ctrl=ctrl)
            data = mjx.step(env.mjx_model, data)
            if block_each:
                data = block_tree(jax, data)
        return data

    def apply_motor_target(
        state, action, sent_target, applied_target, push, push_impulse
    ):
        if config.mjx_step_loop_mode in {"default", "scan"}:
            data = mjx_env.step(env.mjx_model, state.data, applied_target, env.n_substeps)
        else:
            data = step_mjx_host_loop(
                state.data,
                applied_target,
                block_each=config.mjx_step_loop_mode == "python_block_each",
            )
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
        if hasattr(env, "_update_command_window_progress"):
            env._update_command_window_progress(state.info, data)
        obs = env._get_obs(data, state.info, contact)
        done = env._get_termination(data)
        if hasattr(env, "_get_command_progress_failure"):
            command_progress_failure = env._get_command_progress_failure(state.info)
            state.info["command_progress_failure"] = command_progress_failure.astype(
                state.info["command_progress_ratio"].dtype
            )
            done = done | command_progress_failure
        rewards = env._get_reward(
            data, action, state.info, state.metrics, done, first_contact, contact
        )
        rewards = {
            key: value * env._config.reward_config.scales[key]
            for key, value in rewards.items()
        }
        reward = sum(rewards.values()) * env.dt
        if (
            "reward_clip_min" in env._config.reward_config
            and "reward_clip_max" in env._config.reward_config
        ):
            reward = jp.clip(
                reward,
                env._config.reward_config.reward_clip_min,
                env._config.reward_config.reward_clip_max,
            )
        state.info["push"] = push
        state.info["push_velocity_impulse"] = push_impulse
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
        if "target_velocity_cost" in state.info:
            state.metrics["diagnostic/target_velocity_cost"] = state.info[
                "target_velocity_cost"
            ]
        if "actuator_bridge_tracking_cost" in state.info:
            state.metrics["diagnostic/actuator_bridge_tracking_cost"] = state.info[
                "actuator_bridge_tracking_cost"
            ]
        if "actuator_bridge_delay_ticks" in state.info:
            state.metrics["diagnostic/actuator_bridge_delay_ticks"] = state.info[
                "actuator_bridge_delay_ticks"
            ].astype(reward.dtype)
        if "actuator_bridge_tau_s" in state.info:
            state.metrics["diagnostic/actuator_bridge_tau_mean_s"] = jp.mean(
                state.info["actuator_bridge_tau_s"]
            )
        if "actuator_bridge_velocity_limit_rad_s" in state.info:
            state.metrics[
                "diagnostic/actuator_bridge_velocity_limit_mean_rad_s"
            ] = jp.mean(state.info["actuator_bridge_velocity_limit_rad_s"])
        if "command_progress_ratio" in state.info:
            state.metrics["diagnostic/command_progress_ratio"] = state.info[
                "command_progress_ratio"
            ]
        if "command_progress_shortfall_cost" in state.info:
            state.metrics["diagnostic/command_progress_shortfall_cost"] = state.info[
                "command_progress_shortfall_cost"
            ]
        if "command_progress_failure" in state.info:
            state.metrics["diagnostic/command_progress_failure"] = state.info[
                "command_progress_failure"
            ].astype(reward.dtype)
        done = done.astype(reward.dtype)
        return state.replace(data=data, obs=obs, reward=reward, done=done)

    refresh_obs_jit = jax.jit(refresh_obs)
    prepare_step_jit = jax.jit(prepare_step)
    apply_motor_target_runner = (
        jax.jit(apply_motor_target)
        if config.mjx_step_loop_mode in {"default", "scan"}
        else apply_motor_target
    )

    modes = {}
    sim_steps = max(1, int(round(config.duration_s / float(env.dt))))
    if config.trace_jsonl is not None and config.trace_jsonl.exists():
        config.trace_jsonl.unlink()
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
        "mjx_step_loop_mode": config.mjx_step_loop_mode,
        "mjx_step_loop_description": (
            "default/scan uses mujoco_playground._src.mjx_env.step, which "
            "wraps substeps in jax.lax.scan. python/python_block_each are "
            "eval-only ROCm workarounds that drive raw mujoco.mjx.step from "
            "the host for each substep."
        ),
        "push_disabled": not bool(config.eval_push_enable),
        "push_config": {
            "enable": bool(config.eval_push_enable),
            "interval_range_s": [
                float(value) for value in env._config.push_config.interval_range
            ],
            "magnitude_range": [
                float(value) for value in env._config.push_config.magnitude_range
            ],
            "recovery_window_s": float(config.push_recovery_window_s),
            "recovery_max_abs_pitch_rad": float(
                config.push_recovery_max_abs_pitch_rad
            ),
            "recovery_min_base_height_m": float(
                config.push_recovery_min_base_height_m
            ),
        },
        "noise_disabled": True,
        "action_delay_disabled": True,
        "command_pinned": [
            config.command_x,
            config.command_y,
            config.command_yaw,
            0.0,
            0.0,
            0.0,
            0.0,
        ],
        "reward_overrides_applied": applied_reward_overrides,
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
        hidden_state = {
            name: value.copy()
            for name, value in policy_io["hidden_state"].items()
        }

        for tick in range(sim_steps):
            obs = np.asarray(jax.device_get(state.obs["state"]), dtype=np.float32)
            if obs.shape != (config.expected_observation_dim,):
                return {
                    "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
                    "error": f"obs shape {obs.shape} != {(config.expected_observation_dim,)}",
                }
            feed = {input_name: obs[None, :]}
            for state_name in state_input_names:
                feed[state_name] = hidden_state[state_name]
            outputs = session.run([output_name, *state_output_names], feed)
            action = outputs[0][0]
            for state_name, value in zip(state_input_names, outputs[1:], strict=True):
                hidden_state[state_name] = np.asarray(value, dtype=np.float32)
            action = np.asarray(action, dtype=np.float32)
            if action.shape != (config.expected_action_dim,):
                return {
                    "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
                    "error": f"action shape {action.shape} != {(config.expected_action_dim,)}",
                }
            action = np.clip(
                action * float(config.policy_action_gain), -1.0, 1.0
            ).astype(np.float32)
            (
                state,
                action_w_delay,
                pre_rate,
                sent_target,
                push,
                push_impulse,
            ) = prepare_step_jit(state, jp.asarray(action))
            pre_np = np.asarray(jax.device_get(pre_rate), dtype=float)
            sent_np = np.asarray(jax.device_get(sent_target), dtype=float)
            applied_np = (
                sent_np.copy()
                if mode == "vanilla"
                else bridge.step(sent_np, float(env.dt))
            )
            state = apply_motor_target_runner(
                state,
                jp.asarray(action),
                sent_target,
                jp.asarray(applied_np),
                push,
                push_impulse,
            )
            actual = np.asarray(
                jax.device_get(env.get_actuator_joints_qpos(state.data.qpos)),
                dtype=float,
            )
            local_linvel = np.asarray(
                jax.device_get(env.get_local_linvel(state.data)),
                dtype=float,
            )
            foot_site_pos = np.asarray(
                jax.device_get(state.data.site_xpos[env._feet_site_id]),
                dtype=float,
            )
            qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
            base_addr = int(env._floating_base_qpos_addr)
            quat = qpos[base_addr + 3 : base_addr + 7]
            contacts = np.asarray(jax.device_get(state.info["last_contact"]), dtype=bool)
            done = bool(np.asarray(jax.device_get(state.done)))
            reward = float(np.asarray(jax.device_get(state.reward)))
            push_np = np.asarray(jax.device_get(state.info["push"]), dtype=float)
            push_impulse_np = np.asarray(
                jax.device_get(state.info["push_velocity_impulse"]), dtype=float
            )
            reward_terms = {}
            for key, value in state.metrics.items():
                if str(key).startswith(("reward/", "cost/", "diagnostic/")):
                    try:
                        reward_terms[str(key)] = float(np.asarray(jax.device_get(value)))
                    except Exception:
                        pass
            record = {
                "seed": int(config.seed),
                "tick": tick,
                "time_s": tick * float(env.dt),
                "obs0_6": obs[:6].astype(float).tolist(),
                "command": [
                    config.command_x,
                    config.command_y,
                    config.command_yaw,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                ],
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
                "local_linvel_m_s": local_linvel.astype(float).tolist(),
                "foot_contacts": contacts.astype(int).tolist(),
                "foot_site_pos_m": foot_site_pos.tolist(),
                "reward": reward,
                "push": push_impulse_np.astype(float).tolist(),
                "push_direction": push_np.astype(float).tolist(),
                "push_magnitude": float(np.linalg.norm(push_impulse_np)),
                "reward_terms": reward_terms,
                "done": done,
            }
            if config.trace_full_obs:
                record["obs_state"] = obs.astype(float).tolist()
                record["qpos"] = qpos.astype(float).tolist()
                record["qvel"] = np.asarray(jax.device_get(state.data.qvel), dtype=float).tolist()
                record["ctrl"] = np.asarray(jax.device_get(state.data.ctrl), dtype=float).tolist()
                record["base_quat_wxyz"] = quat.astype(float).tolist()
            records.append(record)
            if done:
                termination_reason = "fall_or_nan"
                break

        wall_clock = time.monotonic() - start
        joints = per_joint_mode_summary(records, float(env.dt))
        body_pitch = signed_stats([record["body_pitch_rad"] for record in records])
        base_x = signed_stats([record["base_x_m"] for record in records])
        base_y = signed_stats([record["base_y_m"] for record in records])
        base_height = signed_stats([record["base_height_m"] for record in records])
        local_vx_values = [
            record["local_linvel_m_s"][0]
            for record in records
            if record.get("local_linvel_m_s")
        ]
        local_vx = signed_stats(local_vx_values)
        reward_stats = signed_stats([record["reward"] for record in records])
        reward_terms = reward_term_summary(records)
        if config.trace_jsonl is not None:
            append_trace_records(config.trace_jsonl, mode, records)
        if len(records) >= 2:
            elapsed_s = max(
                float(records[-1]["time_s"]) - float(records[0]["time_s"]),
                float(env.dt),
            )
            progress_x = float(records[-1]["base_x_m"]) - float(records[0]["base_x_m"])
            progress_y = float(records[-1]["base_y_m"]) - float(records[0]["base_y_m"])
            world_mean_vx = progress_x / elapsed_s
            mean_vx = (
                float(np.mean(local_vx_values))
                if local_vx_values
                else world_mean_vx
            )
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
            world_mean_vx = None
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
            "command": [
                config.command_x,
                config.command_y,
                config.command_yaw,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            "body_pitch_rad": body_pitch,
            "base_x_m": base_x,
            "base_y_m": base_y,
            "base_height_m": base_height,
            "local_forward_velocity_m_s": local_vx,
            "forward_motion": {
                "elapsed_s": elapsed_s,
                "progress_x_m": progress_x,
                "progress_y_m": progress_y,
                "world_mean_velocity_x_m_s": world_mean_vx,
                "mean_velocity_x_m_s": mean_vx,
                "command_x_m_s": float(config.command_x),
                "velocity_error_m_s": velocity_error,
                "command_tracking_ratio": ratio,
                "measurement_frame": "local_base_x",
            },
            "forward_shortfall_diagnostic": forward_shortfall_diagnostic(
                local_vx_values,
                float(config.command_x),
                required_ratio=config.forward_diagnostic_required_ratio,
                deadband=config.forward_diagnostic_deadband,
            ),
            "reward": reward_stats,
            "reward_terms": reward_terms,
            "push_recovery": push_recovery_summary(
                records,
                float(env.dt),
                float(config.push_recovery_window_s),
                float(config.push_recovery_max_abs_pitch_rad),
                float(config.push_recovery_min_base_height_m),
            ),
            "foot_contact_counts": {
                "left": int(contact_counts[0]) if len(contact_counts) > 0 else 0,
                "right": int(contact_counts[1]) if len(contact_counts) > 1 else 0,
            },
            "joints": joints,
            "pitch_chain_summary": pitch_chain_summary(joints),
            "policy_io": {
                "obs_input_name": input_name,
                "action_output_name": output_name,
                "state_input_names": list(state_input_names),
                "state_output_names": list(state_output_names),
                "stateful": bool(state_input_names),
            },
        }

    candidate_gate = None
    if config.eval_role == "candidate":
        candidate_gate = classify_candidate_gate(modes, config.fit)
        status = candidate_gate["status"]
    else:
        status = classify_closed_loop(modes) if "fitted" in modes else "PASS_CLOSED_LOOP_REPRODUCTION"
    return {
        "status": status,
        "eval_role": config.eval_role,
        "candidate_gate": candidate_gate,
        "policy": policy,
        "policy_io": {
            "obs_input_name": input_name,
            "action_output_name": output_name,
            "state_input_names": list(state_input_names),
            "state_output_names": list(state_output_names),
            "state_input_shapes": policy_io["state_input_shapes"],
            "stateful": bool(state_input_names),
        },
        "policy_action_gain": float(config.policy_action_gain),
        "command": [
            float(config.command_x),
            float(config.command_y),
            float(config.command_yaw),
            0.0,
            0.0,
            0.0,
            0.0,
        ],
        "forward_diagnostic": {
            "required_ratio": float(config.forward_diagnostic_required_ratio),
            "deadband": float(config.forward_diagnostic_deadband),
        },
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
            "mjx_step_loop_mode": config.mjx_step_loop_mode,
            "action_scale": float(env._config.action_scale),
            "max_motor_velocity": float(env._config.max_motor_velocity),
            "max_motor_velocity_override_rad_s": (
                None
                if config.max_motor_velocity_override_rad_s is None
                else float(config.max_motor_velocity_override_rad_s)
            ),
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "insertion_point": insertion_point,
        "real_x008_reference": REAL_X008_REFERENCE,
        "modes": modes,
    }
