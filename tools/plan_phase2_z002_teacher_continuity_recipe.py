#!/usr/bin/env python3
"""Emit the Phase 2 z=0.002 teacher-continuity recovery recipe.

This is a read-only planning tool. It records the response to the A100
z=0.002 tracking-margin hold: scalar reward shaping preserved the moving gait
but did not recover the strict corrected-bridge tracking threshold. The next
aligned step is to keep the moving z=0.002 parent and add a teacher-action /
trust-region continuity signal rather than running another scalar tweak.

It does not train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_NEXT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT
    / "outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu"
    / "smoke_20260628T103743Z_gpu/2026_06_28_064431_245760"
)
DEFAULT_BEHAVIOR_PRIOR_MLP = (
    ROOT
    / "outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate"
    / "candidate_mlp.npz"
)
DEFAULT_A100_RESULT = ROOT / "outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_A100_RESULT.md"


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(part) for part in parts)


def read_text_optional(path: Path) -> dict[str, Any]:
    try:
        return {
            "path": rel(path),
            "present": True,
            "sha256": sha256_path(path),
            "excerpt": path.read_text(errors="replace")[:5000],
        }
    except Exception as exc:
        return {"path": rel(path), "present": False, "read_error": str(exc)}


def colab_command(session: str, candidate_name: str) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z002-teacher-continuity",
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


def post_training_decision_command(post_training_json: str) -> list[str]:
    return [
        "python3",
        "tools/report_phase2_z002_tracking_margin_post_training_gates.py",
        post_training_json,
        "--output-md",
        "outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_POST_TRAINING_GATE_DECISION.md",
        "--output-json",
        "outputs/analysis/phase2_z002_teacher_continuity_post_training_gate_decision.json",
    ]


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    colab = colab_command(args.session, args.candidate_name)
    post_training_json = "<candidate_name>_post_training_seed_gates.json"
    decision = post_training_decision_command(post_training_json)
    return {
        "status": "PASS_Z002_TEACHER_CONTINUITY_RECIPE_READY",
        "stage": "stage_z002_teacher_continuity",
        "supersedes_recipe": "phase2-z002-tracking-margin",
        "diagnosis_status": "HOLD_Z002_SCALAR_TRACKING_MARGIN_NOT_PROMOTED",
        "root_cause_summary": [
            "The A100 scalar tracking-margin run completed training but no checkpoint passed the compact x=0.08 tracking threshold.",
            "The best compact checkpoint retained motion at x=0.08: track ratio 0.2939, mean vx 0.0235 m/s, max tracking p95 0.2184 rad.",
            "All compact checkpoints stayed below the corrected velocity envelope, so the hold is tracking margin rather than actuator over-speed.",
            "The prior recipe's falsifier fired: do not run another scalar reward tweak that may buy tracking by reducing motion.",
        ],
        "recipe_intent": [
            "Warm-start from the same z=0.002 C0 245760 moving parent, not from scratch.",
            "Keep terrain at z=0.002 and no pushes; this is parent recovery before terrain escalation.",
            "Use a teacher-action behavior-prior MLP plus stronger restore-policy KL as a trust region around the moving gait.",
            "Relax the scalar target-rate penalty relative to tracking-margin so the policy does not recover tracking by freezing.",
            "Reject any checkpoint that passes smoke but fails the canonical compact x=0/x=0.08 corrected-bridge sweep.",
        ],
        "restore_checkpoint": {
            "path": rel(DEFAULT_RESTORE_CHECKPOINT),
            "present": DEFAULT_RESTORE_CHECKPOINT.exists(),
            "directory_sha256_tar_stream": args.restore_checkpoint_sha256,
        },
        "behavior_prior_mlp": {
            "path": rel(DEFAULT_BEHAVIOR_PRIOR_MLP),
            "present": DEFAULT_BEHAVIOR_PRIOR_MLP.exists(),
            "sha256": sha256_path(DEFAULT_BEHAVIOR_PRIOR_MLP),
        },
        "evidence": {
            "a100_tracking_margin_result": read_text_optional(Path(args.a100_result)),
        },
        "key_recipe_settings": {
            "workflow": "phase2-z002-teacher-continuity",
            "terrain_hfield_z_scale": 0.002,
            "num_timesteps": 122880,
            "restore_policy_kl_scale": 7.5,
            "behavior_prior_scale": -0.18,
            "behavior_prior_huber_delta": 0.08,
            "ppo_learning_rate": 0.000002,
            "ppo_clipping_epsilon": 0.015,
            "ppo_max_grad_norm": 0.08,
            "target_rate_scale": -0.01,
            "actuator_tracking_scale": -0.005,
            "command_progress_scale": 3.5,
            "command_progress_shortfall_scale": -10.0,
            "command_progress_required_ratio": 0.55,
            "forward_progress_scale": 4.5,
            "action_rate_scale": -0.035,
            "push_enable": False,
            "actuator_bridge_velocity_limit_range_rad_s": [2.0, 3.25],
        },
        "acceptance": [
            "Compact x=0.08 fitted-bridge sweep passes with track ratio >= 0.25 and tracking p95 <= 0.20.",
            "Compact x=0.0 fitted-bridge sweep remains passing.",
            "Full z=0.002 x=0.08 and x=0.0 post-training seed gates pass before use as a terrain parent.",
            "No robot validation is authorized by this recipe.",
        ],
        "falsifier": (
            "If teacher continuity still holds above 0.20 rad tracking p95 while preserving motion, "
            "stop z=0.002 PPO reward/continuity tweaks and inspect the evaluator/teacher-action target "
            "manifold before spending another A100 run."
        ),
        "commands": {
            "preferred_colab_gpu": {
                "argv": colab,
                "shell": multiline_shell(colab),
            },
            "post_training_decision": {
                "argv": decision,
                "shell": multiline_shell(decision),
            },
        },
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.002 Teacher-Continuity Next Recipe",
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
    lines.extend(["", "## Required Inputs", ""])
    lines.extend(
        [
            f"- restore_checkpoint: `{payload['restore_checkpoint']['path']}` present=`{payload['restore_checkpoint']['present']}`",
            f"- behavior_prior_mlp: `{payload['behavior_prior_mlp']['path']}` present=`{payload['behavior_prior_mlp']['present']}` sha256=`{payload['behavior_prior_mlp']['sha256']}`",
        ]
    )
    lines.extend(["", "## Key Settings", ""])
    for key, value in payload["key_recipe_settings"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Preferred Colab GPU Command", "", "```bash"])
    lines.append(payload["commands"]["preferred_colab_gpu"]["shell"])
    lines.extend(["```", "", "## Acceptance", ""])
    lines.extend(f"- {item}" for item in payload["acceptance"])
    lines.extend(["", "## Post-Training Decision Command", "", "```bash"])
    lines.append(payload["commands"]["post_training_decision"]["shell"])
    lines.extend(["```"])
    lines.extend(["", "## Falsifier", "", payload["falsifier"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="open-duck-l4")
    parser.add_argument("--candidate-name", default="phase2_z002_teacher_continuity_cuda")
    parser.add_argument("--a100-result", default=str(DEFAULT_A100_RESULT))
    parser.add_argument(
        "--restore-checkpoint-sha256",
        default="638a6c46b402622c41d91a334c192274d174439761bd6a189de21b5442012991",
        help="sha256 of `tar -cf - <restore_checkpoint>`, recorded for traceability.",
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
