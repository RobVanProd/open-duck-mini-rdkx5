#!/usr/bin/env python3
"""Train a shared-trunk phase/command-modulated BC student.

This is the next live-oracle phase-student rung after independent phase heads
failed. It preserves the deployed ONNX contract:

  obs[1,101] -> continuous_actions[1,14]

Architecture:

  obs -> normalize -> shared trunk -> hidden
  obs[context_indices] -> normalize -> context MLP -> gamma,beta
  hidden_mod = hidden * (1 + modulation_scale * tanh(gamma))
               + modulation_scale * tanh(beta)
  hidden_mod -> output loc -> tanh(loc) -> action

The context path defaults to command_x and phase channels: obs[6], obs[99],
obs[100]. It is behavior cloning only; it does not train PPO, deploy, SSH, or
touch the robot.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from train_ppo_loc_bc_student import (
    action_metrics,
    percentile,
    read_manifest_samples,
)


def parse_int_list(text: str) -> list[int]:
    values = [int(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def parse_hidden_sizes(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def parse_rate_limits(text: str, action_dim: int, fallback: float) -> np.ndarray:
    if not text.strip():
        return np.full((action_dim,), float(fallback), dtype=np.float32)
    values = np.asarray([float(part.strip()) for part in text.split(",")], dtype=np.float32)
    if values.shape != (action_dim,) or not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise argparse.ArgumentTypeError(f"expected {action_dim} finite positive rate limits")
    return values


def parse_phase_rate_spec(text: str, action_dim: int) -> np.ndarray:
    """Return an [8, action_dim] mask from `joint=bin|bin,...`."""
    mask = np.zeros((8, int(action_dim)), dtype=np.float32)
    if not text.strip():
        return mask
    for item in text.split(","):
        joint_text, sep, bins_text = item.strip().partition("=")
        if not sep:
            raise argparse.ArgumentTypeError(f"invalid phase-rate item {item!r}")
        joint = int(joint_text)
        if not 0 <= joint < action_dim:
            raise argparse.ArgumentTypeError(f"joint index {joint} outside [0,{action_dim})")
        for bin_text in bins_text.split("|"):
            phase_bin = int(bin_text)
            if not 0 <= phase_bin < 8:
                raise argparse.ArgumentTypeError(f"phase bin {phase_bin} outside [0,8)")
            mask[phase_bin, joint] = 1.0
    return mask


def phase_rate_pair_mask(obs: np.ndarray, pairs: np.ndarray, spec: str) -> np.ndarray:
    """Map each consecutive pair's newer phase observation to a joint mask."""
    table = parse_phase_rate_spec(spec, 14)
    if not len(pairs):
        return np.zeros((0, 14), dtype=np.float32)
    phase = obs[pairs[:, 1]][:, [99, 100]]
    angle = np.mod(np.arctan2(phase[:, 1], phase[:, 0]), 2.0 * np.pi)
    bins = np.minimum((angle / (np.pi / 4.0)).astype(np.int64), 7)
    return table[bins]


def init_layer(rng: np.random.Generator, in_dim: int, out_dim: int) -> tuple[np.ndarray, np.ndarray]:
    scale = math.sqrt(2.0 / max(in_dim + out_dim, 1))
    return (
        rng.normal(0.0, scale, size=(in_dim, out_dim)).astype(np.float64),
        np.zeros((out_dim,), dtype=np.float64),
    )


def init_mlp(
    input_dim: int,
    hidden_sizes: Sequence[int],
    output_dim: int,
    seed: int,
) -> list[tuple[np.ndarray, np.ndarray]]:
    rng = np.random.default_rng(int(seed))
    dims = [int(input_dim), *[int(size) for size in hidden_sizes], int(output_dim)]
    return [init_layer(rng, in_dim, out_dim) for in_dim, out_dim in zip(dims[:-1], dims[1:], strict=True)]


def activate_np(values: np.ndarray, activation: str) -> np.ndarray:
    if activation == "tanh":
        return np.tanh(values)
    if activation == "swish":
        return values / (1.0 + np.exp(-values))
    raise ValueError(f"unsupported activation {activation}")


