#!/usr/bin/env python3
"""Probe a staged balance-then-step planner in Open Duck sim.

This is an offline target-generation diagnostic. It does not train, deploy,
SSH, or touch the robot. Unlike the periodic teacher probe, this planner gates
forward step commands behind lateral/base-height/body-pitch checks so the trace
can show whether balance-first sequencing decouples forward motion from side
impulse.
"""

from __future__ import annotations

import argparse
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
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "STAGED_WEIGHT_TRANSFER_PLANNER_PROBE.md"
DEFAULT_OUTPUT_JSON = (
    ROOT / "outputs" / "analysis" / "staged_weight_transfer_planner_probe.json"
)
DEFAULT_TRACE_DIR = (
    ROOT / "outputs" / "analysis" / "staged_weight_transfer_planner_probe_traces"
)


@dataclass
class Planner:
    label: str
    step_gate_mode: int
    period_s: float
    balance_fraction: float
    roll_shift_rad: float
    lateral_gate_m_s: float
    base_y_gate_m: float
    pitch_gate_rad: float
    swing_knee_rad: float
    swing_ankle_rad: float
    swing_hip_reach_rad: float
    stance_retract_scale: float
    stance_push_gain: float
    stance_push_limit_rad: float
    pitch_target_rad: float
    pitch_damping: float
    lateral_gain: float
    body_y_gain: float


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def planner_grid(args: argparse.Namespace) -> list[Planner]:
    if getattr(args, "candidate_json", None):
        candidate_path = Path(args.candidate_json)
        if not candidate_path.is_absolute():
            candidate_path = ROOT / candidate_path
        payload = json.loads(candidate_path.read_text())
        items = payload.get("candidates", payload) if isinstance(payload, dict) else payload
        rows = []
        for index, item in enumerate(items):
            label = item.get("label", f"planner_json_{index:03d}")
            rows.append(
                Planner(
                    label=label,
                    step_gate_mode=int(item.get("step_gate_mode", 0)),
                    period_s=float(item["period_s"]),
                    balance_fraction=float(item["balance_fraction"]),
                    roll_shift_rad=float(item["roll_shift_rad"]),
                    lateral_gate_m_s=float(item["lateral_gate_m_s"]),
                    base_y_gate_m=float(item["base_y_gate_m"]),
                    pitch_gate_rad=float(item["pitch_gate_rad"]),
                    swing_knee_rad=float(item["swing_knee_rad"]),
                    swing_ankle_rad=float(item["swing_ankle_rad"]),
                    swing_hip_reach_rad=float(item["swing_hip_reach_rad"]),
                    stance_retract_scale=float(item["stance_retract_scale"]),
                    stance_push_gain=float(item["stance_push_gain"]),
                    stance_push_limit_rad=float(
                        item.get("stance_push_limit_rad", args.stance_push_limit)
                    ),
                    pitch_target_rad=float(item["pitch_target_rad"]),
                    pitch_damping=float(item["pitch_damping"]),
                    lateral_gain=float(item["lateral_gain"]),
                    body_y_gain=float(item["body_y_gain"]),
                )
            )
        return rows[: args.max_candidates]

    rows: list[Planner] = []
    for period_s in parse_float_list(args.periods):
        for balance_fraction in parse_float_list(args.balance_fractions):
            for roll_shift in parse_float_list(args.roll_shifts):
                for lateral_gate in parse_float_list(args.lateral_gates):
                    for base_y_gate in parse_float_list(args.base_y_gates):
                        for pitch_gate in parse_float_list(args.pitch_gates):
                            for swing_knee in parse_float_list(args.swing_knees):
                                for swing_ankle in parse_float_list(args.swing_ankles):
                                    for swing_hip_reach in parse_float_list(args.swing_hip_reaches):
                                        for stance_retract_scale in parse_float_list(
                                            args.stance_retract_scales
                                        ):
                                            for stance_push_gain in parse_float_list(
                                                args.stance_push_gains
                                            ):
                                                for pitch_target in parse_float_list(
                                                    args.pitch_targets
                                                ):
                                                    for pitch_damping in parse_float_list(
                                                        args.pitch_dampings
                                                    ):
                                                        for lateral_gain in parse_float_list(
                                                            args.lateral_feedback_gains
                                                        ):
                                                            for body_y_gain in parse_float_list(
                                                                args.body_y_gains
                                                            ):
                                                                label = (
                                                                    f"planner_p{label_float(period_s)}"
                                                                    f"_bf{label_float(balance_fraction)}"
                                                                    f"_rs{label_float(roll_shift)}"
                                                                    f"_lg{label_float(lateral_gate)}"
                                                                    f"_byg{label_float(base_y_gate)}"
                                                                    f"_pg{label_float(pitch_gate)}"
                                                                    f"_sk{label_float(swing_knee)}"
                                                                    f"_sa{label_float(swing_ankle)}"
                                                                    f"_shr{label_float(swing_hip_reach)}"
                                                                    f"_srs{label_float(stance_retract_scale)}"
                                                                    f"_spg{label_float(stance_push_gain)}"
                                                                    f"_pt{label_float(pitch_target)}"
                                                                    f"_pd{label_float(pitch_damping)}"
                                                                    f"_lfg{label_float(lateral_gain)}"
                                                                    f"_bygf{label_float(body_y_gain)}"
                                                                )
                                                                rows.append(
                                                                    Planner(
                                                                        label=label,
                                                                        step_gate_mode=0,
                                                                        period_s=period_s,
                                                                        balance_fraction=balance_fraction,
                                                                        roll_shift_rad=roll_shift,
                                                                        lateral_gate_m_s=lateral_gate,
                                                                        base_y_gate_m=base_y_gate,
                                                                        pitch_gate_rad=pitch_gate,
                                                                        swing_knee_rad=swing_knee,
                                                                        swing_ankle_rad=swing_ankle,
                                                                        swing_hip_reach_rad=swing_hip_reach,
                                                                        stance_retract_scale=stance_retract_scale,
                                                                        stance_push_gain=stance_push_gain,
                                                                        stance_push_limit_rad=args.stance_push_limit,
                                                                        pitch_target_rad=pitch_target,
                                                                        pitch_damping=pitch_damping,
                                                                        lateral_gain=lateral_gain,
                                                                        body_y_gain=body_y_gain,
                                                                    )
                                                                )
    if args.shuffle_candidates:
        random.Random(args.grid_seed).shuffle(rows)
    return rows[: args.max_candidates]


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
    planners = planner_grid(args)
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

        def planner_target(
            default_actuator,
            tick,
            step_gate_mode,
            period_s,
            balance_fraction,
            roll_shift_rad,
            lateral_gate_m_s,
            base_y_gate_m,
            pitch_gate_rad,
            swing_knee_rad,
            swing_ankle_rad,
            swing_hip_reach_rad,
            stance_retract_scale,
            stance_push_gain,
            stance_push_limit_rad,
            pitch_target_rad,
            pitch_damping,
            lateral_gain,
            body_y_gain,
            local_vx,
            local_vy,
            body_pitch,
            base_y,
            base_height,
        ):
            phase01 = jp.mod((tick * env.dt) / period_s, 1.0)
            left_stance = jp.where(phase01 < 0.5, 1.0, 0.0)
            right_stance = 1.0 - left_stance
            left_swing = 1.0 - left_stance
            right_swing = 1.0 - right_stance
            half_phase = jp.where(phase01 < 0.5, phase01 * 2.0, (phase01 - 0.5) * 2.0)
            in_balance_phase = half_phase < balance_fraction

            lateral_ok = jp.abs(local_vy) <= lateral_gate_m_s
            base_y_ok = jp.abs(base_y) <= base_y_gate_m
            height_ok = base_height >= args.min_height_m
            pitch_ok = jp.abs(body_pitch - pitch_target_rad) <= pitch_gate_rad
            step_enabled = (~in_balance_phase) & lateral_ok & base_y_ok & height_ok & pitch_ok
            hard_step_scale = step_enabled.astype(jp.float32)
            lateral_scale = jp.clip(
                1.0 - jp.abs(local_vy) / jp.maximum(lateral_gate_m_s, 1.0e-6),
                0.0,
                1.0,
            )
            base_y_scale = jp.clip(
                1.0 - jp.abs(base_y) / jp.maximum(base_y_gate_m, 1.0e-6),
                0.0,
                1.0,
            )
            pitch_scale = jp.clip(
                1.0
                - jp.abs(body_pitch - pitch_target_rad)
                / jp.maximum(pitch_gate_rad, 1.0e-6),
                0.0,
                1.0,
            )
            soft_step_scale = (
                (~in_balance_phase).astype(jp.float32)
                * height_ok.astype(jp.float32)
                * lateral_scale
                * base_y_scale
                * pitch_scale
            )
            ungated_step_scale = (~in_balance_phase).astype(jp.float32)
            step_scale = jp.where(
                step_gate_mode <= 0,
                hard_step_scale,
                jp.where(step_gate_mode == 1, soft_step_scale, ungated_step_scale),
            )

            lateral_correction = jp.clip(
                lateral_gain * local_vy + body_y_gain * base_y,
                -0.06,
                0.06,
            )
            roll = roll_shift_rad * (left_stance - right_stance) - lateral_correction
            pitch_error = body_pitch - pitch_target_rad
            pitch_ankle = jp.clip(-pitch_damping * pitch_error * 0.03, -0.04, 0.04)
            forward_error = command[0] - local_vx
            stance_push = step_scale * jp.clip(
                stance_push_gain * forward_error,
                -stance_push_limit_rad,
                stance_push_limit_rad,
            )

            left_lift = step_scale * swing_knee_rad * left_swing
            right_lift = step_scale * swing_knee_rad * right_swing
            left_step_reach = step_scale * swing_hip_reach_rad * left_swing
            right_step_reach = step_scale * swing_hip_reach_rad * right_swing
            left_stance_retract = (
                -step_scale * stance_retract_scale * swing_hip_reach_rad * left_stance
            )
            right_stance_retract = (
                -step_scale * stance_retract_scale * swing_hip_reach_rad * right_stance
            )
            left_ankle_lift = step_scale * swing_ankle_rad * left_swing
            right_ankle_lift = step_scale * swing_ankle_rad * right_swing

            target = jp.asarray(default_actuator)
            target = target.at[1].set(default_actuator[1] + roll)
            target = target.at[2].set(
                default_actuator[2]
                + left_stance * stance_push
                + left_step_reach
                + left_stance_retract
            )
            target = target.at[3].set(default_actuator[3] + left_lift)
            target = target.at[4].set(default_actuator[4] + left_ankle_lift + pitch_ankle)
            target = target.at[10].set(default_actuator[10] - roll)
            target = target.at[11].set(
                default_actuator[11]
                + right_stance * stance_push
                + right_step_reach
                + right_stance_retract
            )
            target = target.at[12].set(default_actuator[12] + right_lift)
            target = target.at[13].set(default_actuator[13] + right_ankle_lift + pitch_ankle)
            diagnostics = jp.asarray(
                [
                    phase01,
                    in_balance_phase.astype(jp.float32),
                    step_scale,
                    lateral_ok.astype(jp.float32),
                    base_y_ok.astype(jp.float32),
                    height_ok.astype(jp.float32),
                    pitch_ok.astype(jp.float32),
                ]
            )
            return target, diagnostics

        def step_planner(
            state,
            step_gate_mode,
            period_s,
            balance_fraction,
            roll_shift_rad,
            lateral_gate_m_s,
            base_y_gate_m,
            pitch_gate_rad,
            swing_knee_rad,
            swing_ankle_rad,
            swing_hip_reach_rad,
            stance_retract_scale,
            stance_push_gain,
            stance_push_limit_rad,
            pitch_target_rad,
            pitch_damping,
            lateral_gain,
            body_y_gain,
        ):
            state.info["command"] = command
            tick = state.info["step"]
            qpos = state.data.qpos
            base_addr = env._floating_base_qpos_addr
            quat = qpos[base_addr + 3 : base_addr + 7]
            local_linvel = env.get_local_linvel(state.data)
            target, diagnostics = planner_target(
                env._default_actuator,
                tick,
                step_gate_mode,
                period_s,
                balance_fraction,
                roll_shift_rad,
                lateral_gate_m_s,
                base_y_gate_m,
                pitch_gate_rad,
                swing_knee_rad,
                swing_ankle_rad,
                swing_hip_reach_rad,
                stance_retract_scale,
                stance_push_gain,
                stance_push_limit_rad,
                pitch_target_rad,
                pitch_damping,
                lateral_gain,
                body_y_gain,
                local_linvel[0],
                local_linvel[1],
                pitch_from_quat_wxyz(quat),
                qpos[base_addr + 1],
                qpos[base_addr + 2],
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
                diagnostics,
            )

        refresh_obs_jit = jax.jit(refresh_obs)
        step_planner_jit = jax.jit(step_planner)
        sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))

        for planner in planners:
            planner_rows = []
            for seed in seeds:
                state = env.reset(jax.random.PRNGKey(seed))
                state.info["command"] = command
                state = refresh_obs_jit(state)
                records = []
                for tick in range(sim_steps):
                    state, action, target, pre_rate, sent_target, diagnostics = step_planner_jit(
                        state,
                        planner.step_gate_mode,
                        planner.period_s,
                        planner.balance_fraction,
                        planner.roll_shift_rad,
                        planner.lateral_gate_m_s,
                        planner.base_y_gate_m,
                        planner.pitch_gate_rad,
                        planner.swing_knee_rad,
                        planner.swing_ankle_rad,
                        planner.swing_hip_reach_rad,
                        planner.stance_retract_scale,
                        planner.stance_push_gain,
                        planner.stance_push_limit_rad,
                        planner.pitch_target_rad,
                        planner.pitch_damping,
                        planner.lateral_gain,
                        planner.body_y_gain,
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
                    diag = np.asarray(jax.device_get(diagnostics), dtype=float)
                    obs_host = jax.device_get(state.obs)
                    done = bool(np.asarray(jax.device_get(state.done)))
                    record = {
                        "tick": tick,
                        "time_s": tick * float(env.dt),
                        "seed": seed,
                        "mode": planner.label,
                        "planner_step_gate_mode": planner.step_gate_mode,
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
                        "base_height_m": float(qpos[base_addr + 2]),
                        "foot_site_z_m": foot_site_pos[:, 2].astype(float).tolist(),
                        "local_linvel_m_s": local_linvel.astype(float).tolist(),
                        "foot_contacts": contacts.astype(int).tolist(),
                        "planner_phase01": float(diag[0]),
                        "planner_balance_phase": bool(diag[1] >= 0.5),
                        "planner_step_enabled": bool(diag[2] >= 0.5),
                        "planner_lateral_ok": bool(diag[3] >= 0.5),
                        "planner_base_y_ok": bool(diag[4] >= 0.5),
                        "planner_height_ok": bool(diag[5] >= 0.5),
                        "planner_pitch_ok": bool(diag[6] >= 0.5),
                        "observation": policy_observation_list(obs_host),
                        "reward": float(np.asarray(jax.device_get(state.reward))),
                        "done": done,
                    }
                    records.append(record)
                    if done:
                        break
                trace_path = trace_root / planner.label / f"seed_{seed:03d}.jsonl"
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                trace_path.write_text("".join(json.dumps(record) + "\n" for record in records))
                summary = summarize_records(records, args.command_x)
                summary.update(
                    {
                        "seed": seed,
                        "trace": str(trace_path),
                        "step_enabled_pct": (
                            float(
                                np.mean([record["planner_step_enabled"] for record in records])
                                * 100.0
                            )
                            if records
                            else None
                        ),
                    }
                )
                planner_rows.append(summary)
            mean_vx = [row["mean_vx_m_s"] for row in planner_rows if finite(row["mean_vx_m_s"])]
            falls = sum(
                1 for row in planner_rows if row["termination_reason"] != "duration_complete"
            )
            results.append(
                {
                    "planner": planner.__dict__,
                    "runs": planner_rows,
                    "aggregate": {
                        "runs": len(planner_rows),
                        "falls": falls,
                        "duration_complete": len(planner_rows) - falls,
                        "mean_vx_m_s": float(np.mean(mean_vx)) if mean_vx else None,
                        "max_mean_vx_m_s": float(np.max(mean_vx)) if mean_vx else None,
                        "mean_step_enabled_pct": (
                            float(
                                np.mean(
                                    [
                                        row["step_enabled_pct"]
                                        for row in planner_rows
                                        if finite(row.get("step_enabled_pct"))
                                    ]
                                )
                            )
                            if any(finite(row.get("step_enabled_pct")) for row in planner_rows)
                            else None
                        ),
                    },
                }
            )

    ranked = sorted(
        results,
        key=lambda row: (
            row["aggregate"]["duration_complete"],
            row["aggregate"]["mean_vx_m_s"] or -999.0,
            row["aggregate"]["mean_step_enabled_pct"] or -999.0,
            -row["aggregate"]["falls"],
        ),
        reverse=True,
    )
    return {
        "status": "PASS_PLANNER_PROBE_RAN" if results else "HOLD_NO_PLANNER_CANDIDATES",
        "command_x": args.command_x,
        "duration_s": args.duration_s,
        "seeds": seeds,
        "trace_dir": str(trace_root),
        "candidate_count": len(planners),
        "results": ranked,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Staged Weight-Transfer Planner Probe",
        "",
        f"status: `{payload['status']}`",
        f"command_x: `{payload['command_x']}`",
        f"duration_s: `{payload['duration_s']}`",
        f"seeds: `{payload['seeds']}`",
        f"candidate_count: `{payload['candidate_count']}`",
        "",
        "## Top Planner Candidates",
        "",
        "| planner | runs | falls | duration_complete | mean_vx | max_seed_vx | step_enabled_pct |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["results"][:20]:
        planner = item["planner"]
        aggregate = item["aggregate"]
        lines.append(
            "| {label} | {runs} | {falls} | {complete} | {mean_vx} | {max_vx} | {step} |".format(
                label=planner["label"],
                runs=aggregate["runs"],
                falls=aggregate["falls"],
                complete=aggregate["duration_complete"],
                mean_vx=fmt(aggregate["mean_vx_m_s"]),
                max_vx=fmt(aggregate["max_mean_vx_m_s"]),
                step=fmt(aggregate["mean_step_enabled_pct"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a staged closed-loop planner probe, not policy training.",
            "- `planner_step_enabled` records whether lateral/base-height/pitch gates allowed a forward step.",
            "- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.",
            "- A useful planner must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.",
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
    parser.add_argument("--seeds", default="0")
    parser.add_argument("--periods", default="0.56,0.64,0.72")
    parser.add_argument("--balance-fractions", default="0.25,0.4,0.55")
    parser.add_argument("--roll-shifts", default="0.02,0.04")
    parser.add_argument("--lateral-gates", default="0.06,0.08,0.10")
    parser.add_argument("--base-y-gates", default="0.02,0.04,0.06")
    parser.add_argument("--pitch-gates", default="0.12,0.18,0.24")
    parser.add_argument("--swing-knees", default="0.08,0.12")
    parser.add_argument("--swing-ankles", default="-0.02,0.0")
    parser.add_argument("--swing-hip-reaches", default="0.03,0.06")
    parser.add_argument("--stance-retract-scales", default="0.5,1.0")
    parser.add_argument("--stance-push-gains", default="0.5,1.0")
    parser.add_argument("--stance-push-limit", type=float, default=0.04)
    parser.add_argument("--pitch-targets", default="0.0,0.03")
    parser.add_argument("--pitch-dampings", default="1.0,2.0")
    parser.add_argument("--lateral-feedback-gains", default="-0.5,0.0,0.5")
    parser.add_argument("--body-y-gains", default="-0.5,0.0,0.5")
    parser.add_argument("--min-height-m", type=float, default=0.145)
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument(
        "--candidate-json",
        default=None,
        help="Optional JSON list of explicit planner candidates to replay.",
    )
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
