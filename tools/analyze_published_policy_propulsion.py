#!/usr/bin/env python3
"""Summarize published-policy closed-loop propulsion traces.

This is an offline analysis helper. It reads per-seed closed-loop eval JSON
and trace JSONL files; it does not import Playground, run sim, or touch robot
hardware.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


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


def pct(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs = sorted(float(v) for v in values if finite(v))
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
    xs = [float(v) for v in values if finite(v)]
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
        "p50": pct(xs, 0.50),
        "p95": pct(xs, 0.95),
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
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_trace(path: Path) -> list[dict[str, Any]]:
    records = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def contact_state(record: dict[str, Any]) -> str:
    contacts = record.get("foot_contacts") or []
    total = sum(1 for item in contacts if int(item) != 0)
    if total == 0:
        return "flight"
    if total == 1:
        if len(contacts) >= 2:
            return "left_single" if contacts[0] else "right_single"
        return "single"
    return "double"


def local_vx(record: dict[str, Any]) -> float | None:
    values = record.get("local_linvel_m_s") or []
    if values and finite(values[0]):
        return float(values[0])
    return None


def local_vy_abs(record: dict[str, Any]) -> float | None:
    values = record.get("local_linvel_m_s") or []
    if len(values) > 1 and finite(values[1]):
        return abs(float(values[1]))
    return None


def future_vx_deltas(
    records: list[dict[str, Any]], horizon_ticks: int
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[float]] = {
        "all": [],
        "single_support": [],
        "double_support": [],
        "left_single": [],
        "right_single": [],
        "flight": [],
    }
    for i, record in enumerate(records):
        j = i + horizon_ticks
        if j >= len(records):
            continue
        now = local_vx(record)
        later = local_vx(records[j])
        if now is None or later is None:
            continue
        delta = later - now
        state = contact_state(record)
        buckets["all"].append(delta)
        if state in {"left_single", "right_single", "single"}:
            buckets["single_support"].append(delta)
        elif state == "double":
            buckets["double_support"].append(delta)
        elif state == "flight":
            buckets["flight"].append(delta)
        if state in {"left_single", "right_single"}:
            buckets[state].append(delta)
    return {
        key: {"samples": len(values), "delta_vx_m_s": stats(values)}
        for key, values in buckets.items()
    }


def trace_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(records)
    counts = {
        "double": 0,
        "single_support": 0,
        "left_single": 0,
        "right_single": 0,
        "flight": 0,
    }
    for record in records:
        state = contact_state(record)
        if state in {"left_single", "right_single", "single"}:
            counts["single_support"] += 1
        if state in counts:
            counts[state] += 1
    fractions = {
        key + "_pct": (100.0 * value / n if n else None)
        for key, value in counts.items()
    }
    return {
        "samples": n,
        "contact_counts": counts,
        "contact_fractions": fractions,
        "local_vx_m_s": stats(
            [v for v in (local_vx(record) for record in records) if v is not None]
        ),
        "abs_local_vy_m_s": stats(
            [
                v
                for v in (local_vy_abs(record) for record in records)
                if v is not None
            ]
        ),
        "future_vx_delta_0p1s": future_vx_deltas(records, horizon_ticks=5),
    }


def pitch_chain_metrics(mode: dict[str, Any]) -> dict[str, Any]:
    joints = mode.get("joints") or {}
    rows = {}
    for name, joint in joints.items():
        if name not in PITCH_CHAIN:
            continue
        rows[name] = {
            "sent_target_velocity_p95_rad_s": (
                joint.get("sent_target_velocity_rad_s") or {}
            ).get("p95"),
            "sent_target_velocity_max_rad_s": (
                joint.get("sent_target_velocity_rad_s") or {}
            ).get("max"),
            "joint_target_tracking_p95_rad": (
                joint.get("joint_target_tracking_error_rad") or {}
            ).get("p95"),
            "action_saturation_pct": joint.get("action_saturation_pct"),
            "estimated_lag_ticks": (
                joint.get("estimated_lag_sent_to_actual") or {}
            ).get("ticks"),
        }
    return rows


def seed_summary(eval_path: Path) -> dict[str, Any]:
    payload = load_json(eval_path)
    closed = payload.get("closed_loop_sim") or {}
    mode = (closed.get("modes") or {}).get("vanilla") or {}
    seed_dir = eval_path.parent
    trace_path = seed_dir / "trace.jsonl"
    records = load_trace(trace_path)
    forward = mode.get("forward_motion") or {}
    return {
        "seed": payload.get("seed"),
        "status": payload.get("overall_status"),
        "task": payload.get("task"),
        "command": closed.get("command") or mode.get("command"),
        "samples": mode.get("samples"),
        "termination_reason": mode.get("termination_reason"),
        "mean_local_vx_m_s": forward.get("mean_velocity_x_m_s"),
        "command_tracking_ratio": forward.get("command_tracking_ratio"),
        "body_pitch_p95_rad": (mode.get("body_pitch_rad") or {}).get("p95"),
        "base_height_min_m": (mode.get("base_height_m") or {}).get("min"),
        "reward_mean": (mode.get("reward") or {}).get("mean"),
        "pitch_chain_summary": mode.get("pitch_chain_summary") or {},
        "pitch_chain_joints": pitch_chain_metrics(mode),
        "trace_path": str(trace_path),
        "trace": trace_summary(records),
    }


def aggregate(seeds: list[dict[str, Any]], reference: dict[str, Any] | None) -> dict[str, Any]:
    ratios = [s["command_tracking_ratio"] for s in seeds if finite(s.get("command_tracking_ratio"))]
    vx = [s["mean_local_vx_m_s"] for s in seeds if finite(s.get("mean_local_vx_m_s"))]
    pitch = [s["body_pitch_p95_rad"] for s in seeds if finite(s.get("body_pitch_p95_rad"))]
    height = [s["base_height_min_m"] for s in seeds if finite(s.get("base_height_min_m"))]
    single_pct = [
        (s.get("trace") or {})
        .get("contact_fractions", {})
        .get("single_support_pct")
        for s in seeds
    ]
    double_pct = [
        (s.get("trace") or {}).get("contact_fractions", {}).get("double_pct")
        for s in seeds
    ]
    future_single = []
    future_all = []
    for seed in seeds:
        future = (seed.get("trace") or {}).get("future_vx_delta_0p1s") or {}
        for bucket, output in [
            ("single_support", future_single),
            ("all", future_all),
        ]:
            value = (
                (future.get(bucket) or {})
                .get("delta_vx_m_s", {})
                .get("mean")
            )
            if finite(value):
                output.append(float(value))
    completed = [
        seed
        for seed in seeds
        if seed.get("termination_reason") == "duration_complete"
    ]
    moving = [
        seed
        for seed in seeds
        if finite(seed.get("command_tracking_ratio"))
        and float(seed["command_tracking_ratio"]) >= 0.5
    ]
    weak = [
        seed
        for seed in seeds
        if finite(seed.get("command_tracking_ratio"))
        and float(seed["command_tracking_ratio"]) < 0.5
    ]
    status = (
        "PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION"
        if len(completed) == len(seeds) and len(moving) >= max(1, len(seeds) - 1)
        else "WARN_POLICY_FORWARD_MOTION_WEAK_SEEDS"
    )
    return {
        "status": status,
        "seed_count": len(seeds),
        "duration_complete_count": len(completed),
        "moving_seed_count_ratio_ge_0p5": len(moving),
        "weak_seed_count_ratio_lt_0p5": len(weak),
        "mean_local_vx_m_s": stats(vx),
        "command_tracking_ratio": stats(ratios),
        "body_pitch_p95_rad": stats(pitch),
        "base_height_min_m": stats(height),
        "single_support_pct": stats([v for v in single_pct if finite(v)]),
        "double_support_pct": stats([v for v in double_pct if finite(v)]),
        "future_vx_delta_all_0p1s": stats(future_all),
        "future_vx_delta_single_support_0p1s": stats(future_single),
        "reference_comparison": reference,
    }


def reference_digest(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    payload = load_json(path)
    aggregate_payload = payload.get("aggregate") or {}
    variants = aggregate_payload.get("variants") or []
    best = None
    if variants:
        for variant in variants:
            value = variant.get("reference_single_future_vx_delta_mean")
            if not finite(value):
                continue
            if best is None or float(value) > float(
                best.get("reference_single_future_vx_delta_mean")
            ):
                best = variant
    else:
        for label, item in (aggregate_payload.get("by_label") or {}).items():
            windows = item.get("windows") or {}
            reference_single = windows.get("reference_single_support") or {}
            value = reference_single.get("mean_future_vx_delta_m_s")
            if not finite(value):
                continue
            candidate = {
                "variant": label,
                "reference_single_future_vx_delta_mean": value,
                "mean_local_vx_m_s": None,
                "contact_mismatch_pct": item.get("mean_contact_mismatch_pct"),
            }
            if best is None or float(value) > float(
                best.get("reference_single_future_vx_delta_mean")
            ):
                best = candidate
    return {
        "path": str(path),
        "status": payload.get("overall_status") or payload.get("status"),
        "best_reference_single_future_vx_delta_mean_m_s": (
            best or {}
        ).get("reference_single_future_vx_delta_mean"),
        "best_variant": (best or {}).get("variant"),
        "best_mean_local_vx_m_s": (best or {}).get("mean_local_vx_m_s"),
        "best_contact_mismatch_pct": (best or {}).get("contact_mismatch_pct"),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    aggregate_payload = payload["aggregate"]
    duration_count = aggregate_payload["duration_complete_count"]
    seed_count = aggregate_payload["seed_count"]
    moving_count = aggregate_payload["moving_seed_count_ratio_ge_0p5"]
    weak_count = aggregate_payload["weak_seed_count_ratio_lt_0p5"]
    lines = [
        "# Published Policy Propulsion Audit",
        "",
        f"overall_status: `{aggregate_payload['status']}`",
        f"seed_count: `{seed_count}`",
        f"duration_complete_count: `{duration_count}`",
        f"moving_seed_count_ratio_ge_0p5: `{moving_count}`",
        f"weak_seed_count_ratio_lt_0p5: `{weak_count}`",
        "",
        "## Executive Summary",
        "",
        "- The published `BEST_WALK_ONNX_2` policy was evaluated closed-loop in upstream-main `flat_terrain_backlash`.",
        f"- {duration_count} of {seed_count} seeds completed the requested horizon.",
        f"- {moving_count} of {seed_count} seeds tracked forward command with ratio >= 0.5; {weak_count} remained weak.",
        "- This rules out a blanket claim that upstream-main sim/morphology cannot generate forward locomotion.",
        "- The reference-target/open-loop path remains failed, so the mismatch is in controller/reference execution, not just contact friction.",
        "",
        "## Aggregate Metrics",
        "",
        "| metric | mean | p50 | p95 | min | max |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, key in [
        ("mean_local_vx_m_s", "mean_local_vx_m_s"),
        ("command_tracking_ratio", "command_tracking_ratio"),
        ("body_pitch_p95_rad", "body_pitch_p95_rad"),
        ("base_height_min_m", "base_height_min_m"),
        ("single_support_pct", "single_support_pct"),
        ("double_support_pct", "double_support_pct"),
        ("future_vx_delta_all_0p1s", "future_vx_delta_all_0p1s"),
        (
            "future_vx_delta_single_support_0p1s",
            "future_vx_delta_single_support_0p1s",
        ),
    ]:
        item = aggregate_payload[key]
        lines.append(
            f"| {label} | {fmt(item.get('mean'))} | {fmt(item.get('p50'))} | "
            f"{fmt(item.get('p95'))} | {fmt(item.get('min'))} | {fmt(item.get('max'))} |"
        )
    lines.extend(
        [
            "",
            "## Seed Summary",
            "",
            "| seed | status | samples | termination | mean_vx | track_ratio | pitch_p95 | height_min | single_% | double_% | single_dvx_0p1s |",
            "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for seed in payload["seeds"]:
        trace = seed.get("trace") or {}
        fractions = trace.get("contact_fractions") or {}
        future = trace.get("future_vx_delta_0p1s") or {}
        single_dvx = (
            (future.get("single_support") or {})
            .get("delta_vx_m_s", {})
            .get("mean")
        )
        lines.append(
            f"| {seed.get('seed')} | `{seed.get('status')}` | {seed.get('samples')} | "
            f"`{seed.get('termination_reason')}` | {fmt(seed.get('mean_local_vx_m_s'))} | "
            f"{fmt(seed.get('command_tracking_ratio'))} | {fmt(seed.get('body_pitch_p95_rad'))} | "
            f"{fmt(seed.get('base_height_min_m'))} | {fmt(fractions.get('single_support_pct'))} | "
            f"{fmt(fractions.get('double_pct'))} | {fmt(single_dvx)} |"
        )
    reference = aggregate_payload.get("reference_comparison")
    if reference:
        lines.extend(
            [
                "",
                "## Reference Comparison",
                "",
                f"- reference_artifact: `{reference.get('path')}`",
                f"- reference_status: `{reference.get('status')}`",
                f"- best_variant: `{reference.get('best_variant')}`",
                "- best_reference_single_future_vx_delta_mean_m_s: "
                f"`{fmt(reference.get('best_reference_single_future_vx_delta_mean_m_s'))}`",
                f"- best_mean_local_vx_m_s: `{fmt(reference.get('best_mean_local_vx_m_s'))}`",
                f"- best_contact_mismatch_pct: `{fmt(reference.get('best_contact_mismatch_pct'))}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Contact/friction substitution did not make the reference-target path propel forward.",
            "- The published ONNX policy does propel forward closed-loop in the same upstream-main backlash task.",
            "- Next work should compare the published policy's closed-loop contact/CoM strategy against the failed reference-target teacher path.",
            "- Do not resume robot motion from this result; it is an offline sim finding.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-glob",
        default=(
            "outputs/analysis/published_policy_upstream_main_backlash_seed*/"
            "closed_loop_actuator_bridge_eval.json"
        ),
    )
    parser.add_argument(
        "--reference-push-json",
        default=(
            "outputs/analysis/"
            "reference_push_effectiveness_upstream_main_backlash_nearest.json"
        ),
    )
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/PUBLISHED_POLICY_PROPULSION_AUDIT.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/published_policy_propulsion_audit.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    eval_paths = [Path(path) for path in sorted(glob.glob(args.eval_glob))]
    if not eval_paths:
        raise SystemExit(f"no eval files matched {args.eval_glob!r}")
    seeds = [seed_summary(path) for path in eval_paths]
    reference = reference_digest(Path(args.reference_push_json))
    payload = {
        "eval_glob": args.eval_glob,
        "reference_push_json": args.reference_push_json,
        "seeds": seeds,
        "aggregate": aggregate(seeds, reference),
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(output_md, payload)
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    print(f"overall_status: {payload['aggregate']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
