#!/usr/bin/env python3
"""Audit the Open Duck reference-motion data for gait-seeded training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import pickle
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = (
    ROOT.parent
    / "Open_Duck_Playground"
    / "playground"
    / "open_duck_mini_v2"
    / "data"
    / "polynomial_coefficients.pkl"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REFERENCE_MOTION_SEED_AUDIT.md"
DEFAULT_OUTPUT_JSON = (
    ROOT / "outputs" / "analysis" / "reference_motion_seed_audit.json"
)


ACTION_REF_DIMS = {
    "left_hip_yaw": 0,
    "left_hip_roll": 1,
    "left_hip_pitch": 2,
    "left_knee": 3,
    "left_ankle": 4,
    "neck_pitch": 5,
    "head_pitch": 6,
    "head_yaw": 7,
    "head_roll": 8,
    "right_hip_yaw": 11,
    "right_hip_roll": 12,
    "right_hip_pitch": 13,
    "right_knee": 14,
    "right_ankle": 15,
}


def parse_key(key: str) -> tuple[float, float, float]:
    dx, dy, dtheta = key.split("_")
    return float(dx), float(dy), float(dtheta)


def nearest(values: list[float], target: float) -> float:
    return min(values, key=lambda value: abs(value - target))


def sorted_dim_items(coefficients: dict[str, Any]) -> list[tuple[int, Any]]:
    items = []
    for key, value in coefficients.items():
        prefix, index = key.split("_", 1)
        if prefix != "dim":
            continue
        items.append((int(index), value))
    return sorted(items)


def sample_reference(entry: dict[str, Any]) -> np.ndarray:
    period = float(entry["period"])
    fps = float(entry["fps"])
    steps = int(period * fps)
    dims = []
    for _, coeff in sorted_dim_items(entry["coefficients"]):
        # PolyReferenceMotion flips coefficients before jp.polyval.
        dims.append(np.flip(np.asarray(coeff, dtype=float)))
    coeffs = np.asarray(dims, dtype=float)
    samples = []
    for index in range(steps):
        t = np.clip(index % steps / steps, 0.0, 1.0)
        samples.append([np.polyval(coeff, t) for coeff in coeffs])
    return np.asarray(samples, dtype=float)


def stat(values: np.ndarray) -> dict[str, float]:
    return {
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
        "p95_abs": float(np.percentile(np.abs(values), 95)),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Reference Motion Seed Audit",
        "",
        f"status: `{payload['status']}`",
        f"reference_path: `{payload['reference_path']}`",
        f"command: `{payload['requested_command']}`",
        f"nearest_reference_key: `{payload['nearest_reference_key']}`",
        "",
        "## Command Grid",
        "",
        f"- dx_values: `{payload['dx_values']}`",
        f"- dy_values: `{payload['dy_values']}`",
        f"- dtheta_values: `{payload['dtheta_values']}`",
        f"- dx_range: `{payload['dx_range']}`",
        f"- dy_range: `{payload['dy_range']}`",
        f"- dtheta_range: `{payload['dtheta_range']}`",
        "",
        "## Reference Timing",
        "",
        f"- period_s: `{payload['period_s']}`",
        f"- fps: `{payload['fps']}`",
        f"- steps_per_period: `{payload['steps_per_period']}`",
        "",
        "## 14-Action Joint Reference Ranges",
        "",
        "| joint | ref_dim | min | max | mean | p95_abs |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for joint, item in payload["joint_ranges"].items():
        lines.append(
            f"| `{joint}` | {item['ref_dim']} | {item['min']:.4f} | "
            f"{item['max']:.4f} | {item['mean']:.4f} | {item['p95_abs']:.4f} |"
        )
    lines.extend(
        [
            "",
        "## Interpretation",
        "",
            "- The reference-motion data is present and contains the 14 runtime action joints plus two antenna dimensions.",
            "- The active Playground imitation reward compares leg joint pose/velocity, base velocity, base angular velocity, and foot contacts; head/neck and antenna dimensions are present in the reference but are not the leg-imitation error term.",
            "- The lowest positive reference `dx` is above the `x=0.04` low-command gate, so V19 uses a slightly faster gait shape as a reference-motion reward while grading command tracking at `x=0.04`.",
            "- If the reference-imitation policy still degrades into standstill/reverse, the reward/task landscape should be debugged against this reference path rather than continuing cold-start reward tuning.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--command-y", type=float, default=0.0)
    parser.add_argument("--command-yaw", type=float, default=0.0)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    with args.reference.open("rb") as handle:
        data = pickle.load(handle)
    parsed = {key: parse_key(key) for key in data}
    dx_values = sorted({value[0] for value in parsed.values()})
    dy_values = sorted({value[1] for value in parsed.values()})
    dtheta_values = sorted({value[2] for value in parsed.values()})
    ref_dx = nearest(dx_values, args.command_x)
    ref_dy = nearest(dy_values, args.command_y)
    ref_dtheta = nearest(dtheta_values, args.command_yaw)
    nearest_key = min(
        data,
        key=lambda key: (
            (parsed[key][0] - ref_dx) ** 2
            + (parsed[key][1] - ref_dy) ** 2
            + (parsed[key][2] - ref_dtheta) ** 2
        ),
    )
    entry = data[nearest_key]
    samples = sample_reference(entry)
    joint_ranges = {}
    for joint, dim in ACTION_REF_DIMS.items():
        joint_ranges[joint] = {"ref_dim": dim, **stat(samples[:, dim])}
    payload = {
        "status": "PASS_REFERENCE_MOTION_AVAILABLE",
        "reference_path": str(args.reference),
        "requested_command": {
            "x": args.command_x,
            "y": args.command_y,
            "yaw": args.command_yaw,
        },
        "nearest_reference_key": nearest_key,
        "nearest_reference_command": {
            "x": parsed[nearest_key][0],
            "y": parsed[nearest_key][1],
            "yaw": parsed[nearest_key][2],
        },
        "dx_values": dx_values,
        "dy_values": dy_values,
        "dtheta_values": dtheta_values,
        "dx_range": [min(dx_values), max(dx_values)],
        "dy_range": [min(dy_values), max(dy_values)],
        "dtheta_range": [min(dtheta_values), max(dtheta_values)],
        "period_s": float(entry["period"]),
        "fps": float(entry["fps"]),
        "steps_per_period": int(float(entry["period"]) * float(entry["fps"])),
        "joint_ranges": joint_ranges,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(build_markdown(payload))
    print(payload["status"])
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
