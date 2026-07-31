#!/usr/bin/env python3
"""Classify Phase 2 seed failures by motion mode.

This is an offline analysis helper. It reads an existing seed sweep JSON and
optional JSONL traces, then separates forward lunges, reverse pitch-backs,
low-height collapses, low-progress holds, and actuator-envelope holds. It does
not train, deploy, SSH, touch the robot, or modify Playground.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def finite_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result or result in (float("inf"), float("-inf")):
        return None
    return result


def trace_path(trace_root: Path, policy: str, seed: int) -> Path:
    return trace_root / policy / f"seed_{seed:03d}" / "trace.jsonl"


def result_summary(result: dict[str, Any]) -> dict[str, Any]:
    return result.get("summary") or result.get("result_summary") or {}


def classify(summary: dict[str, Any], rows: list[dict[str, Any]], velocity_excess_tolerance: float) -> tuple[str, list[str]]:
    status = str(result_summary({"summary": summary}).get("candidate_gate_status") or summary.get("overall_status") or "")
    final = rows[-1] if rows else {}
    final_vx = None
    local = final.get("local_linvel_m_s")
    if isinstance(local, list | tuple) and local:
        final_vx = finite_float(local[0])
    final_pitch = finite_float(final.get("body_pitch_rad"))
    final_height = finite_float(final.get("base_height_m"))
    track_ratio = finite_float(summary.get("track_ratio"))
    max_excess = finite_float(summary.get("max_pitch_vel_max_limit_excess_rad_s"))
    p95_excess = finite_float(summary.get("max_pitch_vel_limit_excess_rad_s"))
    samples = int(summary.get("samples") or 0)
    push_events = int(summary.get("push_event_count") or 0)

    reasons: list[str] = []
    if (p95_excess or 0.0) > velocity_excess_tolerance or (max_excess or 0.0) > velocity_excess_tolerance:
        reasons.append("actuator_envelope_excess")
    if final_vx is not None and final_vx <= -0.75:
        reasons.append("reverse_velocity")
    if final_vx is not None and final_vx >= 0.75:
        reasons.append("forward_lunge_velocity")
    if final_pitch is not None and final_pitch <= -0.8:
        reasons.append("pitch_back")
    if final_pitch is not None and final_pitch >= 0.8:
        reasons.append("pitch_forward")
    if final_height is not None and final_height < 0.08:
        reasons.append("low_base_height")
    if track_ratio is not None and track_ratio < 0.2 and samples >= 700:
        reasons.append("low_progress")
    if push_events == 0 and samples < 100:
        reasons.append("pre_push_failure")

    if "PASS" in status:
        return "PASS", reasons
    if "actuator_envelope_excess" in reasons:
        return "ACTUATOR_ENVELOPE_EXCESS", reasons
    if "reverse_velocity" in reasons or "pitch_back" in reasons:
        if "pre_push_failure" in reasons:
            return "PRE_PUSH_REVERSE_PITCHBACK", reasons
        return "REVERSE_PITCHBACK", reasons
    if "forward_lunge_velocity" in reasons or "pitch_forward" in reasons:
        return "FORWARD_LUNGE_PITCHOVER", reasons
    if "low_base_height" in reasons:
        return "LOW_HEIGHT_COLLAPSE", reasons
    if "low_progress" in reasons:
        return "LOW_PROGRESS_DURATION", reasons
    return "UNCLASSIFIED_HOLD", reasons


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 2 Seed Failure Modes",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline seed-distribution analysis. It did not train, SSH,",
        "deploy, touch the robot, or modify Playground.",
        "",
        "## Inputs",
        "",
        f"- sweep_json: `{payload['sweep_json']}`",
        f"- trace_root: `{payload['trace_root']}`",
        f"- velocity_excess_tolerance: `{payload['velocity_excess_tolerance']}`",
        "",
        "## Summary",
        "",
        f"- seeds: `{payload['summary']['seeds']}`",
        f"- status_counts: `{payload['summary']['status_counts']}`",
        f"- mode_counts: `{payload['summary']['mode_counts']}`",
        "",
        "## Per-Seed Modes",
        "",
        "| seed | status | mode | samples | track | final_vx | final_pitch | final_height | p95_excess | max_excess | reasons |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in payload["seeds"]:
        lines.append(
            "| {seed} | `{status}` | `{mode}` | {samples} | {track} | {vx} | {pitch} | {height} | {p95} | {maxex} | `{reasons}` |".format(
                seed=item["seed"],
                status=item["status"],
                mode=item["mode"],
                samples=item["samples"],
                track=fmt(item.get("track_ratio")),
                vx=fmt(item.get("final_vx_m_s")),
                pitch=fmt(item.get("final_pitch_rad")),
                height=fmt(item.get("final_base_height_m")),
                p95=fmt(item.get("p95_velocity_excess_rad_s")),
                maxex=fmt(item.get("max_velocity_excess_rad_s")),
                reasons=item.get("reasons"),
            )
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            payload["recommendation"],
        ]
    )
    return "\n".join(lines) + "\n"


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep-json", required=True)
    parser.add_argument("--trace-root", required=True)
    parser.add_argument("--velocity-excess-tolerance", type=float, default=0.1)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    sweep_path = Path(args.sweep_json)
    trace_root = Path(args.trace_root)
    sweep = load_json(sweep_path)
    seed_items: list[dict[str, Any]] = []
    mode_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()

    for result in sweep.get("results") or []:
        seed = int(result.get("seed"))
        policy_name = str(result.get("policy_name") or result.get("policy_label") or "")
        if not policy_name:
            policy_path = Path(str(result.get("policy") or "policy"))
            policy_name = policy_path.stem
        summary = result_summary(result)
        rows = read_jsonl(trace_path(trace_root, policy_name, seed))
        mode, reasons = classify(summary, rows, float(args.velocity_excess_tolerance))
        final = rows[-1] if rows else {}
        local = final.get("local_linvel_m_s")
        final_vx = finite_float(local[0]) if isinstance(local, list | tuple) and local else None
        item = {
            "seed": seed,
            "policy_name": policy_name,
            "status": result.get("status") or summary.get("candidate_gate_status"),
            "mode": mode,
            "reasons": reasons,
            "samples": summary.get("samples"),
            "track_ratio": summary.get("track_ratio"),
            "final_vx_m_s": final_vx,
            "final_pitch_rad": finite_float(final.get("body_pitch_rad")),
            "final_base_height_m": finite_float(final.get("base_height_m")),
            "p95_velocity_excess_rad_s": summary.get("max_pitch_vel_limit_excess_rad_s"),
            "max_velocity_excess_rad_s": summary.get("max_pitch_vel_max_limit_excess_rad_s"),
            "trace_path": str(trace_path(trace_root, policy_name, seed)),
        }
        seed_items.append(item)
        mode_counts[mode] += 1
        status_counts[str(item["status"])] += 1

    status = "PASS_SEED_FAILURE_MODE_REPORT_READY" if seed_items else "HOLD_NO_SEED_RESULTS"
    recommendation = (
        "The next recovery dataset should cover each populated failure mode, not only the compact seed0/seed7 pair. "
        "If reverse pitch-back and forward lunge both appear, use seed-diverse live-oracle relabels plus pass-control traces; "
        "do not add a single scalar damping or progress term and call it distributional."
    )
    payload = {
        "status": status,
        "sweep_json": str(sweep_path),
        "trace_root": str(trace_root),
        "velocity_excess_tolerance": float(args.velocity_excess_tolerance),
        "summary": {
            "seeds": len(seed_items),
            "status_counts": dict(sorted(status_counts.items())),
            "mode_counts": dict(sorted(mode_counts.items())),
        },
        "seeds": sorted(seed_items, key=lambda item: item["seed"]),
        "recommendation": recommendation,
    }

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md = Path(args.output_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_md(payload), encoding="utf-8")
    print(status)
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
