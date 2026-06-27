#!/usr/bin/env python3
"""Compare safe and unsafe BEST_WALK closed-loop windows.

This offline analyzer reads full-observation published-policy traces, scores
short windows with the same movement/contact/envelope criteria used by the
snippet miner, and summarizes which state/action features separate passing
windows from rejected moving windows. It is intended to guide the next
closed-loop selector or continuity source before any training.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import json
import math
from pathlib import Path
from statistics import mean, pstdev
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
PITCH_INDICES = [JOINT_NAMES.index(name) for name in PITCH_CHAIN]


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, str):
        return value
    if finite(value):
        return f"{float(value):.{digits}f}"
    return "NA"


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


def pct(count: int, total: int) -> float | None:
    if total <= 0:
        return None
    return 100.0 * count / total


def read_trace(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def command_label(path: Path) -> str:
    name = path.parent.name
    marker = "published_policy_command_"
    if marker in name:
        rest = name.split(marker, 1)[1]
        if "_seed" in rest:
            return rest.rsplit("_seed", 1)[0]
        return rest
    return name


def vector(row: dict[str, Any], key: str) -> list[float] | None:
    value = row.get(key)
    if not isinstance(value, list) or len(value) < len(JOINT_NAMES):
        return None
    out = [float(item) for item in value[: len(JOINT_NAMES)] if finite(item)]
    return out if len(out) == len(JOINT_NAMES) else None


def contact_code(row: dict[str, Any]) -> str:
    contacts = row.get("foot_contacts")
    if not isinstance(contacts, list) or len(contacts) < 2:
        return "??"
    left = 1 if int(contacts[0]) else 0
    right = 1 if int(contacts[1]) else 0
    return f"{left}{right}"


def contact_bucket(code: str) -> str:
    if code == "11":
        return "double"
    if code in {"10", "01"}:
        return "single"
    if code == "00":
        return "flight"
    return "unknown"


def local_velocity(row: dict[str, Any], index: int) -> float | None:
    value = row.get("local_linvel_m_s")
    if isinstance(value, list) and len(value) > index and finite(value[index]):
        return float(value[index])
    return None


def stance_foot_index(code: str) -> int | None:
    if code == "10":
        return 0
    if code == "01":
        return 1
    return None


def stance_relative_base(row: dict[str, Any]) -> tuple[float, float] | None:
    index = stance_foot_index(contact_code(row))
    feet = row.get("foot_site_pos_m")
    base_x = row.get("base_x_m")
    base_y = row.get("base_y_m")
    if index is None or not isinstance(feet, list) or len(feet) <= index:
        return None
    foot = feet[index]
    if not isinstance(foot, list) or len(foot) < 2:
        return None
    if not (finite(base_x) and finite(base_y) and finite(foot[0]) and finite(foot[1])):
        return None
    return float(base_x) - float(foot[0]), float(base_y) - float(foot[1])


def per_joint_rate(
    rows: list[dict[str, Any]], start: int, samples: int, key: str, dt_s: float
) -> dict[str, dict[str, float | None]]:
    values = {name: [] for name in PITCH_CHAIN}
    previous = vector(rows[start], key) if start < len(rows) else None
    for row in rows[start + 1 : start + samples]:
        current = vector(row, key)
        if previous is not None and current is not None:
            for name, index in zip(PITCH_CHAIN, PITCH_INDICES, strict=True):
                values[name].append(abs(current[index] - previous[index]) / max(dt_s, 1.0e-9))
        previous = current
    return {name: stats(items) for name, items in values.items()}


def max_pitch_rate(per_joint: dict[str, dict[str, float | None]], stat: str = "p95") -> tuple[str | None, float | None]:
    best_name: str | None = None
    best_value: float | None = None
    for name, item in per_joint.items():
        value = item.get(stat)
        if finite(value) and (best_value is None or float(value) > best_value):
            best_name = name
            best_value = float(value)
    return best_name, best_value


def action_delta_stats(rows: list[dict[str, Any]], start: int, samples: int) -> dict[str, float | None]:
    values: list[float] = []
    previous = vector(rows[start], "action") if start < len(rows) else None
    for row in rows[start + 1 : start + samples]:
        current = vector(row, "action")
        if previous is not None and current is not None:
            for index in range(len(JOINT_NAMES)):
                values.append(abs(current[index] - previous[index]))
        previous = current
    return stats(values)


def window_metrics(path: Path, rows: list[dict[str, Any]], start: int, args: argparse.Namespace) -> dict[str, Any]:
    window = rows[start : start + args.window_samples]
    contacts = Counter(contact_code(row) for row in window)
    vx_values = [value for row in window if (value := local_velocity(row, 0)) is not None]
    vy_abs_values = [abs(value) for row in window if (value := local_velocity(row, 1)) is not None]
    pitch_abs = [abs(float(row["body_pitch_rad"])) for row in window if finite(row.get("body_pitch_rad"))]
    heights = [float(row["base_height_m"]) for row in window if finite(row.get("base_height_m"))]
    stance_dx: list[float] = []
    stance_abs_dy: list[float] = []
    future_dvx_single: list[float] = []
    for index, row in enumerate(window):
        rel = stance_relative_base(row)
        if rel is not None:
            stance_dx.append(rel[0])
            stance_abs_dy.append(abs(rel[1]))
        future_index = start + index + args.future_ticks
        now = local_velocity(row, 0)
        later = local_velocity(rows[future_index], 0) if future_index < len(rows) else None
        if contact_bucket(contact_code(row)) == "single" and now is not None and later is not None:
            future_dvx_single.append(later - now)
    target_rates = per_joint_rate(rows, start, args.window_samples, "sent_target_rad", args.dt_s)
    fastest_joint, fastest_p95 = max_pitch_rate(target_rates)
    right_knee_p95 = target_rates["right_knee"]["p95"]
    left_knee_p95 = target_rates["left_knee"]["p95"]
    moving_ticks = [value for value in vx_values if value >= args.min_tick_vx]
    moving_in_envelope = 0
    moving_single_in_envelope = 0
    rate_by_tick: list[float | None] = [None]
    previous = vector(rows[start], "sent_target_rad")
    for row in rows[start + 1 : start + args.window_samples]:
        current = vector(row, "sent_target_rad")
        if previous is None or current is None:
            rate_by_tick.append(None)
        else:
            rate_by_tick.append(
                max(abs(current[index] - previous[index]) / max(args.dt_s, 1.0e-9) for index in PITCH_INDICES)
            )
        previous = current
    for index, row in enumerate(window):
        vx = local_velocity(row, 0)
        rate = rate_by_tick[index]
        if vx is not None and vx >= args.min_tick_vx and finite(rate) and float(rate) <= args.envelope_high:
            moving_in_envelope += 1
            if contact_bucket(contact_code(row)) == "single":
                moving_single_in_envelope += 1
    total = max(len(window), 1)
    metrics = {
        "source_path": str(path),
        "source_name": path.parent.name,
        "command_cell": command_label(path),
        "seed": window[0].get("seed") if window else None,
        "start_tick": window[0].get("tick") if window else None,
        "end_tick": window[-1].get("tick") if window else None,
        "samples": len(window),
        "mean_vx_m_s": mean(vx_values) if vx_values else None,
        "vy_abs_p95_m_s": percentile(vy_abs_values, 0.95),
        "body_pitch_abs_p95_rad": percentile(pitch_abs, 0.95),
        "base_height_min_m": min(heights) if heights else None,
        "single_support_pct": pct(contacts["10"] + contacts["01"], total),
        "double_support_pct": pct(contacts["11"], total),
        "moving_tick_pct": pct(len(moving_ticks), total),
        "moving_in_envelope_pct": pct(moving_in_envelope, total),
        "moving_single_in_envelope_pct": pct(moving_single_in_envelope, total),
        "single_future_dvx_0p1s_m_s": mean(future_dvx_single) if future_dvx_single else None,
        "stance_base_dx_mean_m": mean(stance_dx) if stance_dx else None,
        "stance_base_abs_dy_mean_m": mean(stance_abs_dy) if stance_abs_dy else None,
        "pitch_target_velocity_p95_rad_s": fastest_p95,
        "fastest_pitch_joint_p95": {"joint": fastest_joint, "p95_rad_s": fastest_p95},
        "right_knee_target_velocity_p95_rad_s": right_knee_p95,
        "left_knee_target_velocity_p95_rad_s": left_knee_p95,
        "action_delta": action_delta_stats(rows, start, args.window_samples),
        "contact_pct": {key: pct(value, total) for key, value in sorted(contacts.items())},
    }
    metrics["tier"], metrics["reasons"] = classify(metrics, args)
    metrics["rule_bucket"] = rule_bucket(metrics)
    return metrics


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


def rule_bucket(window: dict[str, Any]) -> str:
    reasons = set(window.get("reasons") or [])
    if window.get("tier") == "PASS_CURATED_CLOSED_LOOP_WINDOW":
        return "pass_safe_moving_single"
    if "high_pitch_velocity_p95" in reasons and (window.get("mean_vx_m_s") or 0.0) >= 0.04:
        return "reject_high_rate_moving"
    if "low_mean_vx" in reasons:
        return "reject_low_progress"
    if "low_single_support" in reasons:
        return "review_low_support"
    if "high_lateral_velocity" in reasons:
        return "review_lateral"
    return "other"


def collect(items: list[dict[str, Any]], key: str | list[str]) -> list[float]:
    out: list[float] = []
    path = [key] if isinstance(key, str) else key
    for item in items:
        value: Any = item
        for part in path:
            value = value.get(part) if isinstance(value, dict) else None
        if finite(value):
            out.append(float(value))
    return out


def summarize_windows(windows: list[dict[str, Any]]) -> dict[str, Any]:
    by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_command: dict[str, Counter[str]] = defaultdict(Counter)
    fastest_joint_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    for window in windows:
        bucket = window["rule_bucket"]
        by_bucket[bucket].append(window)
        by_command[window["command_cell"]][bucket] += 1
        for reason in window.get("reasons") or []:
            reason_counts[reason] += 1
        joint = (window.get("fastest_pitch_joint_p95") or {}).get("joint")
        if joint:
            fastest_joint_counts[joint] += 1
    bucket_summary = {}
    for bucket, items in sorted(by_bucket.items()):
        bucket_summary[bucket] = {
            "windows": len(items),
            "mean_vx_m_s": stats(collect(items, "mean_vx_m_s")),
            "single_support_pct": stats(collect(items, "single_support_pct")),
            "moving_in_envelope_pct": stats(collect(items, "moving_in_envelope_pct")),
            "moving_single_in_envelope_pct": stats(collect(items, "moving_single_in_envelope_pct")),
            "single_future_dvx_0p1s_m_s": stats(collect(items, "single_future_dvx_0p1s_m_s")),
            "stance_base_dx_mean_m": stats(collect(items, "stance_base_dx_mean_m")),
            "stance_base_abs_dy_mean_m": stats(collect(items, "stance_base_abs_dy_mean_m")),
            "vy_abs_p95_m_s": stats(collect(items, "vy_abs_p95_m_s")),
            "body_pitch_abs_p95_rad": stats(collect(items, "body_pitch_abs_p95_rad")),
            "pitch_target_velocity_p95_rad_s": stats(collect(items, "pitch_target_velocity_p95_rad_s")),
            "right_knee_target_velocity_p95_rad_s": stats(collect(items, "right_knee_target_velocity_p95_rad_s")),
            "left_knee_target_velocity_p95_rad_s": stats(collect(items, "left_knee_target_velocity_p95_rad_s")),
            "action_delta_p95": stats(collect(items, ["action_delta", "p95"])),
        }
    return {
        "bucket_summary": bucket_summary,
        "by_command_cell": {key: dict(value) for key, value in sorted(by_command.items())},
        "reason_counts": dict(reason_counts.most_common()),
        "fastest_pitch_joint_counts": dict(fastest_joint_counts.most_common()),
    }


def top_windows(windows: list[dict[str, Any]], bucket: str, limit: int) -> list[dict[str, Any]]:
    selected = [window for window in windows if window["rule_bucket"] == bucket]
    selected.sort(
        key=lambda item: (
            float(item.get("mean_vx_m_s") or -1.0),
            float(item.get("moving_single_in_envelope_pct") or -1.0),
        ),
        reverse=True,
    )
    keys = [
        "command_cell",
        "source_name",
        "seed",
        "start_tick",
        "end_tick",
        "rule_bucket",
        "tier",
        "reasons",
        "mean_vx_m_s",
        "single_support_pct",
        "moving_in_envelope_pct",
        "moving_single_in_envelope_pct",
        "single_future_dvx_0p1s_m_s",
        "stance_base_dx_mean_m",
        "stance_base_abs_dy_mean_m",
        "pitch_target_velocity_p95_rad_s",
        "right_knee_target_velocity_p95_rad_s",
        "left_knee_target_velocity_p95_rad_s",
        "fastest_pitch_joint_p95",
    ]
    return [{key: item.get(key) for key in keys} for item in selected[:limit]]


def status(summary: dict[str, Any]) -> str:
    safe = summary["bucket_summary"].get("pass_safe_moving_single", {}).get("windows", 0)
    high_rate = summary["bucket_summary"].get("reject_high_rate_moving", {}).get("windows", 0)
    if safe and high_rate:
        return "PASS_RULE_CONTRAST_READY"
    if safe:
        return "WARN_ONLY_SAFE_WINDOWS"
    return "HOLD_NO_SAFE_RULE_WINDOWS"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Closed-Loop Window Rule Candidates",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline analysis of existing BEST_WALK full-observation traces. It does not train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Criteria",
        "",
    ]
    for key, value in payload["criteria"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Bucket Summary",
            "",
            "| bucket | windows | vx | single_% | move_env_% | move_single_env_% | single_dvx | stance_dx | stance_abs_dy | pitch_p95 | right_knee_p95 | action_delta_p95 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for bucket, item in payload["summary"]["bucket_summary"].items():
        lines.append(
            f"| {bucket} | {item['windows']} | "
            f"{fmt(item['mean_vx_m_s']['mean'])} | "
            f"{fmt(item['single_support_pct']['mean'])} | "
            f"{fmt(item['moving_in_envelope_pct']['mean'])} | "
            f"{fmt(item['moving_single_in_envelope_pct']['mean'])} | "
            f"{fmt(item['single_future_dvx_0p1s_m_s']['mean'])} | "
            f"{fmt(item['stance_base_dx_mean_m']['mean'])} | "
            f"{fmt(item['stance_base_abs_dy_mean_m']['mean'])} | "
            f"{fmt(item['pitch_target_velocity_p95_rad_s']['mean'])} | "
            f"{fmt(item['right_knee_target_velocity_p95_rad_s']['mean'])} | "
            f"{fmt(item['action_delta_p95']['mean'])} |"
        )
    lines.extend(["", "## By Command Cell", "", "| command_cell | "])
    buckets = sorted(payload["summary"]["bucket_summary"])
    lines[-1] += " | ".join(buckets) + " |"
    lines.append("|---|" + "|".join("---:" for _ in buckets) + "|")
    for command, counts in payload["summary"]["by_command_cell"].items():
        row = [command] + [str(counts.get(bucket, 0)) for bucket in buckets]
        lines.append("| " + " | ".join(row) + " |")
    lines.extend(
        [
            "",
            "## Reason Counts",
            "",
        ]
    )
    for reason, count in payload["summary"]["reason_counts"].items():
        lines.append(f"- {reason}: `{count}`")
    lines.extend(["", "## Fastest Pitch Joint Counts", ""])
    for joint, count in payload["summary"]["fastest_pitch_joint_counts"].items():
        lines.append(f"- {joint}: `{count}`")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `pass_safe_moving_single` windows meet the short-window movement, contact, stability, and pitch-rate gates.",
            "- `reject_high_rate_moving` windows move forward but exceed the pitch-chain target-rate envelope.",
            "- Compare these buckets before building a selector: the desired behavior is not simply more velocity, it is velocity with single support and bounded pitch-chain rate.",
            "- If right-knee or left-knee dominates the high-rate bucket, the next branch should explicitly manage knee target-rate during stance transfer.",
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
    parser.add_argument("--output-md", default="outputs/analysis/CLOSED_LOOP_WINDOW_RULE_CANDIDATES.md")
    parser.add_argument("--output-json", default="outputs/analysis/closed_loop_window_rule_candidates.json")
    parser.add_argument("--window-samples", type=int, default=10)
    parser.add_argument("--stride-samples", type=int, default=2)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--future-ticks", type=int, default=5)
    parser.add_argument("--envelope-high", type=float, default=3.75)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--min-tick-vx", type=float, default=0.04)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-moving-in-envelope-pct", type=float, default=40.0)
    parser.add_argument("--min-moving-single-in-envelope-pct", type=float, default=10.0)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.20)
    parser.add_argument("--max-body-pitch-abs-p95", type=float, default=0.20)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--top-window-limit", type=int, default=20)
    args = parser.parse_args()
    if not args.trace_glob:
        args.trace_glob = ["outputs/analysis/published_policy_command_*_seed*/trace_full_obs_footpos.jsonl"]
    return args


def main() -> int:
    args = parse_args()
    paths: list[Path] = []
    for pattern in args.trace_glob:
        paths.extend(Path(path) for path in glob.glob(str(ROOT / pattern)))
    paths = sorted(set(paths))
    windows: list[dict[str, Any]] = []
    for path in paths:
        rows = read_trace(path)
        for start in range(0, max(len(rows) - args.window_samples + 1, 0), args.stride_samples):
            windows.append(window_metrics(path, rows, start, args))
    summary = summarize_windows(windows)
    payload = {
        "status": status(summary),
        "trace_globs": args.trace_glob,
        "criteria": {
            "window_samples": args.window_samples,
            "stride_samples": args.stride_samples,
            "dt_s": args.dt_s,
            "future_ticks": args.future_ticks,
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
        "summary": summary,
        "top_pass_windows": top_windows(windows, "pass_safe_moving_single", args.top_window_limit),
        "top_high_rate_windows": top_windows(windows, "reject_high_rate_moving", args.top_window_limit),
    }
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={payload['status']}")
    print(f"windows={len(windows)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
