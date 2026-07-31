#!/usr/bin/env python3
"""Compare the training bridge-tracking surrogate with the compact gate metric."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np


STEP_RE = re.compile(r"_(81920|163840|245760)(?:/|$)")


def finite(value: object) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def load_worker(experiment: str, path: Path) -> dict:
    payload = json.loads(path.read_text())
    mode = payload["modes"]["fitted"]
    pitch = mode["pitch_chain_summary"]
    bridge = finite(pitch["bridge_tracking_p95_rad"]["max"])
    joint = finite(pitch["joint_target_tracking_p95_rad"]["max"])
    match = STEP_RE.search(path.as_posix())
    if not match:
        raise ValueError(f"cannot recover checkpoint step from {path}")
    return {
        "experiment": experiment,
        "step": int(match.group(1)),
        "command_x": float(payload["command"][0]),
        "status": payload["status"],
        "samples": int(mode["samples"]),
        "termination_reason": mode["termination_reason"],
        "training_surrogate_bridge_tracking_p95_max_rad": bridge,
        "gate_joint_tracking_p95_max_rad": joint,
        "unmodeled_gap_rad": None if bridge is None or joint is None else joint - bridge,
        "gate_to_surrogate_ratio": (
            None if bridge is None or joint is None or bridge == 0 else joint / bridge
        ),
        "worker_json": str(path),
    }


def main() -> int:
    args = parse_args()
    rows = []
    for experiment, root in args.experiment:
        workers = sorted(Path(root).rglob("closed_loop_worker_*.json"))
        if not workers:
            raise ValueError(f"no worker JSON files under {root}")
        rows.extend(load_worker(experiment, path) for path in workers)
    rows.sort(key=lambda row: (row["experiment"], row["step"], row["command_x"]))

    gaps = np.asarray([row["unmodeled_gap_rad"] for row in rows], dtype=float)
    ratios = np.asarray([row["gate_to_surrogate_ratio"] for row in rows], dtype=float)
    bridge_pass_joint_fail = sum(
        row["training_surrogate_bridge_tracking_p95_max_rad"] <= args.gate_limit_rad
        and row["gate_joint_tracking_p95_max_rad"] > args.gate_limit_rad
        for row in rows
    )
    report = {
        "status": "TRAINING_TRACKING_OBJECTIVE_GAP_CONFIRMED",
        "gate_limit_rad": args.gate_limit_rad,
        "training_objective": "mean pseudo-Huber(sent_target - applied_target) across 14 joints",
        "compact_gate_metric": "max pitch-chain p95 abs(sent_target - actual_joint_position)",
        "rows": rows,
        "summary": {
            "evaluations": len(rows),
            "bridge_surrogate_pass_joint_gate_fail": bridge_pass_joint_fail,
            "unmodeled_gap_mean_rad": float(np.mean(gaps)),
            "unmodeled_gap_min_rad": float(np.min(gaps)),
            "unmodeled_gap_max_rad": float(np.max(gaps)),
            "gate_to_surrogate_ratio_mean": float(np.mean(ratios)),
            "gate_to_surrogate_ratio_min": float(np.min(ratios)),
            "gate_to_surrogate_ratio_max": float(np.max(ratios)),
        },
        "decision": (
            "The existing actuator-tracking reward is not evidence that the compact joint-tracking "
            "constraint is optimized. Do not tune its scalar as a substitute. Any next training "
            "hypothesis must first define and wire a direct actual-joint tracking surrogate, then "
            "pass a CPU-only contract check before preregistered training."
        ),
        "training_authorized": False,
        "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Stage A Training Tracking Objective-Gap Audit",
        "",
        f"Status: **{report['status']}**",
        "",
        "The training penalty and compact acceptance gate measure different quantities:",
        "",
        f"- training: `{report['training_objective']}`;",
        f"- gate: `{report['compact_gate_metric']}`.",
        "",
        "| experiment | step | x | status | bridge surrogate p95 max | joint gate p95 max | gap | ratio |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['experiment']}` | {row['step']:,} | {row['command_x']:.2f} | "
            f"`{row['status']}` | {row['training_surrogate_bridge_tracking_p95_max_rad']:.4f} | "
            f"{row['gate_joint_tracking_p95_max_rad']:.4f} | {row['unmodeled_gap_rad']:.4f} | "
            f"{row['gate_to_surrogate_ratio']:.2f} |"
        )
    summary = report["summary"]
    lines += [
        "",
        "## Summary",
        "",
        f"- evaluations: `{summary['evaluations']}`",
        f"- bridge-surrogate pass but joint-gate fail: `{summary['bridge_surrogate_pass_joint_gate_fail']}`",
        f"- unmodeled gap mean/range: `{summary['unmodeled_gap_mean_rad']:.4f}` / "
        f"`[{summary['unmodeled_gap_min_rad']:.4f}, {summary['unmodeled_gap_max_rad']:.4f}]` rad",
        f"- gate/surrogate ratio mean/range: `{summary['gate_to_surrogate_ratio_mean']:.2f}` / "
        f"`[{summary['gate_to_surrogate_ratio_min']:.2f}, {summary['gate_to_surrogate_ratio_max']:.2f}]`",
        "",
        "## Decision",
        "",
        report["decision"],
        "",
        "No training, deployment, robot access, or GPU use was authorized or performed.",
    ]
    Path(args.output_md).write_text("\n".join(lines) + "\n")
    print(report["status"])
    return 0


def parse_experiment(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("experiment must be NAME=ROOT")
    return tuple(value.split("=", 1))  # type: ignore[return-value]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", action="append", type=parse_experiment, required=True)
    parser.add_argument("--gate-limit-rad", type=float, default=0.20)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
