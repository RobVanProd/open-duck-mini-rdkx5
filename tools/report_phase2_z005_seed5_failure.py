#!/usr/bin/env python3
"""Summarize the shared z=0.005 seed-5 support failure.

This is an offline read-only diagnostic. It compares the current candidate's
seed-5 failures at x=0.08 and x=0.0 on z=0.005 terrain, using closed-loop worker
summaries already produced by the corrected-bridge evaluator. It does not train,
SSH, deploy, touch the robot, or modify Playground.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_X008_WORKER = (
    ROOT
    / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z005_nopush_15s_8seed_cpu/gain099/seed_005/closed_loop_worker_k9_n5vra.json"
)
DEFAULT_X000_WORKER = (
    ROOT
    / "outputs/analysis/candidate_seed_sweep/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_005/closed_loop_worker_xre180ac.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z005_SEED5_FAILURE_DIAGNOSTIC.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z005_seed5_failure_diagnostic.json"


PITCH_CHAIN = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def stat(stats: dict[str, Any] | None, name: str, default: Any = None) -> Any:
    if not isinstance(stats, dict):
        return default
    return stats.get(name, default)


def mode_summary(worker: dict[str, Any]) -> dict[str, Any]:
    mode = worker["modes"]["fitted"]
    foot = mode.get("foot_clearance", {})
    support = foot.get("support", {}) if isinstance(foot, dict) else {}
    forward = mode.get("forward_motion", {})
    pitch = mode.get("pitch_chain_summary", {})
    reward_terms = mode.get("reward_terms", {})
    left_foot = foot.get("feet", {}).get("left", {}) if isinstance(foot, dict) else {}
    right_foot = foot.get("feet", {}).get("right", {}) if isinstance(foot, dict) else {}
    return {
        "status": worker.get("status"),
        "command_x": (worker.get("command") or [None])[0],
        "samples": mode.get("samples"),
        "termination_reason": mode.get("termination_reason"),
        "elapsed_s": (mode.get("samples") or 0) * 0.02,
        "mean_local_vx_m_s": stat(mode.get("local_forward_velocity_m_s"), "mean"),
        "track_ratio": forward.get("command_tracking_ratio"),
        "base_height_min_m": stat(mode.get("base_height_m"), "min"),
        "body_pitch_p95_rad": stat(mode.get("body_pitch_rad"), "p95"),
        "body_pitch_min_rad": stat(mode.get("body_pitch_rad"), "min"),
        "body_pitch_max_rad": stat(mode.get("body_pitch_rad"), "max"),
        "single_support_pct": support.get("single_support_pct"),
        "double_support_pct": support.get("double_support_pct"),
        "no_contact_pct": support.get("no_contact_pct"),
        "left_contact_pct": support.get("left_contact_pct"),
        "right_contact_pct": support.get("right_contact_pct"),
        "left_swing_peak_lift_m": left_foot.get("swing_peak_lift_over_stance_m"),
        "right_swing_peak_lift_m": right_foot.get("swing_peak_lift_over_stance_m"),
        "left_swing_segments": left_foot.get("swing_segment_count"),
        "right_swing_segments": right_foot.get("swing_segment_count"),
        "left_swing_rel_x_range_p95_m": stat(left_foot.get("swing_segment_rel_x_range_m"), "p95"),
        "right_swing_rel_x_range_p95_m": stat(right_foot.get("swing_segment_rel_x_range_m"), "p95"),
        "max_joint_tracking_p95_rad": stat(pitch.get("joint_target_tracking_p95_rad"), "max"),
        "max_sent_vel_p95_rad_s": stat(pitch.get("sent_target_velocity_p95_rad_s"), "max"),
        "max_velocity_excess_rad_s": stat(pitch.get("sent_target_velocity_limit_excess_rad_s"), "max", 0.0),
        "action_rate_cost_mean": stat(reward_terms.get("cost/action_rate"), "mean"),
        "stand_still_cost_mean": stat(reward_terms.get("cost/stand_still"), "mean"),
        "reward_tracking_lin_vel_mean": stat(reward_terms.get("reward/tracking_lin_vel"), "mean"),
        "reward_tracking_ang_vel_mean": stat(reward_terms.get("reward/tracking_ang_vel"), "mean"),
    }


def classify(summary: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if summary["termination_reason"] == "fall_or_nan":
        findings.append("falls before 1.3s")
    if (summary["base_height_min_m"] or 1.0) < 0.08:
        findings.append("base-height collapse")
    if (summary["max_velocity_excess_rad_s"] or 0.0) <= 0.0:
        findings.append("no corrected-envelope velocity excess")
    if (summary["max_sent_vel_p95_rad_s"] or 99.0) < 2.5:
        findings.append("low target-rate demand")
    if (summary["double_support_pct"] or 0.0) > 80.0:
        findings.append("double-support dominated")
    if (summary["mean_local_vx_m_s"] or 0.0) < -0.05:
        findings.append("backward drift/collapse")
    return findings


def collect(args: argparse.Namespace) -> dict[str, Any]:
    x008 = mode_summary(read_json(Path(args.x008_worker)))
    x000 = mode_summary(read_json(Path(args.x000_worker)))
    shared = []
    if all((item["base_height_min_m"] or 1.0) < 0.08 for item in [x008, x000]):
        shared.append("seed 5 collapses vertically on z=0.005 in both command modes")
    if all((item["mean_local_vx_m_s"] or 0.0) < -0.05 for item in [x008, x000]):
        shared.append("failure is backward-biased even at zero command")
    if all((item["max_velocity_excess_rad_s"] or 0.0) <= 0.0 for item in [x008, x000]):
        shared.append("failure is not caused by corrected-envelope velocity excess")
    if all((item["double_support_pct"] or 0.0) > 80.0 for item in [x008, x000]):
        shared.append("support pattern is double-support dominated before collapse")
    return {
        "status": "HOLD_Z005_SEED5_SUPPORT_COLLAPSE_DIAGNOSED",
        "x008": x008,
        "x000": x000,
        "findings": {
            "x008": classify(x008),
            "x000": classify(x000),
            "shared": shared,
        },
        "recommendation": (
            "The next z=0.005 support recipe should target seed-5 terrain support and base-height "
            "margin while preserving the z=0.002 gait. Do not treat this as an actuator-envelope "
            "or action-saturation problem."
        ),
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_md(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.005 Seed-5 Failure Diagnostic",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline read-only diagnostic. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Comparison",
        "",
        "| command | samples | termination | mean vx | track ratio | base height min | body pitch p95 | double support | single support | max sent vel p95 | max tracking p95 | vel excess |",
        "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ["x008", "x000"]:
        item = payload[label]
        lines.append(
            f"| {fmt(item['command_x'], 3)} | {fmt(item['samples'], 0)} | "
            f"`{item['termination_reason']}` | {fmt(item['mean_local_vx_m_s'])} | "
            f"{fmt(item['track_ratio'])} | {fmt(item['base_height_min_m'])} | "
            f"{fmt(item['body_pitch_p95_rad'])} | {fmt(item['double_support_pct'])} | "
            f"{fmt(item['single_support_pct'])} | {fmt(item['max_sent_vel_p95_rad_s'])} | "
            f"{fmt(item['max_joint_tracking_p95_rad'])} | {fmt(item['max_velocity_excess_rad_s'])} |"
        )

    lines.extend(["", "## Swing / Contact", ""])
    lines.extend(
        [
            "| command | left segments | right segments | left lift | right lift | left rel-x p95 | right rel-x p95 |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label in ["x008", "x000"]:
        item = payload[label]
        lines.append(
            f"| {fmt(item['command_x'], 3)} | {fmt(item['left_swing_segments'], 0)} | "
            f"{fmt(item['right_swing_segments'], 0)} | {fmt(item['left_swing_peak_lift_m'])} | "
            f"{fmt(item['right_swing_peak_lift_m'])} | {fmt(item['left_swing_rel_x_range_p95_m'])} | "
            f"{fmt(item['right_swing_rel_x_range_p95_m'])} |"
        )

    lines.extend(["", "## Findings", ""])
    for label, findings in payload["findings"].items():
        lines.append(f"- `{label}`: {', '.join(findings) if findings else 'none'}")

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            payload["recommendation"],
            "",
            "Do not advance to z=0.005 push, stronger terrain, or robot validation from this candidate.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--x008-worker", default=str(DEFAULT_X008_WORKER))
    parser.add_argument("--x000-worker", default=str(DEFAULT_X000_WORKER))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = collect(args)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_md(payload, output_md)
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
