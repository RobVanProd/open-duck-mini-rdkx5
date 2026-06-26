#!/usr/bin/env python3
"""Build a replay manifest from the top relabelled selector continuity runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_closed_loop_window_rule_candidates import ROOT


def entry_id(entry: dict[str, Any]) -> str:
    keys = {
        "source_path": entry["source_path"],
        "start_tick": entry["start_tick"],
        "end_tick": entry["end_tick"],
        "relabel": entry["relabel"],
    }
    return hashlib.sha256(json.dumps(keys, sort_keys=True).encode()).hexdigest()[:16]


def build_entry(run: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    source_name = str(run["source_name"])
    source_path = ROOT / "outputs" / "analysis" / source_name / "trace_full_obs_footpos.jsonl"
    entry = {
        "selector_mode": "relabelled_selector_continuity_replay",
        "mode": "vanilla",
        "relabel": "right_knee_rate_cap" if run.get("uses_relabel") else "none",
        "source_path": str(source_path),
        "source_name": source_name,
        "start_tick": int(run["start_tick"]),
        "end_tick": int(run["end_tick"]),
        "samples": int(run["span_ticks"]),
        "right_knee_cap_rad_s": float(args.right_knee_cap),
        "dt_s": float(args.dt_s),
        "action_scale": float(args.action_scale),
        "continuity_metrics": {
            "mean_vx_m_s": run.get("mean_vx_m_s"),
            "single_support_pct": run.get("single_support_pct"),
            "moving_in_envelope_pct": run.get("moving_in_envelope_pct"),
            "moving_single_in_envelope_pct": run.get("moving_single_in_envelope_pct"),
            "pitch_target_velocity_p95_rad_s": run.get("pitch_target_velocity_p95_rad_s"),
            "right_knee_target_velocity_p95_rad_s": run.get("right_knee_target_velocity_p95_rad_s"),
            "left_knee_target_velocity_p95_rad_s": run.get("left_knee_target_velocity_p95_rad_s"),
        },
    }
    entry["entry_id"] = entry_id(entry)
    return entry


def status(entries: list[dict[str, Any]], args: argparse.Namespace) -> str:
    if not entries:
        return "HOLD_NO_SELECTOR_REPLAY_ENTRIES"
    if len(entries) < args.max_runs:
        return "WARN_SELECTOR_REPLAY_ENTRY_COUNT"
    if not any(entry["relabel"] != "none" for entry in entries):
        return "HOLD_SELECTOR_REPLAY_HAS_NO_RELABELLED_SPANS"
    return "PASS_SELECTOR_REPLAY_MANIFEST_READY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Relabelled Selector Replay Manifest",
        "",
        f"status: `{payload['status']}`",
        "",
        "This manifest converts the top continuity-score runs into replayable selector spans. It does not train, step simulation, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Source",
        "",
        f"- continuity_score: `{payload['continuity_score']}`",
        f"- continuity_status: `{payload['continuity_status']}`",
        f"- max_runs: `{payload['filters']['max_runs']}`",
        f"- min_span_ticks: `{payload['filters']['min_span_ticks']}`",
        f"- right_knee_cap_rad_s: `{payload['filters']['right_knee_cap_rad_s']}`",
        "",
        "## Entries",
        "",
        "| source | ticks | span | relabel | vx | single_% | move_env_% | pitch_p95 |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for entry in payload["entries"]:
        metrics = entry["continuity_metrics"]
        lines.append(
            f"| {entry['source_name']} | {entry['start_tick']}-{entry['end_tick']} | "
            f"{entry['samples']} | `{entry['relabel']}` | {fmt(metrics.get('mean_vx_m_s'))} | "
            f"{fmt(metrics.get('single_support_pct'))} | {fmt(metrics.get('moving_in_envelope_pct'))} | "
            f"{fmt(metrics.get('pitch_target_velocity_p95_rad_s'))} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A pass here only means the continuity-score runs were converted into a replay manifest.",
            "- The next gate is closed-loop sim replay with `run_target_sequence_replay_smoke.py`.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.4f}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuity-json", default="outputs/analysis/relabelled_selector_continuity_score.json")
    parser.add_argument("--output-md", default="outputs/analysis/RELABELLED_SELECTOR_REPLAY_MANIFEST.md")
    parser.add_argument("--output-json", default="outputs/analysis/relabelled_selector_replay_manifest.json")
    parser.add_argument("--max-runs", type=int, default=8)
    parser.add_argument("--min-span-ticks", type=int, default=50)
    parser.add_argument("--right-knee-cap", type=float, default=3.61)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--action-scale", type=float, default=0.25)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    continuity_path = ROOT / args.continuity_json
    continuity = json.loads(continuity_path.read_text())
    runs = [
        run
        for run in continuity.get("top_pass_runs") or []
        if int(run.get("span_ticks") or 0) >= args.min_span_ticks
    ][: args.max_runs]
    entries = [build_entry(run, args) for run in runs]
    payload = {
        "status": status(entries, args),
        "dataset_id": hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16],
        "continuity_score": args.continuity_json,
        "continuity_status": continuity.get("status"),
        "filters": {
            "max_runs": args.max_runs,
            "min_span_ticks": args.min_span_ticks,
            "right_knee_cap_rad_s": args.right_knee_cap,
            "dt_s": args.dt_s,
            "action_scale": args.action_scale,
        },
        "entries": entries,
    }
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, output_md)
    print(f"status={payload['status']}")
    print(f"entries={len(entries)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
