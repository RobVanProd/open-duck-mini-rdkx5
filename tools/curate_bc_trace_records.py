#!/usr/bin/env python3
"""Curate per-record BC JSONL traces before manifest building.

This is an offline data-curation helper. It copies ignored full-observation
JSONL traces to a generated output directory, optionally dropping whole source
traces, capping selected action deltas, and clamping sample weights on matched
rows. It does not train, deploy, SSH, run robot tests, or change robot runtime
behavior.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
from pathlib import Path
import re
from typing import Any


JOINT_INDEX = {
    "left_hip_yaw": 0,
    "left_hip_roll": 1,
    "left_hip_pitch": 2,
    "left_knee": 3,
    "left_ankle": 4,
    "neck_pitch": 5,
    "head_pitch": 6,
    "head_yaw": 7,
    "head_roll": 8,
    "right_hip_yaw": 9,
    "right_hip_roll": 10,
    "right_hip_pitch": 11,
    "right_knee": 12,
    "right_ankle": 13,
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def rel_output_path(source: Path, output_dir: Path, parent_depth: int) -> Path:
    parent_parts = list(source.parent.parts[-max(1, parent_depth) :])
    return output_dir.joinpath(*parent_parts, source.name)


def parse_joint_indices(raw: str) -> list[int]:
    result: list[int] = []
    for item in str(raw).split(","):
        token = item.strip()
        if not token:
            continue
        if token in JOINT_INDEX:
            result.append(JOINT_INDEX[token])
            continue
        index = int(token)
        if not 0 <= index < 14:
            raise ValueError(f"joint index out of range: {index}")
        result.append(index)
    return sorted(set(result))


def contact_code(row: dict[str, Any]) -> str:
    contacts = row.get("foot_contacts")
    if isinstance(contacts, list | tuple) and len(contacts) == 2:
        return f"{int(contacts[0])}{int(contacts[1])}"
    return "NA"


def forward_velocity(row: dict[str, Any]) -> float | None:
    local = row.get("local_linvel_m_s")
    if isinstance(local, list | tuple) and local:
        try:
            return float(local[0])
        except (TypeError, ValueError):
            return None
    return None


def row_matches(row: dict[str, Any], args: argparse.Namespace) -> bool:
    checks: list[bool] = []
    if args.match_sample_weight_reason_regex:
        reasons = " ".join(str(item) for item in row.get("sample_weight_reasons", []))
        checks.append(bool(re.search(args.match_sample_weight_reason_regex, reasons)))
    if args.match_contact_code:
        checks.append(contact_code(row) == args.match_contact_code)
    if args.match_tick_min is not None:
        checks.append(int(row.get("tick") or 0) >= int(args.match_tick_min))
    if args.match_tick_max is not None:
        checks.append(int(row.get("tick") or 0) <= int(args.match_tick_max))
    if args.match_local_vx_max is not None:
        vx = forward_velocity(row)
        checks.append(vx is not None and vx <= float(args.match_local_vx_max))
    if args.match_body_pitch_abs_min is not None:
        pitch = row.get("body_pitch_rad")
        checks.append(pitch is not None and abs(float(pitch)) >= float(args.match_body_pitch_abs_min))
    if args.match_base_height_max is not None:
        height = row.get("base_height_m")
        checks.append(height is not None and float(height) <= float(args.match_base_height_max))
    if not checks:
        return False
    return any(checks) if args.match_any else all(checks)


def should_transform_source(path: Path, args: argparse.Namespace) -> bool:
    if not args.transform_source_regex:
        return True
    return bool(re.search(args.transform_source_regex, str(path)))


def target_velocity_stats(rows: list[dict[str, Any]], joints: list[int], action_scale: float, dt_s: float) -> dict[str, float]:
    max_by_joint: dict[str, float] = {}
    previous: list[float] | None = None
    for row in rows:
        action = row.get("action")
        if not isinstance(action, list | tuple) or len(action) < 14:
            continue
        current = [float(value) for value in action]
        if previous is not None:
            for joint in joints:
                vel = abs(current[joint] - previous[joint]) * action_scale / dt_s
                key = str(joint)
                max_by_joint[key] = max(max_by_joint.get(key, 0.0), vel)
        previous = current
    return max_by_joint


def cap_action_deltas(
    rows: list[dict[str, Any]],
    joints: list[int],
    max_target_velocity_rad_s: float | None,
    action_scale: float,
    dt_s: float,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    if not joints or max_target_velocity_rad_s is None:
        return rows, Counter()
    max_delta = float(max_target_velocity_rad_s) * dt_s / action_scale
    capped_counts: Counter[str] = Counter()
    previous_action: list[float] | None = None
    out: list[dict[str, Any]] = []
    for row in rows:
        copied = dict(row)
        action = copied.get("action")
        if isinstance(action, list | tuple) and len(action) >= 14:
            current = [float(value) for value in action]
            if previous_action is not None:
                row_capped = False
                for joint in joints:
                    delta = current[joint] - previous_action[joint]
                    if abs(delta) > max_delta:
                        current[joint] = previous_action[joint] + max_delta * (1.0 if delta > 0 else -1.0)
                        capped_counts[str(joint)] += 1
                        row_capped = True
                copied["action"] = current
                if row_capped:
                    reasons = set(str(item) for item in copied.get("sample_weight_reasons", []))
                    reasons.add("action_delta_capped")
                    copied["sample_weight_reasons"] = sorted(reasons)
            previous_action = list(current)
        out.append(copied)
    return out, capped_counts


def clamp_row_weights(rows: list[dict[str, Any]], args: argparse.Namespace) -> tuple[list[dict[str, Any]], int]:
    if args.max_matched_weight is None:
        return rows, 0
    out: list[dict[str, Any]] = []
    changed = 0
    for row in rows:
        copied = dict(row)
        if row_matches(copied, args):
            old_weight = float(copied.get("sample_weight", 1.0))
            new_weight = min(old_weight, float(args.max_matched_weight))
            if new_weight != old_weight:
                copied["sample_weight"] = new_weight
                reasons = set(str(item) for item in copied.get("sample_weight_reasons", []))
                reasons.add(args.weight_reason)
                copied["sample_weight_reasons"] = sorted(reasons)
                changed += 1
        out.append(copied)
    return out, changed


def process_trace(path: Path, output_dir: Path, args: argparse.Namespace) -> dict[str, Any] | None:
    if args.drop_source_regex and re.search(args.drop_source_regex, str(path)):
        return {
            "source_trace": str(path),
            "output_trace": None,
            "dropped": True,
            "reason": "drop_source_regex",
        }

    rows = read_jsonl(path)
    output_path = rel_output_path(path, output_dir, int(args.output_parent_depth))
    transformed = should_transform_source(path, args)
    joints = parse_joint_indices(args.joints) if transformed and args.joints else []
    before_vel = target_velocity_stats(rows, joints, float(args.action_scale_rad), float(args.dt_s))
    capped_counts: Counter[str] = Counter()
    weight_clamped = 0
    out_rows = rows
    if transformed:
        out_rows, capped_counts = cap_action_deltas(
            out_rows,
            joints,
            args.max_target_velocity_rad_s,
            float(args.action_scale_rad),
            float(args.dt_s),
        )
        out_rows, weight_clamped = clamp_row_weights(out_rows, args)
    after_vel = target_velocity_stats(out_rows, joints, float(args.action_scale_rad), float(args.dt_s))
    write_jsonl(output_path, out_rows)
    return {
        "source_trace": str(path),
        "output_trace": str(output_path),
        "dropped": False,
        "transformed": transformed,
        "samples": len(rows),
        "weight_clamped_rows": weight_clamped,
        "action_delta_capped": dict(sorted(capped_counts.items())),
        "target_velocity_max_before": before_vel,
        "target_velocity_max_after": after_vel,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Curated BC Trace Records",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline generated trace-curation artifact. It does not train,",
        "deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Settings",
        "",
    ]
    for key, value in payload["settings"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- input_traces: `{payload['summary']['input_traces']}`",
            f"- output_traces: `{payload['summary']['output_traces']}`",
            f"- dropped_traces: `{payload['summary']['dropped_traces']}`",
            f"- transformed_traces: `{payload['summary']['transformed_traces']}`",
            f"- weight_clamped_rows: `{payload['summary']['weight_clamped_rows']}`",
            f"- action_delta_capped: `{payload['summary']['action_delta_capped']}`",
            "",
            "## Traces",
            "",
            "| source | dropped | transformed | samples | weight clamped | action capped |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for item in payload["traces"]:
        lines.append(
            "| {source} | {dropped} | {transformed} | {samples} | {weight} | `{capped}` |".format(
                source=Path(item["source_trace"]).name,
                dropped=item.get("dropped"),
                transformed=item.get("transformed"),
                samples=item.get("samples", 0),
                weight=item.get("weight_clamped_rows", 0),
                capped=item.get("action_delta_capped", {}),
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- This artifact only prepares labels for a later BC fit.",
            "- It is not a deployable candidate and is not a robot-side change.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", required=True)
    parser.add_argument("--output-trace-dir", required=True)
    parser.add_argument("--output-parent-depth", type=int, default=3)
    parser.add_argument("--drop-source-regex", default=None)
    parser.add_argument("--transform-source-regex", default=None)
    parser.add_argument("--joints", default="")
    parser.add_argument("--max-target-velocity-rad-s", type=float, default=None)
    parser.add_argument("--action-scale-rad", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--max-matched-weight", type=float, default=None)
    parser.add_argument("--weight-reason", default="curated_failure_tail_downweight")
    parser.add_argument("--match-sample-weight-reason-regex", default=None)
    parser.add_argument("--match-contact-code", default=None)
    parser.add_argument("--match-tick-min", type=int, default=None)
    parser.add_argument("--match-tick-max", type=int, default=None)
    parser.add_argument("--match-local-vx-max", type=float, default=None)
    parser.add_argument("--match-body-pitch-abs-min", type=float, default=None)
    parser.add_argument("--match-base-height-max", type=float, default=None)
    parser.add_argument("--match-any", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    paths: list[Path] = []
    for item in args.trace_glob:
        paths.extend(Path(path) for path in sorted(glob.glob(item)))
    paths = sorted(dict.fromkeys(paths))
    output_dir = Path(args.output_trace_dir)
    traces = [process_trace(path, output_dir, args) for path in paths]
    traces = [item for item in traces if item is not None]
    action_counts: Counter[str] = Counter()
    for item in traces:
        action_counts.update(item.get("action_delta_capped", {}))
    payload = {
        "status": "PASS_CURATED_BC_TRACE_RECORDS_READY" if any(not item.get("dropped") for item in traces) else "HOLD_NO_OUTPUT_TRACES",
        "trace_globs": args.trace_glob,
        "output_trace_dir": str(output_dir),
        "settings": {
            "drop_source_regex": args.drop_source_regex,
            "transform_source_regex": args.transform_source_regex,
            "joints": args.joints,
            "max_target_velocity_rad_s": args.max_target_velocity_rad_s,
            "max_matched_weight": args.max_matched_weight,
            "match_sample_weight_reason_regex": args.match_sample_weight_reason_regex,
            "match_contact_code": args.match_contact_code,
            "match_tick_min": args.match_tick_min,
            "match_tick_max": args.match_tick_max,
            "match_local_vx_max": args.match_local_vx_max,
            "match_body_pitch_abs_min": args.match_body_pitch_abs_min,
            "match_base_height_max": args.match_base_height_max,
            "match_any": args.match_any,
        },
        "summary": {
            "input_traces": len(paths),
            "output_traces": sum(1 for item in traces if not item.get("dropped")),
            "dropped_traces": sum(1 for item in traces if item.get("dropped")),
            "transformed_traces": sum(1 for item in traces if item.get("transformed")),
            "weight_clamped_rows": sum(int(item.get("weight_clamped_rows") or 0) for item in traces),
            "action_delta_capped": dict(sorted(action_counts.items())),
        },
        "traces": traces,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload))
    print(payload["status"])
    print(f"output_traces={payload['summary']['output_traces']}")
    print(f"weight_clamped_rows={payload['summary']['weight_clamped_rows']}")
    print(f"action_delta_capped={payload['summary']['action_delta_capped']}")
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
