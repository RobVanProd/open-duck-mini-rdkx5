#!/usr/bin/env python3
"""Probe a simple CoM-style weight-transfer controller in Open Duck sim.

This is an offline target-source diagnostic. It does not train, deploy, SSH, or
touch the robot. The controller is intentionally small and interpretable: it
uses base-y, optional stance-foot-relative lateral position, local lateral
velocity, pitch/height gates, and contact state to gate load, swing, and
forward-push phases.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import math
from pathlib import Path
import random
from typing import Any

import numpy as np

from closed_loop_sim_eval import quat_wxyz_to_pitch, temporary_cwd
from eval_reference_motion_rollout import fmt, parse_int_list
from probe_closed_loop_weight_transfer_teacher import label_float, parse_float_list
from search_low_command_target_primitives import policy_observation_list, summarize_records


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "COM_WEIGHT_TRANSFER_CONTROLLER_PROBE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "com_weight_transfer_controller_probe.json"
DEFAULT_TRACE_DIR = ROOT / "outputs" / "analysis" / "com_weight_transfer_controller_probe_traces"


@dataclass
class Controller:
    label: str
    lateral_reference: str
    period_s: float
    load_fraction: float
    unweight_fraction: float
    lateral_offset_m: float
    base_y_gate_m: float
    lateral_velocity_gate_m_s: float
    kp_y: float
    kd_y: float
    kp_vx: float
    feedforward_push_rad: float
    stance_push_limit_rad: float
    swing_knee_rad: float
    swing_ankle_rad: float
    swing_hip_reach_rad: float
    stance_retract_scale: float
    pitch_gate_rad: float
    pitch_target_rad: float
    pitch_damping: float
    clearance_gate_m: float


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def parse_lateral_reference_modes(value: str) -> list[str]:
    aliases = {
        "world": "world",
        "base": "world",
        "stance": "stance_foot_relative",
        "stance_foot": "stance_foot_relative",
        "stance_foot_relative": "stance_foot_relative",
    }
    rows: list[str] = []
    for raw in value.split(","):
        key = raw.strip().lower()
        if not key:
            continue
        if key not in aliases:
            raise ValueError(f"unknown lateral reference mode: {raw}")
        rows.append(aliases[key])
    return rows or ["world"]


def controller_grid(args: argparse.Namespace) -> list[Controller]:
    rows: list[Controller] = []
    for lateral_reference in parse_lateral_reference_modes(args.lateral_reference_modes):
        for period_s in parse_float_list(args.periods):
            for load_fraction in parse_float_list(args.load_fractions):
                for unweight_fraction in parse_float_list(args.unweight_fractions):
                    for lateral_offset in parse_float_list(args.lateral_offsets):
                        for base_y_gate in parse_float_list(args.base_y_gates):
                            for lateral_velocity_gate in parse_float_list(
                                args.lateral_velocity_gates
                            ):
                                for kp_y in parse_float_list(args.kp_y_values):
                                    for kd_y in parse_float_list(args.kd_y_values):
                                        for kp_vx in parse_float_list(args.kp_vx_values):
                                            for feedforward_push in parse_float_list(
                                                args.feedforward_pushes
                                            ):
                                                for swing_knee in parse_float_list(args.swing_knees):
                                                    for swing_ankle in parse_float_list(
                                                        args.swing_ankles
                                                    ):
                                                        for swing_hip_reach in parse_float_list(
                                                            args.swing_hip_reaches
                                                        ):
                                                            for stance_retract_scale in parse_float_list(
                                                                args.stance_retract_scales
                                                            ):
                                                                for pitch_target in parse_float_list(
                                                                    args.pitch_targets
                                                                ):
                                                                    for pitch_damping in parse_float_list(
                                                                        args.pitch_dampings
                                                                    ):
                                                                        label = (
                                                                            f"com_lr{lateral_reference}"
                                                                            f"_p{label_float(period_s)}"
                                                                            f"_lf{label_float(load_fraction)}"
                                                                            f"_uf{label_float(unweight_fraction)}"
                                                                            f"_lo{label_float(lateral_offset)}"
                                                                            f"_byg{label_float(base_y_gate)}"
                                                                            f"_lvg{label_float(lateral_velocity_gate)}"
                                                                            f"_kpy{label_float(kp_y)}"
                                                                            f"_kdy{label_float(kd_y)}"
                                                                            f"_kpvx{label_float(kp_vx)}"
                                                                            f"_ffp{label_float(feedforward_push)}"
                                                                            f"_sk{label_float(swing_knee)}"
                                                                            f"_sa{label_float(swing_ankle)}"
                                                                            f"_shr{label_float(swing_hip_reach)}"
                                                                            f"_srs{label_float(stance_retract_scale)}"
                                                                            f"_pt{label_float(pitch_target)}"
                                                                            f"_pd{label_float(pitch_damping)}"
                                                                        )
                                                                        rows.append(
                                                                            Controller(
                                                                                label=label,
                                                                                lateral_reference=lateral_reference,
                                                                                period_s=period_s,
                                                                                load_fraction=load_fraction,
                                                                                unweight_fraction=unweight_fraction,
                                                                                lateral_offset_m=lateral_offset,
                                                                                base_y_gate_m=base_y_gate,
                                                                                lateral_velocity_gate_m_s=lateral_velocity_gate,
                                                                                kp_y=kp_y,
                                                                                kd_y=kd_y,
                                                                                kp_vx=kp_vx,
                                                                                feedforward_push_rad=feedforward_push,
                                                                                stance_push_limit_rad=args.stance_push_limit,
                                                                                swing_knee_rad=swing_knee,
                                                                                swing_ankle_rad=swing_ankle,
                                                                                swing_hip_reach_rad=swing_hip_reach,
                                                                                stance_retract_scale=stance_retract_scale,
                                                                                pitch_gate_rad=args.pitch_gate,
                                                                                pitch_target_rad=pitch_target,
                                                                                pitch_damping=pitch_damping,
                                                                                clearance_gate_m=args.clearance_gate,
                                                                            )
                                                                        )
    if args.shuffle_candidates:
        random.Random(args.grid_seed).shuffle(rows)
    return rows[: args.max_candidates]


def pct(count: int, total: int) -> float:
    return float(count / total * 100.0) if total else 0.0


def summarize_phase_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    phases = Counter(record.get("controller_phase", "unknown") for record in records)
    return {
        "phase_pct": {key: pct(value, total) for key, value in sorted(phases.items())},
        "load_stance_ready_pct": pct(
            sum(1 for record in records if record.get("load_stance_ready")), total
        ),
        "unweight_swing_ready_pct": pct(
            sum(1 for record in records if record.get("unweight_swing_ready")), total
        ),
        "push_allowed_pct": pct(
            sum(1 for record in records if record.get("push_allowed")), total
        ),
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    import jax
    import jax.numpy as jp
    from mujoco_playground._src import mjx_env
    from mujoco_playground._src.collision import geoms_colliding

    import sys

    playground_path = Path(args.playground_path).resolve()
    if str(playground_path) not in sys.path:
        sys.path.insert(0, str(playground_path))
    from playground.open_duck_mini_v2 import joystick

    command = jp.asarray([args.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    trace_root = Path(args.trace_dir)
    if not trace_root.is_absolute():
        trace_root = ROOT / trace_root
    trace_root.mkdir(parents=True, exist_ok=True)
    controllers = controller_grid(args)
    seeds = parse_int_list(args.seeds)
    results = []

    with temporary_cwd(playground_path):
        env_config = joystick.default_config()
        env = joystick.Joystick(
            task=args.task,
            config=env_config,
            config_overrides={
                "push_config.enable": False,
                "lin_vel_x": [args.command_x, args.command_x],
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
            },
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

        def pitch_from_quat_wxyz(quat):
            w, x, y, z = quat
            return jp.arcsin(jp.clip(2.0 * (w * y - z * x), -1.0, 1.0))

        def controller_target(
            default_actuator,
            tick,
            use_stance_foot_relative,
            period_s,
            load_fraction,
            unweight_fraction,
            lateral_offset_m,
            base_y_gate_m,
            lateral_velocity_gate_m_s,
            kp_y,
            kd_y,
            kp_vx,
            feedforward_push_rad,
            stance_push_limit_rad,
            swing_knee_rad,
            swing_ankle_rad,
            swing_hip_reach_rad,
            stance_retract_scale,
            pitch_gate_rad,
            pitch_target_rad,
            pitch_damping,
            clearance_gate_m,
            local_vx,
            local_vy,
            body_pitch,
            base_y,
            base_height,
            contact,
            foot_site_pos,
        ):
            phase01 = jp.mod((tick * env.dt) / period_s, 1.0)
            load_end = load_fraction
            unweight_end = jp.minimum(load_fraction + unweight_fraction, 0.95)
            in_load = phase01 < load_end
            in_unweight = (phase01 >= load_end) & (phase01 < unweight_end)
            in_push = phase01 >= unweight_end

            left_stance = jp.where(phase01 < 0.5, 1.0, 0.0)
            right_stance = 1.0 - left_stance
            left_swing = 1.0 - left_stance
            right_swing = 1.0 - right_stance
            stance_side = left_stance - right_stance
            left_contact = contact[0].astype(jp.float32)
            right_contact = contact[1].astype(jp.float32)
            stance_contact = left_stance * left_contact + right_stance * right_contact
            swing_contact = left_swing * left_contact + right_swing * right_contact
            foot_site_y = foot_site_pos[:, 1]
            foot_site_z = foot_site_pos[:, 2]
            stance_foot_y = left_stance * foot_site_y[0] + right_stance * foot_site_y[1]
            swing_foot_z = left_swing * foot_site_z[0] + right_swing * foot_site_z[1]

            base_y_relative_to_stance = base_y - stance_foot_y
            controlled_base_y = jp.where(
                use_stance_foot_relative > 0.5,
                base_y_relative_to_stance,
                base_y,
            )
            desired_base_y = stance_side * lateral_offset_m
            lateral_error = desired_base_y - controlled_base_y
            lateral_ok = jp.abs(local_vy) <= lateral_velocity_gate_m_s
            base_y_ok = jp.abs(lateral_error) <= base_y_gate_m
            pitch_ok = jp.abs(body_pitch - pitch_target_rad) <= pitch_gate_rad
            height_ok = base_height >= args.min_height_m
            stance_ok = stance_contact > 0.5
            load_ready = base_y_ok & lateral_ok & stance_ok & height_ok & pitch_ok
            swing_clear = (swing_contact < 0.5) | (swing_foot_z >= clearance_gate_m)
            unweight_ready = load_ready & swing_clear
            push_allowed = unweight_ready & in_push

            roll_cmd = jp.clip(kp_y * lateral_error - kd_y * local_vy, -0.08, 0.08)
            forward_error = command[0] - local_vx
            raw_push = jp.clip(
                kp_vx * forward_error + feedforward_push_rad,
                -stance_push_limit_rad,
                stance_push_limit_rad,
            )
            stance_push = jp.where(push_allowed, raw_push, 0.0)
            swing_lift = jp.where(in_unweight | in_push, swing_knee_rad, 0.0)
            swing_ankle = jp.where(in_unweight | in_push, swing_ankle_rad, 0.0)
            swing_reach = jp.where(in_unweight | in_push, swing_hip_reach_rad, 0.0)
            stance_retract = -stance_retract_scale * swing_reach
            pitch_error = body_pitch - pitch_target_rad
            pitch_ankle = jp.clip(-pitch_damping * pitch_error * 0.03, -0.04, 0.04)

            target = jp.asarray(default_actuator)
            target = target.at[1].set(default_actuator[1] + roll_cmd)
            target = target.at[2].set(
                default_actuator[2]
                + left_stance * (stance_push + stance_retract)
                + left_swing * swing_reach
            )
            target = target.at[3].set(default_actuator[3] + left_swing * swing_lift)
            target = target.at[4].set(default_actuator[4] + left_swing * swing_ankle + pitch_ankle)
            target = target.at[10].set(default_actuator[10] - roll_cmd)
            target = target.at[11].set(
                default_actuator[11]
                + right_stance * (stance_push + stance_retract)
                + right_swing * swing_reach
            )
            target = target.at[12].set(default_actuator[12] + right_swing * swing_lift)
            target = target.at[13].set(default_actuator[13] + right_swing * swing_ankle + pitch_ankle)
            phase_id = jp.where(in_load, 0, jp.where(in_unweight, 1, 2))
            return (
                target,
                phase_id,
                load_ready,
                unweight_ready,
                push_allowed,
                stance_foot_y,
                base_y_relative_to_stance,
                controlled_base_y,
                lateral_error,
            )

        def step_controller(
            state,
            use_stance_foot_relative,
            period_s,
            load_fraction,
            unweight_fraction,
            lateral_offset_m,
            base_y_gate_m,
            lateral_velocity_gate_m_s,
            kp_y,
            kd_y,
            kp_vx,
            feedforward_push_rad,
            stance_push_limit_rad,
            swing_knee_rad,
            swing_ankle_rad,
            swing_hip_reach_rad,
            stance_retract_scale,
            pitch_gate_rad,
            pitch_target_rad,
            pitch_damping,
            clearance_gate_m,
        ):
            state.info["command"] = command
            tick = state.info["step"]
            contact_in = state.info["last_contact"]
            qpos = state.data.qpos
            base_addr = env._floating_base_qpos_addr
            quat = qpos[base_addr + 3 : base_addr + 7]
            local_linvel = env.get_local_linvel(state.data)
            foot_site_pos = state.data.site_xpos[env._feet_site_id]
            (
                target,
                phase_id,
                load_ready,
                unweight_ready,
                push_allowed,
                stance_foot_y,
                base_y_relative_to_stance,
                controlled_base_y,
                lateral_error,
            ) = controller_target(
                env._default_actuator,
                tick,
                use_stance_foot_relative,
                period_s,
                load_fraction,
                unweight_fraction,
                lateral_offset_m,
                base_y_gate_m,
                lateral_velocity_gate_m_s,
                kp_y,
                kd_y,
                kp_vx,
                feedforward_push_rad,
                stance_push_limit_rad,
                swing_knee_rad,
                swing_ankle_rad,
                swing_hip_reach_rad,
                stance_retract_scale,
                pitch_gate_rad,
                pitch_target_rad,
                pitch_damping,
                clearance_gate_m,
                local_linvel[0],
                local_linvel[1],
                pitch_from_quat_wxyz(quat),
                qpos[base_addr + 1],
                qpos[base_addr + 2],
                contact_in,
                foot_site_pos,
            )
            action = jp.clip((target - env._default_actuator) / env._config.action_scale, -1.0, 1.0)
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
            env._update_command_window_progress(state.info, data)
            obs = env._get_obs(data, state.info, contact)
            done = env._get_termination(data)
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
            reward = jp.clip(
                sum(rewards.values()) * env.dt,
                env._config.reward_config.reward_clip_min,
                env._config.reward_config.reward_clip_max,
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
            state.metrics["diagnostic/command_progress_ratio"] = state.info[
                "command_progress_ratio"
            ]
            done = done.astype(reward.dtype)
            return (
                state.replace(data=data, obs=obs, reward=reward, done=done),
                action,
                target,
                pre_rate_limit,
                sent_target,
                phase_id,
                load_ready,
                unweight_ready,
                push_allowed,
                stance_foot_y,
                base_y_relative_to_stance,
                controlled_base_y,
                lateral_error,
            )

        refresh_obs_jit = jax.jit(refresh_obs)
        step_controller_jit = jax.jit(step_controller)
        sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))
        phase_names = {0: "LOAD_STANCE", 1: "UNWEIGHT_SWING", 2: "PUSH_FORWARD"}

        for controller in controllers:
            controller_rows = []
            for seed in seeds:
                state = env.reset(jax.random.PRNGKey(seed))
                state.info["command"] = command
                state = refresh_obs_jit(state)
                records = []
                for tick in range(sim_steps):
                    (
                        state,
                        action,
                        target,
                        pre_rate,
                        sent_target,
                        phase_id,
                        load_ready,
                        unweight_ready,
                        push_allowed,
                        stance_foot_y,
                        base_y_relative_to_stance,
                        controlled_base_y,
                        lateral_error,
                    ) = step_controller_jit(
                        state,
                        1.0 if controller.lateral_reference == "stance_foot_relative" else 0.0,
                        controller.period_s,
                        controller.load_fraction,
                        controller.unweight_fraction,
                        controller.lateral_offset_m,
                        controller.base_y_gate_m,
                        controller.lateral_velocity_gate_m_s,
                        controller.kp_y,
                        controller.kd_y,
                        controller.kp_vx,
                        controller.feedforward_push_rad,
                        controller.stance_push_limit_rad,
                        controller.swing_knee_rad,
                        controller.swing_ankle_rad,
                        controller.swing_hip_reach_rad,
                        controller.stance_retract_scale,
                        controller.pitch_gate_rad,
                        controller.pitch_target_rad,
                        controller.pitch_damping,
                        controller.clearance_gate_m,
                    )
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
                    foot_site_pos = np.asarray(
                        jax.device_get(state.data.site_xpos[env._feet_site_id]),
                        dtype=float,
                    )
                    contacts = np.asarray(jax.device_get(state.info["last_contact"]), dtype=bool)
                    obs_host = jax.device_get(state.obs)
                    done = bool(np.asarray(jax.device_get(state.done)))
                    phase_id_host = int(np.asarray(jax.device_get(phase_id)))
                    record = {
                        "tick": tick,
                        "time_s": tick * float(env.dt),
                        "seed": seed,
                        "mode": controller.label,
                        "controller_phase": phase_names.get(phase_id_host, "UNKNOWN"),
                        "load_stance_ready": bool(np.asarray(jax.device_get(load_ready))),
                        "unweight_swing_ready": bool(np.asarray(jax.device_get(unweight_ready))),
                        "push_allowed": bool(np.asarray(jax.device_get(push_allowed))),
                        "lateral_reference": controller.lateral_reference,
                        "command": [args.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        "action": np.asarray(jax.device_get(action), dtype=float).tolist(),
                        "reference_target_rad": np.asarray(
                            jax.device_get(target), dtype=float
                        ).tolist(),
                        "target_pre_rate_limit_rad": np.asarray(
                            jax.device_get(pre_rate), dtype=float
                        ).tolist(),
                        "sent_target_rad": np.asarray(
                            jax.device_get(sent_target), dtype=float
                        ).tolist(),
                        "actual_position_rad": actual.tolist(),
                        "body_pitch_rad": quat_wxyz_to_pitch(quat),
                        "base_x_m": float(qpos[base_addr]),
                        "base_y_m": float(qpos[base_addr + 1]),
                        "stance_foot_y_m": float(np.asarray(jax.device_get(stance_foot_y))),
                        "base_y_relative_to_stance_m": float(
                            np.asarray(jax.device_get(base_y_relative_to_stance))
                        ),
                        "lateral_control_y_m": float(np.asarray(jax.device_get(controlled_base_y))),
                        "lateral_error_m": float(np.asarray(jax.device_get(lateral_error))),
                        "base_height_m": float(qpos[base_addr + 2]),
                        "foot_site_z_m": foot_site_pos[:, 2].astype(float).tolist(),
                        "local_linvel_m_s": local_linvel.astype(float).tolist(),
                        "foot_contacts": contacts.astype(int).tolist(),
                        "observation": policy_observation_list(obs_host),
                        "reward": float(np.asarray(jax.device_get(state.reward))),
                        "done": done,
                    }
                    records.append(record)
                    if done:
                        break
                trace_path = trace_root / controller.label / f"seed_{seed:03d}.jsonl"
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                trace_path.write_text("".join(json.dumps(record) + "\n" for record in records))
                summary = summarize_records(records, args.command_x)
                summary.update(summarize_phase_records(records))
                summary.update({"seed": seed, "trace": str(trace_path)})
                controller_rows.append(summary)
            mean_vx = [row["mean_vx_m_s"] for row in controller_rows if finite(row["mean_vx_m_s"])]
            falls = sum(
                1 for row in controller_rows if row["termination_reason"] != "duration_complete"
            )
            push_allowed = [
                row["push_allowed_pct"] for row in controller_rows if finite(row["push_allowed_pct"])
            ]
            results.append(
                {
                    "controller": controller.__dict__,
                    "runs": controller_rows,
                    "aggregate": {
                        "runs": len(controller_rows),
                        "falls": falls,
                        "duration_complete": len(controller_rows) - falls,
                        "mean_vx_m_s": float(np.mean(mean_vx)) if mean_vx else None,
                        "max_mean_vx_m_s": float(np.max(mean_vx)) if mean_vx else None,
                        "mean_push_allowed_pct": (
                            float(np.mean(push_allowed)) if push_allowed else None
                        ),
                    },
                }
            )

    ranked = sorted(
        results,
        key=lambda row: (
            row["aggregate"]["duration_complete"],
            row["aggregate"]["mean_vx_m_s"] or -999.0,
            row["aggregate"]["mean_push_allowed_pct"] or -999.0,
            -row["aggregate"]["falls"],
        ),
        reverse=True,
    )
    return {
        "status": "PASS_COM_CONTROLLER_PROBE_RAN" if results else "HOLD_NO_CONTROLLER_CANDIDATES",
        "command_x": args.command_x,
        "duration_s": args.duration_s,
        "seeds": seeds,
        "trace_dir": str(trace_root),
        "candidate_count": len(controllers),
        "limitations": [
            "controller uses base_y or stance-foot-relative base_y as lateral CoM proxies",
            "body_roll and stance-foot-relative sagittal position are not yet modeled",
            "stance-foot-relative mode uses contact phase's stance foot site y, not a true CoM projection",
        ],
        "results": ranked,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# CoM Weight-Transfer Controller Probe",
        "",
        f"status: `{payload['status']}`",
        f"command_x: `{payload['command_x']}`",
        f"duration_s: `{payload['duration_s']}`",
        f"seeds: `{payload['seeds']}`",
        f"candidate_count: `{payload['candidate_count']}`",
        "",
        "## Limitations",
        "",
    ]
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Top Controller Candidates",
            "",
            "| controller | runs | falls | duration_complete | mean_vx | max_seed_vx | push_allowed_mean |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in payload["results"][:20]:
        controller = item["controller"]
        aggregate = item["aggregate"]
        lines.append(
            "| {label} | {runs} | {falls} | {complete} | {mean_vx} | {max_vx} | {push_allowed} |".format(
                label=controller["label"],
                runs=aggregate["runs"],
                falls=aggregate["falls"],
                complete=aggregate["duration_complete"],
                mean_vx=fmt(aggregate["mean_vx_m_s"]),
                max_vx=fmt(aggregate["max_mean_vx_m_s"]),
                push_allowed=fmt(aggregate["mean_push_allowed_pct"], 2),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a closed-loop controller probe, not policy training.",
            "- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.",
            "- A useful controller still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.",
            "- A hold should identify which state transition failed before any training branch starts.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--duration-s", type=float, default=3.0)
    parser.add_argument("--seeds", default="0")
    parser.add_argument("--periods", default="0.56,0.64")
    parser.add_argument(
        "--lateral-reference-modes",
        default="world",
        help="Comma-separated: world, stance, or stance_foot_relative.",
    )
    parser.add_argument("--load-fractions", default="0.35")
    parser.add_argument("--unweight-fractions", default="0.25")
    parser.add_argument("--lateral-offsets", default="0.01,0.02")
    parser.add_argument("--base-y-gates", default="0.02")
    parser.add_argument("--lateral-velocity-gates", default="0.08")
    parser.add_argument("--kp-y-values", default="2.0,3.0")
    parser.add_argument("--kd-y-values", default="0.5,1.0")
    parser.add_argument("--kp-vx-values", default="0.5,1.0")
    parser.add_argument("--feedforward-pushes", default="0.005,0.01")
    parser.add_argument("--stance-push-limit", type=float, default=0.04)
    parser.add_argument("--swing-knees", default="0.08")
    parser.add_argument("--swing-ankles", default="0.0")
    parser.add_argument("--swing-hip-reaches", default="0.06")
    parser.add_argument("--stance-retract-scales", default="0.5")
    parser.add_argument("--pitch-gate", type=float, default=0.35)
    parser.add_argument("--pitch-targets", default="0.0")
    parser.add_argument("--pitch-dampings", default="1.0")
    parser.add_argument("--clearance-gate", type=float, default=0.008)
    parser.add_argument("--min-height-m", type=float, default=0.145)
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument("--shuffle-candidates", action="store_true")
    parser.add_argument("--grid-seed", type=int, default=0)
    parser.add_argument("--trace-dir", default=str(DEFAULT_TRACE_DIR))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = run_probe(args)
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
