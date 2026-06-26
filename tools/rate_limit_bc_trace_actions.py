#!/usr/bin/env python3
"""Rate-limit selected action dimensions in BC JSONL traces.

This is an offline dataset-curation helper. It rewrites ignored trace JSONL
files so selected `action` dimensions obey a per-tick target-rate envelope,
preserving the original action in `original_action`. It does not train, SSH,
deploy, run robot tests, or change runtime behavior.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "BC_TRACE_ACTION_RATE_LIMIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "bc_trace_action_rate_limit.json"

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


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def parse_joints(value: str) -> list[int]:
    joints = []
    name_to_index = {name: idx for idx, name in enumerate(JOINT_NAMES)}
    for raw in value.split(","):
        item = raw.strip()
        if not item:
            continue
        if item in name_to_index:
            joints.append(name_to_index[item])
            continue
        joints.append(int(item))
    for idx in joints:
        if idx < 0 or idx >= len(JOINT_NAMES):
            raise ValueError(f"joint index out of range: {idx}")
    return sorted(dict.fromkeys(joints))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def contact_key(row: dict[str, Any]) -> str:
    contacts = row.get("foot_contacts") or []
    if not isinstance(contacts, list) or len(contacts) < 2:
        return "NA"
    return "".join(str(int(value)) for value in contacts[:2])


def vector(row: dict[str, Any], key: str) -> np.ndarray | None:
    value = row.get(key)
    if not isinstance(value, list) or len(value) != len(JOINT_NAMES):
        return None
    return np.asarray(value, dtype=float)


def process_trace(
    path: Path,
    output_dir: Path,
    *,
    joint_indices: list[int],
    max_action_delta: float,
    action_scale: float,
    dt_s: float,
    output_mode: str,
) -> dict[str, Any]:
    rows = read_jsonl(path)
    output_rows: list[dict[str, Any]] = []
    changed_counts = Counter()
    contacts_for_changed = Counter()
    original_velocities: dict[int, list[float]] = {idx: [] for idx in joint_indices}
    limited_velocities: dict[int, list[float]] = {idx: [] for idx in joint_indices}
    action_delta_removed: dict[int, list[float]] = {idx: [] for idx in joint_indices}
    previous_original: np.ndarray | None = None
    previous_limited: np.ndarray | None = None

    for row in rows:
        action = vector(row, "action")
        if action is None:
            continue
        limited = action.copy()
        if previous_limited is not None:
            for idx in joint_indices:
                delta = float(limited[idx] - previous_limited[idx])
                clipped_delta = float(np.clip(delta, -max_action_delta, max_action_delta))
                if abs(clipped_delta - delta) > 1.0e-12:
                    changed_counts[JOINT_NAMES[idx]] += 1
                    contacts_for_changed[contact_key(row)] += 1
                    limited[idx] = previous_limited[idx] + clipped_delta
                    action_delta_removed[idx].append(abs(delta) - abs(clipped_delta))
                else:
                    action_delta_removed[idx].append(0.0)

        if previous_original is not None:
            for idx in joint_indices:
                original_velocities[idx].append(
                    abs(float(action[idx] - previous_original[idx])) * action_scale / dt_s
                )
        if previous_limited is not None:
            for idx in joint_indices:
                limited_velocities[idx].append(
                    abs(float(limited[idx] - previous_limited[idx])) * action_scale / dt_s
                )

        new_row = dict(row)
        original_action = row.get("original_action", row.get("action"))
        new_row["original_action"] = original_action
        new_row["pre_rate_limit_action"] = row.get("action")
        new_row["action"] = limited.astype(float).tolist()
        new_row["rate_limit_action_joints"] = [JOINT_NAMES[idx] for idx in joint_indices]
        new_row["rate_limit_action_max_delta"] = float(max_action_delta)
        new_row["mode"] = output_mode

        # Keep target_pre_rate_limit_rad coherent for diagnostics when possible.
        pre = vector(row, "target_pre_rate_limit_rad")
        if pre is not None:
            original = action
            adjusted = pre.copy()
            for idx in joint_indices:
                # target = home + action * scale, so preserve inferred home.
                home = pre[idx] - original[idx] * action_scale
                adjusted[idx] = home + limited[idx] * action_scale
            new_row["target_pre_rate_limit_rad"] = adjusted.astype(float).tolist()

        output_rows.append(new_row)
        previous_original = action
        previous_limited = limited

    output_path = output_dir / path.name
    write_jsonl(output_path, output_rows)

    per_joint = {}
    for idx in joint_indices:
        name = JOINT_NAMES[idx]
        per_joint[name] = {
            "changed_ticks": int(changed_counts[name]),
            "original_target_velocity_p95_rad_s": percentile(original_velocities[idx], 95),
            "original_target_velocity_max_rad_s": max(original_velocities[idx])
            if original_velocities[idx]
            else None,
            "limited_target_velocity_p95_rad_s": percentile(limited_velocities[idx], 95),
            "limited_target_velocity_max_rad_s": max(limited_velocities[idx])
            if limited_velocities[idx]
            else None,
            "action_delta_removed_p95": percentile(action_delta_removed[idx], 95),
            "action_delta_removed_max": max(action_delta_removed[idx])
            if action_delta_removed[idx]
            else None,
        }

    return {
        "source_trace": str(path),
        "output_trace": str(output_path),
        "samples_in": len(rows),
        "samples_out": len(output_rows),
        "changed_ticks": int(sum(changed_counts.values())),
        "changed_contact_counts": dict(sorted(contacts_for_changed.items())),
        "per_joint": per_joint,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# BC Trace Action Rate Limit",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.",
        "",
        "## Settings",
        "",
        f"- trace_globs: `{payload['trace_globs']}`",
        f"- output_trace_dir: `{payload['output_trace_dir']}`",
        f"- joints: `{payload['settings']['joints']}`",
        f"- max_target_velocity_rad_s: `{payload['settings']['max_target_velocity_rad_s']}`",
        f"- action_scale: `{payload['settings']['action_scale']}`",
        f"- dt_s: `{payload['settings']['dt_s']}`",
        f"- max_action_delta: `{fmt(payload['settings']['max_action_delta'], 6)}`",
        "",
        "## Summary",
        "",
        f"- traces: `{payload['summary']['traces']}`",
        f"- samples_out: `{payload['summary']['samples_out']}`",
        f"- changed_ticks: `{payload['summary']['changed_ticks']}`",
        f"- changed_contact_counts: `{payload['summary']['changed_contact_counts']}`",
        "",
        "| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["traces"]:
        for joint, row in item["per_joint"].items():
            lines.append(
                "| {source} | {samples} | {changed} | `{joint}` | {orig95} | {origmax} | {lim95} | {limmax} | {rem95} | {remmax} |".format(
                    source=Path(item["source_trace"]).name,
                    samples=item["samples_out"],
                    changed=row["changed_ticks"],
                    joint=joint,
                    orig95=fmt(row.get("original_target_velocity_p95_rad_s")),
                    origmax=fmt(row.get("original_target_velocity_max_rad_s")),
                    lim95=fmt(row.get("limited_target_velocity_p95_rad_s")),
                    limmax=fmt(row.get("limited_target_velocity_max_rad_s")),
                    rem95=fmt(row.get("action_delta_removed_p95")),
                    remmax=fmt(row.get("action_delta_removed_max")),
                )
            )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- Raw output JSONL traces remain ignored unless explicitly force-added.",
            "- This only edits offline training/eval traces; it is not a runtime smoother.",
            "- Any student trained from these traces still requires closed-loop multi-seed gates.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", required=True)
    parser.add_argument("--output-trace-dir", required=True)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--joints", default="right_knee")
    parser.add_argument("--max-target-velocity-rad-s", type=float, default=3.75)
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--output-mode", default="action_rate_limited_trace")
    args = parser.parse_args()

    joint_indices = parse_joints(args.joints)
    max_action_delta = (
        float(args.max_target_velocity_rad_s) * float(args.dt_s) / float(args.action_scale)
    )
    paths: list[Path] = []
    for item in args.trace_glob:
        paths.extend(Path(path) for path in sorted(glob.glob(item)))
    paths = sorted(dict.fromkeys(paths))
    output_dir = Path(args.output_trace_dir)
    traces = [
        process_trace(
            path,
            output_dir,
            joint_indices=joint_indices,
            max_action_delta=max_action_delta,
            action_scale=float(args.action_scale),
            dt_s=float(args.dt_s),
            output_mode=str(args.output_mode),
        )
        for path in paths
    ]
    status = (
        "PASS_BC_TRACE_ACTION_RATE_LIMIT_READY"
        if traces and all(row["samples_out"] for row in traces)
        else "HOLD_BC_TRACE_ACTION_RATE_LIMIT_EMPTY"
    )
    changed_contact_counts = Counter()
    for row in traces:
        changed_contact_counts.update(row.get("changed_contact_counts") or {})
    payload = {
        "status": status,
        "trace_globs": args.trace_glob,
        "output_trace_dir": str(output_dir),
        "settings": {
            "joints": [JOINT_NAMES[idx] for idx in joint_indices],
            "max_target_velocity_rad_s": float(args.max_target_velocity_rad_s),
            "action_scale": float(args.action_scale),
            "dt_s": float(args.dt_s),
            "max_action_delta": max_action_delta,
            "output_mode": str(args.output_mode),
        },
        "summary": {
            "traces": len(traces),
            "samples_out": int(sum(row["samples_out"] for row in traces)),
            "changed_ticks": int(sum(row["changed_ticks"] for row in traces)),
            "changed_contact_counts": dict(sorted(changed_contact_counts.items())),
        },
        "traces": traces,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"traces={len(traces)}")
    print(f"samples_out={payload['summary']['samples_out']}")
    print(f"changed_ticks={payload['summary']['changed_ticks']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
