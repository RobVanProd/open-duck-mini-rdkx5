#!/usr/bin/env python3
"""Analyze whether foot-placement teacher push phases create forward impulse.

This is an offline trace analyzer. It reads JSONL traces produced by
probe_foot_placement_mpc_teacher.py and writes compact markdown/JSON summaries.
It does not run simulation, train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from eval_reference_motion_rollout import fmt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "FOOT_PLACEMENT_PUSH_EFFECTIVENESS_ANALYSIS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "foot_placement_push_effectiveness_analysis.json"
PITCH_CHAIN = (2, 3, 4, 11, 12, 13)


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def pct(count: int, total: int) -> float:
    return float(count / total * 100.0) if total else 0.0


def percentile(values: list[float], q: float) -> float | None:
    data = [float(value) for value in values if finite(value)]
    if not data:
        return None
    return float(np.percentile(np.asarray(data, dtype=float), q))


def signed_stats(values: list[float]) -> dict[str, float | None]:
    data = [float(value) for value in values if finite(value)]
    if not data:
        return {"mean": None, "p50": None, "p95": None, "min": None, "max": None}
    return {
        "mean": float(np.mean(data)),
        "p50": float(np.percentile(data, 50)),
        "p95": float(np.percentile(data, 95)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
    }


def read_trace(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def local_vx(record: dict[str, Any]) -> float | None:
    vel = record.get("local_linvel_m_s")
    if isinstance(vel, list) and vel:
        value = vel[0]
        return float(value) if finite(value) else None
    return None


def local_vy(record: dict[str, Any]) -> float | None:
    vel = record.get("local_linvel_m_s")
    if isinstance(vel, list) and len(vel) > 1:
        value = vel[1]
        return float(value) if finite(value) else None
    return None


def contact_label(record: dict[str, Any]) -> str:
    contacts = record.get("foot_contacts")
    if contacts == [1, 1]:
        return "double"
    if contacts == [1, 0]:
        return "left_only"
    if contacts == [0, 1]:
        return "right_only"
    if contacts == [0, 0]:
        return "none"
    return "unknown"


def max_pitch_target_velocity(records: list[dict[str, Any]], index: int, dt_s: float) -> float | None:
    if index <= 0:
        return None
    current = records[index].get("sent_target_rad")
    previous = records[index - 1].get("sent_target_rad")
    if not isinstance(current, list) or not isinstance(previous, list):
        return None
    if len(current) <= max(PITCH_CHAIN) or len(previous) <= max(PITCH_CHAIN):
        return None
    velocities = [
        abs(float(current[joint]) - float(previous[joint])) / dt_s
        for joint in PITCH_CHAIN
        if finite(current[joint]) and finite(previous[joint])
    ]
    return max(velocities) if velocities else None


def analyze_trace(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    records = read_trace(path)
    if not records:
        return {"trace": str(path), "status": "HOLD_EMPTY_TRACE"}

    mode = str(records[0].get("mode", path.parent.name))
    seed = records[0].get("seed")
    lookahead = max(1, int(round(args.lookahead_s / args.dt_s)))
    push_indices = [
        index for index, record in enumerate(records[:-lookahead]) if record.get("push_allowed")
    ]
    nonpush_indices = [
        index for index, record in enumerate(records[:-lookahead]) if not record.get("push_allowed")
    ]

    push_vx = [local_vx(records[index]) for index in push_indices]
    push_vx = [value for value in push_vx if value is not None]
    nonpush_vx = [local_vx(records[index]) for index in nonpush_indices]
    nonpush_vx = [value for value in nonpush_vx if value is not None]
    push_vy_abs = [abs(local_vy(records[index]) or 0.0) for index in push_indices]
    future_deltas = []
    for index in push_indices:
        now = local_vx(records[index])
        future = local_vx(records[index + lookahead])
        if now is not None and future is not None:
            future_deltas.append(float(future - now))

    contact_counts = Counter(contact_label(records[index]) for index in push_indices)
    pitch_target_vel = [
        value
        for index in push_indices
        if (value := max_pitch_target_velocity(records, index, args.dt_s)) is not None
    ]
    forward_scale = [
        float(records[index].get("forward_scale"))
        for index in push_indices
        if finite(records[index].get("forward_scale"))
    ]
    yaw_error = [
        abs(float(records[index].get("body_yaw_error_rad")))
        for index in push_indices
        if finite(records[index].get("body_yaw_error_rad"))
    ]

    failures: list[str] = []
    push_pct = pct(len(push_indices), max(1, len(records) - lookahead))
    delta_mean = float(mean(future_deltas)) if future_deltas else None
    if push_pct < args.min_push_pct:
        failures.append("push_too_rare")
    if delta_mean is None or delta_mean < args.min_forward_delta_m_s:
        failures.append("push_does_not_accelerate")
    if percentile(push_vy_abs, 95) is not None and percentile(push_vy_abs, 95) > args.max_push_vy_abs_p95:
        failures.append("push_lateral_velocity_high")
    if percentile(pitch_target_vel, 95) is not None and percentile(pitch_target_vel, 95) > args.max_pitch_target_velocity_p95:
        failures.append("push_target_velocity_high")

    return {
        "trace": str(path),
        "status": "PASS_PUSH_EFFECTIVE" if not failures else "HOLD_PUSH_INEFFECTIVE",
        "mode": mode,
        "seed": seed,
        "samples": len(records),
        "lookahead_ticks": lookahead,
        "push_samples": len(push_indices),
        "push_allowed_pct": push_pct,
        "push_contact_pct": {
            key: pct(value, len(push_indices)) for key, value in sorted(contact_counts.items())
        },
        "push_vx_m_s": signed_stats(push_vx),
        "nonpush_vx_m_s": signed_stats(nonpush_vx),
        "push_future_vx_delta_m_s": signed_stats(future_deltas),
        "push_vy_abs_m_s": signed_stats(push_vy_abs),
        "push_pitch_target_velocity_rad_s": signed_stats(pitch_target_vel),
        "push_forward_scale": signed_stats(forward_scale),
        "push_yaw_error_abs_rad": signed_stats(yaw_error),
        "failures": failures,
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    usable = [row for row in rows if row.get("samples")]
    statuses = Counter(str(row.get("status", "UNKNOWN")) for row in usable)
    deltas = [
        row["push_future_vx_delta_m_s"]["mean"]
        for row in usable
        if finite(row.get("push_future_vx_delta_m_s", {}).get("mean"))
    ]
    push_pct = [
        row["push_allowed_pct"] for row in usable if finite(row.get("push_allowed_pct"))
    ]
    failure_counts = Counter(
        failure for row in usable for failure in row.get("failures", [])
    )
    return {
        "trace_count": len(rows),
        "usable_trace_count": len(usable),
        "status_counts": dict(sorted(statuses.items())),
        "mean_push_allowed_pct": float(mean(push_pct)) if push_pct else None,
        "mean_push_future_vx_delta_m_s": float(mean(deltas)) if deltas else None,
        "failure_counts": dict(sorted(failure_counts.items())),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    aggregate_row = payload["aggregate"]
    lines = [
        "# Foot-Placement Push Effectiveness Analysis",
        "",
        f"status: `{payload['status']}`",
        f"trace_count: `{aggregate_row['trace_count']}`",
        f"usable_trace_count: `{aggregate_row['usable_trace_count']}`",
        f"lookahead_s: `{payload['lookahead_s']}`",
        "",
        "## Aggregate",
        "",
        f"- mean_push_allowed_pct: `{fmt(aggregate_row['mean_push_allowed_pct'])}`",
        f"- mean_push_future_vx_delta_m_s: `{fmt(aggregate_row['mean_push_future_vx_delta_m_s'])}`",
        f"- status_counts: `{aggregate_row['status_counts']}`",
        f"- failure_counts: `{aggregate_row['failure_counts']}`",
        "",
        "## Per Trace",
        "",
        "| mode | seed | status | push_pct | push_dvx_mean | push_vx_mean | nonpush_vx_mean | push_vy95 | pitch_vel95 | failures |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["traces"]:
        lines.append(
            "| {mode} | {seed} | {status} | {push_pct} | {dvx} | {push_vx} | {nonpush_vx} | {vy95} | {pitch95} | `{failures}` |".format(
                mode=row.get("mode", "NA"),
                seed=row.get("seed", "NA"),
                status=row.get("status", "NA"),
                push_pct=fmt(row.get("push_allowed_pct"), 2),
                dvx=fmt(row.get("push_future_vx_delta_m_s", {}).get("mean")),
                push_vx=fmt(row.get("push_vx_m_s", {}).get("mean")),
                nonpush_vx=fmt(row.get("nonpush_vx_m_s", {}).get("mean")),
                vy95=fmt(row.get("push_vy_abs_m_s", {}).get("p95")),
                pitch95=fmt(row.get("push_pitch_target_velocity_rad_s", {}).get("p95")),
                failures=", ".join(row.get("failures", [])) or "none",
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This analyzes existing traces only; it does not run simulation or training.",
            "- `push_future_vx_delta_m_s` is the local forward velocity change after the configured lookahead.",
            "- If push is frequent but the velocity delta is near zero or negative, the current propulsion primitive is ineffective rather than merely under-scheduled.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace-glob",
        action="append",
        required=True,
        help="Glob for probe JSONL traces. May be provided multiple times.",
    )
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--lookahead-s", type=float, default=0.10)
    parser.add_argument("--min-push-pct", type=float, default=15.0)
    parser.add_argument("--min-forward-delta-m-s", type=float, default=0.005)
    parser.add_argument("--max-push-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-pitch-target-velocity-p95", type=float, default=3.75)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    paths = sorted(
        {
            Path(match)
            for pattern in args.trace_glob
            for match in glob.glob(pattern)
        }
    )
    rows = [analyze_trace(path, args) for path in paths]
    summary = aggregate(rows)
    status = (
        "PASS_PUSH_EFFECTIVE"
        if summary["usable_trace_count"] > 0
        and summary["status_counts"].get("HOLD_PUSH_INEFFECTIVE", 0) == 0
        else "HOLD_PUSH_INEFFECTIVE"
    )
    payload = {
        "status": status,
        "trace_glob": args.trace_glob,
        "lookahead_s": args.lookahead_s,
        "thresholds": {
            "min_push_pct": args.min_push_pct,
            "min_forward_delta_m_s": args.min_forward_delta_m_s,
            "max_push_vy_abs_p95": args.max_push_vy_abs_p95,
            "max_pitch_target_velocity_p95": args.max_pitch_target_velocity_p95,
        },
        "aggregate": summary,
        "traces": rows,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"trace_count={summary['trace_count']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