def forward_np(
    obs: np.ndarray,
    params: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    mean, std = params["obs_norm"]
    context_mean, context_std = params["context_norm"]
    activation = str(params["activation"])
    modulation_scale = float(params["modulation_scale"])
    context_indices = params["context_indices"].astype(int)

    z = (obs - mean) / std
    for weights, bias in params["trunk"]:
        z = activate_np(z @ weights + bias, activation)
    hidden = z

    c = (obs[:, context_indices] - context_mean) / context_std
    for index, (weights, bias) in enumerate(params["context"]):
        c = c @ weights + bias
        if index < len(params["context"]) - 1:
            c = activate_np(c, activation)
    gamma, beta = np.split(c, 2, axis=1)
    modulated = hidden * (1.0 + modulation_scale * np.tanh(gamma)) + modulation_scale * np.tanh(beta)
    out_w, out_b = params["output"]
    loc = modulated @ out_w + out_b
    return loc, np.tanh(loc)


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

    trunk_hidden = parse_hidden_sizes(args.trunk_hidden_sizes)
    context_hidden = parse_hidden_sizes(args.context_hidden_sizes)
    if not trunk_hidden:
        raise ValueError("--trunk-hidden-sizes must include at least one hidden layer")
    context_indices = np.asarray(parse_int_list(args.context_indices), dtype=np.int64)
    if np.any(context_indices < 0) or np.any(context_indices >= obs.shape[1]):
        raise ValueError("context indices out of observation bounds")
    action_dim = int(actions.shape[1])
    target_rate_limits = parse_rate_limits(
        args.target_rate_limits_rad_s, action_dim, args.target_rate_limit_rad_s
    )
    hidden_dim = int(trunk_hidden[-1])
    activation_name = str(args.activation)

    obs_mean = obs.mean(axis=0)
    obs_std = np.where(obs.std(axis=0) < 1.0e-8, 1.0, obs.std(axis=0))
    context = obs[:, context_indices]
    context_mean = context.mean(axis=0)
    context_std = np.where(context.std(axis=0) < 1.0e-8, 1.0, context.std(axis=0))
    normed_obs = ((obs - obs_mean) / obs_std).astype(np.float32)
    normed_context = ((context - context_mean) / context_std).astype(np.float32)
    y = actions.astype(np.float32)
    sample_weights = np.asarray(weights, dtype=np.float32).reshape(-1)
    if not np.any(sample_weights > 0.0):
        sample_weights = np.ones_like(sample_weights, dtype=np.float32)

    rng_np = np.random.default_rng(int(args.seed))
    trunk_np = init_mlp(obs.shape[1], trunk_hidden[:-1], trunk_hidden[-1], int(args.seed))
    context_np = init_mlp(len(context_indices), context_hidden, hidden_dim * 2, int(args.seed) + 101)
    output_np = init_layer(rng_np, hidden_dim, action_dim)
    params = {
        "trunk": [(jnp.asarray(w, dtype=jnp.float32), jnp.asarray(b, dtype=jnp.float32)) for w, b in trunk_np],
        "context": [(jnp.asarray(w, dtype=jnp.float32), jnp.asarray(b, dtype=jnp.float32)) for w, b in context_np],
        "output": (jnp.asarray(output_np[0], dtype=jnp.float32), jnp.asarray(output_np[1], dtype=jnp.float32)),
    }
    optimizer = optax.adam(float(args.learning_rate))
    opt_state = optimizer.init(params)
    rng = np.random.default_rng(int(args.seed))
    pair_count = int(pairs.shape[0])
    phase_pair_mask = phase_rate_pair_mask(obs, pairs, args.phase_rate_spec)
    pair_batch_size = max(1, min(int(args.batch_size), pair_count if pair_count else 1))

    def activate(values):
        if activation_name == "tanh":
            return jnp.tanh(values)
        if activation_name == "swish":
            return jax.nn.swish(values)
        raise ValueError(f"unsupported activation {activation_name}")

    def forward(model_params, batch_x, batch_c):
        z = batch_x
        for weights, bias in model_params["trunk"]:
            z = activate(z @ weights + bias)
        hidden = z
        c = batch_c
        for index, (weights, bias) in enumerate(model_params["context"]):
            c = c @ weights + bias
            if index < len(model_params["context"]) - 1:
                c = activate(c)
        gamma, beta = jnp.split(c, 2, axis=1)
        modulated = hidden * (1.0 + float(args.modulation_scale) * jnp.tanh(gamma))
        modulated = modulated + float(args.modulation_scale) * jnp.tanh(beta)
        out_w, out_b = model_params["output"]
        loc = modulated @ out_w + out_b
        return loc, jnp.tanh(loc)

    def loss_fn(model_params, batch_x, batch_c, batch_y, batch_w, pair_x0, pair_c0, pair_x1, pair_c1, pair_mask):
        _, pred = forward(model_params, batch_x, batch_c)
        per_sample = jnp.mean((pred - batch_y) ** 2, axis=1)
        supervised = jnp.sum(per_sample * batch_w) / jnp.maximum(jnp.sum(batch_w), 1.0e-9)
        _, pair_pred0 = forward(model_params, pair_x0, pair_c0)
        _, pair_pred1 = forward(model_params, pair_x1, pair_c1)
        target_rate = jnp.abs(pair_pred1 - pair_pred0) * float(args.action_scale_rad) / float(args.dt_s)
        excess = jnp.maximum(target_rate - jnp.asarray(target_rate_limits), 0.0)
        rate_penalty = jnp.mean(excess**2)
        local_excess = jnp.maximum(target_rate - float(args.phase_rate_limit_rad_s), 0.0)
        local_denom = jnp.maximum(jnp.sum(pair_mask), 1.0)
        local_penalty = jnp.sum((local_excess**2) * pair_mask) / local_denom
        return supervised + float(args.target_rate_scale) * rate_penalty + float(args.phase_rate_scale) * local_penalty

    @jax.jit
    def step(model_params, state, batch_x, batch_c, batch_y, batch_w, pair_x0, pair_c0, pair_x1, pair_c1, pair_mask):
        loss, grads = jax.value_and_grad(loss_fn)(
            model_params, batch_x, batch_c, batch_y, batch_w, pair_x0, pair_c0, pair_x1, pair_c1, pair_mask
        )
        updates, state = optimizer.update(grads, state, model_params)
        return optax.apply_updates(model_params, updates), state, loss

    loss_rows = []
    n = int(normed_obs.shape[0])
    for train_step in range(1, int(args.steps) + 1):
        batch_idx = rng.integers(0, n, size=int(args.batch_size))
        if pair_count:
            pair_idx = rng.integers(0, pair_count, size=pair_batch_size)
            p0 = pairs[pair_idx, 0]
            p1 = pairs[pair_idx, 1]
        else:
            p0 = batch_idx[:pair_batch_size]
            p1 = p0
        params, opt_state, loss = step(
            params,
            opt_state,
            jnp.asarray(normed_obs[batch_idx], dtype=jnp.float32),
            jnp.asarray(normed_context[batch_idx], dtype=jnp.float32),
            jnp.asarray(y[batch_idx], dtype=jnp.float32),
            jnp.asarray(sample_weights[batch_idx], dtype=jnp.float32),
            jnp.asarray(normed_obs[p0], dtype=jnp.float32),
            jnp.asarray(normed_context[p0], dtype=jnp.float32),
            jnp.asarray(normed_obs[p1], dtype=jnp.float32),
            jnp.asarray(normed_context[p1], dtype=jnp.float32),
            jnp.asarray(phase_pair_mask[pair_idx] if pair_count else np.zeros((pair_batch_size, action_dim)), dtype=jnp.float32),
        )
        if train_step == 1 or train_step % max(1, int(args.log_every)) == 0 or train_step == int(args.steps):
            loss_rows.append({"step": train_step, "loss": float(loss)})

    params_np = {
        "obs_norm": np.stack([obs_mean, obs_std]).astype(np.float32),
        "context_norm": np.stack([context_mean, context_std]).astype(np.float32),
        "context_indices": context_indices.astype(np.int64),
        "activation": activation_name,
        "modulation_scale": float(args.modulation_scale),
        "trunk": [(np.asarray(w), np.asarray(b)) for w, b in params["trunk"]],
        "context": [(np.asarray(w), np.asarray(b)) for w, b in params["context"]],
        "output": (np.asarray(params["output"][0]), np.asarray(params["output"][1])),
    }
    _, pred = forward_np(obs.astype(np.float32), params_np)
    metrics = action_metrics(actions, pred)
    if pair_count:
        pair_pred0 = pred[pairs[:, 0]]
        pair_pred1 = pred[pairs[:, 1]]
        target_rate = np.abs(pair_pred1 - pair_pred0) * float(args.action_scale_rad) / float(args.dt_s)
    else:
        target_rate = np.zeros((0, action_dim))
    return {
        "params": params_np,
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
        "trunk_hidden_sizes": trunk_hidden,
        "context_hidden_sizes": context_hidden,
    }


def save_npz(path: Path, fit: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    params = fit["params"]
    payload: dict[str, Any] = {
        "obs_norm": params["obs_norm"].astype(np.float32),
        "context_norm": params["context_norm"].astype(np.float32),
        "context_indices": params["context_indices"].astype(np.int64),
        "output_mode": np.asarray(["phase_modulated_tanh_loc"]),
        "activation": np.asarray([str(params["activation"])]),
        "modulation_scale": np.asarray([float(params["modulation_scale"])], dtype=np.float32),
        "trunk_hidden_sizes": np.asarray(fit["trunk_hidden_sizes"], dtype=np.int64),
        "context_hidden_sizes": np.asarray(fit["context_hidden_sizes"], dtype=np.int64),
    }
    for index, (weights, bias) in enumerate(params["trunk"]):
        payload[f"trunk_w{index}"] = weights.astype(np.float32)
        payload[f"trunk_b{index}"] = bias.astype(np.float32)
    for index, (weights, bias) in enumerate(params["context"]):
        payload[f"context_w{index}"] = weights.astype(np.float32)
        payload[f"context_b{index}"] = bias.astype(np.float32)
    payload["output_w"] = params["output"][0].astype(np.float32)
    payload["output_b"] = params["output"][1].astype(np.float32)
    np.savez(path, **payload)


def export_onnx(path: Path, fit: dict[str, Any], obs: np.ndarray) -> dict[str, Any]:
    import onnx
    from onnx import TensorProto, helper, numpy_helper
    import onnxruntime as ort

    params = fit["params"]
    path.parent.mkdir(parents=True, exist_ok=True)
    initializers = [
        numpy_helper.from_array(params["obs_norm"][0].astype(np.float32), name="obs_mean"),
        numpy_helper.from_array(params["obs_norm"][1].astype(np.float32), name="obs_std"),
        numpy_helper.from_array(params["context_indices"].astype(np.int64), name="context_indices"),
        numpy_helper.from_array(params["context_norm"][0].astype(np.float32), name="context_mean"),
        numpy_helper.from_array(params["context_norm"][1].astype(np.float32), name="context_std"),
        numpy_helper.from_array(np.asarray([float(params["modulation_scale"])], dtype=np.float32), name="modulation_scale"),
    ]
    nodes = [
        helper.make_node("Sub", ["obs", "obs_mean"], ["obs_centered"], name="norm_obs_sub"),
        helper.make_node("Div", ["obs_centered", "obs_std"], ["trunk_in"], name="norm_obs_div"),
        helper.make_node("Gather", ["obs", "context_indices"], ["context_raw"], name="context_gather", axis=1),
        helper.make_node("Sub", ["context_raw", "context_mean"], ["context_centered"], name="norm_context_sub"),
        helper.make_node("Div", ["context_centered", "context_std"], ["context_in"], name="norm_context_div"),
    ]

    previous = "trunk_in"
    for index, (weights, bias) in enumerate(params["trunk"]):
        initializers.append(numpy_helper.from_array(weights.astype(np.float32), name=f"trunk_w{index}"))
        initializers.append(numpy_helper.from_array(bias.astype(np.float32), name=f"trunk_b{index}"))
        gemm = f"trunk_gemm{index}"
        nodes.append(helper.make_node("Gemm", [previous, f"trunk_w{index}", f"trunk_b{index}"], [gemm], name=f"trunk_gemm{index}"))
        if params["activation"] == "tanh":
            activated = f"trunk_tanh{index}"
            nodes.append(helper.make_node("Tanh", [gemm], [activated], name=f"trunk_tanh{index}"))
        else:
            sigmoid = f"trunk_sigmoid{index}"
            activated = f"trunk_swish{index}"
            nodes.append(helper.make_node("Sigmoid", [gemm], [sigmoid], name=f"trunk_sigmoid{index}"))
            nodes.append(helper.make_node("Mul", [gemm, sigmoid], [activated], name=f"trunk_swish{index}"))
        previous = activated
    hidden = previous

    previous = "context_in"
    for index, (weights, bias) in enumerate(params["context"]):
        initializers.append(numpy_helper.from_array(weights.astype(np.float32), name=f"context_w{index}"))
        initializers.append(numpy_helper.from_array(bias.astype(np.float32), name=f"context_b{index}"))
        gemm = f"context_gemm{index}"
        nodes.append(helper.make_node("Gemm", [previous, f"context_w{index}", f"context_b{index}"], [gemm], name=f"context_gemm{index}"))
        if index < len(params["context"]) - 1:
            if params["activation"] == "tanh":
                activated = f"context_tanh{index}"
                nodes.append(helper.make_node("Tanh", [gemm], [activated], name=f"context_tanh{index}"))
            else:
                sigmoid = f"context_sigmoid{index}"
                activated = f"context_swish{index}"
                nodes.append(helper.make_node("Sigmoid", [gemm], [sigmoid], name=f"context_sigmoid{index}"))
                nodes.append(helper.make_node("Mul", [gemm, sigmoid], [activated], name=f"context_swish{index}"))
            previous = activated
        else:
            previous = gemm
    context_out = previous
    hidden_dim = int(params["output"][0].shape[0])
    initializers.append(
        numpy_helper.from_array(np.asarray([hidden_dim, hidden_dim], dtype=np.int64), name="split_sizes")
    )
    nodes.extend(
        [
            helper.make_node("Split", [context_out, "split_sizes"], ["gamma_raw", "beta_raw"], name="context_split", axis=1),
            helper.make_node("Tanh", ["gamma_raw"], ["gamma_tanh"], name="gamma_tanh"),
            helper.make_node("Tanh", ["beta_raw"], ["beta_tanh"], name="beta_tanh"),
            helper.make_node("Mul", ["gamma_tanh", "modulation_scale"], ["gamma_scaled"], name="gamma_scale"),
            helper.make_node("Mul", ["beta_tanh", "modulation_scale"], ["beta_scaled"], name="beta_scale"),
            helper.make_node("Add", ["gamma_scaled", "one_initializer"], ["gamma_plus_one"], name="gamma_plus_one"),
        ]
    )
    # Add the scalar initializer after nodes are assembled to keep the computation readable.
    initializers.append(numpy_helper.from_array(np.asarray([1.0], dtype=np.float32), name="one_initializer"))
    nodes.extend(
        [
            helper.make_node("Mul", [hidden, "gamma_plus_one"], ["hidden_scaled"], name="hidden_apply_gamma"),
            helper.make_node("Add", ["hidden_scaled", "beta_scaled"], ["hidden_modulated"], name="hidden_apply_beta"),
        ]
    )
    output_w, output_b = params["output"]
    initializers.append(numpy_helper.from_array(output_w.astype(np.float32), name="output_w"))
    initializers.append(numpy_helper.from_array(output_b.astype(np.float32), name="output_b"))
    nodes.extend(
        [
            helper.make_node("Gemm", ["hidden_modulated", "output_w", "output_b"], ["loc"], name="output_gemm"),
            helper.make_node("Tanh", ["loc"], ["continuous_actions"], name="output_tanh"),
        ]
    )
    graph = helper.make_graph(
        nodes,
        "open_duck_phase_modulated_bc_student",
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

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    sample = obs[: min(64, obs.shape[0])].astype(np.float32)
    _, expected = forward_np(sample, params)
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
    lines = [
        "# Phase-Modulated BC Student",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline behavior cloning with a shared trunk and command/phase modulation.",
        "No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{report['manifest']}`",
        f"- samples: `{report['samples']}`",
        f"- context indices: `{report['context_indices']}`",
        f"- trunk hidden sizes: `{report['trunk_hidden_sizes']}`",
        f"- context hidden sizes: `{report['context_hidden_sizes']}`",
        f"- modulation scale: `{report['modulation_scale']}`",
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
        "",
        "## ONNX Verification",
        "",
        f"- samples checked: `{report['onnx_verify']['samples_checked']}`",
        f"- p95 abs error: `{report['onnx_verify']['p95_abs_error']:.8f}`",
        f"- max abs error: `{report['onnx_verify']['max_abs_error']:.8f}`",
        "",
    ]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--trunk-hidden-sizes", default="512,256")
    parser.add_argument("--context-hidden-sizes", default="64")
    parser.add_argument("--context-indices", dest="context_indices", default="6,99,100")
    parser.add_argument("--modulation-scale", type=float, default=0.5)
    parser.add_argument("--activation", choices=["tanh", "swish"], default="swish")
    parser.add_argument("--steps", type=int, default=7000)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=500)
    parser.add_argument("--target-rate-scale", type=float, default=0.1)
    parser.add_argument("--target-rate-limit-rad-s", type=float, default=3.75)
    parser.add_argument("--target-rate-limits-rad-s", default="")
    parser.add_argument("--phase-rate-spec", default="")
    parser.add_argument("--phase-rate-scale", type=float, default=0.0)
    parser.add_argument("--phase-rate-limit-rad-s", type=float, default=1.2)
    parser.add_argument("--action-scale-rad", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--save-npz", default="outputs/analysis/phase_modulated_bc_student_candidate/candidate_mlp.npz")
    parser.add_argument("--export-onnx", default="outputs/analysis/phase_modulated_bc_student_candidate/candidate.onnx")
    parser.add_argument("--output-md", default="outputs/analysis/PHASE_MODULATED_BC_STUDENT.md")
    parser.add_argument("--output-json", default="outputs/analysis/phase_modulated_bc_student.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    obs, actions, pairs, weights = read_manifest_samples(Path(args.manifest))
    target_rate_limits = parse_rate_limits(
        args.target_rate_limits_rad_s, actions.shape[1], args.target_rate_limit_rad_s
    )
    fit = train_model(obs, actions, pairs, weights, args)
    save_npz(Path(args.save_npz), fit)
    onnx_verify = export_onnx(Path(args.export_onnx), fit, obs)
    report = {
        "status": "PASS_PHASE_MODULATED_BC_FIT_SMOKE",
        "manifest": args.manifest,
        "samples": int(obs.shape[0]),
        "context_indices": parse_int_list(args.context_indices),
        "trunk_hidden_sizes": fit["trunk_hidden_sizes"],
        "context_hidden_sizes": fit["context_hidden_sizes"],
        "modulation_scale": float(args.modulation_scale),
        "activation": args.activation,
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
            "target_rate_limits_rad_s": target_rate_limits.tolist(),
            "phase_rate_spec": args.phase_rate_spec,
            "phase_rate_scale": float(args.phase_rate_scale),
            "phase_rate_limit_rad_s": float(args.phase_rate_limit_rad_s),
            "seed": int(args.seed),
        },
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
