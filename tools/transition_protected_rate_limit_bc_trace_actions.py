#!/usr/bin/env python3
"""Rate-limit BC trace actions while protecting support transitions.

This is an offline dataset-curation helper. It rewrites ignored trace JSONL
files so selected `action` dimensions obey a per-tick target-rate envelope only
on unprotected samples. By default it protects all non-double-support samples
and samples near foot-contact transitions, so a global target-rate filter cannot
erase the double-support preparation -> single-support transition.

It does not train, SSH, deploy, run robot tests, or change runtime behavior.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TRANSITION_PROTECTED_BC_TRACE_ACTION_RATE_LIMIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "transition_protected_bc_trace_action_rate_limit.json"

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
    by_name = {name: idx for idx, name in enumerate(JOINT_NAMES)}
    out: list[int] = []
    for raw in value.split(","):
        item = raw.strip()
        if not item:
            continue
        out.append(by_name[item] if item in by_name else int(item))
    for idx in out:
        if idx < 0 or idx >= len(JOINT_NAMES):
            raise ValueError(f"joint index out of range: {idx}")
    return sorted(dict.fromkeys(out))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def vector(row: dict[str, Any], key: str) -> np.ndarray | None:
    value = row.get(key)
    if not isinstance(value, list) or len(value) != len(JOINT_NAMES):
        return None
    return np.asarray(value, dtype=float)


def contact_code(row: dict[str, Any]) -> str:
    contacts = row.get("foot_contacts") or []
    if not isinstance(contacts, list) or len(contacts) < 2:
        return "NA"
    return "".join(str(1 if int(value) else 0) for value in contacts[:2])


def nearest_transition_distances(codes: list[str]) -> list[int | None]:
    transitions = [idx for idx in range(1, len(codes)) if codes[idx] != codes[idx - 1]]
    out: list[int | None] = []
    for idx in range(len(codes)):
        if not transitions:
            out.append(None)
        else:
            out.append(min(abs(idx - transition) for transition in transitions))
    return out


def is_protected(
    index: int,
    code: str,
    distance: int | None,
    *,
    protect_transition_window_ticks: int,
    protect_non_double_support: bool,
    protected_contacts: set[str],
) -> bool:
    if code in protected_contacts:
        return True
    if protect_non_double_support and code != "11":
        return True
    if distance is not None and distance <= protect_transition_window_ticks:
        return True
    return False


def process_trace(
    path: Path,
    output_dir: Path,
    *,
    joint_indices: list[int],
    max_action_delta: float,
    action_scale: float,
    dt_s: float,
    output_mode: str,
    source_parent_depth: int,
    protect_transition_window_ticks: int,
    protect_non_double_support: bool,
    protected_contacts: set[str],
) -> dict[str, Any]:
    rows = read_jsonl(path)
    codes = [contact_code(row) for row in rows]
    transition_distances = nearest_transition_distances(codes)
    output_rows: list[dict[str, Any]] = []
    changed_counts = Counter()
    changed_contact_counts = Counter()
    protected_counts = Counter()
    original_velocities: dict[int, list[float]] = {idx: [] for idx in joint_indices}
    limited_velocities: dict[int, list[float]] = {idx: [] for idx in joint_indices}
    removed: dict[int, list[float]] = {idx: [] for idx in joint_indices}
    previous_original: np.ndarray | None = None
    previous_limited: np.ndarray | None = None

    for idx, row in enumerate(rows):
        action = vector(row, "action")
        if action is None:
            continue
        limited = action.copy()
        code = codes[idx]
        distance = transition_distances[idx]
        protected = is_protected(
            idx,
            code,
            distance,
            protect_transition_window_ticks=protect_transition_window_ticks,
            protect_non_double_support=protect_non_double_support,
            protected_contacts=protected_contacts,
        )
        if protected:
            protected_counts[code] += 1

        if previous_limited is not None:
            for joint_idx in joint_indices:
                delta = float(limited[joint_idx] - previous_limited[joint_idx])
                clipped_delta = float(np.clip(delta, -max_action_delta, max_action_delta))
                if (not protected) and abs(clipped_delta - delta) > 1.0e-12:
                    changed_counts[JOINT_NAMES[joint_idx]] += 1
                    changed_contact_counts[code] += 1
                    limited[joint_idx] = previous_limited[joint_idx] + clipped_delta
                    removed[joint_idx].append(abs(delta) - abs(clipped_delta))
                else:
                    removed[joint_idx].append(0.0)

        if previous_original is not None:
            for joint_idx in joint_indices:
                original_velocities[joint_idx].append(
                    abs(float(action[joint_idx] - previous_original[joint_idx])) * action_scale / dt_s
                )
        if previous_limited is not None:
            for joint_idx in joint_indices:
                limited_velocities[joint_idx].append(
                    abs(float(limited[joint_idx] - previous_limited[joint_idx])) * action_scale / dt_s
                )

        new_row = dict(row)
        new_row["original_action"] = row.get("original_action", row.get("action"))
        new_row["pre_rate_limit_action"] = row.get("action")
        new_row["action"] = limited.astype(float).tolist()
        new_row["transition_protected_rate_limit_protected"] = bool(protected)
        new_row["transition_protected_rate_limit_contact"] = code
        new_row["transition_protected_rate_limit_transition_distance"] = distance
        new_row["transition_protected_rate_limit_max_delta"] = float(max_action_delta)
        new_row["transition_protected_rate_limit_joints"] = [JOINT_NAMES[item] for item in joint_indices]
        new_row["mode"] = output_mode

        pre = vector(row, "target_pre_rate_limit_rad")
        if pre is not None:
            adjusted = pre.copy()
            for joint_idx in joint_indices:
                home = pre[joint_idx] - action[joint_idx] * action_scale
                adjusted[joint_idx] = home + limited[joint_idx] * action_scale
            new_row["target_pre_rate_limit_rad"] = adjusted.astype(float).tolist()

        output_rows.append(new_row)
        previous_original = action
        previous_limited = limited

    parent_depth = max(0, int(source_parent_depth))
    parent_parts = list(path.parent.parts[-parent_depth:]) if parent_depth else []
    output_path = output_dir / Path(*parent_parts, path.name)
    write_jsonl(output_path, output_rows)

    per_joint = {}
    for joint_idx in joint_indices:
        name = JOINT_NAMES[joint_idx]
        per_joint[name] = {
            "changed_ticks": int(changed_counts[name]),
            "original_target_velocity_p95_rad_s": percentile(original_velocities[joint_idx], 95),
            "original_target_velocity_max_rad_s": max(original_velocities[joint_idx]) if original_velocities[joint_idx] else None,
            "limited_target_velocity_p95_rad_s": percentile(limited_velocities[joint_idx], 95),
            "limited_target_velocity_max_rad_s": max(limited_velocities[joint_idx]) if limited_velocities[joint_idx] else None,
            "action_delta_removed_p95": percentile(removed[joint_idx], 95),
            "action_delta_removed_max": max(removed[joint_idx]) if removed[joint_idx] else None,
        }

    return {
        "source_trace": str(path),
        "output_trace": str(output_path),
        "samples_in": len(rows),
        "samples_out": len(output_rows),
        "protected_samples": int(sum(protected_counts.values())),
        "protected_contact_counts": dict(sorted(protected_counts.items())),
        "changed_ticks": int(sum(changed_counts.values())),
        "changed_contact_counts": dict(sorted(changed_contact_counts.items())),
        "per_joint": per_joint,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Transition-Protected BC Trace Action Rate Limit",
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
        f"- protect_transition_window_ticks: `{payload['settings']['protect_transition_window_ticks']}`",
        f"- protect_non_double_support: `{payload['settings']['protect_non_double_support']}`",
        f"- protected_contacts: `{payload['settings']['protected_contacts']}`",
        "",
        "## Summary",
        "",
        f"- traces: `{payload['summary']['traces']}`",
        f"- samples_out: `{payload['summary']['samples_out']}`",
        f"- protected_samples: `{payload['summary']['protected_samples']}`",
        f"- changed_ticks: `{payload['summary']['changed_ticks']}`",
        f"- changed_contact_counts: `{payload['summary']['changed_contact_counts']}`",
        f"- protected_contact_counts: `{payload['summary']['protected_contact_counts']}`",
        "",
        "| source | samples | protected | changed | joint | orig_p95 | limited_p95 | removed_p95 |",
        "|---|---:|---:|---:|---|---:|---:|---:|",
    ]
    for item in payload["traces"]:
        for joint, row in item["per_joint"].items():
            lines.append(
                "| {source} | {samples} | {protected} | {changed} | `{joint}` | {orig95} | {lim95} | {rem95} |".format(
                    source=Path(item["source_trace"]).name,
                    samples=item["samples_out"],
                    protected=item["protected_samples"],
                    changed=row["changed_ticks"],
                    joint=joint,
                    orig95=fmt(row.get("original_target_velocity_p95_rad_s")),
                    lim95=fmt(row.get("limited_target_velocity_p95_rad_s")),
                    rem95=fmt(row.get("action_delta_removed_p95")),
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
    parser.add_argument("--joints", default="left_hip_pitch,left_knee,left_ankle,right_hip_pitch,right_knee,right_ankle")
    parser.add_argument("--max-target-velocity-rad-s", type=float, default=2.25)
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--protect-transition-window-ticks", type=int, default=6)
    parser.add_argument("--protect-non-double-support", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--protected-contact", action="append", default=[])
    parser.add_argument("--output-mode", default="transition_protected_action_rate_limited")
    parser.add_argument("--source-parent-depth", type=int, default=0)
    args = parser.parse_args()

    paths: list[Path] = []
    for item in args.trace_glob:
        paths.extend(Path(path) for path in sorted(glob.glob(item)))
    paths = sorted(dict.fromkeys(paths))
    joint_indices = parse_joints(args.joints)
    max_action_delta = float(args.max_target_velocity_rad_s) * float(args.dt_s) / float(args.action_scale)
    protected_contacts = {str(item) for item in args.protected_contact}
    traces = [
        process_trace(
            path,
            Path(args.output_trace_dir),
            joint_indices=joint_indices,
            max_action_delta=max_action_delta,
            action_scale=float(args.action_scale),
            dt_s=float(args.dt_s),
            output_mode=str(args.output_mode),
            source_parent_depth=int(args.source_parent_depth),
            protect_transition_window_ticks=int(args.protect_transition_window_ticks),
            protect_non_double_support=bool(args.protect_non_double_support),
            protected_contacts=protected_contacts,
        )
        for path in paths
    ]
    status = "PASS_TRANSITION_PROTECTED_RATE_LIMIT_READY" if traces else "HOLD_NO_TRACES"
    protected_contact_counts = Counter()
    changed_contact_counts = Counter()
    for trace in traces:
        protected_contact_counts.update(trace["protected_contact_counts"])
        changed_contact_counts.update(trace["changed_contact_counts"])
    payload = {
        "status": status,
        "trace_globs": args.trace_glob,
        "output_trace_dir": args.output_trace_dir,
        "settings": {
            "joints": [JOINT_NAMES[idx] for idx in joint_indices],
            "max_target_velocity_rad_s": float(args.max_target_velocity_rad_s),
            "action_scale": float(args.action_scale),
            "dt_s": float(args.dt_s),
            "max_action_delta": max_action_delta,
            "protect_transition_window_ticks": int(args.protect_transition_window_ticks),
            "protect_non_double_support": bool(args.protect_non_double_support),
            "protected_contacts": sorted(protected_contacts),
            "output_mode": str(args.output_mode),
            "source_parent_depth": int(args.source_parent_depth),
        },
        "summary": {
            "traces": len(traces),
            "samples_out": int(sum(trace["samples_out"] for trace in traces)),
            "protected_samples": int(sum(trace["protected_samples"] for trace in traces)),
            "changed_ticks": int(sum(trace["changed_ticks"] for trace in traces)),
            "changed_contact_counts": dict(sorted(changed_contact_counts.items())),
            "protected_contact_counts": dict(sorted(protected_contact_counts.items())),
        },
        "traces": traces,
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"traces={len(traces)}")
    print(f"samples_out={payload['summary']['samples_out']}")
    print(f"protected_samples={payload['summary']['protected_samples']}")
    print(f"changed_ticks={payload['summary']['changed_ticks']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
