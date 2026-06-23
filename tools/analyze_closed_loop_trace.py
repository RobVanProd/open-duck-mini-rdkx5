#!/usr/bin/env python3
"""Analyze an opt-in closed-loop sim trace.

This is an offline-only forensic helper for short candidate failures. It reads
the JSONL emitted by `eval_policy_with_actuator_bridge.py --trace-jsonl` and
summarizes body motion, pitch-chain targets/tracking, contacts, rewards, and
the final window before termination.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from actuator_bridge_model import JOINT_NAMES, PITCH_CHAIN_JOINTS


def finite(value: Any) -> bool:
    return isinstance(value, int | float) and not (
        math.isnan(float(value)) or math.isinf(float(value))
    )


def percentile(values: Sequence[float], pct: float) -> float | None:
    values = sorted(float(value) for value in values if finite(value))
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - k) + values[hi] * (k - lo)


def stats(values: Iterable[float], *, abs_value: bool = False) -> dict[str, float] | None:
    data = []
    for value in values:
        if finite(value):
            number = float(value)
            data.append(abs(number) if abs_value else number)
    if not data:
        return None
    return {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "p50": percentile(data, 50),
        "p95": percentile(data, 95),
        "p99": percentile(data, 99),
        "max": float(np.max(data)),
    }


def load_records(path: Path, mode: str | None) -> list[dict[str, Any]]:
    records = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if mode is not None and record.get("mode") != mode:
            continue
        records.append(record)
    return records


def as_array(records: list[dict[str, Any]], field: str) -> np.ndarray | None:
    rows = []
    for record in records:
        values = record.get(field)
        if not isinstance(values, list):
            return None
        rows.append(values)
    if not rows:
        return None
    return np.asarray(rows, dtype=float)


def abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros_like(values)
    return np.vstack(
        [
            np.zeros((1, values.shape[1])),
            np.abs(np.diff(values, axis=0) / max(dt_s, 1.0e-9)),
        ]
    )


def per_joint(records: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    sent = as_array(records, "sent_target_rad")
    applied = as_array(records, "applied_target_rad")
    actual = as_array(records, "actual_position_rad")
    action = as_array(records, "action")
    if sent is None or applied is None or actual is None or action is None:
        return {}
    sent_velocity = abs_velocity(sent, dt_s)
    applied_velocity = abs_velocity(applied, dt_s)
    bridge_tracking = np.abs(sent - applied)
    joint_tracking = np.abs(sent - actual)
    out: dict[str, Any] = {}
    for idx, joint in enumerate(JOINT_NAMES):
        out[joint] = {
            "sent_target_velocity_rad_s": stats(sent_velocity[:, idx], abs_value=True),
            "applied_target_velocity_rad_s": stats(applied_velocity[:, idx], abs_value=True),
            "bridge_tracking_error_rad": stats(bridge_tracking[:, idx], abs_value=True),
            "joint_target_tracking_error_rad": stats(joint_tracking[:, idx], abs_value=True),
            "action_abs": stats(action[:, idx], abs_value=True),
            "action_saturation_pct": float(np.mean(np.abs(action[:, idx]) >= 0.98) * 100.0),
        }
    return out


def largest_tracking_spike(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    best = None
    for record in records:
        sent = record.get("sent_target_rad")
        actual = record.get("actual_position_rad")
        if not isinstance(sent, list) or not isinstance(actual, list):
            continue
        for idx, joint in enumerate(JOINT_NAMES):
            if idx >= len(sent) or idx >= len(actual):
                continue
            error = abs(float(sent[idx]) - float(actual[idx]))
            if best is None or error > best["error_rad"]:
                best = {
                    "tick": record.get("tick"),
                    "time_s": record.get("time_s"),
                    "joint": joint,
                    "error_rad": error,
                    "sent_target_rad": float(sent[idx]),
                    "actual_position_rad": float(actual[idx]),
                }
    return best


def contact_events(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events = []
    last = None
    for record in records:
        contacts = record.get("foot_contacts")
        if contacts is None:
            continue
        current = tuple(int(value) for value in contacts)
        if last is not None and current != last:
            events.append(
                {
                    "tick": record.get("tick"),
                    "time_s": record.get("time_s"),
                    "from": list(last),
                    "to": list(current),
                }
            )
        last = current
    return events


def reward_terms(records: list[dict[str, Any]], window: int) -> dict[str, Any]:
    tail = records[-window:] if window > 0 else records
    keys = sorted(
        {
            key
            for record in tail
            for key in (record.get("reward_terms") or {}).keys()
        }
    )
    return {
        key: stats(
            [
                (record.get("reward_terms") or {}).get(key)
                for record in tail
                if finite((record.get("reward_terms") or {}).get(key))
            ]
        )
        for key in keys
    }


def build_summary(records: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    if not records:
        return {"status": "HOLD_NO_TRACE_RECORDS"}
    dt_s = float(args.dt_s)
    joint_summary = per_joint(records, dt_s)
    pitch_joints = {joint: joint_summary.get(joint, {}) for joint in PITCH_CHAIN_JOINTS}
    done_records = [record for record in records if record.get("done")]
    body_pitch_abs = [abs(float(record["body_pitch_rad"])) for record in records if finite(record.get("body_pitch_rad"))]
    max_body_pitch_tick = None
    if body_pitch_abs:
        max_record = max(
            (record for record in records if finite(record.get("body_pitch_rad"))),
            key=lambda record: abs(float(record["body_pitch_rad"])),
        )
        max_body_pitch_tick = {
            "tick": max_record.get("tick"),
            "time_s": max_record.get("time_s"),
            "body_pitch_rad": max_record.get("body_pitch_rad"),
        }
    forward = [record.get("local_linvel_m_s", [None])[0] for record in records]
    heights = [record.get("base_height_m") for record in records]
    contact_counts = np.sum(
        np.asarray([record.get("foot_contacts", [0, 0]) for record in records], dtype=int),
        axis=0,
    ).tolist()
    return {
        "status": "PASS_TRACE_ANALYZED",
        "mode": records[0].get("mode"),
        "samples": len(records),
        "duration_s": float(records[-1].get("time_s", 0.0)) if records else None,
        "termination": {
            "done_seen": bool(done_records),
            "first_done_tick": done_records[0].get("tick") if done_records else None,
            "first_done_time_s": done_records[0].get("time_s") if done_records else None,
        },
        "body_pitch_abs_rad": stats(body_pitch_abs),
        "max_body_pitch_tick": max_body_pitch_tick,
        "base_height_m": stats(heights),
        "local_forward_velocity_m_s": stats(forward),
        "progress_x_m": (
            float(records[-1].get("base_x_m")) - float(records[0].get("base_x_m"))
            if finite(records[-1].get("base_x_m")) and finite(records[0].get("base_x_m"))
            else None
        ),
        "foot_contact_counts": {
            "left": int(contact_counts[0]) if len(contact_counts) > 0 else 0,
            "right": int(contact_counts[1]) if len(contact_counts) > 1 else 0,
        },
        "foot_contact_events": contact_events(records),
        "largest_tracking_spike": largest_tracking_spike(records),
        "pitch_chain_joints": pitch_joints,
        "reward_terms_tail": reward_terms(records, args.tail_window),
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, int | float):
        return f"{float(value):.{digits}f}"
    return str(value)


def stat(summary: dict[str, Any] | None, key: str) -> Any:
    if not isinstance(summary, dict):
        return None
    return summary.get(key)


def write_markdown(summary: dict[str, Any], path: Path, source: Path) -> None:
    lines = [
        "# Closed-Loop Failure Trace Analysis",
        "",
        f"source: `{source}`",
        f"status: `{summary.get('status')}`",
        f"mode: `{summary.get('mode')}`",
        f"samples: `{summary.get('samples')}`",
        f"duration_s: `{fmt(summary.get('duration_s'))}`",
        "",
        "## Termination",
        "",
    ]
    termination = summary.get("termination") or {}
    lines.extend(
        [
            f"- done_seen: `{termination.get('done_seen')}`",
            f"- first_done_tick: `{termination.get('first_done_tick')}`",
            f"- first_done_time_s: `{fmt(termination.get('first_done_time_s'))}`",
            "",
            "## Body And Motion",
            "",
            f"- body_pitch_abs_p95_rad: `{fmt(stat(summary.get('body_pitch_abs_rad'), 'p95'))}`",
            f"- body_pitch_abs_max_rad: `{fmt(stat(summary.get('body_pitch_abs_rad'), 'max'))}`",
            f"- base_height_min_m: `{fmt(stat(summary.get('base_height_m'), 'min'))}`",
            f"- local_forward_velocity_mean_m_s: `{fmt(stat(summary.get('local_forward_velocity_m_s'), 'mean'))}`",
            f"- local_forward_velocity_p95_m_s: `{fmt(stat(summary.get('local_forward_velocity_m_s'), 'p95'))}`",
            f"- progress_x_m: `{fmt(summary.get('progress_x_m'))}`",
            f"- max_body_pitch_tick: `{summary.get('max_body_pitch_tick')}`",
            "",
            "## Contacts",
            "",
            f"- foot_contact_counts: `{summary.get('foot_contact_counts')}`",
            f"- contact_events: `{len(summary.get('foot_contact_events') or [])}`",
            "",
            "## Largest Tracking Spike",
            "",
            f"`{summary.get('largest_tracking_spike')}`",
            "",
            "## Pitch-Chain Joints",
            "",
            "| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for joint, item in (summary.get("pitch_chain_joints") or {}).items():
        lines.append(
            "| "
            f"{joint} | "
            f"{fmt(stat(item.get('sent_target_velocity_rad_s'), 'p95'))} | "
            f"{fmt(stat(item.get('applied_target_velocity_rad_s'), 'p95'))} | "
            f"{fmt(stat(item.get('bridge_tracking_error_rad'), 'p95'))} | "
            f"{fmt(stat(item.get('joint_target_tracking_error_rad'), 'p95'))} | "
            f"{fmt(stat(item.get('action_abs'), 'p95'))} | "
            f"{fmt(item.get('action_saturation_pct'))} |"
        )
    lines.extend(["", "## Tail Reward Terms", ""])
    reward_terms = summary.get("reward_terms_tail") or {}
    for key, item in reward_terms.items():
        lines.append(f"- `{key}` mean `{fmt(stat(item, 'mean'))}` p95 `{fmt(stat(item, 'p95'))}`")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace_jsonl")
    parser.add_argument("--mode", default=None)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--tail-window", type=int, default=20)
    parser.add_argument("--output-md", default=None)
    parser.add_argument("--output-json", default=None)
    args = parser.parse_args()

    source = Path(args.trace_jsonl)
    records = load_records(source, args.mode)
    summary = build_summary(records, args)
    if args.output_json:
        out_json = Path(args.output_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        write_markdown(summary, Path(args.output_md), source)
    if not args.output_json and not args.output_md:
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("status") == "PASS_TRACE_ANALYZED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
