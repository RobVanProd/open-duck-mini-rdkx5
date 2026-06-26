#!/usr/bin/env python3
"""Analyze seed-dependent motion/freeze modes from BC replay JSONL traces.

This is an offline diagnostic. It reads ignored per-seed JSONL traces emitted
by run_target_dataset_bc_smoke.py --trace-dir and writes compact markdown/JSON
artifacts. It does not run simulation, train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "BC_REPLAY_SEED_MODE_ANALYSIS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "bc_replay_seed_mode_analysis.json"
PITCH_CHAIN_INDICES = [2, 3, 4, 11, 12, 13]


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def contact_pattern(record: dict[str, Any]) -> str:
    return "".join(str(int(value)) for value in record.get("foot_contacts", []))


def abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros_like(values)
    velocity = np.abs(np.diff(values, axis=0) / max(float(dt_s), 1.0e-9))
    return np.vstack([np.zeros((1, values.shape[1])), velocity])


def mean(values: Iterable[Any]) -> float | None:
    data = [float(value) for value in values if finite(value)]
    return float(np.mean(data)) if data else None


def summarize_trace(path: Path, command_x: float, moving_threshold_m_s: float) -> dict[str, Any]:
    records = read_jsonl(path)
    if not records:
        return {"trace_jsonl": str(path), "status": "HOLD_EMPTY_TRACE", "samples": 0}

    dt_s = float(records[1]["time_s"] - records[0]["time_s"]) if len(records) > 1 else 0.02
    vx = [float(record["local_linvel_m_s"][0]) for record in records]
    vy_abs = [abs(float(record["local_linvel_m_s"][1])) for record in records]
    pitch_abs = [abs(float(record["body_pitch_rad"])) for record in records]
    height = [float(record["base_height_m"]) for record in records]
    action = np.asarray([record["action"] for record in records], dtype=float)
    sent = np.asarray([record["sent_target_rad"] for record in records], dtype=float)
    actual = np.asarray([record["actual_position_rad"] for record in records], dtype=float)
    sent_velocity = abs_velocity(sent, dt_s) if sent.size else np.zeros((0, 0))
    action_delta = abs_velocity(action, dt_s) if action.size else np.zeros((0, 0))
    tracking = np.abs(sent - actual) if sent.size and actual.size else np.zeros((0, 0))
    contacts = Counter(contact_pattern(record) for record in records)
    samples = len(records)
    single_pct = float((contacts.get("01", 0) + contacts.get("10", 0)) / samples * 100.0)
    double_pct = float(contacts.get("11", 0) / samples * 100.0)
    mean_vx = float(np.mean(vx))
    pitch_sent_velocity = (
        sent_velocity[:, PITCH_CHAIN_INDICES].reshape(-1) if sent_velocity.size else np.asarray([])
    )

    first_window = max(1, min(50, samples))
    early_sent_velocity = (
        sent_velocity[:first_window, PITCH_CHAIN_INDICES].reshape(-1)
        if sent_velocity.size
        else np.asarray([])
    )
    early_action_abs = action[:first_window].reshape(-1) if action.size else np.asarray([])

    return {
        "trace_jsonl": str(path),
        "status": "PASS_TRACE_ANALYZED",
        "seed": int(records[0].get("seed", -1)),
        "samples": samples,
        "termination_reason": "fall_or_progress_failure"
        if bool(records[-1].get("done"))
        else "duration_complete",
        "mean_vx_m_s": mean_vx,
        "track_ratio": mean_vx / float(command_x) if abs(command_x) > 1.0e-9 else None,
        "moving": bool(mean_vx >= float(moving_threshold_m_s)),
        "vy_abs_p95_m_s": percentile(vy_abs, 95),
        "body_pitch_abs_p95_rad": percentile(pitch_abs, 95),
        "base_height_min_m": float(np.min(height)),
        "single_support_pct": single_pct,
        "double_support_pct": double_pct,
        "contact_pct": {key: float(value / samples * 100.0) for key, value in sorted(contacts.items())},
        "action_abs_mean": float(np.mean(np.abs(action))) if action.size else None,
        "action_delta_p95_per_s": percentile(action_delta.reshape(-1).tolist(), 95)
        if action_delta.size
        else None,
        "sent_target_velocity_p95_rad_s": percentile(sent_velocity.reshape(-1).tolist(), 95)
        if sent_velocity.size
        else None,
        "pitch_chain_sent_target_velocity_p95_rad_s": percentile(pitch_sent_velocity.tolist(), 95)
        if pitch_sent_velocity.size
        else None,
        "joint_tracking_p95_rad": percentile(tracking.reshape(-1).tolist(), 95)
        if tracking.size
        else None,
        "early_action_abs_mean": float(np.mean(np.abs(early_action_abs))) if early_action_abs.size else None,
        "early_pitch_chain_sent_target_velocity_p95_rad_s": percentile(
            early_sent_velocity.tolist(), 95
        )
        if early_sent_velocity.size
        else None,
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"count": 0}
    return {
        "count": len(rows),
        "seeds": [row.get("seed") for row in rows],
        "mean_vx_m_s": mean(row.get("mean_vx_m_s") for row in rows),
        "track_ratio": mean(row.get("track_ratio") for row in rows),
        "single_support_pct": mean(row.get("single_support_pct") for row in rows),
        "double_support_pct": mean(row.get("double_support_pct") for row in rows),
        "pitch_chain_sent_target_velocity_p95_rad_s": mean(
            row.get("pitch_chain_sent_target_velocity_p95_rad_s") for row in rows
        ),
        "early_action_abs_mean": mean(row.get("early_action_abs_mean") for row in rows),
        "early_pitch_chain_sent_target_velocity_p95_rad_s": mean(
            row.get("early_pitch_chain_sent_target_velocity_p95_rad_s") for row in rows
        ),
        "body_pitch_abs_p95_rad": mean(row.get("body_pitch_abs_p95_rad") for row in rows),
        "base_height_min_m": mean(row.get("base_height_min_m") for row in rows),
    }


def classify(moving_rows: list[dict[str, Any]], frozen_rows: list[dict[str, Any]]) -> str:
    if not frozen_rows:
        return "PASS_NO_FREEZE_SEEDS"
    moving_single = mean(row.get("single_support_pct") for row in moving_rows) or 0.0
    frozen_single = mean(row.get("single_support_pct") for row in frozen_rows) or 0.0
    moving_velocity = mean(row.get("pitch_chain_sent_target_velocity_p95_rad_s") for row in moving_rows) or 0.0
    frozen_velocity = mean(row.get("pitch_chain_sent_target_velocity_p95_rad_s") for row in frozen_rows) or 0.0
    if frozen_single < moving_single * 0.25 and frozen_velocity < moving_velocity * 0.25:
        return "HOLD_FREEZE_LOW_ACTION_DOUBLE_SUPPORT"
    if frozen_velocity < moving_velocity * 0.25:
        return "HOLD_FREEZE_LOW_ACTION"
    if frozen_single < moving_single * 0.25:
        return "HOLD_FREEZE_DOUBLE_SUPPORT"
    return "HOLD_FREEZE_UNCLASSIFIED"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    rows = payload["traces"]
    lines = [
        "# BC Replay Seed Mode Analysis",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline analysis of ignored BC replay traces. It does not run",
        "simulation, training, deployment, SSH, or robot tests.",
        "",
        "## Summary",
        "",
        f"- trace_glob: `{payload['trace_glob']}`",
        f"- command_x: `{fmt(payload['command_x'])}`",
        f"- moving_threshold_m_s: `{fmt(payload['moving_threshold_m_s'])}`",
        f"- moving_seeds: `{payload['moving']['seeds']}`",
        f"- frozen_seeds: `{payload['frozen']['seeds']}`",
        "",
        "| group | count | mean_vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ["moving", "frozen"]:
        row = payload[label]
        lines.append(
            "| {label} | {count} | {vx} | {ratio} | {single} | {double} | {vel} | {early_action} | {early_vel} |".format(
                label=label,
                count=row.get("count"),
                vx=fmt(row.get("mean_vx_m_s")),
                ratio=fmt(row.get("track_ratio")),
                single=fmt(row.get("single_support_pct")),
                double=fmt(row.get("double_support_pct")),
                vel=fmt(row.get("pitch_chain_sent_target_velocity_p95_rad_s")),
                early_action=fmt(row.get("early_action_abs_mean")),
                early_vel=fmt(row.get("early_pitch_chain_sent_target_velocity_p95_rad_s")),
            )
        )
    lines.extend(
        [
            "",
            "## Per Seed",
            "",
            "| seed | mode | samples | termination | vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 | pitch95 | height_min |",
            "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in sorted(rows, key=lambda item: int(item.get("seed", -1))):
        lines.append(
            "| {seed} | {mode} | {samples} | {term} | {vx} | {ratio} | {single} | {double} | {vel} | {early_action} | {early_vel} | {pitch} | {height} |".format(
                seed=row.get("seed"),
                mode="moving" if row.get("moving") else "frozen",
                samples=row.get("samples"),
                term=row.get("termination_reason"),
                vx=fmt(row.get("mean_vx_m_s")),
                ratio=fmt(row.get("track_ratio")),
                single=fmt(row.get("single_support_pct")),
                double=fmt(row.get("double_support_pct")),
                vel=fmt(row.get("pitch_chain_sent_target_velocity_p95_rad_s")),
                early_action=fmt(row.get("early_action_abs_mean")),
                early_vel=fmt(row.get("early_pitch_chain_sent_target_velocity_p95_rad_s")),
                pitch=fmt(row.get("body_pitch_abs_p95_rad")),
                height=fmt(row.get("base_height_min_m")),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The next student must beat the frozen-seed pattern, not merely reduce fall count.",
            "- If frozen seeds show low action/target velocity and high double support, the next design should add closed-loop selection pressure against quiet double-support dwell.",
            "- No robot validation is implied by this analysis.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-dir", default=None)
    parser.add_argument("--trace-glob", default=None)
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--moving-threshold-m-s", type=float, default=0.02)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    if args.trace_glob:
        pattern = args.trace_glob
    elif args.trace_dir:
        pattern = str(Path(args.trace_dir) / "*.jsonl")
    else:
        raise SystemExit("provide --trace-dir or --trace-glob")

    paths = [Path(item) for item in sorted(glob.glob(pattern))]
    if not paths:
        raise SystemExit(f"no traces matched {pattern}")

    traces = [
        summarize_trace(path, command_x=args.command_x, moving_threshold_m_s=args.moving_threshold_m_s)
        for path in paths
    ]
    moving_rows = [row for row in traces if row.get("moving")]
    frozen_rows = [row for row in traces if not row.get("moving")]
    payload = {
        "status": classify(moving_rows, frozen_rows),
        "trace_glob": pattern,
        "command_x": float(args.command_x),
        "moving_threshold_m_s": float(args.moving_threshold_m_s),
        "traces": traces,
        "moving": aggregate(moving_rows),
        "frozen": aggregate(frozen_rows),
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"moving_seeds={payload['moving'].get('seeds')}")
    print(f"frozen_seeds={payload['frozen'].get('seeds')}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
