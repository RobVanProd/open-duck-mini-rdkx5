#!/usr/bin/env python3
"""Build a compact target-dataset manifest from curated motion windows.

This tool does not copy raw traces, export arrays, train a policy, or touch the
robot. It records exactly which curated windows would seed a future dataset so
the handoff can be reviewed before any supervised training.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "outputs" / "analysis" / "target_generator_shuffled_broad_window_curation.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_DATASET_MANIFEST.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_dataset_manifest.json"


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and np.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def stats(values: list[Any]) -> dict[str, float | None]:
    data = [float(value) for value in values if finite(value)]
    if not data:
        return {"min": None, "mean": None, "p50": None, "p95": None, "max": None}
    return {
        "min": float(np.min(data)),
        "mean": float(np.mean(data)),
        "p50": float(np.percentile(data, 50)),
        "p95": float(np.percentile(data, 95)),
        "max": float(np.max(data)),
    }


def entry_id(window: dict[str, Any]) -> str:
    payload = {
        "source_path": window.get("source_path"),
        "mode": window.get("mode"),
        "start_tick": window.get("start_tick"),
        "end_tick": window.get("end_tick"),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return digest[:16]


def compact_entry(window: dict[str, Any]) -> dict[str, Any]:
    source_path = Path(str(window.get("source_path")))
    return {
        "entry_id": entry_id(window),
        "source_path": str(source_path),
        "source_name": source_path.name,
        "mode": window.get("mode"),
        "start_tick": window.get("start_tick"),
        "end_tick": window.get("end_tick"),
        "mean_vx_m_s": window.get("mean_vx_m_s"),
        "vy_abs_p95_m_s": window.get("vy_abs_p95_m_s"),
        "body_pitch_abs_p95_rad": window.get("body_pitch_abs_p95_rad"),
        "base_height_min_m": window.get("base_height_min_m"),
        "sent_target_velocity_p95_rad_s": window.get("sent_target_velocity_p95_rad_s"),
        "joint_tracking_p95_rad": window.get("joint_tracking_p95_rad"),
        "contact_dominance_pct": window.get("contact_dominance_pct"),
        "ticks_until_done_after_window": window.get("ticks_until_done_after_window"),
        "contact_pct": window.get("contact_pct"),
        "raw_trace_exists": source_path.exists(),
    }


def manifest_status(entries: list[dict[str, Any]], args: argparse.Namespace) -> str:
    source_files = {entry["source_name"] for entry in entries}
    source_mode_pairs = {(entry["source_name"], entry["mode"]) for entry in entries}
    if len(entries) < args.min_windows:
        return "HOLD_INSUFFICIENT_MANIFEST_WINDOWS"
    if len(source_files) < args.min_source_files:
        return "HOLD_INSUFFICIENT_MANIFEST_SOURCE_DIVERSITY"
    if len(source_mode_pairs) < args.min_source_mode_pairs:
        return "HOLD_INSUFFICIENT_MANIFEST_MODE_DIVERSITY"
    if not all(entry["raw_trace_exists"] for entry in entries):
        return "HOLD_MANIFEST_SOURCE_TRACE_MISSING"
    return "PASS_TARGET_DATASET_MANIFEST_READY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    metric_stats = payload["metric_stats"]
    lines = [
        "# Target Dataset Manifest",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is a compact manifest of curated low-command target windows.",
        "It does not include raw trace contents and does not start training.",
        "",
        "## Summary",
        "",
        f"- input_curation_json: `{payload['input_curation_json']}`",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- entries: `{summary['entries']}`",
        f"- source_files: `{summary['source_files']}`",
        f"- source_mode_pairs: `{summary['source_mode_pairs']}`",
        f"- raw_traces_present: `{summary['raw_traces_present']}`",
        "",
        "## Source Distribution",
        "",
        "| source | windows |",
        "|---|---:|",
    ]
    for source, count in summary["by_source"].items():
        lines.append(f"| {source} | {count} |")
    lines.extend(
        [
            "",
            "## Metric Summary",
            "",
            "| metric | min | mean | p50 | p95 | max |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for metric, values in metric_stats.items():
        lines.append(
            "| {metric} | {min} | {mean} | {p50} | {p95} | {max} |".format(
                metric=metric,
                min=fmt(values["min"]),
                mean=fmt(values["mean"]),
                p50=fmt(values["p50"]),
                p95=fmt(values["p95"]),
                max=fmt(values["max"]),
            )
        )
    lines.extend(
        [
            "",
            "## Windows",
            "",
            "| id | source | ticks | vx | vy95 | pitch95 | height | sent_vel95 | track95 | contact_max |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for entry in payload["entries"]:
        lines.append(
            "| {entry_id} | {source} | {ticks} | {vx} | {vy} | {pitch} | {height} | {sent_vel} | {track} | {contact} |".format(
                entry_id=entry["entry_id"],
                source=entry["source_name"],
                ticks=f"{entry['start_tick']}-{entry['end_tick']}",
                vx=fmt(entry["mean_vx_m_s"]),
                vy=fmt(entry["vy_abs_p95_m_s"]),
                pitch=fmt(entry["body_pitch_abs_p95_rad"]),
                height=fmt(entry["base_height_min_m"]),
                sent_vel=fmt(entry["sent_target_velocity_p95_rad_s"]),
                track=fmt(entry["joint_tracking_p95_rad"]),
                contact=fmt(entry["contact_dominance_pct"]),
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- This manifest is only seed material for a future supervised/imitation experiment.",
            "- Do not train until the manifest and source skew are reviewed.",
            "- Do not commit raw JSONL traces unless explicitly approved.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curation-json", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--min-windows", type=int, default=8)
    parser.add_argument("--min-source-files", type=int, default=2)
    parser.add_argument("--min-source-mode-pairs", type=int, default=2)
    args = parser.parse_args()

    source = json.loads(Path(args.curation_json).read_text())
    entries = [compact_entry(window) for window in source.get("curated_seed_windows", [])]
    entries.sort(key=lambda item: (item["source_name"], item["start_tick"], item["entry_id"]))
    status = manifest_status(entries, args)
    by_source = dict(sorted(Counter(entry["source_name"] for entry in entries).items()))
    source_mode_pairs = {(entry["source_name"], entry["mode"]) for entry in entries}
    digest = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]
    metric_stats = {
        "mean_vx_m_s": stats([entry["mean_vx_m_s"] for entry in entries]),
        "vy_abs_p95_m_s": stats([entry["vy_abs_p95_m_s"] for entry in entries]),
        "body_pitch_abs_p95_rad": stats([entry["body_pitch_abs_p95_rad"] for entry in entries]),
        "base_height_min_m": stats([entry["base_height_min_m"] for entry in entries]),
        "sent_target_velocity_p95_rad_s": stats(
            [entry["sent_target_velocity_p95_rad_s"] for entry in entries]
        ),
        "joint_tracking_p95_rad": stats([entry["joint_tracking_p95_rad"] for entry in entries]),
        "contact_dominance_pct": stats([entry["contact_dominance_pct"] for entry in entries]),
    }
    payload = {
        "status": status,
        "input_curation_json": str(Path(args.curation_json)),
        "dataset_id": digest,
        "criteria": {
            "min_windows": args.min_windows,
            "min_source_files": args.min_source_files,
            "min_source_mode_pairs": args.min_source_mode_pairs,
        },
        "summary": {
            "entries": len(entries),
            "source_files": len(by_source),
            "source_mode_pairs": len(source_mode_pairs),
            "by_source": by_source,
            "raw_traces_present": all(entry["raw_trace_exists"] for entry in entries),
        },
        "metric_stats": metric_stats,
        "entries": entries,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"dataset_id={digest}")
    print(f"entries={len(entries)}")
    print(f"source_files={len(by_source)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
