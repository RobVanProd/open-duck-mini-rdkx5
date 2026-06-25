#!/usr/bin/env python3
"""Score target primitive traces with a worst-seed objective.

This is an offline scorer for target-generation traces. It does not run
simulation, train, deploy, SSH, or touch the robot. It reads JSONL traces,
slides a fixed window over each primitive/seed rollout, scores each window
against the target objective, and ranks primitives by their worst seed.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_OBJECTIVE_SCORE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_objective_score.json"


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def source_seed(path: Path) -> int | None:
    stem = path.stem
    if not stem.startswith("seed_"):
        return None
    try:
        return int(stem.split("_", 1)[1])
    except ValueError:
        return None


def pattern(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(int(value)) for value in values)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def expand_globs(patterns: list[str]) -> list[Path]:
    paths = []
    for pattern_text in patterns:
        pattern = str(Path(pattern_text) if Path(pattern_text).is_absolute() else ROOT / pattern_text)
        paths.extend(Path(item) for item in glob.glob(pattern, recursive=True))
    return sorted(set(path for path in paths if path.is_file()))


def abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros((0, values.shape[1] if values.ndim == 2 else 0))
    return np.abs(np.diff(values, axis=0) / max(float(dt_s), 1.0e-9))


def done_margin(records: list[dict[str, Any]], end_index: int) -> int | None:
    for offset, record in enumerate(records[end_index + 1 :], start=1):
        if record.get("done"):
            return offset
    return None


def contact_dominance(contact_pct: dict[str, float]) -> float:
    if not contact_pct:
        return 0.0
    return max(float(value) for value in contact_pct.values())


def support_metrics(contact_pct: dict[str, float]) -> dict[str, float]:
    support_a = float(contact_pct.get("10", 0.0))
    support_b = float(contact_pct.get("01", 0.0))
    return {
        "double_support_pct": float(contact_pct.get("11", 0.0)),
        "no_support_pct": float(contact_pct.get("00", 0.0)),
        "single_support_pct": support_a + support_b,
        "support_a_only_pct": support_a,
        "support_b_only_pct": support_b,
        "min_single_support_side_pct": min(support_a, support_b),
    }


def window_metrics(
    records: list[dict[str, Any]],
    start: int,
    window_samples: int,
    dt_s: float,
) -> dict[str, Any]:
    window = records[start : start + window_samples]
    vx = [record["local_linvel_m_s"][0] for record in window]
    vy = [record["local_linvel_m_s"][1] for record in window]
    pitch = [abs(record["body_pitch_rad"]) for record in window]
    height = [record["base_height_m"] for record in window]
    base_x = [record.get("base_x_m") for record in window if finite(record.get("base_x_m"))]
    action = np.asarray([record.get("action", []) for record in window], dtype=float)
    sent = np.asarray([record.get("sent_target_rad", []) for record in window], dtype=float)
    actual = np.asarray([record.get("actual_position_rad", []) for record in window], dtype=float)
    contact_patterns = [pattern(record.get("foot_contacts", [])) for record in window]
    contacts = Counter(contact_patterns)
    foot_z_values = []
    for record in window:
        foot_z_values.extend(
            float(value)
            for value in record.get("foot_site_z_m", [])
            if finite(value)
        )
    sent_velocity = abs_velocity(sent, dt_s) if sent.size else np.zeros((0, 0))
    tracking = np.abs(sent - actual) if sent.size and actual.size else np.zeros((0, 0))
    total = len(window)
    contact_pct = {
        key: float(value / total * 100.0) for key, value in sorted(contacts.items())
    }
    end = start + window_samples - 1
    margin = done_margin(records, end)
    support = support_metrics(contact_pct)
    return {
        "samples": total,
        "start_tick": int(window[0].get("tick", start)),
        "end_tick": int(window[-1].get("tick", end)),
        "start_index": start,
        "end_index": end,
        "done_inside_window": any(record.get("done") for record in window),
        "ticks_until_done_after_window": margin,
        "mean_vx_m_s": float(np.mean(vx)) if vx else None,
        "forward_displacement_m": (
            float(base_x[-1] - base_x[0]) if len(base_x) >= 2 else None
        ),
        "vy_abs_p95_m_s": percentile([abs(value) for value in vy], 95),
        "body_pitch_abs_p95_rad": percentile(pitch, 95),
        "base_height_min_m": float(np.min(height)) if height else None,
        "action_saturation_pct": (
            float(np.mean(np.abs(action) >= 0.999) * 100.0) if action.size else None
        ),
        "sent_target_velocity_p95_rad_s": (
            percentile(sent_velocity.reshape(-1).tolist(), 95)
            if sent_velocity.size
            else None
        ),
        "joint_tracking_p95_rad": (
            percentile(tracking.reshape(-1).tolist(), 95) if tracking.size else None
        ),
        "contact_pct": contact_pct,
        "contact_dominance_pct": contact_dominance(contact_pct),
        **support,
        "contact_transitions": sum(
            1 for a, b in zip(contact_patterns, contact_patterns[1:]) if a != b
        ),
        "foot_site_z_p95_m": percentile(foot_z_values, 95) if foot_z_values else None,
    }


def objective_score(metrics: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    penalties: dict[str, float] = {}
    hard_failures = []
    mean_vx = float(metrics.get("mean_vx_m_s") or -999.0)
    vy95 = float(metrics.get("vy_abs_p95_m_s") or 999.0)
    pitch95 = float(metrics.get("body_pitch_abs_p95_rad") or 999.0)
    height_min = float(metrics.get("base_height_min_m") or -999.0)
    displacement = metrics.get("forward_displacement_m")
    saturation = float(metrics.get("action_saturation_pct") or 0.0)
    sent_vel = float(metrics.get("sent_target_velocity_p95_rad_s") or 999.0)
    tracking = float(metrics.get("joint_tracking_p95_rad") or 999.0)
    contact = float(metrics.get("contact_dominance_pct") or 999.0)
    double_support = float(metrics.get("double_support_pct") or 0.0)
    no_support = float(metrics.get("no_support_pct") or 0.0)
    single_support = float(metrics.get("single_support_pct") or 0.0)
    min_single_side = float(metrics.get("min_single_support_side_pct") or 0.0)
    contact_transitions = int(metrics.get("contact_transitions") or 0)
    foot_site_z_p95 = metrics.get("foot_site_z_p95_m")
    margin = metrics.get("ticks_until_done_after_window")

    penalties["forward_shortfall"] = max(0.0, args.min_mean_vx - mean_vx) * args.forward_weight
    penalties["forward_displacement"] = (
        max(0.0, args.min_forward_displacement_m - float(displacement))
        * args.forward_displacement_weight
        if displacement is not None and args.min_forward_displacement_m >= 0.0
        else 0.0
    )
    penalties["lateral"] = max(0.0, vy95 - args.max_vy_abs_p95) * args.lateral_weight
    penalties["contact"] = max(0.0, contact - args.max_contact_dominance_pct) * args.contact_weight
    penalties["double_support"] = (
        max(0.0, double_support - args.max_double_support_pct)
        * args.double_support_weight
    )
    penalties["no_support"] = (
        max(0.0, no_support - args.max_no_support_pct)
        * args.no_support_weight
    )
    penalties["single_support"] = (
        max(0.0, args.min_single_support_pct - single_support)
        * args.single_support_weight
    )
    penalties["single_support_balance"] = (
        max(0.0, args.min_each_single_support_pct - min_single_side)
        * args.single_support_balance_weight
    )
    penalties["contact_transitions"] = (
        max(0.0, args.min_contact_transitions - float(contact_transitions))
        * args.contact_transition_weight
    )
    penalties["foot_clearance"] = (
        max(0.0, args.min_foot_site_z_p95 - float(foot_site_z_p95))
        * args.foot_clearance_weight
        if foot_site_z_p95 is not None and args.min_foot_site_z_p95 >= 0.0
        else 0.0
    )
    penalties["pitch"] = max(0.0, pitch95 - args.max_pitch_abs_p95) * args.pitch_weight
    penalties["height"] = max(0.0, args.min_base_height - height_min) * args.height_weight
    penalties["saturation"] = max(0.0, saturation - args.max_action_saturation_pct) * args.saturation_weight
    penalties["target_velocity"] = max(0.0, sent_vel - args.max_sent_velocity_p95) * args.actuator_weight
    penalties["tracking"] = max(0.0, tracking - args.max_tracking_p95) * args.actuator_weight
    penalties["done_margin"] = (
        max(0.0, args.min_done_margin - float(margin)) * args.done_margin_weight
        if margin is not None
        else 0.0
    )
    if metrics.get("done_inside_window"):
        penalties["done_inside_window"] = args.done_inside_window_penalty

    if mean_vx < args.min_mean_vx:
        hard_failures.append("low_forward_velocity")
    if (
        displacement is not None
        and args.min_forward_displacement_m >= 0.0
        and float(displacement) < args.min_forward_displacement_m
    ):
        hard_failures.append("low_forward_displacement")
    if vy95 > args.max_vy_abs_p95:
        hard_failures.append("high_lateral_velocity")
    if contact > args.max_contact_dominance_pct:
        hard_failures.append("single_contact_pattern_dominates")
    if double_support > args.max_double_support_pct:
        hard_failures.append("double_support_dominates")
    if no_support > args.max_no_support_pct:
        hard_failures.append("no_support_too_high")
    if single_support < args.min_single_support_pct:
        hard_failures.append("too_little_single_support")
    if min_single_side < args.min_each_single_support_pct:
        hard_failures.append("single_support_not_balanced")
    if contact_transitions < args.min_contact_transitions:
        hard_failures.append("too_few_contact_transitions")
    if (
        args.min_foot_site_z_p95 >= 0.0
        and foot_site_z_p95 is not None
        and float(foot_site_z_p95) < args.min_foot_site_z_p95
    ):
        hard_failures.append("low_foot_clearance")
    if pitch95 > args.max_pitch_abs_p95:
        hard_failures.append("high_body_pitch")
    if height_min < args.min_base_height:
        hard_failures.append("low_base_height")
    if saturation > args.max_action_saturation_pct:
        hard_failures.append("action_saturation")
    if sent_vel > args.max_sent_velocity_p95:
        hard_failures.append("high_sent_target_velocity")
    if tracking > args.max_tracking_p95:
        hard_failures.append("high_tracking_error")
    if margin is not None and int(margin) < args.min_done_margin:
        hard_failures.append("short_done_margin")
    if metrics.get("done_inside_window"):
        hard_failures.append("done_inside_window")

    penalty = sum(penalties.values())
    forward_bonus = min(max(mean_vx, 0.0), args.command_x * args.max_track_ratio)
    score = forward_bonus - penalty
    return {
        "score": float(score),
        "forward_bonus": float(forward_bonus),
        "penalty_total": float(penalty),
        "penalties": penalties,
        "hard_failures": sorted(set(hard_failures)),
        "passes_curation": not hard_failures,
    }


def best_seed_window(records: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any] | None:
    if len(records) < args.window_samples:
        return None
    best = None
    for start in range(0, len(records) - args.window_samples + 1, args.stride_samples):
        metrics = window_metrics(records, start, args.window_samples, args.dt_s)
        scored = objective_score(metrics, args)
        row = {**metrics, **scored}
        if best is None or row["score"] > best["score"]:
            best = row
    return best


def trace_records_by_mode_seed(paths: list[Path]) -> dict[tuple[str, int], list[dict[str, Any]]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for path in paths:
        seed = source_seed(path)
        if seed is None:
            continue
        records = read_jsonl(path)
        by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            by_mode[str(record.get("mode", "unknown"))].append(record)
        for mode, mode_records in by_mode.items():
            grouped[(mode, seed)].extend(mode_records)
    return grouped


def score_traces(args: argparse.Namespace) -> dict[str, Any]:
    paths = expand_globs(args.trace_glob)
    grouped = trace_records_by_mode_seed(paths)
    required_seeds = parse_int_list(args.seeds)
    modes = sorted({mode for mode, _seed in grouped})
    results = []
    reason_counts = Counter()
    seed_reason_counts: dict[int, Counter] = {seed: Counter() for seed in required_seeds}
    for mode in modes:
        seed_rows = {}
        for seed in required_seeds:
            row = best_seed_window(grouped.get((mode, seed), []), args)
            if row is None:
                row = {
                    "score": -999.0,
                    "passes_curation": False,
                    "hard_failures": ["missing_seed_trace_or_window"],
                }
            seed_rows[f"seed_{seed:03d}"] = row
            for reason in row.get("hard_failures", []):
                reason_counts[str(reason)] += 1
                seed_reason_counts[seed][str(reason)] += 1
        worst_seed_name, worst_row = min(
            seed_rows.items(), key=lambda item: float(item[1].get("score", -999.0))
        )
        pass_seeds = [
            seed_name
            for seed_name, row in seed_rows.items()
            if row.get("passes_curation")
        ]
        results.append(
            {
                "mode": mode,
                "worst_seed": worst_seed_name,
                "worst_seed_score": worst_row.get("score"),
                "min_seed_score": worst_row.get("score"),
                "mean_seed_score": float(
                    np.mean([float(row.get("score", -999.0)) for row in seed_rows.values()])
                ),
                "pass_seed_count": len(pass_seeds),
                "pass_seeds": pass_seeds,
                "passes_all_seeds": len(pass_seeds) == len(required_seeds),
                "seeds": seed_rows,
            }
        )
    results.sort(
        key=lambda row: (
            row["passes_all_seeds"],
            row["pass_seed_count"],
            float(row["min_seed_score"] or -999.0),
            float(row["mean_seed_score"] or -999.0),
        ),
        reverse=True,
    )
    robust_modes = [row for row in results if row["passes_all_seeds"]]
    status = "PASS_SEED_ROBUST_TARGETS" if robust_modes else "HOLD_NO_SEED_ROBUST_TARGETS"
    return {
        "status": status,
        "trace_globs": args.trace_glob,
        "trace_files": len(paths),
        "required_seeds": required_seeds,
        "window_samples": args.window_samples,
        "stride_samples": args.stride_samples,
        "criteria": {
            "min_mean_vx": args.min_mean_vx,
            "min_forward_displacement_m": args.min_forward_displacement_m,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_contact_dominance_pct": args.max_contact_dominance_pct,
            "max_double_support_pct": args.max_double_support_pct,
            "max_no_support_pct": args.max_no_support_pct,
            "min_single_support_pct": args.min_single_support_pct,
            "min_each_single_support_pct": args.min_each_single_support_pct,
            "max_pitch_abs_p95": args.max_pitch_abs_p95,
            "min_base_height": args.min_base_height,
            "max_sent_velocity_p95": args.max_sent_velocity_p95,
            "max_tracking_p95": args.max_tracking_p95,
            "min_done_margin": args.min_done_margin,
            "min_contact_transitions": args.min_contact_transitions,
            "min_foot_site_z_p95": args.min_foot_site_z_p95,
        },
        "reason_counts": dict(reason_counts),
        "seed_reason_counts": {
            f"seed_{seed:03d}": dict(counter) for seed, counter in seed_reason_counts.items()
        },
        "mode_count": len(results),
        "robust_mode_count": len(robust_modes),
        "results": results[: args.max_report_modes],
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Target Objective Score",
        "",
        f"status: `{payload['status']}`",
        "",
        "This ranks target primitive traces by the worst seed. It does not run",
        "simulation or training.",
        "",
        "## Summary",
        "",
        f"- trace_files: `{payload['trace_files']}`",
        f"- mode_count: `{payload['mode_count']}`",
        f"- robust_mode_count: `{payload['robust_mode_count']}`",
        f"- required_seeds: `{payload['required_seeds']}`",
        f"- window_samples: `{payload['window_samples']}`",
        "",
        "## Criteria",
        "",
    ]
    for key, value in payload["criteria"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Seed Failure Counts", ""])
    for seed_name, counts in payload["seed_reason_counts"].items():
        lines.append(f"### {seed_name}")
        if counts:
            for reason, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"- `{reason}`: `{count}`")
        else:
            lines.append("- `none`")
        lines.append("")
    lines.extend(
        [
            "## Top Worst-Seed Candidates",
            "",
            "| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |",
            "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    if not payload["results"]:
        lines.append("| NA | 0 | NA | NA | NA | NA | NA | NA | NA | NA |")
    for row in payload["results"][:25]:
        seed0 = row["seeds"].get("seed_000") or {}
        seed2 = row["seeds"].get("seed_002") or {}
        lines.append(
            "| {mode} | {pass_count} | {worst} | {min_score} | {mean_score} | {seed0_vx} | {seed0_dx} | {seed2_vx} | {seed2_dx} | {seed2_vy} | {seed2_contact} | {seed2_transitions} | {seed2_foot_z} | `{seed2_fail}` |".format(
                mode=row["mode"],
                pass_count=row["pass_seed_count"],
                worst=row["worst_seed"],
                min_score=fmt(row["min_seed_score"]),
                mean_score=fmt(row["mean_seed_score"]),
                seed0_vx=fmt(seed0.get("mean_vx_m_s")),
                seed0_dx=fmt(seed0.get("forward_displacement_m")),
                seed2_vx=fmt(seed2.get("mean_vx_m_s")),
                seed2_dx=fmt(seed2.get("forward_displacement_m")),
                seed2_vy=fmt(seed2.get("vy_abs_p95_m_s")),
                seed2_contact=fmt(seed2.get("contact_dominance_pct")),
                seed2_transitions=fmt(seed2.get("contact_transitions"), digits=0),
                seed2_foot_z=fmt(seed2.get("foot_site_z_p95_m")),
                seed2_fail=", ".join(seed2.get("hard_failures") or []),
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.",
            "- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.",
            "- Do not build a supervised target manifest until robust modes exist.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", default=[], required=True)
    parser.add_argument("--seeds", default="0,2")
    parser.add_argument("--window-samples", type=int, default=50)
    parser.add_argument("--stride-samples", type=int, default=5)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument(
        "--min-forward-displacement-m",
        type=float,
        default=-1.0,
        help="Optional base-x displacement gate for the scoring window. Negative disables.",
    )
    parser.add_argument("--max-track-ratio", type=float, default=1.5)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-contact-dominance-pct", type=float, default=95.0)
    parser.add_argument("--max-double-support-pct", type=float, default=100.0)
    parser.add_argument("--max-no-support-pct", type=float, default=100.0)
    parser.add_argument("--min-single-support-pct", type=float, default=0.0)
    parser.add_argument("--min-each-single-support-pct", type=float, default=0.0)
    parser.add_argument("--min-contact-transitions", type=int, default=0)
    parser.add_argument("--min-foot-site-z-p95", type=float, default=-1.0)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.35)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--max-action-saturation-pct", type=float, default=1.0)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=2.5)
    parser.add_argument("--max-tracking-p95", type=float, default=0.12)
    parser.add_argument("--min-done-margin", type=int, default=50)
    parser.add_argument("--forward-weight", type=float, default=8.0)
    parser.add_argument("--forward-displacement-weight", type=float, default=8.0)
    parser.add_argument("--lateral-weight", type=float, default=8.0)
    parser.add_argument("--contact-weight", type=float, default=0.02)
    parser.add_argument("--double-support-weight", type=float, default=0.02)
    parser.add_argument("--no-support-weight", type=float, default=0.02)
    parser.add_argument("--single-support-weight", type=float, default=0.02)
    parser.add_argument("--single-support-balance-weight", type=float, default=0.02)
    parser.add_argument("--contact-transition-weight", type=float, default=0.02)
    parser.add_argument("--foot-clearance-weight", type=float, default=2.0)
    parser.add_argument("--pitch-weight", type=float, default=4.0)
    parser.add_argument("--height-weight", type=float, default=8.0)
    parser.add_argument("--saturation-weight", type=float, default=0.1)
    parser.add_argument("--actuator-weight", type=float, default=1.0)
    parser.add_argument("--done-margin-weight", type=float, default=0.01)
    parser.add_argument("--done-inside-window-penalty", type=float, default=10.0)
    parser.add_argument("--max-report-modes", type=int, default=80)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = score_traces(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"mode_count={payload['mode_count']}")
    print(f"robust_mode_count={payload['robust_mode_count']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
