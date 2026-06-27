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


def expand_policy_args(values: list[str]) -> list[tuple[str, Path]]:
    policies: list[tuple[str | None, Path]] = []
    for value in values:
        label: str | None = None
        path_text = value
        if "=" in value:
            label_text, candidate_path = value.split("=", 1)
            if label_text.strip() and candidate_path.strip():
                label = label_text.strip()
                path_text = candidate_path.strip()
        path = Path(path_text)
        if path.is_dir():
            for item in sorted(path.rglob("*.onnx")):
                item_label = f"{label}_{policy_label(item)}" if label else policy_label(item)
                policies.append((item_label, item))
        else:
            policies.append((label, path))
    deduped: list[tuple[str, Path]] = []
    seen = set()
    for label, path in policies:
        key = str(path)
        if key not in seen:
            seen.add(key)
            deduped.append((label or policy_label(path), path))
    return deduped


def run_eval(
    args: argparse.Namespace, policy_item: tuple[str, Path], command_x: float
) -> dict[str, Any]:
    label, policy = policy_item
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


def grouped_by_policy(results: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        grouped.setdefault(str(result.get("policy_label")), []).append(result)
    return grouped


def is_candidate_pass(status: Any) -> bool:
    return status in {
        "PASS_CANDIDATE_SIM_GATE",
        "PASS_CLOSED_LOOP_REPRODUCTION",
    }


def command_kind(command_x: float) -> str:
    return "zero" if abs(command_x) < 1e-9 else "positive"


def promotion_decision_for_policy(
    rows: list[dict[str, Any]], args: argparse.Namespace
) -> dict[str, Any]:
    if not args.run:
        return {
            "policy": rows[0].get("policy") if rows else None,
            "policy_label": rows[0].get("policy_label") if rows else None,
            "status": "DRY_RUN_PROMOTION_UNEVALUATED",
            "promote": False,
            "pass_count": 0,
            "required_command_count": len(args.commands),
            "duration_complete_count": 0,
            "failure_reasons": [],
            "warnings": ["dry run did not execute candidate gates"],
            "max_pitch_tracking_p95_rad": None,
            "max_pitch_sent_target_velocity_p95_rad_s": None,
            "max_action_saturation_pct": None,
            "positive_command_tracking_ratio_mean": None,
        }
    by_command = {float(row["command_x"]): row for row in rows}
    missing = [
        command_x
        for command_x in args.commands
        if float(command_x) not in by_command
    ]
    failures: list[str] = []
    warnings: list[str] = []
    pass_count = 0
    duration_complete_count = 0
    positive_motion_scores: list[float] = []
    max_tracking_values: list[float] = []
    max_velocity_values: list[float] = []
    max_saturation_values: list[float] = []

    for command_x in args.commands:
        row = by_command.get(float(command_x))
        if row is None:
            continue
        status = row.get("status")
        summary = row.get("summary") or {}
        if is_candidate_pass(status):
            pass_count += 1
        else:
            failures.append(f"command {command_x:g}: {status}")
        if summary.get("termination_reason") == "duration_complete":
            duration_complete_count += 1
        else:
            failures.append(
                f"command {command_x:g}: termination {summary.get('termination_reason')}"
            )

        tracking = summary.get("max_pitch_tracking_p95_rad")
        velocity = summary.get("max_pitch_sent_target_velocity_p95_rad_s")
        saturation = summary.get("max_action_saturation_pct")
        if isinstance(tracking, int | float):
            max_tracking_values.append(float(tracking))
        if isinstance(velocity, int | float):
            max_velocity_values.append(float(velocity))
        if isinstance(saturation, int | float):
            max_saturation_values.append(float(saturation))

        if command_kind(float(command_x)) == "positive":
            ratio = summary.get("command_tracking_ratio")
            vx = summary.get("mean_local_vx_m_s")
            if not isinstance(ratio, int | float):
                failures.append(f"command {command_x:g}: missing tracking ratio")
            elif float(ratio) < args.min_promote_ratio:
                failures.append(
                    f"command {command_x:g}: track ratio {float(ratio):.4f} "
                    f"< {args.min_promote_ratio:.4f}"
                )
            if not isinstance(vx, int | float):
                failures.append(f"command {command_x:g}: missing mean vx")
            elif float(vx) < args.min_promote_vx:
                failures.append(
                    f"command {command_x:g}: mean vx {float(vx):.4f} "
                    f"< {args.min_promote_vx:.4f}"
                )
            if isinstance(ratio, int | float):
                positive_motion_scores.append(float(ratio))
        else:
            ratio = summary.get("command_tracking_ratio")
            if isinstance(ratio, int | float) and abs(float(ratio)) > 0.05:
                warnings.append(
                    f"zero command reports nonzero track ratio {float(ratio):.4f}"
                )

    if missing:
        failures.extend(f"missing command {command_x:g}" for command_x in missing)

    promote = not failures
    if promote:
        status = "PASS_PROMOTE_CANDIDATE_CHECKPOINT"
    elif pass_count:
        status = "HOLD_PARTIAL_CANDIDATE_CHECKPOINT"
    else:
        status = "HOLD_REJECT_CANDIDATE_CHECKPOINT"

    return {
        "policy": rows[0].get("policy") if rows else None,
        "policy_label": rows[0].get("policy_label") if rows else None,
        "status": status,
        "promote": promote,
        "pass_count": pass_count,
        "required_command_count": len(args.commands),
        "duration_complete_count": duration_complete_count,
        "failure_reasons": failures,
        "warnings": warnings,
        "max_pitch_tracking_p95_rad": max(max_tracking_values, default=None),
        "max_pitch_sent_target_velocity_p95_rad_s": max(max_velocity_values, default=None),
        "max_action_saturation_pct": max(max_saturation_values, default=None),
        "positive_command_tracking_ratio_mean": (
            sum(positive_motion_scores) / len(positive_motion_scores)
            if positive_motion_scores
            else None
        ),
    }


def promotion_decisions(
    results: list[dict[str, Any]], args: argparse.Namespace
) -> list[dict[str, Any]]:
    decisions = [
        promotion_decision_for_policy(rows, args)
        for rows in grouped_by_policy(results).values()
    ]
    return sorted(
        decisions,
        key=lambda item: (
            int(bool(item.get("promote"))),
            int(item.get("pass_count") or 0),
            float(item.get("positive_command_tracking_ratio_mean") or -999.0),
            -float(item.get("max_pitch_tracking_p95_rad") or 999.0),
        ),
        reverse=True,
    )


def build_report(results: list[dict[str, Any]], args: argparse.Namespace) -> str:
    low, high = args.velocity_envelope
    decisions = promotion_decisions(results, args)
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
        f"min_promote_vx_m_s: `{args.min_promote_vx}`",
        f"min_promote_ratio: `{args.min_promote_ratio}`",
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
            "## Promotion Decisions",
            "",
            "| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for decision in decisions:
        lines.append(
            f"| `{decision.get('policy_label')}` | `{decision.get('status')}` | "
            f"{decision.get('pass_count')}/{decision.get('required_command_count')} | "
            f"{decision.get('duration_complete_count')}/{decision.get('required_command_count')} | "
            f"{fmt(decision.get('max_pitch_sent_target_velocity_p95_rad_s'))} | "
            f"{fmt(decision.get('max_pitch_tracking_p95_rad'))} | "
            f"{fmt(decision.get('max_action_saturation_pct'))} | "
            f"{fmt(decision.get('positive_command_tracking_ratio_mean'))} |"
        )
    holds = [decision for decision in decisions if not decision.get("promote")]
    if holds:
        lines.extend(["", "### Hold Reasons", ""])
        for decision in holds:
            reasons = decision.get("failure_reasons") or []
            if not reasons:
                reasons = decision.get("warnings") or ["no explicit reason recorded"]
            lines.append(f"- `{decision.get('policy_label')}`: " + "; ".join(reasons[:6]))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A passing robot candidate still requires the normal x=0.0 and x=0.08",
            "  candidate gates. This sweep is only for checkpoint selection.",
            "- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands",
            "  passed their candidate gates in this compact sweep. It is still not",
            "  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.",
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
    parser.add_argument("--min-promote-vx", type=float, default=0.02)
    parser.add_argument("--min-promote-ratio", type=float, default=0.25)
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
        run_eval(args, policy_item, command_x)
        for policy_item in policies
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
    output_json.write_text(
        json.dumps(
            {
                "results": results,
                "promotion_decisions": promotion_decisions(results, args),
            },
            indent=2,
        )
        + "\n"
    )
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
