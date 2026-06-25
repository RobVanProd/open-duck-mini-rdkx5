#!/usr/bin/env python3
"""Probe a simple closed-loop weight-transfer teacher in Open Duck sim.

This is an offline target-generation diagnostic. It does not train, deploy,
SSH, or touch the robot. It writes compact summaries plus optional JSONL traces
that can be scored by score_target_candidates_objective.py.
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
from eval_reference_motion_rollout import JOINT_NAMES, fmt, parse_int_list
from search_low_command_target_primitives import policy_observation_list, summarize_records


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PROBE.md"
DEFAULT_OUTPUT_JSON = (
    ROOT / "outputs" / "analysis" / "closed_loop_weight_transfer_teacher_probe.json"
)
DEFAULT_TRACE_DIR = (
    ROOT / "outputs" / "analysis" / "closed_loop_weight_transfer_teacher_probe_traces"
)


@dataclass
class Teacher:
    label: str
    period_s: float
    roll_shift_rad: float
    swing_knee_rad: float
    swing_ankle_rad: float
    stance_push_gain: float
    stance_push_limit_rad: float
    pitch_damping: float
    lateral_gain: float
    body_y_gain: float
    push_lateral_gate: float
    contact_lift_boost: float


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def label_float(value: float) -> str:
    return f"{value:g}".replace(".", "p").replace("-", "m")


def teacher_grid(args: argparse.Namespace) -> list[Teacher]:
    rows: list[Teacher] = []
    for period_s in parse_float_list(args.periods):
        for roll_shift in parse_float_list(args.roll_shifts):
            for swing_knee in parse_float_list(args.swing_knees):
                for swing_ankle in parse_float_list(args.swing_ankles):
                    for stance_gain in parse_float_list(args.stance_push_gains):
                        for pitch_damping in parse_float_list(args.pitch_dampings):
                            for lateral_gain in parse_float_list(args.lateral_gains):
                                for body_y_gain in parse_float_list(args.body_y_gains):
                                    for push_lateral_gate in parse_float_list(
                                        args.push_lateral_gates
                                    ):
                                        for contact_lift_boost in parse_float_list(
                                            args.contact_lift_boosts
                                        ):
                                            label = (
                                                f"teacher_p{label_float(period_s)}"
                                                f"_rs{label_float(roll_shift)}"
                                                f"_sk{label_float(swing_knee)}"
                                                f"_sa{label_float(swing_ankle)}"
                                                f"_spg{label_float(stance_gain)}"
                                                f"_pd{label_float(pitch_damping)}"
                                                f"_lg{label_float(lateral_gain)}"
                                                f"_byg{label_float(body_y_gain)}"
                                                f"_plg{label_float(push_lateral_gate)}"
                                                f"_clb{label_float(contact_lift_boost)}"
                                            )
                                            rows.append(
                                                Teacher(
                                                    label=label,
                                                    period_s=period_s,
                                                    roll_shift_rad=roll_shift,
                                                    swing_knee_rad=swing_knee,
                                                    swing_ankle_rad=swing_ankle,
                                                    stance_push_gain=stance_gain,
                                                    stance_push_limit_rad=args.stance_push_limit,
                                                    pitch_damping=pitch_damping,
                                                    lateral_gain=lateral_gain,
                                                    body_y_gain=body_y_gain,
                                                    push_lateral_gate=push_lateral_gate,
                                                    contact_lift_boost=contact_lift_boost,
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
    teachers = teacher_grid(args)
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

        def teacher_target(
            default_actuator,
            tick,
            period_s,
            roll_shift_rad,
            swing_knee_rad,
            swing_ankle_rad,
            stance_push_gain,
            stance_push_limit_rad,
            pitch_damping,
            lateral_gain,
            body_y_gain,
            push_lateral_gate,
            contact_lift_boost,
            local_vx,
            local_vy,
            body_pitch,
            base_y,
            base_height,
            contact,
        ):
            phase01 = jp.mod((tick * env.dt) / period_s, 1.0)
            left_stance = jp.where(phase01 < 0.5, 1.0, 0.0)
            right_stance = 1.0 - left_stance
            left_swing = 1.0 - left_stance
            right_swing = 1.0 - right_stance
            left_contact = contact[0].astype(jp.float32)
            right_contact = contact[1].astype(jp.float32)

            forward_error = command[0] - local_vx
            raw_push = jp.clip(
                stance_push_gain * forward_error,
                -stance_push_limit_rad,
                stance_push_limit_rad,
            )
            lateral_push_scale = jp.where(
                push_lateral_gate > 1.0e-6,
                jp.clip(1.0 - jp.abs(local_vy) / push_lateral_gate, 0.0, 1.0),
                1.0,
            )
            height_scale = jp.clip((base_height - args.min_height_m) / 0.03, 0.0, 1.0)
            pitch_scale = jp.clip(1.0 - pitch_damping * jp.abs(body_pitch), 0.0, 1.0)
            stance_push = raw_push * height_scale * pitch_scale * lateral_push_scale
            lateral_correction = jp.clip(
                lateral_gain * local_vy + body_y_gain * base_y,
                -0.06,
                0.06,
            )
            roll = roll_shift_rad * (left_stance - right_stance) - lateral_correction

            left_lift = swing_knee_rad * left_swing * (1.0 + contact_lift_boost * left_contact)
            right_lift = (
                swing_knee_rad * right_swing * (1.0 + contact_lift_boost * right_contact)
            )
            left_ankle_lift = swing_ankle_rad * left_swing
            right_ankle_lift = swing_ankle_rad * right_swing
            pitch_ankle = jp.clip(-pitch_damping * body_pitch * 0.03, -0.04, 0.04)

            target = jp.asarray(default_actuator)
            target = target.at[1].set(default_actuator[1] + roll)
            target = target.at[2].set(default_actuator[2] + left_stance * stance_push)
            target = target.at[3].set(default_actuator[3] + left_lift)
            target = target.at[4].set(default_actuator[4] + left_ankle_lift + pitch_ankle)
            target = target.at[10].set(default_actuator[10] - roll)
            target = target.at[11].set(default_actuator[11] + right_stance * stance_push)
            target = target.at[12].set(default_actuator[12] + right_lift)
            target = target.at[13].set(default_actuator[13] + right_ankle_lift + pitch_ankle)
            return target

        def step_teacher(
            state,
            period_s,
            roll_shift_rad,
            swing_knee_rad,
            swing_ankle_rad,
            stance_push_gain,
            stance_push_limit_rad,
            pitch_damping,
            lateral_gain,
            body_y_gain,
            push_lateral_gate,
            contact_lift_boost,
        ):
            state.info["command"] = command
            tick = state.info["step"]
            contact_in = state.info["last_contact"]
            qpos = state.data.qpos
            base_addr = env._floating_base_qpos_addr
            quat = qpos[base_addr + 3 : base_addr + 7]
            local_linvel = env.get_local_linvel(state.data)
            target = teacher_target(
                env._default_actuator,
                tick,
                period_s,
                roll_shift_rad,
                swing_knee_rad,
                swing_ankle_rad,
                stance_push_gain,
                stance_push_limit_rad,
                pitch_damping,
                lateral_gain,
                body_y_gain,
                push_lateral_gate,
                contact_lift_boost,
                local_linvel[0],
                local_linvel[1],
                pitch_from_quat_wxyz(quat),
                qpos[base_addr + 1],
                qpos[base_addr + 2],
                contact_in,
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
            return state.replace(data=data, obs=obs, reward=reward, done=done), action, target, pre_rate_limit, sent_target

        refresh_obs_jit = jax.jit(refresh_obs)
        step_teacher_jit = jax.jit(step_teacher)
        sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))

        for teacher in teachers:
            teacher_rows = []
            for seed in seeds:
                state = env.reset(jax.random.PRNGKey(seed))
                state.info["command"] = command
                state = refresh_obs_jit(state)
                records = []
                for tick in range(sim_steps):
                    state, action, target, pre_rate, sent_target = step_teacher_jit(
                        state,
                        teacher.period_s,
                        teacher.roll_shift_rad,
                        teacher.swing_knee_rad,
                        teacher.swing_ankle_rad,
                        teacher.stance_push_gain,
                        teacher.stance_push_limit_rad,
                        teacher.pitch_damping,
                        teacher.lateral_gain,
                        teacher.body_y_gain,
                        teacher.push_lateral_gate,
                        teacher.contact_lift_boost,
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
                    record = {
                        "tick": tick,
                        "time_s": tick * float(env.dt),
                        "seed": seed,
                        "mode": teacher.label,
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
                        "observation": policy_observation_list(obs_host),
                        "reward": float(np.asarray(jax.device_get(state.reward))),
                        "done": done,
                    }
                    records.append(record)
                    if done:
                        break
                trace_path = trace_root / teacher.label / f"seed_{seed:03d}.jsonl"
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                trace_path.write_text("".join(json.dumps(record) + "\n" for record in records))
                summary = summarize_records(records, args.command_x)
                summary.update({"seed": seed, "trace": str(trace_path)})
                teacher_rows.append(summary)
            mean_vx = [row["mean_vx_m_s"] for row in teacher_rows if finite(row["mean_vx_m_s"])]
            falls = sum(
                1 for row in teacher_rows if row["termination_reason"] != "duration_complete"
            )
            results.append(
                {
                    "teacher": teacher.__dict__,
                    "runs": teacher_rows,
                    "aggregate": {
                        "runs": len(teacher_rows),
                        "falls": falls,
                        "duration_complete": len(teacher_rows) - falls,
                        "mean_vx_m_s": float(np.mean(mean_vx)) if mean_vx else None,
                        "max_mean_vx_m_s": float(np.max(mean_vx)) if mean_vx else None,
                    },
                }
            )

    ranked = sorted(
        results,
        key=lambda row: (
            row["aggregate"]["duration_complete"],
            row["aggregate"]["mean_vx_m_s"] or -999.0,
            -row["aggregate"]["falls"],
        ),
        reverse=True,
    )
    return {
        "status": "PASS_TEACHER_PROBE_RAN" if results else "HOLD_NO_TEACHER_CANDIDATES",
        "command_x": args.command_x,
        "duration_s": args.duration_s,
        "seeds": seeds,
        "trace_dir": str(trace_root),
        "candidate_count": len(teachers),
        "results": ranked,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Closed-Loop Weight-Transfer Teacher Probe",
        "",
        f"status: `{payload['status']}`",
        f"command_x: `{payload['command_x']}`",
        f"duration_s: `{payload['duration_s']}`",
        f"seeds: `{payload['seeds']}`",
        f"candidate_count: `{payload['candidate_count']}`",
        "",
        "## Top Teacher Candidates",
        "",
        "| teacher | runs | falls | duration_complete | mean_vx | max_seed_vx |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in payload["results"][:20]:
        teacher = item["teacher"]
        aggregate = item["aggregate"]
        lines.append(
            "| {label} | {runs} | {falls} | {complete} | {mean_vx} | {max_vx} |".format(
                label=teacher["label"],
                runs=aggregate["runs"],
                falls=aggregate["falls"],
                complete=aggregate["duration_complete"],
                mean_vx=fmt(aggregate["mean_vx_m_s"]),
                max_vx=fmt(aggregate["max_mean_vx_m_s"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a closed-loop teacher probe, not policy training.",
            "- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.",
            "- A useful teacher still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.",
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
    parser.add_argument("--periods", default="0.48,0.56,0.64")
    parser.add_argument("--roll-shifts", default="0.02,0.04")
    parser.add_argument("--swing-knees", default="0.08,0.12")
    parser.add_argument("--swing-ankles", default="-0.02,0.0")
    parser.add_argument("--stance-push-gains", default="0.5,1.0")
    parser.add_argument("--stance-push-limit", type=float, default=0.04)
    parser.add_argument("--pitch-dampings", default="0.0,1.0")
    parser.add_argument("--lateral-gains", default="0.0,0.5")
    parser.add_argument("--body-y-gains", default="0.0")
    parser.add_argument("--push-lateral-gates", default="0.0")
    parser.add_argument("--contact-lift-boosts", default="0.0,0.5")
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
