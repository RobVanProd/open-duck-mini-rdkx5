#!/usr/bin/env python3
"""Emit the Phase 2 z=0.0035 intermediate motion-floor recipe.

This is a read-only planning tool. It records the response to the z=0.005
motion-floor and motion-prior holds: both stayed under the corrected actuator
envelope but under-moved at x=0.08. The next aligned curriculum step is an
intermediate terrain rung between the passing z=0.002 gates and the failing
z=0.005 gates.

It does not train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z0035_MOTION_FLOOR_NEXT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z0035_motion_floor_next_recipe.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT
    / "outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu"
    / "smoke_20260628T031553Z_gpu/2026_06_27_232221_491520"
)
DEFAULT_Z005_MOTION_FLOOR_DECISION = (
    ROOT / "outputs/analysis/phase2_z005_motion_floor_t4_partial_decision.json"
)
DEFAULT_Z005_MOTION_PRIOR_DECISION = (
    ROOT / "outputs/analysis/phase2_z005_motion_prior_t4_partial_decision.json"
)


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json_optional(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_read_error": str(exc), "_path": rel(path)}


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(part) for part in parts)


def colab_command(session: str, candidate_name: str) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z0035-motion-floor",
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


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    z005_motion = read_json_optional(Path(args.z005_motion_floor_decision))
    z005_prior = read_json_optional(Path(args.z005_motion_prior_decision))
    return {
        "status": "PASS_Z0035_MOTION_FLOOR_RECIPE_READY",
        "stage": "stage_z0035_motion_floor",
        "supersedes_recipe": "phase2-z005-motion-floor",
        "diagnosis_status": "HOLD_Z005_MOTION_FLOOR_UNDER_MOVING",
        "root_cause_summary": [
            "The packaged candidate passes z=0.002 corrected-bridge terrain and gentle-push gates.",
            "The z=0.005 support, motion-floor, and behavior-prior motion-floor attempts stayed under the corrected velocity envelope but under-moved at x=0.08.",
            "The motion-prior T4 compact sweep best completed x=0.08 track ratio was 0.1703, below the compact promotion floor 0.25.",
            "The next curriculum step should test an intermediate terrain height rather than adding more regularization at z=0.005.",
        ],
        "recipe_intent": [
            "Warm-start from the same corrected-bridge A2 checkpoint; do not train from scratch.",
            "Use z=0.0035 rough terrain as an intermediate rung between passing z=0.002 and failing z=0.005.",
            "Keep the motion-floor command-progress pressure that preserves forward intent.",
            "Keep the corrected actuator envelope authoritative and reject velocity excess at the gate.",
            "Do not use the behavior prior in this rung because the z=0.005 behavior-prior run did not improve forward progress.",
        ],
        "restore_checkpoint": {
            "path": rel(DEFAULT_RESTORE_CHECKPOINT),
            "present": DEFAULT_RESTORE_CHECKPOINT.exists(),
        },
        "evidence": {
            "z005_motion_floor_decision": rel(Path(args.z005_motion_floor_decision)),
            "z005_motion_floor_status": z005_motion.get("status"),
            "z005_motion_prior_decision": rel(Path(args.z005_motion_prior_decision)),
            "z005_motion_prior_status": z005_prior.get("status"),
            "z005_motion_prior_best_completed_x008_track_ratio": (
                (z005_prior.get("promotion") or {}).get("best_completed_x008_track_ratio")
            ),
        },
        "key_recipe_settings": {
            "workflow": "phase2-z0035-motion-floor",
            "terrain_hfield_z_scale": 0.0035,
            "num_timesteps": 122880,
            "restore_policy_kl_scale": 3.0,
            "ppo_learning_rate": 0.000004,
            "command_progress_scale": 3.0,
            "command_progress_shortfall_scale": -8.0,
            "command_progress_required_ratio": 0.5,
            "forward_progress_scale": 4.0,
            "base_height_scale": -0.35,
            "actuator_tracking_scale": -0.005,
            "push_enable": False,
            "actuator_bridge_velocity_limit_range_rad_s": [2.0, 3.25],
        },
        "acceptance": [
            "z=0.0035 x=0.08 no-push passes 8/8, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.",
            "z=0.0035 x=0.0 no-push passes 8/8, zero falls, no velocity excess, |mean vx| <= 0.005.",
            "z=0.002 no-push and gentle-push regression gates remain passing.",
            "Passing z=0.0035 is not a robot-validation clearance; it only authorizes returning to z=0.005 with a smaller gap.",
        ],
        "falsifier": (
            "If z=0.0035 also under-moves while staying under envelope, stop terrain "
            "height escalation and re-check the z=0.002 moving policy under the same "
            "post-training gate path before another training run."
        ),
        "commands": {
            "preferred_colab_gpu": {
                "argv": colab_command(args.session, args.candidate_name),
                "shell": multiline_shell(colab_command(args.session, args.candidate_name)),
            }
        },
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.0035 Motion-Floor Next Recipe",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        f"supersedes_recipe: `{payload['supersedes_recipe']}`",
        f"diagnosis_status: `{payload['diagnosis_status']}`",
        "",
        "This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Root Cause Summary",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["root_cause_summary"])
    lines.extend(["", "## Recipe Intent", ""])
    lines.extend(f"- {item}" for item in payload["recipe_intent"])
    lines.extend(["", "## Key Settings", ""])
    for key, value in payload["key_recipe_settings"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Preferred Colab GPU Command", "", "```bash"])
    lines.append(payload["commands"]["preferred_colab_gpu"]["shell"])
    lines.extend(["```", "", "## Acceptance", ""])
    lines.extend(f"- {item}" for item in payload["acceptance"])
    lines.extend(["", "## Falsifier", "", payload["falsifier"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="open-duck-l4")
    parser.add_argument("--candidate-name", default="phase2_z0035_motion_floor_cuda")
    parser.add_argument(
        "--z005-motion-floor-decision",
        default=str(DEFAULT_Z005_MOTION_FLOOR_DECISION),
    )
    parser.add_argument(
        "--z005-motion-prior-decision",
        default=str(DEFAULT_Z005_MOTION_PRIOR_DECISION),
    )
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
