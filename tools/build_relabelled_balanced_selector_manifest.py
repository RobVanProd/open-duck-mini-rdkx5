#!/usr/bin/env python3
"""Build a balanced selector manifest with right-knee-relabeled left stance.

This offline helper combines original passing BEST_WALK windows for right/double
support with relabeled left-stance windows recovered by capping right-knee
target rate. It records source pointers and coverage summaries only; it does
not copy raw samples, train, step simulation, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_closed_loop_window_rule_candidates import ROOT, contact_code, read_trace, window_metrics
from analyze_left_stance_gap import group_key
from analyze_left_stance_rate_recovery import cap_right_knee_targets
from build_knee_rate_selector_manifest import phase_bin, side_label


def majority_contact(rows: list[dict[str, Any]]) -> str:
    counts = Counter(contact_code(row) for row in rows)
    return counts.most_common(1)[0][0] if counts else "??"


def entry_id(entry: dict[str, Any]) -> str:
    keys = {
        "source_path": entry["source_path"],
        "start_tick": entry["start_tick"],
        "end_tick": entry["end_tick"],
        "selector_mode": entry["selector_mode"],
        "relabel": entry["relabel"],
    }
    return hashlib.sha256(json.dumps(keys, sort_keys=True).encode()).hexdigest()[:16]


def make_entry(
    path: Path,
    rows: list[dict[str, Any]],
    start: int,
    metrics: dict[str, Any],
    args: argparse.Namespace,
    relabel: str,
    original_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    span = rows[start : start + args.window_samples]
    center = span[len(span) // 2]
    majority = majority_contact(span)
    entry = {
        "selector_mode": "balanced_knee_rate_relabelled_closed_loop",
        "relabel": relabel,
        "source_path": str(path),
        "source_name": path.parent.name,
        "seed": metrics.get("seed"),
        "start_tick": metrics.get("start_tick"),
        "end_tick": metrics.get("end_tick"),
        "samples": metrics.get("samples"),
        "center_tick": center.get("tick"),
        "center_contact": contact_code(center),
        "majority_contact": majority,
        "stance_side": side_label(majority),
        "phase_bin": phase_bin(center, args.phase_bins),
        "mean_vx_m_s": metrics.get("mean_vx_m_s"),
        "single_support_pct": metrics.get("single_support_pct"),
        "moving_in_envelope_pct": metrics.get("moving_in_envelope_pct"),
        "moving_single_in_envelope_pct": metrics.get("moving_single_in_envelope_pct"),
        "pitch_target_velocity_p95_rad_s": metrics.get("pitch_target_velocity_p95_rad_s"),
        "right_knee_target_velocity_p95_rad_s": metrics.get("right_knee_target_velocity_p95_rad_s"),
        "left_knee_target_velocity_p95_rad_s": metrics.get("left_knee_target_velocity_p95_rad_s"),
    }
    if original_metrics is not None:
        entry["original_pitch_target_velocity_p95_rad_s"] = original_metrics.get("pitch_target_velocity_p95_rad_s")
        entry["original_right_knee_target_velocity_p95_rad_s"] = original_metrics.get(
            "right_knee_target_velocity_p95_rad_s"
        )
    entry["entry_id"] = entry_id(entry)
    return entry


def build_entries(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, int]]:
    paths: list[Path] = []
    for pattern in args.trace_glob:
        paths.extend(Path(path) for path in glob.glob(str(ROOT / pattern)))
    paths = sorted(set(paths))
    entries: list[dict[str, Any]] = []
    counters = Counter()
    for path in paths:
        rows = read_trace(path)
        for start in range(0, max(len(rows) - args.window_samples + 1, 0), args.stride_samples):
            original = window_metrics(path, rows, start, args)
            center_side, majority_side = group_key(original, rows, start)
            left_related = center_side == "left_stance" or majority_side == "left_stance"
            counters["windows_scored"] += 1
            if original.get("tier") == "PASS_CURATED_CLOSED_LOOP_WINDOW":
                counters["original_pass_windows"] += 1
            if left_related:
                counters["left_related_windows"] += 1
                span = rows[start : start + args.window_samples]
                relabeled_span = cap_right_knee_targets(span, args.right_knee_cap, args.dt_s)
                relabeled = window_metrics(path, relabeled_span, 0, args)
                if relabeled.get("tier") == "PASS_CURATED_CLOSED_LOOP_WINDOW":
                    counters["relabeled_left_pass_windows"] += 1
                    entries.append(make_entry(path, rows, start, relabeled, args, "right_knee_rate_cap", original))
            elif original.get("tier") == "PASS_CURATED_CLOSED_LOOP_WINDOW":
                counters["original_nonleft_pass_windows"] += 1
                entries.append(make_entry(path, rows, start, original, args, "none", original))
    return entries, dict(counters)


def coverage(entries: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    by_side = Counter(str(entry.get("stance_side")) for entry in entries)
    by_relabel = Counter(str(entry.get("relabel")) for entry in entries)
    by_phase = Counter("unknown" if entry.get("phase_bin") is None else str(entry["phase_bin"]) for entry in entries)
    by_command_side: dict[str, Counter[str]] = defaultdict(Counter)
    for entry in entries:
        by_command_side[str(entry.get("source_name")).rsplit("_seed", 1)[0]][str(entry.get("stance_side"))] += 1
    phase_bins = {int(key) for key in by_phase if key.isdigit()}
    return {
        "entries": len(entries),
        "by_stance_side": dict(by_side.most_common()),
        "by_relabel": dict(by_relabel.most_common()),
        "covered_phase_bins": sorted(phase_bins),
        "covered_phase_bin_count": len(phase_bins),
        "phase_bins": args.phase_bins,
        "by_phase_bin": dict(sorted(by_phase.items(), key=lambda item: (not item[0].isdigit(), item[0]))),
        "by_command_side": {key: dict(value) for key, value in sorted(by_command_side.items())},
    }


def manifest_status(entries: list[dict[str, Any]], coverage_payload: dict[str, Any], args: argparse.Namespace) -> str:
    if len(entries) < args.min_entries:
        return "HOLD_BALANCED_SELECTOR_SOURCE_TOO_SMALL"
    sides = set(coverage_payload.get("by_stance_side") or {})
    if not {"left_stance", "right_stance"} <= sides:
        return "HOLD_BALANCED_SELECTOR_STANCE_COVERAGE"
    if coverage_payload.get("covered_phase_bin_count", 0) < args.min_phase_bins:
        return "HOLD_BALANCED_SELECTOR_PHASE_COVERAGE"
    return "PASS_BALANCED_SELECTOR_SOURCE_READY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    cov = payload["coverage"]
    lines = [
        "# Relabelled Balanced Selector Manifest",
        "",
        f"status: `{payload['status']}`",
        "",
        "This manifest points to existing BEST_WALK windows and marks relabeled left-stance windows. It does not copy raw samples, train, step simulation, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Filters",
        "",
    ]
    for key, value in payload["filters"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Coverage",
            "",
            f"- entries: `{cov['entries']}`",
            f"- covered_phase_bins: `{cov['covered_phase_bins']}`",
            f"- covered_phase_bin_count: `{cov['covered_phase_bin_count']}` / `{cov['phase_bins']}`",
            "",
            "### By Stance Side",
            "",
        ]
    )
    for key, value in cov["by_stance_side"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "### By Relabel Mode", ""])
    for key, value in cov["by_relabel"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Passing this manifest means the source has enough left/right stance and phase coverage to prototype a selector replay.",
            "- It still has not been stepped in sim and is not training-ready by itself.",
            "- The next required artifact is a 25-50 tick continuity/replay score using these entries.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", default=[])
    parser.add_argument("--output-md", default="outputs/analysis/RELABELLED_BALANCED_SELECTOR_MANIFEST.md")
    parser.add_argument("--output-json", default="outputs/analysis/relabelled_balanced_selector_manifest.json")
    parser.add_argument("--window-samples", type=int, default=10)
    parser.add_argument("--stride-samples", type=int, default=2)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--future-ticks", type=int, default=5)
    parser.add_argument("--envelope-high", type=float, default=3.75)
    parser.add_argument("--right-knee-cap", type=float, default=3.61)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--min-tick-vx", type=float, default=0.04)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-moving-in-envelope-pct", type=float, default=40.0)
    parser.add_argument("--min-moving-single-in-envelope-pct", type=float, default=10.0)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.20)
    parser.add_argument("--max-body-pitch-abs-p95", type=float, default=0.20)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--phase-bins", type=int, default=8)
    parser.add_argument("--min-phase-bins", type=int, default=6)
    parser.add_argument("--min-entries", type=int, default=100)
    args = parser.parse_args()
    if not args.trace_glob:
        args.trace_glob = ["outputs/analysis/published_policy_command_*_seed*/trace_full_obs_footpos.jsonl"]
    return args


def main() -> int:
    args = parse_args()
    entries, counters = build_entries(args)
    coverage_payload = coverage(entries, args)
    payload = {
        "status": manifest_status(entries, coverage_payload, args),
        "dataset_id": hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16],
        "trace_globs": args.trace_glob,
        "filters": {
            "window_samples": args.window_samples,
            "stride_samples": args.stride_samples,
            "envelope_high": args.envelope_high,
            "right_knee_cap": args.right_knee_cap,
            "min_entries": args.min_entries,
            "min_phase_bins": args.min_phase_bins,
        },
        "counters": counters,
        "coverage": coverage_payload,
        "entries": entries,
    }
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={payload['status']}")
    print(f"dataset_id={payload['dataset_id']}")
    print(f"entries={len(entries)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
