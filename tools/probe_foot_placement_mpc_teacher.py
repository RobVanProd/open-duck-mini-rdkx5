#!/usr/bin/env python3
"""Probe a finite-horizon foot-placement weight-transfer teacher.

This is an offline target-source diagnostic. It does not train, deploy, SSH, or
touch the robot. The teacher is intentionally small: it chooses stance side,
lateral body placement, swing-foot reach, and stance push timing from sim state,
then emits JSONL traces that can be scored by score_target_candidates_objective.py.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from itertools import product
import json
import math
from pathlib import Path
import random
from typing import Any

import numpy as np

from closed_loop_sim_eval import (
    quat_wxyz_to_pitch,
    quat_wxyz_to_roll,
    quat_wxyz_to_yaw,
    temporary_cwd,
)
from eval_reference_motion_rollout import fmt, parse_int_list
from probe_closed_loop_weight_transfer_teacher import label_float, parse_float_list
from search_low_command_target_primitives import policy_observation_list, summarize_records


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "FOOT_PLACEMENT_MPC_TEACHER_PROBE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "foot_placement_mpc_teacher_probe.json"
DEFAULT_TRACE_DIR = ROOT / "outputs" / "analysis" / "foot_placement_mpc_teacher_probe_traces"


@dataclass
class Candidate:
    label: str
    initial_stance_side: float
    period_s: float
    load_s: float
    unweight_s: float
    push_s: float
    load_shift_y_m: float
    base_y_gate_m: float
    lateral_velocity_gate_m_s: float
    foot_place_x_m: float
    foot_place_gain: float
    swing_min_advance_m: float
    swing_knee_rad: float
    swing_ankle_rad: float
    swing_reach_limit_rad: float
    stance_retract_rad: float
    stance_hip_push_rad: float
    stance_knee_push_rad: float
    stance_ankle_push_rad: float
    stance_base_x_offset_m: float
    sagittal_gain: float
    vx_gain: float
    propulsion_limit_rad: float
    propulsion_pattern: float
    teacher_target_velocity_limit_rad_s: float
    push_lateral_soft_gate_m_s: float
    push_yaw_soft_gate_rad: float
    push_min_scale: float
    yaw_gain: float
    yaw_vy_gain: float
    roll_gain: float
    vy_damping_gain: float
    body_y_gain: float
    pitch_target_rad: float
    pitch_damping: float
    clearance_gate_m: float
    min_height_m: float


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def pct(count: int, total: int) -> float:
    return float(count / total * 100.0) if total else 0.0


def candidate_grid(args: argparse.Namespace) -> list[Candidate]:
    rows: list[Candidate] = []
    fields = [
        ("period_s", parse_float_list(args.periods)),
        ("load_shift_y", parse_float_list(args.load_shift_y)),
        ("foot_place_x", parse_float_list(args.foot_place_x)),
        ("foot_place_gain", parse_float_list(args.foot_place_gains)),
        ("stance_hip_push", parse_float_list(args.stance_hip_pushes)),
        ("stance_knee_push", parse_float_list(args.stance_knee_pushes)),
        ("stance_ankle_push", parse_float_list(args.stance_ankle_pushes)),
        ("roll_gain", parse_float_list(args.roll_gains)),
        ("vy_damping_gain", parse_float_list(args.vy_damping_gains)),
        ("body_y_gain", parse_float_list(args.body_y_gains)),
        ("push_lateral_soft_gate", parse_float_list(args.push_lateral_soft_gates)),
        ("push_yaw_soft_gate", parse_float_list(args.push_yaw_soft_gates)),
        ("push_min_scale", parse_float_list(args.push_min_scales)),
        ("yaw_gain", parse_float_list(args.yaw_gains)),
        ("yaw_vy_gain", parse_float_list(args.yaw_vy_gains)),
        ("stance_base_x_offset", parse_float_list(args.stance_base_x_offsets)),
        ("sagittal_gain", parse_float_list(args.sagittal_gains)),
        ("vx_gain", parse_float_list(args.vx_gains)),
        ("propulsion_limit", parse_float_list(args.propulsion_limits)),
        ("propulsion_pattern", parse_float_list(args.propulsion_patterns)),
        ("teacher_target_velocity_limit", parse_float_list(args.teacher_target_velocity_limits)),
        ("swing_min_advance", parse_float_list(args.swing_min_advance)),
        ("initial_stance_side", parse_float_list(args.initial_stance_sides)),
    ]
    names = [name for name, _values in fields]
    for values in product(*(values for _name, values in fields)):
        item = dict(zip(names, values, strict=True))
        label = (
            f"fpm_is{label_float(item['initial_stance_side'])}"
            f"_p{label_float(item['period_s'])}"
            f"_ly{label_float(item['load_shift_y'])}"
            f"_fpx{label_float(item['foot_place_x'])}"
            f"_fpg{label_float(item['foot_place_gain'])}"
            f"_sma{label_float(item['swing_min_advance'])}"
            f"_shp{label_float(item['stance_hip_push'])}"
            f"_skp{label_float(item['stance_knee_push'])}"
            f"_sap{label_float(item['stance_ankle_push'])}"
            f"_sbx{label_float(item['stance_base_x_offset'])}"
            f"_sg{label_float(item['sagittal_gain'])}"
            f"_vxg{label_float(item['vx_gain'])}"
            f"_pl{label_float(item['propulsion_limit'])}"
            f"_pp{label_float(item['propulsion_pattern'])}"
            f"_tvl{label_float(item['teacher_target_velocity_limit'])}"
            f"_plg{label_float(item['push_lateral_soft_gate'])}"
            f"_pyg{label_float(item['push_yaw_soft_gate'])}"
            f"_pms{label_float(item['push_min_scale'])}"
            f"_yg{label_float(item['yaw_gain'])}"
            f"_yvg{label_float(item['yaw_vy_gain'])}"
            f"_rg{label_float(item['roll_gain'])}"
            f"_vyg{label_float(item['vy_damping_gain'])}"
            f"_byg{label_float(item['body_y_gain'])}"
        )
        rows.append(
            Candidate(
                label=label,
                initial_stance_side=item["initial_stance_side"],
                period_s=item["period_s"],
                load_s=args.load_s,
                unweight_s=args.unweight_s,
                push_s=args.push_s,
                load_shift_y_m=item["load_shift_y"],
                base_y_gate_m=args.base_y_gate,
                lateral_velocity_gate_m_s=args.lateral_velocity_gate,
                foot_place_x_m=item["foot_place_x"],
                foot_place_gain=item["foot_place_gain"],
                swing_min_advance_m=item["swing_min_advance"],
                swing_knee_rad=args.swing_knee,
                swing_ankle_rad=args.swing_ankle,
                swing_reach_limit_rad=args.swing_reach_limit,
                stance_retract_rad=args.stance_retract,
                stance_hip_push_rad=item["stance_hip_push"],
                stance_knee_push_rad=item["stance_knee_push"],
                stance_ankle_push_rad=item["stance_ankle_push"],
                stance_base_x_offset_m=item["stance_base_x_offset"],
                sagittal_gain=item["sagittal_gain"],
                vx_gain=item["vx_gain"],
                propulsion_limit_rad=item["propulsion_limit"],
                propulsion_pattern=item["propulsion_pattern"],
                teacher_target_velocity_limit_rad_s=item["teacher_target_velocity_limit"],
                push_lateral_soft_gate_m_s=item["push_lateral_soft_gate"],
                push_yaw_soft_gate_rad=item["push_yaw_soft_gate"],
                push_min_scale=item["push_min_scale"],
                yaw_gain=item["yaw_gain"],
                yaw_vy_gain=item["yaw_vy_gain"],
                roll_gain=item["roll_gain"],
                vy_damping_gain=item["vy_damping_gain"],
                body_y_gain=item["body_y_gain"],
                pitch_target_rad=args.pitch_target,
                pitch_damping=args.pitch_damping,
                clearance_gate_m=args.clearance_gate,
                min_height_m=args.min_height,
            )
        )
    if args.shuffle_candidates:
        random.Random(args.grid_seed).shuffle(rows)
    return rows[: args.max_candidates]

def summarize_controller_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    phases = Counter(record.get("controller_phase", "unknown") for record in records)
    return {
        "phase_pct": {key: pct(value, total) for key, value in sorted(phases.items())},
        "load_ready_pct": pct(sum(1 for record in records if record.get("load_ready")), total),
        "swing_ready_pct": pct(sum(1 for record in records if record.get("swing_ready")), total),
        "push_allowed_pct": pct(
            sum(1 for record in records if record.get("push_allowed")), total
        ),
        "switch_ready_pct": pct(sum(1 for record in records if record.get("switch_ready")), total),
        "state_transitions": int(records[-1].get("state_transitions", 0)) if records else 0,
        "forced_transitions": int(records[-1].get("forced_transitions", 0)) if records else 0,
        "recovery_holds": int(records[-1].get("recovery_holds", 0)) if records else 0,
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    if args.jax_platform != "auto":
        import os

        os.environ.setdefault("JAX_PLATFORM_NAME", args.jax_platform)
        os.environ.setdefault("JAX_PLATFORMS", args.jax_platform)

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

    candidates = candidate_grid(args)
    seeds = parse_int_list(args.seeds)
    results: list[dict[str, Any]] = []

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

        def yaw_from_quat_wxyz(quat):
            w, x, y, z = quat
            return jp.arctan2(
                2.0 * (w * z + x * y),
                1.0 - 2.0 * (y * y + z * z),
            )

        def wrap_angle(angle):
            return jp.arctan2(jp.sin(angle), jp.cos(angle))

        def teacher_target(
            default_actuator,
            phase_id,
            stance_side_in,
            load_shift_y_m,
            base_y_gate_m,
            lateral_velocity_gate_m_s,
            foot_place_x_m,
            foot_place_gain,
            swing_min_advance_m,
            swing_knee_rad,
            swing_ankle_rad,
            swing_reach_limit_rad,
            stance_retract_rad,
            stance_hip_push_rad,
            stance_knee_push_rad,
            stance_ankle_push_rad,
            stance_base_x_offset_m,
            sagittal_gain,
            vx_gain,
            propulsion_limit_rad,
            propulsion_pattern,
            push_lateral_soft_gate_m_s,
            push_yaw_soft_gate_rad,
            push_min_scale,
            yaw_gain,
            yaw_vy_gain,
            roll_gain,
            vy_damping_gain,
            body_y_gain,
            pitch_target_rad,
            pitch_damping,
            clearance_gate_m,
            min_height_m,
            local_vx,
            local_vy,
            body_pitch,
            body_yaw,
            yaw_target_rad,
            base_x,
            base_y,
            base_height,
            contact,
            foot_site_pos,
        ):
            left_stance = jp.where(stance_side_in >= 0.0, 1.0, 0.0)
            right_stance = 1.0 - left_stance
            left_swing = 1.0 - left_stance
            right_swing = 1.0 - right_stance
            stance_side = left_stance - right_stance
            left_contact = contact[0].astype(jp.float32)
            right_contact = contact[1].astype(jp.float32)
            stance_contact = left_stance * left_contact + right_stance * right_contact
            swing_contact = left_swing * left_contact + right_swing * right_contact

            foot_x = foot_site_pos[:, 0]
            foot_y = foot_site_pos[:, 1]
            foot_z = foot_site_pos[:, 2]
            stance_foot_x = left_stance * foot_x[0] + right_stance * foot_x[1]
            stance_foot_y = left_stance * foot_y[0] + right_stance * foot_y[1]
            swing_foot_x = left_swing * foot_x[0] + right_swing * foot_x[1]
            swing_foot_z = left_swing * foot_z[0] + right_swing * foot_z[1]

            if args.stance_relative_lateral:
                desired_base_y = stance_foot_y + stance_side * load_shift_y_m
            else:
                desired_base_y = stance_side * load_shift_y_m
            lateral_error = desired_base_y - base_y
            lateral_ready = jp.abs(lateral_error) <= base_y_gate_m
            velocity_ready = jp.abs(local_vy) <= lateral_velocity_gate_m_s
            pitch_ready = jp.abs(body_pitch - pitch_target_rad) <= args.pitch_gate
            height_ready = base_height >= min_height_m
            load_ready = (
                (stance_contact > 0.5)
                & lateral_ready
                & velocity_ready
                & pitch_ready
                & height_ready
            )
            swing_clear = (swing_contact < 0.5) | (swing_foot_z >= clearance_gate_m)
            swing_ready = load_ready & swing_clear
            in_load = phase_id == 0
            in_unweight = phase_id == 1
            in_push = phase_id == 2
            push_allowed = in_push & load_ready & velocity_ready & pitch_ready
            yaw_error = wrap_angle(body_yaw - yaw_target_rad)

            roll = jp.clip(
                roll_gain * lateral_error - vy_damping_gain * local_vy - body_y_gain * base_y,
                -args.roll_limit,
                args.roll_limit,
            )
            desired_swing_x = jp.maximum(
                stance_foot_x + foot_place_x_m,
                swing_foot_x + swing_min_advance_m,
            )
            desired_base_x = stance_foot_x + stance_base_x_offset_m
            sagittal_error = desired_base_x - base_x
            swing_x_error = desired_swing_x - swing_foot_x
            swing_reach = jp.clip(
                foot_place_gain * swing_x_error,
                -swing_reach_limit_rad,
                swing_reach_limit_rad,
            )
            swing_enabled = (in_unweight | in_push) & load_ready
            swing_lift = jp.where(swing_enabled, swing_knee_rad, 0.0)
            swing_ankle = jp.where(swing_enabled, swing_ankle_rad, 0.0)
            swing_reach = jp.where(swing_enabled, swing_reach, 0.0)
            stance_retract = jp.where(swing_enabled, stance_retract_rad, 0.0)
            push_scale = jp.where(push_allowed, 1.0, 0.0)
            forward_error = jp.clip(command[0] - local_vx, 0.0, 0.08)
            forward_scale = jp.clip(forward_error / 0.04, 0.25, 1.25)
            lateral_scale = jp.clip(
                1.0
                - jp.abs(local_vy) / jp.maximum(push_lateral_soft_gate_m_s, 1.0e-6),
                push_min_scale,
                1.0,
            )
            yaw_scale = jp.clip(
                1.0
                - jp.abs(yaw_error) / jp.maximum(push_yaw_soft_gate_rad, 1.0e-6),
                push_min_scale,
                1.0,
            )
            stability_scale = lateral_scale * yaw_scale
            forward_scale = forward_scale * stability_scale
            propulsion_raw = sagittal_gain * sagittal_error + vx_gain * forward_error
            propulsion_drive = jp.clip(
                propulsion_raw,
                -propulsion_limit_rad,
                propulsion_limit_rad,
            ) * push_scale * stability_scale
            patterned_drive = propulsion_pattern * propulsion_drive
            yaw_correction = jp.clip(
                -yaw_gain * yaw_error - yaw_vy_gain * local_vy,
                -args.yaw_limit,
                args.yaw_limit,
            )
            pitch_error = body_pitch - pitch_target_rad
            pitch_ankle = jp.clip(-pitch_damping * pitch_error * 0.03, -0.04, 0.04)

            target = jp.asarray(default_actuator)
            target = target.at[0].set(default_actuator[0] + yaw_correction)
            target = target.at[1].set(default_actuator[1] + roll)
            target = target.at[9].set(default_actuator[9] - yaw_correction)
            target = target.at[10].set(default_actuator[10] - roll)
            target = target.at[2].set(
                default_actuator[2]
                + left_swing * swing_reach
                - left_stance * stance_retract
                + left_stance * stance_hip_push_rad * push_scale * forward_scale
                + left_stance * patterned_drive
            )
            target = target.at[3].set(
                default_actuator[3]
                + left_swing * swing_lift
                + left_stance * stance_knee_push_rad * push_scale * forward_scale
                - left_stance * patterned_drive * 0.75
            )
            target = target.at[4].set(
                default_actuator[4]
                + left_swing * swing_ankle
                + left_stance * stance_ankle_push_rad * push_scale * forward_scale
                - left_stance * patterned_drive * 0.5
                + pitch_ankle
            )
            target = target.at[11].set(
                default_actuator[11]
                + right_swing * swing_reach
                - right_stance * stance_retract
                + right_stance * stance_hip_push_rad * push_scale * forward_scale
                + right_stance * patterned_drive
            )
            target = target.at[12].set(
                default_actuator[12]
                + right_swing * swing_lift
                + right_stance * stance_knee_push_rad * push_scale * forward_scale
                - right_stance * patterned_drive * 0.75
            )
            target = target.at[13].set(
                default_actuator[13]
                + right_swing * swing_ankle
                + right_stance * stance_ankle_push_rad * push_scale * forward_scale
                - right_stance * patterned_drive * 0.5
                + pitch_ankle
            )
            return (
                target,
                load_ready,
                swing_ready,
                push_allowed,
                lateral_error,
                stance_foot_x,
                stance_foot_y,
                desired_base_y,
                swing_foot_x,
                swing_x_error,
                desired_swing_x,
                forward_scale,
                stability_scale,
                lateral_scale,
                yaw_scale,
                yaw_correction,
                yaw_error,
                sagittal_error,
                propulsion_drive,
            )

        def step_teacher(
            state,
            phase_id,
            stance_side,
            load_shift_y_m,
            base_y_gate_m,
            lateral_velocity_gate_m_s,
            foot_place_x_m,
            foot_place_gain,
            swing_min_advance_m,
            swing_knee_rad,
            swing_ankle_rad,
            swing_reach_limit_rad,
            stance_retract_rad,
            stance_hip_push_rad,
            stance_knee_push_rad,
            stance_ankle_push_rad,
            stance_base_x_offset_m,
            sagittal_gain,
            vx_gain,
            propulsion_limit_rad,
            propulsion_pattern,
            teacher_target_velocity_limit_rad_s,
            push_lateral_soft_gate_m_s,
            push_yaw_soft_gate_rad,
            push_min_scale,
            yaw_gain,
            yaw_vy_gain,
            roll_gain,
            vy_damping_gain,
            body_y_gain,
            pitch_target_rad,
            pitch_damping,
            clearance_gate_m,
            min_height_m,
            yaw_target_rad,
        ):
            state.info["command"] = command
            contact_in = state.info["last_contact"]
            qpos = state.data.qpos
            base_addr = env._floating_base_qpos_addr
            quat = qpos[base_addr + 3 : base_addr + 7]
            local_linvel = env.get_local_linvel(state.data)
            foot_site_pos = state.data.site_xpos[env._feet_site_id]
            (
                target,
                load_ready,
                swing_ready,
                push_allowed,
                lateral_error,
                stance_foot_x,
                stance_foot_y,
                desired_base_y,
                swing_foot_x,
                swing_x_error,
                desired_swing_x,
                forward_scale,
                stability_scale,
                lateral_scale,
                yaw_scale,
                yaw_correction,
                yaw_error,
                sagittal_error,
                propulsion_drive,
            ) = teacher_target(
                env._default_actuator,
                phase_id,
                stance_side,
                load_shift_y_m,
                base_y_gate_m,
                lateral_velocity_gate_m_s,
                foot_place_x_m,
                foot_place_gain,
                swing_min_advance_m,
                swing_knee_rad,
                swing_ankle_rad,
                swing_reach_limit_rad,
                stance_retract_rad,
                stance_hip_push_rad,
                stance_knee_push_rad,
                stance_ankle_push_rad,
                stance_base_x_offset_m,
                sagittal_gain,
                vx_gain,
                propulsion_limit_rad,
                propulsion_pattern,
                push_lateral_soft_gate_m_s,
                push_yaw_soft_gate_rad,
                push_min_scale,
                yaw_gain,
                yaw_vy_gain,
                roll_gain,
                vy_damping_gain,
                body_y_gain,
                pitch_target_rad,
                pitch_damping,
                clearance_gate_m,
                min_height_m,
                local_linvel[0],
                local_linvel[1],
                pitch_from_quat_wxyz(quat),
                yaw_from_quat_wxyz(quat),
                yaw_target_rad,
                qpos[base_addr],
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
                prev_motor_targets
                - jp.where(
                    teacher_target_velocity_limit_rad_s > 0.0,
                    teacher_target_velocity_limit_rad_s,
                    env._config.max_motor_velocity,
                )
                * env.dt,
                prev_motor_targets
                + jp.where(
                    teacher_target_velocity_limit_rad_s > 0.0,
                    teacher_target_velocity_limit_rad_s,
                    env._config.max_motor_velocity,
                )
                * env.dt,
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
            return (
                state.replace(data=data, obs=obs, reward=reward, done=done.astype(reward.dtype)),
                action,
                target,
                pre_rate_limit,
                sent_target,
                load_ready,
                swing_ready,
                push_allowed,
                lateral_error,
                stance_foot_x,
                stance_foot_y,
                desired_base_y,
                swing_foot_x,
                swing_x_error,
                desired_swing_x,
                forward_scale,
                stability_scale,
                lateral_scale,
                yaw_scale,
                yaw_correction,
                yaw_error,
                sagittal_error,
                propulsion_drive,
            )

        refresh_obs_jit = jax.jit(refresh_obs)
        step_teacher_jit = jax.jit(step_teacher)
        sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))
        phase_names = {0: "LOAD_STANCE", 1: "UNWEIGHT_SWING", 2: "PUSH_FORWARD"}

        for candidate in candidates:
            candidate_rows = []
            for seed in seeds:
                state = env.reset(jax.random.PRNGKey(seed))
                init_qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
                base_addr = int(env._floating_base_qpos_addr)
                init_quat = init_qpos[base_addr + 3 : base_addr + 7]
                yaw_target_rad = quat_wxyz_to_yaw(init_quat)
                state.info["command"] = command
                state = refresh_obs_jit(state)
                records = []
                phase_id = 0
                phase_ticks = 0
                stance_side = 1.0 if candidate.initial_stance_side >= 0.0 else -1.0
                state_transitions = 0
                forced_transitions = 0
                recovery_holds = 0
                for tick in range(sim_steps):
                    (
                        state,
                        action,
                        target,
                        pre_rate,
                        sent_target,
                        load_ready,
                        swing_ready,
                        push_allowed,
                        lateral_error,
                        stance_foot_x,
                        stance_foot_y,
                        desired_base_y,
                        swing_foot_x,
                        swing_x_error,
                        desired_swing_x,
                        forward_scale,
                        stability_scale,
                        lateral_scale,
                        yaw_scale,
                        yaw_correction,
                        teacher_yaw_error,
                        sagittal_error,
                        propulsion_drive,
                    ) = step_teacher_jit(
                        state,
                        phase_id,
                        stance_side,
                        candidate.load_shift_y_m,
                        candidate.base_y_gate_m,
                        candidate.lateral_velocity_gate_m_s,
                        candidate.foot_place_x_m,
                        candidate.foot_place_gain,
                        candidate.swing_min_advance_m,
                        candidate.swing_knee_rad,
                        candidate.swing_ankle_rad,
                        candidate.swing_reach_limit_rad,
                        candidate.stance_retract_rad,
                        candidate.stance_hip_push_rad,
                        candidate.stance_knee_push_rad,
                        candidate.stance_ankle_push_rad,
                        candidate.stance_base_x_offset_m,
                        candidate.sagittal_gain,
                        candidate.vx_gain,
                        candidate.propulsion_limit_rad,
                        candidate.propulsion_pattern,
                        candidate.teacher_target_velocity_limit_rad_s,
                        candidate.push_lateral_soft_gate_m_s,
                        candidate.push_yaw_soft_gate_rad,
                        candidate.push_min_scale,
                        candidate.yaw_gain,
                        candidate.yaw_vy_gain,
                        candidate.roll_gain,
                        candidate.vy_damping_gain,
                        candidate.body_y_gain,
                        candidate.pitch_target_rad,
                        candidate.pitch_damping,
                        candidate.clearance_gate_m,
                        candidate.min_height_m,
                        yaw_target_rad,
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
                    body_yaw = quat_wxyz_to_yaw(quat)
                    body_yaw_error = math.atan2(
                        math.sin(body_yaw - yaw_target_rad),
                        math.cos(body_yaw - yaw_target_rad),
                    )
                    switch_ready = (
                        abs(float(local_linvel[1])) <= args.switch_lateral_velocity_gate
                        and abs(body_yaw_error) <= args.switch_yaw_gate
                    )
                    record = {
                        "tick": tick,
                        "time_s": tick * float(env.dt),
                        "seed": seed,
                        "mode": candidate.label,
                        "controller_phase": phase_names.get(phase_id, "UNKNOWN"),
                        "state_transitions": int(state_transitions),
                        "forced_transitions": int(forced_transitions),
                        "recovery_holds": int(recovery_holds),
                        "stance_side": "left" if stance_side >= 0.0 else "right",
                        "phase_ticks": int(phase_ticks),
                        "load_ready": bool(np.asarray(jax.device_get(load_ready))),
                        "swing_ready": bool(np.asarray(jax.device_get(swing_ready))),
                        "push_allowed": bool(np.asarray(jax.device_get(push_allowed))),
                        "switch_ready": bool(switch_ready),
                        "lateral_error_m": float(np.asarray(jax.device_get(lateral_error))),
                        "stance_foot_x_m": float(np.asarray(jax.device_get(stance_foot_x))),
                        "stance_foot_y_m": float(np.asarray(jax.device_get(stance_foot_y))),
                        "desired_base_y_m": float(
                            np.asarray(jax.device_get(desired_base_y))
                        ),
                        "swing_foot_x_m": float(np.asarray(jax.device_get(swing_foot_x))),
                        "desired_swing_foot_x_m": float(
                            np.asarray(jax.device_get(desired_swing_x))
                        ),
                        "swing_x_error_m": float(np.asarray(jax.device_get(swing_x_error))),
                        "forward_scale": float(np.asarray(jax.device_get(forward_scale))),
                        "push_stability_scale": float(
                            np.asarray(jax.device_get(stability_scale))
                        ),
                        "push_lateral_scale": float(
                            np.asarray(jax.device_get(lateral_scale))
                        ),
                        "push_yaw_scale": float(np.asarray(jax.device_get(yaw_scale))),
                        "yaw_correction_rad": float(
                            np.asarray(jax.device_get(yaw_correction))
                        ),
                        "teacher_yaw_error_rad": float(
                            np.asarray(jax.device_get(teacher_yaw_error))
                        ),
                        "sagittal_error_m": float(
                            np.asarray(jax.device_get(sagittal_error))
                        ),
                        "propulsion_drive_rad": float(
                            np.asarray(jax.device_get(propulsion_drive))
                        ),
                        "teacher_target_velocity_limit_rad_s": (
                            candidate.teacher_target_velocity_limit_rad_s
                        ),
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
                        "body_roll_rad": quat_wxyz_to_roll(quat),
                        "body_pitch_rad": quat_wxyz_to_pitch(quat),
                        "body_yaw_rad": body_yaw,
                        "body_yaw_target_rad": yaw_target_rad,
                        "body_yaw_error_rad": body_yaw_error,
                        "base_x_m": float(qpos[base_addr]),
                        "base_y_m": float(qpos[base_addr + 1]),
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

                    phase_ticks += 1
                    phase_changed = False
                    forced = False
                    max_load_ticks = max(1, int(round(candidate.load_s / float(env.dt))))
                    max_unweight_ticks = max(1, int(round(candidate.unweight_s / float(env.dt))))
                    push_ticks = max(1, int(round(candidate.push_s / float(env.dt))))
                    max_recovery_ticks = max(1, int(round(args.max_recovery_s / float(env.dt))))
                    allow_unstable_switch = (
                        not args.hold_switch_until_stable
                        or switch_ready
                    )
                    if phase_id == 0:
                        if record["load_ready"] and allow_unstable_switch:
                            phase_id = 1
                            phase_changed = True
                        elif phase_ticks >= max_load_ticks and allow_unstable_switch:
                            phase_id = 1
                            phase_changed = True
                            forced = True
                        elif args.hold_switch_until_stable and phase_ticks >= max_load_ticks:
                            recovery_holds += 1
                    elif phase_id == 1:
                        if record["swing_ready"] and allow_unstable_switch:
                            phase_id = 2
                            phase_changed = True
                        elif phase_ticks >= max_unweight_ticks and allow_unstable_switch:
                            phase_id = 2
                            phase_changed = True
                            forced = True
                        elif args.hold_switch_until_stable and phase_ticks >= max_unweight_ticks:
                            phase_id = 0
                            phase_changed = True
                            recovery_holds += 1
                    else:
                        if phase_ticks >= push_ticks:
                            if allow_unstable_switch or phase_ticks >= push_ticks + max_recovery_ticks:
                                phase_id = 0
                                stance_side *= -1.0
                                phase_changed = True
                                if not switch_ready:
                                    forced = True
                            else:
                                phase_id = 0
                                phase_changed = True
                                recovery_holds += 1
                    if phase_changed:
                        phase_ticks = 0
                        state_transitions += 1
                        if forced:
                            forced_transitions += 1

                trace_path = trace_root / candidate.label / f"seed_{seed:03d}.jsonl"
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                trace_path.write_text("".join(json.dumps(record) + "\n" for record in records))
                summary = summarize_records(records, args.command_x)
                summary.update(summarize_controller_records(records))
                summary.update({"seed": seed, "trace": str(trace_path)})
                candidate_rows.append(summary)

            mean_vx = [row["mean_vx_m_s"] for row in candidate_rows if finite(row["mean_vx_m_s"])]
            falls = sum(
                1 for row in candidate_rows if row["termination_reason"] != "duration_complete"
            )
            push_allowed = [
                row["push_allowed_pct"] for row in candidate_rows if finite(row["push_allowed_pct"])
            ]
            results.append(
                {
                    "candidate": candidate.__dict__,
                    "runs": candidate_rows,
                    "aggregate": {
                        "runs": len(candidate_rows),
                        "falls": falls,
                        "duration_complete": len(candidate_rows) - falls,
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
        "status": "PASS_FOOT_PLACEMENT_MPC_PROBE_RAN" if results else "HOLD_NO_CANDIDATES",
        "command_x": args.command_x,
        "duration_s": args.duration_s,
        "seeds": seeds,
        "trace_dir": str(trace_root),
        "candidate_count": len(candidates),
        "results": ranked,
        "limitations": [
            "first implementation uses joint-space approximations for swing-foot placement",
            "not a full nonlinear MPC solver",
            "passing still requires external 100-150 tick score artifacts",
        ],
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Foot-Placement MPC Teacher Probe",
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
            "## Top Candidates",
            "",
            "| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in payload["results"][:20]:
        candidate = item["candidate"]
        aggregate = item["aggregate"]
        lines.append(
            "| {label} | {runs} | {falls} | {complete} | {mean_vx} | {max_vx} | {push_allowed} |".format(
                label=candidate["label"],
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
            "- This is an offline finite-horizon teacher probe, not policy training.",
            "- Raw traces are ignored by git; compact summaries and score artifacts should be committed.",
            "- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--duration-s", type=float, default=3.0)
    parser.add_argument("--seeds", default="0,2")
    parser.add_argument("--jax-platform", choices=["auto", "cpu", "gpu"], default="cpu")
    parser.add_argument(
        "--initial-stance-sides",
        default="1.0",
        help="Comma-separated stance side seeds: positive starts left, negative starts right.",
    )
    parser.add_argument("--periods", default="0.56")
    parser.add_argument("--load-s", type=float, default=0.28)
    parser.add_argument("--unweight-s", type=float, default=0.22)
    parser.add_argument("--push-s", type=float, default=0.14)
    parser.add_argument("--load-shift-y", default="0.015,0.025")
    parser.add_argument(
        "--stance-relative-lateral",
        action="store_true",
        help=(
            "Make load-shift-y a desired base-y offset from the current stance "
            "foot instead of an absolute world/base-y target. Default is off "
            "to preserve prior probe behavior."
        ),
    )
    parser.add_argument("--base-y-gate", type=float, default=0.03)
    parser.add_argument("--lateral-velocity-gate", type=float, default=0.12)
    parser.add_argument("--foot-place-x", default="0.015,0.03")
    parser.add_argument("--foot-place-gains", default="0.8,1.2")
    parser.add_argument(
        "--swing-min-advance",
        default="-0.08",
        help=(
            "Comma-separated minimum swing-foot x advance values. Negative default "
            "preserves the original permissive placement behavior."
        ),
    )
    parser.add_argument("--swing-knee", type=float, default=0.10)
    parser.add_argument("--swing-ankle", type=float, default=0.0)
    parser.add_argument("--swing-reach-limit", type=float, default=0.08)
    parser.add_argument("--stance-retract", type=float, default=0.04)
    parser.add_argument("--stance-hip-pushes", default="0.02,0.04")
    parser.add_argument("--stance-knee-pushes", default="-0.02,0.0")
    parser.add_argument("--stance-ankle-pushes", default="-0.02,0.02")
    parser.add_argument(
        "--stance-base-x-offsets",
        default="0.0",
        help=(
            "Comma-separated desired base-x offsets from the stance foot for the "
            "sagittal stance-feedback propulsion primitive. Default 0 preserves "
            "previous behavior when paired with zero gains/limits."
        ),
    )
    parser.add_argument(
        "--sagittal-gains",
        default="0.0",
        help=(
            "Comma-separated gains from stance-foot-relative sagittal error to "
            "stance propulsion drive. Default 0 preserves previous behavior."
        ),
    )
    parser.add_argument(
        "--vx-gains",
        default="0.0",
        help=(
            "Comma-separated gains from local forward-velocity error to stance "
            "propulsion drive. Default 0 preserves previous behavior."
        ),
    )
    parser.add_argument(
        "--propulsion-limits",
        default="0.0",
        help=(
            "Comma-separated absolute limits for the stance sagittal propulsion "
            "drive in radians. Default 0 disables the new drive."
        ),
    )
    parser.add_argument(
        "--propulsion-patterns",
        default="1.0",
        help=(
            "Comma-separated signs/pattern scales for the sagittal stance drive. "
            "Use 1 and -1 to test joint-sign convention offline."
        ),
    )
    parser.add_argument(
        "--teacher-target-velocity-limits",
        default="0.0",
        help=(
            "Comma-separated teacher-side sent-target velocity limits in rad/s. "
            "Use 0 to preserve the environment max_motor_velocity behavior."
        ),
    )
    parser.add_argument(
        "--push-lateral-soft-gates",
        default="1000.0",
        help=(
            "Comma-separated lateral velocity soft-gate widths for push scaling. "
            "Large default preserves previous behavior."
        ),
    )
    parser.add_argument(
        "--push-yaw-soft-gates",
        default="1000.0",
        help=(
            "Comma-separated yaw soft-gate widths for push scaling. Large default "
            "preserves previous behavior."
        ),
    )
    parser.add_argument(
        "--push-min-scales",
        default="1.0",
        help=(
            "Comma-separated minimum push stability scales. Default 1.0 preserves "
            "previous behavior; values below 1.0 allow lateral/yaw push attenuation."
        ),
    )
    parser.add_argument(
        "--yaw-gains",
        default="0.0",
        help=(
            "Comma-separated body-yaw feedback gains applied through hip-yaw targets. "
            "Default 0.0 preserves previous behavior."
        ),
    )
    parser.add_argument(
        "--yaw-vy-gains",
        default="0.0",
        help=(
            "Comma-separated lateral-velocity feedback gains applied through hip-yaw "
            "targets. Default 0.0 preserves previous behavior."
        ),
    )
    parser.add_argument("--roll-gains", default="1.5")
    parser.add_argument("--vy-damping-gains", default="0.5,1.0")
    parser.add_argument("--body-y-gains", default="0.5")
    parser.add_argument("--roll-limit", type=float, default=0.08)
    parser.add_argument("--yaw-limit", type=float, default=0.06)
    parser.add_argument(
        "--hold-switch-until-stable",
        action="store_true",
        help=(
            "Hold or recover stance transitions until lateral velocity and yaw are "
            "inside the switch gates. Default off preserves previous fixed timing."
        ),
    )
    parser.add_argument("--switch-lateral-velocity-gate", type=float, default=0.12)
    parser.add_argument("--switch-yaw-gate", type=float, default=0.12)
    parser.add_argument("--max-recovery-s", type=float, default=0.20)
    parser.add_argument("--pitch-target", type=float, default=0.0)
    parser.add_argument("--pitch-gate", type=float, default=0.35)
    parser.add_argument("--pitch-damping", type=float, default=1.0)
    parser.add_argument("--clearance-gate", type=float, default=0.008)
    parser.add_argument("--min-height", type=float, default=0.145)
    parser.add_argument("--max-candidates", type=int, default=12)
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
