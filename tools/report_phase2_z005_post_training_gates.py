#!/usr/bin/env python3
"""Grade Phase 2 terrain post-training seed gates.

This tool consumes the `*_post_training_seed_gates.json` artifact produced by
`run_colab_cli_cuda_workflow.py --workflow phase2-z005-support` or an
intermediate terrain-rung workflow and turns it into an explicit promotion
decision. It is read-only: it does not train, SSH, deploy, touch the robot, or
modify Playground.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z005_POST_TRAINING_GATE_DECISION.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z005_post_training_gate_decision.json"


REQUIRED_GATES = [
    "z005_x008_no_push",
    "z005_x000_no_push",
    "z002_x008_no_push_regression",
    "z002_x000_no_push_regression",
    "z002_x008_gentle_push_regression",
    "z002_x000_gentle_push_regression",
]

REGRESSION_GATES = [
    "z002_x008_no_push_regression",
    "z002_x000_no_push_regression",
    "z002_x008_gentle_push_regression",
    "z002_x000_gentle_push_regression",
]


def required_gates_from_manifest(manifest: dict[str, Any]) -> list[str]:
    results = manifest.get("results") if isinstance(manifest.get("results"), list) else []
    names = [str(item.get("name")) for item in results if item.get("name")]
    primary = [
        name
        for name in names
        if name.endswith("_no_push")
        and name not in REGRESSION_GATES
        and not name.startswith("z002_")
    ]
    if primary:
        return primary + [name for name in REGRESSION_GATES if name in names]
    return REQUIRED_GATES


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def stat_value(stats: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if not isinstance(stats, dict):
        return default
    return stats.get(key, default)


def gate_reason(item: dict[str, Any], args: argparse.Namespace) -> list[str]:
    aggregate = item.get("aggregate") if isinstance(item.get("aggregate"), dict) else {}
    reasons: list[str] = []
    runs = aggregate.get("runs")
    falls = aggregate.get("fall_count")
    complete = aggregate.get("duration_complete_count")
    tracking_max = stat_value(aggregate.get("max_tracking_p95_rad"), "max")
    velocity_excess_max = stat_value(aggregate.get("max_pitch_vel_limit_excess_rad_s"), "max")
    track_ratio_mean = stat_value(aggregate.get("track_ratio"), "mean")
    vx_mean = stat_value(aggregate.get("mean_local_vx_m_s"), "mean")
    push_success_mean = stat_value(aggregate.get("push_success_rate"), "mean")

    if item.get("returncode") not in {0, None}:
        reasons.append(f"returncode {item.get('returncode')} != 0")
    if runs != args.seeds:
        reasons.append(f"runs {runs} != {args.seeds}")
    if falls != 0:
        reasons.append(f"fall_count {falls} != 0")
    if complete != args.seeds:
        reasons.append(f"duration_complete_count {complete} != {args.seeds}")
    if tracking_max is None or tracking_max > args.max_tracking_p95:
        reasons.append(f"tracking_p95_max {tracking_max} > {args.max_tracking_p95}")
    if velocity_excess_max is None or velocity_excess_max > args.max_velocity_excess:
        reasons.append(f"velocity_excess_max {velocity_excess_max} > {args.max_velocity_excess}")

    command_x = float(item.get("command_x") or 0.0)
    if command_x > 0.0:
        if track_ratio_mean is None or track_ratio_mean < args.min_track_ratio:
            reasons.append(f"track_ratio_mean {track_ratio_mean} < {args.min_track_ratio}")
    else:
        if vx_mean is None or abs(vx_mean) > args.max_abs_vx_x0:
            reasons.append(f"abs vx_mean {abs(vx_mean) if vx_mean is not None else None} > {args.max_abs_vx_x0}")

    if item.get("push"):
        if push_success_mean is None or push_success_mean < args.min_push_success:
            reasons.append(f"push_success_mean {push_success_mean} < {args.min_push_success}")

    return reasons


def summarize_gate(item: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    aggregate = item.get("aggregate") if isinstance(item.get("aggregate"), dict) else {}
    reasons = gate_reason(item, args)
    return {
        "name": item.get("name"),
        "command_x": item.get("command_x"),
        "terrain_z": item.get("terrain_z"),
        "push": bool(item.get("push")),
        "returncode": item.get("returncode"),
        "gate_dir": item.get("gate_dir"),
        "result_json": item.get("result_json"),
        "status": "PASS_GATE" if not reasons else "HOLD_GATE",
        "reasons": reasons,
        "metrics": {
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
        },
    }


def collect(args: argparse.Namespace) -> dict[str, Any]:
    input_path = Path(args.input_json)
    manifest = read_json(input_path)
    results = manifest.get("results") if isinstance(manifest.get("results"), list) else []
    required_gates = required_gates_from_manifest(manifest)
    gates_by_name = {str(item.get("name")): summarize_gate(item, args) for item in results}
    missing = [name for name in required_gates if name not in gates_by_name]
    held = [
        name
        for name in required_gates
        if gates_by_name.get(name, {}).get("status") not in {"PASS_GATE", None}
    ]
    if missing:
        status = "MISSING_PHASE2_POST_TRAINING_GATES"
    elif held:
        status = "HOLD_PHASE2_POST_TRAINING_GATES"
    else:
        status = "PASS_PHASE2_POST_TRAINING_GATES"
    return {
        "status": status,
        "input_json": rel(input_path),
        "workflow": manifest.get("workflow"),
        "policy": manifest.get("policy"),
        "candidate_name": manifest.get("candidate_name"),
        "thresholds": {
            "seeds": args.seeds,
            "max_tracking_p95": args.max_tracking_p95,
            "max_velocity_excess": args.max_velocity_excess,
            "min_track_ratio": args.min_track_ratio,
            "max_abs_vx_x0": args.max_abs_vx_x0,
            "min_push_success": args.min_push_success,
        },
        "required_gates": required_gates,
        "missing_gates": missing,
        "held_gates": held,
        "gates": gates_by_name,
        "promotion_allowed": status == "PASS_PHASE2_POST_TRAINING_GATES",
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


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Post-Training Gate Decision",
        "",
        f"status: `{payload['status']}`",
        f"promotion_allowed: `{payload['promotion_allowed']}`",
        "",
        "This is a read-only decision artifact. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Candidate",
        "",
        f"- candidate_name: `{payload.get('candidate_name')}`",
        f"- policy: `{payload.get('policy')}`",
        f"- input_json: `{payload.get('input_json')}`",
        "",
        "## Thresholds",
        "",
    ]
    for key, value in payload["thresholds"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Gate Matrix",
            "",
            "| gate | status | x | z | push | runs | falls | complete | track ratio mean | vx mean | tracking p95 max | vel excess max | push success | reasons |",
            "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for name in payload["required_gates"]:
        gate = payload["gates"].get(name)
        if not gate:
            lines.append(f"| `{name}` | `MISSING_GATE` | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | missing |")
            continue
        metrics = gate["metrics"]
        reasons = "; ".join(gate["reasons"]) if gate["reasons"] else "none"
        lines.append(
            f"| `{name}` | `{gate['status']}` | {fmt(gate['command_x'], 3)} | "
            f"{fmt(gate['terrain_z'], 3)} | `{gate['push']}` | {fmt(metrics['runs'], 0)} | "
            f"{fmt(metrics['fall_count'], 0)} | {fmt(metrics['duration_complete_count'], 0)} | "
            f"{fmt(metrics['track_ratio_mean'])} | {fmt(metrics['mean_local_vx_mean'])} | "
            f"{fmt(metrics['max_tracking_p95_max'])} | {fmt(metrics['max_vel_excess_max'])} | "
            f"{fmt(metrics['push_success_mean'])} | {reasons} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
        ]
    )
    if payload["promotion_allowed"]:
        lines.append("The candidate clears the strict z=0.005 support gate and z=0.002 regression gates in offline sim.")
    else:
        lines.append("Do not promote this candidate. Resolve held or missing gates before advancing Phase 2.")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", help="Path to *_post_training_seed_gates.json")
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--max-tracking-p95", type=float, default=0.20)
    parser.add_argument("--max-velocity-excess", type=float, default=0.0)
    parser.add_argument("--min-track-ratio", type=float, default=0.40)
    parser.add_argument("--max-abs-vx-x0", type=float, default=0.005)
    parser.add_argument("--min-push-success", type=float, default=0.95)
    args = parser.parse_args()
    payload = collect(args)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, output_md)
    print(payload["status"])
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
