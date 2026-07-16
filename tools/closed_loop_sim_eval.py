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
import re
import sys
import tempfile
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
from oracle_phase_com_controller import (
    FEATURE_NAMES as ORACLE_FEATURE_NAMES,
    contact_mode as oracle_contact_mode,
    evaluate_controller as evaluate_oracle_controller,
    feature_vector as oracle_feature_vector,
    load_controller as load_oracle_controller,
    project_combined_action as project_oracle_combined_action,
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
    policy_phase_action_delta_json: Path | None = None
    policy_phase_action_delta_scale: float = 1.0
    policy_phase_action_delta_min_command_x: float = 0.02
    policy_action_rate_limit_rad_s: float | None = None
    policy_action_rate_limit_joint_indices: tuple[int, ...] = (2, 3, 4, 11, 12, 13)
    policy_action_rate_limit_values: tuple[float, ...] = ()
    max_motor_velocity_override_rad_s: float | None = None
    forward_diagnostic_required_ratio: float = 0.5
    forward_diagnostic_deadband: float = 0.02
    reward_overrides: Mapping[str, Any] | None = None
    trace_jsonl: Path | None = None
    trace_full_obs: bool = False
    trace_com_accelerometer_map_ticks: tuple[int, ...] = ()
    policy_obs_input_name: str | None = None
    policy_action_output_name: str | None = None
    policy_state_input_names: tuple[str, ...] = ()
    policy_state_output_names: tuple[str, ...] = ()
    policy_applied_target_observation: bool = False
    policy_reset_com_estimator_input: bool = False
    eval_push_enable: bool = False
    eval_push_interval_min_s: float | None = None
    eval_push_interval_max_s: float | None = None
    eval_push_magnitude_min: float | None = None
    eval_push_magnitude_max: float | None = None
    push_recovery_window_s: float = 0.5
    push_recovery_max_abs_pitch_rad: float = 0.8
    push_recovery_min_base_height_m: float = 0.08
    terrain_hfield_z_scale: float | None = None
    eval_dynamics_override: Mapping[str, Any] | None = None
    reset_settle_ticks: int = 0
    reset_mode: str = "playground"
    bridge_reset_align_joint_indices: tuple[int, ...] = ()
    reference_feature_table_path: Path | None = None
    reference_start_phase: int | None = None
    policy_phase_advance_before_observation: bool = False
    oracle_phase_com_controller_json: Path | None = None
    trace_oracle_state: bool = False


R2_DYNAMICS_OVERRIDE_KEYS = {
    "floor_friction",
    "joint_frictionloss_scale",
    "armature_scale",
    "torso_com_offset_m",
    "all_link_mass_scale",
    "torso_mass_add_kg",
    "joint_qpos0_offset_rad",
    "kp_scale",
}


def apply_eval_dynamics_override(
    model,
    override: Mapping[str, Any] | None,
    jp,
    *,
    torso_body_id: int | None = None,
):
    """Apply exactly one preregistered R2 dynamics axis to an MJX model."""
    if not override:
        return model, {"enabled": False, "key": None, "value": None, "readback": {}}
    if len(override) != 1:
        raise ValueError("eval_dynamics_override must contain exactly one axis")
    key, raw_value = next(iter(override.items()))
    if key not in R2_DYNAMICS_OVERRIDE_KEYS:
        raise ValueError(f"unsupported eval dynamics axis: {key}")

    dof_ids = np.flatnonzero(np.asarray(model.dof_hasfrictionloss, dtype=bool))
    joint_ids = np.asarray(model.dof_jntid, dtype=int)[dof_ids]
    joint_qpos_addrs = np.asarray(model.jnt_qposadr, dtype=int)[joint_ids]
    replacements = {}
    readback = {"affected_dof_ids": dof_ids.tolist(), "affected_joint_qpos_addrs": joint_qpos_addrs.tolist()}

    if key == "floor_friction":
        value = float(raw_value)
        before = float(np.asarray(model.geom_friction)[0, 0])
        replacements["geom_friction"] = model.geom_friction.at[0, 0].set(value)
        readback.update({"before": before, "after": value, "changed_indices": [[0, 0]]})
    elif key == "joint_frictionloss_scale":
        value = float(raw_value)
        before = np.asarray(model.dof_frictionloss)[dof_ids]
        after = before * value
        replacements["dof_frictionloss"] = model.dof_frictionloss.at[dof_ids].set(jp.asarray(after))
        readback.update({"before": before.tolist(), "after": after.tolist(), "changed_indices": dof_ids.tolist()})
    elif key == "armature_scale":
        value = float(raw_value)
        before = np.asarray(model.dof_armature)[dof_ids]
        after = before * value
        replacements["dof_armature"] = model.dof_armature.at[dof_ids].set(jp.asarray(after))
        readback.update({"before": before.tolist(), "after": after.tolist(), "changed_indices": dof_ids.tolist()})
    elif key == "torso_com_offset_m":
        if torso_body_id is None:
            raise ValueError("torso_com_offset_m requires a name-resolved torso_body_id")
        value = np.asarray(raw_value, dtype=float)
        if value.shape != (3,):
            raise ValueError("torso_com_offset_m must have exactly three values")
        body_id = int(torso_body_id)
        if body_id <= 0 or body_id >= int(model.nbody):
            raise ValueError(f"invalid torso_body_id: {body_id}")
        if float(np.asarray(model.body_mass)[body_id]) <= 0.0:
            raise ValueError(f"torso_body_id {body_id} is massless")
        before = np.asarray(model.body_ipos)[body_id]
        after = before + value
        replacements["body_ipos"] = model.body_ipos.at[body_id].set(jp.asarray(after))
        readback.update({
            "body_id": body_id,
            "body_mass_kg": float(np.asarray(model.body_mass)[body_id]),
            "before": before.tolist(),
            "after": after.tolist(),
            "changed_indices": [[body_id, 0], [body_id, 1], [body_id, 2]],
        })
        raw_value = value.tolist()
    elif key == "all_link_mass_scale":
        value = float(raw_value)
        before = np.asarray(model.body_mass)
        after = before * value
        replacements["body_mass"] = jp.asarray(after)
        readback.update({"before": before.tolist(), "after": after.tolist(), "changed_indices": list(range(len(before)))})
    elif key == "torso_mass_add_kg":
        if torso_body_id is None:
            raise ValueError("torso_mass_add_kg requires a name-resolved torso_body_id")
        value = float(raw_value)
        body_id = int(torso_body_id)
        if body_id <= 0 or body_id >= int(model.nbody):
            raise ValueError(f"invalid torso_body_id: {body_id}")
        before = float(np.asarray(model.body_mass)[body_id])
        if before <= 0.0:
            raise ValueError(f"torso_body_id {body_id} is massless")
        after = before + value
        replacements["body_mass"] = model.body_mass.at[body_id].set(after)
        readback.update({"body_id": body_id, "before": before, "after": after, "changed_indices": [body_id]})
    elif key == "joint_qpos0_offset_rad":
        value = np.asarray(raw_value, dtype=float)
        if value.ndim == 0:
            value = np.full(len(joint_qpos_addrs), float(value), dtype=float)
        if value.shape != (len(joint_qpos_addrs),):
            raise ValueError(f"joint_qpos0_offset_rad must be scalar or {len(joint_qpos_addrs)} values")
        before = np.asarray(model.qpos0)[joint_qpos_addrs]
        after = before + value
        replacements["qpos0"] = model.qpos0.at[joint_qpos_addrs].set(jp.asarray(after))
        readback.update({"before": before.tolist(), "after": after.tolist(), "offset": value.tolist(), "changed_indices": joint_qpos_addrs.tolist()})
        raw_value = value.tolist()
    elif key == "kp_scale":
        value = float(raw_value)
        before_gain = np.asarray(model.actuator_gainprm)[:, 0]
        before_bias = np.asarray(model.actuator_biasprm)[:, 1]
        after_gain = before_gain * value
        after_bias = -after_gain
        replacements["actuator_gainprm"] = model.actuator_gainprm.at[:, 0].set(jp.asarray(after_gain))
        replacements["actuator_biasprm"] = model.actuator_biasprm.at[:, 1].set(jp.asarray(after_bias))
        readback.update({"before_gain": before_gain.tolist(), "after_gain": after_gain.tolist(), "before_bias": before_bias.tolist(), "after_bias": after_bias.tolist(), "changed_indices": list(range(len(before_gain)))})
    else:  # pragma: no cover - exhaustive key guard above
        raise AssertionError(key)

    updated = model.tree_replace(replacements)
    return updated, {"enabled": True, "key": key, "value": raw_value, "readback": readback}


def inject_policy_applied_target_observation(obs, applied_target, enabled: bool):
    """Replace only the redundant sent-target observation slot when enabled."""
    if not enabled:
        return obs
    updated = dict(obs)
    updated["state"] = obs["state"].at[83:97].set(applied_target)
    if "privileged_state" in obs:
        updated["privileged_state"] = obs["privileged_state"].at[83:97].set(
            applied_target
        )
    return updated


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


def write_scaled_hfield_scene(source_xml: Path, z_scale: float) -> Path:
    text = source_xml.read_text()
    pattern = re.compile(r'(<hfield\b[^>]*\bsize=")([^"]+)(")')
    match = pattern.search(text)
    if not match:
        raise ValueError(f"no hfield size attribute found in {source_xml}")
    values = match.group(2).split()
    if len(values) != 4:
        raise ValueError(f"expected four hfield size values in {source_xml}: {values}")
    values[2] = f"{float(z_scale):.8g}"
    scaled_text = text[: match.start(2)] + " ".join(values) + text[match.end(2) :]
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=f"_hfield_z{float(z_scale):.8g}.xml",
        prefix=".codex_eval_",
        dir=source_xml.parent,
        delete=False,
    )
    with tmp:
        tmp.write(scaled_text)
    return Path(tmp.name)


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


