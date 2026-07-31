#!/usr/bin/env python3
"""Emit the next Phase 2 z=0.005 motion-floor recipe.

This is a read-only planning tool. It records the response to the T4
``phase2-z005-support`` hold: that recipe stayed under the corrected actuator
envelope but under-moved at x=0.08. The next recipe keeps the same corrected
bridge and terrain rung while shifting pressure back toward command progress.
It does not train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z005_MOTION_FLOOR_NEXT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z005_motion_floor_next_recipe.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT
    / "outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu"
    / "smoke_20260628T031553Z_gpu/2026_06_27_232221_491520"
)
DEFAULT_T4_DECISION = ROOT / "outputs/analysis/phase2_z005_t4_recovery_decision.json"
DEFAULT_DEBUG_SWEEP = (
    ROOT
    / "outputs/analysis/phase2_z005_t4_recovered_latest_local_debug_sweep"
    / "candidate_checkpoint_sweep.json"
)


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(part) for part in parts)


def read_json_optional(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_read_error": str(exc), "_path": rel(path)}


def colab_command(session: str, candidate_name: str) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z005-motion-floor",
        "--session",
        session,
        "--candidate-name",
        candidate_name,
        "--candidate-checkpoint-sweep",
        "--candidate-checkpoint-sweep-commands",
        "0.0,0.08",
        "--candidate-checkpoint-sweep-duration",
        "1.0",
        "--candidate-checkpoint-sweep-jax-platform",
        "cpu",
        "--candidate-timeout-s",
        "10800",
        "--run",
    ]


def local_rocm_command(output_root: str) -> list[str]:
    return [
        "../envs/open-duck-playground/bin/python",
        "tools/run_actuator_bridge_training_smoke.py",
        "--playground-path",
        "../Open_Duck_Playground",
        "--env-python",
        "../envs/open-duck-playground/bin/python",
        "--output-root",
        output_root,
        "--run",
        "--platform",
        "gpu",
        "--local-rocm-safe-env",
        "--timeout-s",
        "2700",
        "--task",
        "rough_terrain_backlash",
        "--num-timesteps",
        "122880",
        "--export-min-step",
        "1",
        "--ppo-num-envs",
        "8",
        "--ppo-num-evals",
        "4",
        "--ppo-episode-length",
        "750",
        "--ppo-unroll-length",
        "20",
        "--ppo-batch-size",
        "64",
        "--ppo-num-minibatches",
        "1",
        "--ppo-num-updates-per-batch",
        "2",
        "--restore-checkpoint-path",
        rel(DEFAULT_RESTORE_CHECKPOINT) or str(DEFAULT_RESTORE_CHECKPOINT),
        "--ppo-learning-rate",
        "0.000004",
        "--ppo-entropy-cost",
        "0.001",
        "--ppo-clipping-epsilon",
        "0.025",
        "--ppo-max-grad-norm",
        "0.12",
        "--restore-policy-kl-scale",
        "3",
        "--tracking-lin-vel-scale",
        "3",
        "--tracking-sigma",
        "0.01",
        "--forward-progress-scale",
        "4",
        "--command-progress-scale",
        "3",
        "--command-progress-shortfall-scale",
        "-8",
        "--command-progress-required-ratio",
        "0.5",
        "--command-progress-warmup-steps",
        "30",
        "--forward-wrong-direction-scale",
        "-6",
        "--forward-wrong-direction-allowed-reverse-ratio",
        "0.01",
        "--action-rate-scale",
        "-0.055",
        "--action-magnitude-scale",
        "-0.003",
        "--base-height-scale",
        "-0.35",
        "--forward-pitch-scale",
        "-0.3",
        "--forward-pitch-rate-scale",
        "-0.06",
        "--forward-contact-support-scale",
        "-0.12",
        "--forward-contact-support-no-contact-weight",
        "1.0",
        "--forward-contact-support-asymmetry-weight",
        "0.1",
        "--forward-single-support-scale",
        "0.05",
        "--forward-double-support-scale",
        "-0.05",
        "--forward-double-support-dwell-scale",
        "-0.05",
        "--forward-double-support-dwell-grace-steps",
        "24",
        "--forward-swing-clearance-scale",
        "-0.00025",
        "--forward-swing-clearance-target-m",
        "0.016",
        "--forward-swing-clearance-huber-delta",
        "0.003",
        "--forward-swing-advance-scale",
        "-0.001",
        "--forward-swing-advance-target-m",
        "0.004",
        "--forward-swing-advance-huber-delta",
        "0.002",
        "--alive-scale",
        "2",
        "--imitation-scale",
        "0",
        "--lin-vel-x-min",
        "0.06",
        "--lin-vel-x-max",
        "0.1",
        "--lin-vel-y-min",
        "0",
        "--lin-vel-y-max",
        "0",
        "--ang-vel-yaw-min",
        "0",
        "--ang-vel-yaw-max",
        "0",
        "--command-resample-steps",
        "600",
        "--zero-command-probability",
        "0.15",
        "--dr-friction-min",
        "0.98",
        "--dr-friction-max",
        "1.02",
        "--dr-frictionloss-scale-min",
        "0.995",
        "--dr-frictionloss-scale-max",
        "1.005",
        "--dr-armature-scale-min",
        "1",
        "--dr-armature-scale-max",
        "1.005",
        "--dr-com-jitter-m",
        "0.002",
        "--dr-mass-scale-min",
        "0.995",
        "--dr-mass-scale-max",
        "1.005",
        "--dr-torso-mass-delta-min",
        "-0.005",
        "--dr-torso-mass-delta-max",
        "0.005",
        "--dr-qpos-jitter-rad",
        "0.002",
        "--dr-actuator-gain-scale-min",
        "0.995",
        "--dr-actuator-gain-scale-max",
        "1.005",
        "--dr-leg-geometry-jitter-scale",
        "0.001",
        "--noise-level",
        "0.5",
        "--noise-hip-pos",
        "0.0075",
        "--noise-knee-pos",
        "0.0075",
        "--noise-ankle-pos",
        "0.0075",
        "--noise-joint-vel",
        "0.75",
        "--noise-gravity",
        "0.04",
        "--noise-gyro",
        "0.04",
        "--noise-accelerometer",
        "0.02",
        "--no-push-enable",
        "--actuator-bridge-delay-min-ticks",
        "3",
        "--actuator-bridge-delay-max-ticks",
        "3",
        "--actuator-bridge-tau-min-s",
        "0.06",
        "--actuator-bridge-tau-max-s",
        "0.14",
        "--actuator-bridge-velocity-limit-min-rad-s",
        "2",
        "--actuator-bridge-velocity-limit-max-rad-s",
        "3.25",
        "--actuator-bridge-per-joint-variation",
        "0.1",
        "--actuator-tracking-scale",
        "-0.005",
        "--actuator-tracking-huber-delta",
        "0.03",
        "--terrain-hfield-z-scale",
        "0.005",
    ]


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    t4_decision = read_json_optional(Path(args.t4_decision))
    debug_sweep = read_json_optional(Path(args.debug_sweep))
    colab = colab_command(args.session, args.candidate_name)
    local = local_rocm_command(args.local_output_root)
    return {
        "status": "PASS_Z005_MOTION_FLOOR_RECIPE_READY",
        "stage": "stage_z005_motion_floor",
        "supersedes_recipe": "phase2-z005-support",
        "current_gate_status": "HOLD_PHASE2_STAGE_Z005_SUPPORT",
        "diagnosis_status": "HOLD_Z005_SUPPORT_OVER_REGULARIZED_LOW_PROGRESS",
        "root_cause_summary": [
            "The T4 z=0.005 support run completed training and stayed under the corrected velocity envelope.",
            "The recovered latest checkpoint under-moved at x=0.08 in the local debug sweep: track_ratio_mean 0.1773, vx_mean 0.0142.",
            "The failure was low forward progress, not actuator velocity excess.",
            "The next recipe returns to the A2 restore checkpoint; it does not continue from the under-moving T4 latest checkpoint.",
        ],
        "recipe_intent": [
            "Preserve the corrected-bridge A2 walking behavior while adapting to z=0.005 terrain.",
            "Keep no-push z=0.005 as the active rung; do not advance to push or stronger terrain.",
            "Raise command-progress pressure so support rewards cannot win by freezing.",
            "Reduce support/base-height damping relative to phase2-z005-support to avoid suppressing forward motion.",
            "Keep corrected actuator bridge limits authoritative and reject velocity excess at the gate.",
        ],
        "restore_checkpoint": {
            "path": rel(DEFAULT_RESTORE_CHECKPOINT),
            "present": DEFAULT_RESTORE_CHECKPOINT.exists(),
        },
        "evidence": {
            "t4_decision": rel(Path(args.t4_decision)),
            "debug_sweep": rel(Path(args.debug_sweep)),
            "t4_decision_status": t4_decision.get("status"),
            "debug_sweep_status": debug_sweep.get("overall_status") or debug_sweep.get("status"),
        },
        "key_recipe_changes_vs_z005_support": {
            "num_timesteps": "81920 -> 122880",
            "restore_policy_kl_scale": "4.0 -> 3.0",
            "ppo_learning_rate": "0.000003 -> 0.000004",
            "command_progress_scale": "1.5 -> 3.0",
            "command_progress_shortfall_scale": "-4 -> -8",
            "command_progress_required_ratio": "0.45 -> 0.50",
            "forward_progress_scale": "2.5 -> 4.0",
            "forward_contact_support_scale": "-0.35 -> -0.12",
            "forward_double_support_dwell_scale": "-0.25 -> -0.05",
            "base_height_scale": "-0.8 -> -0.35",
            "action_rate_scale": "-0.08 -> -0.055",
            "actuator_tracking_scale": "-0.01 -> -0.005",
        },
        "acceptance": [
            "z=0.005 x=0.08 no-push passes 8/8, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.",
            "z=0.005 x=0.0 no-push passes 8/8, zero falls, no velocity excess, |mean vx| <= 0.005.",
            "z=0.002 no-push and gentle-push regression gates remain passing.",
        ],
        "falsifier": (
            "If this recipe also stays under envelope but under-moves at x=0.08, "
            "stop adding z=0.005 support penalties and introduce an intermediate "
            "z=0.0035 terrain rung or a terrain-specific command-progress curriculum."
        ),
        "commands": {
            "preferred_colab_gpu": {
                "argv": colab,
                "shell": multiline_shell(colab),
            },
            "local_rocm_fallback": {
                "argv": local,
                "shell": multiline_shell(local),
                "note": "Backend evidence only unless it clears the same canonical gates.",
            },
        },
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.005 Motion-Floor Next Recipe",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        f"supersedes_recipe: `{payload['supersedes_recipe']}`",
        f"diagnosis_status: `{payload['diagnosis_status']}`",
        "",
        "## Root Cause Summary",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["root_cause_summary"])
    lines.extend(["", "## Recipe Intent", ""])
    lines.extend(f"- {item}" for item in payload["recipe_intent"])
    lines.extend(["", "## Key Changes", ""])
    for key, value in payload["key_recipe_changes_vs_z005_support"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Preferred Colab GPU Command", "", "```bash"])
    lines.append(payload["commands"]["preferred_colab_gpu"]["shell"])
    lines.extend(["```", "", "## Local ROCm Fallback", "", "```bash"])
    lines.append(payload["commands"]["local_rocm_fallback"]["shell"])
    lines.extend(["```", "", "## Acceptance", ""])
    lines.extend(f"- {item}" for item in payload["acceptance"])
    lines.extend(
        [
            "",
            "## Falsifier",
            "",
            payload["falsifier"],
            "",
            "No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this recipe.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="open-duck-l4")
    parser.add_argument("--candidate-name", default="phase2_z005_motion_floor_cuda")
    parser.add_argument(
        "--local-output-root",
        default="outputs/phase2_domain_randomization/stage_z005_motion_floor_local_rocm_safeenv_8env_122880",
    )
    parser.add_argument("--t4-decision", default=str(DEFAULT_T4_DECISION))
    parser.add_argument("--debug-sweep", default=str(DEFAULT_DEBUG_SWEEP))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
