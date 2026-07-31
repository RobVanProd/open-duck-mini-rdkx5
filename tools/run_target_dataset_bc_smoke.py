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
import re
from typing import Any, Iterable, Sequence

import numpy as np

from actuator_bridge_model import (
    ActuatorBridgeModel,
    load_fit_json,
    params_from_fit,
    stress_params,
)
from closed_loop_sim_eval import quat_wxyz_to_pitch, temporary_cwd
from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "outputs" / "analysis" / "target_dataset_obs_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_DATASET_BC_SMOKE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_dataset_bc_smoke.json"
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_FIT_JSON = ROOT / "outputs" / "analysis" / "actuator_response_fit_corrected_knee.json"
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


def write_jsonl(path: Path, records: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records))


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


def load_manifest_samples(
    manifest_path: Path,
    *,
    include_source_regex: str | None = None,
    exclude_source_regex: str | None = None,
) -> tuple[dict[str, Any], SampleSet, list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text())
    include_pattern = re.compile(include_source_regex) if include_source_regex else None
    exclude_pattern = re.compile(exclude_source_regex) if exclude_source_regex else None
    observations: list[list[float]] = []
    actions: list[list[float]] = []
    sources: list[str] = []
    modes: list[str] = []
    ticks: list[int] = []
    loaded_entries = []

    for entry in manifest.get("entries", []):
        source_label = str(entry.get("source_name") or entry.get("source_path") or "")
        if include_pattern and not include_pattern.search(source_label):
            continue
        if exclude_pattern and exclude_pattern.search(source_label):
            continue
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


def consecutive_sample_pairs(samples: SampleSet) -> np.ndarray:
    by_key: dict[tuple[str, str, int], int] = {}
    for index, (source, mode, tick) in enumerate(zip(samples.sources, samples.modes, samples.ticks, strict=True)):
        if tick < 0:
            continue
        by_key.setdefault((source, mode, int(tick)), index)
    pairs = []
    for source, mode, tick in sorted(by_key):
        here = by_key[(source, mode, tick)]
        nxt = by_key.get((source, mode, tick + 1))
        if nxt is not None:
            pairs.append((here, nxt))
    return np.asarray(pairs, dtype=np.int64)


def make_blend_model(
    samples: SampleSet,
    fit: dict[str, Any],
    *,
    kind: str,
    knn_k: int,
    blend_alpha: float,
    dwell_blend_alpha: float = 1.0,
    dwell_trigger_ticks: int = 20,
    vx_blend_alpha: float = 1.0,
    vx_blend_threshold_m_s: float = 0.02,
) -> dict[str, Any]:
    mean = samples.observations.mean(axis=0)
    std = samples.observations.std(axis=0)
    std = np.where(std < 1.0e-8, 1.0, std)
    return {
        "kind": kind,
        "weights": fit["weights"],
        "linear_norm": fit["norm"],
        "train_x": samples.observations,
        "train_y": samples.actions,
        "knn_norm": np.stack([mean, std], axis=0),
        "k": int(knn_k),
        "blend_alpha": float(blend_alpha),
        "dwell_blend_alpha": float(dwell_blend_alpha),
        "dwell_trigger_ticks": int(dwell_trigger_ticks),
        "vx_blend_alpha": float(vx_blend_alpha),
        "vx_blend_threshold_m_s": float(vx_blend_threshold_m_s),
    }


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
    pair_indices: np.ndarray | None = None,
    target_rate_scale: float = 0.0,
    target_rate_limit_rad_s: float = 3.75,
    action_scale_rad: float = 0.25,
    dt_s: float = 0.02,
    obs_noise_std: float = 0.0,
    obs_consistency_scale: float = 0.0,
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
    pairs = np.asarray(pair_indices if pair_indices is not None else np.zeros((0, 2), dtype=np.int64))
    pair_count = int(pairs.shape[0])
    pair_batch_size = max(1, min(batch_size, pair_count if pair_count else 1))
    target_rate_scale = float(target_rate_scale)
    target_rate_limit_rad_s = float(target_rate_limit_rad_s)
    action_scale_rad = float(action_scale_rad)
    dt_s = float(dt_s)
    obs_noise_std = float(obs_noise_std)
    obs_consistency_scale = float(obs_consistency_scale)

    def forward(model_params, batch_x):
        z = batch_x
        for index, (weights, bias) in enumerate(model_params):
            z = z @ weights + bias
            if index < len(model_params) - 1:
                z = jnp.tanh(z)
        return z

    def loss_fn(model_params, batch_x, batch_y, pair_x0, pair_x1, noisy_batch_x):
        pred = forward(model_params, batch_x)
        supervised = jnp.mean((pred - batch_y) ** 2)
        pair_pred0 = forward(model_params, pair_x0)
        pair_pred1 = forward(model_params, pair_x1)
        target_rate = jnp.abs(pair_pred1 - pair_pred0) * action_scale_rad / max(dt_s, 1.0e-9)
        excess_rate = jnp.maximum(target_rate - target_rate_limit_rad_s, 0.0)
        rate_penalty = jnp.mean(excess_rate**2)
        noisy_pred = forward(model_params, noisy_batch_x)
        consistency = jnp.mean((noisy_pred - jax.lax.stop_gradient(pred)) ** 2)
        return supervised + target_rate_scale * rate_penalty + obs_consistency_scale * consistency

    @jax.jit
    def train_step(model_params, state, batch_x, batch_y, pair_x0, pair_x1, noisy_batch_x):
        loss, grads = jax.value_and_grad(loss_fn)(
            model_params,
            batch_x,
            batch_y,
            pair_x0,
            pair_x1,
            noisy_batch_x,
        )
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
        if pair_count:
            pair_rows = pairs[rng.integers(0, pair_count, size=pair_batch_size)]
            pair_x0 = x_norm[pair_rows[:, 0]]
            pair_x1 = x_norm[pair_rows[:, 1]]
        else:
            pair_x0 = np.zeros((pair_batch_size, x_norm.shape[1]), dtype=np.float32)
            pair_x1 = np.zeros((pair_batch_size, x_norm.shape[1]), dtype=np.float32)
        if obs_noise_std > 0.0 and obs_consistency_scale > 0.0:
            noisy_x = x_norm[indices] + rng.normal(
                0.0,
                obs_noise_std,
                size=(batch_size, x_norm.shape[1]),
            ).astype(np.float32)
        else:
            noisy_x = x_norm[indices]
        params, opt_state, loss = train_step(
            params,
            opt_state,
            jnp.asarray(x_norm[indices], dtype=jnp.float32),
            jnp.asarray(y_f32[indices], dtype=jnp.float32),
            jnp.asarray(pair_x0, dtype=jnp.float32),
            jnp.asarray(pair_x1, dtype=jnp.float32),
            jnp.asarray(noisy_x, dtype=jnp.float32),
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
        "pair_count": pair_count,
        "target_rate_scale": target_rate_scale,
        "target_rate_limit_rad_s": target_rate_limit_rad_s,
        "action_scale_rad": action_scale_rad,
        "dt_s": dt_s,
        "obs_noise_std": obs_noise_std,
        "obs_consistency_scale": obs_consistency_scale,
        "parameter_count": parameter_count,
        "sample_to_parameter_ratio": float(n_samples / max(parameter_count, 1)),
    }


