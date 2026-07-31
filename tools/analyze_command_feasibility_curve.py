#!/usr/bin/env python3
"""Sweep command_x and summarize target-velocity feasibility.

This is an offline sim/eval helper. It can either print the planned commands or
run `tools/eval_policy_with_actuator_bridge.py` for each command value. It does
not SSH, deploy, train, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMMANDS = "0.0,0.02,0.04,0.06,0.08,0.10,0.12"
PITCH_CHAIN_JOINTS = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def parse_float_list(value: str) -> list[float]:
    values = [float(part.strip()) for part in value.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected at least one numeric value")
    return values


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, int | float):
        return f"{float(value):.{digits}f}"
    return str(value)


def command_label(command_x: float) -> str:
    text = f"{command_x:+.3f}".replace("+", "p").replace("-", "m").replace(".", "p")
    return f"cmd_{text}"


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def eval_command(args: argparse.Namespace, command_x: float) -> dict[str, Any]:
    output_dir = Path(args.output_dir) / command_label(command_x)
    output_dir.mkdir(parents=True, exist_ok=True)
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
        str(command_x),
        "--duration",
        str(args.duration),
        "--bridge-mode",
        args.bridge_mode,
        "--jax-platform",
        args.jax_platform,
        "--sim-preflight-timeout-s",
        str(args.sim_preflight_timeout_s),
        "--closed-loop-timeout-s",
        str(args.closed_loop_timeout_s),
        "--output-dir",
        str(output_dir),
    ]
    result = {
        "command_x": command_x,
        "output_dir": str(output_dir),
        "command": cmd,
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
        payload = json.loads(json_path.read_text())
    except json.JSONDecodeError as exc:
        result["status"] = "HOLD_BAD_RESULT_JSON"
        result["error"] = str(exc)
        return result
    result["status"] = payload.get("overall_status")
    result["summary"] = summarize_eval_payload(payload, args.mode_name)
    return result


def first_present(mapping: dict[str, Any], names: list[str]) -> tuple[str | None, Any]:
    for name in names:
        if name in mapping:
            return name, mapping[name]
    return None, None


def stat_value(stats: dict[str, Any] | None, key: str) -> float | None:
    if not isinstance(stats, dict):
        return None
    value = stats.get(key)
    return float(value) if isinstance(value, int | float) else None


def summarize_eval_payload(payload: dict[str, Any], preferred_mode: str) -> dict[str, Any]:
    closed_loop = payload.get("closed_loop_sim") or {}
    modes = closed_loop.get("modes") or {}
    mode_name, mode = first_present(
        modes,
        [
            preferred_mode,
            "fitted",
            "fitted_bridge",
            "vanilla",
            "vanilla_no_bridge",
            "stress",
            "stress_bridge",
        ],
    )
    summary: dict[str, Any] = {
        "overall_status": payload.get("overall_status"),
        "closed_loop_status": closed_loop.get("status"),
        "mode": mode_name,
    }
    if not isinstance(mode, dict):
        return summary
    joints = mode.get("joints") or {}
    pitch_velocities = []
    pitch_tracking = []
    pitch_saturation = []
    for joint in PITCH_CHAIN_JOINTS:
        item = joints.get(joint) or {}
        vel = stat_value(item.get("sent_target_velocity_rad_s"), "p95")
        tracking = stat_value(item.get("joint_target_tracking_error_rad"), "p95")
        saturation = item.get("action_saturation_pct")
        if vel is not None:
            pitch_velocities.append((joint, vel))
        if tracking is not None:
            pitch_tracking.append((joint, tracking))
        if isinstance(saturation, int | float):
            pitch_saturation.append((joint, float(saturation)))
    forward = mode.get("forward_motion") or {}
    summary.update(
        {
            "samples": mode.get("samples"),
            "termination_reason": mode.get("termination_reason"),
            "max_pitch_sent_target_velocity_p95_rad_s": max(
                (value for _, value in pitch_velocities), default=None
            ),
            "max_pitch_sent_target_velocity_joint": max(
                pitch_velocities, key=lambda item: item[1], default=(None, None)
            )[0],
            "max_pitch_tracking_p95_rad": max(
                (value for _, value in pitch_tracking), default=None
            ),
            "max_pitch_tracking_joint": max(
                pitch_tracking, key=lambda item: item[1], default=(None, None)
            )[0],
            "max_action_saturation_pct": max(
                (value for _, value in pitch_saturation), default=None
            ),
            "mean_local_vx_m_s": forward.get("mean_velocity_x_m_s"),
            "command_tracking_ratio": forward.get("command_tracking_ratio"),
            "progress_x_m": forward.get("progress_x_m"),
        }
    )
    return summary


def gate_status(summary: dict[str, Any], low: float, high: float) -> str:
    velocity = summary.get("max_pitch_sent_target_velocity_p95_rad_s")
    if velocity is None:
        return "UNKNOWN"
    if velocity < low:
        return "BELOW_MEASURED_ENVELOPE"
    if velocity <= high:
        return "INSIDE_MEASURED_ENVELOPE"
    return "ABOVE_MEASURED_ENVELOPE"


def build_report(results: list[dict[str, Any]], args: argparse.Namespace) -> str:
    low, high = args.velocity_envelope
    lines = [
        "# Command Feasibility Curve",
        "",
        "Offline closed-loop command sweep. This does not SSH, deploy, train, or",
        "touch the robot.",
        "",
        f"policy: `{args.policy}`",
        f"fit_json: `{args.fit_json}`",
        f"bridge_mode: `{args.bridge_mode}`",
        f"duration_s: `{args.duration}`",
        f"velocity_envelope_rad_s: `{[low, high]}`",
        f"run: `{args.run}`",
        "",
        "## Summary",
        "",
        "| command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx | output |",
        "|---:|---|---:|---|---:|---|---:|---:|---:|---|",
    ]
    for result in results:
        summary = result.get("summary") or {}
        envelope = gate_status(summary, low, high)
        lines.append(
            f"| {fmt(result['command_x'], 3)} | `{result.get('status')}` | "
            f"{fmt(summary.get('samples'), 0)} | `{summary.get('termination_reason')}` | "
            f"{fmt(summary.get('max_pitch_sent_target_velocity_p95_rad_s'))} | "
            f"`{envelope}` | {fmt(summary.get('max_pitch_tracking_p95_rad'))} | "
            f"{fmt(summary.get('command_tracking_ratio'))} | "
            f"{fmt(summary.get('mean_local_vx_m_s'))} | `{result.get('output_dir')}` |"
        )
    lines.extend(["", "## Interpretation", ""])
    completed = [item for item in results if item.get("summary")]
    crossings = [
        item
        for item in completed
        if gate_status(item["summary"], low, high) == "ABOVE_MEASURED_ENVELOPE"
    ]
    if crossings:
        first = min(crossings, key=lambda item: item["command_x"])
        lines.append(
            "- First command with pitch-chain p95 target velocity above the "
            f"measured envelope: `{first['command_x']}`."
        )
    else:
        lines.append("- No command in this sweep exceeded the measured velocity envelope.")
    lines.append(
        "- Treat this as a feasibility curve, not a deployability result. Robot "
        "validation remains blocked until candidate x=0.0 and x=0.08 sim gates pass."
    )
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run or plan an offline command_x feasibility curve sweep."
    )
    parser.add_argument("--policy", required=True)
    parser.add_argument("--fit-json", default="outputs/analysis/actuator_response_fit_corrected_knee.json")
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--env-python", default="../envs/open-duck-playground/bin/python")
    parser.add_argument("--commands", type=parse_float_list, default=parse_float_list(DEFAULT_COMMANDS))
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--bridge-mode", default="fitted")
    parser.add_argument("--mode-name", default="fitted")
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--velocity-envelope", type=parse_float_list, default=parse_float_list("2.0,3.25"))
    parser.add_argument("--sim-preflight-timeout-s", type=int, default=600)
    parser.add_argument("--closed-loop-timeout-s", type=int, default=1800)
    parser.add_argument("--output-dir", default="outputs/analysis/command_feasibility_curve")
    parser.add_argument("--output-md", default=None)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if len(args.velocity_envelope) != 2:
        parser.error("--velocity-envelope must contain exactly two comma-separated values")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = [eval_command(args, command_x) for command_x in args.commands]
    report = build_report(results, args)
    output_md = Path(args.output_md) if args.output_md else output_dir / "COMMAND_FEASIBILITY_CURVE.md"
    output_json = Path(args.output_json) if args.output_json else output_dir / "command_feasibility_curve.json"
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(report + "\n")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps({"results": results}, indent=2) + "\n")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
