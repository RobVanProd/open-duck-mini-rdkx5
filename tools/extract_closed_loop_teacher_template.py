#!/usr/bin/env python3
"""Extract compact closed-loop teacher metrics from published-policy traces.

This reads existing per-tick JSONL traces and writes summary artifacts. It does
not run simulation, train, deploy, SSH, or touch robot hardware.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


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
PITCH_CHAIN = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]
PITCH_INDEXES = [JOINT_NAMES.index(name) for name in PITCH_CHAIN]


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if finite(value):
        return f"{float(value):.{digits}f}"
    return str(value)


def percentile(values: list[float], q: float) -> float | None:
    xs = sorted(float(value) for value in values if finite(value))
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def stats(values: list[float]) -> dict[str, float | None]:
    xs = [float(value) for value in values if finite(value)]
    if not xs:
        return {"mean": None, "std": None, "p50": None, "p95": None, "max": None}
    return {
        "mean": mean(xs),
        "std": pstdev(xs) if len(xs) > 1 else 0.0,
        "p50": percentile(xs, 0.50),
        "p95": percentile(xs, 0.95),
        "max": max(xs),
    }


def command_label_from_path(path: Path) -> str:
    text = str(path)
    marker = "published_policy_command_"
    if marker not in text:
        return path.parent.name
    tail = text.split(marker, 1)[1]
    return tail.split("_seed", 1)[0]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def vector(record: dict[str, Any], key: str) -> list[float] | None:
    value = record.get(key)
    if isinstance(value, list) and len(value) >= len(JOINT_NAMES):
        return [float(item) for item in value[: len(JOINT_NAMES)]]
    return None


def contact_code(record: dict[str, Any]) -> str:
    contacts = record.get("foot_contacts")
    if not isinstance(contacts, list) or len(contacts) < 2:
        return "??"
    return f"{1 if int(contacts[0]) else 0}{1 if int(contacts[1]) else 0}"


def local_vx(record: dict[str, Any]) -> float | None:
    values = record.get("local_linvel_m_s")
    if isinstance(values, list) and values and finite(values[0]):
        return float(values[0])
    return None


def command_x(record: dict[str, Any]) -> float | None:
    values = record.get("command")
    if isinstance(values, list) and values and finite(values[0]):
        return float(values[0])
    return None


def max_pitch_target_velocity(records: list[dict[str, Any]], dt_s: float) -> list[float | None]:
    values: list[float | None] = [None]
    previous = vector(records[0], "sent_target_rad") if records else None
    for record in records[1:]:
        current = vector(record, "sent_target_rad")
        if current is None or previous is None:
            values.append(None)
        else:
            values.append(
                max(abs(current[index] - previous[index]) / max(dt_s, 1.0e-9) for index in PITCH_INDEXES)
            )
        previous = current
    return values


def future_delta(records: list[dict[str, Any]], index: int, horizon_ticks: int) -> float | None:
    future = index + horizon_ticks
    if future >= len(records):
        return None
    now = local_vx(records[index])
    later = local_vx(records[future])
    if now is None or later is None:
        return None
    return later - now


def trace_summary(path: Path, dt_s: float, envelope_high: float, lookahead_s: float) -> dict[str, Any]:
    records = read_jsonl(path)
    velocities = max_pitch_target_velocity(records, dt_s)
    horizon_ticks = max(1, int(round(lookahead_s / dt_s)))
    counts = Counter()
    forward_deltas = []
    max_velocities = []
    safe_moving_deltas = []
    command = command_x(records[0]) if records else None
    required_vx = abs(command or 0.0) * 0.5
    action_abs = []
    delayed_action_abs = []
    for index, record in enumerate(records):
        code = contact_code(record)
        if code == "11":
            counts["double_support"] += 1
        elif code in {"10", "01"}:
            counts["single_support"] += 1
        elif code == "00":
            counts["flight"] += 1
        else:
            counts["unknown_contact"] += 1

        velocity = velocities[index]
        if finite(velocity):
            max_velocities.append(float(velocity))
        in_envelope = finite(velocity) and float(velocity) <= envelope_high
        vx = local_vx(record)
        moving = finite(vx) and float(vx) >= required_vx and required_vx > 0.0
        single = code in {"10", "01"}
        if in_envelope:
            counts["in_envelope_ticks"] += 1
        if moving:
            counts["moving_ticks"] += 1
        if moving and in_envelope:
            counts["moving_in_envelope_ticks"] += 1
        if moving and single:
            counts["moving_single_ticks"] += 1
        if moving and single and in_envelope:
            counts["moving_single_in_envelope_ticks"] += 1
            delta = future_delta(records, index, horizon_ticks)
            if finite(delta):
                safe_moving_deltas.append(float(delta))
        if single:
            delta = future_delta(records, index, horizon_ticks)
            if finite(delta):
                forward_deltas.append(float(delta))
        action = vector(record, "action")
        delayed = vector(record, "action_w_delay")
        if action is not None:
            action_abs.extend(abs(value) for value in action)
        if delayed is not None:
            delayed_action_abs.extend(abs(value) for value in delayed)

    total = max(1, len(records))
    return {
        "trace": str(path),
        "label": command_label_from_path(path),
        "seed": records[0].get("seed") if records else None,
        "samples": len(records),
        "command_x": command,
        "mean_local_vx_m_s": stats([local_vx(record) for record in records if finite(local_vx(record))])["mean"],
        "single_support_pct": 100.0 * counts["single_support"] / total,
        "in_envelope_pct": 100.0 * counts["in_envelope_ticks"] / total,
        "moving_tick_pct": 100.0 * counts["moving_ticks"] / total,
        "moving_in_envelope_pct": 100.0 * counts["moving_in_envelope_ticks"] / total,
        "moving_single_in_envelope_pct": 100.0
        * counts["moving_single_in_envelope_ticks"]
        / total,
        "single_support_future_vx_delta_m_s": stats(forward_deltas),
        "moving_single_in_envelope_future_vx_delta_m_s": stats(safe_moving_deltas),
        "max_pitch_target_velocity_rad_s": stats(max_velocities),
        "action_abs": stats(action_abs),
        "action_w_delay_abs": stats(delayed_action_abs),
    }


def aggregate(traces: list[dict[str, Any]]) -> dict[str, Any]:
    def collect(key: str) -> list[float]:
        return [float(trace[key]) for trace in traces if finite(trace.get(key))]

    def collect_nested(key: str, stat_key: str) -> list[float]:
        values = []
        for trace in traces:
            item = trace.get(key)
            if isinstance(item, dict) and finite(item.get(stat_key)):
                values.append(float(item[stat_key]))
        return values

    return {
        "trace_count": len(traces),
        "mean_local_vx_m_s": stats(collect("mean_local_vx_m_s")),
        "single_support_pct": stats(collect("single_support_pct")),
        "in_envelope_pct": stats(collect("in_envelope_pct")),
        "moving_tick_pct": stats(collect("moving_tick_pct")),
        "moving_in_envelope_pct": stats(collect("moving_in_envelope_pct")),
        "moving_single_in_envelope_pct": stats(collect("moving_single_in_envelope_pct")),
        "single_support_future_vx_delta_mean_m_s": stats(
            collect_nested("single_support_future_vx_delta_m_s", "mean")
        ),
        "moving_single_in_envelope_future_vx_delta_mean_m_s": stats(
            collect_nested("moving_single_in_envelope_future_vx_delta_m_s", "mean")
        ),
        "max_pitch_target_velocity_p95_rad_s": stats(
            collect_nested("max_pitch_target_velocity_rad_s", "p95")
        ),
        "max_pitch_target_velocity_max_rad_s": stats(
            collect_nested("max_pitch_target_velocity_rad_s", "max")
        ),
        "action_abs_p95": stats(collect_nested("action_abs", "p95")),
        "action_w_delay_abs_p95": stats(collect_nested("action_w_delay_abs", "p95")),
    }


def classify(groups: dict[str, Any], min_safe_moving_pct: float) -> str:
    moving_groups = []
    for item in groups.values():
        agg = item["aggregate"]
        moving_pct = agg["moving_tick_pct"]["mean"]
        safe_moving_pct = agg["moving_in_envelope_pct"]["mean"]
        if finite(moving_pct) and float(moving_pct) >= 20.0:
            moving_groups.append(item)
        if finite(safe_moving_pct) and float(safe_moving_pct) >= min_safe_moving_pct:
            return "PASS_HAS_LOW_RATE_MOVING_TEACHER_WINDOWS"
    if moving_groups:
        return "HOLD_MOVING_TEACHER_IS_OVER_ENVELOPE_DOMINANT"
    return "HOLD_NO_MOVING_TEACHER_WINDOWS"


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for trace_name in sorted(glob.glob(args.trace_glob)):
        summary = trace_summary(
            Path(trace_name),
            dt_s=args.dt_s,
            envelope_high=args.envelope_high,
            lookahead_s=args.lookahead_s,
        )
        groups.setdefault(summary["label"], []).append(summary)
    group_payload = {
        label: {"traces": traces, "aggregate": aggregate(traces)}
        for label, traces in sorted(groups.items())
    }
    return {
        "status": classify(group_payload, args.min_safe_moving_pct),
        "trace_glob": args.trace_glob,
        "dt_s": args.dt_s,
        "envelope_high_rad_s": args.envelope_high,
        "min_safe_moving_pct": args.min_safe_moving_pct,
        "groups": group_payload,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Closed-Loop Teacher Template",
        "",
        f"overall_status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        "| command_cell | traces | mean_vx | single_% | in_envelope_% | moving_% | moving_in_envelope_% | moving_single_in_envelope_% | single_dvx | safe_moving_single_dvx | pitch_vel_p95 | pitch_vel_max |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, item in payload["groups"].items():
        agg = item["aggregate"]
        lines.append(
            f"| {label} | {agg['trace_count']} | "
            f"{fmt(agg['mean_local_vx_m_s']['mean'])} | "
            f"{fmt(agg['single_support_pct']['mean'])} | "
            f"{fmt(agg['in_envelope_pct']['mean'])} | "
            f"{fmt(agg['moving_tick_pct']['mean'])} | "
            f"{fmt(agg['moving_in_envelope_pct']['mean'])} | "
            f"{fmt(agg['moving_single_in_envelope_pct']['mean'])} | "
            f"{fmt(agg['single_support_future_vx_delta_mean_m_s']['mean'])} | "
            f"{fmt(agg['moving_single_in_envelope_future_vx_delta_mean_m_s']['mean'])} | "
            f"{fmt(agg['max_pitch_target_velocity_p95_rad_s']['mean'])} | "
            f"{fmt(agg['max_pitch_target_velocity_max_rad_s']['mean'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if payload["status"] == "PASS_HAS_LOW_RATE_MOVING_TEACHER_WINDOWS":
        lines.append(
            "The traces contain moving low-rate windows that may be usable as a constrained teacher subset. Validate these windows before training."
        )
    elif payload["status"] == "HOLD_MOVING_TEACHER_IS_OVER_ENVELOPE_DOMINANT":
        lines.append(
            "The moving teacher behavior is dominated by over-envelope target-rate windows. Use the published policy as a movement teacher, but train the student with explicit target-rate constraints rather than copying targets directly."
        )
    else:
        lines.append(
            "No meaningful moving teacher windows were found in the scanned traces."
        )
    lines.extend(["", "Robot validation remains blocked."])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace-glob",
        default="outputs/analysis/published_policy_command_*_seed*/trace_full_obs_footpos.jsonl",
    )
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--lookahead-s", type=float, default=0.1)
    parser.add_argument("--envelope-high", type=float, default=3.75)
    parser.add_argument("--min-safe-moving-pct", type=float, default=10.0)
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/CLOSED_LOOP_TEACHER_TEMPLATE.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/closed_loop_teacher_template.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(build_markdown(payload) + "\n", encoding="utf-8")
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    print(f"overall_status: {payload['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
