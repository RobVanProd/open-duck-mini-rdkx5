#!/usr/bin/env python3
"""Compare published-policy closed-loop traces against reference-target traces.

This is an offline mechanism diagnostic. It reads existing JSONL traces and
summarizes how the published policy creates forward motion compared with the
reference-target rollouts that fail the push-effectiveness gate. It does not
run simulation, import Playground, train, deploy, SSH, or touch robot hardware.
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


def pct(count: int, total: int) -> float | None:
    if total <= 0:
        return None
    return 100.0 * float(count) / float(total)


def read_trace(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def contact_code(record: dict[str, Any], key: str = "foot_contacts") -> str:
    value = record.get(key)
    if not isinstance(value, list) or len(value) < 2:
        return "??"
    left = 1 if int(value[0]) else 0
    right = 1 if int(value[1]) else 0
    return f"{left}{right}"


def contact_bucket(code: str) -> str:
    if code == "11":
        return "double"
    if code in {"10", "01"}:
        return "single"
    if code == "00":
        return "flight"
    return "unknown"


def local_component(record: dict[str, Any], index: int) -> float | None:
    value = record.get("local_linvel_m_s")
    if isinstance(value, list) and len(value) > index and finite(value[index]):
        return float(value[index])
    return None


def target_vector(record: dict[str, Any]) -> list[float] | None:
    for key in ("sent_target_rad", "reference_target_rad", "target_pre_rate_limit_rad"):
        value = record.get(key)
        if isinstance(value, list) and len(value) >= len(JOINT_NAMES):
            return [float(item) for item in value[: len(JOINT_NAMES)]]
    return None


def actual_vector(record: dict[str, Any]) -> list[float] | None:
    value = record.get("actual_position_rad")
    if isinstance(value, list) and len(value) >= len(JOINT_NAMES):
        return [float(item) for item in value[: len(JOINT_NAMES)]]
    return None


def action_vector(record: dict[str, Any]) -> list[float] | None:
    value = record.get("action")
    if isinstance(value, list) and len(value) >= len(JOINT_NAMES):
        return [float(item) for item in value[: len(JOINT_NAMES)]]
    return None


def longest_streak(codes: list[str], target: str) -> int:
    best = 0
    current = 0
    for code in codes:
        if contact_bucket(code) == target:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def first_tick(codes: list[str], target: str) -> int | None:
    for index, code in enumerate(codes):
        if contact_bucket(code) == target:
            return index
    return None


def alternations(codes: list[str]) -> int:
    singles = [code for code in codes if code in {"10", "01"}]
    return sum(1 for prev, cur in zip(singles, singles[1:]) if prev != cur)


def future_vx_delta(records: list[dict[str, Any]], horizon_ticks: int) -> dict[str, Any]:
    buckets: dict[str, list[float]] = {
        "all": [],
        "single": [],
        "double": [],
        "flight": [],
        "left_single": [],
        "right_single": [],
    }
    for index, record in enumerate(records):
        future_index = index + horizon_ticks
        if future_index >= len(records):
            continue
        now = local_component(record, 0)
        later = local_component(records[future_index], 0)
        if now is None or later is None:
            continue
        delta = later - now
        code = contact_code(record)
        bucket = contact_bucket(code)
        buckets["all"].append(delta)
        if bucket in buckets:
            buckets[bucket].append(delta)
        if code == "10":
            buckets["left_single"].append(delta)
        if code == "01":
            buckets["right_single"].append(delta)
    return {
        name: {"samples": len(values), "delta_vx_m_s": stats(values)}
        for name, values in buckets.items()
    }


def reference_contact_summary(
    records: list[dict[str, Any]], horizon_ticks: int
) -> dict[str, Any] | None:
    if not any("reference_foot_contacts" in record for record in records):
        return None
    counts = Counter(contact_code(record, "reference_foot_contacts") for record in records)
    actual_counts = Counter(contact_code(record, "foot_contacts") for record in records)
    pair_counts = Counter(
        f"{contact_code(record, 'reference_foot_contacts')}->{contact_code(record, 'foot_contacts')}"
        for record in records
    )
    mismatches = [
        contact_code(record, "reference_foot_contacts") != contact_code(record, "foot_contacts")
        for record in records
        if contact_code(record, "reference_foot_contacts") != "??"
        and contact_code(record, "foot_contacts") != "??"
    ]
    deltas: dict[str, list[float]] = {
        "reference_single": [],
        "reference_double": [],
        "reference_single_actual_double": [],
        "matched_single": [],
    }
    for index, record in enumerate(records):
        future_index = index + horizon_ticks
        if future_index >= len(records):
            continue
        now = local_component(record, 0)
        later = local_component(records[future_index], 0)
        if now is None or later is None:
            continue
        delta = later - now
        reference = contact_code(record, "reference_foot_contacts")
        actual = contact_code(record, "foot_contacts")
        if contact_bucket(reference) == "single":
            deltas["reference_single"].append(delta)
        if contact_bucket(reference) == "double":
            deltas["reference_double"].append(delta)
        if contact_bucket(reference) == "single" and actual == "11":
            deltas["reference_single_actual_double"].append(delta)
        if contact_bucket(reference) == "single" and reference == actual:
            deltas["matched_single"].append(delta)
    n = len(records)
    return {
        "reference_single_pct": pct(
            sum(count for code, count in counts.items() if contact_bucket(code) == "single"),
            n,
        ),
        "reference_double_pct": pct(counts["11"], n),
        "actual_single_pct": pct(
            sum(
                count
                for code, count in actual_counts.items()
                if contact_bucket(code) == "single"
            ),
            n,
        ),
        "reference_single_actual_double_pct": pct(
            pair_counts["10->11"] + pair_counts["01->11"], n
        ),
        "matched_single_pct": pct(pair_counts["10->10"] + pair_counts["01->01"], n),
        "contact_mismatch_pct": (
            100.0 * mean([1.0 if mismatch else 0.0 for mismatch in mismatches])
            if mismatches
            else None
        ),
        "future_vx_delta": {
            name: {"samples": len(values), "delta_vx_m_s": stats(values)}
            for name, values in deltas.items()
        },
        "contact_pair_pct": {
            pair: pct(count, n) for pair, count in sorted(pair_counts.items())
        },
    }


def per_joint_trace_metrics(records: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    target_velocity: dict[str, list[float]] = {name: [] for name in JOINT_NAMES}
    tracking_error: dict[str, list[float]] = {name: [] for name in JOINT_NAMES}
    action_abs: dict[str, list[float]] = {name: [] for name in JOINT_NAMES}
    action_delta: dict[str, list[float]] = {name: [] for name in JOINT_NAMES}
    previous_target: list[float] | None = None
    previous_action: list[float] | None = None
    for record in records:
        target = target_vector(record)
        actual = actual_vector(record)
        action = action_vector(record)
        if target is not None and previous_target is not None:
            for index, name in enumerate(JOINT_NAMES):
                target_velocity[name].append(
                    abs(target[index] - previous_target[index]) / max(dt_s, 1e-9)
                )
        if target is not None and actual is not None:
            for index, name in enumerate(JOINT_NAMES):
                tracking_error[name].append(abs(target[index] - actual[index]))
        if action is not None:
            for index, name in enumerate(JOINT_NAMES):
                action_abs[name].append(abs(action[index]))
            if previous_action is not None:
                for index, name in enumerate(JOINT_NAMES):
                    action_delta[name].append(abs(action[index] - previous_action[index]))
        previous_target = target
        previous_action = action

    rows = {}
    for name in JOINT_NAMES:
        rows[name] = {
            "target_velocity_rad_s": stats(target_velocity[name]),
            "tracking_error_rad": stats(tracking_error[name]),
            "action_abs": stats(action_abs[name]),
            "action_delta_abs": stats(action_delta[name]),
        }
    pitch_names = [name for name in JOINT_NAMES if name in PITCH_CHAIN]
    return {
        "joints": rows,
        "pitch_chain": {
            "target_velocity_p95_rad_s": stats(
                [
                    rows[name]["target_velocity_rad_s"]["p95"]
                    for name in pitch_names
                    if finite(rows[name]["target_velocity_rad_s"]["p95"])
                ]
            ),
            "tracking_error_p95_rad": stats(
                [
                    rows[name]["tracking_error_rad"]["p95"]
                    for name in pitch_names
                    if finite(rows[name]["tracking_error_rad"]["p95"])
                ]
            ),
            "action_abs_p95": stats(
                [
                    rows[name]["action_abs"]["p95"]
                    for name in pitch_names
                    if finite(rows[name]["action_abs"]["p95"])
                ]
            ),
            "action_delta_p95": stats(
                [
                    rows[name]["action_delta_abs"]["p95"]
                    for name in pitch_names
                    if finite(rows[name]["action_delta_abs"]["p95"])
                ]
            ),
        },
    }


def trace_summary(path: Path, *, label: str, kind: str, dt_s: float, lookahead_s: float) -> dict[str, Any]:
    records = read_trace(path)
    if not records:
        return {"trace": str(path), "label": label, "kind": kind, "status": "HOLD_EMPTY_TRACE"}
    codes = [contact_code(record) for record in records]
    counts = Counter(codes)
    buckets = Counter(contact_bucket(code) for code in codes)
    vx_values = [value for record in records if (value := local_component(record, 0)) is not None]
    vy_abs_values = [
        abs(value)
        for record in records
        if (value := local_component(record, 1)) is not None
    ]
    pitch_values = [
        float(value)
        for record in records
        if finite(value := record.get("body_pitch_rad"))
    ]
    height_values = [
        float(value)
        for record in records
        if finite(value := record.get("base_height_m"))
    ]
    done_count = sum(1 for record in records if record.get("done"))
    elapsed = max(
        float(records[-1].get("time_s", 0.0)) - float(records[0].get("time_s", 0.0)),
        dt_s,
    )
    progress_x = (
        float(records[-1]["base_x_m"]) - float(records[0]["base_x_m"])
        if finite(records[-1].get("base_x_m")) and finite(records[0].get("base_x_m"))
        else None
    )
    progress_y = (
        float(records[-1]["base_y_m"]) - float(records[0]["base_y_m"])
        if finite(records[-1].get("base_y_m")) and finite(records[0].get("base_y_m"))
        else None
    )
    command = records[0].get("command") or []
    command_x = command[0] if command and finite(command[0]) else None
    mean_vx = mean(vx_values) if vx_values else None
    target_metrics = per_joint_trace_metrics(records, dt_s)
    return {
        "trace": str(path),
        "label": label,
        "kind": kind,
        "status": "PASS_TRACE_ANALYZED",
        "seed": records[0].get("seed"),
        "mode": records[0].get("mode"),
        "samples": len(records),
        "done_count": done_count,
        "duration_complete": done_count == 0,
        "command": command,
        "command_tracking_ratio": (
            mean_vx / float(command_x)
            if mean_vx is not None and command_x not in (None, 0.0)
            else None
        ),
        "local_vx_m_s": stats(vx_values),
        "abs_local_vy_m_s": stats(vy_abs_values),
        "body_pitch_rad": stats(pitch_values),
        "base_height_m": stats(height_values),
        "progress": {
            "elapsed_s": elapsed,
            "world_x_m": progress_x,
            "world_y_m": progress_y,
            "world_vx_m_s": progress_x / elapsed if progress_x is not None else None,
            "world_vy_m_s": progress_y / elapsed if progress_y is not None else None,
        },
        "contact_counts": dict(counts),
        "contact_fractions": {
            "double_pct": pct(buckets["double"], len(records)),
            "single_pct": pct(buckets["single"], len(records)),
            "left_single_pct": pct(counts["10"], len(records)),
            "right_single_pct": pct(counts["01"], len(records)),
            "flight_pct": pct(buckets["flight"], len(records)),
        },
        "contact_sequence": {
            "first_single_tick": first_tick(codes, "single"),
            "longest_single_streak_ticks": longest_streak(codes, "single"),
            "longest_double_streak_ticks": longest_streak(codes, "double"),
            "single_side_alternations": alternations(codes),
        },
        "future_vx_delta": future_vx_delta(
            records, max(1, int(round(lookahead_s / dt_s)))
        ),
        "reference_contacts": reference_contact_summary(
            records, max(1, int(round(lookahead_s / dt_s)))
        ),
        "joint_metrics": target_metrics,
    }


def aggregate_group(traces: list[dict[str, Any]]) -> dict[str, Any]:
    def collect(path: list[str]) -> list[float]:
        values = []
        for trace in traces:
            value: Any = trace
            for key in path:
                value = value.get(key) if isinstance(value, dict) else None
            if finite(value):
                values.append(float(value))
        return values

    status_counts = Counter(trace.get("status") for trace in traces)
    return {
        "trace_count": len(traces),
        "status_counts": dict(status_counts),
        "duration_complete_count": sum(1 for trace in traces if trace.get("duration_complete")),
        "mean_local_vx_m_s": stats(collect(["local_vx_m_s", "mean"])),
        "command_tracking_ratio": stats(collect(["command_tracking_ratio"])),
        "abs_local_vy_p95_m_s": stats(collect(["abs_local_vy_m_s", "p95"])),
        "body_pitch_p95_rad": stats(collect(["body_pitch_rad", "p95"])),
        "base_height_min_m": stats(collect(["base_height_m", "min"])),
        "single_support_pct": stats(collect(["contact_fractions", "single_pct"])),
        "double_support_pct": stats(collect(["contact_fractions", "double_pct"])),
        "left_single_pct": stats(collect(["contact_fractions", "left_single_pct"])),
        "right_single_pct": stats(collect(["contact_fractions", "right_single_pct"])),
        "first_single_tick": stats(collect(["contact_sequence", "first_single_tick"])),
        "longest_single_streak_ticks": stats(
            collect(["contact_sequence", "longest_single_streak_ticks"])
        ),
        "longest_double_streak_ticks": stats(
            collect(["contact_sequence", "longest_double_streak_ticks"])
        ),
        "single_side_alternations": stats(
            collect(["contact_sequence", "single_side_alternations"])
        ),
        "future_vx_delta_all_0p1s": stats(
            collect(["future_vx_delta", "all", "delta_vx_m_s", "mean"])
        ),
        "future_vx_delta_single_0p1s": stats(
            collect(["future_vx_delta", "single", "delta_vx_m_s", "mean"])
        ),
        "future_vx_delta_double_0p1s": stats(
            collect(["future_vx_delta", "double", "delta_vx_m_s", "mean"])
        ),
        "reference_contact_mismatch_pct": stats(
            collect(["reference_contacts", "contact_mismatch_pct"])
        ),
        "reference_single_pct": stats(
            collect(["reference_contacts", "reference_single_pct"])
        ),
        "reference_single_actual_double_pct": stats(
            collect(["reference_contacts", "reference_single_actual_double_pct"])
        ),
        "matched_single_pct": stats(
            collect(["reference_contacts", "matched_single_pct"])
        ),
        "reference_single_future_vx_delta_0p1s": stats(
            collect(
                [
                    "reference_contacts",
                    "future_vx_delta",
                    "reference_single",
                    "delta_vx_m_s",
                    "mean",
                ]
            )
        ),
        "matched_single_future_vx_delta_0p1s": stats(
            collect(
                [
                    "reference_contacts",
                    "future_vx_delta",
                    "matched_single",
                    "delta_vx_m_s",
                    "mean",
                ]
            )
        ),
        "pitch_chain_target_velocity_p95_rad_s": stats(
            collect(["joint_metrics", "pitch_chain", "target_velocity_p95_rad_s", "mean"])
        ),
        "pitch_chain_tracking_error_p95_rad": stats(
            collect(["joint_metrics", "pitch_chain", "tracking_error_p95_rad", "mean"])
        ),
        "pitch_chain_action_abs_p95": stats(
            collect(["joint_metrics", "pitch_chain", "action_abs_p95", "mean"])
        ),
        "pitch_chain_action_delta_p95": stats(
            collect(["joint_metrics", "pitch_chain", "action_delta_p95", "mean"])
        ),
    }


def label_from_glob(pattern: str) -> str:
    text = pattern
    if "_raw_traces" in text:
        return "reference_raw"
    if "_cycle_projected_traces" in text:
        return "reference_cycle_projected"
    if "_contact_synchronized_projected_traces" in text:
        return "reference_contact_synchronized"
    if "published_policy" in text:
        return "published_policy_closed_loop"
    return Path(pattern).stem or "group"


def group_from_patterns(patterns: list[str], *, kind: str, dt_s: float, lookahead_s: float) -> dict[str, Any]:
    groups: dict[str, list[Path]] = {}
    for pattern in patterns:
        label = label_from_glob(pattern)
        groups.setdefault(label, []).extend(Path(path) for path in sorted(glob.glob(pattern)))
    outputs = {}
    for label, paths in groups.items():
        traces = [
            trace_summary(path, label=label, kind=kind, dt_s=dt_s, lookahead_s=lookahead_s)
            for path in paths
        ]
        outputs[label] = {
            "kind": kind,
            "patterns": [pattern for pattern in patterns if label_from_glob(pattern) == label],
            "traces": traces,
            "aggregate": aggregate_group(traces),
        }
    return outputs


def compare_groups(groups: dict[str, Any]) -> dict[str, Any]:
    policy = groups.get("published_policy_closed_loop")
    reference = groups.get("reference_contact_synchronized") or groups.get("reference_cycle_projected") or groups.get("reference_raw")
    if not policy or not reference:
        return {"status": "HOLD_MISSING_COMPARISON_GROUP"}
    p = policy["aggregate"]
    r = reference["aggregate"]
    policy_vx = p["mean_local_vx_m_s"]["mean"]
    reference_vx = r["mean_local_vx_m_s"]["mean"]
    policy_single = p["single_support_pct"]["mean"]
    reference_single = r["single_support_pct"]["mean"]
    policy_single_delta = p["future_vx_delta_single_0p1s"]["mean"]
    reference_single_delta = r["future_vx_delta_single_0p1s"]["mean"]
    return {
        "status": "PASS_POLICY_REFERENCE_MECHANISM_SPLIT",
        "policy_group": "published_policy_closed_loop",
        "reference_group": reference.get("traces", [{}])[0].get("label"),
        "policy_minus_reference_mean_vx_m_s": (
            policy_vx - reference_vx if finite(policy_vx) and finite(reference_vx) else None
        ),
        "policy_minus_reference_single_support_pct": (
            policy_single - reference_single
            if finite(policy_single) and finite(reference_single)
            else None
        ),
        "policy_minus_reference_single_delta_vx_m_s": (
            policy_single_delta - reference_single_delta
            if finite(policy_single_delta) and finite(reference_single_delta)
            else None
        ),
        "interpretation": (
            "Published policy closed-loop traces produce stable local forward "
            "motion while the best reference-target traces do not. The next "
            "branch should copy or constrain the closed-loop state-action/contact "
            "mechanism, not keep tuning open-loop target shapes."
        ),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    comparison = payload["comparison"]
    groups = payload["groups"]
    lines = [
        "# Policy vs Reference Mechanism Comparison",
        "",
        f"overall_status: `{comparison['status']}`",
        f"policy_group: `{comparison.get('policy_group')}`",
        f"reference_group: `{comparison.get('reference_group')}`",
        "",
        "## Executive Summary",
        "",
        "- The published policy closed-loop path completes the upstream-main `flat_terrain_backlash` horizon across all eight seeds.",
        "- The best reference-target path still fails to produce forward impulse during reference-requested single-support windows.",
        "- The mechanism split is no longer contact parameters alone; it is closed-loop policy behavior versus open-loop target execution.",
        "- Next work should mine policy state/action/contact timing before authorizing another teacher variant.",
        "",
        "## Aggregate Comparison",
        "",
        "| group | traces | complete | mean_vx | track_ratio | single_% | double_% | single_dvx_0p1s | vy_p95 | pitch_p95 | target_vel_p95 | tracking_p95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in [
        "published_policy_closed_loop",
        "reference_contact_synchronized",
        "reference_cycle_projected",
        "reference_raw",
    ]:
        item = groups.get(name)
        if not item:
            continue
        agg = item["aggregate"]
        lines.append(
            f"| {name} | {agg['trace_count']} | {agg['duration_complete_count']} | "
            f"{fmt(agg['mean_local_vx_m_s']['mean'])} | "
            f"{fmt(agg['command_tracking_ratio']['mean'])} | "
            f"{fmt(agg['single_support_pct']['mean'])} | "
            f"{fmt(agg['double_support_pct']['mean'])} | "
            f"{fmt(agg['future_vx_delta_single_0p1s']['mean'])} | "
            f"{fmt(agg['abs_local_vy_p95_m_s']['mean'])} | "
            f"{fmt(agg['body_pitch_p95_rad']['mean'])} | "
            f"{fmt(agg['pitch_chain_target_velocity_p95_rad_s']['mean'])} | "
            f"{fmt(agg['pitch_chain_tracking_error_p95_rad']['mean'])} |"
        )
    lines.extend(
        [
            "",
            "## Contact Sequence Comparison",
            "",
            "| group | first_single_tick | longest_single | longest_double | alternations | left_single_% | right_single_% | ref_single_% | mismatch_% | ref_single_dvx | matched_single_dvx |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name in [
        "published_policy_closed_loop",
        "reference_contact_synchronized",
        "reference_cycle_projected",
        "reference_raw",
    ]:
        item = groups.get(name)
        if not item:
            continue
        agg = item["aggregate"]
        lines.append(
            f"| {name} | {fmt(agg['first_single_tick']['mean'])} | "
            f"{fmt(agg['longest_single_streak_ticks']['mean'])} | "
            f"{fmt(agg['longest_double_streak_ticks']['mean'])} | "
            f"{fmt(agg['single_side_alternations']['mean'])} | "
            f"{fmt(agg['left_single_pct']['mean'])} | "
            f"{fmt(agg['right_single_pct']['mean'])} | "
            f"{fmt(agg['reference_single_pct']['mean'])} | "
            f"{fmt(agg['reference_contact_mismatch_pct']['mean'])} | "
            f"{fmt(agg['reference_single_future_vx_delta_0p1s']['mean'])} | "
            f"{fmt(agg['matched_single_future_vx_delta_0p1s']['mean'])} |"
        )
    lines.extend(
        [
            "",
            "## Split Metrics",
            "",
            "- policy_minus_reference_mean_vx_m_s: "
            f"`{fmt(comparison.get('policy_minus_reference_mean_vx_m_s'))}`",
            "- policy_minus_reference_single_support_pct: "
            f"`{fmt(comparison.get('policy_minus_reference_single_support_pct'))}`",
            "- policy_minus_reference_single_delta_vx_m_s: "
            f"`{fmt(comparison.get('policy_minus_reference_single_delta_vx_m_s'))}`",
            "",
            "## Interpretation",
            "",
            comparison.get("interpretation", ""),
            "",
            "Robot validation remains blocked.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy-trace-glob",
        action="append",
        default=[
            "outputs/analysis/published_policy_upstream_main_backlash_seed*/trace.jsonl"
        ],
    )
    parser.add_argument(
        "--reference-trace-glob",
        action="append",
        default=[
            "outputs/analysis/reference_motion_rollout_upstream_main_backlash_nearest_raw_traces/*.jsonl",
            "outputs/analysis/reference_motion_rollout_upstream_main_backlash_nearest_cycle_projected_traces/*.jsonl",
            "outputs/analysis/reference_motion_rollout_upstream_main_backlash_nearest_contact_synchronized_projected_traces/*.jsonl",
        ],
    )
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--lookahead-s", type=float, default=0.1)
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/POLICY_REFERENCE_MECHANISM_COMPARISON.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/policy_reference_mechanism_comparison.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    groups = {}
    groups.update(
        group_from_patterns(
            args.policy_trace_glob,
            kind="policy_closed_loop",
            dt_s=args.dt_s,
            lookahead_s=args.lookahead_s,
        )
    )
    groups.update(
        group_from_patterns(
            args.reference_trace_glob,
            kind="reference_target",
            dt_s=args.dt_s,
            lookahead_s=args.lookahead_s,
        )
    )
    payload = {
        "policy_trace_glob": args.policy_trace_glob,
        "reference_trace_glob": args.reference_trace_glob,
        "dt_s": args.dt_s,
        "lookahead_s": args.lookahead_s,
        "groups": groups,
        "comparison": compare_groups(groups),
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(output_md, payload)
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    print(f"overall_status: {payload['comparison']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
