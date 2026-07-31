#!/usr/bin/env python3
"""Emit the Phase 2 z=0.0025 terrain-boundary recipe.

This is a read-only planning tool. It records the response to the measured
terrain cliff: the gain099 corrected-bridge candidate passes z=0.0024 across
the full no-push/gentle-push matrix, while seed 5 fails at z=0.0025 by
backward support collapse without corrected-envelope excess.

It does not train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOUNDARY_DECISION = (
    ROOT / "outputs/analysis/phase2_stagea2_gain099_terrain_z0024_boundary_decision.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z0025_BOUNDARY_NEXT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z0025_boundary_next_recipe.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT
    / "outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu"
    / "smoke_20260628T031553Z_gpu/2026_06_27_232221_491520"
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
        "phase2-z0025-boundary",
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
    boundary = read_json_optional(Path(args.boundary_decision))
    gates = boundary.get("gate_matrix") or {}
    return {
        "status": "PASS_Z0025_BOUNDARY_RECIPE_READY",
        "stage": "stage_z0025_boundary",
        "supersedes_recipe": "phase2-z0035-motion-floor",
        "diagnosis_status": "PASS_Z0024_AND_HOLD_Z0025_SEED5_SUPPORT_COLLAPSE",
        "root_cause_summary": [
            "The gain099 corrected-bridge candidate passes the full z=0.0024 rough-terrain matrix.",
            "Seed 5 passes z=0.0024 but fails at z=0.0025 by backward support collapse.",
            "The z=0.0025 failure has zero corrected-envelope velocity excess, so actuator rate is not the immediate blocker.",
            "Prior z=0.0035/z=0.005 support and motion-floor variants jumped past the measured cliff and held by low progress or collapse.",
        ],
        "recipe_intent": [
            "Warm-start from the trainable A2 checkpoint that produced the gain099 candidate; do not train from scratch.",
            "Train directly at z=0.0025, the first failing terrain height above the confirmed z=0.0024 rung.",
            "Use motion-preserving progress pressure and light support/stance penalties, not the stronger z=0.005 support recipe.",
            "Keep the corrected actuator envelope authoritative and reject any post-training velocity excess.",
            "Preserve z=0.0024 no-push/gentle-push regressions and x=0.0 command semantics.",
        ],
        "restore_checkpoint": {
            "path": rel(DEFAULT_RESTORE_CHECKPOINT),
            "present": DEFAULT_RESTORE_CHECKPOINT.exists(),
        },
        "evidence": {
            "boundary_decision": rel(Path(args.boundary_decision)),
            "boundary_status": boundary.get("decision_status"),
            "z0024_x008_gentle_push": gates.get("x008_gentle_push"),
            "z0024_x0_gentle_push": gates.get("x0_gentle_push"),
        },
        "key_recipe_settings": {
            "workflow": "phase2-z0025-boundary",
            "terrain_hfield_z_scale": 0.0025,
            "num_timesteps": 122880,
            "restore_policy_kl_scale": 3.0,
            "ppo_learning_rate": 0.000004,
            "ppo_num_envs": 64,
            "command_progress_scale": 3.0,
            "command_progress_shortfall_scale": -8.0,
            "command_progress_required_ratio": 0.5,
            "forward_progress_scale": 4.0,
            "base_height_scale": -0.35,
            "actuator_tracking_scale": -0.005,
            "push_enable": False,
            "actuator_bridge_velocity_limit_range_rad_s": [2.0, 3.25],
            "narrow_dr": {
                "friction": [0.98, 1.02],
                "mass_scale": [0.995, 1.005],
                "com_jitter_m": 0.002,
                "leg_geometry_jitter_scale": 0.001,
            },
        },
        "acceptance": [
            "z=0.0025 x=0.08 no-push passes 8/8, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.",
            "z=0.0025 x=0.0 no-push passes 8/8, zero falls, no velocity excess, |mean vx| <= 0.005.",
            "z=0.0024 x=0.08 and x=0.0 no-push/gentle-push regression gates remain passing.",
            "Passing z=0.0025 is not robot-validation clearance; it only authorizes the next terrain increment.",
        ],
        "falsifier": (
            "If z=0.0025 still fails seed 5 by backward support collapse while z=0.0024 "
            "regressions remain clean, stop terrain escalation and train a targeted "
            "seed-5 support-recovery curriculum at z=0.0024->0.0025 before adding wider DR."
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
        "# Phase 2 z=0.0025 Boundary Next Recipe",
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
    parser.add_argument("--session", default="open-duck-a100-phase2d")
    parser.add_argument("--candidate-name", default="phase2_z0025_boundary_cuda")
    parser.add_argument("--boundary-decision", default=str(DEFAULT_BOUNDARY_DECISION))
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
