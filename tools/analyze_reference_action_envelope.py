#!/usr/bin/env python3
"""Analyze a polynomial reference motion against the Open Duck action contract."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_REFERENCE = ROOT / "outputs" / "analysis" / "reference_motion_x004_override.pkl"
DEFAULT_XML = (
    DEFAULT_PLAYGROUND
    / "playground"
    / "open_duck_mini_v2"
    / "xmls"
    / "scene_flat_terrain.xml"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REFERENCE_ACTION_ENVELOPE_V20.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "reference_action_envelope_v20.json"
JOINT_NAMES = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def percentile(values: np.ndarray, pct: float) -> float | None:
    data = np.asarray(values, dtype=float)
    data = data[np.isfinite(data)]
    if data.size == 0:
        return None
    return float(np.percentile(data, pct))


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float) and not math.isfinite(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def reference_to_target(reference_frame: np.ndarray, home: np.ndarray) -> np.ndarray:
    """Map 16-reference joint positions into the 14-action runtime order."""

    target = np.array(home, dtype=float).copy()
    target[:5] = reference_frame[:5]
    target[9:14] = reference_frame[11:16]
    return target


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    import sys

    import mujoco

    playground = Path(args.playground_path).resolve()
    if str(playground) not in sys.path:
        sys.path.insert(0, str(playground))
    from playground.common.poly_reference_motion_numpy import PolyReferenceMotion

    reference_path = Path(args.reference_motion).resolve()
    xml_path = Path(args.xml).resolve()
    model = mujoco.MjModel.from_xml_path(str(xml_path))
    home = np.asarray(model.keyframe("home").ctrl, dtype=float)
    prm = PolyReferenceMotion(str(reference_path))
    period_steps = int(prm.nb_steps_in_period)
    targets = np.asarray(
        [
            reference_to_target(
                np.asarray(
                    prm.get_reference_motion(
                        args.command_x,
                        args.command_y,
                        args.command_yaw,
                        phase,
                    ),
                    dtype=float,
                ),
                home,
            )
            for phase in range(period_steps)
        ],
        dtype=float,
    )
    actions = (targets - home) / float(args.action_scale)
    action_saturation = np.abs(actions) >= float(args.action_saturation_threshold)
    target_velocity = np.abs(
        np.diff(np.vstack([targets, targets[:1]]), axis=0) / float(args.dt_s)
    )
    home_distance = np.linalg.norm(targets - home, axis=1)
    closest_phases = [
        {
            "phase": int(index),
            "home_distance_rad": float(home_distance[index]),
            "saturated_joint_count": int(action_saturation[index].sum()),
            "max_abs_action": float(np.max(np.abs(actions[index]))),
        }
        for index in np.argsort(home_distance)[: args.closest_phases]
    ]
    per_joint = []
    for index, name in enumerate(JOINT_NAMES):
        per_joint.append(
            {
                "joint": name,
                "max_abs_action": float(np.max(np.abs(actions[:, index]))),
                "action_saturation_pct": float(np.mean(action_saturation[:, index]) * 100.0),
                "target_velocity_p95_rad_s": percentile(target_velocity[:, index], 95),
                "target_velocity_max_rad_s": float(np.max(target_velocity[:, index])),
                "exceeds_action_scale": bool(np.max(np.abs(actions[:, index])) >= args.action_saturation_threshold),
                "exceeds_velocity_budget": bool(
                    np.max(target_velocity[:, index]) > args.max_motor_velocity_rad_s
                ),
            }
        )
    stressed = [
        row["joint"]
        for row in per_joint
        if row["exceeds_action_scale"] or row["exceeds_velocity_budget"]
    ]
    status = "PASS_REFERENCE_WITHIN_ACTION_ENVELOPE"
    if stressed:
        status = "HOLD_REFERENCE_EXCEEDS_ACTION_ENVELOPE"
    return {
        "status": status,
        "reference_motion": str(reference_path),
        "reference_sha256": sha256(reference_path),
        "xml": str(xml_path),
        "command": {
            "x": args.command_x,
            "y": args.command_y,
            "yaw": args.command_yaw,
        },
        "period_steps": period_steps,
        "dt_s": args.dt_s,
        "action_scale": args.action_scale,
        "max_motor_velocity_rad_s": args.max_motor_velocity_rad_s,
        "closest_phases_to_home": closest_phases,
        "stressed_joints": stressed,
        "per_joint": per_joint,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Reference Action Envelope",
        "",
        f"status: `{payload['status']}`",
        f"reference: `{payload['reference_motion']}`",
        f"reference_sha256: `{payload['reference_sha256']}`",
        f"command: `{payload['command']}`",
        f"period_steps: `{payload['period_steps']}`",
        f"action_scale: `{payload['action_scale']}`",
        f"max_motor_velocity_rad_s: `{payload['max_motor_velocity_rad_s']}`",
        "",
        "## Closest Phases To Home",
        "",
        "| phase | home_distance_rad | saturated_joint_count | max_abs_action |",
        "|---:|---:|---:|---:|",
    ]
    for row in payload["closest_phases_to_home"]:
        lines.append(
            f"| {row['phase']} | {fmt(row['home_distance_rad'])} | "
            f"{row['saturated_joint_count']} | {fmt(row['max_abs_action'])} |"
        )
    lines.extend(
        [
            "",
            "## Per Joint",
            "",
            "| joint | max_abs_action | action_sat_pct | target_vel_p95 | target_vel_max |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in payload["per_joint"]:
        lines.append(
            "| {joint} | {max_action} | {sat} | {vel95} | {velmax} |".format(
                joint=row["joint"],
                max_action=fmt(row["max_abs_action"]),
                sat=fmt(row["action_saturation_pct"]),
                vel95=fmt(row["target_velocity_p95_rad_s"]),
                velmax=fmt(row["target_velocity_max_rad_s"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a kinematic/action-contract audit, not a sim rollout.",
            "- `max_abs_action > 1` means the raw reference target exceeds `home + action * action_scale`.",
            "- Target velocity above `max_motor_velocity_rad_s` means the target cannot be followed without slew limiting.",
            "- If this holds, behavior cloning from raw reference joint positions would train against an out-of-envelope target.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--reference-motion", default=str(DEFAULT_REFERENCE))
    parser.add_argument("--xml", default=str(DEFAULT_XML))
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--command-y", type=float, default=0.0)
    parser.add_argument("--command-yaw", type=float, default=0.0)
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--max-motor-velocity-rad-s", type=float, default=5.24)
    parser.add_argument("--action-saturation-threshold", type=float, default=0.999)
    parser.add_argument("--closest-phases", type=int, default=8)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = analyze(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
