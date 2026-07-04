#!/usr/bin/env python3
"""Emit the next Phase 2 z=0.0075 post-push stability recipe.

This is a read-only planning artifact. It consumes the measured intermediate
push boundary and traced seed-0/seed-7 failure diagnostic, then emits a
reproducible continuation recipe for the next offline run. It does not train,
SSH, deploy, touch the robot, or modify Playground.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISION_JSON = (
    ROOT
    / "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z0075_intermediate_push_decision.json"
)
DEFAULT_DIAGNOSTIC_JSON = (
    ROOT / "outputs/analysis/phase2_rate150_z0075_intermediate_push_failure_diagnostic.json"
)
DEFAULT_POLICY = (
    ROOT
    / "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx"
)
DEFAULT_BRIDGE = ROOT / "outputs/analysis/actuator_response_fit_corrected_knee.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT / "outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint"
)
DEFAULT_BEHAVIOR_PRIOR_MLP = (
    ROOT
    / "outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_NEXT_RECIPE.md"
)
DEFAULT_OUTPUT_JSON = (
    ROOT / "outputs/analysis/phase2_z0075_post_push_stability_next_recipe.json"
)


PITCH_CHAIN_INDICES = "2,3,4,11,12,13"
RIGHT_PITCH_CHAIN_INDICES = "11,12,13"


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


def file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(str(part)) for part in parts)


def final_training_args(
    behavior_prior_mlp: Path | None,
    behavior_prior_scale: float,
    behavior_prior_huber_delta: float,
) -> list[str]:
    """Arguments appended after phase2-b0g defaults.

    Duplicate argparse options are intentional: the appended values are the
    registered recipe overrides for this bounded continuation.
    """

    args = [
        "--terrain-hfield-z-scale",
        "0.0075",
        "--push-enable",
        "--push-interval-min-s",
        "1.0",
        "--push-interval-max-s",
        "1.5",
        "--push-magnitude-min",
        "0.075",
        "--push-magnitude-max",
        "0.125",
        "--push-recovery-actuator-tracking-scale",
        "-0.025",
        "--push-recovery-actuator-tracking-huber-delta",
        "0.03",
        "--push-recovery-tracking-window-steps",
        "60",
        "--push-recovery-tracking-joint-indices",
        PITCH_CHAIN_INDICES,
        "--base-height-scale",
        "-0.9",
        "--forward-pitch-scale",
        "-0.55",
        "--forward-pitch-rate-scale",
        "-0.12",
        "--actuator-tracking-scale",
        "-0.012",
        "--restore-policy-kl-scale",
        "4.5",
        "--tracking-lin-vel-scale",
        "3",
        "--tracking-sigma",
        "0.01",
        "--forward-progress-scale",
        "2.8",
        "--command-progress-scale",
        "1.7",
        "--command-progress-shortfall-scale",
        "-4.5",
        "--command-progress-required-ratio",
        "0.45",
        "--action-rate-scale",
        "-0.07",
        "--action-magnitude-scale",
        "-0.004",
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
        "--zero-command-probability",
        "0.15",
    ]
    if behavior_prior_mlp is not None:
        args.extend(
            [
                "--enable-behavior-prior",
                "--behavior-prior-mlp-npz",
                rel(behavior_prior_mlp) or str(behavior_prior_mlp),
                "--behavior-prior-scale",
                f"{behavior_prior_scale:.12g}",
                "--behavior-prior-huber-delta",
                f"{behavior_prior_huber_delta:.12g}",
            ]
        )
    return args


def colab_command(
    session: str,
    candidate_name: str,
    restore_checkpoint: Path,
    behavior_prior_mlp: Path | None,
    behavior_prior_scale: float,
    behavior_prior_huber_delta: float,
) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-b0g",
        "--session",
        session,
        "--candidate-name",
        candidate_name,
        "--phase2-restore-checkpoint-path",
        rel(restore_checkpoint) or str(restore_checkpoint),
        "--phase2-terrain-hfield-z-scale",
        "0.0075",
        "--phase2-num-timesteps",
        "122880",
        "--phase2-ppo-num-envs",
        "64",
        "--phase2-ppo-batch-size",
        "512",
        "--candidate-checkpoint-sweep",
        "--candidate-checkpoint-sweep-commands",
        "0.0,0.08",
        "--candidate-checkpoint-sweep-duration",
        "1.0",
        "--candidate-checkpoint-sweep-jax-platform",
        "cpu",
        "--candidate-timeout-s",
        "10800",
        "--phase2-final-training-args-json",
        json.dumps(
            final_training_args(
                behavior_prior_mlp,
                behavior_prior_scale,
                behavior_prior_huber_delta,
            )
        ),
        "--run",
    ]


def local_command(
    output_root: str,
    restore_checkpoint: Path,
    behavior_prior_mlp: Path | None,
    behavior_prior_scale: float,
    behavior_prior_huber_delta: float,
) -> list[str]:
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
        "7200",
        "--task",
        "rough_terrain_backlash",
        "--num-timesteps",
        "122880",
        "--export-min-step",
        "1",
        "--ppo-num-envs",
        "16",
        "--ppo-num-evals",
        "4",
        "--ppo-episode-length",
        "750",
        "--ppo-unroll-length",
        "20",
        "--ppo-batch-size",
        "128",
        "--ppo-num-minibatches",
        "1",
        "--ppo-num-updates-per-batch",
        "2",
        "--restore-checkpoint-path",
        rel(restore_checkpoint) or str(restore_checkpoint),
    ] + final_training_args(
        behavior_prior_mlp,
        behavior_prior_scale,
        behavior_prior_huber_delta,
    )


def eval_command(
    policy: str,
    name: str,
    command_x: float,
    z_scale: float,
    push_min: float | None = None,
    push_max: float | None = None,
    *,
    reset_settle_ticks: int,
    reset_mode: str,
) -> list[str]:
    command = [
        "../envs/open-duck-playground/bin/python",
        "tools/run_candidate_seed_sweep.py",
        "--policies",
        policy,
        "--fit-json",
        "outputs/analysis/actuator_response_fit_corrected_knee.json",
        "--playground-path",
        "../Open_Duck_Playground",
        "--env-python",
        "../envs/open-duck-playground/bin/python",
        "--task",
        "rough_terrain_backlash",
        "--command-x",
        str(command_x),
        "--duration",
        "15",
        "--bridge-mode",
        "fitted",
        "--jax-platform",
        "cpu",
        "--seeds",
        "0,1,2,3,4,5,6,7",
        "--terrain-hfield-z-scale",
        str(z_scale),
        "--reset-settle-ticks",
        str(reset_settle_ticks),
        "--reset-mode",
        reset_mode,
        "--output-md",
        f"outputs/analysis/{name}.md",
        "--output-json",
        f"outputs/analysis/{name}.json",
    ]
    if push_min is not None and push_max is not None:
        command.extend(
            [
                "--eval-push-enable",
                "--eval-push-interval-min-s",
                "1.0",
                "--eval-push-interval-max-s",
                "1.5",
                "--eval-push-magnitude-min",
                str(push_min),
                "--eval-push-magnitude-max",
                str(push_max),
                "--push-recovery-window-s",
                "1.2",
                "--push-recovery-max-abs-pitch-rad",
                "0.8",
                "--push-recovery-min-base-height-m",
                "0.08",
            ]
        )
    command.append("--run")
    return command


def gate_commands(policy: str, *, reset_settle_ticks: int, reset_mode: str) -> list[dict[str, Any]]:
    specs = [
        ("z0075_x008_no_push", 0.08, 0.0075, None, None),
        ("z0075_x000_no_push", 0.0, 0.0075, None, None),
        ("z0075_x008_gentle_push", 0.08, 0.0075, 0.05, 0.10),
        ("z0075_x000_gentle_push", 0.0, 0.0075, 0.05, 0.10),
        ("z0075_x008_intermediate_push", 0.08, 0.0075, 0.075, 0.125),
        ("z0075_x000_intermediate_push", 0.0, 0.0075, 0.075, 0.125),
    ]
    commands = []
    for name, command_x, z_scale, push_min, push_max in specs:
        argv = eval_command(
            policy,
            f"PHASE2_Z0075_POST_PUSH_STABILITY_{name.upper()}",
            command_x,
            z_scale,
            push_min,
            push_max,
            reset_settle_ticks=reset_settle_ticks,
            reset_mode=reset_mode,
        )
        commands.append({"name": name, "argv": argv, "shell": multiline_shell(argv)})
    return commands


def collect(args: argparse.Namespace) -> dict[str, Any]:
    decision_path = Path(args.decision_json)
    diagnostic_path = Path(args.diagnostic_json)
    policy = Path(args.policy)
    bridge = Path(args.bridge_json)
    restore_checkpoint = Path(args.restore_checkpoint)
    behavior_prior_mlp = (
        None if args.behavior_prior_mlp_npz == "" else Path(args.behavior_prior_mlp_npz)
    )
    decision = read_json(decision_path)
    diagnostic = read_json(diagnostic_path)
    failed = diagnostic.get("seeds", [])
    failed_seeds = [item for item in failed if item.get("classification") != "PASS_CONTROL_STABLE"]
    final_args = final_training_args(
        behavior_prior_mlp,
        args.behavior_prior_scale,
        args.behavior_prior_huber_delta,
    )
    colab = colab_command(
        args.session,
        args.candidate_name,
        restore_checkpoint,
        behavior_prior_mlp,
        args.behavior_prior_scale,
        args.behavior_prior_huber_delta,
    )
    local = local_command(
        args.local_output_root,
        restore_checkpoint,
        behavior_prior_mlp,
        args.behavior_prior_scale,
        args.behavior_prior_huber_delta,
    )
    reset_settle_ticks = int(args.reset_settle_ticks)
    reset_mode = str(args.reset_mode)
    return {
        "status": "PASS_PHASE2_Z0075_POST_PUSH_STABILITY_RECIPE_READY",
        "stage": "stage_z0075_post_push_stability",
        "source_status": decision.get("status"),
        "diagnosis_status": diagnostic.get("status"),
        "policy": {
            "path": rel(policy),
            "present": policy.exists(),
            "sha256": file_sha256(policy),
        },
        "corrected_bridge": {
            "path": rel(bridge),
            "present": bridge.exists(),
            "sha256": file_sha256(bridge),
        },
        "restore_checkpoint": {
            "path": rel(restore_checkpoint),
            "present": restore_checkpoint.exists(),
        },
        "behavior_prior": {
            "enabled": behavior_prior_mlp is not None,
            "mlp_npz": rel(behavior_prior_mlp) if behavior_prior_mlp else None,
            "present": behavior_prior_mlp.exists() if behavior_prior_mlp else False,
            "sha256": file_sha256(behavior_prior_mlp) if behavior_prior_mlp else None,
            "scale": args.behavior_prior_scale if behavior_prior_mlp else 0.0,
            "huber_delta": args.behavior_prior_huber_delta if behavior_prior_mlp else None,
            "role": (
                "Frozen state-conditioned Iter21 teacher-action prior; this is used to "
                "preserve the behavior anchor because PPO step-0 compression was rejected."
                if behavior_prior_mlp
                else "disabled"
            ),
        },
        "measured_boundary": {
            "strongest_confirmed_pass": decision.get("strongest_confirmed_pass"),
            "hold": "z=0.0075 terrain with intermediate push magnitude 0.075-0.125",
            "duration_complete": decision.get("duration_complete"),
            "falls": decision.get("falls"),
            "failed_seeds": decision.get("failed_seeds"),
            "metrics": decision.get("metrics"),
            "summary": decision.get("summary"),
            "per_seed": decision.get("per_seed"),
            "reset_settle_ticks": reset_settle_ticks,
            "reset_mode": reset_mode,
        },
        "failure_summary": [
            {
                "seed": item.get("seed"),
                "classification": item.get("classification"),
                "samples": item.get("samples"),
                "last_push_tick": item.get("last_push", {}).get("tick"),
                "ticks_push_end_to_pitch_gt_0p8": item.get(
                    "ticks_from_last_push_end_to_pitch_gt_0p8"
                ),
                "ticks_push_end_to_height_lt_0p08": item.get(
                    "ticks_from_last_push_end_to_height_lt_0p08"
                ),
                "final_pitch": item.get("final", {}).get("body_pitch_rad"),
                "final_height": item.get("final", {}).get("base_height_m"),
                "max_excess": item.get("velocity_excess", {}).get("max_excess"),
            }
            for item in failed_seeds
        ],
        "recipe_intent": [
            "Continue from the corrected-bridge PPO-compatible warm-start; do not train from scratch.",
            "Use the frozen Iter21 teacher-action behavior prior to preserve the gait; restore-policy KL alone failed to preserve forward progress in the A100 post-push run.",
            "Keep z=0.0075 rough terrain and intermediate push magnitude 0.075-0.125 as the target boundary.",
            "Preserve the reset-settle10 rough-terrain/no-push behavior as a regression gate.",
            "Remove the single-tick right-ankle envelope excesses without loosening the corrected actuator envelope.",
            "Extend push-recovery tracking beyond the old 25-tick/0.5s window because seed 5 pitches over inside the longer 1.2s recovery window.",
            "Add base-height, pitch, and pitch-rate pressure so push recovery is graded beyond immediate push success.",
        ],
        "key_recipe_changes": {
            "terrain_hfield_z_scale": 0.0075,
            "push_magnitude_min": 0.075,
            "push_magnitude_max": 0.125,
            "push_interval_s": [1.0, 1.5],
            "push_recovery_tracking_window_steps": 60,
            "push_recovery_tracking_joint_indices": PITCH_CHAIN_INDICES,
            "right_pitch_chain_indices": RIGHT_PITCH_CHAIN_INDICES,
            "push_recovery_actuator_tracking_scale": -0.025,
            "base_height_scale": -0.9,
            "forward_pitch_scale": -0.55,
            "forward_pitch_rate_scale": -0.12,
            "actuator_tracking_scale": -0.012,
            "restore_policy_kl_scale": 4.5,
            "behavior_prior_scale": args.behavior_prior_scale if behavior_prior_mlp else 0.0,
            "behavior_prior_huber_delta": (
                args.behavior_prior_huber_delta if behavior_prior_mlp else None
            ),
            "reset_settle_ticks_for_gates": reset_settle_ticks,
            "reset_mode_for_gates": reset_mode,
        },
        "commands": {
            "final_training_args": final_args,
            "preferred_colab_a100": {
                "argv": colab,
                "shell": multiline_shell(colab),
            },
            "local_rocm_fallback": {
                "argv": local,
                "shell": multiline_shell(local),
                "note": "Use as backend evidence only unless it clears the same canonical CPU gates.",
            },
            "post_training_gates": gate_commands(
                "<candidate.onnx>",
                reset_settle_ticks=reset_settle_ticks,
                reset_mode=reset_mode,
            ),
        },
        "acceptance": [
            "z=0.0075 x=0.08 intermediate push 0.075-0.125 passes 8/8 with zero falls.",
            "z=0.0075 x=0.0 intermediate push preserves command semantics and does not drift.",
            "z=0.0075 gentle-push regression remains 8/8 at x=0.08 and x=0.0.",
            "Corrected per-joint actuator envelope remains authoritative: p95 velocity excess is zero and instantaneous excess is reviewed rather than ignored.",
            "Tracking p95 remains at or below the corrected-bridge gate threshold used by the rate150 candidate.",
        ],
        "falsifier": (
            "If seed 5 still pitches over under intermediate push while the right-ankle "
            "single-tick excesses are removed, stop increasing push magnitude and collect "
            "on-policy post-push recovery labels instead of loosening limits."
        ),
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
        "grounded_replay": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.0075 Post-Push Stability Next Recipe",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        f"source_status: `{payload['source_status']}`",
        f"diagnosis_status: `{payload['diagnosis_status']}`",
        "",
        "This is an offline planning artifact. It did not train, SSH, deploy, touch the robot, or run grounded replay.",
        "",
        "## Inputs",
        "",
        f"- policy: `{payload['policy']['path']}`",
        f"- policy_sha256: `{payload['policy']['sha256']}`",
        f"- corrected_bridge: `{payload['corrected_bridge']['path']}`",
        f"- corrected_bridge_sha256: `{payload['corrected_bridge']['sha256']}`",
        f"- restore_checkpoint: `{payload['restore_checkpoint']['path']}`",
        f"- restore_checkpoint_present: `{payload['restore_checkpoint']['present']}`",
        f"- behavior_prior_enabled: `{payload['behavior_prior']['enabled']}`",
        f"- behavior_prior_mlp_npz: `{payload['behavior_prior']['mlp_npz']}`",
        f"- behavior_prior_sha256: `{payload['behavior_prior']['sha256']}`",
        f"- behavior_prior_scale: `{payload['behavior_prior']['scale']}`",
        f"- behavior_prior_huber_delta: `{payload['behavior_prior']['huber_delta']}`",
        f"- behavior_prior_role: {payload['behavior_prior']['role']}",
        "",
        "## Measured Boundary",
        "",
        f"- strongest_confirmed_pass: `{payload['measured_boundary']['strongest_confirmed_pass']}`",
        f"- hold: `{payload['measured_boundary']['hold']}`",
        f"- duration_complete: `{payload['measured_boundary']['duration_complete']}`",
        f"- falls: `{payload['measured_boundary']['falls']}`",
        f"- failed_seeds: `{payload['measured_boundary']['failed_seeds']}`",
        "",
        "## Failure Summary",
        "",
        "| seed | classification | samples | last push tick | ticks to pitch>0.8 | ticks to height<0.08 | final pitch | final height | max excess joint | max excess |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for item in payload["failure_summary"]:
        max_excess = item.get("max_excess") or {}
        lines.append(
            f"| {item.get('seed')} | `{item.get('classification')}` | {item.get('samples')} | "
            f"{item.get('last_push_tick')} | {item.get('ticks_push_end_to_pitch_gt_0p8')} | "
            f"{item.get('ticks_push_end_to_height_lt_0p08')} | "
            f"{item.get('final_pitch'):.4f} | {item.get('final_height'):.4f} | "
            f"`{max_excess.get('joint')}` | {max_excess.get('excess_rad_s'):.4f} |"
        )
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
            "## Post-Training Gate Commands",
            "",
        ]
    )
    for item in payload["commands"]["post_training_gates"]:
        lines.extend([f"### {item['name']}", "", "```bash", item["shell"], "```", ""])
    lines.extend(["## Acceptance", ""])
    for item in payload["acceptance"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Falsifier", "", payload["falsifier"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision-json", default=str(DEFAULT_DECISION_JSON))
    parser.add_argument("--diagnostic-json", default=str(DEFAULT_DIAGNOSTIC_JSON))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--bridge-json", default=str(DEFAULT_BRIDGE))
    parser.add_argument("--restore-checkpoint", default=str(DEFAULT_RESTORE_CHECKPOINT))
    parser.add_argument("--session", default="open-duck-phase2-a100")
    parser.add_argument(
        "--candidate-name",
        default="phase2_z0075_post_push_stability_cuda",
    )
    parser.add_argument(
        "--local-output-root",
        default="outputs/phase2_domain_randomization/stage_z0075_post_push_stability_local_rocm",
    )
    parser.add_argument("--reset-settle-ticks", type=int, default=10)
    parser.add_argument("--reset-mode", default="home-support")
    parser.add_argument("--behavior-prior-mlp-npz", default=str(DEFAULT_BEHAVIOR_PRIOR_MLP))
    parser.add_argument("--behavior-prior-scale", type=float, default=-0.22)
    parser.add_argument("--behavior-prior-huber-delta", type=float, default=0.06)
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
