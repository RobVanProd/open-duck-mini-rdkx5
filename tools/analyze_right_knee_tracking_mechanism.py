#!/usr/bin/env python3
"""Test preregistered right-knee target-demand mechanisms in saved traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


FEATURES = (
    "applied_target_rate_p95_rad_s",
    "rate_saturation_fraction",
    "limiter_clip_gap_p95_rad",
    "prelimit_target_rate_p95_rad_s",
)


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    pos, neg = scores[labels], scores[~labels]
    return float(np.mean((pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])))


def correlation(a: np.ndarray, b: np.ndarray) -> float | None:
    if float(np.std(a)) == 0.0 or float(np.std(b)) == 0.0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def trace_features(rows: list[dict], index: int, dt: float, rate_limit: float) -> dict[str, float]:
    applied = np.asarray([row["applied_target_rad"][index] for row in rows], dtype=float)
    prelimit = np.asarray([row["target_pre_rate_limit_rad"][index] for row in rows], dtype=float)
    actual = np.asarray([row["actual_position_rad"][index] for row in rows], dtype=float)
    applied_rate = np.abs(np.diff(applied)) / dt
    prelimit_rate = np.abs(np.diff(prelimit)) / dt
    tracking = np.abs(applied - actual)
    return {
        "applied_target_rate_p95_rad_s": float(np.percentile(applied_rate, 95)),
        "rate_saturation_fraction": float(np.mean(applied_rate >= 0.95 * rate_limit)),
        "limiter_clip_gap_p95_rad": float(np.percentile(np.abs(prelimit - applied), 95)),
        "prelimit_target_rate_p95_rad_s": float(np.percentile(prelimit_rate, 95)),
        "right_knee_tracking_error_p95_rad": float(np.percentile(tracking, 95)),
    }


def load(name: str, path: str, args: argparse.Namespace) -> dict:
    sweep = json.loads(Path(path).read_text())
    rows = []
    for result in sweep["results"]:
        trace = Path(result["output_dir"]) / "trace.jsonl"
        records = [json.loads(line) for line in trace.read_text().splitlines()[: args.window_ticks]]
        if len(records) < args.window_ticks:
            raise ValueError(f"{trace} has too few rows")
        rows.append({
            "seed": int(result["seed"]),
            "failure": result["summary"].get("termination_reason") != "duration_complete",
            **trace_features(records, args.joint_index, args.dt_s, args.rate_limit_rad_s),
        })
    labels = np.asarray([row["failure"] for row in rows], dtype=bool)
    tracking = np.asarray([row["right_knee_tracking_error_p95_rad"] for row in rows])
    metrics = {}
    for feature in FEATURES:
        values = np.asarray([row[feature] for row in rows])
        metrics[feature] = {
            "roc_auc": auc(values, labels),
            "tracking_error_pearson": correlation(values, tracking),
            "failure_mean": float(np.mean(values[labels])),
            "complete_mean": float(np.mean(values[~labels])),
        }
    return {"name": name, "sweep": path, "samples": len(rows), "failures": int(np.sum(labels)), "metrics": metrics, "per_seed": rows}


def main() -> int:
    args = parse_args()
    blocks = [load(name, path, args) for name, path in args.block]
    passing = [feature for feature in FEATURES if all(
        block["metrics"][feature]["roc_auc"] >= args.minimum_auc
        and block["metrics"][feature]["tracking_error_pearson"] is not None
        and block["metrics"][feature]["tracking_error_pearson"] >= args.minimum_correlation
        for block in blocks
    )]
    report = {
        "status": "RIGHT_KNEE_TARGET_DEMAND_MECHANISM_SUPPORTED" if passing else "RIGHT_KNEE_TARGET_DEMAND_MECHANISM_NOT_SUPPORTED",
        "preregistration": args.preregistration,
        "joint_index": args.joint_index, "joint_name": "right_knee",
        "window_ticks": args.window_ticks, "dt_s": args.dt_s,
        "rate_limit_rad_s": args.rate_limit_rad_s,
        "minimum_auc_each_block": args.minimum_auc,
        "minimum_correlation_each_block": args.minimum_correlation,
        "blocks": blocks, "passing_features": passing,
        "decision": "A single matched causal demand intervention may be preregistered." if passing else "Do not alter the right-knee rate limiter from this evidence.",
        "intervention_authorized": False, "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Right-Knee Tracking Mechanism Result", "", f"Status: **{report['status']}**", "",
             "| feature | " + " | ".join(f"{b['name']} AUC/corr" for b in blocks) + " | passes |",
             "|---|" + "---:|" * (len(blocks) + 1)]
    for feature in FEATURES:
        values = [b["metrics"][feature] for b in blocks]
        formatted = [
            f"{v['roc_auc']:.3f}/" + (f"{v['tracking_error_pearson']:.3f}" if v["tracking_error_pearson"] is not None else "NA")
            for v in values
        ]
        lines.append(f"| `{feature}` | " + " | ".join(formatted) + f" | `{feature in passing}` |")
    lines += ["", "## Decision", "", report["decision"], "", "No limiter or policy change is authorized."]
    Path(args.output_md).write_text("\n".join(lines) + "\n")
    print(report["status"])
    return 0


def parse_block(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("block must be NAME=SWEEP_JSON")
    return tuple(value.split("=", 1))  # type: ignore[return-value]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block", action="append", type=parse_block, required=True)
    parser.add_argument("--joint-index", type=int, default=12)
    parser.add_argument("--window-ticks", type=int, default=10)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--rate-limit-rad-s", type=float, default=2.0)
    parser.add_argument("--minimum-auc", type=float, default=0.70)
    parser.add_argument("--minimum-correlation", type=float, default=0.50)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
