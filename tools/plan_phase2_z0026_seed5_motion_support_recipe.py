#!/usr/bin/env python3
"""Plan the Phase 2 z=0.0026 seed-5 motion-support repair recipe.

This is a read-only planning tool. It records the response to the current
z=0.0026 terrain hold: the preserved teacher-continuity checkpoint passes
7/8 x=0.08 seeds, but seed 5 reverses and loses base height while staying
inside the corrected actuator envelope.

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
DEFAULT_PARENT_GATE_JSON = (
    ROOT / "outputs/analysis/phase2_z0026_teacher_continuity_81920_full_gate_x008.json"
)
DEFAULT_PARENT_FAILURE_MD = (
    ROOT / "outputs/analysis/PHASE2_Z0026_TEACHER_CONTINUITY_81920_SEED5_FAILURE_ANALYSIS_20260702.md"
)
DEFAULT_SUPPORT_DIAGNOSTIC_JSON = (
    ROOT / "outputs/analysis/phase2_z0026_seed5_support_recovery_diagnostic_20260702.json"
)
DEFAULT_TARGETLIMITED_DECISION_JSON = (
    ROOT / "outputs/analysis/phase2_targetlimited0999_z0026_support_transfer_decision_20260702.json"
)
DEFAULT_BRIDGE_JSON = ROOT / "outputs/analysis/actuator_response_fit_corrected_knee.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT / "outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_NEXT_RECIPE.md"
)
DEFAULT_OUTPUT_JSON = (
    ROOT / "outputs/analysis/phase2_z0026_seed5_motion_support_next_recipe.json"
)


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": rel(path), "present": False}
    if path.is_file():
        return {"path": rel(path), "present": True, "sha256": file_sha256(path)}
    files = sorted(item for item in path.rglob("*") if item.is_file())
    digest = hashlib.sha256()
    for item in files:
        relative = item.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((file_sha256(item) or "").encode("ascii"))
        digest.update(b"\0")
    return {
        "path": rel(path),
        "present": True,
        "file_count": len(files),
        "tree_sha256": digest.hexdigest(),
    }


def read_json_optional(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_read_error": str(exc), "_path": rel(path)}


def read_text_optional(path: Path) -> dict[str, Any]:
    try:
        return {
            "path": rel(path),
            "present": True,
            "sha256": file_sha256(path),
            "excerpt": path.read_text(errors="replace")[:5000],
        }
    except Exception as exc:
        return {"path": rel(path), "present": False, "read_error": str(exc)}


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(part) for part in parts)


def colab_command(
    *,
    session: str,
    candidate_name: str,
    terrain_z: str,
    timesteps: int,
    package_only: bool,
    no_poll: bool,
) -> list[str]:
    final_args = [
        "--forward-wrong-direction-scale",
        "-6.0",
        "--forward-wrong-direction-allowed-reverse-ratio",
        "0.005",
        "--base-height-scale",
        "-0.45",
        "--forward-pitch-scale",
        "-0.35",
        "--forward-pitch-rate-scale",
        "-0.07",
    ]
    parts = [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z002-teacher-continuity",
        "--session",
        session,
        "--candidate-name",
        candidate_name,
        "--phase2-restore-checkpoint-path",
        rel(DEFAULT_RESTORE_CHECKPOINT) or str(DEFAULT_RESTORE_CHECKPOINT),
        "--phase2-terrain-hfield-z-scale",
        terrain_z,
        "--phase2-num-timesteps",
        str(timesteps),
        "--phase2-ppo-num-envs",
        "64",
        "--phase2-ppo-batch-size",
        "512",
        "--phase2-ppo-num-minibatches",
        "4",
        "--phase2-ppo-num-updates-per-batch",
        "2",
        "--artifact-checkpoint-mode",
        "all",
        "--phase2-final-training-args-json",
        json.dumps(final_args),
        "--candidate-checkpoint-sweep",
        "--candidate-checkpoint-sweep-commands",
        "0.0,0.08",
        "--candidate-checkpoint-sweep-duration",
        "1.0",
        "--candidate-checkpoint-sweep-jax-platform",
        "cpu",
        "--candidate-timeout-s",
        "10800",
    ]
    if no_poll:
        parts.append("--no-poll")
    if package_only:
        parts.append("--package-only")
    else:
        parts.append("--run")
    return parts


def post_training_seed5_command(policy_path: str) -> list[str]:
    return [
        "../envs/open-duck-playground/bin/python",
        "tools/run_candidate_seed_sweep.py",
        "--policies",
        f"repair={policy_path}",
        "--fit-json",
        "outputs/analysis/actuator_response_fit_corrected_knee.json",
        "--playground-path",
        "../Open_Duck_Playground",
        "--env-python",
        "../envs/open-duck-playground/bin/python",
        "--duration",
        "2",
        "--bridge-mode",
        "fitted",
        "--task",
        "rough_terrain_backlash",
        "--jax-platform",
        "cpu",
        "--terrain-hfield-z-scale",
        "0.0026",
        "--command-x",
        "0.08",
        "--seeds",
        "5",
        "--trace-seeds",
        "5",
        "--trace-full-obs",
        "--output-dir",
        "outputs/analysis/phase2_z0026_seed5_motion_support_repair_seed5_short",
        "--output-md",
        "outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_REPAIR_SEED5_SHORT.md",
        "--output-json",
        "outputs/analysis/phase2_z0026_seed5_motion_support_repair_seed5_short.json",
        "--run",
    ]


def post_training_full_gate_commands(policy_path: str) -> dict[str, dict[str, Any]]:
    commands = {}
    for command_x, label in [("0.0", "x000"), ("0.08", "x008")]:
        parts = [
            "../envs/open-duck-playground/bin/python",
            "tools/run_candidate_seed_sweep.py",
            "--policies",
            f"repair={policy_path}",
            "--fit-json",
            "outputs/analysis/actuator_response_fit_corrected_knee.json",
            "--playground-path",
            "../Open_Duck_Playground",
            "--env-python",
            "../envs/open-duck-playground/bin/python",
            "--duration",
            "15",
            "--bridge-mode",
            "fitted",
            "--task",
            "rough_terrain_backlash",
            "--jax-platform",
            "cpu",
            "--terrain-hfield-z-scale",
            "0.0026",
            "--command-x",
            command_x,
            "--seeds",
            "0,1,2,3,4,5,6,7",
            "--output-dir",
            f"outputs/analysis/phase2_z0026_seed5_motion_support_repair_full_{label}",
            "--output-md",
            f"outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_REPAIR_FULL_{label.upper()}.md",
            "--output-json",
            f"outputs/analysis/phase2_z0026_seed5_motion_support_repair_full_{label}.json",
            "--run",
        ]
        commands[label] = {"argv": parts, "shell": multiline_shell(parts)}
    return commands


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    parent_gate = read_json_optional(Path(args.parent_gate_json))
    support_diagnostic = read_json_optional(Path(args.support_diagnostic_json))
    targetlimited_decision = read_json_optional(Path(args.targetlimited_decision_json))
    bridge_path = Path(args.bridge_json)
    package_cmd = colab_command(
        session=args.session,
        candidate_name=args.candidate_name,
        terrain_z=args.terrain_z,
        timesteps=args.timesteps,
        package_only=True,
        no_poll=False,
    )
    run_cmd = colab_command(
        session=args.session,
        candidate_name=args.candidate_name,
        terrain_z=args.terrain_z,
        timesteps=args.timesteps,
        package_only=False,
        no_poll=False,
    )
    detached_cmd = colab_command(
        session=args.session,
        candidate_name=args.candidate_name,
        terrain_z=args.terrain_z,
        timesteps=args.timesteps,
        package_only=False,
        no_poll=True,
    )
    candidate_placeholder = "<downloaded_or_exported_repair_candidate.onnx>"
    return {
        "status": "PASS_Z0026_SEED5_MOTION_SUPPORT_RECIPE_READY",
        "stage": "stage_z0026_seed5_motion_support_repair",
        "supersedes": [
            "phase2-z005-support broad support recovery for this failure",
            "z=0.0025 support-only repair loops for this failure",
        ],
        "diagnosis_status": "HOLD_Z0026_MOVING_COMMAND_SUPPORT_TRANSFER",
        "terrain_hfield_z_scale": float(args.terrain_z),
        "decision_basis": {
            "parent_full_gate_json": rel(Path(args.parent_gate_json)),
            "parent_full_gate_present": Path(args.parent_gate_json).exists(),
            "support_diagnostic_json": rel(Path(args.support_diagnostic_json)),
            "support_diagnostic_status": support_diagnostic.get("status"),
            "targetlimited_decision_json": rel(Path(args.targetlimited_decision_json)),
            "targetlimited_status": targetlimited_decision.get("status"),
        },
        "canonical_inputs": {
            "corrected_bridge": {
                "path": rel(bridge_path),
                "present": bridge_path.exists(),
                "sha256": file_sha256(bridge_path),
            },
            "restore_checkpoint": tree_digest(DEFAULT_RESTORE_CHECKPOINT),
        },
        "root_cause_summary": [
            "At z=0.0026, the preserved teacher-continuity 81920 checkpoint is a near-miss: full x=0.08 gate is 7/8, with seed 5 as the only fall.",
            "Seed 5 fails by reverse velocity and base-height collapse while the pitch-chain sent target rates remain inside the corrected actuator envelope.",
            "The current z=0.0025 target-limited support candidate transfers to z=0.0026 at x=0.0 in a short screen, but fails the moving x=0.08 seed-5 screen by the same reverse-height collapse.",
            "The broad phase2-z005-support recovery direction stabilized the short screen by moving backward in double support, so broad support shaping is closed for this failure.",
        ],
        "recipe_intent": [
            "Warm-start from the preserved z=0.0026 teacher-continuity 81920 checkpoint; do not train from scratch.",
            "Keep terrain at z=0.0026 and keep pushes disabled; this isolates support transfer before adding new perturbations.",
            "Preserve the 7 passing seeds with teacher-continuity restore KL and small PPO updates.",
            "Add narrow anti-reverse and base-height pressure only; do not add broad double-support dwell/contact-shaping terms.",
            "Select by compact checkpoint sweep, then require full x=0.0 and x=0.08 8-seed gates before promoting.",
        ],
        "key_recipe_settings": {
            "workflow": "phase2-z002-teacher-continuity",
            "terrain_hfield_z_scale": float(args.terrain_z),
            "num_timesteps": args.timesteps,
            "ppo_num_envs": 64,
            "restore_policy_kl_scale": 7.5,
            "ppo_learning_rate": 0.000002,
            "ppo_clipping_epsilon": 0.015,
            "ppo_max_grad_norm": 0.08,
            "target_rate_scale": -0.01,
            "actuator_tracking_scale": -0.005,
            "forward_progress_scale": 4.5,
            "command_progress_scale": 3.5,
            "command_progress_shortfall_scale": -10.0,
            "command_progress_required_ratio": 0.55,
            "action_rate_scale": -0.035,
            "base_height_scale": -0.45,
            "forward_pitch_scale": -0.35,
            "forward_pitch_rate_scale": -0.07,
            "forward_wrong_direction_scale": -6.0,
            "forward_wrong_direction_allowed_reverse_ratio": 0.005,
            "push_enable": False,
        },
        "acceptance": [
            "Seed 5 x=0.08 short screen must complete duration with positive mean vx and no velocity-envelope excess.",
            "Full z=0.0026 x=0.08 gate must improve from 7/8 to 8/8 duration complete without reducing the passing seeds into standstill.",
            "Full z=0.0026 x=0.0 gate must remain 8/8 duration complete with command semantics preserved.",
            "No candidate is promotable if mean x=0.08 track ratio improves only by over-envelope target velocity or x=0.0 drift.",
            "No robot validation is authorized by this recipe.",
        ],
        "falsifiers": [
            "If seed 5 remains reverse/height-collapse while velocity stays in envelope, stop narrow scalar repair and inspect the seed-5 state/contact manifold.",
            "If the recipe removes the seed-5 fall by lowering motion or reversing, stop this direction; it repeats the broad support-recovery failure.",
            "If any passing seed regresses to fall/standstill, reduce or abandon the anti-reverse/base-height terms rather than escalating terrain.",
        ],
        "evidence": {
            "parent_failure_analysis": read_text_optional(Path(args.parent_failure_md)),
            "parent_full_gate_aggregate": parent_gate.get("aggregate", {}),
        },
        "commands": {
            "package_only": {"argv": package_cmd, "shell": multiline_shell(package_cmd)},
            "preferred_colab_gpu": {"argv": run_cmd, "shell": multiline_shell(run_cmd)},
            "detached_colab_gpu": {"argv": detached_cmd, "shell": multiline_shell(detached_cmd)},
            "post_training_seed5_short": {
                "argv": post_training_seed5_command(candidate_placeholder),
                "shell": multiline_shell(post_training_seed5_command(candidate_placeholder)),
            },
            "post_training_full_gates": post_training_full_gate_commands(candidate_placeholder),
        },
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "grounded_replay_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.0026 Seed-5 Motion-Support Next Recipe",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        f"diagnosis_status: `{payload['diagnosis_status']}`",
        f"terrain_hfield_z_scale: `{payload['terrain_hfield_z_scale']}`",
        "",
        "This is an offline planning artifact. It did not train, SSH, deploy, touch the robot, or run grounded replay.",
        "",
        "## Root Cause Summary",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["root_cause_summary"])
    lines.extend(["", "## Recipe Intent", ""])
    lines.extend(f"- {item}" for item in payload["recipe_intent"])
    lines.extend(["", "## Canonical Inputs", ""])
    bridge = payload["canonical_inputs"]["corrected_bridge"]
    restore = payload["canonical_inputs"]["restore_checkpoint"]
    lines.extend(
        [
            f"- corrected_bridge: `{bridge['path']}` present=`{bridge['present']}` sha256=`{bridge['sha256']}`",
            f"- restore_checkpoint: `{restore['path']}` present=`{restore['present']}` tree_sha256=`{restore.get('tree_sha256')}`",
        ]
    )
    lines.extend(["", "## Key Settings", ""])
    for key, value in payload["key_recipe_settings"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Preferred Colab GPU Command", "", "```bash"])
    lines.append(payload["commands"]["preferred_colab_gpu"]["shell"])
    lines.extend(["```", "", "## Detached Colab GPU Command", "", "```bash"])
    lines.append(payload["commands"]["detached_colab_gpu"]["shell"])
    lines.extend(["```", "", "## Post-Training Seed-5 Short Gate", "", "```bash"])
    lines.append(payload["commands"]["post_training_seed5_short"]["shell"])
    lines.extend(["```", "", "## Post-Training Full Gates", ""])
    for label, command in payload["commands"]["post_training_full_gates"].items():
        lines.extend([f"### {label}", "", "```bash", command["shell"], "```", ""])
    lines.extend(["## Acceptance", ""])
    lines.extend(f"- {item}" for item in payload["acceptance"])
    lines.extend(["", "## Falsifiers", ""])
    lines.extend(f"- {item}" for item in payload["falsifiers"])
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="open-duck-a100-phase2-z0026")
    parser.add_argument("--candidate-name", default="phase2_z0026_seed5_motion_support_cuda")
    parser.add_argument("--terrain-z", default="0.0026")
    parser.add_argument("--timesteps", type=int, default=81920)
    parser.add_argument("--parent-gate-json", default=str(DEFAULT_PARENT_GATE_JSON))
    parser.add_argument("--parent-failure-md", default=str(DEFAULT_PARENT_FAILURE_MD))
    parser.add_argument("--support-diagnostic-json", default=str(DEFAULT_SUPPORT_DIAGNOSTIC_JSON))
    parser.add_argument("--targetlimited-decision-json", default=str(DEFAULT_TARGETLIMITED_DECISION_JSON))
    parser.add_argument("--bridge-json", default=str(DEFAULT_BRIDGE_JSON))
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
