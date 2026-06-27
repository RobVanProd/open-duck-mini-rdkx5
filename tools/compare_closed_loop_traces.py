#!/usr/bin/env python3
"""Compare two closed-loop eval trace JSONL files.

This is an offline analysis helper. It does not run simulation, SSH, deploy, or
touch robot runtime state.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable


JOINTS = [
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


def read_trace(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"empty trace: {path}")
    return rows


def finite(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def quantile(values: Iterable[float], q: float) -> float:
    vals = sorted(finite(v) for v in values)
    if not vals:
        return float("nan")
    if len(vals) == 1:
        return vals[0]
    idx = q * (len(vals) - 1)
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return vals[lo]
    frac = idx - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def mean(values: Iterable[float]) -> float:
    vals = [finite(v) for v in values]
    return sum(vals) / len(vals) if vals else float("nan")


def metric(row: dict[str, Any], name: str) -> float:
    if name == "local_vx":
        return finite((row.get("local_linvel_m_s") or [0.0])[0])
    if name == "local_vy":
        return finite((row.get("local_linvel_m_s") or [0.0, 0.0])[1])
    if name == "local_vz":
        return finite((row.get("local_linvel_m_s") or [0.0, 0.0, 0.0])[2])
    if name == "body_pitch":
        return finite(row.get("body_pitch_rad"))
    if name == "base_height":
        return finite(row.get("base_height_m"))
    if name == "base_x":
        return finite(row.get("base_x_m"))
    if name == "base_y":
        return finite(row.get("base_y_m"))
    if name == "reward":
        return finite(row.get("reward"))
    raise KeyError(name)


def summarize_trace(rows: list[dict[str, Any]]) -> dict[str, Any]:
    contacts = [tuple(int(x) for x in (r.get("foot_contacts") or [0, 0])) for r in rows]
    return {
        "samples": len(rows),
        "duration_s": finite(rows[-1].get("time_s")) + 0.02,
        "termination": "done" if bool(rows[-1].get("done")) else "duration_or_truncated",
        "local_vx_mean": mean(metric(r, "local_vx") for r in rows),
        "local_vx_p05": quantile((metric(r, "local_vx") for r in rows), 0.05),
        "local_vx_p95": quantile((metric(r, "local_vx") for r in rows), 0.95),
        "local_vy_abs_p95": quantile((abs(metric(r, "local_vy")) for r in rows), 0.95),
        "body_pitch_abs_p95": quantile((abs(metric(r, "body_pitch")) for r in rows), 0.95),
        "body_pitch_abs_max": max(abs(metric(r, "body_pitch")) for r in rows),
        "base_height_min": min(metric(r, "base_height") for r in rows),
        "base_x_delta": metric(rows[-1], "base_x") - metric(rows[0], "base_x"),
        "base_y_delta": metric(rows[-1], "base_y") - metric(rows[0], "base_y"),
        "double_support_pct": 100.0 * sum(c == (1, 1) for c in contacts) / len(contacts),
        "left_only_pct": 100.0 * sum(c == (1, 0) for c in contacts) / len(contacts),
        "right_only_pct": 100.0 * sum(c == (0, 1) for c in contacts) / len(contacts),
        "no_contact_pct": 100.0 * sum(c == (0, 0) for c in contacts) / len(contacts),
    }


def abs_delta(left: list[float], right: list[float]) -> list[float]:
    return [abs(finite(a) - finite(b)) for a, b in zip(left, right)]


def summarize_common(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> dict[str, Any]:
    n = min(len(left), len(right))
    pairs = list(zip(left[:n], right[:n]))
    metric_names = [
        "local_vx",
        "local_vy",
        "body_pitch",
        "base_height",
        "base_x",
        "base_y",
        "reward",
    ]
    out: dict[str, Any] = {"common_samples": n}
    for name in metric_names:
        diffs = [metric(r, name) - metric(l, name) for l, r in pairs]
        out[f"{name}_delta_mean"] = mean(diffs)
        out[f"{name}_delta_abs_p95"] = quantile((abs(v) for v in diffs), 0.95)
        out[f"{name}_left_mean"] = mean(metric(l, name) for l, _ in pairs)
        out[f"{name}_right_mean"] = mean(metric(r, name) for _, r in pairs)

    first: dict[str, Any] = {}
    thresholds = {
        "local_vx": 0.05,
        "local_vy": 0.05,
        "body_pitch": 0.05,
        "base_height": 0.02,
        "base_x": 0.03,
        "base_y": 0.03,
    }
    for name, threshold in thresholds.items():
        for i, (lrow, rrow) in enumerate(pairs):
            diff = metric(rrow, name) - metric(lrow, name)
            if abs(diff) >= threshold:
                first[name] = {
                    "tick": int(rrow.get("tick", i)),
                    "time_s": finite(rrow.get("time_s")),
                    "left": metric(lrow, name),
                    "right": metric(rrow, name),
                    "delta": diff,
                    "threshold": threshold,
                }
                break
    out["first_divergence"] = first

    joint_rows = []
    for idx, joint in enumerate(JOINTS):
        action_diffs = [abs_delta(l.get("action") or [], r.get("action") or [])[idx] for l, r in pairs]
        sent_diffs = [
            abs_delta(l.get("sent_target_rad") or [], r.get("sent_target_rad") or [])[idx]
            for l, r in pairs
        ]
        actual_diffs = [
            abs_delta(l.get("actual_position_rad") or [], r.get("actual_position_rad") or [])[idx]
            for l, r in pairs
        ]
        joint_rows.append(
            {
                "joint": joint,
                "action_abs_delta_p95": quantile(action_diffs, 0.95),
                "sent_target_abs_delta_p95_rad": quantile(sent_diffs, 0.95),
                "actual_abs_delta_p95_rad": quantile(actual_diffs, 0.95),
                "pitch_chain": joint in PITCH_CHAIN,
            }
        )
    out["joint_deltas"] = joint_rows
    return out


def fmt(value: Any) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return "NA"
        return f"{value:.4f}"
    return str(value)


def write_markdown(
    path: Path,
    left_name: str,
    right_name: str,
    left_path: Path,
    right_path: Path,
    result: dict[str, Any],
) -> None:
    left = result["left"]
    right = result["right"]
    common = result["common"]
    lines = [
        "# Closed-Loop Trace Comparison",
        "",
        "Offline trace comparison. This does not run robot tests, deploy, SSH, or change runtime behavior.",
        "",
        "## Inputs",
        "",
        f"- left: `{left_name}` `{left_path}`",
        f"- right: `{right_name}` `{right_path}`",
        f"- common_samples: `{common['common_samples']}`",
        "",
        "## Trace Summary",
        "",
        "| trace | samples | duration_s | vx_mean | vx_p05 | vx_p95 | abs_vy_p95 | abs_pitch_p95 | base_height_min | base_x_delta | base_y_delta | double_support_pct | left_only_pct | right_only_pct |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, data in [(left_name, left), (right_name, right)]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{name}`",
                    fmt(data["samples"]),
                    fmt(data["duration_s"]),
                    fmt(data["local_vx_mean"]),
                    fmt(data["local_vx_p05"]),
                    fmt(data["local_vx_p95"]),
                    fmt(data["local_vy_abs_p95"]),
                    fmt(data["body_pitch_abs_p95"]),
                    fmt(data["base_height_min"]),
                    fmt(data["base_x_delta"]),
                    fmt(data["base_y_delta"]),
                    fmt(data["double_support_pct"]),
                    fmt(data["left_only_pct"]),
                    fmt(data["right_only_pct"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Common-Window Delta",
            "",
            f"Common window uses the first `{common['common_samples']}` samples from each trace.",
            "",
            "| metric | left_mean | right_mean | right_minus_left_mean | abs_delta_p95 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for name in ["local_vx", "local_vy", "body_pitch", "base_height", "base_x", "base_y", "reward"]:
        lines.append(
            f"| `{name}` | {fmt(common[f'{name}_left_mean'])} | {fmt(common[f'{name}_right_mean'])} | "
            f"{fmt(common[f'{name}_delta_mean'])} | {fmt(common[f'{name}_delta_abs_p95'])} |"
        )
    lines.extend(["", "## First Divergence", "", "| metric | tick | time_s | left | right | delta | threshold |", "|---|---:|---:|---:|---:|---:|---:|"])
    first = common.get("first_divergence") or {}
    for name in ["local_vx", "local_vy", "body_pitch", "base_height", "base_x", "base_y"]:
        item = first.get(name)
        if not item:
            lines.append(f"| `{name}` | NA | NA | NA | NA | NA | NA |")
        else:
            lines.append(
                f"| `{name}` | {item['tick']} | {fmt(item['time_s'])} | {fmt(item['left'])} | "
                f"{fmt(item['right'])} | {fmt(item['delta'])} | {fmt(item['threshold'])} |"
            )
    lines.extend(
        [
            "",
            "## Pitch-Chain Joint Deltas",
            "",
            "| joint | action_abs_delta_p95 | sent_target_abs_delta_p95_rad | actual_abs_delta_p95_rad |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in common["joint_deltas"]:
        if not row["pitch_chain"]:
            continue
        lines.append(
            f"| `{row['joint']}` | {fmt(row['action_abs_delta_p95'])} | "
            f"{fmt(row['sent_target_abs_delta_p95_rad'])} | {fmt(row['actual_abs_delta_p95_rad'])} |"
        )
    lines.append("")
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left-trace", type=Path, required=True)
    parser.add_argument("--right-trace", type=Path, required=True)
    parser.add_argument("--left-name", default="left")
    parser.add_argument("--right-name", default="right")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    left = read_trace(args.left_trace)
    right = read_trace(args.right_trace)
    result = {
        "left_name": args.left_name,
        "right_name": args.right_name,
        "left_trace": str(args.left_trace),
        "right_trace": str(args.right_trace),
        "left": summarize_trace(left),
        "right": summarize_trace(right),
        "common": summarize_common(left, right),
    }
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(args.output_md, args.left_name, args.right_name, args.left_trace, args.right_trace, result)
    if not args.output_json and not args.output_md:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
