#!/usr/bin/env python3
"""Calibrate a direct pitch-chain tracking scale to the existing bridge cost."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


PITCH_INDICES = np.asarray([2, 3, 4, 11, 12, 13], dtype=int)


def pseudo_huber(error: np.ndarray, delta: float) -> np.ndarray:
    scaled = error / delta
    return delta**2 * (np.sqrt(1.0 + scaled**2) - 1.0)


def load(label: str, path: str, delta: float, existing_scale: float) -> dict:
    rows = [json.loads(line) for line in Path(path).read_text().splitlines()]
    sent = np.asarray([row["sent_target_rad"] for row in rows], dtype=float)
    applied = np.asarray([row["applied_target_rad"] for row in rows], dtype=float)
    actual = np.asarray([row["actual_position_rad"] for row in rows], dtype=float)
    bridge_cost = float(np.mean(pseudo_huber(sent - applied, delta)))
    pitch_cost = float(
        np.mean(pseudo_huber((sent - actual)[:, PITCH_INDICES], delta))
    )
    return {
        "label": label,
        "trace_jsonl": path,
        "samples": len(rows),
        "bridge_cost_mean": bridge_cost,
        "pitch_joint_target_cost_mean": pitch_cost,
        "pitch_to_bridge_ratio": pitch_cost / bridge_cost,
        "equal_magnitude_direct_scale": existing_scale * bridge_cost / pitch_cost,
    }


def main() -> int:
    args = parse_args()
    rows = [load(label, path, args.huber_delta, args.existing_scale) for label, path in args.trace]
    scales = np.asarray([row["equal_magnitude_direct_scale"] for row in rows])
    registered_scale = float(np.mean(scales))
    report = {
        "status": "PASS_DATA_CALIBRATED_SCALE",
        "huber_delta": args.huber_delta,
        "pitch_joint_indices": PITCH_INDICES.tolist(),
        "existing_bridge_tracking_scale": args.existing_scale,
        "rows": rows,
        "registered_direct_tracking_scale": registered_scale,
        "scale_rule": (
            "mean across the preregistered x=0 and x=0.08 compact traces of the scale "
            "that gives the new pitch-chain cost the same mean absolute reward contribution "
            "as the existing all-joint bridge-tracking cost"
        ),
        "training_authorized": False,
        "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Stage A Joint-Target Tracking Scale Calibration",
        "",
        f"Status: **{report['status']}**",
        "",
        "| trace | bridge cost mean | pitch actual-tracking cost mean | ratio | equal scale |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['label']}` | {row['bridge_cost_mean']:.8f} | "
            f"{row['pitch_joint_target_cost_mean']:.8f} | {row['pitch_to_bridge_ratio']:.3f} | "
            f"{row['equal_magnitude_direct_scale']:.6f} |"
        )
    lines += [
        "",
        f"Registered scale: **`{registered_scale:.6f}`** with pseudo-Huber delta "
        f"`{args.huber_delta:.2f}` on pitch indices `{PITCH_INDICES.tolist()}`.",
        "",
        report["scale_rule"].capitalize() + ".",
        "",
        "This calibration prevents choosing a reward scale by outcome fishing. It does not "
        "authorize training, deployment, robot access, or GPU use.",
    ]
    Path(args.output_md).write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": report["status"], "registered_scale": registered_scale}))
    return 0


def parse_trace(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("trace must be LABEL=PATH")
    return tuple(value.split("=", 1))  # type: ignore[return-value]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", action="append", type=parse_trace, required=True)
    parser.add_argument("--huber-delta", type=float, default=0.03)
    parser.add_argument("--existing-scale", type=float, default=-0.04)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
