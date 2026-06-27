#!/usr/bin/env python3
"""Score continuity of the relabelled balanced selector manifest.

This offline gate groups selected manifest windows by source trace, merges
overlapping or nearby entries, applies the same right-knee target-rate cap to
the merged span, and re-scores whether 25/50 tick spans remain movement/contact
and actuator-envelope compatible.
"""

from __future__ import annotations

import argparse
import copy
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

from analyze_closed_loop_window_rule_candidates import ROOT, classify, fmt, read_trace, window_metrics
from analyze_left_stance_rate_recovery import cap_right_knee_targets


def merge_entries(entries: list[dict[str, Any]], allowed_gap_ticks: int) -> list[dict[str, Any]]:
    ordered = sorted(entries, key=lambda item: int(item["start_tick"]))
    runs: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for entry in ordered:
        start = int(entry["start_tick"])
        end = int(entry["end_tick"])
        if current is None or start > int(current["end_tick"]) + allowed_gap_ticks + 1:
            if current is not None:
                runs.append(current)
            current = {
                "source_path": entry["source_path"],
                "source_name": entry["source_name"],
                "start_tick": start,
                "end_tick": end,
                "entry_count": 1,
                "entry_ids": [entry["entry_id"]],
                "relabel_modes": [entry.get("relabel")],
            }
        else:
            current["end_tick"] = max(int(current["end_tick"]), end)
            current["entry_count"] += 1
            current["entry_ids"].append(entry["entry_id"])
            current["relabel_modes"].append(entry.get("relabel"))
    if current is not None:
        runs.append(current)
    for run in runs:
        run["span_ticks"] = int(run["end_tick"]) - int(run["start_tick"]) + 1
        run["uses_relabel"] = any(mode != "none" for mode in run["relabel_modes"])
    return runs


