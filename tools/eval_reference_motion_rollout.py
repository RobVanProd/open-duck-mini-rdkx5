#!/usr/bin/env python3
"""Evaluate a reference-motion target rollout in the Open Duck sim.

This is an offline mechanism diagnostic for the V20 result. It does not train,
SSH, deploy, or touch the robot. It asks:

If the policy action is replaced with actions derived from the matched
reference joint targets, can the sim follow the reference and satisfy the
low-command gate?

The rollout still uses the runtime-style action contract:

    target = home + action * action_scale

and the environment max-motor-velocity limiter. It does not teleport qpos to
the reference trajectory.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import tempfile
from typing import Any, Iterable

import numpy as np

from closed_loop_sim_eval import (
    apply_reward_overrides,
    quat_wxyz_to_pitch,
    signed_stats,
    temporary_cwd,
)
from run_actuator_bridge_training_smoke import (
    apply_reference_override,
    restore_reference_override,
)
from eval_policy_with_actuator_bridge import load_reward_overrides


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs" / "open-duck-playground" / "bin" / "python"
DEFAULT_REFERENCE = ROOT / "outputs" / "analysis" / "reference_motion_x004_override.pkl"
DEFAULT_REWARD_OVERRIDES = (
    ROOT
    / "outputs"
    / "analysis"
    / "colab_cli"
    / "open-duck-a100-v20-staged-curriculum-20260625T032259Z"
    / "manual_partial"
    / "open_duck_staged_curriculum_cli"
    / "01_phase1_interpolated_reference_seed_x004"
    / "phase_01_seed_gate_xp0p040"
    / "phase_reward_overrides.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REFERENCE_MOTION_ROLLOUT_V20.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "reference_motion_rollout_v20.json"
JOINT_NAMES = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


@dataclass
class SeedResult:
    seed: int
    samples: int
    termination_reason: str
    mean_vx: float | None
    track_ratio: float | None
    mean_vy: float | None
    vy_abs_p95: float | None
    body_pitch_abs_p95: float | None
    base_height_min: float | None
    action_saturation_pct: float | None
    reference_target_clip_p95: float | None
    reference_target_clip_max: float | None
    sent_target_velocity_p95: float | None
    joint_tracking_p95: float | None
    contact_counts: dict[str, int]
    contact_transitions: int
    reference_contact_mismatch_pct: float | None
    reward_terms_tail: dict[str, float]


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def percentile(values: list[float], pct: float) -> float | None:
    data = sorted(float(value) for value in values if finite(value))
    if not data:
        return None
    if len(data) == 1:
        return data[0]
    k = (len(data) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return data[lo]
    return data[lo] * (hi - k) + data[hi] * (k - lo)


def stats(values: Iterable[float], *, abs_value: bool = False) -> dict[str, float] | None:
    data = [
        abs(float(value)) if abs_value else float(value)
        for value in values
        if finite(value)
    ]
    if not data:
        return None
    return {
        "mean": float(np.mean(data)),
        "min": float(np.min(data)),
        "p50": percentile(data, 50),
        "p95": percentile(data, 95),
        "max": float(np.max(data)),
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def parse_int_list(value: str) -> list[int]:
    seeds: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            step = 1 if end >= start else -1
            seeds.extend(range(start, end + step, step))
        else:
            seeds.append(int(part))
    seen = set()
    deduped: list[int] = []
    for seed in seeds:
        if seed not in seen:
            seen.add(seed)
            deduped.append(seed)
    if not deduped:
        raise argparse.ArgumentTypeError("expected at least one seed")
    return deduped


def reference_frame_to_actuator_target(ref, default_actuator, jp):
    """Map 16-reference joint positions into the 14-action runtime order."""

    target = jp.asarray(default_actuator)
    target = target.at[:5].set(ref[:5])
    target = target.at[9:14].set(ref[11:16])
    return target


def build_cycle_projection_scales(env, jp, command, *, action_scale: float, max_velocity: float, dt_s: float):
    targets = []
    for phase in range(int(env.PRM.nb_steps_in_period)):
        ref = env.PRM.get_reference_motion(command[0], command[1], command[2], phase)
        target = reference_frame_to_actuator_target(ref, env._default_actuator, jp)
        targets.append(np.asarray(target, dtype=float))
    cycle = np.asarray(targets, dtype=float)
    home = np.asarray(env._default_actuator, dtype=float)
    deltas = cycle - home
    max_abs_delta = np.max(np.abs(deltas), axis=0)
    cycle_velocity = np.abs(np.diff(np.vstack([cycle, cycle[:1]]), axis=0) / max(dt_s, 1.0e-9))
    max_abs_velocity = np.max(cycle_velocity, axis=0)
    scale = np.ones_like(max_abs_delta)
    for index in range(len(scale)):
        if max_abs_delta[index] > 1.0e-9:
            scale[index] = min(scale[index], float(action_scale) / max_abs_delta[index])
        if max_abs_velocity[index] > 1.0e-9:
            scale[index] = min(scale[index], float(max_velocity) / max_abs_velocity[index])
    scale = np.clip(scale, 0.0, 1.0)
    return scale, {
        "scale": scale.tolist(),
        "max_abs_delta_rad": max_abs_delta.tolist(),
        "max_abs_velocity_rad_s": max_abs_velocity.tolist(),
    }


def build_projected_reference_cycle(env, jp, command, projection_scales_np):
    targets = []
    contacts = []
    for phase in range(int(env.PRM.nb_steps_in_period)):
        ref = env.PRM.get_reference_motion(command[0], command[1], command[2], phase)
        target = reference_frame_to_actuator_target(ref, env._default_actuator, jp)
        projected = env._default_actuator + (target - env._default_actuator) * jp.asarray(
            projection_scales_np
        )
        targets.append(np.asarray(projected, dtype=float))
        contacts.append(np.asarray(ref[32:34] > 0.5, dtype=int))
    return np.asarray(targets, dtype=float), np.asarray(contacts, dtype=int)


def summarize_records(
    *,
    seed: int,
    records: list[dict[str, Any]],
    command_x: float,
    dt_s: float,
) -> SeedResult:
    vx = [record["local_linvel_m_s"][0] for record in records]
    vy = [record["local_linvel_m_s"][1] for record in records]
    body_pitch_abs = [abs(record["body_pitch_rad"]) for record in records]
    base_height = [record["base_height_m"] for record in records]
    actions = np.asarray([record["action"] for record in records], dtype=float)
    reference_targets = np.asarray([record["reference_target_rad"] for record in records], dtype=float)
    pre_rate = np.asarray([record["target_pre_rate_limit_rad"] for record in records], dtype=float)
    sent = np.asarray([record["sent_target_rad"] for record in records], dtype=float)
    actual = np.asarray([record["actual_position_rad"] for record in records], dtype=float)
    clip_error = np.abs(reference_targets - pre_rate)
    sent_velocity = (
        np.abs(np.diff(sent, axis=0) / max(dt_s, 1.0e-9))
        if len(records) > 1
        else np.zeros((0, sent.shape[1] if sent.ndim == 2 else 0))
    )
    tracking = np.abs(sent - actual)
    contacts = [tuple(int(value) for value in record["foot_contacts"]) for record in records]
    reference_contacts = [
        tuple(int(value) for value in record.get("reference_foot_contacts", []))
        for record in records
    ]
    contact_counts = {str(pattern): contacts.count(pattern) for pattern in sorted(set(contacts))}
    contact_transitions = sum(1 for a, b in zip(contacts, contacts[1:]) if a != b)
    contact_mismatches = [
        actual != expected
        for actual, expected in zip(contacts, reference_contacts)
        if len(actual) == len(expected) and expected
    ]
    reward_keys = sorted(
        {
            key
            for record in records[-20:]
            for key in (record.get("reward_terms") or {}).keys()
        }
    )
    reward_tail = {}
    for key in reward_keys:
        values = [
            float((record.get("reward_terms") or {}).get(key))
            for record in records[-20:]
            if finite((record.get("reward_terms") or {}).get(key))
        ]
        if values:
            reward_tail[key] = float(np.mean(values))
    mean_vx = float(np.mean(vx)) if vx else None
    return SeedResult(
        seed=seed,
        samples=len(records),
        termination_reason="fall_or_nan" if records and records[-1].get("done") else "duration_complete",
        mean_vx=mean_vx,
        track_ratio=(
            mean_vx / command_x
            if mean_vx is not None and abs(command_x) > 1.0e-9
            else None
        ),
        mean_vy=float(np.mean(vy)) if vy else None,
        vy_abs_p95=percentile([abs(value) for value in vy], 95),
        body_pitch_abs_p95=percentile(body_pitch_abs, 95),
        base_height_min=min(base_height) if base_height else None,
        action_saturation_pct=(
            float(np.mean(np.abs(actions) >= 0.999) * 100.0)
            if actions.size
            else None
        ),
        reference_target_clip_p95=percentile(clip_error.reshape(-1).tolist(), 95),
        reference_target_clip_max=float(np.max(clip_error)) if clip_error.size else None,
        sent_target_velocity_p95=(
            percentile(sent_velocity.reshape(-1).tolist(), 95)
            if sent_velocity.size
            else 0.0
        ),
        joint_tracking_p95=(
            percentile(tracking.reshape(-1).tolist(), 95) if tracking.size else None
        ),
        contact_counts=contact_counts,
        contact_transitions=contact_transitions,
        reference_contact_mismatch_pct=(
            float(np.mean(contact_mismatches) * 100.0)
            if contact_mismatches
            else None
        ),
        reward_terms_tail=reward_tail,
    )


def summarize_per_joint(records: list[dict[str, Any]], dt_s: float) -> list[dict[str, Any]]:
    if not records:
        return []
    actions = np.asarray([record["action"] for record in records], dtype=float)
    reference_targets = np.asarray([record["reference_target_rad"] for record in records], dtype=float)
    pre_rate = np.asarray([record["target_pre_rate_limit_rad"] for record in records], dtype=float)
    sent = np.asarray([record["sent_target_rad"] for record in records], dtype=float)
    actual = np.asarray([record["actual_position_rad"] for record in records], dtype=float)
    clip_error = np.abs(reference_targets - pre_rate)
    tracking = np.abs(sent - actual)
    velocities: list[np.ndarray] = []
    by_seed: dict[int, list[dict[str, Any]]] = {}
    for record in records:
        by_seed.setdefault(int(record["seed"]), []).append(record)
    for seed_records in by_seed.values():
        seed_sent = np.asarray(
            [record["sent_target_rad"] for record in seed_records], dtype=float
        )
        if len(seed_sent) > 1:
            velocities.append(np.abs(np.diff(seed_sent, axis=0) / max(dt_s, 1.0e-9)))
    sent_velocity = np.vstack(velocities) if velocities else np.zeros((0, len(JOINT_NAMES)))
    rows = []
    for index, name in enumerate(JOINT_NAMES):
        rows.append(
            {
                "joint": name,
                "action_saturation_pct": float(np.mean(np.abs(actions[:, index]) >= 0.999) * 100.0),
                "reference_target_clip_p95_rad": percentile(clip_error[:, index].tolist(), 95),
                "reference_target_clip_max_rad": float(np.max(clip_error[:, index])),
                "sent_target_velocity_p95_rad_s": (
                    percentile(sent_velocity[:, index].tolist(), 95)
                    if sent_velocity.size
                    else 0.0
                ),
                "joint_tracking_p95_rad": percentile(tracking[:, index].tolist(), 95),
            }
        )
    return rows


def run_rollout(args: argparse.Namespace) -> dict[str, Any]:
    import jax
    import jax.numpy as jp
    from mujoco_playground._src import mjx_env
    from mujoco_playground._src.collision import geoms_colliding

    sys_path_inserted = False
    import sys

    playground_path = Path(args.playground_path).resolve()
    if str(playground_path) not in sys.path:
        sys.path.insert(0, str(playground_path))
        sys_path_inserted = True
    try:
        from playground.open_duck_mini_v2 import joystick
    finally:
        if sys_path_inserted:
            pass

    reward_overrides = load_reward_overrides(
        Path(args.reward_overrides_json) if args.reward_overrides_json else None,
        args.reward_overrides_phase,
    )
    command = jp.asarray(
        [args.command_x, args.command_y, args.command_yaw, 0.0, 0.0, 0.0, 0.0]
    )
    trace_root = Path(args.trace_dir) if args.trace_dir else None
    if trace_root:
        trace_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="open_duck_reference_rollout_") as tmp:
        tmp_path = Path(tmp)
        override_info = apply_reference_override(args, tmp_path)
        try:
            with temporary_cwd(playground_path):
                env_config = joystick.default_config()
                applied_reward_overrides = apply_reward_overrides(env_config, reward_overrides)
                env = joystick.Joystick(
                    task=args.task,
                    config=env_config,
                    config_overrides={
                        "push_config.enable": False,
                        "lin_vel_x": [args.command_x, args.command_x],
                        "lin_vel_y": [args.command_y, args.command_y],
                        "ang_vel_yaw": [args.command_yaw, args.command_yaw],
                        "neck_pitch_range": [0.0, 0.0],
                        "head_pitch_range": [0.0, 0.0],
                        "head_yaw_range": [0.0, 0.0],
                        "head_roll_range": [0.0, 0.0],
                        "noise_config.level": 0.0,
                        "noise_config.action_min_delay": 0,
                        "noise_config.action_max_delay": 1,
                        "noise_config.imu_min_delay": 0,
                        "noise_config.imu_max_delay": 1,
                    },
                )
                projection_scales_np, projection_summary = build_cycle_projection_scales(
                    env,
                    jp,
                    command,
                    action_scale=float(env._config.action_scale),
                    max_velocity=float(env._config.max_motor_velocity),
                    dt_s=float(env.dt),
                )
                projection_scales = jp.asarray(projection_scales_np)
                projected_cycle_np, projected_contacts_np = build_projected_reference_cycle(
                    env, jp, command, projection_scales_np
                )
                projected_cycle_targets = jp.asarray(projected_cycle_np)
                projected_cycle_contacts = jp.asarray(projected_contacts_np)
                reference_target_mode = args.reference_target_mode
                has_command_progress = hasattr(env, "_update_command_window_progress") and hasattr(
                    env, "_get_command_progress_failure"
                )
                reward_clip_min = float(
                    getattr(env._config.reward_config, "reward_clip_min", 0.0)
                )
                reward_clip_max = float(
                    getattr(env._config.reward_config, "reward_clip_max", 10000.0)
                )

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

            def step_reference(state):
                state.info["command"] = command
                proposed_i = (state.info["imitation_i"] + 1) % env.PRM.nb_steps_in_period
                current_contact = jp.array(
                    [
                        geoms_colliding(state.data, geom_id, env._floor_geom_id)
                        for geom_id in env._feet_geom_id
                    ]
                )
                if reference_target_mode == "contact_synchronized_projected":
                    phases = jp.arange(env.PRM.nb_steps_in_period)
                    phase_distance = (phases - proposed_i) % env.PRM.nb_steps_in_period
                    contact_error = jp.sum(
                        jp.abs(projected_cycle_contacts - current_contact.astype(int)),
                        axis=1,
                    )
                    state.info["imitation_i"] = jp.argmin(
                        contact_error * 100 + phase_distance
                    ).astype(state.info["imitation_i"].dtype)
                else:
                    state.info["imitation_i"] = proposed_i
                state.info["imitation_phase"] = jp.array(
                    [
                        jp.cos((state.info["imitation_i"] / env.PRM.nb_steps_in_period) * 2 * jp.pi),
                        jp.sin((state.info["imitation_i"] / env.PRM.nb_steps_in_period) * 2 * jp.pi),
                    ]
                )
                ref = env.PRM.get_reference_motion(
                    command[0], command[1], command[2], state.info["imitation_i"]
                )
                state.info["current_reference_motion"] = ref
                reference_target = reference_frame_to_actuator_target(
                    ref, env._default_actuator, jp
                )
                if reference_target_mode in (
                    "cycle_projected",
                    "contact_gated_projected",
                    "contact_synchronized_projected",
                ):
                    reference_target = env._default_actuator + (
                        reference_target - env._default_actuator
                    ) * projection_scales
                reference_foot_contacts = jp.where(ref[32:34] > 0.5, 1, 0)
                if reference_target_mode == "contact_gated_projected":
                    # If the reference asks a foot to swing but the sim still has
                    # that foot loaded, damp that leg's target delta instead of
                    # forcing the single-support schedule immediately.
                    leg_scale = jp.ones_like(reference_target)
                    left_scale = jp.where(
                        current_contact[0] & (reference_foot_contacts[0] == 0),
                        args.contact_gate_swing_scale,
                        1.0,
                    )
                    right_scale = jp.where(
                        current_contact[1] & (reference_foot_contacts[1] == 0),
                        args.contact_gate_swing_scale,
                        1.0,
                    )
                    leg_scale = leg_scale.at[:5].set(left_scale)
                    leg_scale = leg_scale.at[9:14].set(right_scale)
                    reference_target = env._default_actuator + (
                        reference_target - env._default_actuator
                    ) * leg_scale
                if reference_target_mode == "contact_synchronized_projected":
                    reference_target = projected_cycle_targets[state.info["imitation_i"]]
                    reference_foot_contacts = projected_cycle_contacts[state.info["imitation_i"]]
                action = jp.clip(
                    (reference_target - env._default_actuator) / env._config.action_scale,
                    -1.0,
                    1.0,
                )
                pre_rate_limit = env._default_actuator + action * env._config.action_scale
                prev_motor_targets = state.info["motor_targets"]
                sent_target = jp.clip(
                    pre_rate_limit,
                    prev_motor_targets - env._config.max_motor_velocity * env.dt,
                    prev_motor_targets + env._config.max_motor_velocity * env.dt,
                )
                data = mjx_env.step(env.mjx_model, state.data, sent_target, env.n_substeps)
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
                if has_command_progress:
                    env._update_command_window_progress(state.info, data)
                obs = env._get_obs(data, state.info, contact)
                done = env._get_termination(data)
                if has_command_progress:
                    command_progress_failure = env._get_command_progress_failure(state.info)
                    state.info["command_progress_failure"] = command_progress_failure.astype(
                        state.info["command_progress_ratio"].dtype
                    )
                else:
                    command_progress_failure = jp.array(False)
                done = done | command_progress_failure
                rewards = env._get_reward(
                    data, action, state.info, state.metrics, done, first_contact, contact
                )
                rewards = {
                    key: value * env._config.reward_config.scales[key]
                    for key, value in rewards.items()
                }
                reward = jp.clip(
                    sum(rewards.values()) * env.dt,
                    reward_clip_min,
                    reward_clip_max,
                )
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
                if has_command_progress:
                    state.metrics["diagnostic/command_progress_ratio"] = state.info[
                        "command_progress_ratio"
                    ]
                    state.metrics["diagnostic/command_progress_shortfall_cost"] = state.info[
                        "command_progress_shortfall_cost"
                    ]
                    state.metrics["diagnostic/command_progress_failure"] = (
                        command_progress_failure.astype(reward.dtype)
                    )
                done = done.astype(reward.dtype)
                return (
                    state.replace(data=data, obs=obs, reward=reward, done=done),
                    action,
                    reference_target,
                    reference_foot_contacts,
                    pre_rate_limit,
                    sent_target,
                )

            refresh_obs_jit = jax.jit(refresh_obs)
            step_reference_jit = jax.jit(step_reference)
            sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))
            seeds = parse_int_list(args.seeds)
            seed_results: list[SeedResult] = []
            seed_payloads: list[dict[str, Any]] = []
            all_records: list[dict[str, Any]] = []
            for seed in seeds:
                records: list[dict[str, Any]] = []
                state = env.reset(jax.random.PRNGKey(seed))
                state.info["command"] = command
                state.info["imitation_i"] = (
                    int(args.first_reference_phase) - 1
                ) % int(env.PRM.nb_steps_in_period)
                state = refresh_obs_jit(state)
                for tick in range(sim_steps):
                    (
                        state,
                        action,
                        reference_target,
                        reference_foot_contacts,
                        pre_rate,
                        sent_target,
                    ) = step_reference_jit(state)
                    qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
                    base_addr = int(env._floating_base_qpos_addr)
                    quat = qpos[base_addr + 3 : base_addr + 7]
                    local_linvel = np.asarray(
                        jax.device_get(env.get_local_linvel(state.data)), dtype=float
                    )
                    actual = np.asarray(
                        jax.device_get(env.get_actuator_joints_qpos(state.data.qpos)),
                        dtype=float,
                    )
                    contacts = np.asarray(jax.device_get(state.info["last_contact"]), dtype=bool)
                    reward_terms = {}
                    for key, value in state.metrics.items():
                        if str(key).startswith(("reward/", "cost/", "diagnostic/")):
                            try:
                                reward_terms[str(key)] = float(np.asarray(jax.device_get(value)))
                            except Exception:
                                pass
                    done = bool(np.asarray(jax.device_get(state.done)))
                    record = {
                        "tick": tick,
                        "time_s": tick * float(env.dt),
                        "seed": seed,
                        "mode": f"reference_target_{reference_target_mode}",
                        "command": [
                            args.command_x,
                            args.command_y,
                            args.command_yaw,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        "imitation_i": int(np.asarray(jax.device_get(state.info["imitation_i"]))),
                        "action": np.asarray(jax.device_get(action), dtype=float).tolist(),
                        "reference_target_rad": np.asarray(
                            jax.device_get(reference_target), dtype=float
                        ).tolist(),
                        "reference_foot_contacts": np.asarray(
                            jax.device_get(reference_foot_contacts), dtype=int
                        ).tolist(),
                        "target_pre_rate_limit_rad": np.asarray(
                            jax.device_get(pre_rate), dtype=float
                        ).tolist(),
                        "sent_target_rad": np.asarray(jax.device_get(sent_target), dtype=float).tolist(),
                        "actual_position_rad": actual.tolist(),
                        "body_pitch_rad": quat_wxyz_to_pitch(quat),
                        "base_x_m": float(qpos[base_addr]),
                        "base_y_m": float(qpos[base_addr + 1]),
                        "base_height_m": float(qpos[base_addr + 2]),
                        "local_linvel_m_s": local_linvel.astype(float).tolist(),
                        "foot_contacts": contacts.astype(int).tolist(),
                        "reward": float(np.asarray(jax.device_get(state.reward))),
                        "reward_terms": reward_terms,
                        "done": done,
                    }
                    records.append(record)
                    all_records.append(record)
                    if done:
                        break
                if trace_root:
                    trace_path = trace_root / f"reference_seed_{seed:03d}.jsonl"
                    trace_path.write_text(
                        "".join(json.dumps(record) + "\n" for record in records)
                    )
                result = summarize_records(
                    seed=seed,
                    records=records,
                    command_x=float(args.command_x),
                    dt_s=float(env.dt),
                )
                seed_results.append(result)
                seed_payloads.append(result.__dict__)
        finally:
            override_info = restore_reference_override(override_info)

    falls = sum(1 for item in seed_results if item.termination_reason != "duration_complete")
    track_values = [item.track_ratio for item in seed_results if finite(item.track_ratio)]
    vx_values = [item.mean_vx for item in seed_results if finite(item.mean_vx)]
    status = "PASS_REFERENCE_TARGET_ROLLOUT"
    if falls:
        status = "HOLD_REFERENCE_TARGET_TERMINATES"
    elif track_values and float(np.mean(track_values)) < float(args.min_track_ratio_mean):
        status = "HOLD_REFERENCE_TARGET_LOW_PROGRESS"
    payload = {
        "status": status,
        "command_x": args.command_x,
        "command_y": args.command_y,
        "command_yaw": args.command_yaw,
        "duration_s": args.duration_s,
        "seeds": parse_int_list(args.seeds),
        "reference": args.reference_motion_override,
        "reference_target_mode": args.reference_target_mode,
        "first_reference_phase": args.first_reference_phase,
        "contact_gate_swing_scale": args.contact_gate_swing_scale,
        "projection": (
            projection_summary
            if args.reference_target_mode
            in ("cycle_projected", "contact_gated_projected", "contact_synchronized_projected")
            else None
        ),
        "reward_overrides_json": args.reward_overrides_json,
        "reward_overrides_phase": args.reward_overrides_phase,
        "override": override_info,
        "applied_reward_overrides": applied_reward_overrides,
        "aggregate": {
            "runs": len(seed_results),
            "falls": falls,
            "duration_complete": len(seed_results) - falls,
            "track_ratio_mean": float(np.mean(track_values)) if track_values else None,
            "vx_mean": float(np.mean(vx_values)) if vx_values else None,
            "samples_mean": float(np.mean([item.samples for item in seed_results])),
            "vy_abs_p95_mean": float(np.mean([item.vy_abs_p95 for item in seed_results if finite(item.vy_abs_p95)])),
            "action_saturation_pct_mean": float(np.mean([item.action_saturation_pct for item in seed_results if finite(item.action_saturation_pct)])),
            "reference_target_clip_p95_mean": float(np.mean([item.reference_target_clip_p95 for item in seed_results if finite(item.reference_target_clip_p95)])),
            "joint_tracking_p95_mean": float(np.mean([item.joint_tracking_p95 for item in seed_results if finite(item.joint_tracking_p95)])),
            "reference_contact_mismatch_pct_mean": float(np.mean([item.reference_contact_mismatch_pct for item in seed_results if finite(item.reference_contact_mismatch_pct)])),
        },
        "per_joint": summarize_per_joint(all_records, dt_s=float(args.duration_s) / max(1, int(round(float(args.duration_s) / 0.02)))),
        "seed_results": seed_payloads,
    }
    return payload


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    aggregate = payload["aggregate"]
    lines = [
        "# Reference Motion Rollout",
        "",
        f"status: `{payload['status']}`",
        f"command_x: `{payload['command_x']}`",
        f"duration_s: `{payload['duration_s']}`",
        f"reference: `{payload['reference']}`",
        f"reference_target_mode: `{payload['reference_target_mode']}`",
        f"first_reference_phase: `{payload['first_reference_phase']}`",
        "",
        "## Aggregate",
        "",
    ]
    for key, value in aggregate.items():
        lines.append(f"- {key}: `{fmt(value)}`" if isinstance(value, float) else f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Per Seed",
            "",
            "| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |",
            "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in payload["seed_results"]:
        lines.append(
            "| {seed} | {samples} | `{termination_reason}` | {vx} | {track} | {vy} | {height} | {sat} | {clip} | {vel} | {tracking} | {contact_mismatch} |".format(
                seed=item["seed"],
                samples=item["samples"],
                termination_reason=item["termination_reason"],
                vx=fmt(item["mean_vx"]),
                track=fmt(item["track_ratio"]),
                vy=fmt(item["vy_abs_p95"]),
                height=fmt(item["base_height_min"]),
                sat=fmt(item["action_saturation_pct"]),
                clip=fmt(item["reference_target_clip_p95"]),
                vel=fmt(item["sent_target_velocity_p95"]),
                tracking=fmt(item["joint_tracking_p95"]),
                contact_mismatch=fmt(item["reference_contact_mismatch_pct"]),
            )
        )
    lines.extend(
        [
            "",
            "## Per Joint",
            "",
            "| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for item in payload.get("per_joint", []):
        lines.append(
            "| {joint} | {sat} | {clip} | {vel} | {tracking} |".format(
                joint=item["joint"],
                sat=fmt(item["action_saturation_pct"]),
                clip=fmt(item["reference_target_clip_p95_rad"]),
                vel=fmt(item["sent_target_velocity_p95_rad_s"]),
                tracking=fmt(item["joint_tracking_p95_rad"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This rollout replaces the ONNX policy with reference-derived actions.",
            "- It still respects action scale and the motor target rate limiter.",
            "- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.",
            "- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.",
            "- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.",
            "- A pass would show that the matched reference is dynamically trackable in the sim contract.",
            "- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--reference-motion-override", default=str(DEFAULT_REFERENCE))
    parser.add_argument(
        "--use-playground-reference",
        action="store_true",
        help=(
            "Do not apply the local reference-motion override; use the "
            "Playground polynomial_coefficients.pkl in place."
        ),
    )
    parser.add_argument("--reward-overrides-json", default=str(DEFAULT_REWARD_OVERRIDES))
    parser.add_argument("--reward-overrides-phase", default="phase1_interpolated_reference_seed_x004")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--command-y", type=float, default=0.0)
    parser.add_argument("--command-yaw", type=float, default=0.0)
    parser.add_argument(
        "--reference-target-mode",
        choices=[
            "raw",
            "cycle_projected",
            "contact_gated_projected",
            "contact_synchronized_projected",
        ],
        default="raw",
    )
    parser.add_argument(
        "--contact-gate-swing-scale",
        type=float,
        default=0.35,
        help=(
            "For contact_gated_projected mode, scale a leg's target delta by this "
            "factor when the reference expects that foot off the floor but the "
            "simulated foot is still in contact."
        ),
    )
    parser.add_argument(
        "--first-reference-phase",
        type=int,
        default=1,
        help="Reference phase used on the first simulated step.",
    )
    parser.add_argument("--duration-s", type=float, default=5.0)
    parser.add_argument("--seeds", default="0-7")
    parser.add_argument("--min-track-ratio-mean", type=float, default=0.25)
    parser.add_argument("--trace-dir", default=None)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    if args.use_playground_reference:
        args.reference_motion_override = None
    payload = run_rollout(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
