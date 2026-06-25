#!/usr/bin/env python3
"""Audit curated target windows for contact-timed reference snippet readiness.

This is an offline trace audit. It does not run simulation, train, deploy, SSH,
or touch the robot. It answers the first contact-timing question: do the
curated low-command source fragments themselves contain usable single-support
alternation, or are they stable because they mostly remain in double support?
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

from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CURATION = (
    ROOT
    / "outputs"
    / "analysis"
    / "target_generator_dynamic_roll_lateral_fix_robust_modes_curation_50.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "CONTACT_TIMED_REFERENCE_SNIPPETS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "contact_timed_reference_snippets.json"
DEFAULT_MANIFEST = (
    ROOT / "outputs" / "analysis" / "contact_timed_reference_snippets_manifest.json"
)


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def contact_pattern(values: Any) -> str:
    if not isinstance(values, list | tuple) or len(values) < 2:
        return "00"
    return "".join(str(int(bool(value))) for value in values[:2])


def support_metrics(patterns: list[str]) -> dict[str, Any]:
    total = len(patterns)
    counts = Counter(patterns)
    pct = {
        key: float(value / total * 100.0) for key, value in sorted(counts.items())
    } if total else {}
    longest = {}
    for pattern in ["00", "01", "10", "11"]:
        run = 0
        best = 0
        for item in patterns:
            if item == pattern:
                run += 1
                best = max(best, run)
            else:
                run = 0
        longest[pattern] = int(best)
    transitions = sum(1 for a, b in zip(patterns, patterns[1:]) if a != b)
    support_a = float(pct.get("10", 0.0))
    support_b = float(pct.get("01", 0.0))
    return {
        "contact_pct": pct,
        "contact_dominance_pct": max(pct.values()) if pct else 0.0,
        "double_support_pct": float(pct.get("11", 0.0)),
        "no_support_pct": float(pct.get("00", 0.0)),
        "single_support_pct": support_a + support_b,
        "support_a_only_pct": support_a,
        "support_b_only_pct": support_b,
        "min_single_support_side_pct": min(support_a, support_b),
        "contact_transitions": int(transitions),
        "longest_contact_run_ticks": longest,
        "contact_sequence_preview": "".join(patterns[:20]),
    }


def entry_id(window: dict[str, Any]) -> str:
    payload = {
        "source_path": window.get("source_path"),
        "mode": window.get("mode"),
        "start_tick": window.get("start_tick"),
        "end_tick": window.get("end_tick"),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def load_window_records(window: dict[str, Any]) -> list[dict[str, Any]]:
    source_path = Path(str(window["source_path"]))
    mode = str(window["mode"])
    start = int(window["start_tick"])
    end = int(window["end_tick"])
    records = [
        record
        for record in read_jsonl(source_path)
        if str(record.get("mode")) == mode and start <= int(record.get("tick", -1)) <= end
    ]
    records.sort(key=lambda record: int(record.get("tick", 0)))
    return records


def window_summary(window: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    records = load_window_records(window)
    patterns = [contact_pattern(record.get("foot_contacts")) for record in records]
    support = support_metrics(patterns)
    vx = [float(record["local_linvel_m_s"][0]) for record in records if record.get("local_linvel_m_s")]
    vy = [
        abs(float(record["local_linvel_m_s"][1]))
        for record in records
        if record.get("local_linvel_m_s") and len(record["local_linvel_m_s"]) > 1
    ]
    pitch = [abs(float(record.get("body_pitch_rad", 0.0))) for record in records]
    height = [float(record.get("base_height_m", 0.0)) for record in records]
    sent = np.asarray([record.get("sent_target_rad", []) for record in records], dtype=float)
    actual = np.asarray([record.get("actual_position_rad", []) for record in records], dtype=float)
    if sent.ndim == 2 and sent.shape[0] > 1:
        sent_velocity = np.abs(np.diff(sent, axis=0) / max(args.dt_s, 1.0e-9))
    else:
        sent_velocity = np.zeros((0, 0))
    tracking = np.abs(sent - actual) if sent.size and actual.size else np.zeros((0, 0))
    reasons = []
    if support["single_support_pct"] < args.min_single_support_pct:
        reasons.append("too_little_single_support")
    if support["min_single_support_side_pct"] < args.min_each_single_support_pct:
        reasons.append("single_support_not_balanced")
    if support["double_support_pct"] > args.max_double_support_pct:
        reasons.append("double_support_dominates")
    if support["contact_transitions"] < args.min_contact_transitions:
        reasons.append("too_few_contact_transitions")
    mean_vx = float(np.mean(vx)) if vx else 0.0
    if mean_vx < args.min_mean_vx:
        reasons.append("low_forward_velocity")
    if percentile(vy, 95) > args.max_vy_abs_p95:
        reasons.append("high_lateral_velocity")
    if percentile(pitch, 95) > args.max_pitch_abs_p95:
        reasons.append("high_body_pitch")
    if (min(height) if height else 0.0) < args.min_base_height:
        reasons.append("low_base_height")
    if (
        sent_velocity.size
        and percentile(sent_velocity.reshape(-1).tolist(), 95) > args.max_sent_velocity_p95
    ):
        reasons.append("high_sent_target_velocity")
    return {
        "entry_id": entry_id(window),
        "source_path": str(window["source_path"]),
        "source_name": Path(str(window["source_path"])).name,
        "mode": window.get("mode"),
        "start_tick": int(window.get("start_tick")),
        "end_tick": int(window.get("end_tick")),
        "samples": len(records),
        "mean_vx_m_s": float(np.mean(vx)) if vx else None,
        "vy_abs_p95_m_s": percentile(vy, 95),
        "body_pitch_abs_p95_rad": percentile(pitch, 95),
        "base_height_min_m": float(min(height)) if height else None,
        "sent_target_velocity_p95_rad_s": (
            percentile(sent_velocity.reshape(-1).tolist(), 95)
            if sent_velocity.size
            else None
        ),
        "joint_tracking_p95_rad": (
            percentile(tracking.reshape(-1).tolist(), 95) if tracking.size else None
        ),
        **support,
        "status": "PASS_CONTACT_TIMED_FRAGMENT" if not reasons else "HOLD_CONTACT_FRAGMENT",
        "reasons": reasons,
        "raw_trace_exists": Path(str(window["source_path"])).exists(),
    }


def overall_status(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return "HOLD_NO_CONTACT_SNIPPETS"
    if any(entry["status"] == "PASS_CONTACT_TIMED_FRAGMENT" for entry in entries):
        return "PASS_CONTACT_TIMED_SNIPPETS_READY"
    if all("double_support_dominates" in entry.get("reasons", []) for entry in entries):
        return "HOLD_SOURCE_FRAGMENTS_DOUBLE_SUPPORT"
    return "HOLD_NO_CONTACT_TIMED_SNIPPETS"


def stats(values: list[Any]) -> dict[str, float | None]:
    data = [float(value) for value in values if finite(value)]
    if not data:
        return {"min": None, "mean": None, "p50": None, "p95": None, "max": None}
    return {
        "min": float(np.min(data)),
        "mean": float(np.mean(data)),
        "p50": percentile(data, 50),
        "p95": percentile(data, 95),
        "max": float(np.max(data)),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Contact-Timed Reference Snippets",
        "",
        f"status: `{payload['status']}`",
        "",
        "This audits curated low-command target windows for contact timing.",
        "It does not run simulation, train, deploy, SSH, or touch the robot.",
        "",
        "## Summary",
        "",
        f"- curation_json: `{payload['curation_json']}`",
        f"- manifest_json: `{payload['manifest_json']}`",
        f"- entries: `{payload['summary']['entries']}`",
        f"- pass_entries: `{payload['summary']['pass_entries']}`",
        f"- double_support_hold_entries: `{payload['summary']['double_support_hold_entries']}`",
        f"- contact_transitions_mean: `{fmt(payload['summary']['contact_transitions']['mean'])}`",
        f"- single_support_pct_mean: `{fmt(payload['summary']['single_support_pct']['mean'])}`",
        f"- double_support_pct_mean: `{fmt(payload['summary']['double_support_pct']['mean'])}`",
        "",
        "## Criteria",
        "",
    ]
    for key, value in payload["criteria"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Snippets",
            "",
            "| id | status | reasons | ticks | vx | vy95 | pitch95 | height | single% | double% | trans | longest11 | sequence_preview |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for entry in payload["entries"]:
        longest = entry.get("longest_contact_run_ticks") or {}
        lines.append(
            "| {id} | `{status}` | `{reasons}` | {ticks} | {vx} | {vy} | {pitch} | {height} | {single} | {double} | {trans} | {longest11} | `{preview}` |".format(
                id=entry["entry_id"],
                status=entry["status"],
                reasons=", ".join(entry.get("reasons") or []),
                ticks=f"{entry['start_tick']}-{entry['end_tick']}",
                vx=fmt(entry.get("mean_vx_m_s")),
                vy=fmt(entry.get("vy_abs_p95_m_s")),
                pitch=fmt(entry.get("body_pitch_abs_p95_rad")),
                height=fmt(entry.get("base_height_min_m")),
                single=fmt(entry.get("single_support_pct")),
                double=fmt(entry.get("double_support_pct")),
                trans=fmt(entry.get("contact_transitions"), digits=0),
                longest11=fmt(longest.get("11"), digits=0),
                preview=entry.get("contact_sequence_preview"),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- If source fragments already contain clean single-support alternation, the next blocker is closed-loop policy/contact execution.",
            "- If source fragments are mostly double support, the target generator must explicitly search for single-support/weight-transfer windows before PPO or BC.",
            "- Do not launch training from snippets that fail this contact-timing audit.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curation-json", default=str(DEFAULT_CURATION))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--manifest-json", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--max-snippets", type=int, default=0)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.35)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=3.75)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-each-single-support-pct", type=float, default=5.0)
    parser.add_argument("--max-double-support-pct", type=float, default=75.0)
    parser.add_argument("--min-contact-transitions", type=int, default=2)
    args = parser.parse_args()

    curation = json.loads(Path(args.curation_json).read_text())
    windows = list(curation.get("curated_seed_windows") or [])
    if args.max_snippets > 0:
        windows = windows[: args.max_snippets]
    entries = [window_summary(window, args) for window in windows]
    status = overall_status(entries)
    pass_entries = [entry for entry in entries if entry["status"] == "PASS_CONTACT_TIMED_FRAGMENT"]
    double_holds = [
        entry for entry in entries if "double_support_dominates" in entry.get("reasons", [])
    ]
    digest = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]
    criteria = {
        "min_mean_vx": args.min_mean_vx,
        "max_vy_abs_p95": args.max_vy_abs_p95,
        "max_pitch_abs_p95": args.max_pitch_abs_p95,
        "min_base_height": args.min_base_height,
        "max_sent_velocity_p95": args.max_sent_velocity_p95,
        "min_single_support_pct": args.min_single_support_pct,
        "min_each_single_support_pct": args.min_each_single_support_pct,
        "max_double_support_pct": args.max_double_support_pct,
        "min_contact_transitions": args.min_contact_transitions,
    }
    manifest = {
        "status": status,
        "input_curation_json": str(Path(args.curation_json)),
        "dataset_id": digest,
        "criteria": criteria,
        "summary": {
            "entries": len(entries),
            "pass_entries": len(pass_entries),
            "double_support_hold_entries": len(double_holds),
            "raw_traces_present": all(entry["raw_trace_exists"] for entry in entries),
        },
        "entries": entries,
    }
    payload = {
        **manifest,
        "curation_json": str(Path(args.curation_json)),
        "manifest_json": str(Path(args.manifest_json)),
        "summary": {
            **manifest["summary"],
            "single_support_pct": stats([entry["single_support_pct"] for entry in entries]),
            "double_support_pct": stats([entry["double_support_pct"] for entry in entries]),
            "contact_transitions": stats([entry["contact_transitions"] for entry in entries]),
        },
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    manifest_json = Path(args.manifest_json)
    manifest_json.parent.mkdir(parents=True, exist_ok=True)
    manifest_json.write_text(json.dumps(manifest, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"entries={len(entries)}")
    print(f"pass_entries={len(pass_entries)}")
    print(f"double_support_hold_entries={len(double_holds)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.manifest_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