def evaluate_run(run: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    path = Path(run["source_path"])
    rows = read_trace(path)
    tick_to_index = {int(row.get("tick", index)): index for index, row in enumerate(rows)}
    start_index = tick_to_index.get(int(run["start_tick"]))
    end_index = tick_to_index.get(int(run["end_tick"]))
    if start_index is None or end_index is None or end_index < start_index:
        out = dict(run)
        out.update({"tier": "REJECT_SELECTOR_RUN", "reasons": ["tick_index_missing"]})
        return out
    span = rows[start_index : end_index + 1]
    if args.apply_right_knee_cap:
        span = cap_right_knee_targets(span, args.right_knee_cap, args.dt_s)
    span_args = copy.copy(args)
    span_args.window_samples = len(span)
    metrics = window_metrics(path, span, 0, span_args)
    tier, reasons = classify(metrics, span_args)
    out = {**run, **metrics}
    out["selector_run_tier"] = tier.replace("PASS_CURATED_CLOSED_LOOP_WINDOW", "PASS_SELECTOR_RUN")
    out["selector_run_reasons"] = reasons
    return out


def compact_run(run: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "source_name",
        "start_tick",
        "end_tick",
        "span_ticks",
        "entry_count",
        "uses_relabel",
        "selector_run_tier",
        "selector_run_reasons",
        "mean_vx_m_s",
        "single_support_pct",
        "moving_in_envelope_pct",
        "moving_single_in_envelope_pct",
        "pitch_target_velocity_p95_rad_s",
        "right_knee_target_velocity_p95_rad_s",
        "left_knee_target_velocity_p95_rad_s",
    ]
    return {key: run.get(key) for key in keys}


def aggregate(runs: list[dict[str, Any]]) -> dict[str, Any]:
    pass_runs = [run for run in runs if run.get("selector_run_tier") == "PASS_SELECTOR_RUN"]
    return {
        "runs": len(runs),
        "pass_runs": len(pass_runs),
        "max_run_span_ticks": max((int(run.get("span_ticks") or 0) for run in runs), default=0),
        "max_pass_run_span_ticks": max((int(run.get("span_ticks") or 0) for run in pass_runs), default=0),
        "pass_run_25_count": sum(1 for run in pass_runs if int(run.get("span_ticks") or 0) >= 25),
        "pass_run_50_count": sum(1 for run in pass_runs if int(run.get("span_ticks") or 0) >= 50),
        "pass_run_with_relabel_count": sum(1 for run in pass_runs if run.get("uses_relabel")),
    }


def status(summary: dict[str, Any]) -> str:
    if summary["pass_run_50_count"] > 0:
        return "PASS_SELECTOR_CONTINUITY_50_TICKS"
    if summary["pass_run_25_count"] > 0:
        return "WARN_SELECTOR_CONTINUITY_25_TICKS"
    if summary["pass_runs"] > 0:
        return "HOLD_SELECTOR_CONTINUITY_TOO_SHORT"
    return "HOLD_NO_PASSING_SELECTOR_RUNS"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# Relabelled Selector Continuity Score",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline continuity score over the relabelled balanced selector manifest. It does not train, step simulation, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Summary",
        "",
        f"- runs: `{summary['runs']}`",
        f"- pass_runs: `{summary['pass_runs']}`",
        f"- max_run_span_ticks: `{summary['max_run_span_ticks']}`",
        f"- max_pass_run_span_ticks: `{summary['max_pass_run_span_ticks']}`",
        f"- pass_run_25_count: `{summary['pass_run_25_count']}`",
        f"- pass_run_50_count: `{summary['pass_run_50_count']}`",
        f"- pass_run_with_relabel_count: `{summary['pass_run_with_relabel_count']}`",
        "",
        "## Longest Passing Runs",
        "",
        "| source | ticks | span | entries | relabel | vx | single_% | move_env_% | move_single_env_% | pitch_p95 | reasons |",
        "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for run in payload.get("top_pass_runs") or []:
        lines.append(
            f"| {run.get('source_name')} | {run.get('start_tick')}-{run.get('end_tick')} | {run.get('span_ticks')} | "
            f"{run.get('entry_count')} | `{run.get('uses_relabel')}` | {fmt(run.get('mean_vx_m_s'))} | "
            f"{fmt(run.get('single_support_pct'))} | {fmt(run.get('moving_in_envelope_pct'))} | "
            f"{fmt(run.get('moving_single_in_envelope_pct'))} | {fmt(run.get('pitch_target_velocity_p95_rad_s'))} | "
            f"`{', '.join(run.get('selector_run_reasons') or [])}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Passing 25-50 ticks here means the balanced manifest has temporally local source runs worth replaying in sim.",
            "- A hold means the source has coverage but still lacks sustained continuity and needs a selector/generator before training.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="outputs/analysis/relabelled_balanced_selector_manifest.json")
    parser.add_argument("--output-md", default="outputs/analysis/RELABELLED_SELECTOR_CONTINUITY_SCORE.md")
    parser.add_argument("--output-json", default="outputs/analysis/relabelled_selector_continuity_score.json")
    parser.add_argument("--allowed-gap-ticks", type=int, default=2)
    parser.add_argument("--apply-right-knee-cap", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--right-knee-cap", type=float, default=3.61)
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads((ROOT / args.manifest).read_text())
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in manifest.get("entries") or []:
        by_source[str(entry["source_path"])].append(entry)
    runs = []
    for entries in by_source.values():
        for run in merge_entries(entries, args.allowed_gap_ticks):
            runs.append(evaluate_run(run, args))
    runs.sort(
        key=lambda item: (
            int(item.get("span_ticks") or 0),
            float(item.get("mean_vx_m_s") or -1.0),
        ),
        reverse=True,
    )
    summary = aggregate(runs)
    payload = {
        "status": status(summary),
        "manifest": args.manifest,
        "manifest_status": manifest.get("status"),
        "manifest_dataset_id": manifest.get("dataset_id"),
        "filters": {
            "allowed_gap_ticks": args.allowed_gap_ticks,
            "apply_right_knee_cap": args.apply_right_knee_cap,
            "right_knee_cap": args.right_knee_cap,
        },
        "summary": summary,
        "top_pass_runs": [compact_run(run) for run in runs if run.get("selector_run_tier") == "PASS_SELECTOR_RUN"][:50],
        "top_runs": [compact_run(run) for run in runs[:50]],
    }
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={payload['status']}")
    print(f"runs={summary['runs']}")
    print(f"max_pass_run_span_ticks={summary['max_pass_run_span_ticks']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
