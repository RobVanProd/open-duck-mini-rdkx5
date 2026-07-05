#!/usr/bin/env python3
"""Report whether the full-8 selected source is nonlinearly routable from obs.

This diagnostic trains a small MLP classifier to distinguish the selected
seed-5 `iter25` branch from the command-gated branch using only the deployed
obs[101] vector. It uses a deterministic per-trace train/test split so the
reported accuracy is held out in time, not just fit accuracy.

It does not train a control policy, deploy, SSH, run robot tests, change robot
runtime behavior, or run grounded replay.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "outputs/analysis/phase2_full8_router_source_selected_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEPARABILITY.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_full8_mlp_router_separability.json"
DEFAULT_SAVE_NPZ = ROOT / "outputs/analysis/phase2_full8_mlp_router_gate/gate_mlp.npz"


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_hidden_sizes(text: str) -> list[int]:
    values = [int(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected at least one hidden size")
    return values


def percentile(values: np.ndarray, q: float) -> float | None:
    arr = np.asarray(values, dtype=np.float64).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    return float(np.percentile(arr, q))


def load_obs(path: Path) -> np.ndarray:
    rows = []
    with path.open() as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            obs = np.asarray(record.get("obs_state"), dtype=np.float64).reshape(-1)
            if obs.shape != (101,):
                raise ValueError(f"{path} row does not contain obs_state[101]")
            rows.append(obs)
    if not rows:
        raise ValueError(f"no obs_state rows in {path}")
    return np.asarray(rows, dtype=np.float64)


def split_trace_indices(n: int, test_fraction: float) -> tuple[np.ndarray, np.ndarray]:
    if not 0.0 < test_fraction < 0.9:
        raise ValueError("--test-fraction must be in (0,0.9)")
    test_count = max(1, int(round(n * test_fraction)))
    train_count = max(1, n - test_count)
    return np.arange(train_count, dtype=np.int64), np.arange(train_count, n, dtype=np.int64)


def load_dataset(
    manifest_path: Path,
    positive_marker: str,
    test_fraction: float,
    extra_negative_traces: list[Path],
    extra_negative_first_ticks: int | None,
    extra_negative_weight: float,
    extra_positive_traces: list[Path],
    extra_positive_first_ticks: int | None,
    extra_positive_weight: float,
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text())
    train_x = []
    train_y = []
    train_w = []
    test_x = []
    test_y = []
    entries = []
    for entry in manifest.get("entries", []):
        if not entry.get("bc_ready", False):
            continue
        source_path = Path(entry["source_path"])
        obs = load_obs(source_path)
        label = 1.0 if positive_marker in str(source_path) else 0.0
        train_idx, test_idx = split_trace_indices(int(obs.shape[0]), test_fraction)
        train_x.append(obs[train_idx])
        train_y.append(np.full((len(train_idx),), label, dtype=np.float64))
        train_w.append(np.ones((len(train_idx),), dtype=np.float64))
        test_x.append(obs[test_idx])
        test_y.append(np.full((len(test_idx),), label, dtype=np.float64))
        entries.append(
            {
                "source_path": rel(source_path),
                "samples": int(obs.shape[0]),
                "train_samples": int(len(train_idx)),
                "test_samples": int(len(test_idx)),
                "branch": "positive" if label > 0.5 else "negative",
                "weight": 1.0,
            }
        )
    for trace_path in extra_negative_traces:
        obs = load_obs(trace_path)
        if extra_negative_first_ticks is not None:
            obs = obs[: max(1, min(int(extra_negative_first_ticks), int(obs.shape[0])))]
        train_x.append(obs)
        train_y.append(np.zeros((int(obs.shape[0]),), dtype=np.float64))
        train_w.append(np.full((int(obs.shape[0]),), float(extra_negative_weight), dtype=np.float64))
        entries.append(
            {
                "source_path": rel(trace_path),
                "samples": int(obs.shape[0]),
                "train_samples": int(obs.shape[0]),
                "test_samples": 0,
                "branch": "negative_correction",
                "weight": float(extra_negative_weight),
            }
        )
    for trace_path in extra_positive_traces:
        obs = load_obs(trace_path)
        if extra_positive_first_ticks is not None:
            obs = obs[: max(1, min(int(extra_positive_first_ticks), int(obs.shape[0])))]
        train_x.append(obs)
        train_y.append(np.ones((int(obs.shape[0]),), dtype=np.float64))
        train_w.append(np.full((int(obs.shape[0]),), float(extra_positive_weight), dtype=np.float64))
        entries.append(
            {
                "source_path": rel(trace_path),
                "samples": int(obs.shape[0]),
                "train_samples": int(obs.shape[0]),
                "test_samples": 0,
                "branch": "positive_correction",
                "weight": float(extra_positive_weight),
            }
        )
    if not train_x:
        raise ValueError(f"no BC-ready entries in {manifest_path}")
    data = {
        "train_x": np.concatenate(train_x, axis=0),
        "train_y": np.concatenate(train_y, axis=0),
        "train_w": np.concatenate(train_w, axis=0),
        "test_x": np.concatenate(test_x, axis=0),
        "test_y": np.concatenate(test_y, axis=0),
    }
    if not (np.any(data["train_y"] > 0.5) and np.any(data["train_y"] < 0.5)):
        raise ValueError("dataset must contain both positive and negative branch labels")
    return data, entries


def init_params(input_dim: int, hidden_sizes: list[int], seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    rng = np.random.default_rng(seed)
    dims = [input_dim, *hidden_sizes, 1]
    params = []
    for in_dim, out_dim in zip(dims[:-1], dims[1:], strict=True):
        scale = np.sqrt(2.0 / max(in_dim + out_dim, 1))
        params.append(
            (
                rng.normal(0.0, scale, size=(in_dim, out_dim)).astype(np.float64),
                np.zeros((out_dim,), dtype=np.float64),
            )
        )
    return params


def train_classifier(data: dict[str, np.ndarray], args: argparse.Namespace) -> dict[str, Any]:
    os.environ.setdefault("JAX_PLATFORMS", "cpu")
    os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")
    import jax
    import jax.numpy as jnp
    import optax

    train_x = data["train_x"]
    train_y = data["train_y"]
    train_extra_w = data.get("train_w", np.ones_like(train_y))
    mean = train_x.mean(axis=0)
    std = np.where(train_x.std(axis=0) < 1.0e-8, 1.0, train_x.std(axis=0))
    x = ((train_x - mean) / std).astype(np.float32)
    y = train_y.astype(np.float32).reshape(-1, 1)
    pos = float(np.sum(train_y > 0.5))
    neg = float(np.sum(train_y < 0.5))
    class_weights = np.where(train_y > 0.5, 0.5 / max(pos, 1.0), 0.5 / max(neg, 1.0)).astype(np.float32)
    class_weights = class_weights * np.asarray(train_extra_w, dtype=np.float32)
    class_weights = (class_weights / np.mean(class_weights)).reshape(-1, 1)
    hidden_sizes = parse_hidden_sizes(args.hidden_sizes)
    params_np = init_params(101, hidden_sizes, int(args.seed))
    params = [(jnp.asarray(w, dtype=jnp.float32), jnp.asarray(b, dtype=jnp.float32)) for w, b in params_np]
    optimizer = optax.adam(float(args.learning_rate))
    opt_state = optimizer.init(params)
    rng = np.random.default_rng(int(args.seed))

    def forward(model_params, batch_x):
        z = batch_x
        for index, (weights, bias) in enumerate(model_params):
            z = z @ weights + bias
            if index < len(model_params) - 1:
                z = jax.nn.swish(z)
        return z

    def loss_fn(model_params, batch_x, batch_y, batch_w):
        logits = forward(model_params, batch_x)
        bce = optax.sigmoid_binary_cross_entropy(logits, batch_y)
        l2 = sum(jnp.sum(w**2) for w, _ in model_params)
        return jnp.mean(bce * batch_w) + float(args.weight_decay) * l2

    @jax.jit
    def step(model_params, state, batch_x, batch_y, batch_w):
        loss, grads = jax.value_and_grad(loss_fn)(model_params, batch_x, batch_y, batch_w)
        updates, state = optimizer.update(grads, state, model_params)
        return optax.apply_updates(model_params, updates), state, loss

    loss_rows = []
    n = int(x.shape[0])
    for train_step in range(1, int(args.steps) + 1):
        idx = rng.integers(0, n, size=int(args.batch_size))
        params, opt_state, loss = step(
            params,
            opt_state,
            jnp.asarray(x[idx], dtype=jnp.float32),
            jnp.asarray(y[idx], dtype=jnp.float32),
            jnp.asarray(class_weights[idx], dtype=jnp.float32),
        )
        if train_step == 1 or train_step % max(1, int(args.log_every)) == 0 or train_step == int(args.steps):
            loss_rows.append({"step": int(train_step), "loss": float(loss)})
    params_np = [(np.asarray(w), np.asarray(b)) for w, b in params]
    return {
        "params": params_np,
        "norm": np.stack([mean, std]).astype(np.float32),
        "hidden_sizes": hidden_sizes,
        "loss_rows": loss_rows,
    }


def save_gate_npz(path: Path, fit: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "output_mode": np.asarray(["obs_mlp_binary_gate"]),
        "hidden_sizes": np.asarray(fit["hidden_sizes"], dtype=np.int64),
        "obs_norm": fit["norm"].astype(np.float32),
    }
    for index, (weights, bias) in enumerate(fit["params"]):
        payload[f"w_{index}"] = weights.astype(np.float32)
        payload[f"b_{index}"] = bias.astype(np.float32)
    np.savez(path, **payload)


def predict_logits(obs: np.ndarray, fit: dict[str, Any]) -> np.ndarray:
    mean, std = fit["norm"]
    z = (obs - mean) / std
    for index, (weights, bias) in enumerate(fit["params"]):
        z = z @ weights + bias
        if index < len(fit["params"]) - 1:
            z = z / (1.0 + np.exp(-z))
    return z.reshape(-1)


def metrics_for_split(logits: np.ndarray, labels: np.ndarray, threshold: float = 0.0) -> dict[str, Any]:
    labels_bool = labels > 0.5
    pred = logits >= threshold
    pos_mask = labels_bool
    neg_mask = ~labels_bool
    positive_selected = float(np.mean(pred[pos_mask]) * 100.0) if np.any(pos_mask) else None
    negative_false_selected = float(np.mean(pred[neg_mask]) * 100.0) if np.any(neg_mask) else None
    balanced = None
    if positive_selected is not None and negative_false_selected is not None:
        balanced = 0.5 * (positive_selected + (100.0 - negative_false_selected))
    return {
        "samples": int(labels.shape[0]),
        "positive_samples": int(np.sum(pos_mask)),
        "negative_samples": int(np.sum(neg_mask)),
        "positive_selected_pct": positive_selected,
        "negative_false_selected_pct": negative_false_selected,
        "balanced_accuracy_pct": balanced,
        "positive_logit_p50": percentile(logits[pos_mask], 50) if np.any(pos_mask) else None,
        "negative_logit_p50": percentile(logits[neg_mask], 50) if np.any(neg_mask) else None,
        "positive_logit_p05": percentile(logits[pos_mask], 5) if np.any(pos_mask) else None,
        "negative_logit_p95": percentile(logits[neg_mask], 95) if np.any(neg_mask) else None,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Full-8 MLP Router Separability",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline diagnostic only. It did not train a control policy, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{report['manifest']}`",
        f"- positive_marker: `{report['positive_marker']}`",
        f"- hidden_sizes: `{report['config']['hidden_sizes']}`",
        f"- train/test split per trace: `{100.0 * (1.0 - report['config']['test_fraction']):.1f}%` / `{100.0 * report['config']['test_fraction']:.1f}%`",
        f"- branch-A correction traces: `{report['config']['extra_negative_trace_count']}`",
        f"- branch-A correction weight: `{report['config']['extra_negative_weight']}`",
        f"- branch-B correction traces: `{report['config']['extra_positive_trace_count']}`",
        f"- branch-B correction weight: `{report['config']['extra_positive_weight']}`",
        "",
        "## Results",
        "",
        "| split | samples | positive_selected | negative_false_selected | balanced_accuracy |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ["train", "test"]:
        item = report["metrics"][name]
        lines.append(
            f"| {name} | {item['samples']} | {item['positive_selected_pct']:.2f}% | "
            f"{item['negative_false_selected_pct']:.2f}% | {item['balanced_accuracy_pct']:.2f}% |"
        )
    lines.extend(
        [
            "",
            "## Logit Separation",
            "",
            "| split | positive p05 | positive p50 | negative p50 | negative p95 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for name in ["train", "test"]:
        item = report["metrics"][name]
        lines.append(
            f"| {name} | {item['positive_logit_p05']:.4f} | {item['positive_logit_p50']:.4f} | "
            f"{item['negative_logit_p50']:.4f} | {item['negative_logit_p95']:.4f} |"
        )
    lines.extend(["", "## Decision", "", report["decision"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--positive-marker", default="iter25/seed_005")
    parser.add_argument("--hidden-sizes", default="64,32")
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=1.0e-3)
    parser.add_argument("--weight-decay", type=float, default=1.0e-5)
    parser.add_argument("--seed", type=int, default=20260705)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--log-every", type=int, default=250)
    parser.add_argument("--min-test-balanced-accuracy-pct", type=float, default=85.0)
    parser.add_argument("--max-test-negative-false-selected-pct", type=float, default=10.0)
    parser.add_argument(
        "--extra-negative-trace",
        action="append",
        default=[],
        help="Trace JSONL whose observations should be branch-A/negative corrective samples.",
    )
    parser.add_argument(
        "--extra-negative-first-ticks",
        type=int,
        default=None,
        help="Use only the first N ticks from each extra negative trace.",
    )
    parser.add_argument("--extra-negative-weight", type=float, default=1.0)
    parser.add_argument(
        "--extra-positive-trace",
        action="append",
        default=[],
        help="Trace JSONL whose observations should be branch-B/positive corrective samples.",
    )
    parser.add_argument(
        "--extra-positive-first-ticks",
        type=int,
        default=None,
        help="Use only the first N ticks from each extra positive trace.",
    )
    parser.add_argument("--extra-positive-weight", type=float, default=1.0)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--save-npz", default=str(DEFAULT_SAVE_NPZ))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extra_negative_traces = [Path(item) for item in args.extra_negative_trace]
    extra_positive_traces = [Path(item) for item in args.extra_positive_trace]
    data, entries = load_dataset(
        Path(args.manifest),
        args.positive_marker,
        float(args.test_fraction),
        extra_negative_traces,
        args.extra_negative_first_ticks,
        float(args.extra_negative_weight),
        extra_positive_traces,
        args.extra_positive_first_ticks,
        float(args.extra_positive_weight),
    )
    fit = train_classifier(data, args)
    save_gate_npz(Path(args.save_npz), fit)
    train_logits = predict_logits(data["train_x"], fit)
    test_logits = predict_logits(data["test_x"], fit)
    metrics = {
        "train": metrics_for_split(train_logits, data["train_y"]),
        "test": metrics_for_split(test_logits, data["test_y"]),
    }
    test = metrics["test"]
    passed = (
        test["balanced_accuracy_pct"] >= float(args.min_test_balanced_accuracy_pct)
        and test["negative_false_selected_pct"] <= float(args.max_test_negative_false_selected_pct)
    )
    status = "PASS_MLP_ROUTER_SEPARABLE" if passed else "HOLD_MLP_ROUTER_OVERLAP"
    decision = (
        "The branch labels are separable by a nonlinear stateless observation gate on the held-out split."
        if passed
        else (
            "Do not assume a stateless nonlinear router is sufficient. The held-out branch classifier "
            "does not meet the false-selection and balanced-accuracy thresholds needed before composing "
            "a two-policy deployable router."
        )
    )
    report = {
        "created_utc": now_utc(),
        "status": status,
        "manifest": rel(Path(args.manifest)),
        "positive_marker": args.positive_marker,
        "entries": entries,
        "metrics": metrics,
        "loss_rows": fit["loss_rows"],
        "config": {
            "hidden_sizes": parse_hidden_sizes(args.hidden_sizes),
            "steps": int(args.steps),
            "batch_size": int(args.batch_size),
            "learning_rate": float(args.learning_rate),
            "weight_decay": float(args.weight_decay),
            "seed": int(args.seed),
            "test_fraction": float(args.test_fraction),
            "extra_negative_trace_count": len(extra_negative_traces),
            "extra_negative_first_ticks": args.extra_negative_first_ticks,
            "extra_negative_weight": float(args.extra_negative_weight),
            "extra_positive_trace_count": len(extra_positive_traces),
            "extra_positive_first_ticks": args.extra_positive_first_ticks,
            "extra_positive_weight": float(args.extra_positive_weight),
        },
        "saved_npz": rel(Path(args.save_npz)),
        "saved_npz_sha256": sha256(Path(args.save_npz)),
        "thresholds": {
            "min_test_balanced_accuracy_pct": float(args.min_test_balanced_accuracy_pct),
            "max_test_negative_false_selected_pct": float(args.max_test_negative_false_selected_pct),
        },
        "decision": decision,
        "no_robot_tests": True,
        "no_ssh": True,
        "no_deploy": True,
        "no_grounded_replay": True,
        "runtime_behavior_changed": False,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_markdown(Path(args.output_md), report)
    print(status)
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
