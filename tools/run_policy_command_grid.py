#!/usr/bin/env python3
"""Run a small offline command grid for the published policy.

This helper searches for command cells where the current closed-loop policy both
moves forward and stays inside the measured pitch-chain target-velocity
envelope. It does not train, SSH, deploy, or touch robot hardware.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = "policy/BEST_WALK_ONNX_2.onnx"
DEFAULT_FIT_JSON = "outputs/analysis/actuator_response_fit.json"
DEFAULT_COMMANDS = (
    "straight_x005:0.05:0.0:0.0,"
    "straight_x006:0.06:0.0:0.0,"
    "straight_x007:0.07:0.0:0.0,"
    "turn_scale050:0.037:-0.0185:-0.037,"
    "turn_scale065:0.0481:-0.0241:-0.0481,"
    "turn_scale080:0.0592:-0.0296:-0.0592,"
    "turn_scale090:0.0666:-0.0333:-0.0666,"
    "turn_scale100:0.074:-0.037:-0.074"
)
PITCH_CHAIN_JOINTS = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if finite(value):
        return f"{float(value):.{digits}f}"
    return str(value)


def parse_float_list(value: str) -> list[float]:
    values = [float(part.strip()) for part in value.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected at least one numeric value")
    return values


def parse_int_list(value: str) -> list[int]:
    values = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer value")
    return values


def parse_commands(value: str) -> list[dict[str, Any]]:
    commands = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(":")
        if len(parts) != 4:
            raise argparse.ArgumentTypeError(
                "commands must be label:x:y:yaw entries separated by commas"
            )
        label, x, y, yaw = parts
        commands.append(
            {
                "label": label.strip(),
                "x": float(x),
                "y": float(y),
                "yaw": float(yaw),
            }
        )
    if not commands:
        raise argparse.ArgumentTypeError("expected at least one command cell")
    labels = [command["label"] for command in commands]
    if len(set(labels)) != len(labels):
        raise argparse.ArgumentTypeError("command labels must be unique")
    return commands


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def stat_value(stats: dict[str, Any] | None, key: str) -> float | None:
    if not isinstance(stats, dict):
        return None
    value = stats.get(key)
    return float(value) if finite(value) else None


def summarize_eval_payload(payload: dict[str, Any]) -> dict[str, Any]:
    closed_loop = payload.get("closed_loop_sim") or {}
    mode = (closed_loop.get("modes") or {}).get("vanilla") or {}
    joints = mode.get("joints") or {}
    pitch_velocities = []
    pitch_tracking = []
    saturation = []
    for joint in PITCH_CHAIN_JOINTS:
        item = joints.get(joint) or {}
        velocity = stat_value(item.get("sent_target_velocity_rad_s"), "p95")
        tracking = stat_value(item.get("joint_target_tracking_error_rad"), "p95")
        sat = item.get("action_saturation_pct")
        if velocity is not None:
            pitch_velocities.append((joint, velocity))
        if tracking is not None:
            pitch_tracking.append((joint, tracking))
        if finite(sat):
            saturation.append((joint, float(sat)))
    forward = mode.get("forward_motion") or {}
    body_pitch = mode.get("body_pitch_rad") or {}
    base_height = mode.get("base_height_m") or {}
    return {
        "overall_status": payload.get("overall_status"),
        "closed_loop_status": closed_loop.get("status"),
        "samples": mode.get("samples"),
        "termination_reason": mode.get("termination_reason"),
        "mean_local_vx_m_s": forward.get("mean_velocity_x_m_s"),
        "command_tracking_ratio": forward.get("command_tracking_ratio"),
        "progress_x_m": forward.get("progress_x_m"),
        "max_pitch_sent_target_velocity_p95_rad_s": max(
            (value for _, value in pitch_velocities), default=None
        ),
        "max_pitch_sent_target_velocity_joint": max(
            pitch_velocities, key=lambda item: item[1], default=(None, None)
        )[0],
        "mean_pitch_sent_target_velocity_p95_rad_s": (
            sum(value for _, value in pitch_velocities) / len(pitch_velocities)
            if pitch_velocities
            else None
        ),
        "max_pitch_tracking_p95_rad": max(
            (value for _, value in pitch_tracking), default=None
        ),
        "max_pitch_tracking_joint": max(
            pitch_tracking, key=lambda item: item[1], default=(None, None)
        )[0],
        "max_action_saturation_pct": max(
            (value for _, value in saturation), default=None
        ),
        "body_pitch_p95_rad": body_pitch.get("p95"),
        "base_height_min_m": base_height.get("min"),
        "foot_contact_counts": mode.get("foot_contact_counts"),
    }


def run_eval(args: argparse.Namespace, command: dict[str, Any], seed: int) -> dict[str, Any]:
    label = str(command["label"])
    output_dir = Path(args.output_dir) / f"{label}_seed{seed}"
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / "trace.jsonl"
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "eval_policy_with_actuator_bridge.py"),
        "--mode",
        "closed-loop-sim",
        "--eval-role",
        "candidate",
        "--policy",
        str(Path(args.policy)),
        "--fit-json",
        str(Path(args.fit_json)),
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--command-x",
        str(command["x"]),
        "--command-y",
        str(command["y"]),
        "--command-yaw",
        str(command["yaw"]),
        "--task",
        str(args.task),
        "--duration",
        str(args.duration),
        "--seed",
        str(seed),
        "--bridge-mode",
        "vanilla",
        "--jax-platform",
        str(args.jax_platform),
        "--sim-preflight-timeout-s",
        str(args.sim_preflight_timeout_s),
        "--closed-loop-timeout-s",
        str(args.closed_loop_timeout_s),
        "--trace-jsonl",
        str(trace_path),
        "--output-dir",
        str(output_dir),
    ]
    if args.trace_full_obs:
        cmd.append("--trace-full-obs")
    result: dict[str, Any] = {
        "label": label,
        "seed": seed,
        "command": {"x": command["x"], "y": command["y"], "yaw": command["yaw"]},
        "output_dir": str(output_dir),
        "trace_jsonl": str(trace_path),
        "command_shell": shell_join(cmd),
    }
    if not args.run:
        result["status"] = "DRY_RUN"
        return result
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=args.closed_loop_timeout_s + 120,
        check=False,
    )
    result["returncode"] = proc.returncode
    result["stdout_tail"] = (proc.stdout or "")[-12000:]
    json_path = output_dir / "closed_loop_actuator_bridge_eval.json"
    result["result_json"] = str(json_path)
    if not json_path.exists():
        result["status"] = "HOLD_NO_RESULT_JSON"
        return result
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result["status"] = "HOLD_BAD_RESULT_JSON"
        result["error"] = str(exc)
        return result
    result["status"] = payload.get("overall_status")
    result["summary"] = summarize_eval_payload(payload)
    return result


def mean(values: list[float]) -> float | None:
    xs = [float(value) for value in values if finite(value)]
    if not xs:
        return None
    return sum(xs) / len(xs)


def aggregate_results(results: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    low, high = args.velocity_envelope
    groups: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        groups.setdefault(str(result["label"]), []).append(result)
    aggregates = {}
    for label, items in sorted(groups.items()):
        summaries = [item.get("summary") for item in items if isinstance(item.get("summary"), dict)]
        moving = [
            summary
            for summary in summaries
            if finite(summary.get("command_tracking_ratio"))
            and float(summary["command_tracking_ratio"]) >= args.moving_ratio
            and finite(summary.get("mean_local_vx_m_s"))
            and float(summary["mean_local_vx_m_s"]) > 0.0
        ]
        max_joint_values = [
            float(summary["max_pitch_sent_target_velocity_p95_rad_s"])
            for summary in summaries
            if finite(summary.get("max_pitch_sent_target_velocity_p95_rad_s"))
        ]
        max_joint_mean = mean(max_joint_values)
        max_joint_max = max(max_joint_values) if max_joint_values else None
        mean_vx = mean(
            [
                float(summary["mean_local_vx_m_s"])
                for summary in summaries
                if finite(summary.get("mean_local_vx_m_s"))
            ]
        )
        track_ratio = mean(
            [
                float(summary["command_tracking_ratio"])
                for summary in summaries
                if finite(summary.get("command_tracking_ratio"))
            ]
        )
        duration_complete = sum(
            1
            for summary in summaries
            if summary.get("termination_reason") == "duration_complete"
        )
        inside_by_max = finite(max_joint_max) and float(max_joint_max) <= high
        inside_by_mean = finite(max_joint_mean) and float(max_joint_mean) <= high
        moving_fraction = len(moving) / len(items) if items else 0.0
        complete_fraction = duration_complete / len(items) if items else 0.0
        if not summaries:
            gate = "HOLD_NO_SUMMARY"
        elif moving_fraction >= args.min_moving_fraction and inside_by_max:
            gate = "PASS_MOVES_INSIDE_ENVELOPE_MAX_JOINT"
        elif moving_fraction >= args.min_moving_fraction and inside_by_mean:
            gate = "WARN_MOVES_INSIDE_MEAN_BUT_MAX_OVER_ENVELOPE"
        elif moving_fraction >= args.min_moving_fraction:
            gate = "WARN_MOVES_OVER_ENVELOPE"
        elif inside_by_max:
            gate = "HOLD_INSIDE_ENVELOPE_NO_FORWARD_MOTION"
        else:
            gate = "HOLD_NO_FORWARD_MOTION_OR_OVER_ENVELOPE"
        command = items[0].get("command") if items else None
        aggregates[label] = {
            "command": command,
            "seed_count": len(items),
            "summary_count": len(summaries),
            "duration_complete_count": duration_complete,
            "moving_seed_count": len(moving),
            "moving_fraction": moving_fraction,
            "complete_fraction": complete_fraction,
            "mean_local_vx_m_s": mean_vx,
            "command_tracking_ratio": track_ratio,
            "max_pitch_target_velocity_p95_mean_rad_s": max_joint_mean,
            "max_pitch_target_velocity_p95_max_seed_rad_s": max_joint_max,
            "envelope_low_rad_s": low,
            "envelope_high_rad_s": high,
            "gate": gate,
        }
    if any(
        item["gate"] == "PASS_MOVES_INSIDE_ENVELOPE_MAX_JOINT"
        for item in aggregates.values()
    ):
        status = "PASS_FOUND_ENVELOPE_SAFE_COMMAND"
    elif any(
        item["gate"] == "WARN_MOVES_INSIDE_MEAN_BUT_MAX_OVER_ENVELOPE"
        for item in aggregates.values()
    ):
        status = "WARN_MEAN_SAFE_BUT_MAX_OVER_ENVELOPE"
    elif any(item["gate"] == "WARN_MOVES_OVER_ENVELOPE" for item in aggregates.values()):
        status = "HOLD_MOVEMENT_REQUIRES_OVER_ENVELOPE"
    else:
        status = "HOLD_NO_MOVING_COMMAND_FOUND"
    return {
        "status": status,
        "velocity_envelope_rad_s": {"low": low, "high": high},
        "moving_ratio_threshold": args.moving_ratio,
        "min_moving_fraction": args.min_moving_fraction,
        "aggregates": aggregates,
    }


def build_markdown(payload: dict[str, Any], args: argparse.Namespace) -> str:
    lines = [
        "# Published Policy Command Grid",
        "",
        f"overall_status: `{payload['status']}`",
        "",
        "## Scope",
        "",
        "- Offline closed-loop sim eval only.",
        "- Same published `BEST_WALK_ONNX_2` policy.",
        "- Vanilla sim path; no fitted actuator bridge, no training, no robot access.",
        "- Gate searches for forward tracking while each seed stays under the measured per-joint pitch-chain velocity envelope.",
        "",
        "## Command Cells",
        "",
        "| command_cell | x | y | yaw | seeds | complete | moving | mean_vx | track_ratio | max_pitch_vel_p95_mean | max_pitch_vel_p95_max_seed | gate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for label, item in payload["aggregates"].items():
        command = item.get("command") or {}
        lines.append(
            f"| {label} | {fmt(command.get('x'), 4)} | {fmt(command.get('y'), 4)} | "
            f"{fmt(command.get('yaw'), 4)} | {item['seed_count']} | "
            f"{item['duration_complete_count']} | {item['moving_seed_count']} | "
            f"{fmt(item['mean_local_vx_m_s'])} | {fmt(item['command_tracking_ratio'])} | "
            f"{fmt(item['max_pitch_target_velocity_p95_mean_rad_s'])} | "
            f"{fmt(item['max_pitch_target_velocity_p95_max_seed_rad_s'])} | "
            f"`{item['gate']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if payload["status"] == "PASS_FOUND_ENVELOPE_SAFE_COMMAND":
        lines.append(
            "At least one command cell moved forward across the requested seed fraction while keeping every evaluated seed under the measured per-joint velocity envelope. Validate that cell with more seeds before using it as a training target."
        )
    elif payload["status"] == "WARN_MEAN_SAFE_BUT_MAX_OVER_ENVELOPE":
        lines.append(
            "At least one command cell moved and looked safe on mean target velocity, but one or more seeds exceeded the measured per-joint envelope. Treat it as a candidate for finer sweep, not as a clean existence proof."
        )
    elif payload["status"] == "HOLD_MOVEMENT_REQUIRES_OVER_ENVELOPE":
        lines.append(
            "In this grid, forward movement only appeared in cells whose per-seed pitch-chain target velocity exceeded the measured envelope. This supports treating published-policy movement as over-envelope for these commands."
        )
    else:
        lines.append(
            "No command cell in this grid produced reliable forward movement. Expand or revise the grid only after reviewing whether the command region is meaningful."
        )
    lines.extend(
        [
            "",
            "Robot validation remains blocked.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--fit-json", default=DEFAULT_FIT_JSON)
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--env-python", default="../envs/open-duck-playground/bin/python")
    parser.add_argument("--task", default="flat_terrain_backlash")
    parser.add_argument("--commands", type=parse_commands, default=parse_commands(DEFAULT_COMMANDS))
    parser.add_argument("--seeds", type=parse_int_list, default=parse_int_list("0,1,2"))
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--velocity-envelope", type=parse_float_list, default=parse_float_list("2.25,3.75"))
    parser.add_argument("--moving-ratio", type=float, default=0.5)
    parser.add_argument("--min-moving-fraction", type=float, default=2.0 / 3.0)
    parser.add_argument("--sim-preflight-timeout-s", type=int, default=600)
    parser.add_argument("--closed-loop-timeout-s", type=int, default=1800)
    parser.add_argument("--trace-full-obs", action="store_true")
    parser.add_argument("--output-dir", default="outputs/analysis/published_policy_command_grid")
    parser.add_argument("--output-md", default="outputs/analysis/PUBLISHED_POLICY_COMMAND_GRID.md")
    parser.add_argument("--output-json", default="outputs/analysis/published_policy_command_grid.json")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if len(args.velocity_envelope) != 2:
        parser.error("--velocity-envelope must contain two comma-separated values")
    return args


def main() -> int:
    args = parse_args()
    results = []
    for command in args.commands:
        for seed in args.seeds:
            result = run_eval(args, command, seed)
            print(
                f"{command['label']} seed={seed} status={result.get('status')}",
                flush=True,
            )
            results.append(result)
    summary = aggregate_results(results, args)
    payload = {
        "results": results,
        **summary,
        "run": bool(args.run),
        "duration_s": args.duration,
        "task": args.task,
        "playground_path": args.playground_path,
        "jax_platform": args.jax_platform,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(build_markdown(payload, args) + "\n", encoding="utf-8")
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    print(f"overall_status: {payload['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
