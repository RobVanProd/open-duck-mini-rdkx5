#!/usr/bin/env python3
"""Relabel a failing seed trace with same-tick actions from passing neighbors.

This is an offline data-curation helper for recovery-teacher diagnostics. It
keeps the failing trace observations and metadata, but replaces `action` with
the average action from one or more neighbor traces at the same tick. It does
not train, deploy, SSH, run robot tests, or change runtime behavior.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


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
JOINT_INDEX = {name: idx for idx, name in enumerate(JOINT_NAMES)}


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def parse_joints(text: str) -> list[int]:
    joints: list[int] = []
    for raw in text.split(","):
        token = raw.strip()
        if not token:
            continue
        joints.append(JOINT_INDEX[token] if token in JOINT_INDEX else int(token))
    for joint in joints:
        if joint < 0 or joint >= len(JOINT_NAMES):
            raise ValueError(f"joint index out of range: {joint}")
    return sorted(dict.fromkeys(joints))


def by_tick(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    out = {}
    for row in rows:
        out[int(row.get("tick") or 0)] = row
    return out


def action_vec(row: dict[str, Any]) -> np.ndarray | None:
    action = row.get("action")
    if not isinstance(action, list | tuple) or len(action) != len(JOINT_NAMES):
        return None
    return np.asarray(action, dtype=float)


def average_neighbor_action(neighbor_maps: list[dict[int, dict[str, Any]]], tick: int) -> np.ndarray | None:
    actions = []
    for mapping in neighbor_maps:
        row = mapping.get(tick)
        if row is None:
            continue
        action = action_vec(row)
        if action is not None:
            actions.append(action)
    if not actions:
        return None
    return np.mean(np.stack(actions, axis=0), axis=0)


def cap_delta(
    action: np.ndarray,
    previous: np.ndarray | None,
    joints: list[int],
    max_target_velocity_rad_s: float | None,
    action_scale: float,
    dt_s: float,
) -> tuple[np.ndarray, int]:
    if previous is None or max_target_velocity_rad_s is None or not joints:
        return action, 0
    max_delta = float(max_target_velocity_rad_s) * float(dt_s) / float(action_scale)
    capped = action.copy()
    changed = 0
    for joint in joints:
        delta = float(capped[joint] - previous[joint])
        if abs(delta) > max_delta:
            capped[joint] = previous[joint] + max_delta * (1.0 if delta > 0 else -1.0)
            changed += 1
    return capped, changed


def contact_code(row: dict[str, Any]) -> str:
    contacts = row.get("foot_contacts")
    if isinstance(contacts, list | tuple) and len(contacts) >= 2:
        return f"{int(contacts[0])}{int(contacts[1])}"
    return "NA"


def digest_rows(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            "tick": row.get("tick"),
            "action": row.get("action"),
            "mode": row.get("mode"),
            "source": row.get("recovery_teacher_neighbors"),
        }
        for row in rows
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Seed Recovery Neighbor Relabel",
        "",
        f"status: `{payload['status']}`",
        "",
        "Offline recovery-teacher curation. It keeps failing-seed observations and",
        "uses same-tick neighbor actions as labels. It does not train, deploy, SSH,",
        "run robot tests, or change runtime behavior.",
        "",
        "## Inputs",
        "",
        f"- failing_trace: `{payload['failing_trace']}`",
    ]
    for path in payload["neighbor_traces"]:
        lines.append(f"- neighbor_trace: `{path}`")
    lines.extend(
        [
            "",
            "## Settings",
            "",
            f"- tick_min: `{payload['settings']['tick_min']}`",
            f"- tick_max: `{payload['settings']['tick_max']}`",
            f"- sample_weight: `{payload['settings']['sample_weight']}`",
            f"- max_target_velocity_rad_s: `{payload['settings']['max_target_velocity_rad_s']}`",
            f"- capped_joints: `{payload['settings']['capped_joints']}`",
            "",
            "## Summary",
            "",
            f"- output_trace: `{payload['output_trace']}`",
            f"- dataset_id: `{payload['dataset_id']}`",
            f"- samples_out: `{payload['summary']['samples_out']}`",
            f"- missing_neighbor_ticks: `{payload['summary']['missing_neighbor_ticks']}`",
            f"- capped_action_components: `{payload['summary']['capped_action_components']}`",
            f"- contact_counts: `{payload['summary']['contact_counts']}`",
            "",
            "## Gate",
            "",
            "- Output JSONL is a generated artifact and should remain ignored unless explicitly approved.",
            "- This is source material for offline BC/DAgger diagnostics, not a candidate policy.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--failing-trace", required=True)
    parser.add_argument("--neighbor-trace", action="append", required=True)
    parser.add_argument("--tick-min", type=int, default=0)
    parser.add_argument("--tick-max", type=int, required=True)
    parser.add_argument("--sample-weight", type=float, default=1.0)
    parser.add_argument("--mode", default="seed_recovery_neighbor_relabel")
    parser.add_argument("--output-trace", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--max-target-velocity-rad-s", type=float, default=None)
    parser.add_argument("--capped-joints", default="")
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    args = parser.parse_args()

    failing_path = Path(args.failing_trace)
    neighbor_paths = [Path(item) for item in args.neighbor_trace]
    failing_rows = read_jsonl(failing_path)
    neighbor_maps = [by_tick(read_jsonl(path)) for path in neighbor_paths]
    capped_joints = parse_joints(args.capped_joints) if args.capped_joints else []

    output_rows: list[dict[str, Any]] = []
    missing_neighbor_ticks = 0
    capped_components = 0
    contact_counts: Counter[str] = Counter()
    previous_action: np.ndarray | None = None
    for row in failing_rows:
        tick = int(row.get("tick") or 0)
        if tick < int(args.tick_min) or tick > int(args.tick_max):
            continue
        neighbor_action = average_neighbor_action(neighbor_maps, tick)
        if neighbor_action is None:
            missing_neighbor_ticks += 1
            continue
        neighbor_action, capped = cap_delta(
            neighbor_action,
            previous_action,
            capped_joints,
            args.max_target_velocity_rad_s,
            float(args.action_scale),
            float(args.dt_s),
        )
        capped_components += capped
        copied = dict(row)
        copied["original_action"] = row.get("original_action", row.get("action"))
        copied["pre_recovery_neighbor_action"] = row.get("action")
        copied["action"] = np.clip(neighbor_action, -1.0, 1.0).astype(float).tolist()
        copied["sample_weight"] = float(args.sample_weight)
        copied["sample_weight_reasons"] = sorted(
            set([*copied.get("sample_weight_reasons", []), "seed_recovery_neighbor"])
        )
        copied["mode"] = str(args.mode)
        copied["recovery_teacher_neighbors"] = [str(path) for path in neighbor_paths]
        copied["recovery_teacher_tick"] = tick
        copied["recovery_teacher_capped_components"] = int(capped)
        output_rows.append(copied)
        contact_counts[contact_code(copied)] += 1
        previous_action = neighbor_action

    output_trace = Path(args.output_trace)
    write_jsonl(output_trace, output_rows)
    status = "PASS_SEED_RECOVERY_NEIGHBOR_RELABEL_READY" if output_rows else "HOLD_SEED_RECOVERY_NEIGHBOR_RELABEL_EMPTY"
    payload = {
        "status": status,
        "dataset_id": digest_rows(output_rows),
        "failing_trace": str(failing_path),
        "neighbor_traces": [str(path) for path in neighbor_paths],
        "output_trace": str(output_trace),
        "settings": {
            "tick_min": int(args.tick_min),
            "tick_max": int(args.tick_max),
            "sample_weight": float(args.sample_weight),
            "mode": str(args.mode),
            "max_target_velocity_rad_s": args.max_target_velocity_rad_s,
            "capped_joints": [JOINT_NAMES[idx] for idx in capped_joints],
            "action_scale": float(args.action_scale),
            "dt_s": float(args.dt_s),
        },
        "summary": {
            "samples_out": len(output_rows),
            "missing_neighbor_ticks": missing_neighbor_ticks,
            "capped_action_components": capped_components,
            "contact_counts": dict(sorted(contact_counts.items())),
        },
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text(render_markdown(payload))
    print(status)
    print(f"samples_out={len(output_rows)}")
    print(f"dataset_id={payload['dataset_id']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
