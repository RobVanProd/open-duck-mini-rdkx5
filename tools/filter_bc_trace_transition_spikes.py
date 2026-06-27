#!/usr/bin/env python3
"""Filter transition-adjacent target-rate spikes from BC JSONL traces.

This is an offline dataset-curation helper. It reads ignored full-observation
JSONL traces, drops rows around selected-joint target-rate spikes near foot
contact transitions, and writes filtered traces plus a review report. It does
not train, SSH, deploy, run robot tests, or change runtime behavior.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "BC_TRACE_TRANSITION_SPIKE_FILTER.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "bc_trace_transition_spike_filter.json"

JOINT_NAMES = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def finite(value: Any) -> bool:
    return isinstance(value, int | float) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, str):
        return value
    if finite(value):
        return f"{float(value):.{digits}f}"
    return "NA"


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


def parse_joints(value: str) -> list[int]:
    by_name = {name: idx for idx, name in enumerate(JOINT_NAMES)}
    out: list[int] = []
    for raw in value.split(","):
        item = raw.strip()
        if not item:
            continue
        out.append(by_name[item] if item in by_name else int(item))
    for idx in out:
        if idx < 0 or idx >= len(JOINT_NAMES):
            raise ValueError(f"joint index out of range: {idx}")
    return sorted(dict.fromkeys(out))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def vector(row: dict[str, Any], key: str) -> list[float] | None:
    value = row.get(key)
    if isinstance(value, list) and len(value) >= len(JOINT_NAMES):
        return [float(item) for item in value[: len(JOINT_NAMES)]]
    return None


def contact_code(row: dict[str, Any]) -> str:
    value = row.get("foot_contacts")
    if not isinstance(value, list) or len(value) < 2:
        return "NA"
    return "".join(str(1 if int(item) else 0) for item in value[:2])


def transition_indices(codes: list[str]) -> list[int]:
    return [idx for idx in range(1, len(codes)) if codes[idx] != codes[idx - 1]]


def target_velocity(
    previous: list[float],
    current: list[float],
    *,
    joint_indices: list[int],
    key_scale: float,
    dt_s: float,
) -> dict[int, float]:
    return {
        idx: abs(float(current[idx]) - float(previous[idx])) * key_scale / max(dt_s, 1.0e-9)
        for idx in joint_indices
    }


def nearest_distance(index: int, transitions: list[int]) -> int | None:
    if not transitions:
        return None
    return min(abs(index - item) for item in transitions)


def process_trace(path: Path, output_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    rows = read_jsonl(path)
    codes = [contact_code(row) for row in rows]
    transitions = transition_indices(codes)
    joint_indices = parse_joints(args.joints)
    key_scale = args.action_scale if args.vector_key == "action" else 1.0

    spike_indices: set[int] = set()
    removal_indices: set[int] = set()
    spike_contacts = Counter()
    spike_distance = Counter()
    removed_contacts = Counter()
    velocities_by_joint: dict[str, list[float]] = {
        JOINT_NAMES[idx]: [] for idx in joint_indices
    }

    previous = vector(rows[0], args.vector_key) if rows else None
    for idx, row in enumerate(rows[1:], start=1):
        current = vector(row, args.vector_key)
        if previous is None or current is None:
            previous = current
            continue
        velocities = target_velocity(
            previous,
            current,
            joint_indices=joint_indices,
            key_scale=key_scale,
            dt_s=args.dt_s,
        )
        previous = current
        for joint_idx, velocity in velocities.items():
            velocities_by_joint[JOINT_NAMES[joint_idx]].append(velocity)
        max_velocity = max(velocities.values()) if velocities else 0.0
        distance = nearest_distance(idx, transitions)
        transition_ok = distance is not None and distance <= args.transition_window_ticks
        if max_velocity <= args.spike_velocity_rad_s or not transition_ok:
            continue
        spike_indices.add(idx)
        spike_contacts[codes[idx]] += 1
        spike_distance[min(int(distance), args.transition_window_ticks)] += 1
        for remove_idx in range(idx - args.drop_window_ticks, idx + args.drop_window_ticks + 1):
            if 0 <= remove_idx < len(rows):
                removal_indices.add(remove_idx)

    kept_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if idx in removal_indices:
            removed_contacts[codes[idx]] += 1
            continue
        new_row = dict(row)
        new_row["mode"] = args.output_mode
        new_row["transition_spike_filter_source_mode"] = row.get("mode")
        kept_rows.append(new_row)

    output_path = output_dir / path.name
    write_jsonl(output_path, kept_rows)

    return {
        "source_trace": str(path),
        "output_trace": str(output_path),
        "samples_in": len(rows),
        "samples_out": len(kept_rows),
        "samples_removed": len(rows) - len(kept_rows),
        "contact_transitions": len(transitions),
        "spike_ticks": len(spike_indices),
        "spike_contact_counts": dict(sorted(spike_contacts.items())),
        "spike_distance_to_transition_counts": dict(sorted(spike_distance.items())),
        "removed_contact_counts": dict(sorted(removed_contacts.items())),
        "velocity_p95_by_joint": {
            joint: percentile(values, 95) for joint, values in velocities_by_joint.items()
        },
        "velocity_max_by_joint": {
            joint: max(values) if values else None for joint, values in velocities_by_joint.items()
        },
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# BC Trace Transition Spike Filter",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.",
        "",
        "## Settings",
        "",
        f"- trace_globs: `{payload['trace_globs']}`",
        f"- output_trace_dir: `{payload['output_trace_dir']}`",
        f"- vector_key: `{payload['settings']['vector_key']}`",
        f"- joints: `{payload['settings']['joints']}`",
        f"- spike_velocity_rad_s: `{payload['settings']['spike_velocity_rad_s']}`",
        f"- transition_window_ticks: `{payload['settings']['transition_window_ticks']}`",
        f"- drop_window_ticks: `{payload['settings']['drop_window_ticks']}`",
        f"- output_mode: `{payload['settings']['output_mode']}`",
        "",
        "## Summary",
        "",
        f"- traces: `{payload['summary']['traces']}`",
        f"- samples_in: `{payload['summary']['samples_in']}`",
        f"- samples_out: `{payload['summary']['samples_out']}`",
        f"- samples_removed: `{payload['summary']['samples_removed']}`",
        f"- spike_ticks: `{payload['summary']['spike_ticks']}`",
        f"- removed_contact_counts: `{payload['summary']['removed_contact_counts']}`",
        "",
        "| source | in | out | removed | transitions | spikes | spike_contacts | removed_contacts |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for item in payload["traces"]:
        lines.append(
            "| {source} | {samples_in} | {samples_out} | {removed} | {transitions} | {spikes} | `{spike_contacts}` | `{removed_contacts}` |".format(
                source=Path(item["source_trace"]).name,
                samples_in=item["samples_in"],
                samples_out=item["samples_out"],
                removed=item["samples_removed"],
                transitions=item["contact_transitions"],
                spikes=item["spike_ticks"],
                spike_contacts=item["spike_contact_counts"],
                removed_contacts=item["removed_contact_counts"],
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- This only creates a filtered dataset source.",
            "- A pass here is not a policy pass.",
            "- Rebuild the BC manifest and run the strict fitted-bridge candidate gate before drawing deployment conclusions.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", required=True)
    parser.add_argument("--output-trace-dir", required=True)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--vector-key", default="action", choices=["action", "target_pre_rate_limit_rad"])
    parser.add_argument("--joints", default="right_knee")
    parser.add_argument("--spike-velocity-rad-s", type=float, default=3.75)
    parser.add_argument("--transition-window-ticks", type=int, default=2)
    parser.add_argument("--drop-window-ticks", type=int, default=1)
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--output-mode", default="transition_spike_filtered")
    parser.add_argument("--min-samples-out", type=int, default=100)
    args = parser.parse_args()

    paths: list[Path] = []
    for item in args.trace_glob:
        paths.extend(Path(path) for path in sorted(glob.glob(item)))
    paths = sorted(dict.fromkeys(paths))

    traces = [
        process_trace(path, Path(args.output_trace_dir), args)
        for path in paths
    ]
    samples_in = sum(item["samples_in"] for item in traces)
    samples_out = sum(item["samples_out"] for item in traces)
    removed_contacts = Counter()
    for item in traces:
        removed_contacts.update(item["removed_contact_counts"])

    status = "PASS_TRANSITION_SPIKE_FILTER_READY"
    if not traces:
        status = "HOLD_NO_TRACES"
    elif any(item["samples_out"] < args.min_samples_out for item in traces):
        status = "HOLD_FILTER_TOO_AGGRESSIVE"

    payload = {
        "status": status,
        "trace_globs": args.trace_glob,
        "output_trace_dir": args.output_trace_dir,
        "settings": {
            "vector_key": args.vector_key,
            "joints": [JOINT_NAMES[idx] for idx in parse_joints(args.joints)],
            "spike_velocity_rad_s": args.spike_velocity_rad_s,
            "transition_window_ticks": args.transition_window_ticks,
            "drop_window_ticks": args.drop_window_ticks,
            "action_scale": args.action_scale,
            "dt_s": args.dt_s,
            "output_mode": args.output_mode,
        },
        "summary": {
            "traces": len(traces),
            "samples_in": samples_in,
            "samples_out": samples_out,
            "samples_removed": samples_in - samples_out,
            "spike_ticks": sum(item["spike_ticks"] for item in traces),
            "removed_contact_counts": dict(sorted(removed_contacts.items())),
        },
        "traces": traces,
    }

    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"traces={len(traces)} samples_out={samples_out} removed={samples_in - samples_out}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
