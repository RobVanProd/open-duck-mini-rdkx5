#!/usr/bin/env python3
"""Filter and merge BC manifests by rollout quality metrics.

This is an offline curation helper. It does not train, deploy, SSH, or touch
the robot. It exists because a trace can be syntactically BC-ready while still
being a bad action label, for example a short reverse/fall rollout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def metric(entry: dict[str, Any], key: str, default: float | None = None) -> float | None:
    value = entry.get(key, default)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def entry_rejections(entry: dict[str, Any], args: argparse.Namespace) -> list[str]:
    reasons: list[str] = []
    source = source_name(entry)
    if args.include_source_regex and not re.search(args.include_source_regex, source):
        reasons.append("source_not_included")
    if args.exclude_source_regex and re.search(args.exclude_source_regex, source):
        reasons.append("source_excluded")
    if args.require_bc_ready and not bool(entry.get("bc_ready")):
        reasons.append("not_bc_ready")
    if args.require_raw_trace and not bool(entry.get("raw_trace_exists")):
        reasons.append("raw_trace_missing")
    if args.reject_done_inside and bool(entry.get("done_inside_window")):
        reasons.append("done_inside_window")
    samples = int(entry.get("samples") or 0)
    if samples < args.min_samples:
        reasons.append("too_few_samples")

    mean_vx = metric(entry, "mean_vx_m_s")
    if mean_vx is None or mean_vx < args.min_mean_vx:
        reasons.append("low_mean_vx")
    vy_abs_p95 = metric(entry, "vy_abs_p95_m_s")
    if vy_abs_p95 is None or vy_abs_p95 > args.max_vy_abs_p95:
        reasons.append("high_lateral_velocity")
    pitch_abs_p95 = metric(entry, "body_pitch_abs_p95_rad")
    if pitch_abs_p95 is None or pitch_abs_p95 > args.max_pitch_abs_p95:
        reasons.append("high_body_pitch")
    height_min = metric(entry, "base_height_min_m")
    if height_min is None or height_min < args.min_base_height:
        reasons.append("low_base_height")
    sent_vel95 = metric(entry, "sent_target_velocity_p95_rad_s")
    if sent_vel95 is None or sent_vel95 > args.max_sent_velocity_p95:
        reasons.append("high_target_velocity")
    tracking_p95 = metric(entry, "joint_tracking_p95_rad")
    if tracking_p95 is None or tracking_p95 > args.max_tracking_p95:
        reasons.append("high_tracking_error")
    return reasons


def source_name(entry: dict[str, Any]) -> str:
    return str(entry.get("source_name") or entry.get("source_path") or "UNKNOWN")


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Filtered BC Manifest",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.",
        "",
        "## Inputs",
        "",
    ]
    for path in payload["input_manifests"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Thresholds",
            "",
        ]
    )
    for key, value in payload["thresholds"].items():
        lines.append(f"- {key}: `{value}`")
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- input_entries: `{summary['input_entries']}`",
            f"- kept_entries: `{summary['kept_entries']}`",
            f"- rejected_entries: `{summary['rejected_entries']}`",
            f"- samples: `{summary['samples']}`",
            f"- source_files: `{summary['source_files']}`",
            f"- max_source_fraction: `{summary['max_source_fraction']:.4f}`",
            "",
            "### Rejection Reasons",
            "",
            "| reason | count |",
            "|---|---:|",
        ]
    )
    for reason, count in payload["rejection_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(
        [
            "",
            "### Kept Entries",
            "",
            "| source | samples | vx | sent_vel95 | track95 | pitch95 | height |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for entry in payload["entries"]:
        lines.append(
            "| {source} | {samples} | {vx:.4f} | {sent:.4f} | {track:.4f} | {pitch:.4f} | {height:.4f} |".format(
                source=source_name(entry),
                samples=int(entry.get("samples") or 0),
                vx=metric(entry, "mean_vx_m_s", 0.0) or 0.0,
                sent=metric(entry, "sent_target_velocity_p95_rad_s", 0.0) or 0.0,
                track=metric(entry, "joint_tracking_p95_rad", 0.0) or 0.0,
                pitch=metric(entry, "body_pitch_abs_p95_rad", 0.0) or 0.0,
                height=metric(entry, "base_height_min_m", 0.0) or 0.0,
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- Kept entries are suitable as positive BC labels for the next supervised fit.",
            "- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", action="append", required=True, help="Input manifest JSON. Repeatable.")
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--min-entries", type=int, default=1)
    parser.add_argument("--min-samples", type=int, default=100)
    parser.add_argument("--min-mean-vx", type=float, default=0.03)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.25)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.25)
    parser.add_argument("--min-base-height", type=float, default=0.12)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=2.5)
    parser.add_argument("--max-tracking-p95", type=float, default=0.2)
    parser.add_argument(
        "--include-source-regex",
        default=None,
        help="Keep only entries whose source name/path matches this regex.",
    )
    parser.add_argument(
        "--exclude-source-regex",
        default=None,
        help="Reject entries whose source name/path matches this regex.",
    )
    parser.add_argument("--require-bc-ready", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--require-raw-trace", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--reject-done-inside", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    input_paths = [Path(item) for item in args.manifest]
    all_entries: list[dict[str, Any]] = []
    for path in input_paths:
        payload = load_json(path)
        for entry in payload.get("entries") or []:
            copied = dict(entry)
            copied["input_manifest"] = str(path)
            all_entries.append(copied)

    kept: list[dict[str, Any]] = []
    rejection_counts: Counter[str] = Counter()
    rejected_entries: list[dict[str, Any]] = []
    for entry in all_entries:
        reasons = entry_rejections(entry, args)
        if reasons:
            rejection_counts.update(reasons)
            rejected_entries.append(
                {
                    "source_name": source_name(entry),
                    "entry_id": entry.get("entry_id"),
                    "reasons": reasons,
                    "input_manifest": entry.get("input_manifest"),
                }
            )
        else:
            kept.append(entry)

    kept.sort(key=lambda item: (source_name(item), int(item.get("start_tick") or 0), str(item.get("entry_id"))))
    by_source = Counter(source_name(entry) for entry in kept)
    digest = hashlib.sha256(json.dumps(kept, sort_keys=True).encode()).hexdigest()[:16]
    status = "PASS_FILTERED_BC_MANIFEST_READY" if len(kept) >= args.min_entries else "HOLD_FILTERED_BC_MANIFEST_TOO_SMALL"
    payload = {
        "status": status,
        "dataset_id": digest,
        "input_manifests": [str(path) for path in input_paths],
        "thresholds": {
            "min_entries": args.min_entries,
            "min_samples": args.min_samples,
            "min_mean_vx": args.min_mean_vx,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_pitch_abs_p95": args.max_pitch_abs_p95,
            "min_base_height": args.min_base_height,
            "max_sent_velocity_p95": args.max_sent_velocity_p95,
            "max_tracking_p95": args.max_tracking_p95,
            "include_source_regex": args.include_source_regex,
            "exclude_source_regex": args.exclude_source_regex,
            "require_bc_ready": args.require_bc_ready,
            "require_raw_trace": args.require_raw_trace,
            "reject_done_inside": args.reject_done_inside,
        },
        "summary": {
            "input_entries": len(all_entries),
            "kept_entries": len(kept),
            "rejected_entries": len(rejected_entries),
            "samples": int(sum(int(entry.get("samples") or 0) for entry in kept)),
            "source_files": len(by_source),
            "max_source_fraction": (max(by_source.values()) / len(kept)) if kept else 0.0,
        },
        "rejection_counts": dict(sorted(rejection_counts.items())),
        "rejected_entries": rejected_entries,
        "entries": kept,
    }
    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_md = Path(args.output_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"status={status}")
    print(f"dataset_id={digest}")
    print(f"kept_entries={len(kept)}")
    print(f"wrote {out_md}")
    print(f"wrote {out_json}")
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
