#!/usr/bin/env python3
"""Summarize closed-loop candidate per-tick traces.

This is an offline analysis helper. It does not train, SSH, deploy, or touch the
robot.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


PITCH_CHAIN = {
    "left_hip_pitch": 2,
    "left_knee": 3,
    "left_ankle": 4,
    "right_hip_pitch": 11,
    "right_knee": 12,
    "right_ankle": 13,
}


def finite_float(value: Any) -> float | None:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def percentile(values: list[float], q: float) -> float | None:
    values = sorted(v for v in values if math.isfinite(v))
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    pos = (len(values) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def stats(values: list[float]) -> dict[str, float | None]:
    values = [v for v in values if math.isfinite(v)]
    if not values:
        return {"mean": None, "min": None, "p50": None, "p95": None, "max": None}
    return {
        "mean": mean(values),
        "min": min(values),
        "p50": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
        "max": max(values),
    }


def load_trace(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        rows.append(row)
    if not rows:
        raise SystemExit(f"{path}: no trace rows")
    return rows


def first_index(rows: list[dict[str, Any]], predicate) -> int | None:
    for idx, row in enumerate(rows):
        if predicate(row):
            return idx
    return None


def get_mode_eval_summary(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = json.loads(path.read_text())
    return payload.get("closed_loop_sim", {}).get("candidate_gate", {})


def vector_value(row: dict[str, Any], key: str, idx: int) -> float | None:
    value = row.get(key)
    if not isinstance(value, list) or idx >= len(value):
        return None
    return finite_float(value[idx])


def load_soft_prior(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text())
    prior = payload.get("prior") or payload
    if not isinstance(prior, dict) or not prior.get("action_mean"):
        raise SystemExit(f"{path}: missing prior.action_mean")
    return prior


def soft_prior_alignment(
    rows: list[dict[str, Any]], prior: dict[str, Any] | None
) -> dict[str, Any] | None:
    if prior is None:
        return None
    action_mean = prior.get("action_mean") or []
    joint_indices = [int(v) for v in prior.get("joint_indices") or []]
    joint_names = [str(v) for v in prior.get("joint_names") or []]
    if not action_mean or not joint_indices:
        return None
    period = int(prior.get("window_len") or len(action_mean))
    abs_errors: list[float] = []
    rms_errors: list[float] = []
    per_joint_errors: dict[str, list[float]] = {
        joint_names[i] if i < len(joint_names) else str(idx): []
        for i, idx in enumerate(joint_indices)
    }
    for row in rows:
        action = row.get("action") or []
        tick = int(row.get("tick") or 0)
        reference = action_mean[tick % period]
        squared = []
        for i, idx in enumerate(joint_indices):
            if idx >= len(action) or i >= len(reference):
                continue
            err = finite_float(action[idx])
            ref = finite_float(reference[i])
            if err is None or ref is None:
                continue
            delta = err - ref
            abs_errors.append(abs(delta))
            squared.append(delta * delta)
            joint_name = joint_names[i] if i < len(joint_names) else str(idx)
            per_joint_errors[joint_name].append(abs(delta))
        if squared:
            rms_errors.append(math.sqrt(sum(squared) / len(squared)))
    return {
        "method": "tick_mod_prior_window",
        "period": period,
        "mean_abs_error": stats(abs_errors),
        "rms_error": stats(rms_errors),
        "per_joint_abs_error": {name: stats(values) for name, values in per_joint_errors.items()},
    }


def analyze(
    rows: list[dict[str, Any]], *, eval_json: Path | None = None, soft_prior: dict[str, Any] | None = None
) -> dict[str, Any]:
    command = rows[0].get("command") or []
    command_x = finite_float(command[0]) if isinstance(command, list) and command else None
    times = [finite_float(row.get("time_s")) for row in rows]
    times_f = [v for v in times if v is not None]
    duration_s = (times_f[-1] - times_f[0]) if len(times_f) >= 2 else None
    local_vx = [
        v
        for row in rows
        if isinstance(row.get("local_linvel_m_s"), list)
        for v in [finite_float(row["local_linvel_m_s"][0])]
        if v is not None
    ]
    base_height = [v for row in rows for v in [finite_float(row.get("base_height_m"))] if v is not None]
    body_pitch = [v for row in rows for v in [finite_float(row.get("body_pitch_rad"))] if v is not None]
    reward = [v for row in rows for v in [finite_float(row.get("reward"))] if v is not None]
    contacts = []
    for row in rows:
        value = row.get("foot_contacts")
        if isinstance(value, list) and len(value) >= 2:
            contacts.append((int(value[0]), int(value[1])))
    reward_terms: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        for name, value in (row.get("reward_terms") or {}).items():
            f = finite_float(value)
            if f is not None:
                reward_terms[name].append(f)

    pitch_tracking: dict[str, list[float]] = {name: [] for name in PITCH_CHAIN}
    pitch_target_velocity: dict[str, list[float]] = {name: [] for name in PITCH_CHAIN}
    last_target: dict[str, float] = {}
    last_time: float | None = None
    for row in rows:
        t = finite_float(row.get("time_s"))
        for name, idx in PITCH_CHAIN.items():
            target = vector_value(row, "sent_target_rad", idx)
            actual = vector_value(row, "actual_position_rad", idx)
            if target is not None and actual is not None:
                pitch_tracking[name].append(abs(target - actual))
            if target is not None and t is not None and name in last_target and last_time is not None:
                dt = t - last_time
                if dt > 0:
                    pitch_target_velocity[name].append(abs((target - last_target[name]) / dt))
            if target is not None:
                last_target[name] = target
        if t is not None:
            last_time = t

    action_values = [
        abs(v)
        for row in rows
        for v in (row.get("action") or [])
        if isinstance(v, (int, float)) and math.isfinite(float(v))
    ]
    action_saturation_pct = (
        100.0 * sum(1 for v in action_values if v >= 0.999) / len(action_values)
        if action_values
        else None
    )

    first_done = first_index(rows, lambda row: bool(row.get("done")))
    first_low_height = first_index(
        rows, lambda row: (finite_float(row.get("base_height_m")) or 999.0) < 0.12
    )
    first_reverse = first_index(
        rows,
        lambda row: isinstance(row.get("local_linvel_m_s"), list)
        and (finite_float(row["local_linvel_m_s"][0]) or 0.0) < -0.02,
    )
    first_no_contact = first_index(
        rows,
        lambda row: isinstance(row.get("foot_contacts"), list)
        and len(row["foot_contacts"]) >= 2
        and int(row["foot_contacts"][0]) == 0
        and int(row["foot_contacts"][1]) == 0,
    )
    first_one_foot = first_index(
        rows,
        lambda row: isinstance(row.get("foot_contacts"), list)
        and len(row["foot_contacts"]) >= 2
        and int(row["foot_contacts"][0]) + int(row["foot_contacts"][1]) == 1,
    )

    term_means = {
        name: mean(values) for name, values in reward_terms.items() if values
    }
    dominant_costs = sorted(
        (
            (name, value)
            for name, value in term_means.items()
            if name.startswith("cost/") and math.isfinite(value)
        ),
        key=lambda item: abs(item[1]),
        reverse=True,
    )[:8]

    vx_mean = mean(local_vx) if local_vx else None
    track_ratio = vx_mean / command_x if vx_mean is not None and command_x else None
    contact_counts = Counter(contacts)

    failure_surface = "UNKNOWN"
    if first_low_height is not None and vx_mean is not None and vx_mean < -0.02:
        failure_surface = "REVERSE_HEIGHT_COLLAPSE"
    elif first_low_height is not None:
        failure_surface = "HEIGHT_COLLAPSE"
    elif vx_mean is not None and vx_mean < -0.02:
        failure_surface = "REVERSE_OR_WRONG_DIRECTION"
    elif track_ratio is not None and track_ratio < 0.25:
        failure_surface = "LOW_PROGRESS_TERMINATION"
    elif first_done is not None:
        failure_surface = "TERMINATION_WITHOUT_CLEAR_SURFACE"

    return {
        "action_saturation_pct": action_saturation_pct,
        "base_height_m": stats(base_height),
        "body_pitch_rad": stats(body_pitch),
        "command_x_m_s": command_x,
        "contact_counts": {str(k): v for k, v in contact_counts.items()},
        "dominant_cost_means": [
            {"term": name, "mean": value} for name, value in dominant_costs
        ],
        "duration_s": duration_s,
        "eval_candidate_gate": get_mode_eval_summary(eval_json),
        "events": {
            "first_done_tick": None if first_done is None else rows[first_done].get("tick"),
            "first_done_time_s": None if first_done is None else rows[first_done].get("time_s"),
            "first_low_height_tick": None if first_low_height is None else rows[first_low_height].get("tick"),
            "first_low_height_time_s": None if first_low_height is None else rows[first_low_height].get("time_s"),
            "first_no_contact_tick": None if first_no_contact is None else rows[first_no_contact].get("tick"),
            "first_one_foot_tick": None if first_one_foot is None else rows[first_one_foot].get("tick"),
            "first_reverse_tick": None if first_reverse is None else rows[first_reverse].get("tick"),
            "first_reverse_time_s": None if first_reverse is None else rows[first_reverse].get("time_s"),
        },
        "failure_surface": failure_surface,
        "local_forward_velocity_m_s": stats(local_vx),
        "pitch_chain": {
            name: {
                "target_velocity_rad_s": stats(pitch_target_velocity[name]),
                "tracking_error_rad": stats(pitch_tracking[name]),
            }
            for name in PITCH_CHAIN
        },
        "reward": stats(reward),
        "reward_term_means": term_means,
        "samples": len(rows),
        "soft_prior_alignment": soft_prior_alignment(rows, soft_prior),
        "track_ratio": track_ratio,
    }


def write_markdown(payload: dict[str, Any], path: Path, *, trace_path: Path) -> None:
    def fmt(value: Any) -> str:
        if value is None:
            return "NA"
        if isinstance(value, float):
            return f"{value:.4f}"
        return str(value)

    lines = [
        "# Candidate Trace Analysis",
        "",
        f"trace: `{trace_path}`",
        f"status: `{payload['failure_surface']}`",
        "",
        "## Summary",
        "",
        f"- samples: `{payload['samples']}`",
        f"- duration_s: `{fmt(payload['duration_s'])}`",
        f"- command_x_m_s: `{fmt(payload['command_x_m_s'])}`",
        f"- mean_local_vx_m_s: `{fmt(payload['local_forward_velocity_m_s']['mean'])}`",
        f"- track_ratio: `{fmt(payload['track_ratio'])}`",
        f"- base_height_min_m: `{fmt(payload['base_height_m']['min'])}`",
        f"- body_pitch_p95_rad: `{fmt(payload['body_pitch_rad']['p95'])}`",
        f"- reward_mean: `{fmt(payload['reward']['mean'])}`",
        f"- action_saturation_pct: `{fmt(payload['action_saturation_pct'])}`",
        "",
        "## Events",
        "",
        "| event | tick | time_s |",
        "|---|---:|---:|",
    ]
    events = payload["events"]
    event_pairs = [
        ("first_reverse", "first_reverse_tick", "first_reverse_time_s"),
        ("first_low_height", "first_low_height_tick", "first_low_height_time_s"),
        ("first_done", "first_done_tick", "first_done_time_s"),
        ("first_one_foot", "first_one_foot_tick", None),
        ("first_no_contact", "first_no_contact_tick", None),
    ]
    for label, tick_key, time_key in event_pairs:
        lines.append(
            f"| `{label}` | {fmt(events.get(tick_key))} | {fmt(events.get(time_key))} |"
        )
    lines.extend(
        [
            "",
            "## Dominant Cost Means",
            "",
            "| term | mean |",
            "|---|---:|",
        ]
    )
    for item in payload["dominant_cost_means"]:
        lines.append(f"| `{item['term']}` | {fmt(item['mean'])} |")
    lines.extend(
        [
            "",
            "## Pitch Chain",
            "",
            "| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |",
            "|---|---:|---:|---:|",
        ]
    )
    for joint, stats_payload in payload["pitch_chain"].items():
        lines.append(
            f"| `{joint}` | "
            f"{fmt(stats_payload['target_velocity_rad_s']['p95'])} | "
            f"{fmt(stats_payload['tracking_error_rad']['p95'])} | "
            f"{fmt(stats_payload['tracking_error_rad']['max'])} |"
        )
    lines.extend(
        [
            "",
            "## Soft Prior Alignment",
            "",
        ]
    )
    prior = payload.get("soft_prior_alignment")
    if prior:
        lines.extend(
            [
                f"- method: `{prior.get('method')}`",
                f"- period: `{prior.get('period')}`",
                f"- mean_abs_error_mean: `{fmt((prior.get('mean_abs_error') or {}).get('mean'))}`",
                f"- rms_error_mean: `{fmt((prior.get('rms_error') or {}).get('mean'))}`",
                "",
                "| joint | abs_error_mean | abs_error_p95 |",
                "|---|---:|---:|",
            ]
        )
        for joint, joint_stats in (prior.get("per_joint_abs_error") or {}).items():
            lines.append(
                f"| `{joint}` | {fmt(joint_stats.get('mean'))} | {fmt(joint_stats.get('p95'))} |"
            )
    else:
        lines.append("- not provided")
    lines.extend(
        [
            "",
            "## Contact States",
            "",
            "| contact_state | count |",
            "|---|---:|",
        ]
    )
    for state, count in sorted(payload["contact_counts"].items()):
        lines.append(f"| `{state}` | {count} |")
    lines.append("")
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace_jsonl", type=Path)
    parser.add_argument("--eval-json", type=Path, default=None)
    parser.add_argument("--soft-prior-config", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    rows = load_trace(args.trace_jsonl)
    payload = analyze(rows, eval_json=args.eval_json, soft_prior=load_soft_prior(args.soft_prior_config))
    payload["trace_jsonl"] = str(args.trace_jsonl)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, args.output_md, trace_path=args.trace_jsonl)
    print(args.output_md)
    print(args.output_json)
    print(payload["failure_surface"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
