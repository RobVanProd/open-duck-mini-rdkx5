#!/usr/bin/env python3
"""Build a reference-motion pickle override for a cleaner low-speed command."""

from __future__ import annotations

import argparse
import copy
import hashlib
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
DEFAULT_OUTPUT_PKL = ROOT / "outputs" / "analysis" / "reference_motion_x004_override.pkl"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REFERENCE_MOTION_OVERRIDE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "reference_motion_override.json"


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


def source_specs(
    data: dict[str, Any], command_x: float, command_yaw: float
) -> list[tuple[str, float]]:
    parsed = {key: parse_key(key) for key in data}
    dx_values = sorted_values({value[0] for value in parsed.values()})
    dy_values = sorted_values({value[1] for value in parsed.values()})
    yaw_values = sorted_values({value[2] for value in parsed.values()})
    dx_lo, dx_hi = bracket(dx_values, command_x)
    yaw = nearest(yaw_values, command_yaw)
    dy_abs = min(abs(value) for value in dy_values)
    if dx_hi == dx_lo:
        high_weight = 0.0
    else:
        high_weight = (command_x - dx_lo) / (dx_hi - dx_lo)
    low_weight = 1.0 - high_weight
    specs = [
        (key_for(dx_lo, -dy_abs, yaw), low_weight * 0.5),
        (key_for(dx_lo, dy_abs, yaw), low_weight * 0.5),
        (key_for(dx_hi, -dy_abs, yaw), high_weight * 0.5),
        (key_for(dx_hi, dy_abs, yaw), high_weight * 0.5),
    ]
    missing = [key for key, _ in specs if key not in data]
    if missing:
        raise SystemExit(f"Missing source keys: {missing}")
    return specs


def selected_key_for_command(
    data: dict[str, Any], command_x: float, command_y: float, command_yaw: float
) -> str:
    parsed = {key: parse_key(key) for key in data}
    dx_values = sorted_values({value[0] for value in parsed.values()})
    dy_values = sorted_values({value[1] for value in parsed.values()})
    yaw_values = sorted_values({value[2] for value in parsed.values()})
    dx = nearest(dx_values, command_x)
    dy = nearest(dy_values, command_y)
    yaw = nearest(yaw_values, command_yaw)
    key = key_for(dx, dy, yaw)
    if key not in data:
        raise SystemExit(f"Selected key is missing from reference grid: {key}")
    return key


def synthesize_coefficients(
    data: dict[str, Any], specs: list[tuple[str, float]]
) -> dict[str, list[float]]:
    # PolyReferenceMotion preserves pickle insertion order when it builds the
    # coefficient array. Keep that order here; lexicographic sorting would put
    # dim_10 before dim_2 and corrupt the reference dimensions.
    coeff_keys = list(data[specs[0][0]]["coefficients"])
    synthesized = {}
    for coeff_key in coeff_keys:
        acc = None
        for source_key, weight in specs:
            values = np.asarray(data[source_key]["coefficients"][coeff_key], dtype=float)
            acc = values * weight if acc is None else acc + values * weight
        assert acc is not None
        synthesized[coeff_key] = [float(value) for value in acc]
    return synthesized


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Reference Motion Override",
        "",
        f"status: `{payload['status']}`",
        f"source_reference: `{payload['source_reference']}`",
        f"output_pickle: `{payload['output_pickle']}`",
        f"output_sha256: `{payload['output_sha256']}`",
        "",
        "## Override",
        "",
        f"- replaced_key: `{payload['replaced_key']}`",
        f"- command_for_lookup: `{payload['command_for_lookup']}`",
        "",
        "## Source Mix",
        "",
    ]
    for item in payload["source_keys"]:
        lines.append(f"- `{item['key']}` weight `{item['weight']:.4f}`")
    lines.extend(
        [
            "",
            "## Synthesized Base Velocity",
            "",
            "| signal | min | max | mean | p95_abs |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for name, item in payload["synthesized_base_velocity"].items():
        lines.append(
            f"| `{name}` | {item['min']:.4f} | {item['max']:.4f} | "
            f"{item['mean']:.4f} | {item['p95_abs']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The override preserves the original reference-grid shape by replacing the nearest key that the current environment already selects for `x=0.04,y=0,yaw=0`.",
            "- This avoids changing `PolyReferenceMotion` before we know whether a command-matched reference helps.",
            "- Do not deploy this to the robot. It is a training-only artifact for a possible V20 experiment.",
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
    parser.add_argument("--output-pkl", type=Path, default=DEFAULT_OUTPUT_PKL)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    with args.reference.open("rb") as handle:
        data = pickle.load(handle)
    replaced_key = selected_key_for_command(
        data, args.command_x, args.command_y, args.command_yaw
    )
    specs = source_specs(data, args.command_x, args.command_yaw)
    override = copy.deepcopy(data)
    override[replaced_key]["coefficients"] = synthesize_coefficients(data, specs)
    samples = sample_entry(override[replaced_key])
    args.output_pkl.parent.mkdir(parents=True, exist_ok=True)
    with args.output_pkl.open("wb") as handle:
        pickle.dump(override, handle)
    payload = {
        "status": "PASS_REFERENCE_OVERRIDE_BUILT",
        "source_reference": str(args.reference),
        "output_pickle": str(args.output_pkl),
        "output_sha256": sha256(args.output_pkl),
        "output_size_bytes": args.output_pkl.stat().st_size,
        "replaced_key": replaced_key,
        "command_for_lookup": {
            "x": args.command_x,
            "y": args.command_y,
            "yaw": args.command_yaw,
        },
        "source_keys": [{"key": key, "weight": weight} for key, weight in specs],
        "synthesized_base_velocity": velocity_summary(samples),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(build_markdown(payload))
    print(payload["status"])
    print(f"Wrote {args.output_pkl}")
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
