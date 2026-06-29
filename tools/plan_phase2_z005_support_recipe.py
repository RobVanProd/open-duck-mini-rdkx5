#!/usr/bin/env python3
"""Plan the next Phase 2 z=0.005 support continuation.

This is a read-only planning artifact. It consumes the current Phase 2 gate
ledger and seed-5 diagnostic, then emits the exact support/base-height recipe
that should be run next on a fresh A100/Colab session. It does not train, SSH,
deploy, touch the robot, or modify Playground.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_JSON = ROOT / "outputs/analysis/phase2_curriculum_gate_ledger.json"
DEFAULT_DIAGNOSTIC_JSON = ROOT / "outputs/analysis/phase2_z005_seed5_failure_diagnostic.json"
DEFAULT_STATUS_JSON = ROOT / "outputs/analysis/phase2_current_status.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z005_SUPPORT_NEXT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z005_support_next_recipe.json"
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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(part) for part in parts)


def colab_command(session: str, candidate_name: str) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z005-support",
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


def local_command(restore_checkpoint: Path, output_root: str) -> list[str]:
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
        "81920",
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
        rel(restore_checkpoint) or str(restore_checkpoint),
        "--ppo-learning-rate",
        "0.000003",
        "--ppo-entropy-cost",
        "0.001",
        "--ppo-clipping-epsilon",
        "0.02",
        "--ppo-max-grad-norm",
        "0.1",
        "--restore-policy-kl-scale",
        "4",
        "--tracking-lin-vel-scale",
        "3",
        "--tracking-sigma",
        "0.01",
        "--forward-progress-scale",
        "2.5",
        "--forward-wrong-direction-scale",
        "-4",
        "--forward-wrong-direction-allowed-reverse-ratio",
        "0.02",
        "--command-progress-scale",
        "1.5",
        "--command-progress-shortfall-scale",
        "-4",
        "--command-progress-required-ratio",
        "0.45",
        "--command-progress-warmup-steps",
        "30",
        "--action-rate-huber-delta",
        "0.05",
        "--actuator-tracking-huber-delta",
        "0.03",
        "--forward-swing-clearance-huber-delta",
        "0.003",
        "--forward-swing-advance-huber-delta",
        "0.002",
        "--action-rate-scale",
        "-0.08",
        "--action-magnitude-scale",
        "-0.005",
        "--base-height-scale",
        "-0.8",
        "--forward-pitch-scale",
        "-0.4",
        "--forward-pitch-rate-scale",
        "-0.08",
        "--forward-contact-support-scale",
        "-0.35",
        "--forward-contact-support-no-contact-weight",
        "2.0",
        "--forward-contact-support-asymmetry-weight",
        "0.25",
        "--forward-single-support-scale",
        "0.1",
        "--forward-double-support-scale",
        "-0.15",
        "--forward-double-support-dwell-scale",
        "-0.25",
        "--forward-double-support-dwell-grace-steps",
        "16",
        "--forward-swing-clearance-scale",
        "-0.0005",
        "--forward-swing-clearance-target-m",
        "0.018",
        "--forward-swing-advance-scale",
        "-0.002",
        "--forward-swing-advance-target-m",
        "0.004",
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
        "--push-interval-min-s",
        "7",
        "--push-interval-max-s",
        "12",
        "--push-magnitude-min",
        "0.02",
        "--push-magnitude-max",
        "0.1",
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
        "-0.01",
        "--terrain-hfield-z-scale",
        "0.005",
    ]


def gate_commands(policy: str) -> list[list[str]]:
    common = [
        "python3",
        "tools/eval_policy_with_actuator_bridge.py",
        "--mode",
        "closed-loop-sim",
        "--eval-role",
        "candidate",
        "--policy",
        policy,
        "--fit-json",
        "outputs/analysis/actuator_response_fit_corrected_knee.json",
        "--playground-path",
        "../Open_Duck_Playground",
        "--env-python",
        "../envs/open-duck-playground/bin/python",
        "--task",
        "rough_terrain_backlash",
        "--duration",
        "15",
        "--bridge-mode",
        "fitted",
    ]
    specs = [
        ("z005_x008_nopush", "0.08", "0.005"),
        ("z005_x000_nopush", "0.0", "0.005"),
        ("z002_x008_nopush", "0.08", "0.002"),
        ("z002_x000_nopush", "0.0", "0.002"),
    ]
    commands = []
    for name, command_x, z_scale in specs:
        commands.append(
            common
            + [
                "--command-x",
                command_x,
                "--terrain-hfield-z-scale",
                z_scale,
                "--output-dir",
                f"outputs/analysis/phase2_z005_support_next_gate/{name}",
            ]
        )
    return commands


def collect(args: argparse.Namespace) -> dict[str, Any]:
    ledger_path = Path(args.ledger_json)
    diagnostic_path = Path(args.diagnostic_json)
    status_path = Path(args.status_json)
    ledger = read_json(ledger_path)
    diagnostic = read_json(diagnostic_path)
    status = read_json(status_path)
    restore_checkpoint = Path(args.restore_checkpoint)
    colab = colab_command(args.session, args.candidate_name)
    local = local_command(restore_checkpoint, args.local_output_root)
    return {
        "status": "PASS_Z005_SUPPORT_RECIPE_READY",
        "stage": "stage_z005_support",
        "diagnosis_status": diagnostic.get("status"),
        "current_gate_status": ledger.get("status"),
        "current_status": status.get("status"),
        "candidate": ledger.get("candidate"),
        "restore_checkpoint": {
            "path": rel(restore_checkpoint),
            "present": restore_checkpoint.exists(),
        },
        "root_cause_summary": diagnostic.get("findings", {}).get("shared", []),
        "recipe_intent": [
            "Continue from the last z=0.002 passing A2 checkpoint; do not train from scratch.",
            "Use z=0.005 rough terrain with no push; this is a support/base-height rung, not a push rung.",
            "Increase base-height and contact-support pressure while keeping restore-policy KL strong enough to preserve the z=0.002 gait.",
            "Strengthen wrong-direction penalty because seed 5 collapses backward even at x=0.0.",
            "Relax double-support dwell pressure compared with the prior z=0.005 recipe so the zero-command support behavior is not over-penalized.",
            "Keep corrected actuator bridge limits authoritative and reject velocity excess at the gate.",
        ],
        "key_recipe_changes": {
            "restore_policy_kl_scale": 4.0,
            "base_height_scale": -0.8,
            "forward_wrong_direction_scale": -4.0,
            "forward_wrong_direction_allowed_reverse_ratio": 0.02,
            "forward_contact_support_scale": -0.35,
            "forward_contact_support_no_contact_weight": 2.0,
            "forward_contact_support_asymmetry_weight": 0.25,
            "forward_double_support_scale": -0.15,
            "forward_double_support_dwell_scale": -0.25,
            "forward_double_support_dwell_grace_steps": 16,
            "terrain_hfield_z_scale": 0.005,
            "push_enable": False,
        },
        "commands": {
            "preferred_colab_a100": {
                "argv": colab,
                "shell": multiline_shell(colab),
            },
            "local_rocm_fallback": {
                "argv": local,
                "shell": multiline_shell(local),
                "note": "Backend evidence only unless it clears the same canonical gates; local ROCm is not the preferred policy-producing path.",
            },
            "post_training_gate_examples": [
                {"argv": command, "shell": shell_join(command)} for command in gate_commands("<candidate.onnx>")
            ],
        },
        "acceptance": [
            "z=0.005 x=0.08 no-push passes 8/8, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.",
            "z=0.005 x=0.0 no-push passes 8/8, zero falls, no velocity excess, |mean vx| <= 0.005.",
            "z=0.002 no-push and gentle-push regression gates remain passing.",
        ],
        "falsifier": (
            "If seed 5 still collapses vertically at z=0.005 x=0.0 with no velocity excess, "
            "stop increasing terrain difficulty and inspect reset/support distribution or add an intermediate terrain rung."
        ),
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.005 Support Next Recipe",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        f"diagnosis_status: `{payload['diagnosis_status']}`",
        f"current_gate_status: `{payload['current_gate_status']}`",
        "",
        "This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Current Candidate",
        "",
        f"- candidate: `{payload['candidate'].get('path')}`",
        f"- candidate_sha256: `{payload['candidate'].get('sha256')}`",
        f"- restore_checkpoint: `{payload['restore_checkpoint']['path']}`",
        f"- restore_checkpoint_present: `{payload['restore_checkpoint']['present']}`",
        "",
        "## Diagnosis Driving This Recipe",
        "",
    ]
    for item in payload["root_cause_summary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Recipe Intent", ""])
    for item in payload["recipe_intent"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Key Recipe Changes", ""])
    for key, value in payload["key_recipe_changes"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Preferred A100 / Colab Command",
            "",
            "```bash",
            payload["commands"]["preferred_colab_a100"]["shell"],
            "```",
            "",
            "## Local ROCm Fallback Command",
            "",
            payload["commands"]["local_rocm_fallback"]["note"],
            "",
            "```bash",
            payload["commands"]["local_rocm_fallback"]["shell"],
            "```",
            "",
            "## Post-Training Gate Examples",
            "",
        ]
    )
    for item in payload["commands"]["post_training_gate_examples"]:
        lines.extend(["```bash", item["shell"], "```", ""])
    lines.extend(["## Acceptance", ""])
    for item in payload["acceptance"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Falsifier", "", payload["falsifier"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger-json", default=str(DEFAULT_LEDGER_JSON))
    parser.add_argument("--diagnostic-json", default=str(DEFAULT_DIAGNOSTIC_JSON))
    parser.add_argument("--status-json", default=str(DEFAULT_STATUS_JSON))
    parser.add_argument("--restore-checkpoint", default=str(DEFAULT_RESTORE_CHECKPOINT))
    parser.add_argument("--session", default="open-duck-l4")
    parser.add_argument("--candidate-name", default="phase2_z005_support_baseheight_cuda")
    parser.add_argument(
        "--local-output-root",
        default="outputs/phase2_domain_randomization/stage_z005_support_baseheight_local_rocm_safeenv_8env_81920",
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = collect(args)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, output_md)
    print(payload["status"])
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
