#!/usr/bin/env python3
"""Train a PPO-compatible tanh-loc BC student from trace observations/actions.

The model matches the Brax PPO actor's deterministic contract:

  obs -> normalized MLP -> loc[14] -> tanh(loc) -> action[14]

It is still behavior cloning, not PPO training. The output NPZ stores loc-head
weights that can be mapped into the first half of the PPO actor's final
tanh-normal distribution layer.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any, Sequence

import numpy as np


def percentile(values: Sequence[float] | np.ndarray, q: float) -> float | None:
    arr = np.asarray(values, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    return float(np.percentile(arr, q))


def read_manifest_samples(manifest_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    manifest = json.loads(manifest_path.read_text())
    observations: list[list[float]] = []
    actions: list[list[float]] = []
    weights: list[float] = []
    pairs: list[tuple[int, int]] = []
    for entry in manifest.get("entries", []):
        if not entry.get("bc_ready", False):
            continue
        source_path = Path(entry["source_path"])
        if not source_path.exists():
            continue
        entry_sample_weight = float(entry.get("sample_weight", 1.0))
        previous_index: int | None = None
        with source_path.open() as handle:
            for line in handle:
                record = json.loads(line)
                obs = record.get("obs_state")
                action = record.get("action")
                if obs is None or action is None:
                    continue
                obs_arr = np.asarray(obs, dtype=np.float64).reshape(-1)
                action_arr = np.asarray(action, dtype=np.float64).reshape(-1)
                if obs_arr.shape != (101,) or action_arr.shape != (14,):
                    continue
                current_index = len(observations)
                observations.append(obs_arr.astype(float).tolist())
                actions.append(np.clip(action_arr, -1.0, 1.0).astype(float).tolist())
                record_sample_weight = float(record.get("sample_weight", 1.0))
                weights.append(max(entry_sample_weight * record_sample_weight, 0.0))
                if previous_index is not None:
                    pairs.append((previous_index, current_index))
                previous_index = current_index
    if not observations:
        raise ValueError(f"no BC-ready samples found in {manifest_path}")
    return (
        np.asarray(observations, dtype=np.float64),
        np.asarray(actions, dtype=np.float64),
        np.asarray(pairs, dtype=np.int64),
        np.asarray(weights, dtype=np.float64),
    )


def init_params(
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
        params.append(
            (
                rng.normal(0.0, scale, size=(in_dim, out_dim)).astype(np.float64),
                np.zeros((out_dim,), dtype=np.float64),
            )
        )
    return params


def activate_np(values: np.ndarray, activation: str) -> np.ndarray:
    if activation == "tanh":
        return np.tanh(values)
    if activation == "swish":
        return values / (1.0 + np.exp(-values))
    raise ValueError(f"unsupported activation {activation}")


def predict_actions_np(
    obs: np.ndarray,
    params: list[tuple[np.ndarray, np.ndarray]],
    norm: np.ndarray,
    activation: str,
) -> tuple[np.ndarray, np.ndarray]:
    mean, std = norm
    z = (obs - mean) / std
    for index, (weights, bias) in enumerate(params):
        z = z @ weights + bias
        if index < len(params) - 1:
            z = activate_np(z, activation)
    loc = z
    return loc, np.tanh(loc)


def action_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    err = y_pred - y_true
    abs_err = np.abs(err)
    return {
        "samples": int(y_true.shape[0]),
        "mae": float(np.mean(abs_err)),
        "rmse": float(np.sqrt(np.mean(err**2))),
        "p50_abs_error": percentile(abs_err, 50),
        "p95_abs_error": percentile(abs_err, 95),
        "p99_abs_error": percentile(abs_err, 99),
        "max_abs_error": float(np.max(abs_err)) if abs_err.size else None,
        "pred_action_saturation_pct": float(np.mean(np.abs(y_pred) >= 0.999) * 100.0),
    }


def abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros((0, values.shape[1] if values.ndim == 2 else 0))
    return np.abs(np.diff(values, axis=0)) / max(float(dt_s), 1.0e-9)


def train_model(
    obs: np.ndarray,
    actions: np.ndarray,
    pairs: np.ndarray,
    weights: np.ndarray,
    args: argparse.Namespace,
) -> dict[str, Any]:
    os.environ.setdefault("JAX_PLATFORMS", "cpu")
    os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")
    import jax
    import jax.numpy as jnp
    import optax

    hidden_sizes = [int(item) for item in args.hidden_sizes.split(",") if item]
    mean = obs.mean(axis=0)
    std = obs.std(axis=0)
    std = np.where(std < 1.0e-8, 1.0, std)
    norm = np.stack([mean, std]).astype(np.float64)
    x_norm = ((obs - mean) / std).astype(np.float32)
    y = actions.astype(np.float32)
    sample_weights = np.asarray(weights, dtype=np.float32).reshape(-1)
    if sample_weights.shape != (obs.shape[0],):
        raise ValueError("sample weights must match observations")
    if not np.any(sample_weights > 0.0):
        sample_weights = np.ones_like(sample_weights, dtype=np.float32)
    params_np = init_params(obs.shape[1], hidden_sizes, actions.shape[1], args.seed)
    params = [(jnp.asarray(w, dtype=jnp.float32), jnp.asarray(b, dtype=jnp.float32)) for w, b in params_np]
    optimizer = optax.adam(float(args.learning_rate))
    opt_state = optimizer.init(params)
    rng = np.random.default_rng(int(args.seed))
    pair_count = int(pairs.shape[0])
    pair_batch_size = max(1, min(int(args.batch_size), pair_count if pair_count else 1))
    activation_name = str(args.activation)

    def forward(model_params, batch_x):
        z = batch_x
        for index, (weights, bias) in enumerate(model_params):
            z = z @ weights + bias
            if index < len(model_params) - 1:
                if activation_name == "tanh":
                    z = jnp.tanh(z)
                elif activation_name == "swish":
                    z = jax.nn.swish(z)
                else:
                    raise ValueError(f"unsupported activation {activation_name}")
        loc = z
        return loc, jnp.tanh(loc)

    def loss_fn(model_params, batch_x, batch_y, batch_w, pair_x0, pair_x1):
        _, pred = forward(model_params, batch_x)
        per_sample = jnp.mean((pred - batch_y) ** 2, axis=1)
        supervised = jnp.sum(per_sample * batch_w) / jnp.maximum(jnp.sum(batch_w), 1.0e-9)
        _, pair_pred0 = forward(model_params, pair_x0)
        _, pair_pred1 = forward(model_params, pair_x1)
        target_rate = jnp.abs(pair_pred1 - pair_pred0) * float(args.action_scale_rad) / float(args.dt_s)
        excess = jnp.maximum(target_rate - float(args.target_rate_limit_rad_s), 0.0)
        rate_penalty = jnp.mean(excess**2)
        return supervised + float(args.target_rate_scale) * rate_penalty

    @jax.jit
    def step(model_params, state, batch_x, batch_y, batch_w, pair_x0, pair_x1):
        loss, grads = jax.value_and_grad(loss_fn)(model_params, batch_x, batch_y, batch_w, pair_x0, pair_x1)
        updates, state = optimizer.update(grads, state, model_params)
        return optax.apply_updates(model_params, updates), state, loss

    loss_rows = []
    n = x_norm.shape[0]
    for train_step in range(1, int(args.steps) + 1):
        batch_idx = rng.integers(0, n, size=int(args.batch_size))
        if pair_count:
            pair_idx = rng.integers(0, pair_count, size=pair_batch_size)
            pair_x0 = x_norm[pairs[pair_idx, 0]]
            pair_x1 = x_norm[pairs[pair_idx, 1]]
        else:
            pair_x0 = x_norm[batch_idx[:pair_batch_size]]
            pair_x1 = pair_x0
        params, opt_state, loss = step(
            params,
            opt_state,
            jnp.asarray(x_norm[batch_idx], dtype=jnp.float32),
            jnp.asarray(y[batch_idx], dtype=jnp.float32),
            jnp.asarray(sample_weights[batch_idx], dtype=jnp.float32),
            jnp.asarray(pair_x0, dtype=jnp.float32),
            jnp.asarray(pair_x1, dtype=jnp.float32),
        )
        if train_step == 1 or train_step % max(1, int(args.log_every)) == 0 or train_step == int(args.steps):
            loss_rows.append({"step": train_step, "loss": float(loss)})

    params_out = [(np.asarray(w), np.asarray(b)) for w, b in params]
    _, pred = predict_actions_np(obs, params_out, norm, activation_name)
    metrics = action_metrics(actions, pred)
    consecutive_pred = pred[pairs[:, 1]] if pair_count else np.zeros((0, actions.shape[1]))
    consecutive_prev = pred[pairs[:, 0]] if pair_count else np.zeros((0, actions.shape[1]))
    target_rate = (
        np.abs(consecutive_pred - consecutive_prev) * float(args.action_scale_rad) / float(args.dt_s)
        if pair_count
        else np.zeros((0, actions.shape[1]))
    )
    return {
        "hidden_sizes": hidden_sizes,
        "activation": activation_name,
        "norm": norm,
        "params": params_out,
        "loss_rows": loss_rows,
        "metrics": metrics,
        "target_rate": {
            "pair_count": int(pair_count),
            "p50_rad_s": percentile(target_rate, 50),
            "p95_rad_s": percentile(target_rate, 95),
            "p99_rad_s": percentile(target_rate, 99),
            "max_rad_s": float(np.max(target_rate)) if target_rate.size else None,
        },
        "sample_weight": {
            "p50": percentile(sample_weights, 50),
            "p95": percentile(sample_weights, 95),
            "max": float(np.max(sample_weights)) if sample_weights.size else None,
            "weighted_samples": float(np.sum(sample_weights)),
        },
    }


def save_npz(path: Path, fit: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "norm": fit["norm"].astype(np.float32),
        "hidden_sizes": np.asarray(fit["hidden_sizes"], dtype=np.int64),
        "output_mode": np.asarray(["ppo_tanh_loc"]),
        "activation": np.asarray([str(fit["activation"])]),
    }
    for index, (weights, bias) in enumerate(fit["params"]):
        payload[f"w{index}"] = weights.astype(np.float32)
        payload[f"b{index}"] = bias.astype(np.float32)
    np.savez(path, **payload)


def export_onnx(path: Path, fit: dict[str, Any], obs: np.ndarray) -> dict[str, Any]:
    import onnx
    from onnx import TensorProto, helper, numpy_helper
    import onnxruntime as ort

    path.parent.mkdir(parents=True, exist_ok=True)
    initializers = [
        numpy_helper.from_array(fit["norm"][0].astype(np.float32), name="mean"),
        numpy_helper.from_array(fit["norm"][1].astype(np.float32), name="std"),
    ]
    nodes = [
        helper.make_node("Sub", ["obs", "mean"], ["centered"], name="norm_sub"),
        helper.make_node("Div", ["centered", "std"], ["hidden_in"], name="norm_div"),
    ]
    previous = "hidden_in"
    for index, (weights, bias) in enumerate(fit["params"]):
        initializers.append(numpy_helper.from_array(weights.astype(np.float32), name=f"w{index}"))
        initializers.append(numpy_helper.from_array(bias.astype(np.float32), name=f"b{index}"))
        gemm = f"gemm{index}_out"
        nodes.append(helper.make_node("Gemm", [previous, f"w{index}", f"b{index}"], [gemm], name=f"gemm{index}"))
        if index < len(fit["params"]) - 1:
            if fit["activation"] == "tanh":
                activated = f"tanh{index}_out"
                nodes.append(helper.make_node("Tanh", [gemm], [activated], name=f"tanh{index}"))
            elif fit["activation"] == "swish":
                sigmoid = f"sigmoid{index}_out"
                activated = f"swish{index}_out"
                nodes.append(helper.make_node("Sigmoid", [gemm], [sigmoid], name=f"sigmoid{index}"))
                nodes.append(helper.make_node("Mul", [gemm, sigmoid], [activated], name=f"swish{index}"))
            else:
                raise ValueError(f"unsupported activation {fit['activation']}")
            previous = activated
        else:
            nodes.append(helper.make_node("Tanh", [gemm], ["continuous_actions"], name="ppo_loc_tanh"))
    graph = helper.make_graph(
        nodes,
        "open_duck_ppo_loc_bc_student",
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

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    sample = obs[: min(64, obs.shape[0])].astype(np.float32)
    _, expected = predict_actions_np(sample, fit["params"], fit["norm"], fit["activation"])
    actual = np.vstack(
        [session.run(["continuous_actions"], {"obs": row[None, :]})[0][0] for row in sample]
    )
    err = np.abs(actual - expected)
    return {
        "path": str(path),
        "samples_checked": int(sample.shape[0]),
        "max_abs_error": float(np.max(err)) if err.size else None,
        "p95_abs_error": percentile(err, 95),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# PPO-Loc BC Student",
        "",
        f"status: `{report['status']}`",
        "",
        "This is an offline behavior-cloning fit using the PPO actor's deterministic",
        "`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,",
        "or change robot runtime behavior.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{report['manifest']}`",
        f"- samples: `{report['samples']}`",
        f"- weighted samples: `{report['sample_weight']['weighted_samples']:.4f}`",
        f"- pairs: `{report['target_rate']['pair_count']}`",
        f"- hidden sizes: `{report['hidden_sizes']}`",
        f"- activation: `{report['activation']}`",
        "",
        "## Outputs",
        "",
        f"- NPZ: `{report['saved_npz']}`",
        f"- ONNX: `{report['exported_onnx']}`",
        "",
        "## Fit Metrics",
        "",
        f"- MAE: `{report['train_metrics']['mae']:.6f}`",
        f"- p95 abs error: `{report['train_metrics']['p95_abs_error']:.6f}`",
        f"- max abs error: `{report['train_metrics']['max_abs_error']:.6f}`",
        f"- target-rate p95: `{report['target_rate']['p95_rad_s']:.6f}` rad/s",
        f"- target-rate max: `{report['target_rate']['max_rad_s']:.6f}` rad/s",
        f"- sample weight p50/p95/max: `{report['sample_weight']['p50']:.4f}` / `{report['sample_weight']['p95']:.4f}` / `{report['sample_weight']['max']:.4f}`",
        "",
        "## Loss",
        "",
        "| step | loss |",
        "|---:|---:|",
    ]
    for row in report["loss_rows"]:
        lines.append(f"| {row['step']} | {row['loss']:.6f} |")
    lines += [
        "",
        "## ONNX Verification",
        "",
        f"- samples checked: `{report['onnx_verify']['samples_checked']}`",
        f"- p95 abs error: `{report['onnx_verify']['p95_abs_error']:.8f}`",
        f"- max abs error: `{report['onnx_verify']['max_abs_error']:.8f}`",
        "",
        "## Gate",
        "",
        "This only verifies a PPO-compatible supervised fit. The next gate is the",
        "standard task-matched fitted closed-loop candidate sweep using the exported",
        "ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is",
        "worth promoting.",
        "",
    ]
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--hidden-sizes", default="512,256,128")
    parser.add_argument("--activation", choices=["tanh", "swish"], default="swish")
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=500)
    parser.add_argument("--target-rate-scale", type=float, default=0.1)
    parser.add_argument("--target-rate-limit-rad-s", type=float, default=3.75)
    parser.add_argument("--action-scale-rad", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument(
        "--save-npz",
        default="outputs/analysis/ppo_loc_bc_student_candidate/candidate_mlp.npz",
    )
    parser.add_argument(
        "--export-onnx",
        default="outputs/analysis/ppo_loc_bc_student_candidate/candidate.onnx",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/PPO_LOC_BC_STUDENT.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/ppo_loc_bc_student.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    obs, actions, pairs, weights = read_manifest_samples(Path(args.manifest))
    fit = train_model(obs, actions, pairs, weights, args)
    save_npz(Path(args.save_npz), fit)
    onnx_verify = export_onnx(Path(args.export_onnx), fit, obs)
    status = "PASS_PPO_LOC_BC_FIT_SMOKE"
    report = {
        "status": status,
        "manifest": args.manifest,
        "samples": int(obs.shape[0]),
        "hidden_sizes": fit["hidden_sizes"],
        "activation": fit["activation"],
        "saved_npz": args.save_npz,
        "exported_onnx": args.export_onnx,
        "train_metrics": fit["metrics"],
        "target_rate": fit["target_rate"],
        "sample_weight": fit["sample_weight"],
        "loss_rows": fit["loss_rows"],
        "onnx_verify": onnx_verify,
        "config": {
            "steps": int(args.steps),
            "batch_size": int(args.batch_size),
            "learning_rate": float(args.learning_rate),
            "target_rate_scale": float(args.target_rate_scale),
            "target_rate_limit_rad_s": float(args.target_rate_limit_rad_s),
            "action_scale_rad": float(args.action_scale_rad),
            "dt_s": float(args.dt_s),
            "seed": int(args.seed),
        },
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2))
    write_markdown(Path(args.output_md), report)
    print(status)
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