def foot_clearance_summary(records: Sequence[Mapping[str, Any]]) -> dict:
    """Summarize foot site height and support timing from rollout records."""
    foot_names = ("left", "right")
    foot_pos = []
    contacts = []
    base_x = []
    for record in records:
        pos = record.get("foot_site_pos_m")
        contact = record.get("foot_contacts")
        base_x_m = record.get("base_x_m")
        if (
            isinstance(pos, list)
            and len(pos) >= 2
            and isinstance(contact, list)
            and len(contact) >= 2
        ):
            foot_pos.append(pos[:2])
            contacts.append(contact[:2])
            base_x.append(float(base_x_m) if finite(base_x_m) else 0.0)
    if not foot_pos:
        return {
            "available": False,
            "feet": {},
            "support": {},
        }

    pos_arr = np.asarray(foot_pos, dtype=float)
    contact_arr = np.asarray(contacts, dtype=bool)
    base_x_arr = np.asarray(base_x, dtype=float)
    support_counts = np.sum(contact_arr, axis=1)
    samples = int(contact_arr.shape[0])
    feet: dict[str, Any] = {}
    for index, name in enumerate(foot_names):
        z = pos_arr[:, index, 2]
        rel_x = pos_arr[:, index, 0] - base_x_arr
        contact = contact_arr[:, index]
        stance_z = z[contact]
        swing_z = z[~contact]
        stance_ref = float(np.median(stance_z)) if stance_z.size else None
        lift = swing_z - stance_ref if stance_ref is not None else np.asarray([])
        swing_segments = []
        start = None
        for sample_index, is_swing in enumerate(~contact):
            if bool(is_swing) and start is None:
                start = sample_index
            is_last = sample_index == samples - 1
            if start is not None and ((not bool(is_swing)) or is_last):
                end = sample_index if not bool(is_swing) else sample_index + 1
                if end - start >= 2:
                    segment_rel_x = rel_x[start:end]
                    segment_lift = (
                        z[start:end] - stance_ref
                        if stance_ref is not None
                        else np.asarray([])
                    )
                    swing_segments.append(
                        {
                            "ticks": int(end - start),
                            "rel_x_delta_m": float(segment_rel_x[-1] - segment_rel_x[0]),
                            "rel_x_range_m": float(
                                np.max(segment_rel_x) - np.min(segment_rel_x)
                            ),
                            "peak_lift_over_stance_m": (
                                float(np.max(segment_lift))
                                if segment_lift.size
                                else None
                            ),
                        }
                    )
                start = None
        rel_x_ranges = [item["rel_x_range_m"] for item in swing_segments]
        rel_x_deltas = [item["rel_x_delta_m"] for item in swing_segments]
        segment_peak_lifts = [
            item["peak_lift_over_stance_m"]
            for item in swing_segments
            if item["peak_lift_over_stance_m"] is not None
        ]
        feet[name] = {
            "contact_pct": float(np.mean(contact) * 100.0),
            "contact_transition_count": int(np.sum(contact[1:] != contact[:-1]))
            if samples > 1
            else 0,
            "swing_samples": int(np.sum(~contact)),
            "stance_samples": int(np.sum(contact)),
            "swing_segment_count": int(len(swing_segments)),
            "site_z_m": signed_stats(z),
            "site_rel_x_m": signed_stats(rel_x),
            "stance_site_z_m": signed_stats(stance_z),
            "swing_site_z_m": signed_stats(swing_z),
            "stance_reference_z_m": stance_ref,
            "swing_lift_over_stance_m": signed_stats(lift),
            "swing_peak_lift_over_stance_m": (
                float(np.max(lift)) if lift.size else None
            ),
            "swing_segment_rel_x_delta_m": signed_stats(rel_x_deltas),
            "swing_segment_rel_x_range_m": signed_stats(rel_x_ranges),
            "swing_segment_peak_lift_over_stance_m": signed_stats(segment_peak_lifts),
        }
    support = {
        "samples": samples,
        "left_contact_pct": feet["left"]["contact_pct"],
        "right_contact_pct": feet["right"]["contact_pct"],
        "no_contact_pct": float(np.mean(support_counts == 0) * 100.0),
        "single_support_pct": float(np.mean(support_counts == 1) * 100.0),
        "double_support_pct": float(np.mean(support_counts == 2) * 100.0),
        "left_only_pct": float(
            np.mean(contact_arr[:, 0] & ~contact_arr[:, 1]) * 100.0
        ),
        "right_only_pct": float(
            np.mean(contact_arr[:, 1] & ~contact_arr[:, 0]) * 100.0
        ),
        "support_transition_count": int(
            np.sum(np.any(contact_arr[1:] != contact_arr[:-1], axis=1))
        )
        if samples > 1
        else 0,
    }
    return {
        "available": True,
        "feet": feet,
        "support": support,
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
    "forward_swing_clearance_scale": "forward_swing_clearance",
    "forward_swing_balance_scale": "forward_swing_balance",
    "forward_swing_advance_scale": "forward_swing_advance",
    "forward_swing_target_rate_limit_scale": "forward_swing_target_rate_limit",
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
    "forward_swing_clearance_target_m",
    "forward_swing_balance_grace_steps",
    "forward_swing_advance_target_m",
    "forward_swing_target_rate_limit_joint_indices",
    "forward_swing_target_rate_limit_values",
    "action_rate_huber_delta",
    "action_magnitude_huber_delta",
    "target_rate_huber_delta",
    "actuator_tracking_huber_delta",
    "forward_shortfall_huber_delta",
    "forward_overshoot_huber_delta",
    "forward_wrong_direction_huber_delta",
    "forward_pitch_huber_delta",
    "forward_pitch_rate_huber_delta",
    "forward_swing_clearance_huber_delta",
    "forward_swing_advance_huber_delta",
    "forward_swing_target_rate_limit_huber_delta",
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
    # Float32 target construction can exceed an exact decimal limit by roughly
    # 1e-6 rad/s. Do not turn numerical representation noise into a policy hold.
    velocity_tolerance_rad_s = 1.0e-5
    thresholds = {
        "max_action_saturation_pct": 1.0,
        "max_pitch_tracking_p95_rad": 0.20,
        "max_sent_target_velocity_limit_excess_rad_s": 0.0,
        "max_sent_target_velocity_max_limit_excess_rad_s": 0.0,
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
    per_joint_sent_velocity_max: dict[str, float] = {}
    per_joint_velocity_violations = []
    per_joint_velocity_max_violations = []
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
            velocity_stats = item.get("sent_target_velocity_rad_s") or {}
            velocity = velocity_stats.get("p95")
            velocity_max = velocity_stats.get("max")
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
                if (
                    finite(limit)
                    and velocity_value > float(limit) + velocity_tolerance_rad_s
                ):
                    per_joint_velocity_violations.append(
                        {
                            "joint": joint,
                            "velocity_p95_rad_s": velocity_value,
                            "limit_rad_s": float(limit),
                            "excess_rad_s": velocity_value - float(limit),
                        }
                    )
            if finite(velocity_max):
                velocity_max_value = float(velocity_max)
                per_joint_sent_velocity_max[joint] = max(
                    per_joint_sent_velocity_max.get(joint, -math.inf),
                    velocity_max_value,
                )
                limit = velocity_limits.get(joint)
                if (
                    finite(limit)
                    and velocity_max_value > float(limit) + velocity_tolerance_rad_s
                ):
                    per_joint_velocity_max_violations.append(
                        {
                            "joint": joint,
                            "velocity_max_rad_s": velocity_max_value,
                            "limit_rad_s": float(limit),
                            "excess_rad_s": velocity_max_value - float(limit),
                        }
                    )
            if finite(saturation):
                action_saturation.append(float(saturation))
    max_velocity_excess = max_finite(
        item["excess_rad_s"] for item in per_joint_velocity_violations
    )
    max_velocity_max_excess = max_finite(
        item["excess_rad_s"] for item in per_joint_velocity_max_violations
    )

    metrics = {
        "max_action_saturation_pct": max_finite(action_saturation),
        "max_pitch_tracking_p95_rad": max_finite(pitch_tracking),
        "max_sent_target_velocity_p95_rad_s": max_finite(sent_velocity),
        "per_joint_sent_target_velocity_p95_rad_s": per_joint_sent_velocity_p95,
        "per_joint_sent_target_velocity_max_rad_s": per_joint_sent_velocity_max,
        "pitch_chain_velocity_violations": per_joint_velocity_violations,
        "pitch_chain_velocity_max_violations": per_joint_velocity_max_violations,
        "max_sent_target_velocity_limit_excess_rad_s": max_velocity_excess or 0.0,
        "max_sent_target_velocity_max_limit_excess_rad_s": (
            max_velocity_max_excess or 0.0
        ),
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
    elif (
        metrics["max_sent_target_velocity_max_limit_excess_rad_s"]
        > thresholds["max_sent_target_velocity_max_limit_excess_rad_s"]
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
    if (
        config.reference_feature_table_path is not None
        and not config.reference_feature_table_path.exists()
    ):
        return {
            "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
            "error": (
                "reference feature table missing: "
                f"{config.reference_feature_table_path}"
            ),
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
        from playground.open_duck_mini_v2 import constants as duck_constants
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

    terrain_override = {
        "enabled": False,
        "hfield_z_scale": None,
        "source_xml": None,
        "temp_xml": None,
    }
    temp_scene_xml: Path | None = None
    original_task_to_xml = duck_constants.task_to_xml
    try:
        with temporary_cwd(config.playground_root):
            env_config = joystick.default_config()
            if config.policy_reset_com_estimator_input:
                if not hasattr(env_config, "ground_up_reset_com_estimator_input"):
                    raise ValueError(
                        "playground config does not expose "
                        "ground_up_reset_com_estimator_input"
                    )
                env_config.ground_up_reset_com_estimator_input = True
                env_config.nominal_reference_bootstrap = True
            if config.reference_feature_table_path is not None:
                env_config.reference_feature_table_path = str(
                    config.reference_feature_table_path.resolve()
                )
            applied_reward_overrides = apply_reward_overrides(
                env_config, config.reward_overrides
            )
            if config.terrain_hfield_z_scale is not None:
                source_xml = Path(original_task_to_xml(config.task))
                temp_scene_xml = write_scaled_hfield_scene(
                    source_xml, float(config.terrain_hfield_z_scale)
                )
                terrain_override = {
                    "enabled": True,
                    "hfield_z_scale": float(config.terrain_hfield_z_scale),
                    "source_xml": str(source_xml),
                    "temp_xml": str(temp_scene_xml),
                }

                def task_to_xml_override(task_name: str):
                    if task_name == config.task:
                        return temp_scene_xml
                    return original_task_to_xml(task_name)

                duck_constants.task_to_xml = task_to_xml_override
            env = joystick.Joystick(
                task=config.task, config=env_config, config_overrides=overrides
            )
            torso_body_id = int(env.mj_model.body("trunk_assembly").id)
            env._mjx_model, dynamics_override = apply_eval_dynamics_override(
                env.mjx_model,
                config.eval_dynamics_override,
                jp,
                torso_body_id=torso_body_id,
            )
            if dynamics_override["key"] in {"torso_com_offset_m", "torso_mass_add_kg"}:
                dynamics_override["readback"]["body_name"] = "trunk_assembly"
            if dynamics_override["key"] == "joint_qpos0_offset_rad":
                addresses = np.asarray(
                    dynamics_override["readback"]["affected_joint_qpos_addrs"],
                    dtype=int,
                )
                offsets = np.asarray(dynamics_override["value"], dtype=float)
                init_before = np.asarray(env._init_q)[addresses]
                init_after = init_before + offsets
                env._init_q = env._init_q.at[addresses].set(jp.asarray(init_after))
                dynamics_override["readback"]["home_init_before"] = init_before.tolist()
                dynamics_override["readback"]["home_init_after"] = init_after.tolist()
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "status": "HOLD_SIM_RUNTIME_ERROR",
            "error": f"env init failed: {type(exc).__name__}: {exc}",
        }
    finally:
        duck_constants.task_to_xml = original_task_to_xml
        if temp_scene_xml is not None:
            with contextlib.suppress(OSError):
                temp_scene_xml.unlink()

    com_accelerometer_map_ticks = tuple(
        int(tick) for tick in config.trace_com_accelerometer_map_ticks
    )
    if len(set(com_accelerometer_map_ticks)) != len(com_accelerometer_map_ticks):
        raise ValueError("trace_com_accelerometer_map_ticks must be unique")
    if any(tick < 0 for tick in com_accelerometer_map_ticks):
        raise ValueError("trace_com_accelerometer_map_ticks must be nonnegative")
    com_accelerometer_map_runner = None
    com_negative_body_ipos = None
    com_positive_body_ipos = None
    if com_accelerometer_map_ticks:
        nominal_body_ipos = env.mjx_model.body_ipos
        com_negative_body_ipos = nominal_body_ipos.at[torso_body_id, 0].add(-0.05)
        com_positive_body_ipos = nominal_body_ipos.at[torso_body_id, 0].add(0.05)

        def read_com_accelerometer(data, body_ipos):
            branch_model = env.mjx_model.replace(body_ipos=body_ipos)
            branch_data = mjx.forward(branch_model, data)
            return env.get_accelerometer(branch_data)

        com_accelerometer_map_runner = read_com_accelerometer

    try:
        session = ort.InferenceSession(str(config.policy_path), providers=["CPUExecutionProvider"])
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "status": "HOLD_ENV_NOT_READY",
            "error": f"ONNX Runtime session failed: {type(exc).__name__}: {exc}",
        }
    policy = policy_metadata(session, config.policy_path)
    phase_action_delta = None
    if config.policy_phase_action_delta_json is not None:
        try:
            phase_payload = json.loads(config.policy_phase_action_delta_json.read_text())
            phase_action_delta = np.asarray(
                phase_payload["phase_action_coefficient_delta"], dtype=np.float32
            )
        except Exception as exc:
            return {
                "status": "HOLD_POLICY_PHASE_DELTA_CONTRACT",
                "error": f"failed to load phase action delta: {type(exc).__name__}: {exc}",
            }
        if phase_action_delta.shape != (3, config.expected_action_dim):
            return {
                "status": "HOLD_POLICY_PHASE_DELTA_CONTRACT",
                "error": (
                    f"phase action delta shape {phase_action_delta.shape} != "
                    f"{(3, config.expected_action_dim)}"
                ),
            }
    oracle_controller = None
    oracle_endpoint_offset_m = 0.0
    if config.oracle_phase_com_controller_json is not None:
        try:
            oracle_controller = load_oracle_controller(
                config.oracle_phase_com_controller_json
            )
        except Exception as exc:
            return {
                "status": "HOLD_ORACLE_CONTROLLER_CONTRACT",
                "error": f"failed to load oracle controller: {type(exc).__name__}: {exc}",
            }
        if config.eval_dynamics_override:
            offset = config.eval_dynamics_override.get("torso_com_offset_m")
            if offset is not None:
                oracle_endpoint_offset_m = float(np.asarray(offset, dtype=float)[0])
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
        applied_target = state.info.get(
            "actuator_bridge_applied_targets", state.info["motor_targets"]
        )
        obs = inject_policy_applied_target_observation(
            env._get_obs(state.data, state.info, contact),
            applied_target,
            config.policy_applied_target_observation,
        )
        return state.replace(obs=obs)

    def set_reference_start(state):
        if not joystick.USE_IMITATION_REWARD or config.reference_start_phase is None:
            return state
        phase = int(config.reference_start_phase) % int(env.PRM.nb_steps_in_period)
        state.info["imitation_i"] = phase
        state.info["imitation_phase"] = jp.array(
            [
                jp.cos((phase / env.PRM.nb_steps_in_period) * 2 * jp.pi),
                jp.sin((phase / env.PRM.nb_steps_in_period) * 2 * jp.pi),
            ]
        )
        state.info["current_reference_motion"] = env.PRM.get_reference_motion(
            command[0], command[1], command[2], phase
        )
        return state

    def advance_reference(state):
        """Advance only the imitation phase/reference, without stepping physics."""
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
        return state

    def prepare_step(state, action):
        state.info["command"] = command
        if not config.policy_phase_advance_before_observation:
            state = advance_reference(state)

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
        obs = inject_policy_applied_target_observation(
            env._get_obs(data, state.info, contact),
            applied_target,
            config.policy_applied_target_observation,
        )
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

    def settle_reset_step(state, applied_target):
        if config.mjx_step_loop_mode in {"default", "scan"}:
            data = mjx_env.step(env.mjx_model, state.data, applied_target, env.n_substeps)
        else:
            data = step_mjx_host_loop(
                state.data,
                applied_target,
                block_each=config.mjx_step_loop_mode == "python_block_each",
            )
        contact = jp.array(
            [
                geoms_colliding(data, geom_id, env._floor_geom_id)
                for geom_id in env._feet_geom_id
            ]
        )
        state.info["command"] = command
        state.info["motor_targets"] = applied_target
        state.info["last_contact"] = contact
        state.info["feet_air_time"] = jp.zeros_like(state.info["feet_air_time"])
        state.info["swing_peak"] = jp.zeros_like(state.info["swing_peak"])
        obs = inject_policy_applied_target_observation(
            env._get_obs(data, state.info, contact),
            applied_target,
            config.policy_applied_target_observation,
        )
        return state.replace(data=data, obs=obs)

    def apply_eval_reset_mode(state):
        if config.reset_mode == "playground":
            return state
        if config.reset_mode != "home-support":
            raise ValueError(f"unsupported reset_mode: {config.reset_mode}")
        data = mjx_env.init(
            env.mjx_model,
            qpos=env._init_q,
            qvel=jp.zeros(env.mjx_model.nv),
            ctrl=env._default_actuator,
        )
        contact = jp.array(
            [
                geoms_colliding(data, geom_id, env._floor_geom_id)
                for geom_id in env._feet_geom_id
            ]
        )
        state.info["command"] = command
        state.info["last_act"] = jp.zeros(env.mjx_model.nu)
        state.info["last_last_act"] = jp.zeros(env.mjx_model.nu)
        state.info["last_last_last_act"] = jp.zeros(env.mjx_model.nu)
        state.info["motor_targets"] = env._default_actuator
        if "actuator_bridge_target_history" in state.info:
            history = state.info["actuator_bridge_target_history"]
            history_ticks = int(history.size) // int(env.mjx_model.nu)
            state.info["actuator_bridge_target_history"] = jp.tile(
                env._default_actuator,
                history_ticks,
            )
        if "actuator_bridge_applied_targets" in state.info:
            state.info["actuator_bridge_applied_targets"] = env._default_actuator
        if "target_velocity" in state.info:
            state.info["target_velocity"] = jp.zeros(env.mjx_model.nu)
        state.info["last_contact"] = contact
        state.info["feet_air_time"] = jp.zeros_like(state.info["feet_air_time"])
        state.info["swing_peak"] = jp.zeros_like(state.info["swing_peak"])
        if "foot_stance_height" in state.info:
            state.info["foot_stance_height"] = data.site_xpos[env._feet_site_id][..., -1]
        if "foot_stance_forward_x" in state.info:
            state.info["foot_stance_forward_x"] = env._foot_forward_x(data)
        if "swing_peak_lift" in state.info:
            state.info["swing_peak_lift"] = jp.zeros_like(state.info["swing_peak_lift"])
        if "swing_peak_forward_advance" in state.info:
            state.info["swing_peak_forward_advance"] = jp.zeros_like(
                state.info["swing_peak_forward_advance"]
            )
        if "forward_swing_steps" in state.info:
            state.info["forward_swing_steps"] = jp.zeros_like(
                state.info["forward_swing_steps"]
            )
        state.info["action_history"] = jp.zeros_like(state.info["action_history"])
        state.info["imu_history"] = jp.zeros_like(state.info["imu_history"])
        obs = inject_policy_applied_target_observation(
            env._get_obs(data, state.info, contact),
            env._default_actuator,
            config.policy_applied_target_observation,
        )
        return state.replace(data=data, obs=obs, done=jp.zeros_like(state.done))

    refresh_obs_jit = jax.jit(refresh_obs)
    prepare_step_jit = jax.jit(prepare_step)
    advance_reference_jit = jax.jit(advance_reference)
    apply_motor_target_runner = (
        jax.jit(apply_motor_target)
        if config.mjx_step_loop_mode in {"default", "scan"}
        else apply_motor_target
    )
    settle_reset_step_runner = (
        jax.jit(settle_reset_step)
        if config.mjx_step_loop_mode in {"default", "scan"}
        else settle_reset_step
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
            "keeps the sent target in environment info. obs[83:97] is the bridge-"
            "applied target only when policy_applied_target_observation is enabled."
        ),
        "double_rate_limit": False,
        "policy_applied_target_observation": bool(
            config.policy_applied_target_observation
        ),
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
        "reference_feature_table_path": (
            None
            if config.reference_feature_table_path is None
            else str(config.reference_feature_table_path.resolve())
        ),
        "reference_start_phase": (
            None if config.reference_start_phase is None
            else int(config.reference_start_phase)
        ),
        "policy_phase_advance_before_observation": bool(
            config.policy_phase_advance_before_observation
        ),
        "terrain_override": terrain_override,
        "dynamics_override": dynamics_override,
        "reset_settle_ticks": int(config.reset_settle_ticks),
        "reset_mode": config.reset_mode,
        "bridge_reset_align_joint_indices": list(
            config.bridge_reset_align_joint_indices
        ),
        "bridge_reset_alignment_description": (
            "Default-off eval-only diagnostic: initialize only the selected "
            "actuator-bridge applied targets from measured reset joint positions."
        ),
        "reset_settle_duration_s": float(config.reset_settle_ticks) * float(env.dt),
        "reset_settle_description": (
            "Eval-only default-off diagnostic. When nonzero, reset physics is "
            "stepped under the reset motor target before the policy loop starts; "
            "policy hidden state, action history, reward counters, and sample "
            "counts are not advanced."
        ),
        "trace_com_accelerometer_map": {
            "enabled": bool(com_accelerometer_map_ticks),
            "ticks": list(com_accelerometer_map_ticks),
            "body_name": "trunk_assembly",
            "body_id": int(torso_body_id),
            "body_ipos_axis": 0,
            "offsets_m": [-0.05, 0.05],
            "branch_operation": "mjx.forward_only_no_time_advance",
        },
    }

    for mode in available_modes(config.bridge_mode):
        start = time.monotonic()
        records: list[dict] = []
        params = mode_params(mode, config.fit)
        state = env.reset(jax.random.PRNGKey(config.seed))
        state.info["command"] = command
        state = apply_eval_reset_mode(state)
        state = set_reference_start(state)
        state = refresh_obs_jit(state)
        if config.reset_settle_ticks > 0:
            settle_target = state.info["motor_targets"]
            for _ in range(int(config.reset_settle_ticks)):
                state = settle_reset_step_runner(state, settle_target)
            state = refresh_obs_jit(state)
        initial_target = np.asarray(
            jax.device_get(state.info["motor_targets"]), dtype=float
        )
        if config.bridge_reset_align_joint_indices:
            reset_actual = np.asarray(
                jax.device_get(env.get_actuator_joints_qpos(state.data.qpos)),
                dtype=float,
            )
            indices = np.asarray(config.bridge_reset_align_joint_indices, dtype=int)
            if np.any(indices < 0) or np.any(indices >= initial_target.size):
                raise ValueError(
                    "bridge_reset_align_joint_indices outside actuator contract: "
                    f"{config.bridge_reset_align_joint_indices}"
                )
            initial_target = initial_target.copy()
            initial_target[indices] = reset_actual[indices]
        bridge = ActuatorBridgeModel(params, initial_target=initial_target)
        termination_reason = None
        hidden_state = {
            name: value.copy()
            for name, value in policy_io["hidden_state"].items()
        }
        previous_rate_bounded_action: np.ndarray | None = (
            np.zeros(config.expected_action_dim, dtype=np.float32)
            if config.policy_action_rate_limit_rad_s is not None
            else None
        )
        previous_oracle_final_action = np.zeros(
            config.expected_action_dim, dtype=np.float32
        )
        previous_whole_body_com: np.ndarray | None = None

        for tick in range(sim_steps):
            if config.policy_phase_advance_before_observation:
                state = advance_reference_jit(state)
                state = refresh_obs_jit(state)
            obs = np.asarray(jax.device_get(state.obs["state"]), dtype=np.float32)
            if obs.shape != (config.expected_observation_dim,):
                return {
                    "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
                    "error": f"obs shape {obs.shape} != {(config.expected_observation_dim,)}",
                }
            pre_qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
            pre_qvel = np.asarray(jax.device_get(state.data.qvel), dtype=float)
            pre_base_addr = int(env._floating_base_qpos_addr)
            pre_quat = pre_qpos[pre_base_addr + 3 : pre_base_addr + 7]
            pre_pitch = quat_wxyz_to_pitch(pre_quat)
            pre_roll = quat_wxyz_to_roll(pre_quat)
            pre_contacts = np.asarray(
                jax.device_get(state.info["last_contact"]), dtype=bool
            )
            pre_foot_site_pos = np.asarray(
                jax.device_get(state.data.site_xpos[env._feet_site_id]), dtype=float
            )
            pre_whole_body_com = np.asarray(
                jax.device_get(state.data.subtree_com[0]), dtype=float
            )
            if previous_whole_body_com is None:
                base_qvel_addr = int(env._floating_base_qvel_addr)
                pre_whole_body_com_velocity = pre_qvel[
                    base_qvel_addr : base_qvel_addr + 3
                ].copy()
            else:
                pre_whole_body_com_velocity = (
                    pre_whole_body_com - previous_whole_body_com
                ) / float(env.dt)
            base_qvel_addr = int(env._floating_base_qvel_addr)
            pre_angular_velocity = pre_qvel[
                base_qvel_addr + 3 : base_qvel_addr + 6
            ]
            phase_index = int(np.asarray(jax.device_get(state.info["imitation_i"])))
            phase_fraction = phase_index / float(env.PRM.nb_steps_in_period)
            oracle_features, oracle_geometry = oracle_feature_vector(
                phase_fraction=phase_fraction,
                contacts=pre_contacts,
                foot_positions=pre_foot_site_pos,
                whole_body_com=pre_whole_body_com,
                whole_body_com_velocity=pre_whole_body_com_velocity,
                command_x=float(config.command_x),
                pitch=pre_pitch,
                pitch_rate=float(pre_angular_velocity[1]),
                roll=pre_roll,
                roll_rate=float(pre_angular_velocity[0]),
            )
            com_accelerometer_map = None
            if tick in com_accelerometer_map_ticks:
                negative_accelerometer = np.asarray(
                    jax.device_get(
                        com_accelerometer_map_runner(
                            state.data, com_negative_body_ipos
                        )
                    ),
                    dtype=float,
                )
                positive_accelerometer = np.asarray(
                    jax.device_get(
                        com_accelerometer_map_runner(
                            state.data, com_positive_body_ipos
                        )
                    ),
                    dtype=float,
                )
                com_accelerometer_map = {
                    "nominal_actor_accelerometer_m_s2": obs[3:6].astype(float).tolist(),
                    "negative_accelerometer_m_s2": negative_accelerometer.tolist(),
                    "positive_accelerometer_m_s2": positive_accelerometer.tolist(),
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
            policy_base_action = np.clip(
                action * float(config.policy_action_gain), -1.0, 1.0
            ).astype(np.float32)
            phase_correction = np.zeros(config.expected_action_dim, dtype=np.float32)
            if (
                phase_action_delta is not None
                and float(config.command_x)
                >= float(config.policy_phase_action_delta_min_command_x)
            ):
                phase_features = np.asarray(
                    [1.0, float(obs[99]), float(obs[100])], dtype=np.float32
                )
                phase_correction = (
                    phase_features @ phase_action_delta
                    * float(config.policy_phase_action_delta_scale)
                ).astype(np.float32)
            raw_action = np.clip(
                policy_base_action + phase_correction, -1.0, 1.0
            ).astype(np.float32)
            action = raw_action.copy()
            oracle_residual = np.zeros(config.expected_action_dim, dtype=np.float32)
            oracle_evaluation = {
                "endpoint_bank": "disabled",
                "unclipped_corrected": [0.0] * 6,
            }
            oracle_projection = None
            oracle_previous_final_for_measurement = previous_oracle_final_action.copy()
            if oracle_controller is not None:
                mode_name = oracle_contact_mode(pre_contacts)
                oracle_residual, oracle_evaluation = evaluate_oracle_controller(
                    oracle_controller,
                    endpoint_offset_m=oracle_endpoint_offset_m,
                    mode=mode_name,
                    features=oracle_features,
                    action_dim=config.expected_action_dim,
                )
                # The protected graph already contains these projections.  At
                # nominal COM, the exact-zero residual therefore returns its
                # output directly; redundantly applying the same float32
                # projection can move a boundary value by one ULP.
                if abs(oracle_endpoint_offset_m) >= 1e-12:
                    actual_pre = np.asarray(
                        jax.device_get(env.get_actuator_joints_qpos(state.data.qpos)),
                        dtype=float,
                    )
                    action, oracle_projection = project_oracle_combined_action(
                        base_action=raw_action,
                        residual_action=oracle_residual,
                        previous_final_action=previous_oracle_final_action,
                        actual_position_rad=actual_pre,
                        default_position_rad=np.asarray(env._default_actuator, dtype=float),
                        action_scale_rad=float(env._config.action_scale),
                        max_action_delta=np.asarray(
                            oracle_controller["max_action_delta"], dtype=float
                        ),
                        actual_centered_guard_rad=float(
                            oracle_controller["actual_centered_guard_rad"]
                        ),
                    )
                previous_oracle_final_action = action.copy()
                if "previous_action" in hidden_state:
                    hidden_state["previous_action"] = action[None, :].astype(np.float32)
            if (
                config.policy_action_rate_limit_rad_s is not None
                and previous_rate_bounded_action is not None
            ):
                indices = np.asarray(
                    config.policy_action_rate_limit_joint_indices, dtype=int
                )
                if config.policy_action_rate_limit_values:
                    rate_limits = np.asarray(config.policy_action_rate_limit_values, dtype=float)
                    if rate_limits.shape != indices.shape:
                        raise ValueError("policy action rate-limit values/indices length mismatch")
                else:
                    rate_limits = np.full(indices.shape, float(config.policy_action_rate_limit_rad_s))
                max_action_delta = rate_limits * float(env.dt) / float(env._config.action_scale)
                action[indices] = np.clip(
                    action[indices],
                    previous_rate_bounded_action[indices] - max_action_delta,
                    previous_rate_bounded_action[indices] + max_action_delta,
                )
            previous_rate_bounded_action = action.copy()
            previous_sent_for_measurement = np.asarray(
                jax.device_get(state.info["motor_targets"]), dtype=float
            )
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
            tracking_error = np.abs(applied_np - actual)
            sent_velocity = np.abs(
                (sent_np - previous_sent_for_measurement) / float(env.dt)
            )
            velocity_limits = pitch_chain_velocity_limits_from_fit(config.fit)
            per_joint_rate_excess = np.zeros(config.expected_action_dim, dtype=float)
            for joint_name, limit in velocity_limits.items():
                joint_index = JOINT_NAMES.index(joint_name)
                raw_excess = max(0.0, sent_velocity[joint_index] - float(limit))
                per_joint_rate_excess[joint_index] = (
                    0.0 if raw_excess <= 1.0e-5 else raw_excess
                )
            oracle_envelope_excess = 0.0
            if oracle_projection is not None:
                max_delta = np.asarray(
                    oracle_controller["max_action_delta"], dtype=float
                )
                low = np.asarray(oracle_projection["guard_low_action"], dtype=float)
                high = np.asarray(oracle_projection["guard_high_action"], dtype=float)
                oracle_envelope_excess = max(
                    float(
                        np.max(
                            np.maximum(
                                np.abs(action - oracle_previous_final_for_measurement)
                                - max_delta,
                                0.0,
                            )
                        )
                    ),
                    float(np.max(np.maximum(low - action, 0.0))),
                    float(np.max(np.maximum(action - high, 0.0))),
                )
                if oracle_envelope_excess <= 1.0e-7:
                    oracle_envelope_excess = 0.0
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
                "policy_base_action": policy_base_action.astype(float).tolist(),
                "policy_phase_action_correction": phase_correction.astype(float).tolist(),
                "policy_raw_action": raw_action.astype(float).tolist(),
                "oracle_residual_action": oracle_residual.astype(float).tolist(),
                "action_w_delay": np.asarray(
                    jax.device_get(action_w_delay), dtype=float
                ).tolist(),
                "target_pre_rate_limit_rad": pre_np.tolist(),
                "sent_target_rad": sent_np.tolist(),
                "applied_target_rad": applied_np.tolist(),
                "actual_position_rad": actual.tolist(),
                "tracking_error_rad": tracking_error.tolist(),
                "action_saturated": (np.abs(action) >= 1.0 - 1.0e-7).astype(int).tolist(),
                "sent_target_velocity_rad_s": sent_velocity.tolist(),
                "sent_target_rate_excess_rad_s": per_joint_rate_excess.tolist(),
                "oracle_envelope_excess_normalized": oracle_envelope_excess,
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
            if config.trace_oracle_state or oracle_controller is not None:
                record["oracle_state"] = {
                    "feature_names": list(ORACLE_FEATURE_NAMES),
                    "features": oracle_features.tolist(),
                    "phase_index": phase_index,
                    "phase_fraction": phase_fraction,
                    "contacts": pre_contacts.astype(int).tolist(),
                    "contact_mode": oracle_geometry["contact_mode"],
                    "whole_body_com_m": pre_whole_body_com.tolist(),
                    "whole_body_com_velocity_m_s": pre_whole_body_com_velocity.tolist(),
                    "support_centroid_m": oracle_geometry["support_centroid_m"],
                    "support_relative_com_m": oracle_geometry[
                        "support_relative_com_m"
                    ],
                    "pitch_rad": pre_pitch,
                    "roll_rad": pre_roll,
                    "pitch_rate_rad_s": float(pre_angular_velocity[1]),
                    "roll_rate_rad_s": float(pre_angular_velocity[0]),
                    "applied_target_rad": np.asarray(
                        jax.device_get(
                            state.info.get(
                                "actuator_bridge_applied_targets",
                                state.info["motor_targets"],
                            )
                        ),
                        dtype=float,
                    ).tolist(),
                    "command_x_m_s": float(config.command_x),
                    "endpoint_offset_m": oracle_endpoint_offset_m,
                    "controller_evaluation": oracle_evaluation,
                    "projection": (
                        None
                        if oracle_projection is None
                        else {
                            key: value.astype(float).tolist()
                            for key, value in oracle_projection.items()
                        }
                    ),
                }
            if config.trace_full_obs:
                record["obs_state"] = obs.astype(float).tolist()
                record["qpos"] = qpos.astype(float).tolist()
                record["qvel"] = np.asarray(jax.device_get(state.data.qvel), dtype=float).tolist()
                record["ctrl"] = np.asarray(jax.device_get(state.data.ctrl), dtype=float).tolist()
                record["base_quat_wxyz"] = quat.astype(float).tolist()
            if com_accelerometer_map is not None:
                record["torso_com_accelerometer_map"] = com_accelerometer_map
            records.append(record)
            previous_whole_body_com = pre_whole_body_com.copy()
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
        body_forward_progress = (
            float(np.sum(local_vx_values) * float(env.dt))
            if local_vx_values
            else None
        )
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
        foot_clearance = foot_clearance_summary(records)
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
                "body_forward_progress_m": body_forward_progress,
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
            "foot_clearance": foot_clearance,
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
        "policy_phase_action_delta_json": (
            None
            if config.policy_phase_action_delta_json is None
            else str(config.policy_phase_action_delta_json)
        ),
        "policy_phase_action_delta_scale": float(config.policy_phase_action_delta_scale),
        "policy_phase_action_delta_min_command_x": float(
            config.policy_phase_action_delta_min_command_x
        ),
        "policy_phase_advance_before_observation": bool(
            config.policy_phase_advance_before_observation
        ),
        "oracle_phase_com_controller_json": (
            None
            if config.oracle_phase_com_controller_json is None
            else str(config.oracle_phase_com_controller_json)
        ),
        "trace_oracle_state": bool(config.trace_oracle_state),
        "policy_action_rate_limit_rad_s": config.policy_action_rate_limit_rad_s,
        "policy_action_rate_limit_joint_indices": list(
            config.policy_action_rate_limit_joint_indices
        ),
        "policy_action_rate_limit_values": list(config.policy_action_rate_limit_values),
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
            "terrain_override": terrain_override,
            "dynamics_override": dynamics_override,
        },
        "insertion_point": insertion_point,
        "real_x008_reference": REAL_X008_REFERENCE,
        "modes": modes,
    }
