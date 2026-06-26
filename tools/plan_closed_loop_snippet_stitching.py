#!/usr/bin/env python3
"""Plan whether closed-loop snippets can be stitched into longer windows.

This is an offline analysis helper. It re-mines short passing snippets from
published-policy traces, merges overlapping or nearby snippets, and evaluates
whether the resulting contiguous spans can reach longer 25/50 tick horizons
without reintroducing target-rate or support failures.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import json
from pathlib import Path
from typing import Any

from mine_closed_loop_teacher_windows import (
    ROOT,
    classify,
    command_label,
    contact_code,
    finite,
    fmt,
    mine_trace,
    pitch_velocity_by_tick,
    read_trace,
    window_metrics,
)


def merge_pass_windows(windows: list[dict[str, Any]], allowed_gap_ticks: int) -> list[dict[str, Any]]:
    pass_windows = sorted(
        [window for window in windows if window.get("tier") == "PASS_CURATED_CLOSED_LOOP_WINDOW"],
        key=lambda item: int(item.get("start_tick") or 0),
    )
    runs: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for window in pass_windows:
        start = int(window["start_tick"])
        end = int(window["end_tick"])
        if current is None or start > int(current["end_tick"]) + allowed_gap_ticks + 1:
            if current is not None:
                runs.append(current)
            current = {
                "start_tick": start,
                "end_tick": end,
                "snippet_count": 1,
                "snippet_ticks": [(start, end)],
            }
        else:
            current["end_tick"] = max(int(current["end_tick"]), end)
            current["snippet_count"] += 1
            current["snippet_ticks"].append((start, end))
    if current is not None:
        runs.append(current)
    for run in runs:
        run["span_ticks"] = int(run["end_tick"]) - int(run["start_tick"]) + 1
    return runs


def evaluate_run(
    run: dict[str, Any],
    rows: list[dict[str, Any]],
    velocities: list[float | None],
    args: argparse.Namespace,
    path: Path,
) -> dict[str, Any]:
    start_tick = int(run["start_tick"])
    end_tick = int(run["end_tick"])
    tick_to_index = {int(row.get("tick", index)): index for index, row in enumerate(rows)}
    start_index = tick_to_index.get(start_tick)
    end_index = tick_to_index.get(end_tick)
    if start_index is None or end_index is None or end_index < start_index:
        metrics = dict(run)
        metrics.update({"tier": "REJECT_STITCH_RUN", "reasons": ["tick_index_missing"]})
        return metrics
    samples = end_index - start_index + 1
    metrics = window_metrics(rows, velocities, start_index, samples, args, path)
    tier, reasons = classify(metrics, args)
    metrics.update(
        {
            "stitch_tier": tier.replace("PASS_CURATED_CLOSED_LOOP_WINDOW", "PASS_STITCH_RUN"),
            "stitch_reasons": reasons,
            "snippet_count": run["snippet_count"],
            "snippet_ticks": run["snippet_ticks"],
            "span_ticks": samples,
        }
    )
    return metrics


def trace_plan(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    rows = read_trace(path)
    velocities = pitch_velocity_by_tick(rows, args.dt_s)
    windows = mine_trace(path, args)
    runs = merge_pass_windows(windows, args.allowed_gap_ticks)
    evaluated = [evaluate_run(run, rows, velocities, args, path) for run in runs]
    pass_runs = [run for run in evaluated if run.get("stitch_tier") == "PASS_STITCH_RUN"]
    contact_counts = Counter(contact_code(row) for row in rows)
    return {
        "source_path": str(path),
        "source_name": path.parent.name,
        "command_cell": command_label(path),
        "seed": rows[0].get("seed") if rows else None,
        "samples": len(rows),
        "short_pass_windows": sum(1 for window in windows if window.get("tier") == "PASS_CURATED_CLOSED_LOOP_WINDOW"),
        "run_count": len(evaluated),
        "pass_run_count": len(pass_runs),
        "max_run_span_ticks": max((int(run.get("span_ticks") or 0) for run in evaluated), default=0),
        "max_pass_run_span_ticks": max((int(run.get("span_ticks") or 0) for run in pass_runs), default=0),
        "contact_counts": dict(sorted(contact_counts.items())),
        "runs": sorted(
            evaluated,
            key=lambda item: (
                int(item.get("span_ticks") or 0),
                float(item.get("mean_vx_m_s") or -1.0),
            ),
            reverse=True,
        )[: args.max_runs_per_trace],
    }


def aggregate(traces: list[dict[str, Any]]) -> dict[str, Any]:
    by_cell: dict[str, dict[str, Any]] = {}
    for trace in traces:
        item = by_cell.setdefault(
            trace["command_cell"],
            {
                "traces": 0,
                "short_pass_windows": 0,
                "runs": 0,
                "pass_runs": 0,
                "max_run_span_ticks": 0,
                "max_pass_run_span_ticks": 0,
            },
        )
        item["traces"] += 1
        item["short_pass_windows"] += int(trace["short_pass_windows"])
        item["runs"] += int(trace["run_count"])
        item["pass_runs"] += int(trace["pass_run_count"])
        item["max_run_span_ticks"] = max(item["max_run_span_ticks"], int(trace["max_run_span_ticks"]))
        item["max_pass_run_span_ticks"] = max(
            item["max_pass_run_span_ticks"], int(trace["max_pass_run_span_ticks"])
        )
    pass_25 = sum(1 for trace in traces if int(trace["max_pass_run_span_ticks"]) >= 25)
    pass_50 = sum(1 for trace in traces if int(trace["max_pass_run_span_ticks"]) >= 50)
    return {
        "traces": len(traces),
        "short_pass_windows": sum(int(trace["short_pass_windows"]) for trace in traces),
        "runs": sum(int(trace["run_count"]) for trace in traces),
        "pass_runs": sum(int(trace["pass_run_count"]) for trace in traces),
        "trace_count_with_pass_run_25_ticks": pass_25,
        "trace_count_with_pass_run_50_ticks": pass_50,
        "max_run_span_ticks": max((int(trace["max_run_span_ticks"]) for trace in traces), default=0),
        "max_pass_run_span_ticks": max((int(trace["max_pass_run_span_ticks"]) for trace in traces), default=0),
        "by_command_cell": by_cell,
    }


def compact_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "command_cell": run.get("command_cell"),
        "source_name": run.get("source_name"),
        "seed": run.get("seed"),
        "start_tick": run.get("start_tick"),
        "end_tick": run.get("end_tick"),
        "span_ticks": run.get("span_ticks"),
        "stitch_tier": run.get("stitch_tier"),
        "stitch_reasons": run.get("stitch_reasons"),
        "snippet_count": run.get("snippet_count"),
        "mean_vx_m_s": run.get("mean_vx_m_s"),
        "single_support_pct": run.get("single_support_pct"),
        "moving_in_envelope_pct": run.get("moving_in_envelope_pct"),
        "moving_single_in_envelope_pct": run.get("moving_single_in_envelope_pct"),
        "pitch_target_velocity_p95_rad_s": run.get("pitch_target_velocity_p95_rad_s"),
        "vy_abs_p95_m_s": run.get("vy_abs_p95_m_s"),
        "base_height_min_m": run.get("base_height_min_m"),
        "fastest_pitch_joint_p95": run.get("fastest_pitch_joint_p95"),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    aggregate_payload = payload["aggregate"]
    lines = [
        "# Closed-Loop Snippet Stitch Plan",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline analysis artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Criteria",
        "",
    ]
    for key, value in payload["criteria"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Aggregate",
            "",
            f"- traces: `{aggregate_payload['traces']}`",
            f"- short_pass_windows: `{aggregate_payload['short_pass_windows']}`",
            f"- runs: `{aggregate_payload['runs']}`",
            f"- pass_runs: `{aggregate_payload['pass_runs']}`",
            f"- trace_count_with_pass_run_25_ticks: `{aggregate_payload['trace_count_with_pass_run_25_ticks']}`",
            f"- trace_count_with_pass_run_50_ticks: `{aggregate_payload['trace_count_with_pass_run_50_ticks']}`",
            f"- max_run_span_ticks: `{aggregate_payload['max_run_span_ticks']}`",
            f"- max_pass_run_span_ticks: `{aggregate_payload['max_pass_run_span_ticks']}`",
            "",
            "## By Command Cell",
            "",
            "| command_cell | traces | short_pass | runs | pass_runs | max_run | max_pass_run |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label, item in aggregate_payload["by_command_cell"].items():
        lines.append(
            f"| {label} | {item['traces']} | {item['short_pass_windows']} | {item['runs']} | {item['pass_runs']} | {item['max_run_span_ticks']} | {item['max_pass_run_span_ticks']} |"
        )
    lines.extend(
        [
            "",
            "## Longest Passing Runs",
            "",
            "| command | source | ticks | span | snippets | vx | single_% | move_env_% | move_single_env_% | pitch_p95 | reasons |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    runs = payload.get("top_runs") or []
    if not runs:
        lines.append("| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |")
    for run in runs:
        lines.append(
            "| {command} | `{source}` | {ticks} | {span} | {snippets} | {vx} | {single} | {move_env} | {move_single} | {pitch} | `{reasons}` |".format(
                command=run.get("command_cell"),
                source=run.get("source_name"),
                ticks=f"{run.get('start_tick')}-{run.get('end_tick')}",
                span=run.get("span_ticks"),
                snippets=run.get("snippet_count"),
                vx=fmt(run.get("mean_vx_m_s")),
                single=fmt(run.get("single_support_pct")),
                move_env=fmt(run.get("moving_in_envelope_pct")),
                move_single=fmt(run.get("moving_single_in_envelope_pct")),
                pitch=fmt(run.get("pitch_target_velocity_p95_rad_s")),
                reasons=", ".join(run.get("stitch_reasons") or []),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A passing stitch run means the merged span still satisfies the same window criteria.",
            "- If pass runs do not reach 25 ticks, the short snippets should be treated as local hints, not a BC source.",
            "- If pass runs reach 25-50 ticks, the next step is to export a compact manifest and replay the stitched targets before BC.",
        ]
    )
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
    parser.add_argument("--output-md", default="outputs/analysis/CLOSED_LOOP_SNIPPET_STITCH_PLAN.md")
    parser.add_argument("--output-json", default="outputs/analysis/closed_loop_snippet_stitch_plan.json")
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--window-samples", type=int, default=10)
    parser.add_argument("--stride-samples", type=int, default=2)
    parser.add_argument("--allowed-gap-ticks", type=int, default=2)
    parser.add_argument("--max-runs-per-trace", type=int, default=10)
    parser.add_argument("--envelope-high", type=float, default=3.75)
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
        args.trace_glob = ["outputs/analysis/published_policy_upstream_main_backlash*seed*/trace.jsonl"]
    return args


def main() -> int:
    args = parse_args()
    paths = []
    for pattern in args.trace_glob:
        paths.extend(Path(path) for path in glob.glob(str(ROOT / pattern)))
    paths = sorted(set(paths))
    trace_plans = [trace_plan(path, args) for path in paths]
    aggregate_payload = aggregate(trace_plans)
    if aggregate_payload["trace_count_with_pass_run_50_ticks"] > 0:
        status = "PASS_STITCH_RUNS_REACH_50_TICKS"
    elif aggregate_payload["trace_count_with_pass_run_25_ticks"] > 0:
        status = "WARN_STITCH_RUNS_REACH_25_TICKS"
    elif aggregate_payload["pass_runs"] > 0:
        status = "HOLD_STITCH_RUNS_TOO_SHORT"
    else:
        status = "HOLD_NO_PASSING_STITCH_RUNS"
    all_runs = []
    for trace in trace_plans:
        all_runs.extend(compact_run(run) for run in trace["runs"])
    all_runs.sort(
        key=lambda run: (
            int(run.get("span_ticks") or 0),
            float(run.get("mean_vx_m_s") or -1.0),
        ),
        reverse=True,
    )
    payload = {
        "status": status,
        "trace_globs": args.trace_glob,
        "criteria": {
            "window_samples": args.window_samples,
            "stride_samples": args.stride_samples,
            "allowed_gap_ticks": args.allowed_gap_ticks,
            "dt_s": args.dt_s,
            "envelope_high": args.envelope_high,
            "min_mean_vx": args.min_mean_vx,
            "min_tick_vx": args.min_tick_vx,
            "min_single_support_pct": args.min_single_support_pct,
            "min_moving_in_envelope_pct": args.min_moving_in_envelope_pct,
            "min_moving_single_in_envelope_pct": args.min_moving_single_in_envelope_pct,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_body_pitch_abs_p95": args.max_body_pitch_abs_p95,
            "min_base_height": args.min_base_height,
        },
        "aggregate": aggregate_payload,
        "top_runs": all_runs[:50],
    }
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={status}")
    print(f"pass_runs={aggregate_payload['pass_runs']}")
    print(f"max_pass_run_span_ticks={aggregate_payload['max_pass_run_span_ticks']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
