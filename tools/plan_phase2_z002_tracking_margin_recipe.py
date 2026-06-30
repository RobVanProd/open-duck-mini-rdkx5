#!/usr/bin/env python3
"""Emit the Phase 2 z=0.002 tracking-margin recovery recipe.

This is a read-only planning tool. It records the response to the z=0.0035
motion-floor hold: the intermediate terrain rung stayed under the corrected
actuator envelope but lost useful x=0.08 forward progress. The next aligned
step is to return to the z=0.002 moving parent and recover strict tracking
margin before escalating terrain height again.

It does not train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_NEXT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z002_tracking_margin_next_recipe.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT
    / "outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu"
    / "smoke_20260628T103743Z_gpu/2026_06_28_064431_245760"
)
DEFAULT_COMPARISON_DECISION = ROOT / "docs/PHASE2_Z002_VS_Z0035_COMPACT_SWEEP_DECISION.md"
DEFAULT_Z0035_RESULT = ROOT / "docs/PHASE2_Z0035_MOTION_FLOOR_RESULT.md"


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(part) for part in parts)


def read_text_optional(path: Path) -> dict[str, Any]:
    try:
        return {
            "path": rel(path),
            "present": True,
            "sha256_not_recorded": True,
            "excerpt": path.read_text(errors="replace")[:4000],
        }
    except Exception as exc:
        return {"path": rel(path), "present": False, "read_error": str(exc)}


def colab_command(session: str, candidate_name: str) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z002-tracking-margin",
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
    return {
        "status": "PASS_Z002_TRACKING_MARGIN_RECIPE_READY",
        "stage": "stage_z002_tracking_margin",
        "supersedes_recipe": "phase2-z0035-motion-floor",
        "diagnosis_status": "HOLD_Z0035_UNDER_MOVING",
        "root_cause_summary": [
            "The z=0.002 C0/C2 policies still move at x=0.08 under the compact corrected-bridge sweep, with track ratio about 0.30.",
            "The z=0.002 policies miss the strict tracking gate at about 0.219 rad, so they need tracking margin recovery.",
            "The z=0.0035 motion-floor run drops to track ratio about 0.16, so terrain height escalation is eroding forward progress before causing any velocity-envelope excess.",
            "The next run should recover z=0.002 tracking margin from the moving C0 parent before trying a higher terrain height again.",
        ],
        "recipe_intent": [
            "Warm-start from the z=0.002 C0 245760 checkpoint, not from scratch.",
            "Keep terrain at z=0.002 and no pushes; this rung is about tracking margin, not harder terrain.",
            "Use a very small PPO update with strong restore-policy KL to avoid eroding the moving gait.",
            "Apply a mild target-rate penalty and light motion-floor terms while keeping forward progress pressure active.",
            "Reject any policy that fixes tracking by freezing or drifting at x=0.08.",
        ],
        "restore_checkpoint": {
            "path": rel(DEFAULT_RESTORE_CHECKPOINT),
            "present": DEFAULT_RESTORE_CHECKPOINT.exists(),
        },
        "evidence": {
            "comparison_decision": read_text_optional(Path(args.comparison_decision)),
            "z0035_result": read_text_optional(Path(args.z0035_result)),
        },
        "key_recipe_settings": {
            "workflow": "phase2-z002-tracking-margin",
            "terrain_hfield_z_scale": 0.002,
            "num_timesteps": 122880,
            "restore_policy_kl_scale": 6.0,
            "ppo_learning_rate": 0.000002,
            "ppo_clipping_epsilon": 0.015,
            "ppo_max_grad_norm": 0.08,
            "target_rate_scale": -0.02,
            "actuator_tracking_scale": -0.005,
            "command_progress_scale": 3.5,
            "command_progress_shortfall_scale": -10.0,
            "command_progress_required_ratio": 0.55,
            "forward_progress_scale": 4.5,
            "action_rate_scale": -0.04,
            "push_enable": False,
            "actuator_bridge_velocity_limit_range_rad_s": [2.0, 3.25],
        },
        "acceptance": [
            "z=0.002 x=0.08 no-push passes compact sweep with track ratio >= 0.25 and tracking p95 <= 0.20.",
            "z=0.002 x=0.0 no-push remains passing in the compact sweep.",
            "Full post-training z=0.002 seed gates pass before this policy can be used as a parent for terrain escalation.",
            "No robot validation is authorized by this recipe.",
        ],
        "falsifier": (
            "If tracking improves only by reducing x=0.08 track ratio below 0.25, "
            "stop scalar tracking-margin training and switch to a teacher-action or "
            "trust-region continuity mechanism around the moving z=0.002 policy."
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
        "# Phase 2 z=0.002 Tracking-Margin Next Recipe",
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
    parser.add_argument("--candidate-name", default="phase2_z002_tracking_margin_cuda")
    parser.add_argument("--comparison-decision", default=str(DEFAULT_COMPARISON_DECISION))
    parser.add_argument("--z0035-result", default=str(DEFAULT_Z0035_RESULT))
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
