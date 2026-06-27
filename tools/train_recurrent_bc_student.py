#!/usr/bin/env python3
"""Train a small stateful recurrent BC student from trace sequences.

This is an offline diagnostic for the live-oracle phase-student branch. It
exports an explicit stateful ONNX contract:

  inputs:  obs[1,101], h_in[1,H]
  outputs: continuous_actions[1,14], h_out[1,H]

The current robot runtime does not carry h_in/h_out, so this export is not
deployable. It is only for canonical closed-loop sim gates through the
stateful evaluator flags.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


def percentile(values, q: float) -> float | None:
    arr = np.asarray(values, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    return float(np.percentile(arr, q))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_manifest_sequences(manifest_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text())
    sequences: list[dict[str, Any]] = []
    for entry in manifest.get("entries", []):
        if not entry.get("bc_ready", False):
            continue
        source_path = Path(entry["source_path"])
        if not source_path.exists():
            continue
        obs_rows: list[np.ndarray] = []
        action_rows: list[np.ndarray] = []
        weight_rows: list[float] = []
        entry_weight = max(float(entry.get("sample_weight", 1.0)), 0.0)
        for record in read_jsonl(source_path):
            obs = np.asarray(record.get("obs_state"), dtype=np.float64).reshape(-1)
            action = np.asarray(record.get("action"), dtype=np.float64).reshape(-1)
            if obs.shape != (101,) or action.shape != (14,):
                continue
            obs_rows.append(obs)
            action_rows.append(np.clip(action, -1.0, 1.0))
            weight_rows.append(entry_weight * max(float(record.get("sample_weight", 1.0)), 0.0))
        if obs_rows:
            weights = np.asarray(weight_rows, dtype=np.float64)
            if not np.any(weights > 0):
                weights = np.ones_like(weights)
            sequences.append(
                {
                    "source_path": str(source_path),
                    "source_name": entry.get("source_name", source_path.name),
                    "obs": np.asarray(obs_rows, dtype=np.float64),
                    "actions": np.asarray(action_rows, dtype=np.float64),
                    "weights": weights,
                }
            )
    if not sequences:
        raise ValueError(f"no BC-ready recurrent sequences found in {manifest_path}")
    return sequences, manifest


def flatten_sequences(sequences: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    obs = np.concatenate([seq["obs"] for seq in sequences], axis=0)
    actions = np.concatenate([seq["actions"] for seq in sequences], axis=0)
    weights = np.concatenate([seq["weights"] for seq in sequences], axis=0)
    return obs, actions, weights


def init_params(obs_dim: int, hidden_dim: int, action_dim: int, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(int(seed))
    scale_in = math.sqrt(2.0 / max(obs_dim + hidden_dim, 1))
    scale_h = math.sqrt(2.0 / max(hidden_dim + hidden_dim, 1))
    scale_out = math.sqrt(2.0 / max(hidden_dim + action_dim, 1))
    return {
        "wx": rng.normal(0.0, scale_in, size=(obs_dim, hidden_dim)).astype(np.float64),
        "wh": rng.normal(0.0, scale_h, size=(hidden_dim, hidden_dim)).astype(np.float64),
        "bh": np.zeros((hidden_dim,), dtype=np.float64),
        "wa": rng.normal(0.0, scale_out, size=(hidden_dim, action_dim)).astype(np.float64),
        "ba": np.zeros((action_dim,), dtype=np.float64),
    }


def forward_np(obs: np.ndarray, h_in: np.ndarray, params: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    h_out = np.tanh(obs @ params["wx"] + h_in @ params["wh"] + params["bh"])
    action = np.tanh(h_out @ params["wa"] + params["ba"])
    return action, h_out


def sequence_metrics(
    sequences: list[dict[str, Any]],
    params: dict[str, np.ndarray],
    norm: np.ndarray,
    args: argparse.Namespace,
) -> dict[str, Any]:
    errors = []
    target_rates = []
    for seq in sequences:
        h = np.zeros((1, int(args.hidden_dim)), dtype=np.float64)
        pred_rows = []
        obs_norm = (seq["obs"] - norm[0]) / norm[1]
        for row in obs_norm:
            pred, h = forward_np(row[None, :], h, params)
            pred_rows.append(pred[0])
        pred_arr = np.asarray(pred_rows, dtype=np.float64)
        errors.append(np.abs(pred_arr - seq["actions"]))
        if pred_arr.shape[0] >= 2:
            target_rates.append(
                np.abs(np.diff(pred_arr, axis=0)) * float(args.action_scale_rad) / float(args.dt_s)
            )
    err = np.concatenate(errors, axis=0) if errors else np.zeros((0, 14))
    rates = np.concatenate(target_rates, axis=0) if target_rates else np.zeros((0, 14))
    return {
        "samples": int(err.shape[0]),
        "mae": float(np.mean(err)) if err.size else None,
        "p95_abs_error": percentile(err, 95),
        "p99_abs_error": percentile(err, 99),
        "max_abs_error": float(np.max(err)) if err.size else None,
        "target_rate_p95_rad_s": percentile(rates, 95),
        "target_rate_max_rad_s": float(np.max(rates)) if rates.size else None,
    }


def train_model(sequences: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    os.environ.setdefault("JAX_PLATFORMS", "cpu")
    os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")
    import jax
    import jax.numpy as jnp
    import optax

    obs_all, _, _ = flatten_sequences(sequences)
    mean = obs_all.mean(axis=0)
    std = np.where(obs_all.std(axis=0) < 1.0e-8, 1.0, obs_all.std(axis=0))
    norm = np.stack([mean, std]).astype(np.float64)
    params_np = init_params(101, int(args.hidden_dim), 14, int(args.seed))
    params = {key: jnp.asarray(value, dtype=jnp.float32) for key, value in params_np.items()}
    optimizer = optax.adam(float(args.learning_rate))
    opt_state = optimizer.init(params)
    rng = np.random.default_rng(int(args.seed))
    eligible = [
        index
        for index, seq in enumerate(sequences)
        if int(seq["obs"].shape[0]) >= int(args.sequence_length)
    ]
    if not eligible:
        raise ValueError("no sequence is long enough for --sequence-length")

    def forward_step(model_params, carry, obs_t):
        h = carry
        h_next = jnp.tanh(obs_t @ model_params["wx"] + h @ model_params["wh"] + model_params["bh"])
        action = jnp.tanh(h_next @ model_params["wa"] + model_params["ba"])
        return h_next, action

    def loss_fn(model_params, batch_obs, batch_actions, batch_weights):
        batch_size = batch_obs.shape[0]
        h0 = jnp.zeros((batch_size, int(args.hidden_dim)), dtype=jnp.float32)
        _, pred_tb = jax.lax.scan(
            lambda h, obs_t: forward_step(model_params, h, obs_t),
            h0,
            jnp.swapaxes(batch_obs, 0, 1),
        )
        pred = jnp.swapaxes(pred_tb, 0, 1)
        per_sample = jnp.mean((pred - batch_actions) ** 2, axis=2)
        supervised = jnp.sum(per_sample * batch_weights) / jnp.maximum(jnp.sum(batch_weights), 1.0e-9)
        target_rate = jnp.abs(pred[:, 1:, :] - pred[:, :-1, :]) * float(args.action_scale_rad) / float(args.dt_s)
        excess = jnp.maximum(target_rate - float(args.target_rate_limit_rad_s), 0.0)
        rate_penalty = jnp.mean(excess**2)
        return supervised + float(args.target_rate_scale) * rate_penalty

    @jax.jit
    def step(model_params, state, batch_obs, batch_actions, batch_weights):
        loss, grads = jax.value_and_grad(loss_fn)(model_params, batch_obs, batch_actions, batch_weights)
        updates, state = optimizer.update(grads, state, model_params)
        return optax.apply_updates(model_params, updates), state, loss

    loss_rows = []
    for train_step in range(1, int(args.steps) + 1):
        obs_batch = []
        action_batch = []
        weight_batch = []
        for _ in range(int(args.batch_size)):
            seq = sequences[int(rng.choice(eligible))]
            max_start = int(seq["obs"].shape[0]) - int(args.sequence_length)
            start = int(rng.integers(0, max_start + 1))
            end = start + int(args.sequence_length)
            obs_batch.append((seq["obs"][start:end] - norm[0]) / norm[1])
            action_batch.append(seq["actions"][start:end])
            weight_batch.append(seq["weights"][start:end])
        params, opt_state, loss = step(
            params,
            opt_state,
            jnp.asarray(np.asarray(obs_batch), dtype=jnp.float32),
            jnp.asarray(np.asarray(action_batch), dtype=jnp.float32),
            jnp.asarray(np.asarray(weight_batch), dtype=jnp.float32),
        )
        if train_step == 1 or train_step % max(1, int(args.log_every)) == 0 or train_step == int(args.steps):
            loss_rows.append({"step": int(train_step), "loss": float(loss)})

    params_out = {key: np.asarray(value, dtype=np.float64) for key, value in params.items()}
    metrics = sequence_metrics(sequences, params_out, norm, args)
    return {
        "params": params_out,
        "norm": norm,
        "loss_rows": loss_rows,
        "metrics": metrics,
    }


def save_npz(path: Path, fit: dict[str, Any], args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "output_mode": np.asarray(["stateful_rnn_tanh"]),
        "hidden_dim": np.asarray([int(args.hidden_dim)], dtype=np.int64),
        "norm": fit["norm"].astype(np.float32),
    }
    for key, value in fit["params"].items():
        payload[key] = value.astype(np.float32)
    np.savez(path, **payload)


def export_onnx(path: Path, fit: dict[str, Any], sequences: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    import onnx
    from onnx import TensorProto, helper, numpy_helper
    import onnxruntime as ort

    path.parent.mkdir(parents=True, exist_ok=True)
    params = fit["params"]
    norm = fit["norm"]
    initializers = [
        numpy_helper.from_array(norm[0].astype(np.float32), name="obs_mean"),
        numpy_helper.from_array(norm[1].astype(np.float32), name="obs_std"),
    ]
    for key, value in params.items():
        initializers.append(numpy_helper.from_array(value.astype(np.float32), name=key))
    nodes = [
        helper.make_node("Sub", ["obs", "obs_mean"], ["obs_centered"], name="norm_sub"),
        helper.make_node("Div", ["obs_centered", "obs_std"], ["obs_norm"], name="norm_div"),
        helper.make_node("Gemm", ["obs_norm", "wx"], ["obs_proj"], name="obs_gemm"),
        helper.make_node("Gemm", ["h_in", "wh"], ["h_proj"], name="hidden_gemm"),
        helper.make_node("Add", ["obs_proj", "h_proj"], ["h_sum"], name="hidden_sum"),
        helper.make_node("Add", ["h_sum", "bh"], ["h_pre"], name="hidden_bias"),
        helper.make_node("Tanh", ["h_pre"], ["h_out"], name="hidden_tanh"),
        helper.make_node("Gemm", ["h_out", "wa", "ba"], ["action_pre"], name="action_gemm"),
        helper.make_node("Tanh", ["action_pre"], ["continuous_actions"], name="action_tanh"),
    ]
    graph = helper.make_graph(
        nodes,
        "open_duck_recurrent_bc_student",
        [
            helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, 101]),
            helper.make_tensor_value_info("h_in", TensorProto.FLOAT, [1, int(args.hidden_dim)]),
        ],
        [
            helper.make_tensor_value_info("continuous_actions", TensorProto.FLOAT, [1, 14]),
            helper.make_tensor_value_info("h_out", TensorProto.FLOAT, [1, int(args.hidden_dim)]),
        ],
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
    seq = sequences[0]
    limit = min(int(args.verify_steps), int(seq["obs"].shape[0]))
    h_np = np.zeros((1, int(args.hidden_dim)), dtype=np.float32)
    h_onnx = h_np.copy()
    max_action_err = 0.0
    max_hidden_err = 0.0
    for index in range(limit):
        obs_raw = seq["obs"][index : index + 1].astype(np.float32)
        obs_norm = ((seq["obs"][index : index + 1] - norm[0]) / norm[1]).astype(np.float32)
        expected_action, h_np = forward_np(obs_norm, h_np, params)
        actual_action, h_onnx = session.run(
            ["continuous_actions", "h_out"], {"obs": obs_raw, "h_in": h_onnx}
        )
        max_action_err = max(max_action_err, float(np.max(np.abs(actual_action - expected_action))))
        max_hidden_err = max(max_hidden_err, float(np.max(np.abs(h_onnx - h_np))))
    return {
        "path": str(path),
        "steps_checked": int(limit),
        "max_action_error": max_action_err,
        "max_hidden_error": max_hidden_err,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Recurrent BC Student",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline stateful behavior-cloning diagnostic. It did not train PPO, deploy, SSH, run robot tests, or change robot runtime behavior.",
        "",
        "## Contract",
        "",
        "```text",
        "inputs:  obs[1,101], h_in[1,H]",
        "outputs: continuous_actions[1,14], h_out[1,H]",
        "```",
        "",
        "This ONNX is not robot-deployable without a runtime hidden-state adapter.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{report['manifest']}`",
        f"- sequences: `{report['sequences']}`",
        f"- samples: `{report['samples']}`",
        f"- hidden_dim: `{report['hidden_dim']}`",
        f"- sequence_length: `{report['config']['sequence_length']}`",
        "",
        "## Fit Metrics",
        "",
        f"- MAE: `{report['train_metrics']['mae']:.6f}`",
        f"- p95 abs error: `{report['train_metrics']['p95_abs_error']:.6f}`",
        f"- max abs error: `{report['train_metrics']['max_abs_error']:.6f}`",
        f"- target-rate p95: `{report['train_metrics']['target_rate_p95_rad_s']:.6f}` rad/s",
        f"- target-rate max: `{report['train_metrics']['target_rate_max_rad_s']:.6f}` rad/s",
        "",
        "## ONNX Verification",
        "",
        f"- steps checked: `{report['onnx_verify']['steps_checked']}`",
        f"- max action error: `{report['onnx_verify']['max_action_error']:.8f}`",
        f"- max hidden error: `{report['onnx_verify']['max_hidden_error']:.8f}`",
        "",
        "## Eval Command",
        "",
        "```bash",
        "tools/run_candidate_seed_sweep.py \\",
        f"  --policies recurrent={report['exported_onnx']} \\",
        "  --policy-obs-input-name obs \\",
        "  --policy-action-output-name continuous_actions \\",
        "  --policy-state-input-names h_in \\",
        "  --policy-state-output-names h_out \\",
        "  --task flat_terrain_backlash --bridge-mode fitted --command-x 0.08 --duration 15 --seeds 0-7 --run",
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--sequence-length", type=int, default=32)
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=250)
    parser.add_argument("--target-rate-scale", type=float, default=0.05)
    parser.add_argument("--target-rate-limit-rad-s", type=float, default=3.75)
    parser.add_argument("--action-scale-rad", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--verify-steps", type=int, default=128)
    parser.add_argument("--save-npz", default="outputs/analysis/recurrent_bc_student_candidate/candidate_rnn.npz")
    parser.add_argument("--export-onnx", default="outputs/analysis/recurrent_bc_student_candidate/candidate.onnx")
    parser.add_argument("--output-md", default="outputs/analysis/RECURRENT_BC_STUDENT.md")
    parser.add_argument("--output-json", default="outputs/analysis/recurrent_bc_student.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sequences, _ = load_manifest_sequences(Path(args.manifest))
    obs_all, _, _ = flatten_sequences(sequences)
    fit = train_model(sequences, args)
    save_npz(Path(args.save_npz), fit, args)
    onnx_verify = export_onnx(Path(args.export_onnx), fit, sequences, args)
    report = {
        "status": "PASS_RECURRENT_BC_FIT_SMOKE",
        "manifest": args.manifest,
        "sequences": len(sequences),
        "samples": int(obs_all.shape[0]),
        "hidden_dim": int(args.hidden_dim),
        "saved_npz": args.save_npz,
        "exported_onnx": args.export_onnx,
        "train_metrics": fit["metrics"],
        "loss_rows": fit["loss_rows"],
        "onnx_verify": onnx_verify,
        "config": {
            "steps": int(args.steps),
            "batch_size": int(args.batch_size),
            "sequence_length": int(args.sequence_length),
            "learning_rate": float(args.learning_rate),
            "target_rate_scale": float(args.target_rate_scale),
            "target_rate_limit_rad_s": float(args.target_rate_limit_rad_s),
            "seed": int(args.seed),
        },
        "no_robot_tests": True,
        "no_deploy": True,
        "runtime_behavior_changed": False,
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
