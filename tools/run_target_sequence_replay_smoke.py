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
import re
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
DEFAULT_SOFT_PRIOR_CONFIG = ROOT / "outputs" / "analysis" / "soft_prior_fragment_config.json"


@dataclass
class SequencePolicy:
    name: str
    source: str
    mode: str
    prefix_actions: np.ndarray
    window_actions: np.ndarray
    prefix_contacts: list[tuple[int, int]]
    window_contacts: list[tuple[int, int]]
    window_body_pitch_abs: np.ndarray
    window_base_height: np.ndarray
    window_vy_abs: np.ndarray
    entry_ids: list[str]

    def action_at(self, tick: int) -> np.ndarray:
        if tick < self.prefix_actions.shape[0]:
            return self.prefix_actions[tick]
        if self.window_actions.shape[0] == 0:
            return self.prefix_actions[-1]
        index = (tick - self.prefix_actions.shape[0]) % self.window_actions.shape[0]
        return self.window_actions[index]


@dataclass
class PhaseState:
    phase_index: int = 0
    hold_count: int = 0
    holds: int = 0
    skips: int = 0
    contact_mismatches: int = 0
    phase_indices: list[int] | None = None

    def __post_init__(self) -> None:
        if self.phase_indices is None:
            self.phase_indices = []


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def parse_csv_ints(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def safe_slug(value: str, *, max_len: int = 96) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return (slug or "unknown")[:max_len]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def pattern(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(int(value)) for value in values)


def contact_tuple(values: Any) -> tuple[int, int]:
    if isinstance(values, np.ndarray):
        values = values.astype(int).reshape(-1).tolist()
    if not isinstance(values, list | tuple) or len(values) < 2:
        return (0, 0)
    return (int(values[0]), int(values[1]))


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
    prefix_contacts = []
    for tick in range(start_tick):
        record = by_tick.get(tick)
        if record is None:
            continue
        action = np.asarray(record.get("action"), dtype=float).reshape(-1)
        if action.shape == (14,):
            prefix.append(action)
            prefix_contacts.append(contact_tuple(record.get("foot_contacts")))
    window = []
    window_contacts = []
    window_body_pitch_abs = []
    window_base_height = []
    window_vy_abs = []
    for tick in range(start_tick, end_tick + 1):
        record = by_tick.get(tick)
        if record is None:
            continue
        action = np.asarray(record.get("action"), dtype=float).reshape(-1)
        if action.shape == (14,):
            window.append(action)
            window_contacts.append(contact_tuple(record.get("foot_contacts")))
            window_body_pitch_abs.append(abs(float(record.get("body_pitch_rad", 0.0))))
            window_base_height.append(float(record.get("base_height_m", 0.0)))
            local_linvel = record.get("local_linvel_m_s") or [0.0, 0.0, 0.0]
            window_vy_abs.append(abs(float(local_linvel[1])) if len(local_linvel) > 1 else 0.0)
    if not window:
        raise ValueError(f"entry {entry.get('entry_id')} has no usable action window")
    if not prefix:
        prefix = [window[0]]
        prefix_contacts = [window_contacts[0]]
    return SequencePolicy(
        name=f"{entry.get('entry_id')}_{source_path.stem}_{start_tick}_{end_tick}",
        source=source_path.name,
        mode=mode,
        prefix_actions=np.asarray(prefix, dtype=np.float64),
        window_actions=np.asarray(window, dtype=np.float64),
        prefix_contacts=prefix_contacts,
        window_contacts=window_contacts,
        window_body_pitch_abs=np.asarray(window_body_pitch_abs, dtype=np.float64),
        window_base_height=np.asarray(window_base_height, dtype=np.float64),
        window_vy_abs=np.asarray(window_vy_abs, dtype=np.float64),
        entry_ids=[str(entry.get("entry_id"))],
    )


def average_sequences(name: str, sequences: list[SequencePolicy]) -> SequencePolicy:
    if not sequences:
        raise ValueError("cannot average an empty sequence list")
    prefix_len = min(seq.prefix_actions.shape[0] for seq in sequences)
    window_len = min(seq.window_actions.shape[0] for seq in sequences)
    prefix = np.mean([seq.prefix_actions[:prefix_len] for seq in sequences], axis=0)
    window = np.mean([seq.window_actions[:window_len] for seq in sequences], axis=0)
    prefix_contacts = []
    for index in range(prefix_len):
        counter = Counter(seq.prefix_contacts[index] for seq in sequences if len(seq.prefix_contacts) > index)
        prefix_contacts.append(counter.most_common(1)[0][0] if counter else (0, 0))
    window_contacts = []
    for index in range(window_len):
        counter = Counter(seq.window_contacts[index] for seq in sequences if len(seq.window_contacts) > index)
        window_contacts.append(counter.most_common(1)[0][0] if counter else (0, 0))
    return SequencePolicy(
        name=name,
        source="aggregate",
        mode="aggregate",
        prefix_actions=np.asarray(prefix, dtype=np.float64),
        window_actions=np.asarray(window, dtype=np.float64),
        prefix_contacts=prefix_contacts,
        window_contacts=window_contacts,
        window_body_pitch_abs=np.mean([seq.window_body_pitch_abs[:window_len] for seq in sequences], axis=0),
        window_base_height=np.mean([seq.window_base_height[:window_len] for seq in sequences], axis=0),
        window_vy_abs=np.mean([seq.window_vy_abs[:window_len] for seq in sequences], axis=0),
        entry_ids=[entry for seq in sequences for entry in seq.entry_ids],
    )


def apply_periodic_seam_correction(policy: SequencePolicy) -> SequencePolicy:
    """Remove the linear discontinuity between window end and next window start.

    The curated windows are short successful segments, not guaranteed periodic
    cycles. Looping them with a hard jump can erase forward progress. This
    correction is a diagnostic adapter: it distributes the end-start action
    delta across the window so the final action meets the first action.
    """
    window = np.asarray(policy.window_actions, dtype=np.float64)
    if window.shape[0] < 2:
        return policy
    seam = window[-1] - window[0]
    ramp = np.linspace(0.0, 1.0, window.shape[0], dtype=np.float64).reshape(-1, 1)
    corrected = np.clip(window - ramp * seam.reshape(1, -1), -1.0, 1.0)
    return SequencePolicy(
        name=f"{policy.name}_seam_corrected",
        source=policy.source,
        mode=policy.mode,
        prefix_actions=policy.prefix_actions,
        window_actions=corrected,
        prefix_contacts=policy.prefix_contacts,
        window_contacts=policy.window_contacts,
        window_body_pitch_abs=policy.window_body_pitch_abs,
        window_base_height=policy.window_base_height,
        window_vy_abs=policy.window_vy_abs,
        entry_ids=policy.entry_ids,
    )


def load_sequence_policies(manifest_path: Path, args: argparse.Namespace) -> tuple[dict[str, Any], list[SequencePolicy]]:
    manifest = json.loads(manifest_path.read_text())
    if args.soft_prior_config:
        return manifest, [load_soft_prior_policy(Path(args.soft_prior_config))]
    entries = manifest.get("entries", [])
    if args.max_entries > 0:
        entries = entries[: args.max_entries]
    sequences = [load_entry_sequence(entry) for entry in entries]
    if args.policy_set == "per-entry":
        policies = sequences
    elif args.policy_set == "aggregate":
        policies = [average_sequences("aggregate_phase_table", sequences)]
    else:
        policies = [average_sequences("aggregate_phase_table", sequences), *sequences]
    if args.periodic_seam_correction:
        policies = [apply_periodic_seam_correction(policy) for policy in policies]
    return manifest, policies


def load_soft_prior_policy(config_path: Path) -> SequencePolicy:
    config = json.loads(config_path.read_text())
    prior = config.get("prior") or {}
    action_mean = np.asarray(prior.get("action_mean") or [], dtype=np.float64)
    joint_indices = [int(index) for index in prior.get("joint_indices") or []]
    if action_mean.ndim != 2 or action_mean.shape[1] != len(joint_indices):
        raise ValueError(f"invalid soft-prior action_mean/joint_indices in {config_path}")
    full_actions = np.zeros((action_mean.shape[0], 14), dtype=np.float64)
    for column, joint_index in enumerate(joint_indices):
        if joint_index < 0 or joint_index >= 14:
            raise ValueError(f"soft-prior joint index out of range: {joint_index}")
        full_actions[:, joint_index] = action_mean[:, column]
    contacts = []
    for item in prior.get("phase_contact_mode") or []:
        text = str(item)
        if len(text) >= 2 and all(char in "01" for char in text[:2]):
            contacts.append((int(text[0]), int(text[1])))
        else:
            contacts.append((0, 0))
    if len(contacts) != full_actions.shape[0]:
        contacts = [(0, 0)] * full_actions.shape[0]
    return SequencePolicy(
        name=f"soft_prior_pitch_chain_{config.get('dataset_id', 'unknown')}",
        source=str(config_path),
        mode="soft_prior_pitch_chain_mean",
        prefix_actions=full_actions[:1],
        window_actions=full_actions,
        prefix_contacts=contacts[:1],
        window_contacts=contacts,
        window_body_pitch_abs=np.zeros(full_actions.shape[0], dtype=np.float64),
        window_base_height=np.zeros(full_actions.shape[0], dtype=np.float64),
        window_vy_abs=np.zeros(full_actions.shape[0], dtype=np.float64),
        entry_ids=[str(config.get("dataset_id", config_path.name))],
    )


def contact_mismatch_count(left: tuple[int, int], right: tuple[int, int]) -> int:
    return int(left[0] != right[0]) + int(left[1] != right[1])


def choose_phase_action(
    *,
    policy: SequencePolicy,
    tick: int,
    phase_state: PhaseState,
    actual_contact: tuple[int, int],
    body_pitch_abs: float,
    base_height: float,
    vy_abs: float,
    args: argparse.Namespace,
) -> tuple[np.ndarray, dict[str, Any]]:
    prefix_len = int(policy.prefix_actions.shape[0])
    if tick < prefix_len:
        prefix_index = min(tick, prefix_len - 1)
        return policy.prefix_actions[prefix_index], {
            "phase_mode": "prefix",
            "phase_index": None,
            "target_contact": policy.prefix_contacts[prefix_index],
            "actual_contact": actual_contact,
            "phase_hold": False,
            "phase_skip": 0,
            "contact_mismatch": contact_mismatch_count(
                actual_contact, policy.prefix_contacts[prefix_index]
            ),
        }

    window_len = int(policy.window_actions.shape[0])
    base_index = phase_state.phase_index % window_len
    phase_skip = 0
    phase_hold = False
    chosen = base_index

    if args.phase_adapter == "fixed_time":
        chosen = (tick - prefix_len) % window_len
        phase_state.phase_index = (chosen + 1) % window_len
    elif args.phase_adapter == "contact_hold":
        mismatch = contact_mismatch_count(actual_contact, policy.window_contacts[base_index])
        chosen = base_index
        if mismatch and phase_state.hold_count < args.max_phase_hold_ticks:
            phase_hold = True
            phase_state.hold_count += 1
            phase_state.holds += 1
        else:
            phase_state.hold_count = 0
            phase_state.phase_index = (base_index + 1) % window_len
    elif args.phase_adapter == "contact_match":
        candidates = [(base_index + offset) % window_len for offset in range(args.phase_lookahead + 1)]
        matches = [
            (offset, index)
            for offset, index in enumerate(candidates)
            if contact_mismatch_count(actual_contact, policy.window_contacts[index]) == 0
        ]
        phase_skip, chosen = matches[0] if matches else (0, base_index)
        phase_state.skips += phase_skip
        phase_state.phase_index = (chosen + 1) % window_len
    elif args.phase_adapter == "state_match":
        best_score = None
        best_offset = 0
        best_index = base_index
        for offset in range(args.phase_lookahead + 1):
            index = (base_index + offset) % window_len
            score = (
                args.contact_mismatch_weight
                * contact_mismatch_count(actual_contact, policy.window_contacts[index])
            )
            score += args.pitch_match_weight * abs(
                float(body_pitch_abs) - float(policy.window_body_pitch_abs[index])
            )
            score += args.height_match_weight * abs(
                float(base_height) - float(policy.window_base_height[index])
            )
            score += args.vy_match_weight * abs(float(vy_abs) - float(policy.window_vy_abs[index]))
            score += args.phase_skip_weight * offset
            if best_score is None or score < best_score:
                best_score = score
                best_offset = offset
                best_index = index
        phase_skip = best_offset
        chosen = best_index
        phase_state.skips += phase_skip
        phase_state.phase_index = (chosen + 1) % window_len
    else:
        raise ValueError(f"unsupported phase adapter {args.phase_adapter}")

    target_contact = policy.window_contacts[chosen]
    mismatch_count = contact_mismatch_count(actual_contact, target_contact)
    if mismatch_count:
        phase_state.contact_mismatches += 1
    phase_state.phase_indices.append(int(chosen))
    return policy.window_actions[chosen], {
        "phase_mode": args.phase_adapter,
        "phase_index": int(chosen),
        "target_contact": target_contact,
        "actual_contact": actual_contact,
        "phase_hold": phase_hold,
        "phase_skip": int(phase_skip),
        "contact_mismatch": int(mismatch_count),
    }


def phase_summary(phase_state: PhaseState, records: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    duration_s = max(len(records) * float(dt_s), 1.0e-9)
    phase_records = [record for record in records if record.get("phase_index") is not None]
    mismatches = [
        int(record.get("contact_mismatch", 0)) > 0
        for record in phase_records
    ]
    return {
        "holds": int(phase_state.holds),
        "skips": int(phase_state.skips),
        "holds_per_s": float(phase_state.holds / duration_s),
        "skips_per_s": float(phase_state.skips / duration_s),
        "contact_mismatch_pct": float(np.mean(mismatches) * 100.0) if mismatches else None,
        "phase_index_histogram": {
            str(key): int(value)
            for key, value in sorted(Counter(phase_state.phase_indices or []).items())
        },
    }


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
    trace_root = Path(args.trace_dir).resolve() if args.trace_dir else None
    if trace_root is not None:
        trace_root.mkdir(parents=True, exist_ok=True)

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
        if "command_progress_ratio" in state.info:
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
            phase_state = PhaseState()
            state = env.reset(jax.random.PRNGKey(seed))
            state.info["command"] = command
            state = refresh_obs_jit(state)
            records = []
            for tick in range(sim_steps):
                pre_qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
                base_addr = int(env._floating_base_qpos_addr)
                pre_quat = pre_qpos[base_addr + 3 : base_addr + 7]
                pre_local_linvel = np.asarray(
                    jax.device_get(env.get_local_linvel(state.data)), dtype=float
                )
                actual_contact = contact_tuple(np.asarray(jax.device_get(state.info["last_contact"])))
                action, phase_info = choose_phase_action(
                    policy=policy,
                    tick=tick,
                    phase_state=phase_state,
                    actual_contact=actual_contact,
                    body_pitch_abs=abs(quat_wxyz_to_pitch(pre_quat)),
                    base_height=float(pre_qpos[base_addr + 2]),
                    vy_abs=abs(float(pre_local_linvel[1])),
                    args=args,
                )
                action = action.astype(np.float32)
                state, pre_rate, sent_target = step_sequence_jit(state, jp.asarray(action))
                qpos = np.asarray(jax.device_get(state.data.qpos), dtype=float)
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
                        "mode": policy.name,
                        "policy_name": policy.name,
                        "source_mode": policy.mode,
                        "phase_adapter": args.phase_adapter,
                        "phase_index": phase_info["phase_index"],
                        "phase_hold": phase_info["phase_hold"],
                        "phase_skip": phase_info["phase_skip"],
                        "target_contact": list(phase_info["target_contact"]),
                        "actual_contact": list(phase_info["actual_contact"]),
                        "contact_mismatch": phase_info["contact_mismatch"],
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
            trace_path = None
            if trace_root is not None:
                trace_path = trace_root / safe_slug(policy.name) / f"seed_{seed:03d}.jsonl"
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                trace_path.write_text("".join(json.dumps(record) + "\n" for record in records))
            seed_rows[f"seed_{seed:03d}"] = summarize_rollout(
                records,
                args.command_x,
                float(env.dt),
                phase_state=phase_state,
            )
            if trace_path is not None:
                seed_rows[f"seed_{seed:03d}"]["trace"] = str(trace_path)
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


def summarize_rollout(
    records: list[dict[str, Any]],
    command_x: float,
    dt_s: float,
    *,
    phase_state: PhaseState | None = None,
) -> dict[str, Any]:
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
    summary = {
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
    if phase_state is not None:
        summary["phase"] = phase_summary(phase_state, records, dt_s)
    return summary


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


def map_soft_prior_status(status: str) -> str:
    mapping = {
        "PASS_SEQUENCE_REPLAY_FORWARD_MOTION": "PASS_SOFT_PRIOR_SMOKE",
        "HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION": "HOLD_SOFT_PRIOR_FREEZE",
        "HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE": "HOLD_SOFT_PRIOR_LATERAL_UNSTABLE",
        "HOLD_SEQUENCE_REPLAY_PITCH_UNSTABLE": "HOLD_SOFT_PRIOR_LUNGE",
        "HOLD_SEQUENCE_REPLAY_HEIGHT_COLLAPSE": "HOLD_SOFT_PRIOR_CONTACT_STUCK",
        "HOLD_SEQUENCE_REPLAY_ABOVE_ENVELOPE": "HOLD_SOFT_PRIOR_PRIOR_TOO_FAST",
        "HOLD_SEQUENCE_REPLAY_TERMINATED": "HOLD_SOFT_PRIOR_LUNGE",
    }
    return mapping.get(status, status)


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
        f"- periodic_seam_correction: `{payload['periodic_seam_correction']}`",
        f"- soft_prior_config: `{payload.get('soft_prior_config') or 'None'}`",
        f"- phase_adapter: `{payload['phase_adapter']}`",
        f"- trace_dir: `{payload.get('trace_dir') or 'None'}`",
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
                "### Phase Adapter Summary",
                "",
                "| policy | seed | holds/s | skips/s | contact_mismatch_pct | phase_bins |",
                "|---|---|---:|---:|---:|---:|",
            ]
        )
        for name, policy in sorted((rollout.get("policies") or {}).items()):
            for seed, row in sorted((policy.get("seeds") or {}).items()):
                phase = row.get("phase") or {}
                lines.append(
                    "| {policy} | {seed} | {holds} | {skips} | {mismatch} | {bins} |".format(
                        policy=name[:42],
                        seed=seed,
                        holds=fmt(phase.get("holds_per_s")),
                        skips=fmt(phase.get("skips_per_s")),
                        mismatch=fmt(phase.get("contact_mismatch_pct")),
                        bins=len(phase.get("phase_index_histogram") or {}),
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
    parser.add_argument(
        "--soft-prior-config",
        default=None,
        help=(
            "Optional compact soft-prior config. When set, ignore manifest action "
            "tables and replay the pitch-chain mean prior as a default-off smoke."
        ),
    )
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--duration-s", type=float, default=3.0)
    parser.add_argument("--seeds", default="0,2")
    parser.add_argument("--policy-set", choices=["aggregate", "per-entry", "all"], default="all")
    parser.add_argument(
        "--phase-adapter",
        choices=["fixed_time", "contact_hold", "contact_match", "state_match"],
        default="fixed_time",
    )
    parser.add_argument("--max-phase-hold-ticks", type=int, default=3)
    parser.add_argument("--phase-lookahead", type=int, default=8)
    parser.add_argument("--contact-mismatch-weight", type=float, default=10.0)
    parser.add_argument("--pitch-match-weight", type=float, default=2.0)
    parser.add_argument("--height-match-weight", type=float, default=5.0)
    parser.add_argument("--vy-match-weight", type=float, default=1.0)
    parser.add_argument("--phase-skip-weight", type=float, default=0.1)
    parser.add_argument(
        "--periodic-seam-correction",
        action="store_true",
        help="Linearly remove the action jump between the end and start of looped windows.",
    )
    parser.add_argument("--max-entries", type=int, default=0)
    parser.add_argument(
        "--trace-dir",
        default=None,
        help="Optional JSONL trace output directory. Raw traces are not intended for git.",
    )
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
    if args.soft_prior_config:
        status = map_soft_prior_status(status)

    payload = {
        "status": status,
        "manifest_path": str(manifest_path),
        "dataset_id": manifest.get("dataset_id"),
        "manifest_status": manifest.get("status"),
        "policy_set": args.policy_set,
        "periodic_seam_correction": bool(args.periodic_seam_correction),
        "soft_prior_config": args.soft_prior_config,
        "phase_adapter": args.phase_adapter,
        "trace_dir": args.trace_dir,
        "phase_adapter_config": {
            "max_phase_hold_ticks": args.max_phase_hold_ticks,
            "phase_lookahead": args.phase_lookahead,
            "contact_mismatch_weight": args.contact_mismatch_weight,
            "pitch_match_weight": args.pitch_match_weight,
            "height_match_weight": args.height_match_weight,
            "vy_match_weight": args.vy_match_weight,
            "phase_skip_weight": args.phase_skip_weight,
        },
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
