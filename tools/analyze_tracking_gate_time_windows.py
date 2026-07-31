#!/usr/bin/env python3
"""Audit compact tracking metrics in fixed contiguous time windows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


JOINT_NAMES = [
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
    "neck_pitch", "head_pitch", "head_yaw", "head_roll", "right_hip_yaw",
    "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
]
PITCH_INDICES = [2, 3, 4, 11, 12, 13]


def summarize(rows: list[dict], command_x: float) -> dict:
    sent = np.asarray([row["sent_target_rad"] for row in rows], dtype=float)
    actual = np.asarray([row["actual_position_rad"] for row in rows], dtype=float)
    tracking = np.abs(sent - actual)
    per_joint = {
        JOINT_NAMES[index]: float(np.percentile(tracking[:, index], 95))
        for index in PITCH_INDICES
    }
    worst_joint = max(per_joint, key=per_joint.get)  # type: ignore[arg-type]
    vx = float(np.mean([row["local_linvel_m_s"][0] for row in rows]))
    return {
        "samples": len(rows),
        "max_pitch_tracking_p95_rad": per_joint[worst_joint],
        "max_pitch_tracking_joint": worst_joint,
        "per_pitch_joint_tracking_p95_rad": per_joint,
        "mean_local_vx_m_s": vx,
        "command_tracking_ratio": vx / command_x if command_x else None,
        "passes_tracking_limit": per_joint[worst_joint] <= 0.20,
    }


def main() -> int:
    args = parse_args()
    rows = [json.loads(line) for line in Path(args.trace_jsonl).read_text().splitlines()]
    windows = []
    for start in range(0, len(rows), args.window_ticks):
        block = rows[start : start + args.window_ticks]
        if len(block) != args.window_ticks:
            break
        windows.append({
            "start_tick": start,
            "end_tick_exclusive": start + args.window_ticks,
            "start_s": start * args.dt_s,
            "end_s": (start + args.window_ticks) * args.dt_s,
            **summarize(block, args.command_x),
        })
    report = {
        "status": "PASS_TRACKING_WINDOW_AUDIT_READY",
        "trace_jsonl": args.trace_jsonl,
        "command_x": args.command_x,
        "window_ticks": args.window_ticks,
        "dt_s": args.dt_s,
        "tracking_limit_rad": 0.20,
        "full_trace": summarize(rows, args.command_x),
        "windows": windows,
        "startup_window_fails": bool(windows and not windows[0]["passes_tracking_limit"]),
        "post_startup_all_pass": bool(windows[1:] and all(row["passes_tracking_limit"] for row in windows[1:])),
        "decision": (
            "Do not change the compact gate from this single-seed audit. Use the result only "
            "to distinguish reset/startup tracking from steady-state tracking and define an "
            "independent gate-validity study before further policy training."
        ),
        "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Tracking Gate Fixed-Window Audit",
        "",
        f"Status: **{report['status']}**",
        "",
        "| window | tracking p95 max | joint | vx | ratio | <=0.20 |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for row in windows:
        lines.append(
            f"| {row['start_s']:.1f}-{row['end_s']:.1f}s | "
            f"{row['max_pitch_tracking_p95_rad']:.4f} | `{row['max_pitch_tracking_joint']}` | "
            f"{row['mean_local_vx_m_s']:.4f} | {row['command_tracking_ratio']:.3f} | "
            f"`{row['passes_tracking_limit']}` |"
        )
    lines += [
        "",
        f"- startup window fails: `{report['startup_window_fails']}`",
        f"- every later complete window passes: `{report['post_startup_all_pass']}`",
        "",
        "## Decision",
        "",
        report["decision"],
        "",
        "No gate, training, deployment, robot, SSH, or GPU change was performed.",
    ]
    Path(args.output_md).write_text("\n".join(lines) + "\n")
    print(report["status"])
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-jsonl", required=True)
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--window-ticks", type=int, default=50)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
