#!/usr/bin/env python3
"""Report whether the full-8 selected source is linearly routable from obs.

This diagnostic asks whether a stateless linear score over the deployed
observation vector can separate the seed-5 `iter25` branch from the selected
command-gated branch. It does not train a policy, deploy, SSH, run robot tests,
change runtime behavior, or run grounded replay.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "outputs/analysis/phase2_full8_router_source_selected_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_FULL8_OBS_LINEAR_ROUTER_SEPARABILITY.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_full8_obs_linear_router_separability.json"


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


def percentile(values: np.ndarray, q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64).reshape(-1), q))


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


def load_groups(manifest_path: Path, positive_marker: str) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text())
    positive = []
    negative = []
    entries = []
    for entry in manifest.get("entries", []):
        if not entry.get("bc_ready", False):
            continue
        source_path = Path(entry["source_path"])
        obs = load_obs(source_path)
        is_positive = positive_marker in str(source_path)
        (positive if is_positive else negative).append(obs)
        entries.append(
            {
                "source_path": rel(source_path),
                "samples": int(obs.shape[0]),
                "branch": "positive" if is_positive else "negative",
            }
        )
    if not positive or not negative:
        raise ValueError("manifest must contain both positive and negative branch traces")
    return np.concatenate(positive, axis=0), np.concatenate(negative, axis=0), entries


def fit_diag_linear(positive: np.ndarray, negative: np.ndarray, variance_floor: float) -> dict[str, Any]:
    mu_pos = positive.mean(axis=0)
    mu_neg = negative.mean(axis=0)
    center = (mu_pos + mu_neg) / 2.0
    pooled_var = 0.5 * (positive.var(axis=0) + negative.var(axis=0))
    weights = (mu_pos - mu_neg) / np.where(pooled_var < variance_floor, variance_floor, pooled_var)
    norm = float(np.linalg.norm(weights))
    if norm > 0.0:
        weights = weights / norm
    pos_scores = (positive - center) @ weights
    neg_scores = (negative - center) @ weights
    if float(pos_scores.mean()) >= float(neg_scores.mean()):
        direction = "ge"
        threshold = (percentile(pos_scores, 5) + percentile(neg_scores, 95)) / 2.0
        pos_selected = pos_scores >= threshold
        neg_selected = neg_scores >= threshold
    else:
        direction = "le"
        threshold = (percentile(pos_scores, 95) + percentile(neg_scores, 5)) / 2.0
        pos_selected = pos_scores <= threshold
        neg_selected = neg_scores <= threshold
    top = []
    for index in np.argsort(np.abs(weights))[::-1][:20]:
        top.append(
            {
                "obs_index": int(index),
                "weight": float(weights[index]),
                "center": float(center[index]),
                "positive_mean": float(mu_pos[index]),
                "negative_mean": float(mu_neg[index]),
            }
        )
    return {
        "direction": direction,
        "threshold": float(threshold),
        "positive_scores": {
            "mean": float(pos_scores.mean()),
            "p05": percentile(pos_scores, 5),
            "p50": percentile(pos_scores, 50),
            "p95": percentile(pos_scores, 95),
        },
        "negative_scores": {
            "mean": float(neg_scores.mean()),
            "p05": percentile(neg_scores, 5),
            "p50": percentile(neg_scores, 50),
            "p95": percentile(neg_scores, 95),
        },
        "positive_selected_pct": float(np.mean(pos_selected) * 100.0),
        "negative_false_selected_pct": float(np.mean(neg_selected) * 100.0),
        "balanced_accuracy_pct": float(
            0.5 * (np.mean(pos_selected) + np.mean(~neg_selected)) * 100.0
        ),
        "top_features": top,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    fit = report["linear_fit"]
    status = report["status"]
    lines = [
        "# Full-8 Obs-Linear Router Separability",
        "",
        f"status: `{status}`",
        "",
        "Offline diagnostic only. It did not train a policy, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{report['manifest']}`",
        f"- positive_marker: `{report['positive_marker']}`",
        f"- positive_samples: `{report['positive_samples']}`",
        f"- negative_samples: `{report['negative_samples']}`",
        "",
        "## Linear Score",
        "",
        f"- direction: `{fit['direction']}`",
        f"- threshold: `{fit['threshold']:.6f}`",
        f"- positive selected: `{fit['positive_selected_pct']:.2f}%`",
        f"- negative false selected: `{fit['negative_false_selected_pct']:.2f}%`",
        f"- balanced accuracy: `{fit['balanced_accuracy_pct']:.2f}%`",
        "",
        "| group | mean | p05 | p50 | p95 |",
        "|---|---:|---:|---:|---:|",
        (
            f"| positive | {fit['positive_scores']['mean']:.6f} | {fit['positive_scores']['p05']:.6f} | "
            f"{fit['positive_scores']['p50']:.6f} | {fit['positive_scores']['p95']:.6f} |"
        ),
        (
            f"| negative | {fit['negative_scores']['mean']:.6f} | {fit['negative_scores']['p05']:.6f} | "
            f"{fit['negative_scores']['p50']:.6f} | {fit['negative_scores']['p95']:.6f} |"
        ),
        "",
        "## Top Features",
        "",
        "| obs_index | weight | center | positive_mean | negative_mean |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in fit["top_features"]:
        lines.append(
            f"| {row['obs_index']} | {row['weight']:.6f} | {row['center']:.6f} | "
            f"{row['positive_mean']:.6f} | {row['negative_mean']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            report["decision"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--positive-marker", default="iter25/seed_005")
    parser.add_argument("--variance-floor", type=float, default=1.0e-4)
    parser.add_argument("--min-balanced-accuracy-pct", type=float, default=85.0)
    parser.add_argument("--max-negative-false-selected-pct", type=float, default=10.0)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    positive, negative, entries = load_groups(manifest_path, args.positive_marker)
    fit = fit_diag_linear(positive, negative, float(args.variance_floor))
    passed = (
        fit["balanced_accuracy_pct"] >= float(args.min_balanced_accuracy_pct)
        and fit["negative_false_selected_pct"] <= float(args.max_negative_false_selected_pct)
    )
    status = "PASS_OBS_LINEAR_ROUTER_SEPARABLE" if passed else "HOLD_OBS_LINEAR_ROUTER_OVERLAP"
    decision = (
        "The selected full-8 source is sufficiently separated for an obs-linear branch gate."
        if passed
        else (
            "Do not build a two-policy obs-linear gate from this score. The positive seed-5 branch "
            "and negative command-gated branch overlap heavily in stateless observation space, so a "
            "linear gate would select the seed-5 branch on too many non-seed-5 samples."
        )
    )
    report = {
        "created_utc": now_utc(),
        "status": status,
        "manifest": rel(manifest_path),
        "positive_marker": args.positive_marker,
        "positive_samples": int(positive.shape[0]),
        "negative_samples": int(negative.shape[0]),
        "entries": entries,
        "linear_fit": fit,
        "thresholds": {
            "min_balanced_accuracy_pct": float(args.min_balanced_accuracy_pct),
            "max_negative_false_selected_pct": float(args.max_negative_false_selected_pct),
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
