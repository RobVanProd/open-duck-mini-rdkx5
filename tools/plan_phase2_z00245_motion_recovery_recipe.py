#!/usr/bin/env python3
"""Plan the next Phase 2 z=0.00245 motion-recovery recipe.

This is a read-only planning tool. It records the response to the A100
z=0.00245 on-policy support hold: the run stayed below the corrected actuator
envelope and kept x=0.0 stable, but under-moved at x=0.08.

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
DEFAULT_HOLD_JSON = ROOT / "outputs/analysis/phase2_z00245_a100_on_policy_support_hold_20260702.json"
DEFAULT_SWEEP_JSON = (
    ROOT
    / "outputs/analysis/phase2_z00245_on_policy_support_fullrun_compact_sweep"
    / "candidate_checkpoint_sweep.json"
)
DEFAULT_BRIDGE_JSON = ROOT / "outputs/analysis/actuator_response_fit_corrected_knee.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z00245_MOTION_RECOVERY_NEXT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z00245_motion_recovery_next_recipe.json"
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


def file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_digest(path: Path) -> dict[str, Any]:
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
    parts = [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z0025-boundary",
        "--session",
        session,
        "--candidate-name",
        candidate_name,
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
        "--phase2-target-rate-scale",
        "-0.005",
        "--phase2-actuator-tracking-scale",
        "-0.005",
        "--phase2-forward-progress-scale",
        "5.0",
        "--phase2-command-progress-scale",
        "4.0",
        "--phase2-command-progress-shortfall-scale",
        "-12.0",
        "--phase2-command-progress-required-ratio",
        "0.55",
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


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    hold_path = Path(args.hold_json)
    sweep_path = Path(args.sweep_json)
    bridge_path = Path(args.bridge_json)
    restore_path = Path(args.restore_checkpoint)
    hold = read_json_optional(hold_path)
    sweep = read_json_optional(sweep_path)
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
    return {
        "status": "PASS_Z00245_MOTION_RECOVERY_RECIPE_READY",
        "stage": "stage_z00245_motion_recovery",
        "supersedes": "stage_z00245_on_policy_support_recovery",
        "diagnosis_status": "HOLD_Z00245_ON_POLICY_SUPPORT_LOW_PROGRESS",
        "terrain_hfield_z_scale": float(args.terrain_z),
        "decision_basis": {
            "hold_json": rel(hold_path),
            "hold_status": hold.get("status"),
            "compact_sweep_json": rel(sweep_path),
            "compact_sweep_sha256": file_sha256(sweep_path),
            "promotion_decisions": sweep.get("promotion_decisions", []),
        },
        "canonical_inputs": {
            "corrected_bridge": {
                "path": rel(bridge_path),
                "present": bridge_path.exists(),
                "sha256": file_sha256(bridge_path),
            },
            "restore_checkpoint": checkpoint_digest(restore_path),
        },
        "root_cause_summary": [
            "The z=0.00245 A100 support run completed and exported checkpoints.",
            "All compact x=0.08 screens stayed below the corrected per-joint velocity envelope with zero saturation.",
            "All compact x=0.08 screens under-moved: track ratio 0.1823-0.2200 and mean vx 0.0146-0.0176 m/s.",
            "The hold is conservative low progress plus a small tracking miss, not actuator overspeed.",
        ],
        "recipe_intent": [
            "Warm-start from the same Phase A2 trainable checkpoint; do not train from scratch.",
            "Keep the z=0.00245 terrain rung; do not advance terrain or add pushes.",
            "Raise command/forward-progress pressure enough to escape the conservative gait.",
            "Relax target-rate damping slightly because the failed checkpoints were far below the corrected envelope.",
            "Keep corrected actuator tracking active and reject any post-training velocity excess at the gate.",
        ],
        "key_changes_vs_support_hold": {
            "phase2_forward_progress_scale": "4.0 -> 5.0",
            "phase2_command_progress_scale": "3.0 -> 4.0",
            "phase2_command_progress_shortfall_scale": "-8.0 -> -12.0",
            "phase2_command_progress_required_ratio": "0.45 -> 0.55",
            "phase2_target_rate_scale": "-0.01 -> -0.005",
            "phase2_actuator_tracking_scale": "-0.005 unchanged",
            "terrain_hfield_z_scale": f"{args.terrain_z} unchanged",
            "push_enable": "disabled unchanged",
        },
        "acceptance": [
            "Compact x=0.08 checkpoint sweep must find at least one checkpoint with track ratio >= 0.25 and mean vx >= 0.02 m/s while staying below the corrected envelope.",
            "Promoted checkpoint must pass the normal corrected-bridge x=0.0 and x=0.08 8-seed gates before any robot consideration.",
            "x=0.0 command semantics must remain stable; zero-command drift is not acceptable progress.",
            "No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this recipe.",
        ],
        "falsifier": (
            "If this recipe remains in-envelope but still under-moves at x=0.08, "
            "stop this scalar-progress-pressure path. The next branch should add "
            "a behavior-prior/teacher-continuity mechanism or live-oracle data, "
            "not another generic support/safety penalty."
        ),
        "commands": {
            "package_only": {"argv": package_cmd, "shell": multiline_shell(package_cmd)},
            "preferred_colab_gpu": {"argv": run_cmd, "shell": multiline_shell(run_cmd)},
            "detached_colab_gpu": {
                "argv": detached_cmd,
                "shell": multiline_shell(detached_cmd),
                "note": "Use this when Colab CLI polling is unreliable; monitor with short colab exec/download commands.",
            },
        },
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.00245 Motion-Recovery Next Recipe",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        f"supersedes: `{payload['supersedes']}`",
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
    lines.extend(["", "## Key Changes", ""])
    for key, value in payload["key_changes_vs_support_hold"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Preferred Colab GPU Command", "", "```bash"])
    lines.append(payload["commands"]["preferred_colab_gpu"]["shell"])
    lines.extend(["```", "", "## Detached Colab GPU Command", "", "```bash"])
    lines.append(payload["commands"]["detached_colab_gpu"]["shell"])
    lines.extend(["```", "", "## Acceptance", ""])
    lines.extend(f"- {item}" for item in payload["acceptance"])
    lines.extend(["", "## Falsifier", "", payload["falsifier"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="open-duck-a100-phase2-z00245")
    parser.add_argument("--candidate-name", default="phase2_z00245_motion_recovery_cuda")
    parser.add_argument("--terrain-z", default="0.00245")
    parser.add_argument("--timesteps", type=int, default=122880)
    parser.add_argument("--hold-json", default=str(DEFAULT_HOLD_JSON))
    parser.add_argument("--sweep-json", default=str(DEFAULT_SWEEP_JSON))
    parser.add_argument("--bridge-json", default=str(DEFAULT_BRIDGE_JSON))
    parser.add_argument("--restore-checkpoint", default=str(DEFAULT_RESTORE_CHECKPOINT))
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
