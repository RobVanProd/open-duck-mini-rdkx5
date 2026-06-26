#!/usr/bin/env python3
"""Build a compact knee-rate-aware selector source manifest.

This offline helper filters BEST_WALK full-observation windows for moving,
single-support, actuator-envelope-safe snippets with an explicit right-knee
target-rate cap. It records source pointers and coverage summaries only; it
does not copy raw observations/actions, train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from analyze_closed_loop_window_rule_candidates import (
    ROOT,
    command_label,
    contact_code,
    finite,
    fmt,
    read_trace,
    window_metrics,
)


def phase_bin(row: dict[str, Any], bins: int) -> int | None:
    obs = row.get("obs_state")
    if not isinstance(obs, list) or len(obs) < 101:
        return None
    x = obs[99]
    y = obs[100]
    if not (finite(x) and finite(y)):
        return None
    if abs(float(x)) < 1.0e-9 and abs(float(y)) < 1.0e-9:
        return None
    angle = math.atan2(float(y), float(x))
    if angle < 0.0:
        angle += 2.0 * math.pi
    return int((angle / (2.0 * math.pi)) * bins) % bins


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


def entry_id(entry: dict[str, Any]) -> str:
    keys = {
        "source_path": entry["source_path"],
        "start_tick": entry["start_tick"],
        "end_tick": entry["end_tick"],
        "selector_mode": entry["selector_mode"],
    }
    return hashlib.sha256(json.dumps(keys, sort_keys=True).encode()).hexdigest()[:16]


def is_selected(window: dict[str, Any], args: argparse.Namespace) -> bool:
    if window.get("tier") != "PASS_CURATED_CLOSED_LOOP_WINDOW":
        return False
    if (window.get("right_knee_target_velocity_p95_rad_s") or 999.0) > args.max_right_knee_p95:
        return False
    if (window.get("pitch_target_velocity_p95_rad_s") or 999.0) > args.envelope_high:
        return False
    return True


def make_entry(path: Path, rows: list[dict[str, Any]], start: int, window: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    span = rows[start : start + args.window_samples]
    center = span[len(span) // 2]
    contact = majority_contact(span)
    entry = {
        "selector_mode": "knee_rate_aware_closed_loop",
        "source_path": str(path),
        "source_name": path.parent.name,
        "command_cell": command_label(path),
        "seed": window.get("seed"),
        "start_tick": window.get("start_tick"),
        "end_tick": window.get("end_tick"),
        "samples": window.get("samples"),
        "center_tick": center.get("tick"),
        "center_contact": contact_code(center),
        "majority_contact": contact,
        "stance_side": side_label(contact),
        "phase_bin": phase_bin(center, args.phase_bins),
        "mean_vx_m_s": window.get("mean_vx_m_s"),
        "single_support_pct": window.get("single_support_pct"),
        "moving_in_envelope_pct": window.get("moving_in_envelope_pct"),
        "moving_single_in_envelope_pct": window.get("moving_single_in_envelope_pct"),
        "pitch_target_velocity_p95_rad_s": window.get("pitch_target_velocity_p95_rad_s"),
        "right_knee_target_velocity_p95_rad_s": window.get("right_knee_target_velocity_p95_rad_s"),
        "left_knee_target_velocity_p95_rad_s": window.get("left_knee_target_velocity_p95_rad_s"),
        "action_delta_p95": (window.get("action_delta") or {}).get("p95"),
    }
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
            window = window_metrics(path, rows, start, args)
            counters["windows_scored"] += 1
            if window.get("tier") == "PASS_CURATED_CLOSED_LOOP_WINDOW":
                counters["pass_windows"] += 1
            if is_selected(window, args):
                counters["selected_windows"] += 1
                entries.append(make_entry(path, rows, start, window, args))
    return entries, dict(counters)


def coverage(entries: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    by_command: dict[str, Counter[str]] = defaultdict(Counter)
    by_phase: Counter[str] = Counter()
    by_side: Counter[str] = Counter()
    by_command_phase: dict[str, Counter[str]] = defaultdict(Counter)
    for entry in entries:
        command = str(entry.get("command_cell"))
        side = str(entry.get("stance_side"))
        phase = entry.get("phase_bin")
        phase_key = "unknown" if phase is None else str(int(phase))
        by_command[command][side] += 1
        by_phase[phase_key] += 1
        by_side[side] += 1
        by_command_phase[command][phase_key] += 1
    known_phase_bins = {int(key) for key in by_phase if key.isdigit()}
    return {
        "entries": len(entries),
        "phase_bins": args.phase_bins,
        "covered_phase_bins": sorted(known_phase_bins),
        "covered_phase_bin_count": len(known_phase_bins),
        "by_command_cell": {key: dict(value) for key, value in sorted(by_command.items())},
        "by_phase_bin": dict(sorted(by_phase.items(), key=lambda item: (not item[0].isdigit(), item[0]))),
        "by_stance_side": dict(by_side.most_common()),
        "by_command_phase_bin": {key: dict(value) for key, value in sorted(by_command_phase.items())},
    }


def manifest_status(entries: list[dict[str, Any]], coverage_payload: dict[str, Any], args: argparse.Namespace) -> str:
    if len(entries) < args.min_entries:
        return "HOLD_SELECTOR_SOURCE_TOO_SMALL"
    sides = set(coverage_payload.get("by_stance_side") or {})
    if not {"left_stance", "right_stance"} <= sides:
        return "HOLD_SELECTOR_MISSING_STANCE_SIDE"
    if coverage_payload.get("covered_phase_bin_count", 0) < args.min_phase_bins:
        return "HOLD_SELECTOR_PHASE_COVERAGE_LOW"
    return "PASS_KNEE_RATE_SELECTOR_SOURCE_READY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    coverage_payload = payload["coverage"]
    lines = [
        "# Knee-Rate-Aware Closed-Loop Selector Manifest",
        "",
        f"status: `{payload['status']}`",
        "",
        "This manifest points to existing BEST_WALK full-observation windows. It does not copy raw samples, train, deploy, SSH, run robot tests, or change runtime behavior.",
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
            f"- entries: `{coverage_payload['entries']}`",
            f"- covered_phase_bins: `{coverage_payload['covered_phase_bins']}`",
            f"- covered_phase_bin_count: `{coverage_payload['covered_phase_bin_count']}` / `{coverage_payload['phase_bins']}`",
            "",
            "### By Stance Side",
            "",
        ]
    )
    for side, count in coverage_payload["by_stance_side"].items():
        lines.append(f"- {side}: `{count}`")
    lines.extend(["", "### By Command Cell", "", "| command_cell | left_stance | right_stance | double | other |", "|---|---:|---:|---:|---:|"])
    for command, counts in coverage_payload["by_command_cell"].items():
        other = sum(value for key, value in counts.items() if key not in {"left_stance", "right_stance", "double"})
        lines.append(
            f"| {command} | {counts.get('left_stance', 0)} | {counts.get('right_stance', 0)} | {counts.get('double', 0)} | {other} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if payload["status"] == "PASS_KNEE_RATE_SELECTOR_SOURCE_READY":
        lines.extend(
            [
                "- This manifest has enough stance-side and phase coverage to prototype a selector source.",
                "- It does not mean the examples are temporally continuous or ready for BC by themselves.",
                "- The next required gate is a 25-50 tick selector replay/continuity score before any training or export.",
            ]
        )
    elif payload["status"] == "HOLD_SELECTOR_MISSING_STANCE_SIDE":
        lines.extend(
            [
                "- The source is not balanced enough for selector training: at least one stance side is missing.",
                "- Do not train from this manifest. Investigate why safe BEST_WALK windows collapse to one stance side plus double support.",
                "- The next branch should either recover the missing stance side or use a different closed-loop mechanism source.",
            ]
        )
    elif payload["status"] == "HOLD_SELECTOR_PHASE_COVERAGE_LOW":
        lines.extend(
            [
                "- The source does not cover enough phase bins for a phase-aware selector.",
                "- Do not train from this manifest without adding coverage or changing the selector design.",
            ]
        )
    else:
        lines.append("- The selector source is not ready for training or export.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace-glob",
        action="append",
        default=[],
        help="Trace glob. May be passed multiple times.",
    )
    parser.add_argument("--output-md", default="outputs/analysis/KNEE_RATE_SELECTOR_MANIFEST.md")
    parser.add_argument("--output-json", default="outputs/analysis/knee_rate_selector_manifest.json")
    parser.add_argument("--window-samples", type=int, default=10)
    parser.add_argument("--stride-samples", type=int, default=2)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--future-ticks", type=int, default=5)
    parser.add_argument("--envelope-high", type=float, default=3.75)
    parser.add_argument("--max-right-knee-p95", type=float, default=3.61)
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
            "max_right_knee_p95": args.max_right_knee_p95,
            "min_mean_vx": args.min_mean_vx,
            "min_single_support_pct": args.min_single_support_pct,
            "min_moving_in_envelope_pct": args.min_moving_in_envelope_pct,
            "min_moving_single_in_envelope_pct": args.min_moving_single_in_envelope_pct,
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
