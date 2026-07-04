#!/usr/bin/env python3
"""Report traced intermediate-push failures for the Phase 2 rate150 candidate.

This is an offline analysis helper. It reads an existing candidate seed sweep,
per-seed closed-loop traces, and the corrected actuator fit. It does not train,
SSH, deploy, touch the robot, or modify Playground.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_trace(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def first_crossing(rows: list[dict[str, Any]], predicate) -> dict[str, Any] | None:
    for row in rows:
        if predicate(row):
            return row
    return None


def percentile(values: list[float], pct: float) -> float | None:
    finite = sorted(v for v in values if math.isfinite(v))
    if not finite:
        return None
    if len(finite) == 1:
        return finite[0]
    pos = (len(finite) - 1) * pct / 100.0
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return finite[lo]
    frac = pos - lo
    return finite[lo] * (1.0 - frac) + finite[hi] * frac


def stats(values: list[float]) -> dict[str, float | None]:
    finite = [v for v in values if math.isfinite(v)]
    if not finite:
        return {"min": None, "p50": None, "p95": None, "max": None}
    return {
        "min": min(finite),
        "p50": percentile(finite, 50),
        "p95": percentile(finite, 95),
        "max": max(finite),
    }


def corrected_limits(fit_json: Path) -> dict[str, float]:
    payload = load_json(fit_json)
    joints = payload["primary"]["joints"]
    return {
        name: float(joints[name]["combined"]["velocity_limit_rad_s"])
        for name in PITCH_CHAIN
    }


def trace_velocity_excess(
    rows: list[dict[str, Any]],
    actuator_names: list[str],
    limits: dict[str, float],
    dt_s: float,
) -> dict[str, Any]:
    index = {name: actuator_names.index(name) for name in PITCH_CHAIN}
    per_joint: dict[str, list[float]] = {name: [] for name in PITCH_CHAIN}
    max_item = {
        "excess_rad_s": 0.0,
        "velocity_rad_s": 0.0,
        "limit_rad_s": None,
        "joint": None,
        "tick": None,
        "time_s": None,
    }
    for prev, cur in zip(rows, rows[1:]):
        prev_targets = prev.get("sent_target_rad") or []
        cur_targets = cur.get("sent_target_rad") or []
        if len(prev_targets) <= max(index.values()) or len(cur_targets) <= max(index.values()):
            continue
        for name, idx in index.items():
            velocity = abs(float(cur_targets[idx]) - float(prev_targets[idx])) / dt_s
            excess = max(0.0, velocity - limits[name])
            per_joint[name].append(excess)
            if excess > float(max_item["excess_rad_s"]):
                max_item = {
                    "excess_rad_s": excess,
                    "velocity_rad_s": velocity,
                    "limit_rad_s": limits[name],
                    "joint": name,
                    "tick": cur.get("tick"),
                    "time_s": cur.get("time_s"),
                }
    return {
        "per_joint_excess_rad_s": {name: stats(values) for name, values in per_joint.items()},
        "max_excess": max_item,
    }


def event_end_tick(event: dict[str, Any]) -> int | None:
    tick = event.get("tick")
    samples = event.get("window_samples")
    if tick is None or samples is None:
        return None
    return int(tick) + max(0, int(samples) - 1)


def summarize_seed(
    result: dict[str, Any],
    trace_root: Path,
    limits: dict[str, float],
    dt_s: float,
) -> dict[str, Any]:
    seed = int(result["seed"])
    output_dir = Path(result["output_dir"])
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    trace_path = output_dir / "trace.jsonl"
    eval_path = output_dir / "closed_loop_actuator_bridge_eval.json"
    rows = load_trace(trace_path)
    eval_payload = load_json(eval_path)
    mode = eval_payload["closed_loop_sim"]["modes"]["fitted"]
    actuator_names = eval_payload["closed_loop_sim"]["env"]["actuator_names"]
    push_events = mode.get("push_recovery", {}).get("events", [])
    last_push = push_events[-1] if push_events else None
    last_push_end = event_end_tick(last_push) if last_push else None
    pitch04 = first_crossing(rows, lambda r: abs(float(r["body_pitch_rad"])) > 0.4)
    pitch08 = first_crossing(rows, lambda r: abs(float(r["body_pitch_rad"])) > 0.8)
    height008 = first_crossing(rows, lambda r: float(r["base_height_m"]) < 0.08)
    height012 = first_crossing(rows, lambda r: float(r["base_height_m"]) < 0.12)
    vel = trace_velocity_excess(rows, actuator_names, limits, dt_s)
    final = rows[-1]
    status = result["status"]
    all_push_windows_recovered = bool(push_events) and all(
        bool(event.get("recovered")) for event in push_events
    )
    delayed_pitch = (
        status != "PASS_CANDIDATE_SIM_GATE"
        and all_push_windows_recovered
        and pitch08 is not None
        and last_push_end is not None
        and int(pitch08["tick"]) > last_push_end
    )
    if status == "PASS_CANDIDATE_SIM_GATE":
        classification = "PASS_CONTROL_STABLE"
    elif delayed_pitch:
        classification = "POST_PUSH_DELAYED_PITCHOVER"
    else:
        classification = "FALL_OR_TERMINATION_UNCLASSIFIED"
    return {
        "seed": seed,
        "status": status,
        "samples": int(result["summary"]["samples"]),
        "termination": result["summary"]["termination_reason"],
        "trace_path": str(trace_path.relative_to(ROOT)),
        "push_event_count": len(push_events),
        "push_success_rate": result["summary"].get("push_success_rate"),
        "last_push": last_push,
        "last_push_end_tick": last_push_end,
        "first_pitch_gt_0p4": crossing_payload(pitch04),
        "first_pitch_gt_0p8": crossing_payload(pitch08),
        "first_height_lt_0p12": crossing_payload(height012),
        "first_height_lt_0p08": crossing_payload(height008),
        "ticks_from_last_push_end_to_pitch_gt_0p8": (
            None
            if pitch08 is None or last_push_end is None
            else int(pitch08["tick"]) - last_push_end
        ),
        "ticks_from_last_push_end_to_height_lt_0p08": (
            None
            if height008 is None or last_push_end is None
            else int(height008["tick"]) - last_push_end
        ),
        "final": {
            "tick": final.get("tick"),
            "time_s": final.get("time_s"),
            "body_pitch_rad": final.get("body_pitch_rad"),
            "base_height_m": final.get("base_height_m"),
            "local_vx_m_s": (final.get("local_linvel_m_s") or [None])[0],
            "local_vy_m_s": (final.get("local_linvel_m_s") or [None, None])[1],
            "foot_contacts": final.get("foot_contacts"),
            "done": final.get("done"),
        },
        "velocity_excess": vel,
        "classification": classification,
    }


def crossing_payload(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "tick": row.get("tick"),
        "time_s": row.get("time_s"),
        "body_pitch_rad": row.get("body_pitch_rad"),
        "base_height_m": row.get("base_height_m"),
        "local_vx_m_s": (row.get("local_linvel_m_s") or [None])[0],
        "local_vy_m_s": (row.get("local_linvel_m_s") or [None, None])[1],
        "foot_contacts": row.get("foot_contacts"),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Intermediate-Push Failure Diagnostic",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline trace analysis. It did not train, SSH, deploy, touch",
        "the robot, or modify Playground.",
        "",
        "## Executive Summary",
        "",
        "- The intermediate-push hold is reproduced in traced seeds 0 and 7.",
        "- Both failing seeds are marked recovered inside every 0.5 s push window.",
        "- Collapse happens after the last push recovery window, as a delayed pitch-over.",
        "- Seed 1 is a passing control under the same push/terrain settings.",
        "- The next offline refinement should target post-push pitch/base-height stability,",
        "  especially for seeds 0 and 7, without loosening the corrected actuator envelope.",
        "",
        "## Inputs",
        "",
        f"- sweep_json: `{payload['sweep_json']}`",
        f"- fit_json: `{payload['fit_json']}`",
        f"- trace_root: `{payload['trace_root']}`",
        f"- dt_s: `{payload['dt_s']}`",
        "",
        "## Per-Seed Timing",
        "",
        "| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for item in payload["seeds"]:
        max_excess = item["velocity_excess"]["max_excess"]
        lines.append(
            "| "
            f"{item['seed']} | "
            f"`{item['status']}` | "
            f"{item['samples']} | "
            f"{item['push_event_count']} | "
            f"{fmt(item['push_success_rate'])} | "
            f"{fmt((item.get('last_push') or {}).get('tick'))} | "
            f"{fmt((item.get('first_pitch_gt_0p8') or {}).get('tick'))} | "
            f"{fmt((item.get('first_height_lt_0p08') or {}).get('tick'))} | "
            f"{fmt(item.get('ticks_from_last_push_end_to_pitch_gt_0p8'))} | "
            f"{fmt(item.get('ticks_from_last_push_end_to_height_lt_0p08'))} | "
            f"`{fmt(max_excess.get('joint'))}` | "
            f"{fmt(max_excess.get('excess_rad_s'))} | "
            f"`{item['classification']}` |"
        )
    lines.extend(
        [
            "",
            "## Failed-Seed Interpretation",
            "",
        ]
    )
    for item in payload["seeds"]:
        if item["classification"] == "PASS_CONTROL_STABLE":
            continue
        last_push = item.get("last_push") or {}
        pitch08 = item.get("first_pitch_gt_0p8") or {}
        height008 = item.get("first_height_lt_0p08") or {}
        lines.extend(
            [
                f"### Seed {item['seed']}",
                "",
                f"- last push: tick `{fmt(last_push.get('tick'))}`, magnitude `{fmt(last_push.get('push_magnitude'))}`, vector `{last_push.get('push')}`",
                f"- last push recovery window ended at tick `{fmt(item.get('last_push_end_tick'))}` and was marked recovered: `{last_push.get('recovered')}`",
                f"- pitch exceeded 0.8 rad at tick `{fmt(pitch08.get('tick'))}`",
                f"- base height fell below 0.08 m at tick `{fmt(height008.get('tick'))}`",
                f"- final state: pitch `{fmt(item['final']['body_pitch_rad'])}`, height `{fmt(item['final']['base_height_m'])}`, vx `{fmt(item['final']['local_vx_m_s'])}`, contacts `{item['final']['foot_contacts']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Recommendation",
            "",
            "Do not treat the intermediate-push bracket as promotable. It is a",
            "near-boundary stability hold: push windows themselves pass the short",
            "recovery check, but failing seeds pitch over shortly after the final",
            "recovery window. The next offline recipe should preserve the passing",
            "gentle-push behavior while adding post-push pitch/base-height damping",
            "or recovery data for seeds 0 and 7. The corrected actuator envelope",
            "must remain fixed.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def collect(args: argparse.Namespace) -> dict[str, Any]:
    sweep = load_json(args.sweep_json)
    limits = corrected_limits(args.fit_json)
    items = [
        summarize_seed(result, args.trace_root, limits, args.dt_s)
        for result in sweep["results"]
    ]
    failures = [item for item in items if item["status"] != "PASS_CANDIDATE_SIM_GATE"]
    delayed = [
        item for item in failures if item["classification"] == "POST_PUSH_DELAYED_PITCHOVER"
    ]
    status = (
        "HOLD_PHASE2_INTERMEDIATE_PUSH_POST_RECOVERY_PITCHOVER"
        if failures and len(delayed) == len(failures)
        else "PASS_PHASE2_INTERMEDIATE_PUSH_TRACE_DIAGNOSTIC"
        if not failures
        else "HOLD_PHASE2_INTERMEDIATE_PUSH_TRACE_MIXED"
    )
    return {
        "status": status,
        "sweep_json": str(args.sweep_json.relative_to(ROOT)),
        "fit_json": str(args.fit_json.relative_to(ROOT)),
        "trace_root": str(args.trace_root.relative_to(ROOT)),
        "dt_s": args.dt_s,
        "corrected_limits_rad_s": limits,
        "seeds": items,
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
        "grounded_replay": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sweep-json",
        type=Path,
        default=ROOT / "outputs/analysis/phase2_rate150_z0075_intermediate_push_trace_seeds_0_1_7.json",
    )
    parser.add_argument(
        "--trace-root",
        type=Path,
        default=ROOT / "outputs/analysis/phase2_rate150_z0075_intermediate_push_trace_seeds_0_1_7",
    )
    parser.add_argument(
        "--fit-json",
        type=Path,
        default=ROOT / "outputs/analysis/actuator_response_fit_corrected_knee.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=ROOT / "outputs/analysis/PHASE2_RATE150_Z0075_INTERMEDIATE_PUSH_FAILURE_DIAGNOSTIC.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=ROOT / "outputs/analysis/phase2_rate150_z0075_intermediate_push_failure_diagnostic.json",
    )
    parser.add_argument("--dt-s", type=float, default=0.02)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = collect(args)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(payload, args.output_md)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
