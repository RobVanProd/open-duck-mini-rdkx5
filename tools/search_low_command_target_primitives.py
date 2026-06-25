#!/usr/bin/env python3
"""Search simple low-command target primitives in Open Duck sim.

This is an offline target-generation diagnostic. It does not train, deploy,
SSH, or touch the robot. It writes compact summaries plus optional JSONL traces
that can be passed to mine_realized_target_windows.py.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import random
from typing import Any, Iterable

import numpy as np

from closed_loop_sim_eval import quat_wxyz_to_pitch, temporary_cwd
from eval_reference_motion_rollout import JOINT_NAMES, fmt, parse_int_list, percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_GENERATOR_SEARCH.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_generator_search.json"
DEFAULT_TRACE_DIR = ROOT / "outputs" / "analysis" / "target_generator_search_traces"


@dataclass
class Primitive:
    label: str
    period_s: float
    hip_roll_bias: float
    hip_pitch_bias: float
    hip_pitch_amp: float
    knee_bias: float
    knee_amp: float
    ankle_bias: float
    ankle_amp: float
    phase_offset: float
    lift_duty: float
    lift_scale: float


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


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


def candidate_grid(args: argparse.Namespace) -> list[Primitive]:
    periods = [float(item) for item in args.periods.split(",") if item.strip()]
    hip_roll_biases = [float(item) for item in args.hip_roll_biases.split(",") if item.strip()]
    hip_biases = [float(item) for item in args.hip_pitch_biases.split(",") if item.strip()]
    hip_amps = [float(item) for item in args.hip_pitch_amps.split(",") if item.strip()]
    knee_biases = [float(item) for item in args.knee_biases.split(",") if item.strip()]
    knee_amps = [float(item) for item in args.knee_amps.split(",") if item.strip()]
    ankle_biases = [float(item) for item in args.ankle_biases.split(",") if item.strip()]
    ankle_scales = [float(item) for item in args.ankle_scales.split(",") if item.strip()]
    phase_offsets = [float(item) for item in args.phase_offsets.split(",") if item.strip()]
    lift_duties = [float(item) for item in args.lift_duties.split(",") if item.strip()]
    lift_scales = [float(item) for item in args.lift_scales.split(",") if item.strip()]
    rows = []
    for period_s in periods:
        for hip_roll_bias in hip_roll_biases:
            for hip_bias in hip_biases:
                for hip_amp in hip_amps:
                    for knee_bias in knee_biases:
                        for knee_amp in knee_amps:
                            for ankle_bias in ankle_biases:
                                for ankle_scale in ankle_scales:
                                    for phase_offset in phase_offsets:
                                        for lift_duty in lift_duties:
                                            for lift_scale in lift_scales:
                                                ankle_amp = ankle_scale * hip_amp
                                                lift_label = (
                                                    ""
                                                    if lift_scale == 0.0 and lift_duty == 0.5
                                                    else f"_ld{lift_duty:g}_ls{lift_scale:g}"
                                                )
                                                rows.append(
                                                    Primitive(
                                                        label=(
                                                            f"p{period_s:g}_hrb{hip_roll_bias:g}_"
                                                            f"hb{hip_bias:g}_h{hip_amp:g}_"
                                                            f"kb{knee_bias:g}_k{knee_amp:g}_"
                                                            f"ab{ankle_bias:g}_a{ankle_amp:g}_"
                                                            f"ph{phase_offset:g}{lift_label}"
                                                        ).replace(".", "p").replace("-", "m"),
                                                        period_s=period_s,
                                                        hip_roll_bias=hip_roll_bias,
                                                        hip_pitch_bias=hip_bias,
                                                        hip_pitch_amp=hip_amp,
                                                        knee_bias=knee_bias,
                                                        knee_amp=knee_amp,
                                                        ankle_bias=ankle_bias,
                                                        ankle_amp=ankle_amp,
                                                        phase_offset=phase_offset,
                                                        lift_duty=lift_duty,
                                                        lift_scale=lift_scale,
                                                    )
                                                )
    if args.shuffle_candidates:
        random.Random(args.grid_seed).shuffle(rows)
    return rows[: args.max_candidates]


def pattern(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(int(value)) for value in values)


def policy_observation_list(obs: Any) -> list[float] | None:
    obs_host = obs
    if isinstance(obs_host, dict):
        obs_host = obs_host.get("state")
    if obs_host is None:
        return None
    data = np.asarray(obs_host, dtype=float).reshape(-1)
    return data.astype(float).tolist()


def summarize_records(records: list[dict[str, Any]], command_x: float) -> dict[str, Any]:
    vx = [record["local_linvel_m_s"][0] for record in records]
    vy = [record["local_linvel_m_s"][1] for record in records]
    pitch = [abs(record["body_pitch_rad"]) for record in records]
    height = [record["base_height_m"] for record in records]
    foot_z = np.asarray([record.get("foot_site_z_m", []) for record in records], dtype=float)
    action = np.asarray([record["action"] for record in records], dtype=float)
    sent = np.asarray([record["sent_target_rad"] for record in records], dtype=float)
    actual = np.asarray([record["actual_position_rad"] for record in records], dtype=float)
    target = np.asarray([record["reference_target_rad"] for record in records], dtype=float)
    tracking = np.abs(sent - actual) if sent.size and actual.size else np.zeros((0, 0))
    target_clip = np.abs(target - np.asarray([record["target_pre_rate_limit_rad"] for record in records], dtype=float))
    sent_velocity = (
        np.abs(np.diff(sent, axis=0) / 0.02)
        if len(records) > 1 and sent.size
        else np.zeros((0, len(JOINT_NAMES)))
    )
    contacts = [pattern(record.get("foot_contacts", [])) for record in records]
    contact_counts = {key: contacts.count(key) for key in sorted(set(contacts))}
    return {
        "samples": len(records),
        "termination_reason": "fall_or_nan" if records and records[-1].get("done") else "duration_complete",
        "mean_vx_m_s": float(np.mean(vx)) if vx else None,
        "track_ratio": float(np.mean(vx) / command_x) if vx and abs(command_x) > 1.0e-9 else None,
        "vy_abs_p95_m_s": percentile([abs(value) for value in vy], 95),
        "body_pitch_abs_p95_rad": percentile(pitch, 95),
        "base_height_min_m": float(np.min(height)) if height else None,
        "foot_site_z_p95_m": (
            percentile(foot_z.reshape(-1).tolist(), 95) if foot_z.size else None
        ),
        "action_saturation_pct": float(np.mean(np.abs(action) >= 0.999) * 100.0) if action.size else None,
        "target_clip_p95_rad": percentile(target_clip.reshape(-1).tolist(), 95) if target_clip.size else None,
        "sent_target_velocity_p95_rad_s": percentile(sent_velocity.reshape(-1).tolist(), 95) if sent_velocity.size else None,
        "joint_tracking_p95_rad": percentile(tracking.reshape(-1).tolist(), 95) if tracking.size else None,
        "contact_counts": contact_counts,
        "contact_transitions": sum(1 for a, b in zip(contacts, contacts[1:]) if a != b),
    }


def run_search(args: argparse.Namespace) -> dict[str, Any]:
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
    trace_root.mkdir(parents=True, exist_ok=True)
    primitives = candidate_grid(args)
    seeds = parse_int_list(args.seeds)
    results = []
    all_records = []

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

    def primitive_target(
        default_actuator,
        tick,
        period_s,
        hip_roll_bias,
        hip_bias,
        hip_amp,
        knee_bias,
        knee_amp,
        ankle_bias,
        ankle_amp,
        phase_offset,
        lift_duty,
        lift_scale,
    ):
        t = tick * env.dt
        phase = 2.0 * jp.pi * (t / period_s) + phase_offset
        left = jp.sin(phase)
        right = jp.sin(phase + jp.pi)

        def lift_pulse(angle):
            phase01 = jp.mod(angle / (2.0 * jp.pi), 1.0)
            centered_dist = jp.abs(jp.mod(phase01 - 0.5 + 0.5, 1.0) - 0.5)
            half_duty = jp.maximum(lift_duty * 0.5, 1.0e-6)
            return jp.clip(1.0 - centered_dist / half_duty, 0.0, 1.0)

        left_lift = (1.0 - lift_scale) * jp.maximum(0.0, left) + lift_scale * lift_pulse(phase)
        right_lift = (1.0 - lift_scale) * jp.maximum(0.0, right) + lift_scale * lift_pulse(
            phase + jp.pi
        )
        left_ankle = (1.0 - lift_scale) * left + lift_scale * lift_pulse(phase)
        right_ankle = (1.0 - lift_scale) * right + lift_scale * lift_pulse(phase + jp.pi)

        target = jp.asarray(default_actuator)
        target = target.at[1].set(default_actuator[1] + hip_roll_bias)
        target = target.at[2].set(default_actuator[2] + hip_bias + hip_amp * left)
        target = target.at[3].set(default_actuator[3] + knee_bias + knee_amp * left_lift)
        target = target.at[4].set(default_actuator[4] + ankle_bias + ankle_amp * left_ankle)
        target = target.at[10].set(default_actuator[10] - hip_roll_bias)
        target = target.at[11].set(default_actuator[11] + hip_bias + hip_amp * right)
        target = target.at[12].set(default_actuator[12] + knee_bias + knee_amp * right_lift)
        target = target.at[13].set(default_actuator[13] + ankle_bias + ankle_amp * right_ankle)
        return target

    def step_primitive(
        state,
        period_s,
        hip_roll_bias,
        hip_bias,
        hip_amp,
        knee_bias,
        knee_amp,
        ankle_bias,
        ankle_amp,
        phase_offset,
        lift_duty,
        lift_scale,
    ):
        state.info["command"] = command
        tick = state.info["step"]
        target = primitive_target(
            env._default_actuator,
            tick,
            period_s,
            hip_roll_bias,
            hip_bias,
            hip_amp,
            knee_bias,
            knee_amp,
            ankle_bias,
            ankle_amp,
            phase_offset,
            lift_duty,
            lift_scale,
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
    step_primitive_jit = jax.jit(step_primitive)
    sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))

    for primitive in primitives:
        primitive_rows = []
        for seed in seeds:
            state = env.reset(jax.random.PRNGKey(seed))
            state.info["command"] = command
            state = refresh_obs_jit(state)
            records = []
            for tick in range(sim_steps):
                state, action, target, pre_rate, sent_target = step_primitive_jit(
                    state,
                    primitive.period_s,
                    primitive.hip_roll_bias,
                    primitive.hip_pitch_bias,
                    primitive.hip_pitch_amp,
                    primitive.knee_bias,
                    primitive.knee_amp,
                    primitive.ankle_bias,
                    primitive.ankle_amp,
                    primitive.phase_offset,
                    primitive.lift_duty,
                    primitive.lift_scale,
                )
                qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
                base_addr = int(env._floating_base_qpos_addr)
                quat = qpos[base_addr + 3 : base_addr + 7]
                local_linvel = np.asarray(
                    jax.device_get(env.get_local_linvel(state.data)), dtype=float
                )
                actual = np.asarray(
                    jax.device_get(env.get_actuator_joints_qpos(state.data.qpos)), dtype=float
                )
                foot_site_pos = np.asarray(
                    jax.device_get(state.data.site_xpos[env._feet_site_id]), dtype=float
                )
                contacts = np.asarray(jax.device_get(state.info["last_contact"]), dtype=bool)
                obs_host = jax.device_get(state.obs)
                policy_obs = policy_observation_list(obs_host)
                done = bool(np.asarray(jax.device_get(state.done)))
                record = {
                    "tick": tick,
                    "time_s": tick * float(env.dt),
                    "seed": seed,
                    "mode": f"primitive_{primitive.label}",
                    "command": [args.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    "action": np.asarray(jax.device_get(action), dtype=float).tolist(),
                    "reference_target_rad": np.asarray(jax.device_get(target), dtype=float).tolist(),
                    "target_pre_rate_limit_rad": np.asarray(jax.device_get(pre_rate), dtype=float).tolist(),
                    "sent_target_rad": np.asarray(jax.device_get(sent_target), dtype=float).tolist(),
                    "actual_position_rad": actual.tolist(),
                    "body_pitch_rad": quat_wxyz_to_pitch(quat),
                    "base_x_m": float(qpos[base_addr]),
                    "base_y_m": float(qpos[base_addr + 1]),
                    "base_height_m": float(qpos[base_addr + 2]),
                    "foot_site_z_m": foot_site_pos[:, 2].astype(float).tolist(),
                    "local_linvel_m_s": local_linvel.astype(float).tolist(),
                    "foot_contacts": contacts.astype(int).tolist(),
                    "observation": policy_obs,
                    "reward": float(np.asarray(jax.device_get(state.reward))),
                    "done": done,
                }
                records.append(record)
                all_records.extend(records[-1:])
                if done:
                    break
            trace_path = trace_root / primitive.label / f"seed_{seed:03d}.jsonl"
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            trace_path.write_text("".join(json.dumps(record) + "\n" for record in records))
            summary = summarize_records(records, args.command_x)
            summary.update({"seed": seed, "trace": str(trace_path)})
            primitive_rows.append(summary)
        mean_vx = [row["mean_vx_m_s"] for row in primitive_rows if finite(row["mean_vx_m_s"])]
        falls = sum(1 for row in primitive_rows if row["termination_reason"] != "duration_complete")
        results.append(
            {
                "primitive": primitive.__dict__,
                "runs": primitive_rows,
                "aggregate": {
                    "runs": len(primitive_rows),
                    "falls": falls,
                    "duration_complete": len(primitive_rows) - falls,
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
        "status": "PASS_TARGET_SEARCH_RAN" if results else "HOLD_NO_TARGET_SEARCH_CANDIDATES",
        "command_x": args.command_x,
        "duration_s": args.duration_s,
        "seeds": seeds,
        "trace_dir": str(trace_root),
        "candidate_count": len(primitives),
        "results": ranked,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Target Generator Search",
        "",
        f"status: `{payload['status']}`",
        f"command_x: `{payload['command_x']}`",
        f"duration_s: `{payload['duration_s']}`",
        f"seeds: `{payload['seeds']}`",
        f"candidate_count: `{payload['candidate_count']}`",
        "",
        "## Top Primitive Candidates",
        "",
        "| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in payload["results"][:20]:
        primitive = item["primitive"]
        aggregate = item["aggregate"]
        lines.append(
            "| {label} | {runs} | {falls} | {complete} | {mean_vx} | {max_vx} |".format(
                label=primitive["label"],
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
            "- This is a target-window generator search, not policy training.",
            "- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.",
            "- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.",
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
    parser.add_argument("--periods", default="0.7,0.9,1.1")
    parser.add_argument("--hip-roll-biases", default="0.0")
    parser.add_argument("--hip-pitch-biases", default="0.0")
    parser.add_argument("--hip-pitch-amps", default="0.03,0.05,0.07")
    parser.add_argument("--knee-biases", default="0.0")
    parser.add_argument("--knee-amps", default="0.04,0.08")
    parser.add_argument("--ankle-biases", default="0.0")
    parser.add_argument("--ankle-scales", default="-0.5,-1.0")
    parser.add_argument("--phase-offsets", default="0.0,1.5708")
    parser.add_argument("--lift-duties", default="0.5")
    parser.add_argument("--lift-scales", default="0.0")
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument("--shuffle-candidates", action="store_true")
    parser.add_argument("--grid-seed", type=int, default=0)
    parser.add_argument("--trace-dir", default=str(DEFAULT_TRACE_DIR))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = run_search(args)
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
