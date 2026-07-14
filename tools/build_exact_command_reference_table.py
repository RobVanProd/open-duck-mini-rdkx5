#!/usr/bin/env python3
"""Build exact-command rows by trilinear interpolation of a reference table."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bracket(values: np.ndarray, target: float) -> tuple[float, float, float]:
    if target < values[0] or target > values[-1]:
        raise ValueError(f"target {target} outside [{values[0]}, {values[-1]}]")
    lower = float(values[values <= target][-1])
    upper = float(values[values >= target][0])
    weight = 0.0 if upper == lower else (target - lower) / (upper - lower)
    return lower, upper, float(weight)


def interpolate(commands: np.ndarray, actions: np.ndarray, target: np.ndarray):
    axes = [np.unique(commands[:, axis]) for axis in range(3)]
    brackets = [bracket(values, float(target[axis])) for axis, values in enumerate(axes)]
    total = np.zeros_like(actions[0], dtype=np.float64)
    sources = []
    for x in (0, 1):
        for y in (0, 1):
            for yaw in (0, 1):
                bits = (x, y, yaw)
                point = np.array([brackets[i][bits[i]] for i in range(3)], dtype=np.float32)
                weight = float(np.prod([
                    brackets[i][2] if bits[i] else 1.0 - brackets[i][2]
                    for i in range(3)
                ]))
                if weight == 0.0:
                    continue
                matches = np.flatnonzero(np.all(np.isclose(commands, point), axis=1))
                if len(matches) != 1:
                    raise ValueError(f"expected one source row for {point}, found {matches}")
                row = int(matches[0])
                total += actions[row].astype(np.float64) * weight
                sources.append({
                    "row": row,
                    "command": commands[row].astype(float).tolist(),
                    "weight": weight,
                })
    if abs(sum(item["weight"] for item in sources) - 1.0) > 1.0e-6:
        raise AssertionError("interpolation weights do not sum to one")
    return total.astype(np.float32), brackets, sources


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--command-x", default="0.074,0.08")
    args = parser.parse_args()

    source = np.load(args.input)
    commands = np.asarray(source["commands"], dtype=np.float32)
    actions = np.asarray(source["actions"], dtype=np.float32)
    expected_rows = int(np.prod([len(np.unique(commands[:, axis])) for axis in range(3)]))
    if expected_rows != len(commands) or actions.shape != (len(commands), 27, 14):
        raise ValueError("input table is not the expected full Cartesian 240x27x14 grid")

    output_commands = []
    output_actions = []
    rows = []
    for command_x in [float(value) for value in args.command_x.split(",")]:
        target = np.array([command_x, 0.0, 0.0], dtype=np.float32)
        action, brackets, sources = interpolate(commands, actions, target)
        nearest_row = int(np.argmin(np.sum(np.abs(commands - target), axis=1)))
        nearest = actions[nearest_row]
        output_commands.append(target)
        output_actions.append(action)
        rows.append({
            "target": target.astype(float).tolist(),
            "brackets": [list(map(float, item)) for item in brackets],
            "sources": sources,
            "nearest_row": nearest_row,
            "nearest_command": commands[nearest_row].astype(float).tolist(),
            "interpolated_vs_nearest_max_abs_action": float(np.max(np.abs(action - nearest))),
            "interpolated_vs_nearest_rms_action": float(np.sqrt(np.mean(np.square(action - nearest)))),
        })

    output_commands.append(np.zeros(3, dtype=np.float32))
    output_actions.append(np.zeros((27, 14), dtype=np.float32))
    out_actions = np.asarray(output_actions, dtype=np.float32)
    action_scale = float(source["action_scale_rad"])
    dt_s = float(source["dt_s"])
    max_rate = np.max(np.abs(np.diff(
        np.concatenate([out_actions[:, -1:, :], out_actions], axis=1), axis=1
    )), axis=(0, 1)) * action_scale / dt_s
    limits = np.asarray(source["velocity_limits_rad_s"], dtype=np.float32)
    if float(np.max(np.abs(out_actions))) > 1.000001 or np.any(max_rate > limits + 1.0e-5):
        raise AssertionError("interpolation violated action or velocity envelope")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        commands=np.asarray(output_commands, dtype=np.float32),
        actions=out_actions,
        action_scale_rad=source["action_scale_rad"],
        dt_s=source["dt_s"],
        home_rad=source["home_rad"],
        velocity_limits_rad_s=source["velocity_limits_rad_s"],
    )
    payload = {
        "schema_version": "ground_up_exact_command_reference_table.v1",
        "status": "PASS_EXACT_COMMAND_INTERPOLATION_CONTRACT",
        "input": str(args.input),
        "input_sha256": sha256(args.input),
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "output_shape": list(out_actions.shape),
        "output_commands": np.asarray(output_commands).astype(float).tolist(),
        "max_abs_action": float(np.max(np.abs(out_actions))),
        "max_rate_by_joint_rad_s": max_rate.astype(float).tolist(),
        "velocity_limits_rad_s": limits.astype(float).tolist(),
        "rows": rows,
        "robot_access": False,
        "local_gpu_access": False,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
