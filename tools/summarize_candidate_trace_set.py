#!/usr/bin/env python3
"""Summarize a set of candidate trace analysis JSON files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


def number(value: Any) -> float | None:
    return value if isinstance(value, (int, float)) else None


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def mean_of(values: list[float | None]) -> float | None:
    vals = [v for v in values if isinstance(v, (int, float))]
    return mean(vals) if vals else None


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    payload["_path"] = str(path)
    return payload


def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    surfaces = Counter(item.get("failure_surface", "UNKNOWN") for item in items)
    rows = []
    for item in items:
        seed = None
        trace = item.get("trace_jsonl") or ""
        for part in Path(trace).parts:
            if part.startswith("v21_trace_seed") and part.endswith("_cpu"):
                seed = part.removeprefix("v21_trace_seed").removesuffix("_cpu")
        rows.append(
            {
                "action_saturation_pct": item.get("action_saturation_pct"),
                "base_height_min_m": (item.get("base_height_m") or {}).get("min"),
                "body_pitch_p95_rad": (item.get("body_pitch_rad") or {}).get("p95"),
                "command_x_m_s": item.get("command_x_m_s"),
                "dominant_cost": (item.get("dominant_cost_means") or [{}])[0],
                "failure_surface": item.get("failure_surface"),
                "first_low_height_tick": (item.get("events") or {}).get("first_low_height_tick"),
                "first_reverse_tick": (item.get("events") or {}).get("first_reverse_tick"),
                "mean_local_vx_m_s": (item.get("local_forward_velocity_m_s") or {}).get("mean"),
                "samples": item.get("samples"),
                "seed": seed,
                "track_ratio": item.get("track_ratio"),
                "trace_jsonl": item.get("trace_jsonl"),
            }
        )
    return {
        "aggregate": {
            "action_saturation_pct_mean": mean_of([row["action_saturation_pct"] for row in rows]),
            "base_height_min_mean_m": mean_of([row["base_height_min_m"] for row in rows]),
            "falls_or_terminations": len(rows),
            "mean_local_vx_m_s": mean_of([row["mean_local_vx_m_s"] for row in rows]),
            "samples_mean": mean_of([row["samples"] for row in rows]),
            "track_ratio_mean": mean_of([row["track_ratio"] for row in rows]),
        },
        "failure_surface_counts": dict(surfaces),
        "rows": rows,
        "status": "HOLD_TRACE_SET_LOW_COMMAND_FAILURES",
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Candidate Trace Set Summary",
        "",
        f"status: `{payload['status']}`",
        "",
        "## Aggregate",
        "",
    ]
    for key, value in payload["aggregate"].items():
        lines.append(f"- {key}: `{fmt(value)}`")
    lines.extend(["", "## Failure Surfaces", "", "| surface | count |", "|---|---:|"])
    for surface, count in sorted(payload["failure_surface_counts"].items()):
        lines.append(f"| `{surface}` | {count} |")
    lines.extend(
        [
            "",
            "## Per-Seed Rows",
            "",
            "| seed | surface | samples | mean_vx | track_ratio | base_height_min | first_reverse_tick | first_low_height_tick | dominant_cost |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in payload["rows"]:
        dominant = row.get("dominant_cost") or {}
        dominant_text = f"{dominant.get('term')}={fmt(dominant.get('mean'))}"
        lines.append(
            f"| {fmt(row.get('seed'))} | `{row.get('failure_surface')}` | "
            f"{fmt(row.get('samples'))} | {fmt(row.get('mean_local_vx_m_s'))} | "
            f"{fmt(row.get('track_ratio'))} | {fmt(row.get('base_height_min_m'))} | "
            f"{fmt(row.get('first_reverse_tick'))} | {fmt(row.get('first_low_height_tick'))} | "
            f"`{dominant_text}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The trace set should be read as an offline sim diagnosis only. It does not",
            "approve robot testing. Low target velocity and zero action saturation mean",
            "these failures are behavior discovery/stability failures, not actuator",
            "envelope failures.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis_json", nargs="+", type=Path)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    payload = summarize([load(path) for path in args.analysis_json])
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, args.output_md)
    print(args.output_md)
    print(args.output_json)
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
