#!/usr/bin/env python3
"""Analyze whether the reference grid can synthesize a straight low-speed gait."""

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
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REFERENCE_GRID_INTERPOLATION.md"
DEFAULT_OUTPUT_JSON = (
    ROOT / "outputs" / "analysis" / "reference_grid_interpolation.json"
)


def parse_key(key: str) -> tuple[float, float, float]:
    dx, dy, dtheta = key.split("_")
    return float(dx), float(dy), float(dtheta)


def key_for(dx: float, dy: float, dtheta: float) -> str:
    return f"{dx}_{dy}_{dtheta}"


def sorted_values(values: set[float]) -> list[float]:
    return sorted(values)


def nearest(values: list[float], target: float) -> float:
    return min(values, key=lambda value: abs(value - target))


def bracket(values: list[float], target: float) -> tuple[float, float]:
    lower = max((value for value in values if value <= target), default=values[0])
    upper = min((value for value in values if value >= target), default=values[-1])
    return lower, upper


def sample_entry(entry: dict[str, Any]) -> np.ndarray:
    steps = int(float(entry["period"]) * float(entry["fps"]))
    dims = []
    for key, value in entry["coefficients"].items():
        prefix, index = key.split("_", 1)
        if prefix == "dim":
            dims.append((int(index), np.flip(np.asarray(value, dtype=float))))
    coeffs = np.asarray([value for _, value in sorted(dims)], dtype=float)
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


def velocity_summary(samples: np.ndarray) -> dict[str, dict[str, float]]:
    return {
        "linvel_x": stat(samples[:, 34]),
        "linvel_y": stat(samples[:, 35]),
        "linvel_z": stat(samples[:, 36]),
        "angvel_x": stat(samples[:, 37]),
        "angvel_y": stat(samples[:, 38]),
        "angvel_z": stat(samples[:, 39]),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Reference Grid Interpolation",
        "",
        f"status: `{payload['status']}`",
        f"reference_path: `{payload['reference_path']}`",
        f"target_command: `{payload['target_command']}`",
        "",
        "## Source Keys",
        "",
    ]
    for item in payload["source_keys"]:
        lines.append(
            f"- `{item['key']}` command `{item['command']}` weight `{item['weight']:.4f}`"
        )
    lines.extend(
        [
            "",
            "## Composite Base Velocity",
            "",
            "| signal | min | max | mean | p95_abs |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for name, item in payload["composite_base_velocity"].items():
        lines.append(
            f"| `{name}` | {item['min']:.4f} | {item['max']:.4f} | "
            f"{item['mean']:.4f} | {item['p95_abs']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The reference grid has no exact `y=0` entry, but it has symmetric positive/negative lateral entries.",
            "- Averaging the two nearest lateral references cancels most mean lateral velocity.",
            "- Interpolating between the nearest lower/upper `dx` rows can synthesize a lower-speed reference closer to the `x=0.04` gate than the raw nearest key.",
            "- This is an offline analysis only; training would need explicit support for using a synthesized reference artifact before launching V20.",
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
    dx_values = sorted_values({value[0] for value in parsed.values()})
    dy_values = sorted_values({value[1] for value in parsed.values()})
    yaw_values = sorted_values({value[2] for value in parsed.values()})

    dx_lo, dx_hi = bracket(dx_values, args.command_x)
    yaw = nearest(yaw_values, args.command_yaw)
    dy_abs = min(abs(value) for value in dy_values)
    dy_pair = (-dy_abs, dy_abs)
    if dx_hi == dx_lo:
        high_weight = 0.0
    else:
        high_weight = (args.command_x - dx_lo) / (dx_hi - dx_lo)
    low_weight = 1.0 - high_weight

    source_specs = [
        (dx_lo, dy_pair[0], yaw, low_weight * 0.5),
        (dx_lo, dy_pair[1], yaw, low_weight * 0.5),
        (dx_hi, dy_pair[0], yaw, high_weight * 0.5),
        (dx_hi, dy_pair[1], yaw, high_weight * 0.5),
    ]
    composite = None
    source_keys = []
    for dx, dy, dtheta, weight in source_specs:
        key = key_for(dx, dy, dtheta)
        if key not in data:
            raise SystemExit(f"Missing expected reference key: {key}")
        samples = sample_entry(data[key])
        composite = samples * weight if composite is None else composite + samples * weight
        source_keys.append(
            {
                "key": key,
                "command": {"x": dx, "y": dy, "yaw": dtheta},
                "weight": weight,
            }
        )

    assert composite is not None
    velocity = velocity_summary(composite)
    payload = {
        "status": "PASS_INTERPOLATED_REFERENCE_PROPOSAL",
        "reference_path": str(args.reference),
        "target_command": {
            "x": args.command_x,
            "y": args.command_y,
            "yaw": args.command_yaw,
        },
        "dx_bracket": [dx_lo, dx_hi],
        "dy_pair": list(dy_pair),
        "yaw_reference": yaw,
        "source_keys": source_keys,
        "composite_base_velocity": velocity,
        "mean_velocity_error": {
            "x": velocity["linvel_x"]["mean"] - args.command_x,
            "y": velocity["linvel_y"]["mean"] - args.command_y,
            "yaw": velocity["angvel_z"]["mean"] - args.command_yaw,
        },
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
