#!/usr/bin/env python3
"""Test whether right-knee rate relabeling recovers unsafe left-stance windows.

This is an offline target-sequence analysis. It does not step simulation. It
copies existing BEST_WALK windows, applies a right-knee target-rate cap inside
the window, re-scores the window with the normal movement/contact/envelope
gate, and reports whether the left-stance gap is plausibly recoverable by
right-knee relabeling alone.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import glob
import json
from pathlib import Path
from typing import Any

from analyze_closed_loop_window_rule_candidates import (
    JOINT_NAMES,
    ROOT,
    classify,
    contact_code,
    finite,
    fmt,
    read_trace,
    window_metrics,
)
from analyze_left_stance_gap import group_key, side_label


RIGHT_KNEE_INDEX = JOINT_NAMES.index("right_knee")


def cap_right_knee_targets(rows: list[dict[str, Any]], cap_rad_s: float, dt_s: float) -> list[dict[str, Any]]:
    capped = copy.deepcopy(rows)
    previous: float | None = None
    max_step = cap_rad_s * dt_s
    for row in capped:
        target = row.get("sent_target_rad")
        if not isinstance(target, list) or len(target) <= RIGHT_KNEE_INDEX or not finite(target[RIGHT_KNEE_INDEX]):
            previous = None
            continue
        current = float(target[RIGHT_KNEE_INDEX])
        if previous is not None:
            delta = current - previous
            if delta > max_step:
                current = previous + max_step
            elif delta < -max_step:
                current = previous - max_step
            target[RIGHT_KNEE_INDEX] = current
        previous = current
    return capped


def left_related(center_side: str, majority_side: str) -> bool:
    return center_side == "left_stance" or majority_side == "left_stance"


def relabeled_window(path: Path, rows: list[dict[str, Any]], start: int, args: argparse.Namespace) -> dict[str, Any] | None:
    original = window_metrics(path, rows, start, args)
    center_side, majority_side = group_key(original, rows, start)
    if not left_related(center_side, majority_side):
        return None
    span = rows[start : start + args.window_samples]
    capped_span = cap_right_knee_targets(span, args.right_knee_cap, args.dt_s)
    relabeled = window_metrics(path, capped_span, 0, args)
    tier, reasons = classify(relabeled, args)
    relabeled["tier"] = tier
    relabeled["reasons"] = reasons
    return {
        "source_path": str(path),
        "source_name": path.parent.name,
        "seed": original.get("seed"),
        "start_tick": original.get("start_tick"),
        "end_tick": original.get("end_tick"),
        "center_side": center_side,
        "majority_side": majority_side,
        "original_tier": original.get("tier"),
        "original_reasons": original.get("reasons"),
        "original_pitch_p95": original.get("pitch_target_velocity_p95_rad_s"),
        "original_right_knee_p95": original.get("right_knee_target_velocity_p95_rad_s"),
        "original_left_knee_p95": original.get("left_knee_target_velocity_p95_rad_s"),
        "relabeled_tier": relabeled.get("tier"),
        "relabeled_reasons": relabeled.get("reasons"),
        "relabeled_pitch_p95": relabeled.get("pitch_target_velocity_p95_rad_s"),
        "relabeled_right_knee_p95": relabeled.get("right_knee_target_velocity_p95_rad_s"),
        "relabeled_left_knee_p95": relabeled.get("left_knee_target_velocity_p95_rad_s"),
        "mean_vx_m_s": original.get("mean_vx_m_s"),
        "single_support_pct": original.get("single_support_pct"),
        "moving_in_envelope_pct": original.get("moving_in_envelope_pct"),
        "moving_single_in_envelope_pct": original.get("moving_single_in_envelope_pct"),
    }


def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        groups[f"center_{item['center_side']}__majority_{item['majority_side']}"].append(item)
    out = {}
    for key, values in sorted(groups.items()):
        recovered = [item for item in values if item["relabeled_tier"] == "PASS_CURATED_CLOSED_LOOP_WINDOW"]
        out[key] = {
            "windows": len(values),
            "original_pass": sum(1 for item in values if item["original_tier"] == "PASS_CURATED_CLOSED_LOOP_WINDOW"),
            "relabeled_pass": len(recovered),
            "relabeled_pass_pct": 100.0 * len(recovered) / max(len(values), 1),
            "original_reason_counts": dict(Counter(reason for item in values for reason in item.get("original_reasons") or []).most_common()),
            "relabeled_reason_counts": dict(Counter(reason for item in values for reason in item.get("relabeled_reasons") or []).most_common()),
        }
    return out


def status(payload: dict[str, Any], args: argparse.Namespace) -> str:
    total = payload["summary"]["total_left_related_windows"]
    recovered = payload["summary"]["relabeled_pass_windows"]
    if total <= 0:
        return "HOLD_NO_LEFT_STANCE_WINDOWS"
    pct = 100.0 * recovered / total
    if pct >= args.min_recovery_pct:
        return "PASS_RIGHT_KNEE_RELABEL_RECOVERS_LEFT_STANCE"
    if recovered > 0:
        return "WARN_PARTIAL_RIGHT_KNEE_RELABEL_RECOVERY"
    return "HOLD_RIGHT_KNEE_RELABEL_INSUFFICIENT"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Left-Stance Right-Knee Rate Recovery",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline relabeling analysis of existing BEST_WALK windows. It does not step simulation, train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Filters",
        "",
    ]
    for key, value in payload["filters"].items():
        lines.append(f"- {key}: `{value}`")
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- total_left_related_windows: `{summary['total_left_related_windows']}`",
            f"- original_pass_windows: `{summary['original_pass_windows']}`",
            f"- relabeled_pass_windows: `{summary['relabeled_pass_windows']}`",
            f"- relabeled_pass_pct: `{fmt(summary['relabeled_pass_pct'])}`",
            "",
            "## By Contact Group",
            "",
            "| group | windows | original_pass | relabeled_pass | relabeled_pass_% | top remaining reasons |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for key, item in payload["groups"].items():
        reasons = ", ".join(
            f"{reason}:{count}" for reason, count in list(item["relabeled_reason_counts"].items())[:3]
        )
        lines.append(
            f"| {key} | {item['windows']} | {item['original_pass']} | {item['relabeled_pass']} | {fmt(item['relabeled_pass_pct'])} | {reasons} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A pass here means right-knee relabeling can create enough left-stance candidate windows to justify a selector/replay prototype.",
            "- A hold means the left-stance problem is not solved by right-knee rate capping alone and needs a different source or dynamics-aware recovery.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", default=[])
    parser.add_argument("--output-md", default="outputs/analysis/LEFT_STANCE_RATE_RECOVERY.md")
    parser.add_argument("--output-json", default="outputs/analysis/left_stance_rate_recovery.json")
    parser.add_argument("--window-samples", type=int, default=10)
    parser.add_argument("--stride-samples", type=int, default=2)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--future-ticks", type=int, default=5)
    parser.add_argument("--envelope-high", type=float, default=3.75)
    parser.add_argument("--right-knee-cap", type=float, default=3.61)
    parser.add_argument("--min-recovery-pct", type=float, default=20.0)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--min-tick-vx", type=float, default=0.04)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-moving-in-envelope-pct", type=float, default=40.0)
    parser.add_argument("--min-moving-single-in-envelope-pct", type=float, default=10.0)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.20)
    parser.add_argument("--max-body-pitch-abs-p95", type=float, default=0.20)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    args = parser.parse_args()
    if not args.trace_glob:
        args.trace_glob = ["outputs/analysis/published_policy_command_*_seed*/trace_full_obs_footpos.jsonl"]
    return args


def main() -> int:
    args = parse_args()
    paths: list[Path] = []
    for pattern in args.trace_glob:
        paths.extend(Path(path) for path in glob.glob(str(ROOT / pattern)))
    paths = sorted(set(paths))
    items = []
    for path in paths:
        rows = read_trace(path)
        for start in range(0, max(len(rows) - args.window_samples + 1, 0), args.stride_samples):
            item = relabeled_window(path, rows, start, args)
            if item is not None:
                items.append(item)
    original_pass = sum(1 for item in items if item["original_tier"] == "PASS_CURATED_CLOSED_LOOP_WINDOW")
    relabeled_pass = sum(1 for item in items if item["relabeled_tier"] == "PASS_CURATED_CLOSED_LOOP_WINDOW")
    payload = {
        "filters": {
            "window_samples": args.window_samples,
            "stride_samples": args.stride_samples,
            "envelope_high": args.envelope_high,
            "right_knee_cap": args.right_knee_cap,
            "min_recovery_pct": args.min_recovery_pct,
        },
        "summary": {
            "total_left_related_windows": len(items),
            "original_pass_windows": original_pass,
            "relabeled_pass_windows": relabeled_pass,
            "relabeled_pass_pct": 100.0 * relabeled_pass / max(len(items), 1),
        },
        "groups": summarize(items),
    }
    payload["status"] = status(payload, args)
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={payload['status']}")
    print(f"left_related_windows={len(items)}")
    print(f"relabeled_pass_windows={relabeled_pass}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
