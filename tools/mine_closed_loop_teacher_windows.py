#!/usr/bin/env python3
"""Mine closed-loop teacher windows from published-policy traces.

This is an offline analysis helper. It reads JSONL traces emitted by
eval_policy_with_actuator_bridge.py and identifies contiguous windows where the
published policy is moving forward, spending time in single support, and mostly
staying within the measured pitch-chain target-rate envelope.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PITCH_CHAIN = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]
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
PITCH_INDICES = [JOINT_NAMES.index(name) for name in PITCH_CHAIN]


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


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
        return {"mean": None, "std": None, "min": None, "p50": None, "p95": None, "max": None}
    return {
        "mean": mean(xs),
        "std": pstdev(xs) if len(xs) > 1 else 0.0,
        "min": min(xs),
        "p50": percentile(xs, 0.50),
        "p95": percentile(xs, 0.95),
        "max": max(xs),
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, str):
        return value
    if finite(value):
        return f"{float(value):.{digits}f}"
    return "NA"


def command_label(path: Path) -> str:
    name = path.parent.name
    if "_x004_seed" in name:
        return "straight_x004"
    if "_x008_seed" in name:
        return "straight_x008"
    if name.startswith("published_policy_upstream_main_backlash_seed"):
        return "upstream_nearest_turn"
    return name


def read_trace(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def vector(row: dict[str, Any], key: str) -> list[float] | None:
    value = row.get(key)
    if isinstance(value, list) and len(value) >= len(JOINT_NAMES):
        return [float(item) for item in value[: len(JOINT_NAMES)]]
    return None


def contact_code(row: dict[str, Any]) -> str:
    value = row.get("foot_contacts")
    if not isinstance(value, list) or len(value) < 2:
        return "??"
    return f"{1 if int(value[0]) else 0}{1 if int(value[1]) else 0}"


def local_velocity(row: dict[str, Any], index: int) -> float | None:
    value = row.get("local_linvel_m_s")
    if isinstance(value, list) and len(value) > index and finite(value[index]):
        return float(value[index])
    return None


def pitch_velocity_by_tick(rows: list[dict[str, Any]], dt_s: float) -> list[float | None]:
    out: list[float | None] = [None]
    previous = vector(rows[0], "sent_target_rad") if rows else None
    for row in rows[1:]:
        current = vector(row, "sent_target_rad")
        if previous is None or current is None:
            out.append(None)
        else:
            out.append(
                max(
                    abs(current[index] - previous[index]) / max(dt_s, 1.0e-9)
                    for index in PITCH_INDICES
                )
            )
        previous = current
    return out


def per_joint_pitch_velocity_p95(rows: list[dict[str, Any]], dt_s: float) -> dict[str, float | None]:
    previous = vector(rows[0], "sent_target_rad") if rows else None
    values = {name: [] for name in PITCH_CHAIN}
    for row in rows[1:]:
        current = vector(row, "sent_target_rad")
        if previous is not None and current is not None:
            for name, index in zip(PITCH_CHAIN, PITCH_INDICES, strict=True):
                values[name].append(abs(current[index] - previous[index]) / max(dt_s, 1.0e-9))
        previous = current
    return {name: percentile(items, 0.95) for name, items in values.items()}


def window_metrics(
    rows: list[dict[str, Any]],
    velocities: list[float | None],
    start: int,
    samples: int,
    args: argparse.Namespace,
    source: Path,
) -> dict[str, Any]:
    window = rows[start : start + samples]
    velocity_window = velocities[start : start + samples]
    total = len(window)
    contacts = Counter(contact_code(row) for row in window)
    vx = [value for row in window if finite(value := local_velocity(row, 0))]
    vy_abs = [abs(value) for row in window if finite(value := local_velocity(row, 1))]
    pitch = [abs(float(row["body_pitch_rad"])) for row in window if finite(row.get("body_pitch_rad"))]
    heights = [float(row["base_height_m"]) for row in window if finite(row.get("base_height_m"))]
    safe_ticks = [v for v in velocity_window if finite(v) and float(v) <= args.envelope_high]
    moving_ticks = [
        row
        for row in window
        if finite(value := local_velocity(row, 0)) and float(value) >= args.min_tick_vx
    ]
    moving_safe_ticks = [
        index
        for index, row in enumerate(window)
        if finite(vx_value := local_velocity(row, 0))
        and float(vx_value) >= args.min_tick_vx
        and finite(velocity_window[index])
        and float(velocity_window[index]) <= args.envelope_high
    ]
    moving_single_safe_ticks = [
        index
        for index in moving_safe_ticks
        if contact_code(window[index]) in {"10", "01"}
    ]
    per_joint = per_joint_pitch_velocity_p95(window, args.dt_s)
    fastest_joint = None
    for name, value in per_joint.items():
        if finite(value) and (fastest_joint is None or float(value) > fastest_joint["p95_rad_s"]):
            fastest_joint = {"joint": name, "p95_rad_s": float(value)}
    return {
        "source_path": str(source),
        "source_name": source.parent.name,
        "command_cell": command_label(source),
        "seed": window[0].get("seed"),
        "start_tick": window[0].get("tick"),
        "end_tick": window[-1].get("tick"),
        "start_time_s": window[0].get("time_s"),
        "end_time_s": window[-1].get("time_s"),
        "samples": total,
        "mean_vx_m_s": mean(vx) if vx else None,
        "vy_abs_p95_m_s": percentile(vy_abs, 0.95),
        "body_pitch_abs_p95_rad": percentile(pitch, 0.95),
        "base_height_min_m": min(heights) if heights else None,
        "single_support_pct": 100.0 * (contacts["10"] + contacts["01"]) / max(total, 1),
        "double_support_pct": 100.0 * contacts["11"] / max(total, 1),
        "in_envelope_pct": 100.0 * len(safe_ticks) / max(total, 1),
        "moving_tick_pct": 100.0 * len(moving_ticks) / max(total, 1),
        "moving_in_envelope_pct": 100.0 * len(moving_safe_ticks) / max(total, 1),
        "moving_single_in_envelope_pct": 100.0 * len(moving_single_safe_ticks) / max(total, 1),
        "pitch_target_velocity_p95_rad_s": percentile([v for v in velocity_window if finite(v)], 0.95),
        "pitch_target_velocity_max_rad_s": max([float(v) for v in velocity_window if finite(v)], default=None),
        "fastest_pitch_joint_p95": fastest_joint,
        "contact_pct": {key: 100.0 * value / max(total, 1) for key, value in sorted(contacts.items())},
    }


def classify(window: dict[str, Any], args: argparse.Namespace) -> tuple[str, list[str]]:
    reasons = []
    if (window.get("mean_vx_m_s") or -1.0) < args.min_mean_vx:
        reasons.append("low_mean_vx")
    if (window.get("single_support_pct") or 0.0) < args.min_single_support_pct:
        reasons.append("low_single_support")
    if (window.get("moving_in_envelope_pct") or 0.0) < args.min_moving_in_envelope_pct:
        reasons.append("low_moving_in_envelope")
    if (window.get("moving_single_in_envelope_pct") or 0.0) < args.min_moving_single_in_envelope_pct:
        reasons.append("low_moving_single_in_envelope")
    if (window.get("pitch_target_velocity_p95_rad_s") or 999.0) > args.envelope_high:
        reasons.append("high_pitch_velocity_p95")
    if (window.get("vy_abs_p95_m_s") or 0.0) > args.max_vy_abs_p95:
        reasons.append("high_lateral_velocity")
    if (window.get("body_pitch_abs_p95_rad") or 0.0) > args.max_body_pitch_abs_p95:
        reasons.append("high_body_pitch")
    if (window.get("base_height_min_m") or 0.0) < args.min_base_height:
        reasons.append("low_base_height")
    if not reasons:
        return "PASS_CURATED_CLOSED_LOOP_WINDOW", reasons
    if {"low_mean_vx", "high_pitch_velocity_p95", "low_base_height"} & set(reasons):
        return "REJECT_WINDOW", reasons
    return "REVIEW_WINDOW", reasons


def mine_trace(path: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    rows = read_trace(path)
    velocities = pitch_velocity_by_tick(rows, args.dt_s)
    windows = []
    for start in range(0, max(0, len(rows) - args.window_samples + 1), args.stride_samples):
        metrics = window_metrics(rows, velocities, start, args.window_samples, args, path)
        tier, reasons = classify(metrics, args)
        metrics["tier"] = tier
        metrics["reasons"] = reasons
        windows.append(metrics)
    return windows


def aggregate(windows: list[dict[str, Any]]) -> dict[str, Any]:
    pass_windows = [w for w in windows if w["tier"] == "PASS_CURATED_CLOSED_LOOP_WINDOW"]
    review_windows = [w for w in windows if w["tier"] == "REVIEW_WINDOW"]
    rejected = [w for w in windows if w["tier"] == "REJECT_WINDOW"]
    by_cell = {}
    for window in windows:
        item = by_cell.setdefault(
            window["command_cell"],
            {"windows": 0, "pass": 0, "review": 0, "reject": 0, "mean_vx": []},
        )
        item["windows"] += 1
        item[{"PASS_CURATED_CLOSED_LOOP_WINDOW": "pass", "REVIEW_WINDOW": "review"}.get(window["tier"], "reject")] += 1
        if finite(window.get("mean_vx_m_s")):
            item["mean_vx"].append(float(window["mean_vx_m_s"]))
    for item in by_cell.values():
        item["mean_vx"] = stats(item["mean_vx"])
    return {
        "windows": len(windows),
        "pass_windows": len(pass_windows),
        "review_windows": len(review_windows),
        "rejected_windows": len(rejected),
        "pass_source_names": sorted({w["source_name"] for w in pass_windows}),
        "pass_command_cells": sorted({w["command_cell"] for w in pass_windows}),
        "by_command_cell": by_cell,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Closed-Loop Teacher Window Mine",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline trace-mining artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Criteria",
        "",
    ]
    for key, value in payload["criteria"].items():
        lines.append(f"- {key}: `{value}`")
    aggregate_payload = payload["aggregate"]
    lines.extend(
        [
            "",
            "## Aggregate",
            "",
            f"- windows: `{aggregate_payload['windows']}`",
            f"- pass_windows: `{aggregate_payload['pass_windows']}`",
            f"- review_windows: `{aggregate_payload['review_windows']}`",
            f"- rejected_windows: `{aggregate_payload['rejected_windows']}`",
            f"- pass_command_cells: `{aggregate_payload['pass_command_cells']}`",
            f"- pass_source_names: `{aggregate_payload['pass_source_names']}`",
            "",
            "## By Command Cell",
            "",
            "| command_cell | windows | pass | review | reject | mean_vx |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for label, item in aggregate_payload["by_command_cell"].items():
        lines.append(
            f"| {label} | {item['windows']} | {item['pass']} | {item['review']} | {item['reject']} | {fmt(item['mean_vx']['mean'])} |"
        )
    lines.extend(
        [
            "",
            "## Top Passing Windows",
            "",
            "| command | source | ticks | vx | single_% | move_env_% | move_single_env_% | pitch_p95 | vy95 | height | fastest_pitch |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    passing = payload.get("top_passing_windows") or []
    passing.sort(
        key=lambda w: (
            float(w.get("mean_vx_m_s") or -1.0),
            float(w.get("moving_single_in_envelope_pct") or -1.0),
        ),
        reverse=True,
    )
    if not passing:
        lines.append("| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |")
    for window in passing[:25]:
        fastest = window.get("fastest_pitch_joint_p95") or {}
        lines.append(
            "| {command} | `{source}` | {ticks} | {vx} | {single} | {move_env} | {move_single} | {pitch} | {vy} | {height} | `{joint}:{joint_vel}` |".format(
                command=window["command_cell"],
                source=window["source_name"],
                ticks=f"{window['start_tick']}-{window['end_tick']}",
                vx=fmt(window["mean_vx_m_s"]),
                single=fmt(window["single_support_pct"]),
                move_env=fmt(window["moving_in_envelope_pct"]),
                move_single=fmt(window["moving_single_in_envelope_pct"]),
                pitch=fmt(window["pitch_target_velocity_p95_rad_s"]),
                vy=fmt(window["vy_abs_p95_m_s"]),
                height=fmt(window["base_height_min_m"]),
                joint=fastest.get("joint", "NA"),
                joint_vel=fmt(fastest.get("p95_rad_s")),
            )
        )
    lines.extend(
        [
            "",
            "## Rejection Reasons",
            "",
            "| reason | count |",
            "|---|---:|",
        ]
    )
    reasons = payload.get("reason_counts") or {}
    if not reasons:
        lines.append("| NA | 0 |")
    for reason, count in sorted(reasons.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Passing windows are candidate teacher snippets only; they are not a complete walking policy.",
            "- If passing windows exist only inside the moving command cells, straight x=0.04 should remain a posture/no-motion gate, not the first walking gate.",
            "- Before BC/export, inspect whether passing snippets have enough phase/contact diversity and whether high right-knee windows can be rejected without destroying continuity.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace-glob",
        action="append",
        default=[],
        help="Trace glob. May be passed multiple times.",
    )
    parser.add_argument("--output-md", default="outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_MINE.md")
    parser.add_argument("--output-json", default="outputs/analysis/closed_loop_teacher_window_mine.json")
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--window-samples", type=int, default=25)
    parser.add_argument("--stride-samples", type=int, default=5)
    parser.add_argument("--envelope-high", type=float, default=3.75)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--min-tick-vx", type=float, default=0.04)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-moving-in-envelope-pct", type=float, default=40.0)
    parser.add_argument("--min-moving-single-in-envelope-pct", type=float, default=10.0)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.20)
    parser.add_argument("--max-body-pitch-abs-p95", type=float, default=0.20)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    args = parser.parse_args()
    if not args.trace_glob:
        args.trace_glob = ["outputs/analysis/published_policy_upstream_main_backlash*seed*/trace.jsonl"]
    return args


def compact_window(window: dict[str, Any]) -> dict[str, Any]:
    return {
        "tier": window.get("tier"),
        "reasons": window.get("reasons"),
        "source_name": window.get("source_name"),
        "command_cell": window.get("command_cell"),
        "seed": window.get("seed"),
        "start_tick": window.get("start_tick"),
        "end_tick": window.get("end_tick"),
        "mean_vx_m_s": window.get("mean_vx_m_s"),
        "vy_abs_p95_m_s": window.get("vy_abs_p95_m_s"),
        "body_pitch_abs_p95_rad": window.get("body_pitch_abs_p95_rad"),
        "base_height_min_m": window.get("base_height_min_m"),
        "single_support_pct": window.get("single_support_pct"),
        "moving_in_envelope_pct": window.get("moving_in_envelope_pct"),
        "moving_single_in_envelope_pct": window.get("moving_single_in_envelope_pct"),
        "pitch_target_velocity_p95_rad_s": window.get("pitch_target_velocity_p95_rad_s"),
        "pitch_target_velocity_max_rad_s": window.get("pitch_target_velocity_max_rad_s"),
        "fastest_pitch_joint_p95": window.get("fastest_pitch_joint_p95"),
        "contact_pct": window.get("contact_pct"),
    }


def top_windows(windows: list[dict[str, Any]], tier: str, limit: int) -> list[dict[str, Any]]:
    selected = [window for window in windows if window.get("tier") == tier]
    selected.sort(
        key=lambda window: (
            float(window.get("mean_vx_m_s") or -1.0),
            float(window.get("moving_single_in_envelope_pct") or -1.0),
        ),
        reverse=True,
    )
    return [compact_window(window) for window in selected[:limit]]


def main() -> int:
    args = parse_args()
    paths = []
    for pattern in args.trace_glob:
        paths.extend(Path(path) for path in glob.glob(str(ROOT / pattern)))
    paths = sorted(set(paths))
    windows = []
    for path in paths:
        windows.extend(mine_trace(path, args))
    aggregate_payload = aggregate(windows)
    reason_counts = Counter(reason for window in windows for reason in window.get("reasons", []))
    status = (
        "PASS_CURATED_CLOSED_LOOP_WINDOWS_FOUND"
        if aggregate_payload["pass_windows"] >= 8
        else "HOLD_INSUFFICIENT_CLOSED_LOOP_WINDOWS"
    )
    payload = {
        "status": status,
        "trace_globs": args.trace_glob,
        "criteria": {
            "window_samples": args.window_samples,
            "stride_samples": args.stride_samples,
            "dt_s": args.dt_s,
            "envelope_high": args.envelope_high,
            "min_mean_vx": args.min_mean_vx,
            "min_tick_vx": args.min_tick_vx,
            "min_single_support_pct": args.min_single_support_pct,
            "min_moving_in_envelope_pct": args.min_moving_in_envelope_pct,
            "min_moving_single_in_envelope_pct": args.min_moving_single_in_envelope_pct,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_body_pitch_abs_p95": args.max_body_pitch_abs_p95,
            "min_base_height": args.min_base_height,
        },
        "aggregate": aggregate_payload,
        "reason_counts": dict(sorted(reason_counts.items())),
        "top_passing_windows": top_windows(windows, "PASS_CURATED_CLOSED_LOOP_WINDOW", 50),
        "top_review_windows": top_windows(windows, "REVIEW_WINDOW", 25),
        "top_rejected_windows": top_windows(windows, "REJECT_WINDOW", 25),
    }
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={status}")
    print(f"windows={aggregate_payload['windows']}")
    print(f"pass_windows={aggregate_payload['pass_windows']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
