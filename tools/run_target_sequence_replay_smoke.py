#!/usr/bin/env python3
"""Replay curated target-window action sequences in closed-loop sim.

This is an offline diagnostic. It does not fit a neural policy, run PPO, SSH,
deploy, or touch the robot. It tests whether preserving the curated target
sequence timing is enough to keep the low-command gait alive in closed-loop
simulation after memoryless one-step BC failed.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from closed_loop_sim_eval import quat_wxyz_to_pitch, temporary_cwd
from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    ROOT / "outputs" / "analysis" / "target_dataset_manifest_dynamic_roll_lateral_fix_robust_modes.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_SEQUENCE_REPLAY_SMOKE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_sequence_replay_smoke.json"
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"


@dataclass
class SequencePolicy:
    name: str
    source: str
    mode: str
    prefix_actions: np.ndarray
    window_actions: np.ndarray
    entry_ids: list[str]

    def action_at(self, tick: int) -> np.ndarray:
        if tick < self.prefix_actions.shape[0]:
            return self.prefix_actions[tick]
        if self.window_actions.shape[0] == 0:
            return self.prefix_actions[-1]
        index = (tick - self.prefix_actions.shape[0]) % self.window_actions.shape[0]
        return self.window_actions[index]


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def parse_csv_ints(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def pattern(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(int(value)) for value in values)


def signed_stats(values: Iterable[float]) -> dict[str, float] | None:
    data = np.asarray([float(value) for value in values if finite(value)], dtype=float)
    if data.size == 0:
        return None
    return {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "p50": percentile(data.tolist(), 50),
        "p95": percentile(data.tolist(), 95),
        "p99": percentile(data.tolist(), 99),
        "max": float(np.max(data)),
    }


def abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros_like(values)
    velocity = np.abs(np.diff(values, axis=0) / max(float(dt_s), 1.0e-9))
    return np.vstack([np.zeros((1, values.shape[1])), velocity])


def load_entry_sequence(entry: dict[str, Any]) -> SequencePolicy:
    source_path = Path(str(entry["source_path"]))
    mode = str(entry["mode"])
    start_tick = int(entry["start_tick"])
    end_tick = int(entry["end_tick"])
    records = [
        record
        for record in read_jsonl(source_path)
        if str(record.get("mode")) == mode and isinstance(record.get("action"), list)
    ]
    by_tick = {int(record["tick"]): record for record in records if "tick" in record}
    prefix = []
    for tick in range(start_tick):
        record = by_tick.get(tick)
        if record is None:
            continue
        action = np.asarray(record.get("action"), dtype=float).reshape(-1)
        if action.shape == (14,):
            prefix.append(action)
    window = []
    for tick in range(start_tick, end_tick + 1):
        record = by_tick.get(tick)
        if record is None:
            continue
        action = np.asarray(record.get("action"), dtype=float).reshape(-1)
        if action.shape == (14,):
            window.append(action)
    if not window:
        raise ValueError(f"entry {entry.get('entry_id')} has no usable action window")
    if not prefix:
        prefix = [window[0]]
    return SequencePolicy(
        name=f"{entry.get('entry_id')}_{source_path.stem}_{start_tick}_{end_tick}",
        source=source_path.name,
        mode=mode,
        prefix_actions=np.asarray(prefix, dtype=np.float64),
        window_actions=np.asarray(window, dtype=np.float64),
        entry_ids=[str(entry.get("entry_id"))],
    )


def average_sequences(name: str, sequences: list[SequencePolicy]) -> SequencePolicy:
    if not sequences:
        raise ValueError("cannot average an empty sequence list")
    prefix_len = min(seq.prefix_actions.shape[0] for seq in sequences)
    window_len = min(seq.window_actions.shape[0] for seq in sequences)
    prefix = np.mean([seq.prefix_actions[:prefix_len] for seq in sequences], axis=0)
    window = np.mean([seq.window_actions[:window_len] for seq in sequences], axis=0)
    return SequencePolicy(
        name=name,
        source="aggregate",
        mode="aggregate",
        prefix_actions=np.asarray(prefix, dtype=np.float64),
        window_actions=np.asarray(window, dtype=np.float64),
        entry_ids=[entry for seq in sequences for entry in seq.entry_ids],
    )


def load_sequence_policies(manifest_path: Path, args: argparse.Namespace) -> tuple[dict[str, Any], list[SequencePolicy]]:
    manifest = json.loads(manifest_path.read_text())
    entries = manifest.get("entries", [])
    if args.max_entries > 0:
        entries = entries[: args.max_entries]
    sequences = [load_entry_sequence(entry) for entry in entries]
    if args.policy_set == "per-entry":
        return manifest, sequences
    if args.policy_set == "aggregate":
        return manifest, [average_sequences("aggregate_phase_table", sequences)]
    return manifest, [average_sequences("aggregate_phase_table", sequences), *sequences]


def run_closed_loop_rollout(
    *,
    policies: list[SequencePolicy],
    args: argparse.Namespace,
) -> dict[str, Any]:
    if args.jax_platform != "auto":
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
    seeds = parse_csv_ints(args.seeds)

    with temporary_cwd(playground_path):
        config = joystick.default_config()
        env = joystick.Joystick(
            task=args.task,
            config=config,
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

    def step_sequence(state, action):
        state.info["command"] = command
        action = jp.clip(action, -1.0, 1.0)
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
        return state.replace(data=data, obs=obs, reward=reward, done=done), pre_rate_limit, sent_target

    refresh_obs_jit = jax.jit(refresh_obs)
    step_sequence_jit = jax.jit(step_sequence)
    sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))
    policy_results: dict[str, Any] = {}

    for policy in policies:
        seed_rows = {}
        for seed in seeds:
            state = env.reset(jax.random.PRNGKey(seed))
            state.info["command"] = command
            state = refresh_obs_jit(state)
            records = []
            for tick in range(sim_steps):
                action = policy.action_at(tick).astype(np.float32)
                state, pre_rate, sent_target = step_sequence_jit(state, jp.asarray(action))
                qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
                base_addr = int(env._floating_base_qpos_addr)
                quat = qpos[base_addr + 3 : base_addr + 7]
                local_linvel = np.asarray(
                    jax.device_get(env.get_local_linvel(state.data)), dtype=float
                )
                actual = np.asarray(
                    jax.device_get(env.get_actuator_joints_qpos(state.data.qpos)), dtype=float
                )
                contacts = np.asarray(jax.device_get(state.info["last_contact"]), dtype=bool)
                done = bool(np.asarray(jax.device_get(state.done)))
                records.append(
                    {
                        "tick": tick,
                        "time_s": tick * float(env.dt),
                        "seed": seed,
                        "policy_name": policy.name,
                        "action": action.astype(float).tolist(),
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
                        "local_linvel_m_s": local_linvel.astype(float).tolist(),
                        "foot_contacts": contacts.astype(int).tolist(),
                        "reward": float(np.asarray(jax.device_get(state.reward))),
                        "done": done,
                    }
                )
                if done:
                    break
            seed_rows[f"seed_{seed:03d}"] = summarize_rollout(records, args.command_x, float(env.dt))
        policy_results[policy.name] = {
            "source": policy.source,
            "mode": policy.mode,
            "entry_ids": policy.entry_ids,
            "prefix_len": int(policy.prefix_actions.shape[0]),
            "window_len": int(policy.window_actions.shape[0]),
            "status": classify_policy_rollout(seed_rows, args),
            "seeds": seed_rows,
        }

    return {
        "status": classify_overall(policy_results),
        "jax_backend": jax.default_backend(),
        "jax_devices": [str(device) for device in jax.devices()],
        "env": {
            "playground_root": str(playground_path),
            "task": args.task,
            "action_size": int(env.action_size),
            "observation_size": {key: list(value) for key, value in env.observation_size.items()},
            "actuator_names": list(env.actuator_names),
            "ctrl_dt": float(env.dt),
            "sim_dt": float(env.sim_dt),
            "action_scale": float(env._config.action_scale),
            "max_motor_velocity": float(env._config.max_motor_velocity),
        },
        "policies": policy_results,
    }


def summarize_rollout(records: list[dict[str, Any]], command_x: float, dt_s: float) -> dict[str, Any]:
    if not records:
        return {"status": "HOLD_NO_ROLLOUT_SAMPLES", "samples": 0}
    vx = [record["local_linvel_m_s"][0] for record in records]
    vy = [abs(record["local_linvel_m_s"][1]) for record in records]
    pitch = [abs(record["body_pitch_rad"]) for record in records]
    height = [record["base_height_m"] for record in records]
    action = np.asarray([record["action"] for record in records], dtype=float)
    sent = np.asarray([record["sent_target_rad"] for record in records], dtype=float)
    actual = np.asarray([record["actual_position_rad"] for record in records], dtype=float)
    tracking = np.abs(sent - actual) if sent.size and actual.size else np.zeros((0, 0))
    sent_velocity = abs_velocity(sent, dt_s) if sent.size else np.zeros((0, 0))
    contacts = Counter(pattern(record.get("foot_contacts", [])) for record in records)
    mean_vx = float(np.mean(vx)) if vx else None
    done = bool(records[-1].get("done"))
    return {
        "status": "PASS_ROLLOUT_COMPLETED" if not done else "HOLD_ROLLOUT_TERMINATED",
        "samples": len(records),
        "termination_reason": "fall_or_progress_failure" if done else "duration_complete",
        "mean_vx_m_s": mean_vx,
        "track_ratio": mean_vx / float(command_x) if mean_vx is not None and abs(command_x) > 1e-9 else None,
        "vy_abs_p95_m_s": percentile(vy, 95),
        "body_pitch_abs_p95_rad": percentile(pitch, 95),
        "base_height_min_m": float(np.min(height)) if height else None,
        "action_saturation_pct": float(np.mean(np.abs(action) >= 0.999) * 100.0) if action.size else None,
        "action_abs_mean": float(np.mean(np.abs(action))) if action.size else None,
        "sent_target_velocity_p95_rad_s": percentile(sent_velocity.reshape(-1).tolist(), 95)
        if sent_velocity.size
        else None,
        "joint_tracking_p95_rad": percentile(tracking.reshape(-1).tolist(), 95)
        if tracking.size
        else None,
        "contact_pct": {key: float(value / len(records) * 100.0) for key, value in sorted(contacts.items())},
    }


def classify_policy_rollout(rows: dict[str, Any], args: argparse.Namespace) -> str:
    if not rows:
        return "HOLD_SEQUENCE_REPLAY_NOT_RUN"
    if any(row.get("status") != "PASS_ROLLOUT_COMPLETED" for row in rows.values()):
        return "HOLD_SEQUENCE_REPLAY_TERMINATED"
    if any((row.get("mean_vx_m_s") or 0.0) < args.min_mean_vx for row in rows.values()):
        return "HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION"
    if any((row.get("vy_abs_p95_m_s") or 0.0) > args.max_vy_abs_p95 for row in rows.values()):
        return "HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE"
    if any((row.get("body_pitch_abs_p95_rad") or 0.0) > args.max_body_pitch_abs_p95 for row in rows.values()):
        return "HOLD_SEQUENCE_REPLAY_PITCH_UNSTABLE"
    if any((row.get("base_height_min_m") or 0.0) < args.min_base_height for row in rows.values()):
        return "HOLD_SEQUENCE_REPLAY_HEIGHT_COLLAPSE"
    if any((row.get("sent_target_velocity_p95_rad_s") or 0.0) > args.max_sent_velocity_p95 for row in rows.values()):
        return "HOLD_SEQUENCE_REPLAY_ABOVE_ENVELOPE"
    return "PASS_SEQUENCE_REPLAY_FORWARD_MOTION"


def classify_overall(policies: dict[str, Any]) -> str:
    if not policies:
        return "HOLD_SEQUENCE_REPLAY_NOT_RUN"
    if any(row.get("status") == "PASS_SEQUENCE_REPLAY_FORWARD_MOTION" for row in policies.values()):
        return "PASS_SEQUENCE_REPLAY_FORWARD_MOTION"
    statuses = Counter(str(row.get("status")) for row in policies.values())
    if statuses:
        return statuses.most_common(1)[0][0]
    return "HOLD_SEQUENCE_REPLAY_NO_PASS"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    thresholds = payload["thresholds"]
    lines = [
        "# Target Sequence Replay Smoke",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline sequence-preservation diagnostic over curated target windows.",
        "It replays target action tables in closed-loop sim; it is not PPO, BC training, or a deployable policy.",
        "",
        "## Dataset",
        "",
        f"- manifest: `{payload['manifest_path']}`",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- manifest_status: `{payload['manifest_status']}`",
        f"- policy_set: `{payload['policy_set']}`",
        f"- sequence_policies: `{payload['sequence_policy_count']}`",
        f"- command_x: `{fmt(payload['command_x'])}`",
        f"- duration_s: `{fmt(payload['duration_s'])}`",
        f"- seeds: `{payload['seeds']}`",
        "",
        "## Gates",
        "",
        f"- min_mean_vx_m_s: `{fmt(thresholds['min_mean_vx'])}`",
        f"- max_vy_abs_p95_m_s: `{fmt(thresholds['max_vy_abs_p95'])}`",
        f"- max_body_pitch_abs_p95_rad: `{fmt(thresholds['max_body_pitch_abs_p95'])}`",
        f"- min_base_height_m: `{fmt(thresholds['min_base_height'])}`",
        f"- max_sent_velocity_p95_rad_s: `{fmt(thresholds['max_sent_velocity_p95'])}`",
        "",
        "## Closed-Loop Sequence Replay",
        "",
    ]
    rollout = payload.get("rollout")
    if rollout is None:
        lines.extend(["status: `HOLD_SEQUENCE_REPLAY_NOT_RUN`", ""])
    else:
        lines.extend(
            [
                f"status: `{rollout['status']}`",
                f"jax_backend: `{rollout.get('jax_backend')}`",
                f"jax_devices: `{rollout.get('jax_devices')}`",
                "",
                "| policy | status | seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |",
                "|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for name, policy in sorted((rollout.get("policies") or {}).items()):
            for seed, row in sorted((policy.get("seeds") or {}).items()):
                lines.append(
                    "| {policy} | `{status}` | {seed} | {samples} | {term} | {vx} | {ratio} | {vy} | {pitch} | {height} | {sent} | {track} |".format(
                        policy=name[:42],
                        status=policy.get("status"),
                        seed=seed,
                        samples=row.get("samples", 0),
                        term=row.get("termination_reason"),
                        vx=fmt(row.get("mean_vx_m_s")),
                        ratio=fmt(row.get("track_ratio")),
                        vy=fmt(row.get("vy_abs_p95_m_s")),
                        pitch=fmt(row.get("body_pitch_abs_p95_rad")),
                        height=fmt(row.get("base_height_min_m")),
                        sent=fmt(row.get("sent_target_velocity_p95_rad_s")),
                        track=fmt(row.get("joint_tracking_p95_rad")),
                    )
                )
        lines.extend(
            [
                "",
                "### Policy Table Summary",
                "",
                "| policy | source | prefix_len | window_len | entry_count | status |",
                "|---|---|---:|---:|---:|---|",
            ]
        )
        for name, policy in sorted((rollout.get("policies") or {}).items()):
            lines.append(
                "| {name} | {source} | {prefix} | {window} | {entries} | `{status}` |".format(
                    name=name[:56],
                    source=policy.get("source"),
                    prefix=policy.get("prefix_len"),
                    window=policy.get("window_len"),
                    entries=len(policy.get("entry_ids") or []),
                    status=policy.get("status"),
                )
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Passing this smoke would justify a sequence/phase-aware imitation learner.",
            "- Failing this smoke means target timing alone is not enough; do not launch PPO from these windows.",
            "- This diagnostic preserves rollout timing; it does not test a memoryless obs-to-action clone.",
            "- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--duration-s", type=float, default=3.0)
    parser.add_argument("--seeds", default="0,2")
    parser.add_argument("--policy-set", choices=["aggregate", "per-entry", "all"], default="all")
    parser.add_argument("--max-entries", type=int, default=0)
    parser.add_argument(
        "--jax-platform",
        choices=["auto", "cpu", "gpu"],
        default="cpu",
        help="Use cpu by default because local ROCm/MJX remains unstable.",
    )
    parser.add_argument("--no-rollout", action="store_true")
    parser.add_argument("--min-mean-vx", type=float, default=0.02)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-body-pitch-abs-p95", type=float, default=0.25)
    parser.add_argument("--min-base-height", type=float, default=0.10)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=3.75)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest, policies = load_sequence_policies(manifest_path, args)
    rollout = None
    status = "HOLD_SEQUENCE_REPLAY_NOT_RUN"
    if not args.no_rollout:
        rollout = run_closed_loop_rollout(policies=policies, args=args)
        status = rollout["status"]

    payload = {
        "status": status,
        "manifest_path": str(manifest_path),
        "dataset_id": manifest.get("dataset_id"),
        "manifest_status": manifest.get("status"),
        "policy_set": args.policy_set,
        "sequence_policy_count": len(policies),
        "command_x": float(args.command_x),
        "duration_s": float(args.duration_s),
        "seeds": parse_csv_ints(args.seeds),
        "thresholds": {
            "min_mean_vx": args.min_mean_vx,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_body_pitch_abs_p95": args.max_body_pitch_abs_p95,
            "min_base_height": args.min_base_height,
            "max_sent_velocity_p95": args.max_sent_velocity_p95,
        },
        "policies": [
            {
                "name": policy.name,
                "source": policy.source,
                "mode": policy.mode,
                "prefix_len": int(policy.prefix_actions.shape[0]),
                "window_len": int(policy.window_actions.shape[0]),
                "entry_ids": policy.entry_ids,
            }
            for policy in policies
        ],
        "rollout": rollout,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"dataset_id={manifest.get('dataset_id')}")
    print(f"sequence_policies={len(policies)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