def save_mlp_npz(path: Path, mlp_fit: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays: dict[str, np.ndarray] = {
        "norm": np.asarray(mlp_fit["norm"], dtype=np.float32),
        "hidden_sizes": np.asarray(mlp_fit["hidden_sizes"], dtype=np.int64),
    }
    for index, (weights, bias) in enumerate(mlp_fit["params"]):
        arrays[f"w{index}"] = np.asarray(weights, dtype=np.float32)
        arrays[f"b{index}"] = np.asarray(bias, dtype=np.float32)
    np.savez(path, **arrays)


def export_mlp_onnx(path: Path, mlp_fit: dict[str, Any]) -> dict[str, Any]:
    import onnx
    from onnx import TensorProto, helper, numpy_helper

    path.parent.mkdir(parents=True, exist_ok=True)
    norm = np.asarray(mlp_fit["norm"], dtype=np.float32)
    params = [
        (np.asarray(weights, dtype=np.float32), np.asarray(bias, dtype=np.float32))
        for weights, bias in mlp_fit["params"]
    ]
    nodes = []
    initializers = [
        numpy_helper.from_array(norm[0].astype(np.float32), name="obs_mean"),
        numpy_helper.from_array(norm[1].astype(np.float32), name="obs_std"),
        numpy_helper.from_array(np.asarray([-1.0], dtype=np.float32), name="clip_min"),
        numpy_helper.from_array(np.asarray([1.0], dtype=np.float32), name="clip_max"),
    ]
    nodes.append(helper.make_node("Sub", ["obs", "obs_mean"], ["obs_centered"], name="normalize_sub"))
    nodes.append(helper.make_node("Div", ["obs_centered", "obs_std"], ["layer0_in"], name="normalize_div"))
    previous = "layer0_in"
    for index, (weights, bias) in enumerate(params):
        w_name = f"w{index}"
        b_name = f"b{index}"
        gemm_out = f"gemm{index}_out"
        initializers.append(numpy_helper.from_array(weights, name=w_name))
        initializers.append(numpy_helper.from_array(bias, name=b_name))
        nodes.append(helper.make_node("Gemm", [previous, w_name, b_name], [gemm_out], name=f"gemm{index}"))
        if index < len(params) - 1:
            tanh_out = f"tanh{index}_out"
            nodes.append(helper.make_node("Tanh", [gemm_out], [tanh_out], name=f"tanh{index}"))
            previous = tanh_out
        else:
            previous = gemm_out
    nodes.append(
        helper.make_node(
            "Clip",
            [previous, "clip_min", "clip_max"],
            ["continuous_actions"],
            name="action_clip",
        )
    )
    graph = helper.make_graph(
        nodes,
        "open_duck_mlp_bc_student",
        [helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, 101])],
        [helper.make_tensor_value_info("continuous_actions", TensorProto.FLOAT, [1, 14])],
        initializer=initializers,
    )
    model = helper.make_model(
        graph,
        producer_name="open-duck-mini-rdkx5",
        opset_imports=[helper.make_operatorsetid("", 13)],
    )
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    onnx.save(model, path)
    return {"path": str(path), "input_name": "obs", "output_name": "continuous_actions"}


