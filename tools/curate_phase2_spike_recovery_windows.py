#!/usr/bin/env python3
"""Curate spike-local Phase 2 recovery labels from failed rollout traces.

This offline helper emits compact JSONL snippets from failed full-observation
rollouts. It keeps the student's visited observations and its own action labels,
but locally smooths pitch-chain action deltas in selected failure windows. The
intent is to remove instantaneous corrected-envelope spikes without copying an
unrelated seed's action trajectory.

It does not train, deploy, SSH, run robot tests, or change runtime behavior.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


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
JOINT_INDEX = {name: idx for idx, name in enumerate(JOINT_NAMES)}
PITCH_CHAIN = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def vec(row: dict[str, Any], key: str) -> np.ndarray | None:
    value = row.get(key)
    if not isinstance(value, list) or len(value) != len(JOINT_NAMES):
        return None
    return np.asarray(value, dtype=float)


def load_velocity_limits(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text())
    joints = data.get("primary", {}).get("joints", {})
    limits: dict[str, float] = {}
    for joint in PITCH_CHAIN:
        value = joints.get(joint, {}).get("combined", {}).get("velocity_limit_rad_s")
        if value is not None:
            limits[joint] = float(value)
    missing = [joint for joint in PITCH_CHAIN if joint not in limits]
    if missing:
        raise ValueError(f"fit json missing corrected velocity limits for {missing}")
    return limits


def action_from_target(row: dict[str, Any], target: np.ndarray, original_action: np.ndarray, action_scale: float) -> np.ndarray:
    pre = vec(row, "target_pre_rate_limit_rad")
    sent = vec(row, "sent_target_rad")
    reference = pre if pre is not None else sent
    if reference is None:
        return original_action
    home = reference - original_action * action_scale
    return np.clip((target - home) / action_scale, -1.0, 1.0)


def target_velocity(rows: list[dict[str, Any]], key: str, dt_s: float) -> np.ndarray:
    targets = [vec(row, key) for row in rows]
    if any(item is None for item in targets) or len(targets) < 2:
        return np.zeros((0, len(JOINT_NAMES)), dtype=float)
    stacked = np.stack([item for item in targets if item is not None], axis=0)
    return np.abs(np.diff(stacked, axis=0)) / max(float(dt_s), 1.0e-9)


def excess_ticks(
    rows: list[dict[str, Any]],
    limits: dict[str, float],
    *,
    dt_s: float,
    tolerance: float,
    radius: int,
) -> tuple[set[int], dict[str, Any]]:
    velocities = target_velocity(rows, "target_pre_rate_limit_rad", dt_s)
    if velocities.size == 0:
        velocities = target_velocity(rows, "sent_target_rad", dt_s)
    selected: set[int] = set()
    per_joint_counts: Counter[str] = Counter()
    max_excess = 0.0
    for step, row_vel in enumerate(velocities, start=1):
        tick_excess = False
        for joint, limit in limits.items():
            idx = JOINT_INDEX[joint]
            excess = float(row_vel[idx] - limit)
            if excess > tolerance:
                tick_excess = True
                per_joint_counts[joint] += 1
                max_excess = max(max_excess, excess)
        if tick_excess:
            for tick in range(max(0, step - radius), min(len(rows), step + radius + 1)):
                selected.add(tick)
    return selected, {"per_joint_counts": dict(sorted(per_joint_counts.items())), "max_excess": max_excess}


def add_range(selected: set[int], start: int, end: int, count: int) -> None:
    lo = max(0, start)
    hi = min(count - 1, end)
    for tick in range(lo, hi + 1):
        selected.add(tick)


def digest_rows(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            "tick": row.get("tick"),
            "action": row.get("action"),
            "mode": row.get("mode"),
            "reasons": row.get("sample_weight_reasons"),
        }
        for row in rows
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def process_seed(
    seed_info: dict[str, Any],
    output_dir: Path,
    limits: dict[str, float],
    args: argparse.Namespace,
) -> dict[str, Any]:
    trace_path = Path(seed_info["trace_path"])
    rows = read_jsonl(trace_path)
    count = len(rows)
    selected, excess_summary = excess_ticks(
        rows,
        limits,
        dt_s=float(args.dt_s),
        tolerance=float(args.excess_tolerance_rad_s),
        radius=int(args.spike_radius),
    )
    reason_by_tick: dict[int, set[str]] = {tick: {"envelope_spike"} for tick in selected}
    mode = str(seed_info.get("mode") or "")
    if "FORWARD_LUNGE" in mode or "ACTUATOR_ENVELOPE_EXCESS" in mode:
        start = max(0, count - int(args.lunge_tail_ticks))
        add_range(selected, start, count - 1, count)
        for tick in range(start, count):
            reason_by_tick.setdefault(tick, set()).add("late_lunge_tail")
    if "PRE_PUSH_REVERSE" in mode:
        end = min(count - 1, int(args.reverse_head_ticks) - 1)
        add_range(selected, 0, end, count)
        for tick in range(0, end + 1):
            reason_by_tick.setdefault(tick, set()).add("early_reverse_head")

    output_rows: list[dict[str, Any]] = []
    removed_by_joint: dict[str, list[float]] = {joint: [] for joint in PITCH_CHAIN}
    changed_by_joint: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    previous_limited: np.ndarray | None = None
    previous_tick: int | None = None
    selected_sorted = sorted(selected)
    for tick in selected_sorted:
        row = rows[tick]
        action = vec(row, "action")
        if action is None:
            continue
        previous_source = previous_limited
        if previous_source is None and tick > 0:
            previous_source = vec(rows[tick - 1], "action")
        limited = action.copy()
        if previous_source is not None:
            contiguous = previous_tick is not None and tick == previous_tick + 1
            reasons = reason_by_tick.get(tick, set())
            delta_scale = 1.0
            if "late_lunge_tail" in reasons:
                delta_scale = min(delta_scale, float(args.lunge_delta_scale))
            if "early_reverse_head" in reasons:
                delta_scale = min(delta_scale, float(args.reverse_delta_scale))
            for joint, limit in limits.items():
                idx = JOINT_INDEX[joint]
                max_delta = float(limit) * float(args.limit_fraction) * float(args.dt_s) / float(args.action_scale)
                raw_delta = float(limited[idx] - previous_source[idx])
                shaped_delta = raw_delta * (delta_scale if contiguous else 1.0)
                clipped_delta = float(np.clip(shaped_delta, -max_delta, max_delta))
                if abs(clipped_delta - raw_delta) > 1.0e-12:
                    changed_by_joint[joint] += 1
                removed_by_joint[joint].append(abs(raw_delta) - abs(clipped_delta))
                limited[idx] = previous_source[idx] + clipped_delta

        copied = dict(row)
        copied["original_action"] = row.get("original_action", row.get("action"))
        copied["pre_spike_recovery_action"] = row.get("action")
        copied["action"] = limited.astype(float).tolist()
        copied["sample_weight"] = float(args.sample_weight)
        reasons = sorted(reason_by_tick.get(tick, {"selected"}))
        copied["sample_weight_reasons"] = sorted(
            set([*copied.get("sample_weight_reasons", []), *reasons, "phase2_spike_local_recovery"])
        )
        for reason in reasons:
            reason_counts[reason] += 1
        copied["mode"] = str(args.output_mode)
        copied["source_failure_mode"] = mode
        copied["source_failure_seed"] = int(seed_info.get("seed"))
        copied["spike_recovery_limit_fraction"] = float(args.limit_fraction)
        copied["spike_recovery_lunge_delta_scale"] = float(args.lunge_delta_scale)
        pre = vec(row, "target_pre_rate_limit_rad")
        if pre is not None:
            original_action = action
            adjusted = pre.copy()
            for joint in limits:
                idx = JOINT_INDEX[joint]
                home = pre[idx] - original_action[idx] * float(args.action_scale)
                adjusted[idx] = home + limited[idx] * float(args.action_scale)
            copied["target_pre_rate_limit_rad"] = adjusted.astype(float).tolist()
        sent = vec(row, "sent_target_rad")
        if sent is not None:
            copied["spike_recovery_inferred_action_from_sent_target"] = action_from_target(
                row, sent, action, float(args.action_scale)
            ).astype(float).tolist()
        output_rows.append(copied)
        previous_limited = limited
        previous_tick = tick

    seed = int(seed_info.get("seed"))
    output_trace = output_dir / f"seed_{seed:03d}" / "trace.jsonl"
    write_jsonl(output_trace, output_rows)
    per_joint = {
        joint: {
            "changed_ticks": int(changed_by_joint[joint]),
            "delta_removed_max": max(removed_by_joint[joint]) if removed_by_joint[joint] else 0.0,
            "delta_removed_mean": float(np.mean(removed_by_joint[joint])) if removed_by_joint[joint] else 0.0,
        }
        for joint in PITCH_CHAIN
    }
    return {
        "seed": seed,
        "source_trace": str(trace_path),
        "output_trace": str(output_trace),
        "source_failure_mode": mode,
        "samples_in": count,
        "samples_out": len(output_rows),
        "tick_min": int(selected_sorted[0]) if selected_sorted else None,
        "tick_max": int(selected_sorted[-1]) if selected_sorted else None,
        "dataset_id": digest_rows(output_rows),
        "selection_reason_counts": dict(sorted(reason_counts.items())),
        "excess_summary": excess_summary,
        "changed_by_joint": dict(sorted(changed_by_joint.items())),
        "per_joint": per_joint,
    }


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 2 Spike-Local Recovery Windows",
        "",
        f"status: `{payload['status']}`",
        "",
        "Offline-only curation for Phase 2 z=0.0075 recovery. It keeps failed-seed",
        "observations and smooths only selected pitch-chain action deltas; it does",
        "not copy same-tick neighbor trajectories and does not train or touch the robot.",
        "",
        "## Inputs",
        "",
        f"- failure_modes_json: `{payload['failure_modes_json']}`",
        f"- fit_json: `{payload['fit_json']}`",
        f"- output_trace_dir: `{payload['output_trace_dir']}`",
        "",
        "## Settings",
        "",
    ]
    for key, value in payload["settings"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Corrected Pitch-Chain Limits",
            "",
            "| joint | limit rad/s |",
            "|---|---:|",
        ]
    )
    for joint, limit in payload["corrected_limits_rad_s"].items():
        lines.append(f"| `{joint}` | {fmt(limit)} |")
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- seeds: `{summary['seeds']}`",
            f"- samples_out: `{summary['samples_out']}`",
            f"- dataset_id: `{payload['dataset_id']}`",
            "",
            "| seed | mode | ticks | samples | reasons | max_excess | changed joints |",
            "|---:|---|---:|---:|---|---:|---|",
        ]
    )
    for item in payload["seeds"]:
        changed = ", ".join(f"{k}:{v}" for k, v in item["changed_by_joint"].items()) or "none"
        lines.append(
            "| {seed} | `{mode}` | {ticks} | {samples} | `{reasons}` | {maxex} | {changed} |".format(
                seed=item["seed"],
                mode=item["source_failure_mode"],
                ticks=f"{item['tick_min']}-{item['tick_max']}",
                samples=item["samples_out"],
                reasons=item["selection_reason_counts"],
                maxex=fmt(item["excess_summary"].get("max_excess")),
                changed=changed,
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- Raw JSONL snippets remain generated artifacts unless explicitly force-added.",
            "- This curation is a candidate-data source only; promotion requires a trained",
            "  ONNX candidate to pass the canonical corrected-bridge seed gate.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--failure-modes-json", required=True)
    parser.add_argument("--fit-json", default="outputs/analysis/actuator_response_fit_corrected_knee.json")
    parser.add_argument("--output-trace-dir", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--sample-weight", type=float, default=1.5)
    parser.add_argument("--limit-fraction", type=float, default=0.85)
    parser.add_argument("--lunge-tail-ticks", type=int, default=80)
    parser.add_argument("--reverse-head-ticks", type=int, default=60)
    parser.add_argument("--spike-radius", type=int, default=8)
    parser.add_argument("--excess-tolerance-rad-s", type=float, default=0.02)
    parser.add_argument("--lunge-delta-scale", type=float, default=0.8)
    parser.add_argument("--reverse-delta-scale", type=float, default=0.7)
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--output-mode", default="phase2_spike_local_recovery")
    args = parser.parse_args()

    failure_modes_path = Path(args.failure_modes_json)
    failure_modes = json.loads(failure_modes_path.read_text())
    limits = load_velocity_limits(Path(args.fit_json))
    output_dir = Path(args.output_trace_dir)
    seed_rows = [
        process_seed(seed, output_dir, limits, args)
        for seed in failure_modes.get("seeds", [])
        if seed.get("trace_path")
    ]
    digest = hashlib.sha256(json.dumps(seed_rows, sort_keys=True).encode()).hexdigest()[:16]
    status = "PASS_PHASE2_SPIKE_RECOVERY_WINDOWS_READY" if any(row["samples_out"] for row in seed_rows) else "HOLD_PHASE2_SPIKE_RECOVERY_EMPTY"
    payload = {
        "status": status,
        "dataset_id": digest,
        "failure_modes_json": str(failure_modes_path),
        "fit_json": str(args.fit_json),
        "output_trace_dir": str(output_dir),
        "corrected_limits_rad_s": limits,
        "settings": {
            "sample_weight": float(args.sample_weight),
            "limit_fraction": float(args.limit_fraction),
            "lunge_tail_ticks": int(args.lunge_tail_ticks),
            "reverse_head_ticks": int(args.reverse_head_ticks),
            "spike_radius": int(args.spike_radius),
            "excess_tolerance_rad_s": float(args.excess_tolerance_rad_s),
            "lunge_delta_scale": float(args.lunge_delta_scale),
            "reverse_delta_scale": float(args.reverse_delta_scale),
            "action_scale": float(args.action_scale),
            "dt_s": float(args.dt_s),
            "output_mode": str(args.output_mode),
        },
        "summary": {
            "seeds": len(seed_rows),
            "samples_out": int(sum(row["samples_out"] for row in seed_rows)),
        },
        "seeds": seed_rows,
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text(render_md(payload))
    print(f"status={status}")
    print(f"dataset_id={digest}")
    print(f"samples_out={payload['summary']['samples_out']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
