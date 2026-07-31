#!/usr/bin/env python3
"""Quantify yaw dependence in the upstream imitation velocity comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import pickle

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = ROOT.parent / "Open_Duck_Playground/playground/open_duck_mini_v2/data/polynomial_coefficients.pkl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reference_horizontal_velocity(path: Path, command_x: float) -> np.ndarray:
    data = pickle.loads(path.read_bytes())
    keys = []
    for key in data:
        dx, dy, dtheta = (float(value) for value in key.split("_"))
        keys.append((abs(dx - command_x) + abs(dy) + abs(dtheta), key))
    selected = data[min(keys)[1]]
    period = float(selected["period"])
    fps = float(selected["fps"])
    count = int(period * fps)
    coefficients = [np.flip(np.asarray(value, dtype=np.float64)) for value in selected["coefficients"].values()]
    samples = np.asarray([
        [np.polyval(coef, index / count) for coef in coefficients]
        for index in range(count)
    ])
    return samples[:, 34:36].mean(axis=0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", default=str(DEFAULT_REFERENCE))
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--tracking-sigma", type=float, default=0.25)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    reference = Path(args.reference).resolve()
    ref_local = reference_horizontal_velocity(reference, args.command_x)
    rows = []
    for yaw in np.linspace(-np.pi, np.pi, 9):
        rotation = np.asarray([
            [np.cos(yaw), -np.sin(yaw)],
            [np.sin(yaw), np.cos(yaw)],
        ])
        perfect_world = rotation @ ref_local
        upstream_error = float(np.sum(np.square(perfect_world - ref_local)))
        rows.append({
            "yaw_rad": float(yaw),
            "perfect_local_velocity_xy": ref_local.tolist(),
            "corresponding_world_velocity_xy": perfect_world.tolist(),
            "upstream_global_frame_squared_error": upstream_error,
            "upstream_imitation_velocity_reward": float(np.exp(-8.0 * upstream_error)),
            "corrected_local_frame_squared_error": 0.0,
            "corrected_imitation_velocity_reward": 1.0,
        })

    payload = {
        "schema_version": "ground_up_reference_velocity_frame_audit.v1",
        "status": "FAIL_UPSTREAM_IMITATION_VELOCITY_NOT_YAW_INVARIANT",
        "reference": str(reference),
        "reference_sha256": sha256(reference),
        "nearest_reference_mean_velocity_xy": ref_local.tolist(),
        "reset_yaw_range_rad": [-3.14, 3.14],
        "source_evidence": {
            "reset": "joystick.py samples yaw uniformly from -3.14 to 3.14",
            "command_tracking": "reward_tracking_lin_vel receives get_local_linvel(data)",
            "imitation": "reward_imitation receives free-base qvel and compares qvel[:2] directly with reference[:2]",
        },
        "max_upstream_squared_error_for_perfect_local_tracking": max(row["upstream_global_frame_squared_error"] for row in rows),
        "min_upstream_reward_for_perfect_local_tracking": min(row["upstream_imitation_velocity_reward"] for row in rows),
        "yaw_samples": rows,
        "required_fix": "pass body-local linear velocity to imitation reward so command and reference objectives share a frame",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("status", "max_upstream_squared_error_for_perfect_local_tracking", "min_upstream_reward_for_perfect_local_tracking")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
