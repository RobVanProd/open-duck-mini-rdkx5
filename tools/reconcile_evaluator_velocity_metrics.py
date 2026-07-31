#!/usr/bin/env python3
"""Compare BC-smoke velocity metrics with the canonical strict evaluator.

This tool is intentionally read-only. It exists to prevent confusing the
flattened all-joint BC-smoke `sent_vel95` metric with the strict gate's
max-per-pitch-joint p95 velocity.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def finite(value: Any) -> bool:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return False
    return value == value and value not in {float("inf"), float("-inf")}


def fmt(value: Any, digits: int = 4) -> str:
    if not finite(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def load_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text())


def bc_smoke_rows(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not payload:
        return []
    rollout = payload.get("rollout") or {}
    modes = rollout.get("modes") or {}
    rows: list[dict[str, Any]] = []
    for seed, mode in sorted(modes.items()):
        rows.append(
            {
                "source": "bc_smoke",
                "seed": seed,
                "status": mode.get("status"),
                "samples": mode.get("samples"),
                "termination": mode.get("termination_reason"),
                "flat_all_joint_sent_vel95_rad_s": mode.get(
                    "sent_target_velocity_p95_rad_s"
                ),
                "joint_tracking_p95_rad": mode.get("joint_tracking_p95_rad"),
                "mean_vx_m_s": mode.get("mean_vx_m_s"),
                "track_ratio": mode.get("track_ratio"),
            }
        )
    return rows


def canonical_rows(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not payload:
        return []
    rows: list[dict[str, Any]] = []

    # run_candidate_seed_sweep summary schema
    for result in payload.get("results") or []:
        summary = result.get("summary") or {}
        rows.append(
            {
                "source": "canonical_seed_sweep",
                "seed": result.get("seed"),
                "status": result.get("status"),
                "samples": summary.get("samples"),
                "termination": summary.get("termination_reason"),
                "max_pitch_joint_sent_vel95_rad_s": summary.get(
                    "max_pitch_vel_p95_rad_s"
                ),
                "max_pitch_tracking_p95_rad": summary.get("max_tracking_p95_rad"),
                "mean_vx_m_s": summary.get("mean_local_vx_m_s"),
                "track_ratio": summary.get("track_ratio"),
            }
        )

    # single eval_policy_with_actuator_bridge schema
    closed = payload.get("closed_loop_sim") or {}
    modes = closed.get("modes") or {}
    gate = closed.get("candidate_gate") or {}
    metrics = gate.get("metrics") or {}
    if modes and not rows:
        for name, mode in sorted(modes.items()):
            forward = mode.get("forward_motion") or {}
            rows.append(
                {
                    "source": f"canonical_eval:{name}",
                    "seed": mode.get("seed"),
                    "status": gate.get("status") or payload.get("overall_status"),
                    "samples": mode.get("samples"),
                    "termination": mode.get("termination_reason"),
                    "max_pitch_joint_sent_vel95_rad_s": metrics.get(
                        "max_sent_target_velocity_p95_rad_s"
                    ),
                    "max_pitch_tracking_p95_rad": metrics.get(
                        "max_pitch_tracking_p95_rad"
                    ),
                    "mean_vx_m_s": forward.get("mean_velocity_x_m_s"),
                    "track_ratio": forward.get("command_tracking_ratio"),
                }
            )
    return rows


def max_metric(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if finite(row.get(key))]
    return max(values) if values else None


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Evaluator Velocity Metric Reconciliation",
        "",
        f"status: `{report['status']}`",
        "",
        "This read-only comparison separates the BC-smoke flattened all-joint",
        "velocity metric from the canonical strict gate's max-per-pitch-joint",
        "velocity metric.",
        "",
        "## Inputs",
        "",
        f"- bc_smoke_json: `{report.get('bc_smoke_json') or 'None'}`",
        f"- canonical_json: `{report.get('canonical_json') or 'None'}`",
        "",
        "## Summary",
        "",
        f"- BC smoke max flattened sent_vel95: `{fmt(report.get('bc_flat_sent_vel95_max_rad_s'))}` rad/s",
        f"- canonical max pitch-joint sent_vel95: `{fmt(report.get('canonical_pitch_sent_vel95_max_rad_s'))}` rad/s",
        f"- canonical max pitch tracking p95: `{fmt(report.get('canonical_pitch_tracking_p95_max_rad'))}` rad",
        "",
        "## BC Smoke Rows",
        "",
        "| seed | status | samples | termination | flat_sent_vel95 | track95 | vx | ratio |",
        "|---|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in report["bc_smoke_rows"]:
        lines.append(
            "| {seed} | `{status}` | {samples} | `{term}` | {vel} | {track} | {vx} | {ratio} |".format(
                seed=row.get("seed"),
                status=row.get("status"),
                samples=row.get("samples"),
                term=row.get("termination"),
                vel=fmt(row.get("flat_all_joint_sent_vel95_rad_s")),
                track=fmt(row.get("joint_tracking_p95_rad")),
                vx=fmt(row.get("mean_vx_m_s")),
                ratio=fmt(row.get("track_ratio")),
            )
        )
    lines.extend(
        [
            "",
            "## Canonical Rows",
            "",
            "| seed | status | samples | termination | max_pitch_sent_vel95 | max_pitch_track95 | vx | ratio |",
            "|---|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["canonical_rows"]:
        lines.append(
            "| {seed} | `{status}` | {samples} | `{term}` | {vel} | {track} | {vx} | {ratio} |".format(
                seed=row.get("seed"),
                status=row.get("status"),
                samples=row.get("samples"),
                term=row.get("termination"),
                vel=fmt(row.get("max_pitch_joint_sent_vel95_rad_s")),
                track=fmt(row.get("max_pitch_tracking_p95_rad")),
                vx=fmt(row.get("mean_vx_m_s")),
                ratio=fmt(row.get("track_ratio")),
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Use the canonical strict evaluator for promotion decisions. The BC",
            "smoke metric is useful for quick replay debugging, but because it",
            "flattens all joints and ticks it can mask a pitch-joint envelope",
            "violation.",
            "",
            "Gate result: `PASS_EVALUATOR_CANONICAL`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bc-smoke-json")
    parser.add_argument("--canonical-json")
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/EVALUATOR_RECONCILIATION_METRIC_COMPARE.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/evaluator_reconciliation_metric_compare.json",
    )
    args = parser.parse_args()

    bc_payload = load_json(args.bc_smoke_json)
    canonical_payload = load_json(args.canonical_json)
    bc_rows = bc_smoke_rows(bc_payload)
    canon_rows = canonical_rows(canonical_payload)
    report = {
        "status": "PASS_EVALUATOR_CANONICAL",
        "bc_smoke_json": args.bc_smoke_json,
        "canonical_json": args.canonical_json,
        "bc_smoke_rows": bc_rows,
        "canonical_rows": canon_rows,
        "bc_flat_sent_vel95_max_rad_s": max_metric(
            bc_rows, "flat_all_joint_sent_vel95_rad_s"
        ),
        "canonical_pitch_sent_vel95_max_rad_s": max_metric(
            canon_rows, "max_pitch_joint_sent_vel95_rad_s"
        ),
        "canonical_pitch_tracking_p95_max_rad": max_metric(
            canon_rows, "max_pitch_tracking_p95_rad"
        ),
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2))
    write_markdown(report, Path(args.output_md))
    print(report["status"])
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
