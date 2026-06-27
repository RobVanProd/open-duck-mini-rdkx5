#!/usr/bin/env python3
"""Check PPO step-0 actor fidelity against a BC MLP candidate.

The current PPO actor is tanh-normal: deterministic actions are tanh(loc).
The BC MLP exported by run_target_dataset_bc_smoke.py predicts clipped actions
directly. This tool measures the direct-copy mismatch and tests a safer mapping
that refits only the PPO final loc head to arctanh(BC actions), with hidden
layers and normalization copied from the BC candidate.

This is offline-only: no training, SSH, robot tests, deployment, or runtime
behavior changes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def percentile(values: np.ndarray, q: float) -> float | None:
    if values.size == 0:
        return None
    return float(np.percentile(values.reshape(-1), q))


def read_manifest_samples(manifest_path: Path, *, max_samples: int | None) -> tuple[np.ndarray, np.ndarray]:
    manifest = json.loads(manifest_path.read_text())
    observations: list[list[float]] = []
    actions: list[list[float]] = []
    for entry in manifest.get("entries", []):
        if not entry.get("bc_ready", False):
            continue
        source_path = Path(entry["source_path"])
        if not source_path.exists():
            continue
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
                observations.append(obs_arr.astype(float).tolist())
                actions.append(action_arr.astype(float).tolist())
                if max_samples is not None and len(observations) >= max_samples:
                    return np.asarray(observations), np.asarray(actions)
    if not observations:
        raise ValueError(f"no obs/action samples found in {manifest_path}")
    return np.asarray(observations), np.asarray(actions)


def load_bc_npz(path: Path) -> dict[str, Any]:
    payload = np.load(path, allow_pickle=True)
    hidden_sizes = payload["hidden_sizes"].astype(int).tolist()
    weights = []
    index = 0
    while f"w{index}" in payload.files:
        weights.append((payload[f"w{index}"].astype(np.float64), payload[f"b{index}"].astype(np.float64)))
        index += 1
    return {
        "path": str(path),
        "norm": payload["norm"].astype(np.float64),
        "hidden_sizes": hidden_sizes,
        "weights": weights,
    }


def hidden_forward(obs: np.ndarray, bc: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    mean, std = bc["norm"]
    z = (obs - mean) / std
    weights = bc["weights"]
    for layer_index, (w, b) in enumerate(weights[:-1]):
        z = z @ w + b
        z = np.tanh(z)
    final_w, final_b = weights[-1]
    raw = z @ final_w + final_b
    action = np.clip(raw, -1.0, 1.0)
    return z, action


def action_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    error = candidate - reference
    abs_error = np.abs(error)
    return {
        "samples": int(reference.shape[0]),
        "mae": float(np.mean(abs_error)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "p50_abs_error": percentile(abs_error, 50),
        "p95_abs_error": percentile(abs_error, 95),
        "p99_abs_error": percentile(abs_error, 99),
        "max_abs_error": float(np.max(abs_error)) if abs_error.size else None,
        "candidate_action_saturation_pct": float(np.mean(np.abs(candidate) >= 0.999) * 100.0),
    }


def fit_final_loc_head(
    hidden: np.ndarray,
    reference_action: np.ndarray,
    *,
    alpha: float,
    atanh_clip: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    clipped = np.clip(reference_action, -atanh_clip, atanh_clip)
    target_loc = np.arctanh(clipped)
    design = np.concatenate([hidden, np.ones((hidden.shape[0], 1))], axis=1)
    eye = np.eye(design.shape[1], dtype=np.float64)
    eye[-1, -1] = 0.0
    weights = np.linalg.solve(design.T @ design + float(alpha) * eye, design.T @ target_loc)
    kernel = weights[:-1]
    bias = weights[-1]
    pred = np.tanh(design @ weights)
    return kernel, bias, pred


def run_report(args: argparse.Namespace) -> dict[str, Any]:
    obs, dataset_actions = read_manifest_samples(Path(args.manifest), max_samples=args.max_samples)
    bc = load_bc_npz(Path(args.bc_npz))
    hidden, bc_actions = hidden_forward(obs, bc)

    direct_loc = np.asarray(hidden @ bc["weights"][-1][0] + bc["weights"][-1][1])
    direct_ppo_actions = np.tanh(direct_loc)
    direct_metrics = action_metrics(bc_actions, direct_ppo_actions)
    dataset_metrics = action_metrics(dataset_actions, bc_actions)

    refit_rows = []
    best = None
    for alpha in args.alpha_grid:
        kernel, bias, pred = fit_final_loc_head(
            hidden,
            bc_actions,
            alpha=float(alpha),
            atanh_clip=float(args.atanh_clip),
        )
        metrics = action_metrics(bc_actions, pred)
        row = {
            "alpha": float(alpha),
            "metrics": metrics,
            "kernel_shape": list(kernel.shape),
            "bias_shape": list(bias.shape),
            "kernel_norm": float(np.linalg.norm(kernel)),
            "bias_norm": float(np.linalg.norm(bias)),
        }
        refit_rows.append(row)
        if best is None or (
            metrics["p95_abs_error"],
            metrics["mae"],
            metrics["max_abs_error"],
        ) < (
            best["metrics"]["p95_abs_error"],
            best["metrics"]["mae"],
            best["metrics"]["max_abs_error"],
        ):
            best = row

    assert best is not None
    status = (
        "PASS_PPO_BC_STEP0_ACTION_FIDELITY"
        if best["metrics"]["p95_abs_error"] <= args.pass_p95_abs_error
        and best["metrics"]["max_abs_error"] <= args.pass_max_abs_error
        else "HOLD_PPO_BC_STEP0_ACTION_FIDELITY"
    )
    return {
        "status": status,
        "manifest": args.manifest,
        "bc_npz": args.bc_npz,
        "samples": int(obs.shape[0]),
        "obs_dim": int(obs.shape[1]),
        "action_dim": int(bc_actions.shape[1]),
        "hidden_sizes": bc["hidden_sizes"],
        "atanh_clip": float(args.atanh_clip),
        "pass_thresholds": {
            "p95_abs_error": float(args.pass_p95_abs_error),
            "max_abs_error": float(args.pass_max_abs_error),
        },
        "dataset_action_vs_bc_action": dataset_metrics,
        "direct_copy_tanh_loc": direct_metrics,
        "final_head_refit_best": best,
        "final_head_refit_rows": refit_rows,
        "decision": (
            "Use final-head arctanh refit for PPO loc initialization; direct BC final-head "
            "copy is not exact because PPO exports tanh(loc)."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    direct = report["direct_copy_tanh_loc"]
    refit = report["final_head_refit_best"]
    dataset = report["dataset_action_vs_bc_action"]
    lines = [
        "# PPO BC Step-0 Fidelity",
        "",
        f"status: `{report['status']}`",
        "",
        "This is an offline action-fidelity check. It did not train, deploy, SSH,",
        "run robot tests, or change robot runtime behavior.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{report['manifest']}`",
        f"- BC NPZ: `{report['bc_npz']}`",
        f"- samples: `{report['samples']}`",
        f"- hidden sizes: `{report['hidden_sizes']}`",
        "",
        "## Baseline Consistency",
        "",
        "Dataset trace actions compared with the BC NPZ prediction:",
        "",
        f"- p95 abs error: `{dataset['p95_abs_error']:.6f}`",
        f"- max abs error: `{dataset['max_abs_error']:.6f}`",
        "",
        "## Direct PPO Copy",
        "",
        "Directly copying the BC final action head into PPO loc produces",
        "`tanh(BC_raw_action)`, not `BC_action`. This is the measured mismatch:",
        "",
        f"- p95 abs error: `{direct['p95_abs_error']:.6f}`",
        f"- max abs error: `{direct['max_abs_error']:.6f}`",
        f"- MAE: `{direct['mae']:.6f}`",
        "",
        "## Final Loc Head Refit",
        "",
        "Keeping the BC normalizer and hidden layers fixed, the final PPO loc head",
        "was refit to `atanh(BC_action)`.",
        "",
        f"- best alpha: `{refit['alpha']}`",
        f"- p95 abs error: `{refit['metrics']['p95_abs_error']:.6f}`",
        f"- max abs error: `{refit['metrics']['max_abs_error']:.6f}`",
        f"- MAE: `{refit['metrics']['mae']:.6f}`",
        "",
        "| alpha | p95 abs error | max abs error | MAE |",
        "|---:|---:|---:|---:|",
    ]
    for row in report["final_head_refit_rows"]:
        metrics = row["metrics"]
        lines.append(
            f"| {row['alpha']:.3g} | {metrics['p95_abs_error']:.6f} | "
            f"{metrics['max_abs_error']:.6f} | {metrics['mae']:.6f} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        report["decision"],
        "",
        "This is still only an action-level step-0 check. If it passes, the",
        "next gate must build actual PPO params with this loc head, keep value",
        "params fresh, initialize scale logits deliberately, and run the",
        "standard task-matched fitted closed-loop evaluator before any PPO",
        "updates. If it holds, train or fit a PPO-loc student directly instead",
        "of forcing an action-space BC head into a tanh-normal actor.",
        "",
    ]
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--bc-npz", required=True)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--atanh-clip", type=float, default=0.999)
    parser.add_argument(
        "--alpha-grid",
        type=float,
        nargs="+",
        default=[0.0, 1.0e-8, 1.0e-6, 1.0e-4, 1.0e-2],
    )
    parser.add_argument("--pass-p95-abs-error", type=float, default=0.002)
    parser.add_argument("--pass-max-abs-error", type=float, default=0.02)
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/PPO_BC_WARMSTART_STEP0_FIDELITY.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/ppo_bc_warmstart_step0_fidelity.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_report(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2))
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if report["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