def verify_mlp_onnx(path: Path, mlp_fit: dict[str, Any], observations: np.ndarray) -> dict[str, Any]:
    import onnxruntime as ort

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    sample = observations[: min(32, observations.shape[0])].astype(np.float32)
    expected = predict_mlp_np(sample, mlp_fit["params"], mlp_fit["norm"]).astype(np.float32)
    actual = session.run(["continuous_actions"], {"obs": sample[:1]})[0]
    batch_actual = []
    for row in sample:
        batch_actual.append(session.run(["continuous_actions"], {"obs": row[None, :]})[0][0])
    batch_actual_np = np.asarray(batch_actual, dtype=np.float32)
    error = np.abs(batch_actual_np - expected)
    return {
        "path": str(path),
        "single_output_shape": list(actual.shape),
        "samples_checked": int(sample.shape[0]),
        "max_abs_error": float(np.max(error)) if error.size else None,
        "p95_abs_error": percentile(error.reshape(-1).tolist(), 95) if error.size else None,
    }


def export_blend_onnx(path: Path, blend_model: dict[str, Any]) -> dict[str, Any]:
    import onnx
    from onnx import TensorProto, helper, numpy_helper

    if blend_model.get("kind") != "blend":
        raise ValueError("exact blend ONNX export only supports model kind 'blend'")

    path.parent.mkdir(parents=True, exist_ok=True)
    train_x = np.asarray(blend_model["train_x"], dtype=np.float32)
    train_y = np.asarray(blend_model["train_y"], dtype=np.float32)
    knn_norm = np.asarray(blend_model["knn_norm"], dtype=np.float32)
    linear_norm = np.asarray(blend_model["linear_norm"], dtype=np.float32)
    weights = np.asarray(blend_model["weights"], dtype=np.float32)
    alpha = float(blend_model["blend_alpha"])
    k = int(blend_model["k"])
    if train_x.ndim != 2 or train_x.shape[1] != 101:
        raise ValueError(f"expected train_x shape [N,101], got {train_x.shape}")
    if train_y.ndim != 2 or train_y.shape[1] != 14:
        raise ValueError(f"expected train_y shape [N,14], got {train_y.shape}")
    if not (1 <= k <= train_x.shape[0]):
        raise ValueError(f"k must be within train sample count, got k={k}, n={train_x.shape[0]}")

    train_norm = ((train_x - knn_norm[0]) / knn_norm[1]).astype(np.float32)
    ridge_w = weights[:-1].astype(np.float32)
    ridge_b = weights[-1].astype(np.float32)
    initializers = [
        numpy_helper.from_array(linear_norm[0].astype(np.float32), name="linear_mean"),
        numpy_helper.from_array(linear_norm[1].astype(np.float32), name="linear_std"),
        numpy_helper.from_array(knn_norm[0].astype(np.float32), name="knn_mean"),
        numpy_helper.from_array(knn_norm[1].astype(np.float32), name="knn_std"),
        numpy_helper.from_array(train_norm, name="train_norm"),
        numpy_helper.from_array(train_y, name="train_y"),
        numpy_helper.from_array(ridge_w, name="ridge_w"),
        numpy_helper.from_array(ridge_b, name="ridge_b"),
        numpy_helper.from_array(np.asarray([k], dtype=np.int64), name="topk_k"),
        numpy_helper.from_array(np.asarray([alpha], dtype=np.float32), name="blend_alpha"),
        numpy_helper.from_array(np.asarray([1.0 - alpha], dtype=np.float32), name="blend_linear_weight"),
        numpy_helper.from_array(np.asarray([-1.0], dtype=np.float32), name="clip_min"),
        numpy_helper.from_array(np.asarray([1.0], dtype=np.float32), name="clip_max"),
    ]
    nodes = [
        helper.make_node("Sub", ["obs", "linear_mean"], ["linear_centered"], name="linear_sub"),
        helper.make_node("Div", ["linear_centered", "linear_std"], ["linear_in"], name="linear_div"),
        helper.make_node("Gemm", ["linear_in", "ridge_w", "ridge_b"], ["linear_out"], name="ridge_gemm"),
        helper.make_node("Sub", ["obs", "knn_mean"], ["knn_centered"], name="knn_sub"),
        helper.make_node("Div", ["knn_centered", "knn_std"], ["knn_in"], name="knn_div"),
        helper.make_node("Unsqueeze", ["knn_in"], ["knn_query"], name="query_unsqueeze", axes=[1]),
        helper.make_node("Sub", ["knn_query", "train_norm"], ["diff"], name="knn_diff"),
        helper.make_node("Mul", ["diff", "diff"], ["diff_sq"], name="knn_diff_sq"),
        helper.make_node("ReduceSum", ["diff_sq"], ["dist_sq"], name="knn_dist_sq", axes=[2], keepdims=0),
        helper.make_node("Neg", ["dist_sq"], ["neg_dist_sq"], name="knn_neg_dist"),
        helper.make_node("TopK", ["neg_dist_sq", "topk_k"], ["topk_values", "topk_indices"], name="knn_topk"),
        helper.make_node("Gather", ["train_y", "topk_indices"], ["neighbor_actions"], name="knn_gather", axis=0),
        helper.make_node(
            "ReduceMean",
            ["neighbor_actions"],
            ["knn_out"],
            name="knn_mean_action",
            axes=[1],
            keepdims=0,
        ),
        helper.make_node("Mul", ["knn_out", "blend_alpha"], ["knn_weighted"], name="blend_knn"),
        helper.make_node(
            "Mul",
            ["linear_out", "blend_linear_weight"],
            ["linear_weighted"],
            name="blend_linear",
        ),
        helper.make_node("Add", ["knn_weighted", "linear_weighted"], ["blend_out"], name="blend_add"),
        helper.make_node("Clip", ["blend_out", "clip_min", "clip_max"], ["continuous_actions"], name="action_clip"),
    ]
    graph = helper.make_graph(
        nodes,
        "open_duck_exact_blend_bc_student",
        [helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, 101])],
        [helper.make_tensor_value_info("continuous_actions", TensorProto.FLOAT, [1, 14])],
        initializer=initializers,
    )
    model = helper.make_model(
        graph,
        producer_name="open-duck-mini-rdkx5",
        opset_imports=[helper.make_operatorsetid("", 12)],
    )
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    onnx.save(model, path)
    return {
        "path": str(path),
        "input_name": "obs",
        "output_name": "continuous_actions",
        "knn_samples": int(train_x.shape[0]),
        "knn_k": k,
        "blend_alpha": alpha,
    }


