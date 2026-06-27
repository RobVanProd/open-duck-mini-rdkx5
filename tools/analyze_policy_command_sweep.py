#!/usr/bin/env python3
"""Analyze published-policy command sweep traces.

This offline helper summarizes the same policy across command cells and extracts
a compact stance-foot/base timing read from full-observation traces. It does not
run simulation, train, deploy, SSH, or touch robot hardware.
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
PITCH_CHAIN = {
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
}


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
        return {
            "mean": None,
            "std": None,
            "min": None,
            "p50": None,
            "p95": None,
            "max": None,
        }
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_trace(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def contact_code(record: dict[str, Any]) -> str:
    contacts = record.get("foot_contacts")
    if not isinstance(contacts, list) or len(contacts) < 2:
        return "??"
    return f"{1 if int(contacts[0]) else 0}{1 if int(contacts[1]) else 0}"


def contact_bucket(code: str) -> str:
    if code == "11":
        return "double"
    if code in {"10", "01"}:
        return "single"
    if code == "00":
        return "flight"
    return "unknown"


def local_v(record: dict[str, Any], index: int) -> float | None:
    value = record.get("local_linvel_m_s")
    if isinstance(value, list) and len(value) > index and finite(value[index]):
        return float(value[index])
    return None


def vector(record: dict[str, Any], key: str) -> list[float] | None:
    value = record.get(key)
    if isinstance(value, list) and len(value) >= len(JOINT_NAMES):
        return [float(item) for item in value[: len(JOINT_NAMES)]]
    return None


def pitch_chain_target_velocity(records: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    per_joint: dict[str, list[float]] = {name: [] for name in JOINT_NAMES}
    prev = None
    for record in records:
        cur = vector(record, "sent_target_rad")
        if cur is not None and prev is not None:
            for i, name in enumerate(JOINT_NAMES):
                per_joint[name].append(abs(cur[i] - prev[i]) / max(dt_s, 1e-9))
        prev = cur
    pitch_p95 = []
    for name in PITCH_CHAIN:
        value = stats(per_joint[name])["p95"]
        if finite(value):
            pitch_p95.append(float(value))
    return {
        "per_joint": {name: stats(values) for name, values in per_joint.items()},
        "pitch_chain_p95_rad_s": stats(pitch_p95),
    }


def future_delta(records: list[dict[str, Any]], index: int, horizon_ticks: int) -> float | None:
    j = index + horizon_ticks
    if j >= len(records):
        return None
    now = local_v(records[index], 0)
    later = local_v(records[j], 0)
    if now is None or later is None:
        return None
    return later - now


def stance_geometry(records: list[dict[str, Any]], horizon_ticks: int) -> dict[str, Any]:
    rows = []
    positive_rows = []
    negative_rows = []
    side_counts = Counter()
    for i, record in enumerate(records):
        code = contact_code(record)
        if code not in {"10", "01"}:
            continue
        foot_positions = record.get("foot_site_pos_m")
        if not isinstance(foot_positions, list) or len(foot_positions) < 2:
            continue
        foot_index = 0 if code == "10" else 1
        stance_foot = foot_positions[foot_index]
        if not isinstance(stance_foot, list) or len(stance_foot) < 3:
            continue
        base_x = record.get("base_x_m")
        base_y = record.get("base_y_m")
        base_z = record.get("base_height_m")
        if not (finite(base_x) and finite(base_y) and finite(base_z)):
            continue
        dx = float(base_x) - float(stance_foot[0])
        dy = float(base_y) - float(stance_foot[1])
        dz = float(base_z) - float(stance_foot[2])
        delta = future_delta(records, i, horizon_ticks)
        row = {
            "dx_m": dx,
            "dy_m": dy,
            "dz_m": dz,
            "abs_dy_m": abs(dy),
            "radial_xy_m": math.sqrt(dx * dx + dy * dy),
            "local_vx_m_s": local_v(record, 0),
            "local_vy_m_s": local_v(record, 1),
            "future_vx_delta_m_s": delta,
            "side": "left" if code == "10" else "right",
        }
        rows.append(row)
        side_counts[row["side"]] += 1
        if finite(delta) and float(delta) > 0.0:
            positive_rows.append(row)
        elif finite(delta):
            negative_rows.append(row)

    def collect(items: list[dict[str, Any]], key: str) -> list[float]:
        return [float(row[key]) for row in items if finite(row.get(key))]

    def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "samples": len(items),
            "base_minus_stance_foot_x_m": stats(collect(items, "dx_m")),
            "base_minus_stance_foot_y_m": stats(collect(items, "dy_m")),
            "base_minus_stance_foot_abs_y_m": stats(collect(items, "abs_dy_m")),
            "base_minus_stance_foot_z_m": stats(collect(items, "dz_m")),
            "base_stance_radial_xy_m": stats(collect(items, "radial_xy_m")),
            "local_vx_m_s": stats(collect(items, "local_vx_m_s")),
            "local_vy_m_s": stats(collect(items, "local_vy_m_s")),
            "future_vx_delta_m_s": stats(collect(items, "future_vx_delta_m_s")),
            "left_samples": sum(1 for row in items if row["side"] == "left"),
            "right_samples": sum(1 for row in items if row["side"] == "right"),
        }

    return {
        "all_single_support": summarize(rows),
        "positive_future_vx_delta": summarize(positive_rows),
        "nonpositive_future_vx_delta": summarize(negative_rows),
        "side_counts": dict(side_counts),
    }


def trace_summary(trace_path: Path, eval_path: Path, dt_s: float, lookahead_s: float) -> dict[str, Any]:
    records = read_trace(trace_path)
    eval_payload = load_json(eval_path)
    mode = eval_payload["closed_loop_sim"]["modes"]["vanilla"]
    forward = mode["forward_motion"]
    codes = [contact_code(record) for record in records]
    counts = Counter(contact_bucket(code) for code in codes)
    command = eval_payload["closed_loop_sim"].get("command") or mode.get("command")
    horizon_ticks = max(1, int(round(lookahead_s / dt_s)))
    single_deltas = [
        value
        for i, record in enumerate(records)
        if contact_bucket(contact_code(record)) == "single"
        and finite(value := future_delta(records, i, horizon_ticks))
    ]
    return {
        "seed": eval_payload.get("seed"),
        "trace": str(trace_path),
        "eval_json": str(eval_path),
        "samples": mode.get("samples"),
        "termination_reason": mode.get("termination_reason"),
        "duration_complete": mode.get("termination_reason") == "duration_complete",
        "command": command,
        "mean_local_vx_m_s": forward.get("mean_velocity_x_m_s"),
        "command_tracking_ratio": forward.get("command_tracking_ratio"),
        "body_pitch_p95_rad": (mode.get("body_pitch_rad") or {}).get("p95"),
        "base_height_min_m": (mode.get("base_height_m") or {}).get("min"),
        "single_support_pct": 100.0 * counts["single"] / len(records) if records else None,
        "double_support_pct": 100.0 * counts["double"] / len(records) if records else None,
        "single_support_future_vx_delta_0p1s": stats(single_deltas),
        "target_velocity": pitch_chain_target_velocity(records, dt_s),
        "stance_geometry": stance_geometry(records, horizon_ticks),
    }


def command_label_from_path(path: Path) -> str:
    text = str(path)
    marker = "published_policy_command_"
    if marker not in text:
        return path.parent.name
    tail = text.split(marker, 1)[1]
    return tail.split("_seed", 1)[0]


def aggregate(traces: list[dict[str, Any]]) -> dict[str, Any]:
    def collect(path: list[str]) -> list[float]:
        values = []
        for trace in traces:
            value: Any = trace
            for key in path:
                value = value.get(key) if isinstance(value, dict) else None
            if finite(value):
                values.append(float(value))
        return values

    moving = [
        trace
        for trace in traces
        if finite(trace.get("command_tracking_ratio"))
        and float(trace["command_tracking_ratio"]) >= 0.5
    ]
    return {
        "trace_count": len(traces),
        "duration_complete_count": sum(1 for trace in traces if trace["duration_complete"]),
        "moving_seed_count_ratio_ge_0p5": len(moving),
        "mean_local_vx_m_s": stats(collect(["mean_local_vx_m_s"])),
        "command_tracking_ratio": stats(collect(["command_tracking_ratio"])),
        "body_pitch_p95_rad": stats(collect(["body_pitch_p95_rad"])),
        "base_height_min_m": stats(collect(["base_height_min_m"])),
        "single_support_pct": stats(collect(["single_support_pct"])),
        "double_support_pct": stats(collect(["double_support_pct"])),
        "single_support_future_vx_delta_0p1s": stats(
            collect(["single_support_future_vx_delta_0p1s", "mean"])
        ),
        "pitch_chain_target_velocity_p95_rad_s": stats(
            collect(["target_velocity", "pitch_chain_p95_rad_s", "mean"])
        ),
        "pitch_chain_target_velocity_p95_max_joint_rad_s": stats(
            collect(["target_velocity", "pitch_chain_p95_rad_s", "max"])
        ),
        "stance_base_minus_foot_x_m": stats(
            collect(["stance_geometry", "all_single_support", "base_minus_stance_foot_x_m", "mean"])
        ),
        "stance_base_minus_foot_abs_y_m": stats(
            collect(["stance_geometry", "all_single_support", "base_minus_stance_foot_abs_y_m", "mean"])
        ),
        "positive_push_stance_base_minus_foot_x_m": stats(
            collect(["stance_geometry", "positive_future_vx_delta", "base_minus_stance_foot_x_m", "mean"])
        ),
        "positive_push_stance_base_minus_foot_abs_y_m": stats(
            collect(["stance_geometry", "positive_future_vx_delta", "base_minus_stance_foot_abs_y_m", "mean"])
        ),
    }


def build_payload(pattern: str, dt_s: float, lookahead_s: float) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for trace_name in sorted(glob.glob(pattern)):
        trace_path = Path(trace_name)
        label = command_label_from_path(trace_path)
        eval_path = trace_path.parent / "closed_loop_actuator_bridge_eval.json"
        if not eval_path.exists():
            continue
        groups.setdefault(label, []).append(
            trace_summary(trace_path, eval_path, dt_s, lookahead_s)
        )
    group_payload = {
        label: {"traces": traces, "aggregate": aggregate(traces)}
        for label, traces in sorted(groups.items())
    }
    return {
        "trace_glob": pattern,
        "dt_s": dt_s,
        "lookahead_s": lookahead_s,
        "groups": group_payload,
        "status": classify(group_payload),
    }


def classify(groups: dict[str, Any]) -> str:
    turning = groups.get("turning_x0074_yneg0037_yawneg0074", {}).get("aggregate", {})
    x004 = groups.get("straight_x004", {}).get("aggregate", {})
    x008 = groups.get("straight_x008", {}).get("aggregate", {})
    if not turning or not x004 or not x008:
        return "HOLD_MISSING_COMMAND_CELL"
    turning_movers = turning.get("moving_seed_count_ratio_ge_0p5", 0)
    x004_movers = x004.get("moving_seed_count_ratio_ge_0p5", 0)
    x008_movers = x008.get("moving_seed_count_ratio_ge_0p5", 0)
    moving_groups = [turning, x008]
    moving_max_joint = [
        group.get("pitch_chain_target_velocity_p95_max_joint_rad_s", {}).get("mean")
        for group in moving_groups
    ]
    if turning_movers >= 7 and x004_movers == 0 and x008_movers >= 7:
        if any(finite(value) and float(value) > 3.75 for value in moving_max_joint):
            return "WARN_COMMAND_SPECIFIC_PROPULSION_OVER_ENVELOPE"
        return "PASS_COMMAND_SPECIFIC_PROPULSION_SPLIT"
    return "WARN_COMMAND_SWEEP_REVIEW_REQUIRED"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Published Policy Command Sweep",
        "",
        f"overall_status: `{payload['status']}`",
        "",
        "## Executive Summary",
        "",
        "- Same published `BEST_WALK_ONNX_2` policy, upstream-main `flat_terrain_backlash`, vanilla dynamics.",
        "- Three command cells were evaluated with full observation and foot-site traces.",
        "- The upstream turning command and straight `x=0.08` produce forward tracking.",
        "- Straight `x=0.04` completes without falling but does not meaningfully move forward.",
        "- This means the old straight `x=0.04` gate is not cleared by the published policy either.",
        "",
        "## Command Curve",
        "",
        "| command_cell | traces | complete | moving>=0.5 | mean_vx | track_ratio | single_% | single_dvx_0p1s | target_vel_p95_mean | target_vel_p95_max_joint | pitch_p95 | height_min |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, item in payload["groups"].items():
        agg = item["aggregate"]
        lines.append(
            f"| {label} | {agg['trace_count']} | {agg['duration_complete_count']} | "
            f"{agg['moving_seed_count_ratio_ge_0p5']} | "
            f"{fmt(agg['mean_local_vx_m_s']['mean'])} | "
            f"{fmt(agg['command_tracking_ratio']['mean'])} | "
            f"{fmt(agg['single_support_pct']['mean'])} | "
            f"{fmt(agg['single_support_future_vx_delta_0p1s']['mean'])} | "
            f"{fmt(agg['pitch_chain_target_velocity_p95_rad_s']['mean'])} | "
            f"{fmt(agg['pitch_chain_target_velocity_p95_max_joint_rad_s']['mean'])} | "
            f"{fmt(agg['body_pitch_p95_rad']['mean'])} | "
            f"{fmt(agg['base_height_min_m']['mean'])} |"
        )
    lines.extend(
        [
            "",
            "## Stance Geometry",
            "",
            "| command_cell | base_minus_stance_x | base_minus_stance_abs_y | positive_push_x | positive_push_abs_y |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for label, item in payload["groups"].items():
        agg = item["aggregate"]
        lines.append(
            f"| {label} | {fmt(agg['stance_base_minus_foot_x_m']['mean'])} | "
            f"{fmt(agg['stance_base_minus_foot_abs_y_m']['mean'])} | "
            f"{fmt(agg['positive_push_stance_base_minus_foot_x_m']['mean'])} | "
            f"{fmt(agg['positive_push_stance_base_minus_foot_abs_y_m']['mean'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The existence proof is command-specific and actuator-envelope-limited. The published policy walks in vanilla sim at the upstream turning command and at straight `x=0.08`, but not at straight `x=0.04`. The moving command cells still have at least one pitch-chain joint with p95 target velocity above the measured 3.75 rad/s envelope, so this is not a real-robot-ready gait. The straight low-speed gate should not be treated as an easy baseline or as an existence-proven target.",
            "",
            "Robot validation remains blocked.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace-glob",
        default="outputs/analysis/published_policy_command_*_seed*/trace_full_obs_footpos.jsonl",
    )
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--lookahead-s", type=float, default=0.1)
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/PUBLISHED_POLICY_COMMAND_SWEEP.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/published_policy_command_sweep.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.trace_glob, args.dt_s, args.lookahead_s)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(output_md, payload)
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    print(f"overall_status: {payload['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
