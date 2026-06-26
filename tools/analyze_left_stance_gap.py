#!/usr/bin/env python3
"""Analyze why left-stance BEST_WALK windows are missing from safe selectors.

This offline helper scores all short full-observation windows and groups them
by center/majority contact state. It answers whether left-stance windows are
absent, present but high-rate, or present but failing another gate.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import json
from pathlib import Path
from statistics import mean
from typing import Any

from analyze_closed_loop_window_rule_candidates import (
    ROOT,
    command_label,
    contact_code,
    finite,
    fmt,
    read_trace,
    stats,
    window_metrics,
)


def majority_contact(rows: list[dict[str, Any]]) -> str:
    counts = Counter(contact_code(row) for row in rows)
    return counts.most_common(1)[0][0] if counts else "??"


def side_label(code: str) -> str:
    if code == "10":
        return "left_stance"
    if code == "01":
        return "right_stance"
    if code == "11":
        return "double"
    if code == "00":
        return "flight"
    return "unknown"


def collect(items: list[dict[str, Any]], key: str) -> list[float]:
    out = []
    for item in items:
        value = item.get(key)
        if finite(value):
            out.append(float(value))
    return out


def group_key(window: dict[str, Any], rows: list[dict[str, Any]], start: int) -> tuple[str, str]:
    span = rows[start : start + window["samples"]]
    center = span[len(span) // 2]
    return side_label(contact_code(center)), side_label(majority_contact(span))


def summarize_group(items: list[dict[str, Any]]) -> dict[str, Any]:
    reasons = Counter(reason for item in items for reason in item.get("reasons") or [])
    buckets = Counter(item.get("rule_bucket") for item in items)
    commands = Counter(item.get("command_cell") for item in items)
    pass_count = sum(1 for item in items if item.get("tier") == "PASS_CURATED_CLOSED_LOOP_WINDOW")
    return {
        "windows": len(items),
        "pass_windows": pass_count,
        "pass_pct": 100.0 * pass_count / max(len(items), 1),
        "rule_buckets": dict(buckets.most_common()),
        "commands": dict(commands.most_common()),
        "reasons": dict(reasons.most_common()),
        "mean_vx_m_s": stats(collect(items, "mean_vx_m_s")),
        "single_support_pct": stats(collect(items, "single_support_pct")),
        "moving_in_envelope_pct": stats(collect(items, "moving_in_envelope_pct")),
        "moving_single_in_envelope_pct": stats(collect(items, "moving_single_in_envelope_pct")),
        "pitch_target_velocity_p95_rad_s": stats(collect(items, "pitch_target_velocity_p95_rad_s")),
        "right_knee_target_velocity_p95_rad_s": stats(collect(items, "right_knee_target_velocity_p95_rad_s")),
        "left_knee_target_velocity_p95_rad_s": stats(collect(items, "left_knee_target_velocity_p95_rad_s")),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    paths: list[Path] = []
    for pattern in args.trace_glob:
        paths.extend(Path(path) for path in glob.glob(str(ROOT / pattern)))
    paths = sorted(set(paths))
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    left_examples: list[dict[str, Any]] = []
    counters = Counter()
    for path in paths:
        rows = read_trace(path)
        for start in range(0, max(len(rows) - args.window_samples + 1, 0), args.stride_samples):
            window = window_metrics(path, rows, start, args)
            center_side, majority_side = group_key(window, rows, start)
            window["center_side"] = center_side
            window["majority_side"] = majority_side
            groups[(center_side, majority_side)].append(window)
            counters["windows"] += 1
            if center_side == "left_stance" or majority_side == "left_stance":
                counters["left_related_windows"] += 1
                if len(left_examples) < args.example_limit:
                    left_examples.append(
                        {
                            "source_name": window["source_name"],
                            "command_cell": command_label(path),
                            "seed": window.get("seed"),
                            "start_tick": window.get("start_tick"),
                            "end_tick": window.get("end_tick"),
                            "center_side": center_side,
                            "majority_side": majority_side,
                            "tier": window.get("tier"),
                            "rule_bucket": window.get("rule_bucket"),
                            "reasons": window.get("reasons"),
                            "mean_vx_m_s": window.get("mean_vx_m_s"),
                            "pitch_target_velocity_p95_rad_s": window.get("pitch_target_velocity_p95_rad_s"),
                            "right_knee_target_velocity_p95_rad_s": window.get("right_knee_target_velocity_p95_rad_s"),
                            "left_knee_target_velocity_p95_rad_s": window.get("left_knee_target_velocity_p95_rad_s"),
                        }
                    )
    summary = {
        f"center_{center}__majority_{majority}": summarize_group(items)
        for (center, majority), items in sorted(groups.items())
    }
    return {
        "paths": [str(path) for path in paths],
        "counters": dict(counters),
        "groups": summary,
        "left_examples": left_examples,
    }


def result_status(payload: dict[str, Any]) -> str:
    groups = payload["groups"]
    left_groups = [value for key, value in groups.items() if "left_stance" in key]
    if not left_groups:
        return "HOLD_LEFT_STANCE_ABSENT"
    left_pass = sum(group.get("pass_windows", 0) for group in left_groups)
    if left_pass == 0:
        return "HOLD_LEFT_STANCE_PRESENT_BUT_UNSAFE"
    return "WARN_LEFT_STANCE_EXISTS_BUT_NOT_IN_SELECTOR"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Left-Stance Gap Analysis",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline analysis of existing BEST_WALK full-observation traces. It does not train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Summary",
        "",
        f"- windows: `{payload['counters'].get('windows', 0)}`",
        f"- left_related_windows: `{payload['counters'].get('left_related_windows', 0)}`",
        "",
        "## Contact-Side Groups",
        "",
        "| group | windows | pass | pass_% | vx | pitch_p95 | right_knee_p95 | left_knee_p95 | top reasons |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for key, item in payload["groups"].items():
        top_reasons = ", ".join(f"{reason}:{count}" for reason, count in list(item["reasons"].items())[:3])
        lines.append(
            f"| {key} | {item['windows']} | {item['pass_windows']} | {fmt(item['pass_pct'])} | "
            f"{fmt(item['mean_vx_m_s']['mean'])} | {fmt(item['pitch_target_velocity_p95_rad_s']['mean'])} | "
            f"{fmt(item['right_knee_target_velocity_p95_rad_s']['mean'])} | {fmt(item['left_knee_target_velocity_p95_rad_s']['mean'])} | {top_reasons} |"
        )
    lines.extend(
        [
            "",
            "## Left-Stance Examples",
            "",
            "| source | ticks | bucket | reasons | vx | pitch_p95 | right_knee_p95 | left_knee_p95 |",
            "|---|---:|---|---|---:|---:|---:|---:|",
        ]
    )
    for item in payload.get("left_examples") or []:
        lines.append(
            f"| {item['source_name']} | {item['start_tick']}-{item['end_tick']} | {item['rule_bucket']} | "
            f"{', '.join(item.get('reasons') or [])} | {fmt(item.get('mean_vx_m_s'))} | "
            f"{fmt(item.get('pitch_target_velocity_p95_rad_s'))} | {fmt(item.get('right_knee_target_velocity_p95_rad_s'))} | "
            f"{fmt(item.get('left_knee_target_velocity_p95_rad_s'))} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- If left stance is absent, the selector source must be mirrored/recovered from another source before training.",
            "- If left stance exists but is unsafe, the next branch should target the specific failing reason instead of training from the one-sided source.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", default=[])
    parser.add_argument("--output-md", default="outputs/analysis/LEFT_STANCE_GAP_ANALYSIS.md")
    parser.add_argument("--output-json", default="outputs/analysis/left_stance_gap_analysis.json")
    parser.add_argument("--window-samples", type=int, default=10)
    parser.add_argument("--stride-samples", type=int, default=2)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--future-ticks", type=int, default=5)
    parser.add_argument("--envelope-high", type=float, default=3.75)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--min-tick-vx", type=float, default=0.04)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-moving-in-envelope-pct", type=float, default=40.0)
    parser.add_argument("--min-moving-single-in-envelope-pct", type=float, default=10.0)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.20)
    parser.add_argument("--max-body-pitch-abs-p95", type=float, default=0.20)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--example-limit", type=int, default=20)
    args = parser.parse_args()
    if not args.trace_glob:
        args.trace_glob = ["outputs/analysis/published_policy_command_*_seed*/trace_full_obs_footpos.jsonl"]
    return args


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    payload["status"] = result_status(payload)
    payload["criteria"] = {
        "window_samples": args.window_samples,
        "stride_samples": args.stride_samples,
        "envelope_high": args.envelope_high,
        "min_mean_vx": args.min_mean_vx,
        "min_single_support_pct": args.min_single_support_pct,
    }
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={payload['status']}")
    print(f"windows={payload['counters'].get('windows', 0)}")
    print(f"left_related_windows={payload['counters'].get('left_related_windows', 0)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
