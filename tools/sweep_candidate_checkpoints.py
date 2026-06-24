#!/usr/bin/env python3
"""Sweep candidate ONNX checkpoints through compact closed-loop gates.

This is an offline selection helper for training artifacts. It does not SSH,
deploy, train, or touch the robot. Its job is to stop treating the final
checkpoint as automatically best when earlier phase checkpoints may preserve
motion that later consolidation erases.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from analyze_command_feasibility_curve import (  # noqa: E402
    command_label,
    fmt,
    gate_status,
    parse_float_list,
    summarize_eval_payload,
)


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def policy_label(path: Path) -> str:
    stem = path.with_suffix("").name
    parent = path.parent.name
    label = f"{parent}_{stem}" if parent else stem
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", label)


def expand_policy_args(values: list[str]) -> list[Path]:
    policies: list[Path] = []
    for value in values:
        path = Path(value)
        if path.is_dir():
            policies.extend(sorted(path.rglob("*.onnx")))
        else:
            policies.append(path)
    deduped: list[Path] = []
    seen = set()
    for path in policies:
        key = str(path)
        if key not in seen:
            seen.add(key)
            deduped.append(path)
    return deduped


def run_eval(args: argparse.Namespace, policy: Path, command_x: float) -> dict[str, Any]:
    label = policy_label(policy)
    output_dir = Path(args.output_dir) / label / command_label(command_x)
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "tools" / "eval_policy_with_actuator_bridge.py"),
        "--mode",
        "closed-loop-sim",
        "--eval-role",
        "candidate",
        "--policy",
        str(policy),
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
    result: dict[str, Any] = {
        "policy": str(policy),
        "policy_label": label,
        "command_x": command_x,
        "output_dir": str(output_dir),
        "command": command,
        "command_shell": shell_join(command),
    }
    if not args.run:
        result["status"] = "DRY_RUN"
        return result
    proc = subprocess.run(
        command,
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


def is_interesting(summary: dict[str, Any], args: argparse.Namespace) -> bool:
    vx = summary.get("mean_local_vx_m_s")
    ratio = summary.get("command_tracking_ratio")
    termination = summary.get("termination_reason")
    velocity = summary.get("max_pitch_sent_target_velocity_p95_rad_s")
    if not isinstance(vx, int | float) or not isinstance(velocity, int | float):
        return False
    if termination != "duration_complete":
        return False
    if vx < args.min_interesting_vx:
        return False
    if isinstance(ratio, int | float) and ratio < args.min_interesting_ratio:
        return False
    low, high = args.velocity_envelope
    return low <= velocity <= high or velocity < low


def build_report(results: list[dict[str, Any]], args: argparse.Namespace) -> str:
    low, high = args.velocity_envelope
    lines = [
        "# Candidate Checkpoint Sweep",
        "",
        "Offline checkpoint selection sweep. This does not SSH, deploy, train,",
        "or touch the robot.",
        "",
        f"commands: `{args.commands}`",
        f"bridge_mode: `{args.bridge_mode}`",
        f"duration_s: `{args.duration}`",
        f"velocity_envelope_rad_s: `{[low, high]}`",
        f"run: `{args.run}`",
        "",
        "## Results",
        "",
        "| policy | command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |",
        "|---|---:|---|---:|---|---:|---|---:|---:|---:|",
    ]
    for result in results:
        summary = result.get("summary") or {}
        envelope = gate_status(summary, low, high)
        lines.append(
            f"| `{result.get('policy_label')}` | {fmt(result.get('command_x'), 3)} | "
            f"`{result.get('status')}` | {fmt(summary.get('samples'), 0)} | "
            f"`{summary.get('termination_reason')}` | "
            f"{fmt(summary.get('max_pitch_sent_target_velocity_p95_rad_s'))} | "
            f"`{envelope}` | {fmt(summary.get('max_pitch_tracking_p95_rad'))} | "
            f"{fmt(summary.get('command_tracking_ratio'))} | "
            f"{fmt(summary.get('mean_local_vx_m_s'))} |"
        )
    lines.extend(["", "## Interesting Checkpoints", ""])
    interesting = [
        result
        for result in results
        if result.get("summary") and is_interesting(result["summary"], args)
    ]
    if not interesting:
        lines.append("- None met the configured interesting-motion criteria.")
    else:
        for result in sorted(
            interesting,
            key=lambda item: float(item["summary"].get("mean_local_vx_m_s") or 0.0),
            reverse=True,
        ):
            summary = result["summary"]
            lines.append(
                "- "
                f"`{result['policy']}` command `{fmt(result['command_x'], 3)}`: "
                f"vx `{fmt(summary.get('mean_local_vx_m_s'))}`, "
                f"ratio `{fmt(summary.get('command_tracking_ratio'))}`, "
                f"vel_p95 `{fmt(summary.get('max_pitch_sent_target_velocity_p95_rad_s'))}`, "
                f"tracking_p95 `{fmt(summary.get('max_pitch_tracking_p95_rad'))}`"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A passing robot candidate still requires the normal x=0.0 and x=0.08",
            "  candidate gates. This sweep is only for checkpoint selection.",
            "- If no checkpoint shows meaningful in-envelope motion, the next",
            "  training change should add a teacher-action or trust-region",
            "  continuity mechanism rather than another small scalar reward tweak.",
        ]
    )
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run or plan an offline candidate checkpoint selection sweep."
    )
    parser.add_argument("--policies", nargs="+", required=True)
    parser.add_argument("--fit-json", default="outputs/analysis/actuator_response_fit.json")
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--env-python", default="../envs/open-duck-playground/bin/python")
    parser.add_argument("--commands", type=parse_float_list, default=parse_float_list("0.08"))
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--bridge-mode", default="fitted")
    parser.add_argument("--mode-name", default="fitted")
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--velocity-envelope", type=parse_float_list, default=parse_float_list("2.25,3.75"))
    parser.add_argument("--min-interesting-vx", type=float, default=0.02)
    parser.add_argument("--min-interesting-ratio", type=float, default=0.25)
    parser.add_argument("--sim-preflight-timeout-s", type=int, default=600)
    parser.add_argument("--closed-loop-timeout-s", type=int, default=1800)
    parser.add_argument("--output-dir", default="outputs/analysis/candidate_checkpoint_sweep")
    parser.add_argument("--output-md", default=None)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if len(args.velocity_envelope) != 2:
        parser.error("--velocity-envelope must contain exactly two comma-separated values")
    policies = expand_policy_args(args.policies)
    if not policies:
        parser.error("--policies did not resolve to any ONNX files")

    results = [
        run_eval(args, policy, command_x)
        for policy in policies
        for command_x in args.commands
    ]
    report = build_report(results, args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_md = Path(args.output_md) if args.output_md else output_dir / "CANDIDATE_CHECKPOINT_SWEEP.md"
    output_json = (
        Path(args.output_json) if args.output_json else output_dir / "candidate_checkpoint_sweep.json"
    )
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(report + "\n")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps({"results": results}, indent=2) + "\n")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