def verify_blend_onnx(path: Path, blend_model: dict[str, Any], observations: np.ndarray) -> dict[str, Any]:
    import onnxruntime as ort

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    sample = observations[: min(32, observations.shape[0])].astype(np.float32)
    expected_rows = []
    for row in sample.astype(np.float64):
        expected_rows.append(
            np.clip(
                float(blend_model["blend_alpha"])
                * predict_knn(
                    row[None, :],
                    blend_model["train_x"],
                    blend_model["train_y"],
                    blend_model["knn_norm"],
                    int(blend_model["k"]),
                )
                + (1.0 - float(blend_model["blend_alpha"]))
                * predict_ridge(row[None, :], blend_model["weights"], blend_model["linear_norm"]),
                -1.0,
                1.0,
            )[0]
        )
    expected = np.asarray(expected_rows, dtype=np.float32)
    batch_actual = []
    for row in sample:
        batch_actual.append(session.run(["continuous_actions"], {"obs": row[None, :]})[0][0])
    actual = np.asarray(batch_actual, dtype=np.float32)
    error = np.abs(actual - expected)
    return {
        "path": str(path),
        "single_output_shape": list(session.run(["continuous_actions"], {"obs": sample[:1]})[0].shape),
        "samples_checked": int(sample.shape[0]),
        "max_abs_error": float(np.max(error)) if error.size else None,
        "p95_abs_error": percentile(error.reshape(-1).tolist(), 95) if error.size else None,
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

    def prepare_step(state, action):
        state.info["command"] = command
        action = jp.clip(action, -1.0, 1.0)
        pre_rate_limit = env._default_actuator + action * env._config.action_scale
        prev_motor_targets = state.info["motor_targets"]
        sent_target = jp.clip(
            pre_rate_limit,
            prev_motor_targets - env._config.max_motor_velocity * env.dt,
            prev_motor_targets + env._config.max_motor_velocity * env.dt,
        )
        return state, pre_rate_limit, sent_target

    def apply_motor_target(state, action, sent_target, applied_target):
        state.info["command"] = command
        action = jp.clip(action, -1.0, 1.0)
        data = mjx_env.step(env.mjx_model, state.data, applied_target, env.n_substeps)
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
        return state.replace(data=data, obs=obs, reward=reward, done=done)

    def predict_blend_model(
        blend_model: dict[str, Any],
        obs: np.ndarray,
        blend_alpha_override: float | None = None,
    ) -> np.ndarray:
        linear_pred = predict_ridge(obs, blend_model["weights"], blend_model["linear_norm"])
        knn_pred = predict_knn(
            obs,
            blend_model["train_x"],
            blend_model["train_y"],
            blend_model["knn_norm"],
            int(blend_model["k"]),
        )
        alpha = float(
            blend_model["blend_alpha"] if blend_alpha_override is None else blend_alpha_override
        )
        return np.clip(alpha * knn_pred + (1.0 - alpha) * linear_pred, -1.0, 1.0).reshape(-1)

    def predict_action(
        obs: np.ndarray,
        blend_alpha_override: float | None = None,
        use_alt_model: bool = False,
    ) -> np.ndarray:
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
        if model["kind"] in {"blend", "dwell_blend", "vx_blend"}:
            return predict_blend_model(model, obs, blend_alpha_override)
        if model["kind"] == "source_vx_blend":
            active_model = model["alt_model"] if use_alt_model else model["primary_model"]
            return predict_blend_model(active_model, obs, blend_alpha_override)
        if model["kind"] == "mlp":
            return predict_mlp_np(obs, model["params"], model["norm"]).reshape(-1)
        raise ValueError(f"unsupported model kind {model['kind']}")

    refresh_obs_jit = jax.jit(refresh_obs)
    prepare_step_jit = jax.jit(prepare_step)
    apply_motor_target_jit = jax.jit(apply_motor_target)
    sim_steps = max(1, int(round(float(args.duration_s) / float(env.dt))))
    bridge_params = None
    if args.actuator_bridge_mode == "fitted":
        bridge_params = params_from_fit(load_fit_json(args.fit_json), JOINT_NAMES)
    elif args.actuator_bridge_mode == "stress":
        bridge_params = stress_params(JOINT_NAMES)

    for seed in seeds:
        state = env.reset(jax.random.PRNGKey(seed))
        state.info["command"] = command
        state = refresh_obs_jit(state)
        initial_target = np.asarray(jax.device_get(state.info["motor_targets"]), dtype=float)
        bridge = (
            ActuatorBridgeModel(bridge_params, initial_target=initial_target)
            if bridge_params is not None
            else None
        )
        records = []
        double_support_streak = 0
        for tick in range(sim_steps):
            obs = np.asarray(jax.device_get(state.obs["state"]), dtype=np.float64).reshape(1, -1)
            pre_step_local_linvel = np.asarray(
                jax.device_get(env.get_local_linvel(state.data)), dtype=float
            )
            current_contacts = np.asarray(jax.device_get(state.info["last_contact"]), dtype=bool).reshape(-1)
            double_support = bool(current_contacts.size >= 2 and bool(np.all(current_contacts[:2])))
            double_support_streak = double_support_streak + 1 if double_support else 0
            blend_alpha_used = None
            if model["kind"] == "dwell_blend":
                blend_alpha_used = (
                    float(model["dwell_blend_alpha"])
                    if double_support_streak >= int(model["dwell_trigger_ticks"])
                    else float(model["blend_alpha"])
                )
            elif model["kind"] == "vx_blend":
                blend_alpha_used = (
                    float(model["vx_blend_alpha"])
                    if float(pre_step_local_linvel[0]) >= float(model["vx_blend_threshold_m_s"])
                    else float(model["blend_alpha"])
                )
            use_alt_model = False
            if model["kind"] == "source_vx_blend":
                use_alt_model = (
                    float(pre_step_local_linvel[0]) >= float(model["source_vx_threshold_m_s"])
                )
                active_model = model["alt_model"] if use_alt_model else model["primary_model"]
                blend_alpha_used = (
                    float(active_model["vx_blend_alpha"])
                    if float(pre_step_local_linvel[0]) >= float(active_model["vx_blend_threshold_m_s"])
                    else float(active_model["blend_alpha"])
                )
            action = predict_action(
                obs,
                blend_alpha_override=blend_alpha_used,
                use_alt_model=use_alt_model,
            ).astype(np.float32)
            state, pre_rate, sent_target = prepare_step_jit(state, jp.asarray(action))
            sent_np = np.asarray(jax.device_get(sent_target), dtype=float)
            applied_np = sent_np if bridge is None else bridge.step(sent_np, float(env.dt))
            state = apply_motor_target_jit(
                state,
                jp.asarray(action),
                sent_target,
                jp.asarray(applied_np),
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
            contacts = np.asarray(jax.device_get(state.info["last_contact"]), dtype=bool)
            done = bool(np.asarray(jax.device_get(state.done)))
            record = {
                "mode": model["kind"],
                "tick": tick,
                "time_s": tick * float(env.dt),
                "seed": seed,
                "command": [args.command_x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "action": action.astype(float).tolist(),
                "blend_alpha_used": blend_alpha_used,
                "source_model_used": "alt" if use_alt_model else "primary",
                "actuator_bridge_mode": args.actuator_bridge_mode,
                "double_support_streak": double_support_streak,
                "pre_step_local_linvel_m_s": pre_step_local_linvel.astype(float).tolist(),
                "target_pre_rate_limit_rad": np.asarray(jax.device_get(pre_rate), dtype=float).tolist(),
                "sent_target_rad": sent_np.tolist(),
                "applied_target_rad": applied_np.tolist(),
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
            if args.trace_full_obs:
                record["obs_state"] = obs.reshape(-1).astype(float).tolist()
            records.append(record)
            if done:
                break
        modes[f"seed_{seed:03d}"] = summarize_rollout(records, args.command_x, float(env.dt))
        if args.trace_dir:
            trace_path = Path(args.trace_dir) / f"seed_{seed:03d}.jsonl"
            write_jsonl(trace_path, records)
            modes[f"seed_{seed:03d}"]["trace_jsonl"] = str(trace_path)

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
        f"- include_source_regex: `{payload.get('include_source_regex')}`",
        f"- exclude_source_regex: `{payload.get('exclude_source_regex')}`",
        f"- alt_include_source_regex: `{payload.get('alt_include_source_regex')}`",
        f"- alt_exclude_source_regex: `{payload.get('alt_exclude_source_regex')}`",
        f"- actuator_bridge_mode: `{payload.get('actuator_bridge_mode')}`",
        f"- fit_json: `{payload.get('fit_json')}`",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- samples: `{payload['dataset']['samples']}`",
        f"- entries: `{payload['dataset']['entries']}`",
        f"- source_files: `{payload['dataset']['source_files']}`",
        f"- max_source_fraction: `{fmt(payload['dataset']['max_source_fraction'])}`",
        f"- warning: `{payload['dataset']['source_skew_warning']}`",
    ]
    if payload.get("alt_dataset") is not None:
        alt = payload["alt_dataset"]
        lines.extend(
            [
                f"- alt_samples: `{alt['samples']}`",
                f"- alt_entries: `{alt['entries']}`",
                f"- alt_source_files: `{alt['source_files']}`",
                f"- alt_best_alpha: `{alt['best_alpha']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Supervised Fit",
            "",
        f"- model_kind: `{payload['fit']['model_kind']}`",
        f"- knn_k: `{payload.get('knn_k')}`",
        f"- blend_alpha: `{payload.get('blend_alpha')}`",
        f"- dwell_blend_alpha: `{payload.get('dwell_blend_alpha')}`",
        f"- dwell_trigger_ticks: `{payload.get('dwell_trigger_ticks')}`",
        f"- vx_blend_alpha: `{payload.get('vx_blend_alpha')}`",
        f"- vx_blend_threshold_m_s: `{payload.get('vx_blend_threshold_m_s')}`",
        f"- source_vx_threshold_m_s: `{payload.get('source_vx_threshold_m_s')}`",
        f"- best_alpha: `{payload['fit']['best_alpha']}`",
        f"- train_rmse: `{fmt(payload['fit']['train']['rmse'])}`",
        f"- train_mae: `{fmt(payload['fit']['train']['mae'])}`",
        f"- train_p95_abs_error: `{fmt(payload['fit']['train']['p95_abs_error'])}`",
        f"- train_max_abs_error: `{fmt(payload['fit']['train']['max_abs_error'])}`",
        f"- pred_action_saturation_pct: `{fmt(payload['fit']['train']['pred_action_saturation_pct'])}`",
        f"- sample_to_parameter_ratio: `{fmt(payload['fit']['sample_to_parameter_ratio'])}`",
        f"- consecutive_pair_count: `{payload['fit'].get('consecutive_pair_count')}`",
        "",
        ]
    )
    mlp = payload["fit"].get("mlp")
    if mlp is not None:
        lines.extend(
            [
                "### MLP Settings",
                "",
                f"- hidden_sizes: `{mlp['hidden_sizes']}`",
                f"- steps: `{mlp['steps']}`",
                f"- batch_size: `{mlp['batch_size']}`",
                f"- learning_rate: `{mlp['learning_rate']}`",
                f"- pair_count: `{mlp['pair_count']}`",
                f"- target_rate_scale: `{mlp['target_rate_scale']}`",
                f"- target_rate_limit_rad_s: `{mlp['target_rate_limit_rad_s']}`",
                f"- obs_noise_std: `{mlp['obs_noise_std']}`",
                f"- obs_consistency_scale: `{mlp['obs_consistency_scale']}`",
                f"- saved_npz: `{mlp.get('saved_npz')}`",
                f"- exported_onnx: `{mlp.get('exported_onnx')}`",
                f"- onnx_verify_max_abs_error: `{fmt((mlp.get('onnx_verify') or {}).get('max_abs_error'))}`",
                "",
                "| step | loss |",
                "|---:|---:|",
            ]
        )
        for row in mlp.get("history") or []:
            lines.append(f"| {row['step']} | {fmt(row['loss'], 6)} |")
        lines.append("")
    blend_onnx = payload["fit"].get("blend_onnx")
    if blend_onnx is not None:
        exported = blend_onnx.get("exported_onnx") or {}
        verify = blend_onnx.get("onnx_verify") or {}
        lines.extend(
            [
                "### Exact Blend ONNX",
                "",
                f"- exported_onnx: `{exported.get('path')}`",
                f"- input_name: `{exported.get('input_name')}`",
                f"- output_name: `{exported.get('output_name')}`",
                f"- knn_samples: `{exported.get('knn_samples')}`",
                f"- knn_k: `{exported.get('knn_k')}`",
                f"- blend_alpha: `{exported.get('blend_alpha')}`",
                f"- onnx_verify_samples_checked: `{verify.get('samples_checked')}`",
                f"- onnx_verify_max_abs_error: `{fmt(verify.get('max_abs_error'), 8)}`",
                f"- onnx_verify_p95_abs_error: `{fmt(verify.get('p95_abs_error'), 8)}`",
                "",
            ]
        )
    lines.extend(
        [
            f"### Source Holdout ({payload['fit'].get('source_holdout_model_kind', 'ridge')} baseline)",
        "",
        "| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |",
        "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
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
    parser.add_argument(
        "--include-source-regex",
        default=None,
        help="Optional regex for source labels to include from the manifest.",
    )
    parser.add_argument(
        "--exclude-source-regex",
        default=None,
        help="Optional regex for source labels to exclude from the manifest.",
    )
    parser.add_argument(
        "--alt-include-source-regex",
        default=None,
        help="Optional source include regex for source_vx_blend alternate model.",
    )
    parser.add_argument(
        "--alt-exclude-source-regex",
        default=None,
        help="Optional source exclude regex for source_vx_blend alternate model.",
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--duration-s", type=float, default=3.0)
    parser.add_argument("--seeds", default="0,2")
    parser.add_argument("--ridge-alphas", default="1e-6,1e-4,1e-2,1,100")
    parser.add_argument(
        "--model-kind",
        choices=["linear", "knn", "blend", "dwell_blend", "vx_blend", "source_vx_blend", "mlp"],
        default="linear",
    )
    parser.add_argument("--knn-k", type=int, default=5)
    parser.add_argument("--blend-alpha", type=float, default=0.75)
    parser.add_argument("--dwell-blend-alpha", type=float, default=1.0)
    parser.add_argument("--dwell-trigger-ticks", type=int, default=20)
    parser.add_argument("--vx-blend-alpha", type=float, default=1.0)
    parser.add_argument("--vx-blend-threshold-m-s", type=float, default=0.02)
    parser.add_argument("--source-vx-threshold-m-s", type=float, default=0.02)
    parser.add_argument(
        "--actuator-bridge-mode",
        choices=["vanilla", "fitted", "stress"],
        default="vanilla",
        help="Eval-only actuator bridge mode inserted after the built-in target rate limit.",
    )
    parser.add_argument("--fit-json", default=str(DEFAULT_FIT_JSON))
    parser.add_argument("--mlp-hidden-sizes", default="128,128")
    parser.add_argument("--mlp-steps", type=int, default=2000)
    parser.add_argument("--mlp-batch-size", type=int, default=512)
    parser.add_argument("--mlp-learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--mlp-seed", type=int, default=0)
    parser.add_argument("--mlp-target-rate-scale", type=float, default=0.0)
    parser.add_argument("--mlp-target-rate-limit-rad-s", type=float, default=3.75)
    parser.add_argument("--mlp-obs-noise-std", type=float, default=0.0)
    parser.add_argument("--mlp-obs-consistency-scale", type=float, default=0.0)
    parser.add_argument("--save-mlp-npz", default=None)
    parser.add_argument("--export-mlp-onnx", default=None)
    parser.add_argument(
        "--export-blend-onnx",
        default=None,
        help="Optional output path for an exact blend kNN+ridge ONNX export.",
    )
    parser.add_argument(
        "--trace-dir",
        default=None,
        help="Optional directory for ignored per-seed JSONL rollout traces.",
    )
    parser.add_argument(
        "--trace-full-obs",
        action="store_true",
        help="Include obs_state in trace records for offline distillation manifests.",
    )
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
    manifest, samples, entries = load_manifest_samples(
        manifest_path,
        include_source_regex=args.include_source_regex,
        exclude_source_regex=args.exclude_source_regex,
    )
    alt_samples = None
    alt_entries: list[dict[str, Any]] = []
    alt_fit = None
    if args.model_kind == "source_vx_blend":
        alt_manifest, alt_samples, alt_entries = load_manifest_samples(
            manifest_path,
            include_source_regex=args.alt_include_source_regex,
            exclude_source_regex=args.alt_exclude_source_regex,
        )
        if alt_manifest.get("dataset_id") != manifest.get("dataset_id"):
            raise ValueError("alternate manifest dataset id mismatch")
    pair_indices = consecutive_sample_pairs(samples)
    source_counts = Counter(samples.sources)
    alphas = parse_csv_floats(args.ridge_alphas)
    fit = select_alpha(samples, alphas)
    holdout = source_holdout(samples, fit["best_alpha"])
    if alt_samples is not None:
        alt_fit = select_alpha(alt_samples, alphas)

    max_source_fraction = max(source_counts.values()) / max(sum(source_counts.values()), 1)
    ridge_parameter_count = (samples.observations.shape[1] + 1) * samples.actions.shape[1]
    mlp_fit = None
    mlp_saved_npz = None
    mlp_exported_onnx = None
    mlp_onnx_verify = None
    blend_exported_onnx = None
    blend_onnx_verify = None
    if args.model_kind == "mlp":
        mlp_fit = fit_mlp_jax(
            samples.observations,
            samples.actions,
            hidden_sizes=parse_hidden_sizes(args.mlp_hidden_sizes),
            steps=args.mlp_steps,
            batch_size=args.mlp_batch_size,
            learning_rate=args.mlp_learning_rate,
            seed=args.mlp_seed,
            pair_indices=pair_indices,
            target_rate_scale=args.mlp_target_rate_scale,
            target_rate_limit_rad_s=args.mlp_target_rate_limit_rad_s,
            obs_noise_std=args.mlp_obs_noise_std,
            obs_consistency_scale=args.mlp_obs_consistency_scale,
        )
        if args.save_mlp_npz:
            save_mlp_npz(Path(args.save_mlp_npz), mlp_fit)
            mlp_saved_npz = str(Path(args.save_mlp_npz))
        if args.export_mlp_onnx:
            mlp_exported_onnx = export_mlp_onnx(Path(args.export_mlp_onnx), mlp_fit)["path"]
            mlp_onnx_verify = verify_mlp_onnx(
                Path(args.export_mlp_onnx), mlp_fit, samples.observations
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
        if args.model_kind == "blend" and args.export_blend_onnx:
            export_model = make_blend_model(
                samples,
                fit,
                kind="blend",
                knn_k=args.knn_k,
                blend_alpha=args.blend_alpha,
            )
            blend_exported_onnx = export_blend_onnx(
                Path(args.export_blend_onnx),
                export_model,
            )
            blend_onnx_verify = verify_blend_onnx(
                Path(args.export_blend_onnx),
                export_model,
                samples.observations,
            )
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
        elif args.model_kind in {"blend", "dwell_blend", "vx_blend"}:
            model = make_blend_model(
                samples,
                fit,
                kind=args.model_kind,
                knn_k=args.knn_k,
                blend_alpha=args.blend_alpha,
                dwell_blend_alpha=args.dwell_blend_alpha,
                dwell_trigger_ticks=args.dwell_trigger_ticks,
                vx_blend_alpha=args.vx_blend_alpha,
                vx_blend_threshold_m_s=args.vx_blend_threshold_m_s,
            )
        elif args.model_kind == "source_vx_blend":
            assert alt_samples is not None
            assert alt_fit is not None
            model = {
                "kind": "source_vx_blend",
                "primary_model": make_blend_model(
                    samples,
                    fit,
                    kind="vx_blend",
                    knn_k=args.knn_k,
                    blend_alpha=args.blend_alpha,
                    vx_blend_alpha=args.vx_blend_alpha,
                    vx_blend_threshold_m_s=args.vx_blend_threshold_m_s,
                ),
                "alt_model": make_blend_model(
                    alt_samples,
                    alt_fit,
                    kind="vx_blend",
                    knn_k=args.knn_k,
                    blend_alpha=args.blend_alpha,
                    vx_blend_alpha=args.vx_blend_alpha,
                    vx_blend_threshold_m_s=args.vx_blend_threshold_m_s,
                ),
                "source_vx_threshold_m_s": float(args.source_vx_threshold_m_s),
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
        "include_source_regex": args.include_source_regex,
        "exclude_source_regex": args.exclude_source_regex,
        "alt_include_source_regex": args.alt_include_source_regex,
        "alt_exclude_source_regex": args.alt_exclude_source_regex,
        "actuator_bridge_mode": args.actuator_bridge_mode,
        "fit_json": str(args.fit_json),
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
        "alt_dataset": (
            {
                "entries": len(alt_entries),
                "samples": int(alt_samples.observations.shape[0]),
                "source_files": len(Counter(alt_samples.sources)),
                "best_alpha": alt_fit["best_alpha"] if alt_fit is not None else None,
            }
            if alt_samples is not None
            else None
        ),
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
            "consecutive_pair_count": int(pair_indices.shape[0]),
            "coefficient_norm": float(np.linalg.norm(fit["weights"][:-1])),
            "intercept_norm": float(np.linalg.norm(fit["weights"][-1])),
            "mlp": (
                {
                    "hidden_sizes": mlp_fit["hidden_sizes"],
                    "steps": mlp_fit["steps"],
                    "batch_size": mlp_fit["batch_size"],
                    "learning_rate": mlp_fit["learning_rate"],
                    "pair_count": mlp_fit["pair_count"],
                    "target_rate_scale": mlp_fit["target_rate_scale"],
                    "target_rate_limit_rad_s": mlp_fit["target_rate_limit_rad_s"],
                    "action_scale_rad": mlp_fit["action_scale_rad"],
                    "dt_s": mlp_fit["dt_s"],
                    "obs_noise_std": mlp_fit["obs_noise_std"],
                    "obs_consistency_scale": mlp_fit["obs_consistency_scale"],
                    "history": mlp_fit["history"],
                    "saved_npz": mlp_saved_npz,
                    "exported_onnx": mlp_exported_onnx,
                    "onnx_verify": mlp_onnx_verify,
                }
                if mlp_fit is not None
                else None
            ),
            "blend_onnx": (
                {
                    "exported_onnx": blend_exported_onnx,
                    "onnx_verify": blend_onnx_verify,
                }
                if blend_exported_onnx is not None
                else None
            ),
        },
        "smoke_model_kind": args.model_kind,
        "knn_k": int(args.knn_k),
        "blend_alpha": float(args.blend_alpha),
        "dwell_blend_alpha": float(args.dwell_blend_alpha),
        "dwell_trigger_ticks": int(args.dwell_trigger_ticks),
        "vx_blend_alpha": float(args.vx_blend_alpha),
        "vx_blend_threshold_m_s": float(args.vx_blend_threshold_m_s),
        "source_vx_threshold_m_s": float(args.source_vx_threshold_m_s),
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
