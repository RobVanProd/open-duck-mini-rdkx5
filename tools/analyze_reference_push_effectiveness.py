#!/usr/bin/env python3
"""Compare reference-rollout propulsion opportunities using existing traces.

This is an offline analyzer. It reads JSONL traces from
eval_reference_motion_rollout.py and applies the same core read used by the
teacher push-effectiveness analysis: when a propulsion opportunity is present,
does local forward velocity increase after a short lookahead, and is that
change bought with lateral velocity or target-rate violations?

For reference rollouts there is no explicit ``push_allowed`` field, so the
primary opportunity is the reference asking for single support. The analyzer
also reports actual single-support and matched single-support windows to
separate "reference asked for a step" from "the simulated body actually
unweighted a foot."
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Callable

import numpy as np

from eval_reference_motion_rollout import fmt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REFERENCE_PUSH_EFFECTIVENESS_COMPARISON.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "reference_push_effectiveness_comparison.json"
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
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def vec2(record: dict[str, Any], key: str) -> tuple[int, int] | None:
    value = record.get(key)
    if not isinstance(value, list) or len(value) < 2:
        return None
    if not finite(value[0]) or not finite(value[1]):
        return None
    return (int(value[0]), int(value[1]))


def contact_code(contact: tuple[int, int] | None) -> str:
    if contact is None:
        return "??"
    return f"{int(contact[0])}{int(contact[1])}"


def is_single(contact: tuple[int, int] | None) -> bool:
    return contact in ((1, 0), (0, 1))


def local_vx(record: dict[str, Any]) -> float | None:
    vel = record.get("local_linvel_m_s")
    if isinstance(vel, list) and vel and finite(vel[0]):
        return float(vel[0])
    return None


def local_vy(record: dict[str, Any]) -> float | None:
    vel = record.get("local_linvel_m_s")
    if isinstance(vel, list) and len(vel) > 1 and finite(vel[1]):
        return float(vel[1])
    return None


def pitch_target_velocity(records: list[dict[str, Any]], index: int, dt_s: float) -> float | None:
    if index <= 0:
        return None
    current = records[index].get("sent_target_rad")
    previous = records[index - 1].get("sent_target_rad")
    if not isinstance(current, list) or not isinstance(previous, list):
        return None
    if len(current) <= max(PITCH_CHAIN) or len(previous) <= max(PITCH_CHAIN):
        return None
    velocities = [
        abs(float(current[joint]) - float(previous[joint])) / max(dt_s, 1.0e-9)
        for joint in PITCH_CHAIN
        if finite(current[joint]) and finite(previous[joint])
    ]
    return max(velocities) if velocities else None


def opportunity_predicates() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "reference_single_support": lambda record: is_single(
            vec2(record, "reference_foot_contacts")
        ),
        "actual_single_support": lambda record: is_single(vec2(record, "foot_contacts")),
        "matched_single_support": lambda record: (
            (actual := vec2(record, "foot_contacts")) is not None
            and (reference := vec2(record, "reference_foot_contacts")) is not None
            and is_single(actual)
            and actual == reference
        ),
        "reference_single_actual_double": lambda record: (
            is_single(vec2(record, "reference_foot_contacts"))
            and vec2(record, "foot_contacts") == (1, 1)
        ),
    }


def analyze_window(
    records: list[dict[str, Any]],
    indices: list[int],
    *,
    lookahead: int,
    dt_s: float,
) -> dict[str, Any]:
    vx = [local_vx(records[index]) for index in indices]
    vx = [value for value in vx if value is not None]
    vy_abs = [abs(value) for index in indices if (value := local_vy(records[index])) is not None]
    future_deltas = []
    pitch_velocities = []
    pairs = Counter()
    for index in indices:
        actual = vec2(records[index], "foot_contacts")
        reference = vec2(records[index], "reference_foot_contacts")
        pairs[f"{contact_code(reference)}->{contact_code(actual)}"] += 1
        now = local_vx(records[index])
        future = local_vx(records[index + lookahead])
        if now is not None and future is not None:
            future_deltas.append(float(future - now))
        pitch_velocity = pitch_target_velocity(records, index, dt_s)
        if pitch_velocity is not None:
            pitch_velocities.append(pitch_velocity)
    return {
        "samples": len(indices),
        "sample_pct": pct(len(indices), max(1, len(records) - lookahead)),
        "vx_m_s": signed_stats(vx),
        "future_vx_delta_m_s": signed_stats(future_deltas),
        "vy_abs_m_s": signed_stats(vy_abs),
        "pitch_target_velocity_rad_s": signed_stats(pitch_velocities),
        "contact_pair_pct": {
            key: pct(value, len(indices)) for key, value in sorted(pairs.items())
        },
    }


def analyze_trace(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    records = read_trace(path)
    if not records:
        return {"trace": str(path), "status": "HOLD_EMPTY_TRACE"}
    lookahead = max(1, int(round(args.lookahead_s / args.dt_s)))
    available_count = max(0, len(records) - lookahead)
    predicates = opportunity_predicates()
    windows = {}
    for name, predicate in predicates.items():
        indices = [
            index
            for index, record in enumerate(records[:available_count])
            if predicate(record)
        ]
        windows[name] = analyze_window(
            records, indices, lookahead=lookahead, dt_s=args.dt_s
        )
    actual_reference_pairs = Counter(
        f"{contact_code(vec2(record, 'reference_foot_contacts'))}->{contact_code(vec2(record, 'foot_contacts'))}"
        for record in records
    )
    mismatches = [
        vec2(record, "foot_contacts") != vec2(record, "reference_foot_contacts")
        for record in records
        if vec2(record, "foot_contacts") is not None
        and vec2(record, "reference_foot_contacts") is not None
    ]
    return {
        "trace": str(path),
        "status": "PASS_TRACE_ANALYZED",
        "label": path.parent.name,
        "mode": records[0].get("mode"),
        "seed": records[0].get("seed"),
        "samples": len(records),
        "command": records[0].get("command"),
        "contact_mismatch_pct": (
            float(np.mean(mismatches) * 100.0) if mismatches else None
        ),
        "contact_pair_pct": {
            key: pct(value, len(records))
            for key, value in sorted(actual_reference_pairs.items())
        },
        "windows": windows,
    }


def aggregate(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    usable = [row for row in rows if row.get("status") == "PASS_TRACE_ANALYZED"]
    labels = sorted({str(row.get("label")) for row in usable})
    by_label = {}
    for label in labels:
        items = [row for row in usable if row.get("label") == label]
        label_summary: dict[str, Any] = {
            "trace_count": len(items),
            "mean_contact_mismatch_pct": mean(
                [
                    float(row["contact_mismatch_pct"])
                    for row in items
                    if finite(row.get("contact_mismatch_pct"))
                ]
            )
            if any(finite(row.get("contact_mismatch_pct")) for row in items)
            else None,
            "windows": {},
        }
        for window_name in opportunity_predicates():
            window_rows = [row["windows"][window_name] for row in items]
            delta_means = [
                window["future_vx_delta_m_s"]["mean"]
                for window in window_rows
                if finite(window.get("future_vx_delta_m_s", {}).get("mean"))
            ]
            sample_pct = [
                window["sample_pct"]
                for window in window_rows
                if finite(window.get("sample_pct"))
            ]
            vy95 = [
                window["vy_abs_m_s"]["p95"]
                for window in window_rows
                if finite(window.get("vy_abs_m_s", {}).get("p95"))
            ]
            pitch95 = [
                window["pitch_target_velocity_rad_s"]["p95"]
                for window in window_rows
                if finite(window.get("pitch_target_velocity_rad_s", {}).get("p95"))
            ]
            label_summary["windows"][window_name] = {
                "mean_sample_pct": float(mean(sample_pct)) if sample_pct else None,
                "mean_future_vx_delta_m_s": float(mean(delta_means)) if delta_means else None,
                "mean_vy_abs_p95_m_s": float(mean(vy95)) if vy95 else None,
                "mean_pitch_target_velocity_p95_rad_s": (
                    float(mean(pitch95)) if pitch95 else None
                ),
            }
        by_label[label] = label_summary

    reference_single_deltas = [
        summary["windows"]["reference_single_support"]["mean_future_vx_delta_m_s"]
        for summary in by_label.values()
        if finite(
            summary["windows"]["reference_single_support"].get(
                "mean_future_vx_delta_m_s"
            )
        )
    ]
    reference_actual_double_pct = [
        summary["windows"]["reference_single_actual_double"]["mean_sample_pct"]
        for summary in by_label.values()
        if finite(
            summary["windows"]["reference_single_actual_double"].get("mean_sample_pct")
        )
    ]
    best_delta = max(reference_single_deltas) if reference_single_deltas else None
    worst_actual_double = (
        max(reference_actual_double_pct) if reference_actual_double_pct else None
    )
    qualifying_labels = []
    positive_but_unstable_labels = []
    high_contact_mismatch_labels = []
    for label, summary in by_label.items():
        ref_single = summary["windows"]["reference_single_support"]
        delta = ref_single["mean_future_vx_delta_m_s"]
        vy95 = ref_single["mean_vy_abs_p95_m_s"]
        pitch95 = ref_single["mean_pitch_target_velocity_p95_rad_s"]
        actual_double = summary["windows"]["reference_single_actual_double"]["mean_sample_pct"]
        contact_mismatch = summary["mean_contact_mismatch_pct"]
        if finite(contact_mismatch) and float(contact_mismatch) > args.max_contact_mismatch_pct:
            high_contact_mismatch_labels.append(label)
        if not finite(delta) or float(delta) < args.min_forward_delta_m_s:
            continue
        stable = (
            (not finite(vy95) or float(vy95) <= args.max_vy_abs_p95)
            and (not finite(pitch95) or float(pitch95) <= args.max_pitch_target_velocity_p95)
            and (
                not finite(actual_double)
                or float(actual_double) <= args.max_reference_single_actual_double_pct
            )
            and (
                not finite(contact_mismatch)
                or float(contact_mismatch) <= args.max_contact_mismatch_pct
            )
        )
        if stable:
            qualifying_labels.append(label)
        else:
            positive_but_unstable_labels.append(label)
    if not usable:
        status = "HOLD_REFERENCE_TRACE_MISSING"
    elif qualifying_labels:
        status = "PASS_REFERENCE_PROPULSION_EFFECTIVE"
    elif positive_but_unstable_labels:
        status = "HOLD_REFERENCE_PROPULSION_UNSTABLE"
    elif (
        worst_actual_double is not None
        and float(worst_actual_double) > args.max_reference_single_actual_double_pct
    ) or high_contact_mismatch_labels:
        status = "HOLD_REFERENCE_CONTACT_MISMATCH"
    else:
        status = "HOLD_REFERENCE_PROPULSION_INEFFECTIVE"
    return {
        "status": status,
        "trace_count": len(rows),
        "usable_trace_count": len(usable),
        "by_label": by_label,
        "best_reference_single_future_vx_delta_m_s": best_delta,
        "max_reference_single_actual_double_pct": worst_actual_double,
        "qualifying_labels": qualifying_labels,
        "positive_but_unstable_labels": positive_but_unstable_labels,
        "high_contact_mismatch_labels": high_contact_mismatch_labels,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    aggregate_row = payload["aggregate"]
    lines = [
        "# Reference Push-Effectiveness Comparison",
        "",
        f"status: `{payload['status']}`",
        f"trace_count: `{aggregate_row['trace_count']}`",
        f"usable_trace_count: `{aggregate_row['usable_trace_count']}`",
        f"lookahead_s: `{payload['lookahead_s']}`",
        "",
        "## Aggregate",
        "",
        f"- best_reference_single_future_vx_delta_m_s: `{fmt(aggregate_row['best_reference_single_future_vx_delta_m_s'])}`",
        f"- max_reference_single_actual_double_pct: `{fmt(aggregate_row['max_reference_single_actual_double_pct'])}`",
        f"- qualifying_labels: `{aggregate_row['qualifying_labels']}`",
        f"- positive_but_unstable_labels: `{aggregate_row['positive_but_unstable_labels']}`",
        f"- high_contact_mismatch_labels: `{aggregate_row['high_contact_mismatch_labels']}`",
        "",
        "## By Trace Set",
        "",
        "| trace_set | traces | contact_mismatch | ref_single_pct | ref_single_dvx | ref_single_vy95 | ref_single_pitch_vel95 | actual_single_pct | matched_single_pct | ref_single_actual_double_pct |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, summary in sorted(aggregate_row["by_label"].items()):
        ref_single = summary["windows"]["reference_single_support"]
        actual_single = summary["windows"]["actual_single_support"]
        matched = summary["windows"]["matched_single_support"]
        ref_double = summary["windows"]["reference_single_actual_double"]
        lines.append(
            "| {label} | {traces} | {mismatch} | {ref_pct} | {ref_dvx} | {ref_vy} | {ref_pitch} | {actual_pct} | {matched_pct} | {ref_double_pct} |".format(
                label=label,
                traces=summary["trace_count"],
                mismatch=fmt(summary["mean_contact_mismatch_pct"]),
                ref_pct=fmt(ref_single["mean_sample_pct"]),
                ref_dvx=fmt(ref_single["mean_future_vx_delta_m_s"]),
                ref_vy=fmt(ref_single["mean_vy_abs_p95_m_s"]),
                ref_pitch=fmt(ref_single["mean_pitch_target_velocity_p95_rad_s"]),
                actual_pct=fmt(actual_single["mean_sample_pct"]),
                matched_pct=fmt(matched["mean_sample_pct"]),
                ref_double_pct=fmt(ref_double["mean_sample_pct"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This analyzes existing reference rollout traces only; it does not train, deploy, SSH, or touch the robot.",
            "- `reference_single_support` is the reference asking the body to stand on one foot.",
            "- `reference_single_actual_double` is the key mismatch: the reference asks single support while the sim remains in double support.",
            "- A positive 0.1s future-vx delta during reference single support would show that the reference gait's support phase propels the body forward in this sim.",
            "- Near-zero/negative future-vx delta or persistent actual double support means the controller search should stop treating another teacher variant as the next default move.",
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
        help="Glob for reference rollout JSONL traces. May be provided multiple times.",
    )
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--lookahead-s", type=float, default=0.10)
    parser.add_argument("--min-forward-delta-m-s", type=float, default=0.005)
    parser.add_argument("--max-reference-single-actual-double-pct", type=float, default=60.0)
    parser.add_argument("--max-contact-mismatch-pct", type=float, default=60.0)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
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
    summary = aggregate(rows, args)
    payload = {
        "status": summary["status"],
        "trace_glob": args.trace_glob,
        "lookahead_s": args.lookahead_s,
        "thresholds": {
            "min_forward_delta_m_s": args.min_forward_delta_m_s,
            "max_reference_single_actual_double_pct": args.max_reference_single_actual_double_pct,
            "max_contact_mismatch_pct": args.max_contact_mismatch_pct,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_pitch_target_velocity_p95": args.max_pitch_target_velocity_p95,
        },
        "aggregate": summary,
        "traces": rows,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"trace_count={summary['trace_count']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
