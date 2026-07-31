#!/usr/bin/env python3
"""Mine corrected-bridge teacher windows with per-joint velocity limits.

This is an offline analysis helper. It reads full-observation traces from
eval_policy_with_actuator_bridge.py and finds short windows where BEST_WALK
still moves forward, uses single support, and stays inside the corrected
per-joint pitch-chain velocity envelope.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
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
PITCH_INDEX = {name: JOINT_NAMES.index(name) for name in PITCH_CHAIN}


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
        return {"mean": None, "min": None, "p50": None, "p95": None, "max": None}
    return {
        "mean": mean(xs),
        "min": min(xs),
        "p50": percentile(xs, 0.50),
        "p95": percentile(xs, 0.95),
        "max": max(xs),
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if finite(value):
        return f"{float(value):.{digits}f}"
    return str(value)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
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
    contacts = row.get("foot_contacts")
    if not isinstance(contacts, list) or len(contacts) < 2:
        return "??"
    return f"{1 if int(contacts[0]) else 0}{1 if int(contacts[1]) else 0}"


def side_label(code: str) -> str:
    return {
        "10": "left_stance",
        "01": "right_stance",
        "11": "double_support",
        "00": "flight",
    }.get(code, "unknown")


def local_velocity(row: dict[str, Any], index: int) -> float | None:
    value = row.get("local_linvel_m_s")
    if isinstance(value, list) and len(value) > index and finite(value[index]):
        return float(value[index])
    return None


def load_velocity_limits(path: Path) -> dict[str, float]:
    payload = json.loads(path.read_text())
    root = payload.get("primary", payload)
    joints = root.get("joints", {})
    limits = {}
    for joint in PITCH_CHAIN:
        combined = (joints.get(joint) or {}).get("combined") or {}
        value = combined.get("velocity_limit_rad_s")
        if finite(value):
            limits[joint] = float(value)
    missing = [joint for joint in PITCH_CHAIN if joint not in limits]
    if missing:
        raise SystemExit(f"fit JSON is missing pitch-chain limits for: {', '.join(missing)}")
    return limits


def per_joint_velocity_p95(rows: list[dict[str, Any]], dt_s: float) -> dict[str, float | None]:
    values = {joint: [] for joint in PITCH_CHAIN}
    previous = vector(rows[0], "sent_target_rad") if rows else None
    for row in rows[1:]:
        current = vector(row, "sent_target_rad")
        if previous is not None and current is not None:
            for joint, index in PITCH_INDEX.items():
                values[joint].append(abs(current[index] - previous[index]) / max(dt_s, 1e-9))
        previous = current
    return {joint: percentile(items, 0.95) for joint, items in values.items()}


def velocity_excess(per_joint: dict[str, float | None], limits: dict[str, float]) -> dict[str, float]:
    out = {}
    for joint, limit in limits.items():
        value = per_joint.get(joint)
        if finite(value):
            out[joint] = max(0.0, float(value) - float(limit))
    return out


def majority_contact(rows: list[dict[str, Any]]) -> str:
    counts = Counter(contact_code(row) for row in rows)
    return counts.most_common(1)[0][0] if counts else "??"


def window_metrics(
    path: Path,
    rows: list[dict[str, Any]],
    start: int,
    args: argparse.Namespace,
    limits: dict[str, float],
) -> dict[str, Any]:
    window = rows[start : start + args.window_samples]
    contacts = Counter(contact_code(row) for row in window)
    vx = [value for row in window if finite(value := local_velocity(row, 0))]
    vy_abs = [abs(value) for row in window if finite(value := local_velocity(row, 1))]
    pitch_abs = [
        abs(float(row["body_pitch_rad"]))
        for row in window
        if finite(row.get("body_pitch_rad"))
    ]
    heights = [
        float(row["base_height_m"])
        for row in window
        if finite(row.get("base_height_m"))
    ]
    per_joint = per_joint_velocity_p95(window, args.dt_s)
    excess = velocity_excess(per_joint, limits)
    center = contact_code(window[len(window) // 2]) if window else "??"
    majority = majority_contact(window)
    total = max(len(window), 1)
    moving = sum(1 for value in vx if value >= args.min_tick_vx)
    in_envelope = sum(
        1
        for joint, value in per_joint.items()
        if finite(value) and float(value) <= limits[joint]
    )
    return {
        "source_path": str(path),
        "source_name": path.parent.name,
        "seed": window[0].get("seed") if window else None,
        "start_tick": window[0].get("tick") if window else None,
        "end_tick": window[-1].get("tick") if window else None,
        "samples": len(window),
        "mean_vx_m_s": mean(vx) if vx else None,
        "vy_abs_p95_m_s": percentile(vy_abs, 0.95),
        "body_pitch_abs_p95_rad": percentile(pitch_abs, 0.95),
        "base_height_min_m": min(heights) if heights else None,
        "single_support_pct": 100.0 * (contacts["10"] + contacts["01"]) / total,
        "double_support_pct": 100.0 * contacts["11"] / total,
        "left_stance_pct": 100.0 * contacts["10"] / total,
        "right_stance_pct": 100.0 * contacts["01"] / total,
        "moving_tick_pct": 100.0 * moving / total,
        "per_joint_velocity_p95_rad_s": per_joint,
        "per_joint_velocity_excess_rad_s": excess,
        "max_velocity_excess_rad_s": max(excess.values(), default=0.0),
        "joints_in_envelope_count": in_envelope,
        "center_contact": center,
        "majority_contact": majority,
        "center_side": side_label(center),
        "majority_side": side_label(majority),
        "contact_pct": {
            key: 100.0 * value / total for key, value in sorted(contacts.items())
        },
    }


def classify(window: dict[str, Any], args: argparse.Namespace) -> tuple[str, list[str]]:
    reasons = []
    if (window.get("mean_vx_m_s") or -1.0) < args.min_mean_vx:
        reasons.append("low_mean_vx")
    if (window.get("single_support_pct") or 0.0) < args.min_single_support_pct:
        reasons.append("low_single_support")
    if (window.get("moving_tick_pct") or 0.0) < args.min_moving_tick_pct:
        reasons.append("low_moving_tick")
    if (window.get("max_velocity_excess_rad_s") or 0.0) > args.max_velocity_excess:
        reasons.append("over_corrected_envelope")
    if (window.get("vy_abs_p95_m_s") or 0.0) > args.max_vy_abs_p95:
        reasons.append("high_lateral_velocity")
    if (window.get("body_pitch_abs_p95_rad") or 0.0) > args.max_body_pitch_abs_p95:
        reasons.append("high_body_pitch")
    if (window.get("base_height_min_m") or 0.0) < args.min_base_height:
        reasons.append("low_base_height")
    return ("PASS_CORRECTED_IN_ENVELOPE_WINDOW" if not reasons else "REJECT_WINDOW", reasons)


def collect_windows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, float]]:
    limits = load_velocity_limits(ROOT / args.fit_json)
    paths = []
    for pattern in args.trace_glob:
        paths.extend(Path(path) for path in glob.glob(str(ROOT / pattern)))
    paths = sorted(set(paths))
    windows = []
    for path in paths:
        rows = read_jsonl(path)
        for start in range(0, max(len(rows) - args.window_samples + 1, 0), args.stride_samples):
            item = window_metrics(path, rows, start, args, limits)
            tier, reasons = classify(item, args)
            item["tier"] = tier
            item["reasons"] = reasons
            windows.append(item)
    return windows, limits


def summarize(windows: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [item for item in windows if item["tier"] == "PASS_CORRECTED_IN_ENVELOPE_WINDOW"]
    groups = defaultdict(list)
    for item in windows:
        groups[f"center_{item['center_side']}__majority_{item['majority_side']}"].append(item)
    pass_groups = Counter(
        f"center_{item['center_side']}__majority_{item['majority_side']}" for item in passing
    )
    return {
        "windows": len(windows),
        "pass_windows": len(passing),
        "reason_counts": dict(Counter(reason for item in windows for reason in item["reasons"]).most_common()),
        "pass_group_counts": dict(pass_groups.most_common()),
        "pass_left_stance_windows": sum(
            1 for item in passing if "left_stance" in {item["center_side"], item["majority_side"]}
        ),
        "pass_right_stance_windows": sum(
            1 for item in passing if "right_stance" in {item["center_side"], item["majority_side"]}
        ),
        "by_group": {
            key: {
                "windows": len(values),
                "pass": sum(1 for item in values if item["tier"] == "PASS_CORRECTED_IN_ENVELOPE_WINDOW"),
                "mean_vx": stats([item.get("mean_vx_m_s") for item in values]),
                "max_excess": stats([item.get("max_velocity_excess_rad_s") for item in values]),
                "single_support_pct": stats([item.get("single_support_pct") for item in values]),
                "reasons": dict(Counter(reason for item in values for reason in item["reasons"]).most_common(5)),
            }
            for key, values in sorted(groups.items())
        },
    }


def status(summary: dict[str, Any], args: argparse.Namespace) -> str:
    if summary["pass_windows"] < args.min_pass_windows:
        return "HOLD_NO_CORRECTED_IN_ENVELOPE_WINDOWS"
    left = summary["pass_left_stance_windows"]
    right = summary["pass_right_stance_windows"]
    if left <= 0 or right <= 0:
        return "HOLD_CORRECTED_WINDOWS_ONE_SIDED"
    ratio = min(left, right) / max(left, right)
    if ratio < args.min_side_balance_ratio:
        return "WARN_CORRECTED_WINDOWS_IMBALANCED"
    return "PASS_CORRECTED_WINDOWS_BALANCED"


def compact_window(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "tier": item["tier"],
        "reasons": item["reasons"],
        "source_name": item["source_name"],
        "seed": item["seed"],
        "start_tick": item["start_tick"],
        "end_tick": item["end_tick"],
        "mean_vx_m_s": item["mean_vx_m_s"],
        "single_support_pct": item["single_support_pct"],
        "left_stance_pct": item["left_stance_pct"],
        "right_stance_pct": item["right_stance_pct"],
        "max_velocity_excess_rad_s": item["max_velocity_excess_rad_s"],
        "center_side": item["center_side"],
        "majority_side": item["majority_side"],
        "per_joint_velocity_p95_rad_s": item["per_joint_velocity_p95_rad_s"],
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# Corrected Bridge Teacher Window Analysis",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is offline sim analysis only. It does not SSH, deploy, train, or touch robot hardware.",
        "",
        "## Corrected Velocity Limits",
        "",
        "| joint | limit_rad_s |",
        "|---|---:|",
    ]
    for joint in PITCH_CHAIN:
        lines.append(f"| `{joint}` | {fmt(payload['velocity_limits_rad_s'].get(joint))} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- windows: `{summary['windows']}`",
            f"- pass_windows: `{summary['pass_windows']}`",
            f"- pass_left_stance_windows: `{summary['pass_left_stance_windows']}`",
            f"- pass_right_stance_windows: `{summary['pass_right_stance_windows']}`",
            f"- reason_counts: `{summary['reason_counts']}`",
            "",
            "## Contact Groups",
            "",
            "| group | windows | pass | mean_vx | max_excess | single_support | top_reasons |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for key, item in summary["by_group"].items():
        reasons = ", ".join(f"{reason}:{count}" for reason, count in item["reasons"].items())
        lines.append(
            f"| {key} | {item['windows']} | {item['pass']} | "
            f"{fmt(item['mean_vx']['mean'])} | {fmt(item['max_excess']['mean'])} | "
            f"{fmt(item['single_support_pct']['mean'])} | {reasons} |"
        )
    lines.extend(
        [
            "",
            "## Top Passing Windows",
            "",
            "| seed | ticks | center | majority | vx | single_% | left_% | right_% | max_excess |",
            "|---:|---:|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for item in payload["top_passing_windows"]:
        lines.append(
            f"| {item['seed']} | {item['start_tick']}-{item['end_tick']} | "
            f"{item['center_side']} | {item['majority_side']} | {fmt(item['mean_vx_m_s'])} | "
            f"{fmt(item['single_support_pct'])} | {fmt(item['left_stance_pct'])} | "
            f"{fmt(item['right_stance_pct'])} | {fmt(item['max_velocity_excess_rad_s'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `PASS_CORRECTED_WINDOWS_BALANCED` means corrected in-envelope snippets exist on both stance sides.",
            "- `HOLD_CORRECTED_WINDOWS_ONE_SIDED` means the old one-sided selector problem remains under the corrected bridge.",
            "- `HOLD_NO_CORRECTED_IN_ENVELOPE_WINDOWS` means the old teacher source is no longer usable under the corrected per-joint envelope.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", default=[])
    parser.add_argument("--fit-json", default="outputs/analysis/actuator_response_fit_corrected_knee.json")
    parser.add_argument("--output-md", default="outputs/analysis/CORRECTED_BRIDGE_TEACHER_WINDOWS.md")
    parser.add_argument("--output-json", default="outputs/analysis/corrected_bridge_teacher_windows.json")
    parser.add_argument("--window-samples", type=int, default=25)
    parser.add_argument("--stride-samples", type=int, default=5)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--min-mean-vx", type=float, default=0.03)
    parser.add_argument("--min-tick-vx", type=float, default=0.02)
    parser.add_argument("--min-moving-tick-pct", type=float, default=50.0)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--max-velocity-excess", type=float, default=0.0)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.20)
    parser.add_argument("--max-body-pitch-abs-p95", type=float, default=0.20)
    parser.add_argument("--min-base-height", type=float, default=0.12)
    parser.add_argument("--min-pass-windows", type=int, default=8)
    parser.add_argument("--min-side-balance-ratio", type=float, default=0.25)
    parser.add_argument("--top-window-limit", type=int, default=25)
    args = parser.parse_args()
    if not args.trace_glob:
        args.trace_glob = [
            "outputs/analysis/corrected_bridge_best_walk_reroll_x008/*/seed_*/trace.jsonl"
        ]

    windows, limits = collect_windows(args)
    summary = summarize(windows)
    payload = {
        "status": status(summary, args),
        "fit_json": args.fit_json,
        "velocity_limits_rad_s": limits,
        "criteria": {
            "window_samples": args.window_samples,
            "stride_samples": args.stride_samples,
            "min_mean_vx": args.min_mean_vx,
            "min_single_support_pct": args.min_single_support_pct,
            "max_velocity_excess": args.max_velocity_excess,
        },
        "summary": summary,
        "top_passing_windows": [
            compact_window(item)
            for item in sorted(
                [w for w in windows if w["tier"] == "PASS_CORRECTED_IN_ENVELOPE_WINDOW"],
                key=lambda w: (
                    -float(w.get("mean_vx_m_s") or -1.0),
                    float(w.get("max_velocity_excess_rad_s") or 999.0),
                ),
            )[: args.top_window_limit]
        ],
        "top_rejected_windows": [
            compact_window(item)
            for item in sorted(
                [w for w in windows if w["tier"] != "PASS_CORRECTED_IN_ENVELOPE_WINDOW"],
                key=lambda w: (
                    float(w.get("max_velocity_excess_rad_s") or 999.0),
                    -float(w.get("mean_vx_m_s") or -1.0),
                ),
            )[: args.top_window_limit]
        ],
    }
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={payload['status']}")
    print(f"pass_windows={summary['pass_windows']}")
    print(f"left={summary['pass_left_stance_windows']} right={summary['pass_right_stance_windows']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
