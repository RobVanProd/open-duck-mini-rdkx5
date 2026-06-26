#!/usr/bin/env python3
"""Run a tiny behavior-cloning smoke on the curated target dataset.

This is an offline diagnostic. It fits a tiny supervised obs[101] ->
action[14] model from curated target windows and can optionally replay that
model in the Open Duck Playground sim. It does not run PPO, deploy, SSH, or
touch the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from closed_loop_sim_eval import quat_wxyz_to_pitch, temporary_cwd
from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "outputs" / "analysis" / "target_dataset_obs_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_DATASET_BC_SMOKE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_dataset_bc_smoke.json"
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
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
class SampleSet:
    observations: np.ndarray
    actions: np.ndarray
    sources: list[str]
    modes: list[str]
    ticks: list[int]


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def parse_csv_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


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


def load_manifest_samples(manifest_path: Path) -> tuple[dict[str, Any], SampleSet, list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text())
    observations: list[list[float]] = []
    actions: list[list[float]] = []
    sources: list[str] = []
    modes: list[str] = []
    ticks: list[int] = []
    loaded_entries = []

    for entry in manifest.get("entries", []):
        source_path = Path(str(entry["source_path"]))
        records = [
            record
            for record in read_jsonl(source_path)
            if str(record.get("mode")) == str(entry.get("mode"))
            and int(entry["start_tick"]) <= int(record.get("tick", -1)) <= int(entry["end_tick"])
        ]
        entry_samples = 0
        for record in records:
            obs = (
                record.get("observation")
                or record.get("obs_state")
                or record.get("obs")
                or record.get("raw_vector")
                or record.get("observation_raw_vector")
            )
            action = record.get("action")
            if obs is None or action is None:
                continue
            obs_arr = np.asarray(obs, dtype=float).reshape(-1)
            action_arr = np.asarray(action, dtype=float).reshape(-1)
            if obs_arr.shape != (101,) or action_arr.shape != (14,):
                continue
            observations.append(obs_arr.astype(float).tolist())
            actions.append(action_arr.astype(float).tolist())
            sources.append(str(entry.get("source_name")))
            modes.append(str(entry.get("mode")))
            ticks.append(int(record.get("tick", -1)))
            entry_samples += 1
        row = dict(entry)
        row["loaded_samples"] = entry_samples
        loaded_entries.append(row)

    if not observations:
        raise ValueError(f"no BC-ready obs/action samples found in {manifest_path}")

    samples = SampleSet(
        observations=np.asarray(observations, dtype=np.float64),
        actions=np.asarray(actions, dtype=np.float64),
        sources=sources,
        modes=modes,
        ticks=ticks,
    )
    return manifest, samples, loaded_entries


def fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std < 1.0e-8, 1.0, std)
    x_norm = (x - mean) / std
    design = np.concatenate([x_norm, np.ones((x_norm.shape[0], 1))], axis=1)
    reg = np.eye(design.shape[1], dtype=np.float64) * float(alpha)
    reg[-1, -1] = 0.0
    weights = np.linalg.solve(design.T @ design + reg, design.T @ y)
    return weights, np.stack([mean, std], axis=0)


def predict_ridge(x: np.ndarray, weights: np.ndarray, norm: np.ndarray) -> np.ndarray:
    mean, std = norm
    x_norm = (x - mean) / std
    design = np.concatenate([x_norm, np.ones((x_norm.shape[0], 1))], axis=1)
    return np.clip(design @ weights, -1.0, 1.0)


def predict_knn(
    x: np.ndarray,
    train_x: np.ndarray,
    train_y: np.ndarray,
    norm: np.ndarray,
    k: int,
) -> np.ndarray:
    mean, std = norm
    x_norm = (x - mean) / std
    train_norm = (train_x - mean) / std
    k = max(1, min(int(k), train_x.shape[0]))
    rows = []
    for row in x_norm:
        dist = np.linalg.norm(train_norm - row.reshape(1, -1), axis=1)
        idx = np.argpartition(dist, k - 1)[:k]
        rows.append(np.mean(train_y[idx], axis=0))
    return np.clip(np.asarray(rows, dtype=np.float64), -1.0, 1.0)


def parse_hidden_sizes(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def init_mlp_params(
    input_dim: int,
    hidden_sizes: Sequence[int],
    output_dim: int,
    seed: int,
) -> list[tuple[np.ndarray, np.ndarray]]:
    rng = np.random.default_rng(int(seed))
    dims = [int(input_dim), *[int(size) for size in hidden_sizes], int(output_dim)]
    params = []
    for in_dim, out_dim in zip(dims[:-1], dims[1:], strict=True):
        scale = math.sqrt(2.0 / max(in_dim + out_dim, 1))
        weights = rng.normal(0.0, scale, size=(in_dim, out_dim)).astype(np.float64)
        bias = np.zeros((out_dim,), dtype=np.float64)
        params.append((weights, bias))
    return params


def predict_mlp_np(
    x: np.ndarray,
    params: list[tuple[np.ndarray, np.ndarray]],
    norm: np.ndarray,
) -> np.ndarray:
    mean, std = norm
    z = (x - mean) / std
    for index, (weights, bias) in enumerate(params):
        z = z @ weights + bias
        if index < len(params) - 1:
            z = np.tanh(z)
    return np.clip(z, -1.0, 1.0)


def fit_mlp_jax(
    x: np.ndarray,
    y: np.ndarray,
    *,
    hidden_sizes: Sequence[int],
    steps: int,
    batch_size: int,
    learning_rate: float,
    seed: int,
) -> dict[str, Any]:
    import jax
    import jax.numpy as jnp
    import optax

    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std < 1.0e-8, 1.0, std)
    x_norm = ((x - mean) / std).astype(np.float32)
    y_f32 = y.astype(np.float32)
    params_np = init_mlp_params(x.shape[1], hidden_sizes, y.shape[1], seed)
    params = [(jnp.asarray(weights, dtype=jnp.float32), jnp.asarray(bias, dtype=jnp.float32)) for weights, bias in params_np]
    optimizer = optax.adam(float(learning_rate))
    opt_state = optimizer.init(params)

    def forward(model_params, batch_x):
        z = batch_x
        for index, (weights, bias) in enumerate(model_params):
            z = z @ weights + bias
            if index < len(model_params) - 1:
                z = jnp.tanh(z)
        return z

    def loss_fn(model_params, batch_x, batch_y):
        pred = forward(model_params, batch_x)
        return jnp.mean((pred - batch_y) ** 2)

    @jax.jit
    def train_step(model_params, state, batch_x, batch_y):
        loss, grads = jax.value_and_grad(loss_fn)(model_params, batch_x, batch_y)
        updates, state = optimizer.update(grads, state, model_params)
        model_params = optax.apply_updates(model_params, updates)
        return model_params, state, loss

    rng = np.random.default_rng(int(seed) + 17)
    n_samples = int(x_norm.shape[0])
    batch_size = max(1, min(int(batch_size), n_samples))
    steps = max(1, int(steps))
    history = []
    log_every = max(1, steps // 10)
    for step in range(steps):
        indices = rng.integers(0, n_samples, size=batch_size)
        params, opt_state, loss = train_step(
            params,
            opt_state,
            jnp.asarray(x_norm[indices], dtype=jnp.float32),
            jnp.asarray(y_f32[indices], dtype=jnp.float32),
        )
        if step == 0 or step == steps - 1 or (step + 1) % log_every == 0:
            history.append({"step": int(step + 1), "loss": float(jax.device_get(loss))})

    params_out = [
        (np.asarray(jax.device_get(weights), dtype=np.float64), np.asarray(jax.device_get(bias), dtype=np.float64))
        for weights, bias in params
    ]
    pred = predict_mlp_np(x, params_out, np.stack([mean, std], axis=0))
    parameter_count = int(sum(weights.size + bias.size for weights, bias in params_out))
    return {
        "kind": "mlp",
        "params": params_out,
        "norm": np.stack([mean, std], axis=0),
        "train": action_metrics(y, pred),
        "history": history,
        "hidden_sizes": [int(size) for size in hidden_sizes],
        "steps": steps,
        "batch_size": batch_size,
        "learning_rate": float(learning_rate),
        "parameter_count": parameter_count,
        "sample_to_parameter_ratio": float(n_samples / max(parameter_count, 1)),
    }


def action_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    error = y_pred - y_true
    abs_error = np.abs(error)
    return {
        "samples": int(y_true.shape[0]),
        "mse": float(np.mean(error**2)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(abs_error)),
        "p95_abs_error": percentile(abs_error.reshape(-1).tolist(), 95),
        "max_abs_error": float(np.max(abs_error)),
        "pred_action_saturation_pct": float(np.mean(np.abs(y_pred) >= 0.999) * 100.0),
    }


def select_alpha(samples: SampleSet, alphas: Sequence[float]) -> dict[str, Any]:
    rows = []
    x = samples.observations
    y = samples.actions
    for alpha in alphas:
        weights, norm = fit_ridge(x, y, alpha)
        pred = predict_ridge(x, weights, norm)
        rows.append({"alpha": float(alpha), "train": action_metrics(y, pred)})
    best = min(rows, key=lambda row: (row["train"]["mae"], row["train"]["p95_abs_error"]))
    weights, norm = fit_ridge(x, y, best["alpha"])
    return {"best_alpha": best["alpha"], "rows": rows, "weights": weights, "norm": norm}


def source_holdout(samples: SampleSet, alpha: float) -> list[dict[str, Any]]:
    rows = []
    sources = sorted(set(samples.sources))
    for source in sources:
        train_idx = np.asarray([item != source for item in samples.sources], dtype=bool)
        test_idx = ~train_idx
        if int(np.sum(train_idx)) < 20 or int(np.sum(test_idx)) < 1:
            rows.append(
                {
                    "held_out_source": source,
                    "status": "HOLD_INSUFFICIENT_SAMPLES",
                    "train_samples": int(np.sum(train_idx)),
                    "test_samples": int(np.sum(test_idx)),
                }
            )
            continue
        weights, norm = fit_ridge(samples.observations[train_idx], samples.actions[train_idx], alpha)
        pred = predict_ridge(samples.observations[test_idx], weights, norm)
        rows.append(
            {
                "held_out_source": source,
                "status": "PASS_SOURCE_HOLDOUT_EVALUATED",
                "train_samples": int(np.sum(train_idx)),
                "test_samples": int(np.sum(test_idx)),
                "metrics": action_metrics(samples.actions[test_idx], pred),
            }
        )
    return rows


def run_closed_loop_rollout(
    *,
    model: dict[str, Any],
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
    modes: dict[str, Any] = {}

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

    def step_bc(state, action):
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

    def predict_action(obs: np.ndarray) -> np.ndarray:
        if model["kind"] == "linear":
            return predict_ridge(obs, model["weights"], model["norm"]).reshape(-1)
        if model["kind"] == "knn":
            return predict_knn(
                obs,
                model["train_x"],
                model["train_y"],
                model["norm"],
                int(model["k"]),
            ).reshape(-1)
        if model["kind"] == "mlp":
            return predict_mlp_np(obs, model["params"], model["norm"]).reshape(-1)
        raise ValueError(f"unsupported model kind {model['kind']}")

    refresh_obs_jit = jax.jit(refresh_obs)
    step_bc_jit = jax.jit(step_bc)
    sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))

    for seed in seeds:
        state = env.reset(jax.random.PRNGKey(seed))
        state.info["command"] = command
        state = refresh_obs_jit(state)
        records = []
        for tick in range(sim_steps):
            obs = np.asarray(jax.device_get(state.obs["state"]), dtype=np.float64).reshape(1, -1)
            action = predict_action(obs).astype(np.float32)
            state, pre_rate, sent_target = step_bc_jit(state, jp.asarray(action))
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
            record = {
                "tick": tick,
                "time_s": tick * float(env.dt),
                "seed": seed,
                "command": [args.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "action": action.astype(float).tolist(),
                "target_pre_rate_limit_rad": np.asarray(jax.device_get(pre_rate), dtype=float).tolist(),
                "sent_target_rad": np.asarray(jax.device_get(sent_target), dtype=float).tolist(),
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
            records.append(record)
            if done:
                break
        modes[f"seed_{seed:03d}"] = summarize_rollout(records, args.command_x, float(env.dt))

    return {
        "status": classify_rollout(modes),
        "model_kind": model["kind"],
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
        "modes": modes,
    }


def summarize_rollout(records: list[dict[str, Any]], command_x: float, dt_s: float) -> dict[str, Any]:
    if not records:
        return {"status": "HOLD_NO_ROLLOUT_SAMPLES", "samples": 0}
    vx = [record["local_linvel_m_s"][0] for record in records]
    vy = [abs(record["local_linvel_m_s"][1]) for record in records]
    pitch = [abs(record["body_pitch_rad"]) for record in records]
    height = [record["base_height_m"] for record in records]
    action = np.asarray([record["action"] for record in records], dtype=float)
    action_delta = abs_velocity(action, dt_s) if action.size else np.zeros((0, 0))
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
        "action_delta_p95_per_s": percentile(action_delta.reshape(-1).tolist(), 95)
        if action_delta.size
        else None,
        "sent_target_velocity_p95_rad_s": percentile(sent_velocity.reshape(-1).tolist(), 95)
        if sent_velocity.size
        else None,
        "joint_tracking_p95_rad": percentile(tracking.reshape(-1).tolist(), 95)
        if tracking.size
        else None,
        "contact_pct": {key: float(value / len(records) * 100.0) for key, value in sorted(contacts.items())},
    }


def classify_rollout(modes: dict[str, Any]) -> str:
    if not modes:
        return "HOLD_BC_ROLLOUT_NOT_RUN"
    bad = [row for row in modes.values() if row.get("status") != "PASS_ROLLOUT_COMPLETED"]
    moving = [
        row
        for row in modes.values()
        if (row.get("mean_vx_m_s") is not None and row["mean_vx_m_s"] >= 0.02)
    ]
    if bad:
        return "HOLD_BC_REPLAY_TERMINATED"
    if len(moving) < len(modes):
        return "HOLD_BC_REPLAY_LOW_FORWARD_MOTION"
    return "PASS_BC_FIT_SMOKE_FORWARD_REPLAY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Target Dataset BC Smoke",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is a tiny offline behavior-cloning smoke over curated target windows.",
        "It is not PPO training and does not produce a deployable policy.",
        "",
        "## Dataset",
        "",
        f"- manifest: `{payload['manifest_path']}`",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- samples: `{payload['dataset']['samples']}`",
        f"- entries: `{payload['dataset']['entries']}`",
        f"- source_files: `{payload['dataset']['source_files']}`",
        f"- max_source_fraction: `{fmt(payload['dataset']['max_source_fraction'])}`",
        f"- warning: `{payload['dataset']['source_skew_warning']}`",
        "",
        "## Supervised Fit",
        "",
        f"- model_kind: `{payload['fit']['model_kind']}`",
        f"- best_alpha: `{payload['fit']['best_alpha']}`",
        f"- train_rmse: `{fmt(payload['fit']['train']['rmse'])}`",
        f"- train_mae: `{fmt(payload['fit']['train']['mae'])}`",
        f"- train_p95_abs_error: `{fmt(payload['fit']['train']['p95_abs_error'])}`",
        f"- train_max_abs_error: `{fmt(payload['fit']['train']['max_abs_error'])}`",
        f"- pred_action_saturation_pct: `{fmt(payload['fit']['train']['pred_action_saturation_pct'])}`",
        f"- sample_to_parameter_ratio: `{fmt(payload['fit']['sample_to_parameter_ratio'])}`",
        "",
        f"### Source Holdout ({payload['fit'].get('source_holdout_model_kind', 'ridge')} baseline)",
        "",
        "| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["fit"]["source_holdout"]:
        metrics = row.get("metrics") or {}
        lines.append(
            "| {source} | `{status}` | {train} | {test} | {mae} | {p95} | {maxe} |".format(
                source=row["held_out_source"],
                status=row["status"],
                train=row["train_samples"],
                test=row["test_samples"],
                mae=fmt(metrics.get("mae")),
                p95=fmt(metrics.get("p95_abs_error")),
                maxe=fmt(metrics.get("max_abs_error")),
            )
        )

    rollout = payload.get("rollout")
    lines.extend(["", "## Closed-Loop Smoke", ""])
    if rollout is None:
        lines.extend(
            [
                "status: `HOLD_BC_ROLLOUT_NOT_RUN`",
                "",
                "Closed-loop replay was skipped by request.",
            ]
        )
    else:
        lines.extend(
            [
                f"status: `{rollout['status']}`",
                f"jax_backend: `{rollout.get('jax_backend')}`",
                f"jax_devices: `{rollout.get('jax_devices')}`",
                f"model_kind: `{rollout.get('model_kind')}`",
                "",
                "| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |",
                "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for seed, row in sorted((rollout.get("modes") or {}).items()):
            lines.append(
                "| {seed} | {samples} | {term} | {vx} | {ratio} | {vy} | {pitch} | {height} | {sent} | {track} |".format(
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
                "### Rollout Action Summary",
                "",
                "| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |",
                "|---|---:|---:|---:|",
            ]
        )
        for seed, row in sorted((rollout.get("modes") or {}).items()):
            lines.append(
                "| {seed} | {mean} | {delta} | {sat} |".format(
                    seed=seed,
                    mean=fmt(row.get("action_abs_mean")),
                    delta=fmt(row.get("action_delta_p95_per_s")),
                    sat=fmt(row.get("action_saturation_pct")),
                )
            )

    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.",
            "- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.",
            "- Review source distribution and held-out-source errors before any larger imitation/pretraining run.",
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
    parser.add_argument("--ridge-alphas", default="1e-6,1e-4,1e-2,1,100")
    parser.add_argument("--model-kind", choices=["linear", "knn", "mlp"], default="linear")
    parser.add_argument("--knn-k", type=int, default=5)
    parser.add_argument("--mlp-hidden-sizes", default="128,128")
    parser.add_argument("--mlp-steps", type=int, default=2000)
    parser.add_argument("--mlp-batch-size", type=int, default=512)
    parser.add_argument("--mlp-learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--mlp-seed", type=int, default=0)
    parser.add_argument(
        "--jax-platform",
        choices=["auto", "cpu", "gpu"],
        default="cpu",
        help="Use cpu by default because local ROCm/MJX remains unstable.",
    )
    parser.add_argument("--no-rollout", action="store_true")
    args = parser.parse_args()

    if args.jax_platform != "auto":
        os.environ.setdefault("JAX_PLATFORM_NAME", args.jax_platform)
        os.environ.setdefault("JAX_PLATFORMS", args.jax_platform)

    manifest_path = Path(args.manifest)
    manifest, samples, entries = load_manifest_samples(manifest_path)
    source_counts = Counter(samples.sources)
    alphas = parse_csv_floats(args.ridge_alphas)
    fit = select_alpha(samples, alphas)
    holdout = source_holdout(samples, fit["best_alpha"])

    max_source_fraction = max(source_counts.values()) / max(sum(source_counts.values()), 1)
    ridge_parameter_count = (samples.observations.shape[1] + 1) * samples.actions.shape[1]
    mlp_fit = None
    if args.model_kind == "mlp":
        mlp_fit = fit_mlp_jax(
            samples.observations,
            samples.actions,
            hidden_sizes=parse_hidden_sizes(args.mlp_hidden_sizes),
            steps=args.mlp_steps,
            batch_size=args.mlp_batch_size,
            learning_rate=args.mlp_learning_rate,
            seed=args.mlp_seed,
        )
        train_metrics = mlp_fit["train"]
        parameter_count = int(mlp_fit["parameter_count"])
        sample_to_parameter_ratio = float(mlp_fit["sample_to_parameter_ratio"])
        model_fit_warnings = [
            "overparameterized_mlp_fit"
            if samples.observations.shape[0] < parameter_count
            else "none"
        ]
    else:
        train_pred = predict_ridge(samples.observations, fit["weights"], fit["norm"])
        train_metrics = action_metrics(samples.actions, train_pred)
        parameter_count = ridge_parameter_count
        sample_to_parameter_ratio = float(samples.observations.shape[0] / max(parameter_count, 1))
        model_fit_warnings = [
            "overparameterized_linear_fit"
            if samples.observations.shape[0] < parameter_count
            else "none"
        ]
    rollout = None
    status = "HOLD_BC_FIT_NO_CLOSED_LOOP"
    if not args.no_rollout:
        if args.model_kind == "linear":
            model = {
                "kind": "linear",
                "weights": fit["weights"],
                "norm": fit["norm"],
            }
        elif args.model_kind == "knn":
            mean = samples.observations.mean(axis=0)
            std = samples.observations.std(axis=0)
            std = np.where(std < 1.0e-8, 1.0, std)
            model = {
                "kind": "knn",
                "train_x": samples.observations,
                "train_y": samples.actions,
                "norm": np.stack([mean, std], axis=0),
                "k": int(args.knn_k),
            }
        elif args.model_kind == "mlp":
            assert mlp_fit is not None
            model = {
                "kind": "mlp",
                "params": mlp_fit["params"],
                "norm": mlp_fit["norm"],
            }
        rollout = run_closed_loop_rollout(model=model, args=args)
        status = rollout["status"]

    payload = {
        "status": status,
        "manifest_path": str(manifest_path),
        "dataset_id": manifest.get("dataset_id"),
        "dataset": {
            "entries": len(entries),
            "samples": int(samples.observations.shape[0]),
            "observation_dim": int(samples.observations.shape[1]),
            "action_dim": int(samples.actions.shape[1]),
            "source_files": len(source_counts),
            "source_counts": dict(sorted(source_counts.items())),
            "max_source_fraction": float(max_source_fraction),
            "source_skew_warning": bool(max_source_fraction > 0.75),
        },
        "fit": {
            "model_kind": args.model_kind,
            "best_alpha": fit["best_alpha"],
            "alpha_grid": [
                {
                    "alpha": row["alpha"],
                    "train_mae": row["train"]["mae"],
                    "train_p95_abs_error": row["train"]["p95_abs_error"],
                    "train_max_abs_error": row["train"]["max_abs_error"],
                }
                for row in fit["rows"]
            ],
            "train": train_metrics,
            "source_holdout_model_kind": "ridge",
            "source_holdout": holdout,
            "parameter_count": int(parameter_count),
            "sample_to_parameter_ratio": sample_to_parameter_ratio,
            "warnings": model_fit_warnings,
            "coefficient_norm": float(np.linalg.norm(fit["weights"][:-1])),
            "intercept_norm": float(np.linalg.norm(fit["weights"][-1])),
            "mlp": (
                {
                    "hidden_sizes": mlp_fit["hidden_sizes"],
                    "steps": mlp_fit["steps"],
                    "batch_size": mlp_fit["batch_size"],
                    "learning_rate": mlp_fit["learning_rate"],
                    "history": mlp_fit["history"],
                }
                if mlp_fit is not None
                else None
            ),
        },
        "smoke_model_kind": args.model_kind,
        "knn_k": int(args.knn_k),
        "rollout": rollout,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"dataset_id={manifest.get('dataset_id')}")
    print(f"samples={samples.observations.shape[0]}")
    print(f"best_alpha={fit['best_alpha']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
