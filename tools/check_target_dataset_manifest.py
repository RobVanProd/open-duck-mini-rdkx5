#!/usr/bin/env python3
"""Sanity-check a compact target dataset manifest without training.

The checker reads the manifest and the local ignored source traces, recomputes
window metrics, and confirms that the manifest entries still match the source
data. It does not export raw traces, train a policy, deploy, SSH, or touch the
robot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "outputs" / "analysis" / "target_dataset_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_DATASET_SANITY_CHECK.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_dataset_sanity_check.json"


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


def entry_id(entry: dict[str, Any]) -> str:
    payload = {
        "source_path": entry.get("source_path"),
        "mode": entry.get("mode"),
        "start_tick": entry.get("start_tick"),
        "end_tick": entry.get("end_tick"),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return digest[:16]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros((0, values.shape[1] if values.ndim == 2 else 0))
    return np.abs(np.diff(values, axis=0) / max(dt_s, 1.0e-9))


def pattern(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(int(value)) for value in values)


def contact_dominance(contact_pct: dict[str, Any]) -> float:
    if not contact_pct:
        return 0.0
    return max(float(value) for value in contact_pct.values())


def window_metrics(window: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    vx = [record["local_linvel_m_s"][0] for record in window]
    vy = [record["local_linvel_m_s"][1] for record in window]
    pitch = [abs(record["body_pitch_rad"]) for record in window]
    height = [record["base_height_m"] for record in window]
    action = np.asarray([record.get("action", []) for record in window], dtype=float)
    sent = np.asarray([record.get("sent_target_rad", []) for record in window], dtype=float)
    actual = np.asarray([record.get("actual_position_rad", []) for record in window], dtype=float)
    contacts = Counter(pattern(record.get("foot_contacts", [])) for record in window)
    total = len(window)
    sent_velocity = abs_velocity(sent, dt_s) if sent.size else np.zeros((0, 0))
    return {
        "samples": total,
        "mean_vx_m_s": float(np.mean(vx)) if vx else None,
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
        "joint_tracking_p95_rad": None,
        "contact_pct": {
            key: float(value / total * 100.0) for key, value in sorted(contacts.items())
        },
    }


def fixed_window_metrics(window: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    metrics = window_metrics(window, dt_s)
    sent = np.asarray([record.get("sent_target_rad", []) for record in window], dtype=float)
    actual = np.asarray([record.get("actual_position_rad", []) for record in window], dtype=float)
    tracking = np.abs(sent - actual) if sent.size and actual.size else np.zeros((0, 0))
    metrics["joint_tracking_p95_rad"] = (
        percentile(tracking.reshape(-1).tolist(), 95) if tracking.size else None
    )
    metrics["contact_dominance_pct"] = contact_dominance(metrics["contact_pct"])
    return metrics


def close_enough(a: Any, b: Any, tol: float) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


def check_entry(entry: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    errors = []
    warnings = []
    source_path = Path(str(entry.get("source_path")))
    if entry_id(entry) != entry.get("entry_id"):
        errors.append("entry_id_mismatch")
    if not source_path.exists():
        errors.append("source_trace_missing")
        return {"entry_id": entry.get("entry_id"), "errors": errors, "warnings": warnings}

    records = [
        record
        for record in read_jsonl(source_path)
        if str(record.get("mode")) == str(entry.get("mode"))
    ]
    start_tick = int(entry.get("start_tick"))
    end_tick = int(entry.get("end_tick"))
    window = [
        record
        for record in records
        if start_tick <= int(record.get("tick", -1)) <= end_tick
    ]
    expected_samples = end_tick - start_tick + 1
    if len(window) != expected_samples:
        errors.append(f"window_sample_count_{len(window)}_expected_{expected_samples}")
    if any(record.get("done") for record in window):
        errors.append("done_inside_window")
    for record in window:
        if len(record.get("action", [])) != 14:
            errors.append("action_dim_not_14")
            break
        if len(record.get("sent_target_rad", [])) != 14:
            errors.append("sent_target_dim_not_14")
            break
        if len(record.get("actual_position_rad", [])) != 14:
            errors.append("actual_position_dim_not_14")
            break
        command = record.get("command", [])
        if len(command) < 1 or not close_enough(command[0], args.command_x, args.metric_tolerance):
            errors.append("command_x_mismatch")
            break

    metrics = fixed_window_metrics(window, args.dt_s) if window else {}
    metric_keys = [
        "mean_vx_m_s",
        "vy_abs_p95_m_s",
        "body_pitch_abs_p95_rad",
        "base_height_min_m",
        "sent_target_velocity_p95_rad_s",
        "joint_tracking_p95_rad",
        "contact_dominance_pct",
    ]
    for key in metric_keys:
        if not close_enough(metrics.get(key), entry.get(key), args.metric_tolerance):
            errors.append(f"{key}_mismatch")

    if (metrics.get("mean_vx_m_s") or -999.0) < args.min_mean_vx:
        errors.append("low_forward_velocity")
    if (metrics.get("vy_abs_p95_m_s") or 999.0) > args.max_vy_abs_p95:
        errors.append("high_lateral_velocity")
    if (metrics.get("body_pitch_abs_p95_rad") or 999.0) > args.max_pitch_abs_p95:
        errors.append("high_body_pitch")
    if (metrics.get("base_height_min_m") or -999.0) < args.min_base_height:
        errors.append("low_base_height")
    if (metrics.get("sent_target_velocity_p95_rad_s") or 999.0) > args.max_sent_velocity_p95:
        errors.append("high_sent_target_velocity")
    if (metrics.get("joint_tracking_p95_rad") or 999.0) > args.max_tracking_p95:
        errors.append("high_tracking_error")
    if (metrics.get("contact_dominance_pct") or 999.0) > args.max_contact_dominance_pct:
        errors.append("single_contact_pattern_dominates")

    return {
        "entry_id": entry.get("entry_id"),
        "source_name": entry.get("source_name"),
        "mode": entry.get("mode"),
        "ticks": f"{start_tick}-{end_tick}",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "metrics": metrics,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Target Dataset Sanity Check",
        "",
        f"status: `{payload['status']}`",
        "",
        "This check recomputes compact window metrics from local source traces.",
        "It does not copy raw traces and does not start training.",
        "",
        "## Summary",
        "",
        f"- manifest: `{payload['manifest_path']}`",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- entries_checked: `{payload['summary']['entries_checked']}`",
        f"- entries_with_errors: `{payload['summary']['entries_with_errors']}`",
        f"- source_files: `{payload['summary']['source_files']}`",
        f"- max_source_fraction: `{fmt(payload['summary']['max_source_fraction'])}`",
        "",
        "## Warnings",
        "",
    ]
    if payload["warnings"]:
        for warning in payload["warnings"]:
            lines.append(f"- `{warning}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Entry Results",
            "",
            "| id | source | ticks | errors | vx | vy95 | pitch95 | height | sent_vel95 | track95 |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for result in payload["entry_results"]:
        metrics = result.get("metrics", {})
        errors = ", ".join(result["errors"]) if result["errors"] else "none"
        lines.append(
            "| {entry_id} | {source} | {ticks} | `{errors}` | {vx} | {vy} | {pitch} | {height} | {sent_vel} | {track} |".format(
                entry_id=result["entry_id"],
                source=result.get("source_name"),
                ticks=result.get("ticks"),
                errors=errors,
                vx=fmt(metrics.get("mean_vx_m_s")),
                vy=fmt(metrics.get("vy_abs_p95_m_s")),
                pitch=fmt(metrics.get("body_pitch_abs_p95_rad")),
                height=fmt(metrics.get("base_height_min_m")),
                sent_vel=fmt(metrics.get("sent_target_velocity_p95_rad_s")),
                track=fmt(metrics.get("joint_tracking_p95_rad")),
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- A pass or warning-pass here only proves the compact manifest matches local trace evidence.",
            "- It does not prove the dataset is sufficient for robust policy training.",
            "- Review source skew before any supervised/imitation smoke run.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-json", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--metric-tolerance", type=float, default=1.0e-6)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.35)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=2.5)
    parser.add_argument("--max-tracking-p95", type=float, default=0.12)
    parser.add_argument("--max-contact-dominance-pct", type=float, default=95.0)
    parser.add_argument("--warn-max-source-fraction", type=float, default=0.8)
    args = parser.parse_args()

    manifest_path = Path(args.manifest_json)
    manifest = json.loads(manifest_path.read_text())
    entries = manifest.get("entries", [])
    entry_results = [check_entry(entry, args) for entry in entries]
    entries_with_errors = sum(1 for result in entry_results if result["errors"])
    by_source = Counter(entry.get("source_name") for entry in entries)
    max_source_fraction = (
        max(by_source.values()) / len(entries) if entries else 0.0
    )
    warnings = []
    if max_source_fraction > args.warn_max_source_fraction:
        warnings.append("source_distribution_skew")
    if len(by_source) < 2:
        warnings.append("single_source_file")

    if entries_with_errors:
        status = "HOLD_TARGET_DATASET_SANITY_ERRORS"
    elif warnings:
        status = "WARN_TARGET_DATASET_SANITY_SOURCE_SKEW"
    else:
        status = "PASS_TARGET_DATASET_SANITY_CHECK"

    payload = {
        "status": status,
        "manifest_path": str(manifest_path),
        "dataset_id": manifest.get("dataset_id"),
        "summary": {
            "entries_checked": len(entry_results),
            "entries_with_errors": entries_with_errors,
            "source_files": len(by_source),
            "by_source": dict(sorted(by_source.items())),
            "max_source_fraction": max_source_fraction,
        },
        "criteria": {
            "command_x": args.command_x,
            "dt_s": args.dt_s,
            "metric_tolerance": args.metric_tolerance,
            "min_mean_vx": args.min_mean_vx,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_pitch_abs_p95": args.max_pitch_abs_p95,
            "min_base_height": args.min_base_height,
            "max_sent_velocity_p95": args.max_sent_velocity_p95,
            "max_tracking_p95": args.max_tracking_p95,
            "max_contact_dominance_pct": args.max_contact_dominance_pct,
            "warn_max_source_fraction": args.warn_max_source_fraction,
        },
        "warnings": warnings,
        "entry_results": entry_results,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"entries_checked={len(entry_results)}")
    print(f"entries_with_errors={entries_with_errors}")
    print(f"warnings={','.join(warnings) if warnings else 'none'}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 1 if entries_with_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
