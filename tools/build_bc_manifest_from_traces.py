#!/usr/bin/env python3
"""Build a compact BC manifest from full-observation replay traces.

This is for offline distillation only. It records which ignored JSONL traces are
usable as obs[101] -> action[14] examples, without copying raw trace contents,
training a policy, deploying, SSHing, or touching the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "BC_TRACE_MANIFEST.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "bc_trace_manifest.json"


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


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
    return float(data[lo] * (hi - k) + data[hi] * (k - lo))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def abs_velocity(values: np.ndarray, dt_s: float) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros((0, values.shape[1] if values.ndim == 2 else 0))
    return np.abs(np.diff(values, axis=0) / max(dt_s, 1.0e-9))


def pattern(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(int(value)) for value in values)


def entry_id(source_path: Path, mode: str, start_tick: int, end_tick: int) -> str:
    payload = {
        "source_path": str(source_path),
        "mode": mode,
        "start_tick": start_tick,
        "end_tick": end_tick,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def trace_metrics(records: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    vx = [row["local_linvel_m_s"][0] for row in records if row.get("local_linvel_m_s")]
    vy = [abs(row["local_linvel_m_s"][1]) for row in records if row.get("local_linvel_m_s")]
    pitch = [abs(row["body_pitch_rad"]) for row in records if finite(row.get("body_pitch_rad"))]
    height = [row["base_height_m"] for row in records if finite(row.get("base_height_m"))]
    sent = np.asarray([row.get("sent_target_rad", []) for row in records], dtype=float)
    actual = np.asarray([row.get("actual_position_rad", []) for row in records], dtype=float)
    sent_velocity = abs_velocity(sent, dt_s) if sent.size else np.zeros((0, 0))
    tracking = np.abs(sent - actual) if sent.size and actual.size else np.zeros((0, 0))
    contacts = Counter(pattern(row.get("foot_contacts", [])) for row in records)
    total = max(len(records), 1)
    return {
        "samples": len(records),
        "mean_vx_m_s": float(np.mean(vx)) if vx else None,
        "vy_abs_p95_m_s": percentile(vy, 95),
        "body_pitch_abs_p95_rad": percentile(pitch, 95),
        "base_height_min_m": float(np.min(height)) if height else None,
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


def compact_entry(path: Path, records: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    mode = str(records[0].get("mode") or args.default_mode)
    ticks = [int(row.get("tick", -1)) for row in records]
    start_tick = min(ticks)
    end_tick = max(ticks)
    parent_depth = max(1, int(args.source_parent_depth))
    parent_parts = list(path.parent.parts[-parent_depth:])
    source_name = str(Path(*parent_parts, path.name)) if parent_parts else path.name
    metrics = trace_metrics(records, args.dt_s)
    obs_ok = all(len(row.get("obs_state") or []) == 101 for row in records)
    action_ok = all(len(row.get("action") or []) == 14 for row in records)
    done_inside = any(bool(row.get("done")) for row in records[:-1])
    entry = {
        "entry_id": entry_id(path, mode, start_tick, end_tick),
        "source_path": str(path),
        "source_name": source_name,
        "mode": mode,
        "start_tick": start_tick,
        "end_tick": end_tick,
        "raw_trace_exists": path.exists(),
        "bc_ready": bool(obs_ok and action_ok and not done_inside),
        "obs_state_dim_ok": bool(obs_ok),
        "action_dim_ok": bool(action_ok),
        "done_inside_window": bool(done_inside),
        **metrics,
    }
    return entry


def manifest_status(entries: list[dict[str, Any]], min_entries: int) -> str:
    if len(entries) < min_entries:
        return "HOLD_INSUFFICIENT_TRACE_ENTRIES"
    if not all(entry.get("bc_ready") for entry in entries):
        return "HOLD_TRACE_NOT_BC_READY"
    return "PASS_BC_TRACE_MANIFEST_READY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# BC Trace Manifest",
        "",
        f"status: `{payload['status']}`",
        "",
        "This manifest points to ignored full-observation selector replay traces.",
        "It is for offline distillation only and does not include raw trace contents.",
        "",
        "## Summary",
        "",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- entries: `{payload['summary']['entries']}`",
        f"- samples: `{payload['summary']['samples']}`",
        f"- bc_ready_entries: `{payload['summary']['bc_ready_entries']}`",
        "",
        "## Entries",
        "",
        "| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for entry in payload["entries"]:
        command_x = payload["command_x"]
        vx = entry.get("mean_vx_m_s")
        ratio = None if not command_x else (vx / command_x if vx is not None else None)
        lines.append(
            "| {source} | {ticks} | {samples} | `{ready}` | {vx} | {ratio} | {sent} | {track} | {pitch} | {height} |".format(
                source=entry["source_name"],
                ticks=f"{entry['start_tick']}-{entry['end_tick']}",
                samples=entry["samples"],
                ready=entry["bc_ready"],
                vx=fmt(vx),
                ratio=fmt(ratio),
                sent=fmt(entry.get("sent_target_velocity_p95_rad_s")),
                track=fmt(entry.get("joint_tracking_p95_rad")),
                pitch=fmt(entry.get("body_pitch_abs_p95_rad")),
                height=fmt(entry.get("base_height_min_m")),
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- Do not commit raw JSONL traces unless explicitly approved.",
            "- Do not treat this manifest as a deployable policy.",
            "- Use it only as offline seed material for a portable student.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", required=True)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--default-mode", default="selector_trace")
    parser.add_argument(
        "--source-parent-depth",
        type=int,
        default=1,
        help="Number of source parent directories to include in manifest source_name.",
    )
    parser.add_argument("--min-entries", type=int, default=1)
    args = parser.parse_args()

    paths: list[Path] = []
    for item in args.trace_glob:
        paths.extend(Path(path) for path in sorted(glob.glob(item, recursive=True)))
    paths = sorted(dict.fromkeys(paths))
    entries = []
    for path in paths:
        records = read_jsonl(path)
        if records:
            entries.append(compact_entry(path, records, args))
    digest = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]
    payload = {
        "status": manifest_status(entries, args.min_entries),
        "dataset_id": digest,
        "command_x": float(args.command_x),
        "trace_globs": args.trace_glob,
        "summary": {
            "entries": len(entries),
            "samples": int(sum(entry.get("samples", 0) for entry in entries)),
            "bc_ready_entries": int(sum(1 for entry in entries if entry.get("bc_ready"))),
        },
        "entries": entries,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"dataset_id={payload['dataset_id']}")
    print(f"entries={payload['summary']['entries']}")
    print(f"samples={payload['summary']['samples']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
