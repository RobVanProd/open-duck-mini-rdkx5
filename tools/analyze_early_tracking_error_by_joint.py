#!/usr/bin/env python3
"""Localize preregistered early actuator tracking error by joint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


JOINTS = (
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
    "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
)


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    positive, negative = scores[labels], scores[~labels]
    return float(np.mean((positive[:, None] > negative[None, :]) + 0.5 * (positive[:, None] == negative[None, :])))


def load(name: str, path: str, ticks: int) -> dict:
    sweep = json.loads(Path(path).read_text())
    values, labels, seeds = [], [], []
    for result in sweep["results"]:
        trace = Path(result["output_dir"]) / "trace.jsonl"
        rows = [json.loads(line) for line in trace.read_text().splitlines()[:ticks]]
        if len(rows) < ticks:
            raise ValueError(f"{trace} has fewer than {ticks} rows")
        errors = np.abs(np.asarray([row["applied_target_rad"] for row in rows]) - np.asarray([row["actual_position_rad"] for row in rows]))
        if errors.shape != (ticks, len(JOINTS)):
            raise ValueError(f"unexpected actuator error shape {errors.shape} in {trace}")
        values.append(np.percentile(errors, 95, axis=0))
        labels.append(result["summary"].get("termination_reason") != "duration_complete")
        seeds.append(int(result["seed"]))
    values_array, labels_array = np.asarray(values), np.asarray(labels, dtype=bool)
    return {
        "name": name, "sweep": path, "samples": len(labels), "failures": int(np.sum(labels_array)),
        "metrics": {
            joint: {
                "roc_auc": auc(values_array[:, index], labels_array),
                "failure_mean_rad": float(np.mean(values_array[labels_array, index])),
                "complete_mean_rad": float(np.mean(values_array[~labels_array, index])),
            }
            for index, joint in enumerate(JOINTS)
        },
        "per_seed": [
            {"seed": seed, "failure": bool(labels_array[i]), "p95_error_rad": {joint: float(values_array[i, j]) for j, joint in enumerate(JOINTS)}}
            for i, seed in enumerate(seeds)
        ],
    }


def main() -> int:
    args = parse_args()
    blocks = [load(name, path, args.window_ticks) for name, path in args.block]
    passing = [joint for joint in JOINTS if all(block["metrics"][joint]["roc_auc"] >= args.minimum_auc for block in blocks)]
    report = {
        "status": "LOCALIZED_TRACKING_ERROR_CANDIDATES_IDENTIFIED" if passing else "TRACKING_ERROR_DISTRIBUTED_NO_JOINT_TARGET",
        "preregistration": args.preregistration,
        "window_ticks": args.window_ticks,
        "minimum_auc_each_block": args.minimum_auc,
        "joint_order": list(JOINTS), "blocks": blocks, "passing_joints": passing,
        "decision": "Causal screen required before any joint change." if passing else "Do not invent a joint correction from the aggregate signal.",
        "intervention_authorized": False, "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Early Tracking-Error Joint Localization", "", f"Status: **{report['status']}**", "",
             "| joint | " + " | ".join(f"{block['name']} AUC" for block in blocks) + " | minimum | passes |",
             "|---|" + "---:|" * (len(blocks) + 2)]
    for joint in JOINTS:
        scores = [block["metrics"][joint]["roc_auc"] for block in blocks]
        lines.append(f"| `{joint}` | " + " | ".join(f"{score:.3f}" for score in scores) + f" | {min(scores):.3f} | `{joint in passing}` |")
    lines += ["", "## Decision", "", report["decision"], "", "Association only; no intervention is authorized."]
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
    parser.add_argument("--window-ticks", type=int, default=10)
    parser.add_argument("--minimum-auc", type=float, default=0.70)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
