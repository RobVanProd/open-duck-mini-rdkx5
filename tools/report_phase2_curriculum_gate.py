#!/usr/bin/env python3
"""Report Phase 2 curriculum gate advancement.

This is a read-only ledger. It does not train, SSH, deploy, touch the robot, or
modify Playground. It turns the current corrected-bridge seed-sweep artifacts
into an explicit stage-advancement decision so Phase 2 cannot silently advance
past a held or missing gate.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_CURRICULUM_GATE_LEDGER.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_curriculum_gate_ledger.json"


DEFAULT_GATES = {
    "z002_x008_nopush": {
        "path": ROOT
        / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_nopush_15s_8seed_cpu.json",
        "command_x": 0.08,
        "terrain_z": 0.002,
        "push": False,
    },
    "z002_x000_nopush": {
        "path": ROOT
        / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_nopush_15s_8seed_cpu.json",
        "command_x": 0.0,
        "terrain_z": 0.002,
        "push": False,
    },
    "z002_x008_gentle_push": {
        "path": ROOT
        / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_gentle_push_15s_8seed_cpu.json",
        "command_x": 0.08,
        "terrain_z": 0.002,
        "push": True,
    },
    "z002_x000_gentle_push": {
        "path": ROOT
        / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_gentle_push_15s_8seed_cpu.json",
        "command_x": 0.0,
        "terrain_z": 0.002,
        "push": True,
    },
    "z005_x008_nopush": {
        "path": ROOT
        / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z005_nopush_15s_8seed_cpu.json",
        "command_x": 0.08,
        "terrain_z": 0.005,
        "push": False,
    },
    "z005_x000_nopush": {
        "path": ROOT
        / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z005_nopush_15s_8seed_cpu.json",
        "command_x": 0.0,
        "terrain_z": 0.005,
        "push": False,
    },
    "z005_x008_gentle_push": {
        "path": ROOT
        / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z005_gentle_push_15s_8seed_cpu.json",
        "command_x": 0.08,
        "terrain_z": 0.005,
        "push": True,
    },
    "z005_x000_gentle_push": {
        "path": ROOT
        / "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z005_gentle_push_15s_8seed_cpu.json",
        "command_x": 0.0,
        "terrain_z": 0.005,
        "push": True,
    },
}


STAGES = [
    {
        "id": "stage_a2_z002_regression",
        "required_gates": [
            "z002_x008_nopush",
            "z002_x000_nopush",
            "z002_x008_gentle_push",
            "z002_x000_gentle_push",
        ],
        "advance_if_pass": "stage_z005_support",
    },
    {
        "id": "stage_z005_support",
        "required_gates": [
            "z005_x008_nopush",
            "z005_x000_nopush",
            "z002_x008_nopush",
            "z002_x000_nopush",
            "z002_x008_gentle_push",
            "z002_x000_gentle_push",
        ],
        "advance_if_pass": "stage_z005_gentle_push",
    },
    {
        "id": "stage_z005_gentle_push",
        "required_gates": [
            "z005_x008_nopush",
            "z005_x000_nopush",
            "z005_x008_gentle_push",
            "z005_x000_gentle_push",
            "z002_x008_nopush",
            "z002_x000_nopush",
            "z002_x008_gentle_push",
            "z002_x000_gentle_push",
        ],
        "advance_if_pass": "stage_z005_stronger_push_or_terrain",
    },
]


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def stat_value(stats: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if not isinstance(stats, dict):
        return default
    return stats.get(key, default)


def first_aggregate(payload: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    aggregate = payload.get("aggregate")
    if not isinstance(aggregate, dict) or not aggregate:
        return None, None
    name = next(iter(aggregate))
    item = aggregate.get(name)
    return name, item if isinstance(item, dict) else None


def evaluate_gate(name: str, spec: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    path = Path(spec["path"])
    result: dict[str, Any] = {
        "name": name,
        "path": rel(path),
        "exists": path.exists(),
        "expected_command_x": spec["command_x"],
        "expected_terrain_z": spec["terrain_z"],
        "expected_push": spec["push"],
    }
    if not path.exists():
        result["status"] = "MISSING_GATE_ARTIFACT"
        result["reasons"] = ["artifact missing"]
        return result

    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        result["status"] = "INVALID_GATE_JSON"
        result["reasons"] = [str(exc)]
        return result

    config = payload.get("config") if isinstance(payload.get("config"), dict) else {}
    policy_label, aggregate = first_aggregate(payload)
    result["policy_label"] = policy_label
    result["config"] = {
        "command_x": config.get("command_x"),
        "terrain_hfield_z_scale": config.get("terrain_hfield_z_scale"),
        "eval_push_enable": config.get("eval_push_enable"),
        "seeds": config.get("seeds"),
        "duration_s": config.get("duration_s"),
        "task": config.get("task"),
        "bridge_mode": config.get("bridge_mode"),
    }
    if aggregate is None:
        result["status"] = "INVALID_GATE_AGGREGATE"
        result["reasons"] = ["aggregate missing"]
        return result

    metrics = {
        "runs": aggregate.get("runs"),
        "fall_count": aggregate.get("fall_count"),
        "duration_complete_count": aggregate.get("duration_complete_count"),
        "track_ratio_mean": stat_value(aggregate.get("track_ratio"), "mean"),
        "mean_local_vx_mean": stat_value(aggregate.get("mean_local_vx_m_s"), "mean"),
        "max_tracking_p95_max": stat_value(aggregate.get("max_tracking_p95_rad"), "max"),
        "max_pitch_vel_p95_max": stat_value(aggregate.get("max_pitch_vel_p95_rad_s"), "max"),
        "max_vel_excess_max": stat_value(aggregate.get("max_pitch_vel_limit_excess_rad_s"), "max"),
        "push_success_mean": stat_value(aggregate.get("push_success_rate"), "mean"),
        "base_height_min_min": stat_value(aggregate.get("base_height_min_m"), "min"),
    }
    result["metrics"] = metrics

    reasons: list[str] = []
    expected_seeds = args.seeds
    if metrics["runs"] != expected_seeds:
        reasons.append(f"runs {metrics['runs']} != {expected_seeds}")
    if metrics["fall_count"] != 0:
        reasons.append(f"fall_count {metrics['fall_count']} != 0")
    if metrics["duration_complete_count"] != expected_seeds:
        reasons.append(f"duration_complete_count {metrics['duration_complete_count']} != {expected_seeds}")
    if (metrics["max_vel_excess_max"] or 0.0) > args.max_velocity_excess:
        reasons.append(f"velocity_excess {metrics['max_vel_excess_max']} > {args.max_velocity_excess}")
    if (metrics["max_tracking_p95_max"] or 0.0) > args.max_tracking_p95:
        reasons.append(f"tracking_p95 {metrics['max_tracking_p95_max']} > {args.max_tracking_p95}")

    command_x = float(spec["command_x"])
    if command_x > 0:
        if metrics["track_ratio_mean"] is None or metrics["track_ratio_mean"] < args.min_track_ratio:
            reasons.append(f"track_ratio_mean {metrics['track_ratio_mean']} < {args.min_track_ratio}")
    else:
        vx = abs(metrics["mean_local_vx_mean"] or 0.0)
        if vx > args.max_abs_vx_x0:
            reasons.append(f"abs mean vx {vx} > {args.max_abs_vx_x0}")

    if spec["push"]:
        push_success = metrics["push_success_mean"]
        if push_success is None or push_success < args.min_push_success:
            reasons.append(f"push_success_mean {push_success} < {args.min_push_success}")

    result["reasons"] = reasons
    result["status"] = "PASS_GATE" if not reasons else "HOLD_GATE"
    return result


def stage_status(stage: dict[str, Any], gates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    statuses = {name: gates.get(name, {}).get("status") for name in stage["required_gates"]}
    missing = [name for name, status in statuses.items() if status in {None, "MISSING_GATE_ARTIFACT"}]
    holds = [name for name, status in statuses.items() if status not in {"PASS_GATE", None, "MISSING_GATE_ARTIFACT"}]
    if holds:
        status = "HOLD_STAGE"
    elif missing:
        status = "MISSING_STAGE_GATES"
    else:
        status = "PASS_STAGE"
    return {
        "id": stage["id"],
        "status": status,
        "required_gates": stage["required_gates"],
        "gate_statuses": statuses,
        "missing_gates": missing,
        "held_gates": holds,
        "advance_if_pass": stage["advance_if_pass"],
    }


def gate_specs_from_args(args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    specs = copy.deepcopy(DEFAULT_GATES)
    for item in args.gate_json or []:
        if "=" not in item:
            raise SystemExit(f"--gate-json must be NAME=PATH, got {item!r}")
        name, raw_path = item.split("=", 1)
        if name not in specs:
            known = ", ".join(sorted(specs))
            raise SystemExit(f"unknown gate {name!r}; known gates: {known}")
        specs[name]["path"] = Path(raw_path)
    return specs


def collect(args: argparse.Namespace) -> dict[str, Any]:
    gate_specs = gate_specs_from_args(args)
    gates = {name: evaluate_gate(name, spec, args) for name, spec in gate_specs.items()}
    stages = [stage_status(stage, gates) for stage in STAGES]

    first_hold = next((stage for stage in stages if stage["status"] != "PASS_STAGE"), None)
    if first_hold is None:
        status = "PASS_PHASE2_CURRICULUM_GATES_READY_TO_ADVANCE"
        current_stage = STAGES[-1]["advance_if_pass"]
    elif first_hold["status"] == "HOLD_STAGE":
        status = f"HOLD_PHASE2_{first_hold['id'].upper()}"
        current_stage = first_hold["id"]
    else:
        status = f"MISSING_PHASE2_{first_hold['id'].upper()}_EVIDENCE"
        current_stage = first_hold["id"]

    return {
        "status": status,
        "generated_at": timestamp(),
        "candidate": {
            "path": args.candidate,
            "sha256": args.candidate_sha256,
        },
        "thresholds": {
            "seeds": args.seeds,
            "max_tracking_p95": args.max_tracking_p95,
            "max_velocity_excess": args.max_velocity_excess,
            "min_track_ratio": args.min_track_ratio,
            "max_abs_vx_x0": args.max_abs_vx_x0,
            "min_push_success": args.min_push_success,
        },
        "current_stage": current_stage,
        "gates": gates,
        "stages": stages,
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
        "# Phase 2 Curriculum Gate Ledger",
        "",
        f"status: `{payload['status']}`",
        f"generated_at: `{payload['generated_at']}`",
        "",
        "This is a read-only stage-advancement ledger. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Candidate",
        "",
        f"- candidate: `{payload['candidate']['path']}`",
        f"- candidate_sha256: `{payload['candidate']['sha256']}`",
        "",
        "## Stage Status",
        "",
        "| stage | status | held gates | missing gates | advance if pass |",
        "|---|---|---|---|---|",
    ]
    for stage in payload["stages"]:
        lines.append(
            f"| `{stage['id']}` | `{stage['status']}` | "
            f"`{', '.join(stage['held_gates']) or 'none'}` | "
            f"`{', '.join(stage['missing_gates']) or 'none'}` | "
            f"`{stage['advance_if_pass']}` |"
        )

    lines.extend(
        [
            "",
            "## Gate Matrix",
            "",
            "| gate | status | runs | falls | complete | x | z | push | track ratio mean | vx mean | max tracking p95 | max vel excess | push success | reasons |",
            "|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for name, gate in payload["gates"].items():
        metrics = gate.get("metrics", {})
        lines.append(
            f"| `{name}` | `{gate['status']}` | "
            f"{fmt(metrics.get('runs'), 0)} | "
            f"{fmt(metrics.get('fall_count'), 0)} | "
            f"{fmt(metrics.get('duration_complete_count'), 0)} | "
            f"{fmt(gate.get('expected_command_x'), 3)} | "
            f"{fmt(gate.get('expected_terrain_z'), 3)} | "
            f"`{gate.get('expected_push')}` | "
            f"{fmt(metrics.get('track_ratio_mean'))} | "
            f"{fmt(metrics.get('mean_local_vx_mean'))} | "
            f"{fmt(metrics.get('max_tracking_p95_max'))} | "
            f"{fmt(metrics.get('max_vel_excess_max'))} | "
            f"{fmt(metrics.get('push_success_mean'))} | "
            f"{'; '.join(gate.get('reasons', [])) or 'none'} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- current_stage: `{payload['current_stage']}`",
        ]
    )
    if payload["status"].startswith("HOLD_PHASE2_STAGE_Z005_SUPPORT"):
        lines.extend(
            [
                "- decision: continue z=0.005 support training from the corrected-bridge candidate.",
                "- do not advance to z=0.005 push or stronger terrain until z=0.005 no-push gates pass.",
            ]
        )
    elif payload["status"].startswith("MISSING_PHASE2"):
        lines.append("- decision: run or recover the missing gate artifacts before advancing.")
    else:
        lines.append("- decision: required gates are clear for the next curriculum rung.")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate",
        default="policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx",
    )
    parser.add_argument(
        "--candidate-sha256",
        default="209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b",
    )
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--max-tracking-p95", type=float, default=0.20)
    parser.add_argument("--max-velocity-excess", type=float, default=0.0)
    parser.add_argument("--min-track-ratio", type=float, default=0.40)
    parser.add_argument("--max-abs-vx-x0", type=float, default=0.005)
    parser.add_argument("--min-push-success", type=float, default=0.90)
    parser.add_argument(
        "--gate-json",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Override a gate artifact path without changing the historical defaults.",
    )
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
