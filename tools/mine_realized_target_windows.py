#!/usr/bin/env python3
"""Mine realized motion windows from existing Open Duck sim traces.

This is an offline planning tool. It does not train or run simulation. It reads
JSONL rollout traces and identifies short windows where the simulated robot
actually moved forward while staying within simple posture/height gates.

The output is a manifest of candidate windows, not a raw behavior-cloning
dataset. Keeping it as a manifest avoids committing bulky trace slices while
still making the next dataset-building decision auditable.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import glob
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACE_GLOBS = [
    "outputs/analysis/movement_bootstrap_v5_phase1_x008_failure_trace/*.jsonl",
    "outputs/analysis/movement_bootstrap_v7_x008_failure_trace/*.jsonl",
    "outputs/analysis/v10_local_cpu_seed0_20260624T032503Z/*.jsonl",
]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REALIZED_TARGET_WINDOW_MINE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "realized_target_window_mine.json"


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def percentile(values: list[float], pct: float) -> float | None:
    data = sorted(float(value) for value in values if finite(value))
    if not data:
        return None
    if len(data) == 1:
        return data[0]
    k = (len(data) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return data[lo]
    return data[lo] * (hi - k) + data[hi] * (k - lo)


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def pattern(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(int(value)) for value in values)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            record["_source_path"] = str(path)
            records.append(record)
    return records


def trace_groups(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        mode = str(record.get("mode", "unknown"))
        groups.setdefault(mode, []).append(record)
    return groups


def abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros((0, values.shape[1] if values.ndim == 2 else 0))
    return np.abs(np.diff(values, axis=0) / max(dt_s, 1.0e-9))


def window_metrics(window: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    vx = [record["local_linvel_m_s"][0] for record in window]
    vy = [record["local_linvel_m_s"][1] for record in window]
    pitch = [abs(record["body_pitch_rad"]) for record in window]
    height = [record["base_height_m"] for record in window]
    action = np.asarray([record.get("action", []) for record in window], dtype=float)
    sent = np.asarray([record.get("sent_target_rad", []) for record in window], dtype=float)
    actual = np.asarray([record.get("actual_position_rad", []) for record in window], dtype=float)
    contacts = Counter(pattern(record.get("foot_contacts", [])) for record in window)
    sent_velocity = abs_velocity(sent, dt_s) if sent.size else np.zeros((0, 0))
    tracking = np.abs(sent - actual) if sent.size and actual.size else np.zeros((0, 0))
    total = len(window)
    return {
        "samples": total,
        "start_tick": int(window[0].get("tick", 0)),
        "end_tick": int(window[-1].get("tick", 0)),
        "start_time_s": float(window[0].get("time_s", 0.0)),
        "end_time_s": float(window[-1].get("time_s", 0.0)),
        "mean_vx_m_s": float(np.mean(vx)) if vx else None,
        "max_vx_m_s": float(np.max(vx)) if vx else None,
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
        "contact_pct": {
            key: float(value / total * 100.0) for key, value in sorted(contacts.items())
        },
    }


def passes_window(metrics: dict[str, Any], args: argparse.Namespace) -> bool:
    return (
        metrics["mean_vx_m_s"] is not None
        and metrics["mean_vx_m_s"] >= args.min_mean_vx
        and metrics["body_pitch_abs_p95_rad"] is not None
        and metrics["body_pitch_abs_p95_rad"] <= args.max_pitch_abs_p95
        and metrics["base_height_min_m"] is not None
        and metrics["base_height_min_m"] >= args.min_base_height
        and (metrics["action_saturation_pct"] or 0.0) <= args.max_action_saturation_pct
    )


def done_margin(records: list[dict[str, Any]], end_index: int) -> int | None:
    for offset, record in enumerate(records[end_index + 1 :], start=1):
        if record.get("done"):
            return offset
    return None


def analyze_trace(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    records = read_jsonl(path)
    groups = trace_groups(records)
    mode_summaries = []
    windows = []
    for mode, mode_records in groups.items():
        done_indices = [index for index, record in enumerate(mode_records) if record.get("done")]
        vx = [record["local_linvel_m_s"][0] for record in mode_records if "local_linvel_m_s" in record]
        mode_windows = []
        for start in range(0, max(0, len(mode_records) - args.window_samples + 1), args.stride_samples):
            end = start + args.window_samples - 1
            window = mode_records[start : start + args.window_samples]
            if any(record.get("done") for record in window):
                continue
            margin = done_margin(mode_records, end)
            if margin is not None and margin < args.min_done_margin:
                continue
            metrics = window_metrics(window, args.dt_s)
            if not passes_window(metrics, args):
                continue
            metrics.update(
                {
                    "source_path": str(path),
                    "mode": mode,
                    "window_start_index": start,
                    "window_end_index": end,
                    "ticks_until_done_after_window": margin,
                }
            )
            mode_windows.append(metrics)
        mode_summaries.append(
            {
                "mode": mode,
                "samples": len(mode_records),
                "done_count": len(done_indices),
                "mean_vx_m_s": float(np.mean(vx)) if vx else None,
                "max_vx_m_s": float(np.max(vx)) if vx else None,
                "min_base_height_m": (
                    float(np.min([record["base_height_m"] for record in mode_records]))
                    if mode_records and "base_height_m" in mode_records[0]
                    else None
                ),
                "candidate_window_count": len(mode_windows),
            }
        )
        windows.extend(mode_windows)
    windows.sort(
        key=lambda item: (
            item["mean_vx_m_s"],
            item["base_height_min_m"],
            -1.0 * (item["body_pitch_abs_p95_rad"] or 999.0),
        ),
        reverse=True,
    )
    return {
        "source_path": str(path),
        "mode_summaries": mode_summaries,
        "candidate_windows": windows[: args.max_windows_per_trace],
        "candidate_window_count": len(windows),
    }


def expand_globs(patterns: list[str]) -> list[Path]:
    paths = []
    for pattern_text in patterns:
        pattern_path = Path(pattern_text)
        pattern = str(pattern_path if pattern_path.is_absolute() else ROOT / pattern_path)
        paths.extend(Path(path) for path in glob.glob(pattern))
    return sorted(set(paths))


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Realized Target Window Mine",
        "",
        f"status: `{payload['status']}`",
        "",
        "This mines existing simulated rollout traces for short windows that already",
        "show realized forward motion under actual sim/contact dynamics. It produces",
        "a manifest, not a raw BC dataset.",
        "",
        "## Criteria",
        "",
    ]
    for key, value in payload["criteria"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Trace Summary",
            "",
            "| source | mode | samples | done_count | mean_vx | max_vx | min_height | candidates |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for trace in payload["traces"]:
        source = Path(trace["source_path"]).name
        for mode in trace["mode_summaries"]:
            lines.append(
                "| {source} | `{mode}` | {samples} | {done_count} | {mean_vx} | {max_vx} | {min_height} | {candidates} |".format(
                    source=source,
                    mode=mode["mode"],
                    samples=mode["samples"],
                    done_count=mode["done_count"],
                    mean_vx=fmt(mode["mean_vx_m_s"]),
                    max_vx=fmt(mode["max_vx_m_s"]),
                    min_height=fmt(mode["min_base_height_m"]),
                    candidates=mode["candidate_window_count"],
                )
            )
    lines.extend(
        [
            "",
            "## Top Candidate Windows",
            "",
            "| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    top_windows = payload["top_windows"]
    if not top_windows:
        lines.append("| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |")
    for item in top_windows:
        lines.append(
            "| {source} | `{mode}` | {ticks} | {mean_vx} | {vy} | {pitch} | {height} | {sat} | {vel} | {track} | {margin} | `{contacts}` |".format(
                source=Path(item["source_path"]).name,
                mode=item["mode"],
                ticks=f"{item['start_tick']}-{item['end_tick']}",
                mean_vx=fmt(item["mean_vx_m_s"]),
                vy=fmt(item["vy_abs_p95_m_s"]),
                pitch=fmt(item["body_pitch_abs_p95_rad"]),
                height=fmt(item["base_height_min_m"]),
                sat=fmt(item["action_saturation_pct"]),
                vel=fmt(item["sent_target_velocity_p95_rad_s"]),
                track=fmt(item["joint_tracking_p95_rad"]),
                margin=item["ticks_until_done_after_window"],
                contacts=item["contact_pct"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.",
            "- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.",
            "- If no windows pass, the next step is to generate realized stable targets deliberately in sim.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-glob", action="append", default=None)
    parser.add_argument("--window-samples", type=int, default=25)
    parser.add_argument("--stride-samples", type=int, default=5)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.45)
    parser.add_argument("--min-base-height", type=float, default=0.10)
    parser.add_argument("--max-action-saturation-pct", type=float, default=5.0)
    parser.add_argument("--min-done-margin", type=int, default=10)
    parser.add_argument("--max-windows-per-trace", type=int, default=20)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    paths = expand_globs(args.trace_glob or DEFAULT_TRACE_GLOBS)
    if not paths:
        raise SystemExit("No trace files matched")
    traces = [analyze_trace(path, args) for path in paths]
    all_windows = [
        window for trace in traces for window in trace["candidate_windows"]
    ]
    all_windows.sort(
        key=lambda item: (
            item["mean_vx_m_s"],
            item["base_height_min_m"],
            -1.0 * (item["body_pitch_abs_p95_rad"] or 999.0),
        ),
        reverse=True,
    )
    status = "PASS_REALIZED_WINDOWS_AVAILABLE" if all_windows else "HOLD_NO_REALIZED_WINDOWS"
    payload = {
        "status": status,
        "criteria": {
            "window_samples": args.window_samples,
            "stride_samples": args.stride_samples,
            "min_mean_vx": args.min_mean_vx,
            "max_pitch_abs_p95": args.max_pitch_abs_p95,
            "min_base_height": args.min_base_height,
            "max_action_saturation_pct": args.max_action_saturation_pct,
            "min_done_margin": args.min_done_margin,
        },
        "trace_globs": args.trace_glob or DEFAULT_TRACE_GLOBS,
        "traces": traces,
        "top_windows": all_windows[:25],
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
