#!/usr/bin/env python3
"""Summarize weight-transfer target-source score artifacts.

This is an offline reporting helper. It reads compact JSON artifacts produced
by score_target_candidates_objective.py and writes a campaign-level markdown/JSON
summary. It does not run simulation, train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "WEIGHT_TRANSFER_TARGET_CAMPAIGN_SUMMARY.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "weight_transfer_target_campaign_summary.json"
DEFAULT_SCORE_JSONS = [
    "outputs/analysis/target_objective_score_weight_transfer_dynamic_roll_lateral_fix_100.json",
    "outputs/analysis/target_objective_score_weight_transfer_dynamic_roll_lateral_fix_150.json",
    "outputs/analysis/target_objective_score_weight_transfer_probe_100.json",
    "outputs/analysis/target_objective_score_weight_transfer_probe_150.json",
    "outputs/analysis/target_objective_score_stance_push_probe_100.json",
    "outputs/analysis/target_objective_score_stance_push_probe_150.json",
    "outputs/analysis/target_objective_score_velocity_feedback_probe_100.json",
    "outputs/analysis/target_objective_score_velocity_feedback_probe_150.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_score_100.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_score_150.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_v2_score_100.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_v2_score_150.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_v3_score_100.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_v3_score_150.json",
    "outputs/analysis/staged_weight_transfer_planner_score_100.json",
    "outputs/analysis/staged_weight_transfer_planner_score_150.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_forward_intent_score_100.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_forward_intent_score_150.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_lateral_refine_score_100.json",
    "outputs/analysis/closed_loop_weight_transfer_teacher_lateral_refine_score_150.json",
    "outputs/analysis/support_state_weight_transfer_probe_score_100.json",
    "outputs/analysis/support_state_weight_transfer_probe_score_150.json",
    "outputs/analysis/support_loaded_weight_transfer_probe_score_100.json",
    "outputs/analysis/support_loaded_weight_transfer_probe_score_150.json",
    "outputs/analysis/com_weight_transfer_controller_probe_score_100.json",
    "outputs/analysis/com_weight_transfer_controller_probe_score_150.json",
    "outputs/analysis/com_weight_transfer_controller_relaxed_probe_score_100.json",
    "outputs/analysis/com_weight_transfer_controller_relaxed_probe_score_150.json",
    "outputs/analysis/com_weight_transfer_controller_stance_probe_score_100.json",
    "outputs/analysis/com_weight_transfer_controller_stance_probe_score_150.json",
    "outputs/analysis/com_weight_transfer_controller_stance_aggressive_probe_score_100.json",
    "outputs/analysis/com_weight_transfer_controller_stance_aggressive_probe_score_150.json",
    "outputs/analysis/com_weight_transfer_controller_stance_reverse_push_probe_score_100.json",
    "outputs/analysis/com_weight_transfer_controller_stance_reverse_push_probe_score_150.json",
]


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def seed_sort_key(seed: str) -> tuple[int, str]:
    digits = "".join(ch for ch in seed if ch.isdigit())
    return (int(digits) if digits else 999999, seed)


def summarize_score(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "label": path.stem,
            "status": "MISSING",
            "missing": True,
        }
    payload = json.loads(path.read_text())
    top = (payload.get("results") or [{}])[0]
    seed_rows = []
    for seed, row in sorted((top.get("seeds") or {}).items(), key=lambda item: seed_sort_key(item[0])):
        seed_rows.append(
            {
                "seed": seed,
                "mean_vx_m_s": row.get("mean_vx_m_s"),
                "forward_displacement_m": row.get("forward_displacement_m"),
                "vy_abs_p95_m_s": row.get("vy_abs_p95_m_s"),
                "double_support_pct": row.get("double_support_pct"),
                "single_support_pct": row.get("single_support_pct"),
                "min_single_support_side_pct": row.get("min_single_support_side_pct"),
                "contact_transitions": row.get("contact_transitions"),
                "sent_target_velocity_p95_rad_s": row.get("sent_target_velocity_p95_rad_s"),
                "hard_failures": row.get("hard_failures") or [],
            }
        )
    return {
        "path": str(path),
        "label": path.stem,
        "status": payload.get("status", "UNKNOWN"),
        "missing": False,
        "window_samples": payload.get("window_samples"),
        "mode_count": payload.get("mode_count"),
        "robust_mode_count": payload.get("robust_mode_count"),
        "reason_counts": payload.get("reason_counts") or {},
        "top_mode": top.get("mode"),
        "top_min_seed_score": top.get("min_seed_score"),
        "top_mean_seed_score": top.get("mean_seed_score"),
        "top_seeds": seed_rows,
    }


def aggregate_failures(summaries: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for summary in summaries:
        counts.update(
            {
                key: int(value)
                for key, value in (summary.get("reason_counts") or {}).items()
            }
        )
    return dict(counts.most_common())


def best_seed_metric(summaries: list[dict[str, Any]], key: str, maximize: bool = True) -> dict[str, Any] | None:
    best = None
    for summary in summaries:
        for seed in summary.get("top_seeds") or []:
            value = seed.get(key)
            if value is None:
                continue
            candidate = {
                "label": summary["label"],
                "path": summary["path"],
                "seed": seed["seed"],
                "value": value,
                "seed_row": seed,
            }
            if best is None:
                best = candidate
            elif maximize and float(value) > float(best["value"]):
                best = candidate
            elif not maximize and float(value) < float(best["value"]):
                best = candidate
    return best


def infer_decision(summaries: list[dict[str, Any]]) -> str:
    if any(int(summary.get("robust_mode_count") or 0) > 0 for summary in summaries):
        return "PASS_TARGET_SOURCE_AVAILABLE"
    failures = aggregate_failures(summaries)
    high_lateral = failures.get("high_lateral_velocity", 0)
    low_forward = failures.get("low_forward_velocity", 0) + failures.get(
        "low_forward_displacement", 0
    )
    support = (
        failures.get("double_support_dominates", 0)
        + failures.get("too_little_single_support", 0)
        + failures.get("single_support_not_balanced", 0)
        + failures.get("single_contact_pattern_dominates", 0)
        + failures.get("too_few_contact_transitions", 0)
    )
    if high_lateral and low_forward and support:
        return "HOLD_FORWARD_LATERAL_SUPPORT_TRADEOFF"
    if low_forward and support:
        return "HOLD_FORWARD_AND_SUPPORT_TRANSFER"
    if high_lateral:
        return "HOLD_LATERAL_UNSTABLE"
    if low_forward:
        return "HOLD_FORWARD_STILL_LOW"
    return "HOLD_NO_ROBUST_TARGETS"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Weight-Transfer Target Campaign Summary",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline summary of compact target-source score artifacts. It",
        "does not run simulation, training, robot SSH, deployment, or hardware tests.",
        "",
        "## Score Artifacts",
        "",
        "| label | window | status | robust | modes | top seed0 vx/dx | top seed2 vx/dx | top seed0/seed2 vy95 | top failures |",
        "|---|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for summary in payload["summaries"]:
        if summary.get("missing"):
            lines.append(
                f"| `{summary['label']}` | NA | `MISSING` | NA | NA | NA | NA | NA | missing |"
            )
            continue
        seeds = {seed["seed"]: seed for seed in summary.get("top_seeds", [])}
        seed0 = seeds.get("seed_000") or seeds.get("0") or {}
        seed2 = seeds.get("seed_002") or seeds.get("2") or {}
        failures = sorted(
            set((seed0.get("hard_failures") or []) + (seed2.get("hard_failures") or []))
        )
        lines.append(
            "| `{label}` | {window} | `{status}` | {robust} | {modes} | {s0vx}/{s0dx} | {s2vx}/{s2dx} | {s0vy}/{s2vy} | {failures} |".format(
                label=summary["label"],
                window=summary.get("window_samples", "NA"),
                status=summary.get("status", "UNKNOWN"),
                robust=summary.get("robust_mode_count", "NA"),
                modes=summary.get("mode_count", "NA"),
                s0vx=fmt(seed0.get("mean_vx_m_s")),
                s0dx=fmt(seed0.get("forward_displacement_m")),
                s2vx=fmt(seed2.get("mean_vx_m_s")),
                s2dx=fmt(seed2.get("forward_displacement_m")),
                s0vy=fmt(seed0.get("vy_abs_p95_m_s")),
                s2vy=fmt(seed2.get("vy_abs_p95_m_s")),
                failures=", ".join(failures[:4]) if failures else "none",
            )
        )
    lines.extend(
        [
            "",
            "## Aggregate Failure Counts",
            "",
            "| reason | count |",
            "|---|---:|",
        ]
    )
    for reason, count in payload["aggregate_failures"].items():
        lines.append(f"| `{reason}` | {count} |")
    best_dx = payload.get("best_forward_displacement")
    best_vy = payload.get("best_lateral")
    lines.extend(
        [
            "",
            "## Extremes",
            "",
            f"- best top-window forward displacement: `{fmt(best_dx.get('value') if best_dx else None)}` from `{best_dx.get('label') if best_dx else 'NA'}` / `{best_dx.get('seed') if best_dx else 'NA'}`",
            f"- lowest top-window lateral p95: `{fmt(best_vy.get('value') if best_vy else None)}` from `{best_vy.get('label') if best_vy else 'NA'}` / `{best_vy.get('seed') if best_vy else 'NA'}`",
            "",
            "## Decision",
            "",
            "```text",
            payload["status"],
            "```",
            "",
            "Do not use these artifacts as training permission unless the status is",
            "`PASS_TARGET_SOURCE_AVAILABLE`. Current holds should drive a new",
            "contact/weight-transfer objective or controller structure, not another",
            "nearby prior-scale or teacher-grid expansion.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--score-json",
        action="append",
        default=None,
        help="Score JSON from score_target_candidates_objective.py. May be repeated.",
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    score_jsons = args.score_json or DEFAULT_SCORE_JSONS
    summaries = [summarize_score(resolve(path)) for path in score_jsons]
    present = [summary for summary in summaries if not summary.get("missing")]
    payload = {
        "status": infer_decision(present),
        "score_jsons": [str(resolve(path)) for path in score_jsons],
        "summaries": summaries,
        "aggregate_failures": aggregate_failures(present),
        "best_forward_displacement": best_seed_metric(present, "forward_displacement_m"),
        "best_lateral": best_seed_metric(present, "vy_abs_p95_m_s", maximize=False),
    }
    output_json = resolve(args.output_json)
    output_md = resolve(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, output_md)
    print(f"status: {payload['status']}")
    print(f"wrote: {output_md}")
    print(f"wrote: {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
