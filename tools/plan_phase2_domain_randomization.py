#!/usr/bin/env python3
"""Generate the Phase 2 domain-randomized robustness training plan.

This planner is offline-only and dry-run by design. It writes a staged
curriculum manifest and command templates, but it intentionally refuses to mark
the plan runnable unless a trainable warm-start checkpoint is provided.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shlex
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = (
    ROOT
    / "policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx"
)
DEFAULT_FIT = ROOT / "outputs/analysis/actuator_response_fit_corrected_knee.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_DOMAIN_RANDOMIZATION_PLAN.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_domain_randomization_plan.json"
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs/open-duck-playground/bin/python"


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def cli(value: Any) -> str:
    if isinstance(value, float):
        text = f"{value:.12f}".rstrip("0").rstrip(".")
        return text if text not in {"", "-0"} else "0"
    return str(value)


def stage_command(args: argparse.Namespace, stage: dict[str, Any], output_root: Path) -> list[str]:
    command = [
        str(Path(args.env_python)),
        str(ROOT / "tools/run_actuator_bridge_training_smoke.py"),
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--output-root",
        str(output_root / stage["id"]),
        "--platform",
        args.platform,
        "--task",
        stage["task"],
        "--num-timesteps",
        str(stage["num_timesteps"]),
        "--export-min-step",
        str(args.export_min_step),
        "--ppo-num-envs",
        str(args.ppo_num_envs),
        "--ppo-num-evals",
        str(args.ppo_num_evals),
        "--ppo-episode-length",
        str(args.ppo_episode_length),
        "--ppo-unroll-length",
        str(args.ppo_unroll_length),
        "--ppo-batch-size",
        str(args.ppo_batch_size),
        "--ppo-num-minibatches",
        str(args.ppo_num_minibatches),
        "--ppo-num-updates-per-batch",
        str(args.ppo_num_updates_per_batch),
        "--enable-behavior-prior",
        "--behavior-prior-mlp-npz",
        args.behavior_prior_mlp_npz,
        "--behavior-prior-scale",
        cli(stage["behavior_prior_scale"]),
        "--actuator-bridge-delay-min-ticks",
        str(stage["bridge"]["delay_ticks"][0]),
        "--actuator-bridge-delay-max-ticks",
        str(stage["bridge"]["delay_ticks"][1]),
        "--actuator-bridge-tau-min-s",
        cli(stage["bridge"]["tau_s"][0]),
        "--actuator-bridge-tau-max-s",
        cli(stage["bridge"]["tau_s"][1]),
        "--actuator-bridge-velocity-limit-min-rad-s",
        cli(stage["bridge"]["velocity_limit_rad_s"][0]),
        "--actuator-bridge-velocity-limit-max-rad-s",
        cli(stage["bridge"]["velocity_limit_rad_s"][1]),
        "--actuator-bridge-per-joint-variation",
        cli(stage["bridge"]["per_joint_variation"]),
        "--lin-vel-x-min",
        "0.06",
        "--lin-vel-x-max",
        "0.10",
        "--lin-vel-y-min",
        "0.0",
        "--lin-vel-y-max",
        "0.0",
        "--ang-vel-yaw-min",
        "0.0",
        "--ang-vel-yaw-max",
        "0.0",
        "--zero-command-probability",
        "0.15",
        "--command-resample-steps",
        "600",
        "--target-rate-scale",
        "-0.04",
        "--target-rate-huber-delta",
        "0.08",
        "--actuator-tracking-scale",
        "-0.03",
        "--actuator-tracking-huber-delta",
        "0.04",
        "--action-rate-scale",
        "-0.12",
        "--action-rate-huber-delta",
        "0.05",
        "--action-magnitude-scale",
        "-0.01",
        "--forward-progress-scale",
        "2.0",
        "--command-progress-scale",
        "1.0",
        "--command-progress-shortfall-scale",
        "-2.0",
        "--command-progress-required-ratio",
        "0.35",
        "--command-progress-warmup-steps",
        "30",
        "--forward-pitch-scale",
        "-0.4",
        "--forward-pitch-rate-scale",
        "-0.08",
        "--base-height-scale",
        "-0.3",
        "--imitation-scale",
        "0.0",
        "--alive-scale",
        "2.0",
    ]
    if args.restore_checkpoint:
        command.extend(["--restore-checkpoint-path", args.restore_checkpoint])
        command.extend(["--restore-policy-kl-scale", cli(stage["restore_policy_kl_scale"])])
    if args.jax_platforms:
        command.extend(["--jax-platforms", args.jax_platforms])
    return command


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    policy = Path(args.policy)
    fit_json = Path(args.fit_json)
    checkpoint = Path(args.restore_checkpoint) if args.restore_checkpoint else None
    behavior_prior = Path(args.behavior_prior_mlp_npz)

    warmstart_status = (
        "PASS_TRAINABLE_WARMSTART"
        if checkpoint is not None and checkpoint.exists()
        else "HOLD_TRAINABLE_WARMSTART_CHECKPOINT_MISSING"
    )

    stages = [
        {
            "id": "stage_a_narrow_flat_no_push",
            "purpose": "preserve Phase 1 gait under weak randomization on flat terrain",
            "task": "flat_terrain_backlash",
            "num_timesteps": args.stage_timesteps,
            "friction": [0.7, 1.0],
            "mass_scale": [0.97, 1.03],
            "com_offset_m": [-0.015, 0.015],
            "push": {"enabled": False, "magnitude": [0.0, 0.0]},
            "terrain": "flat",
            "bridge": {
                "delay_ticks": [3, 4],
                "tau_s": [0.06, 0.10],
                "velocity_limit_rad_s": [2.0, 3.25],
                "per_joint_variation": 0.05,
            },
            "behavior_prior_scale": -0.08,
            "restore_policy_kl_scale": 0.05,
        },
        {
            "id": "stage_b_full_flat_gentle_push",
            "purpose": "full physics randomization on flat terrain with gentle push perturbations",
            "task": "flat_terrain_backlash",
            "num_timesteps": args.stage_timesteps,
            "friction": [0.5, 1.25],
            "mass_scale": [0.9, 1.1],
            "com_offset_m": [-0.03, 0.03],
            "push": {"enabled": True, "magnitude": [0.05, 0.25]},
            "terrain": "flat",
            "bridge": {
                "delay_ticks": [3, 5],
                "tau_s": [0.06, 0.14],
                "velocity_limit_rad_s": [2.0, 3.25],
                "per_joint_variation": 0.10,
            },
            "behavior_prior_scale": -0.06,
            "restore_policy_kl_scale": 0.03,
        },
        {
            "id": "stage_c_rough_gentle_push",
            "purpose": "introduce existing rough hfield terrain after flat robustness passes",
            "task": "rough_terrain_backlash",
            "num_timesteps": args.stage_timesteps,
            "friction": [0.5, 1.25],
            "mass_scale": [0.9, 1.1],
            "com_offset_m": [-0.03, 0.03],
            "push": {"enabled": True, "magnitude": [0.05, 0.35]},
            "terrain": "existing hfield rough terrain",
            "bridge": {
                "delay_ticks": [3, 5],
                "tau_s": [0.06, 0.14],
                "velocity_limit_rad_s": [2.0, 3.25],
                "per_joint_variation": 0.10,
            },
            "behavior_prior_scale": -0.05,
            "restore_policy_kl_scale": 0.02,
        },
        {
            "id": "stage_d_rough_stronger_push",
            "purpose": "final robustness stage with stronger perturbations, still in corrected envelope",
            "task": "rough_terrain_backlash",
            "num_timesteps": args.stage_timesteps,
            "friction": [0.5, 1.25],
            "mass_scale": [0.9, 1.1],
            "com_offset_m": [-0.04, 0.04],
            "push": {"enabled": True, "magnitude": [0.1, 0.6]},
            "terrain": "existing hfield rough terrain",
            "bridge": {
                "delay_ticks": [3, 6],
                "tau_s": [0.06, 0.14],
                "velocity_limit_rad_s": [2.0, 3.25],
                "per_joint_variation": 0.12,
            },
            "behavior_prior_scale": -0.04,
            "restore_policy_kl_scale": 0.015,
        },
    ]

    output_root = Path(args.output_root)
    commands = {}
    for stage in stages:
        command = stage_command(args, stage, output_root)
        stage["command"] = command
        stage["command_shell"] = shell_join(command)
        commands[stage["id"]] = command

    return {
        "status": "HOLD_PHASE2_PLAN_BLOCKED" if warmstart_status.startswith("HOLD") else "READY_DRY_RUN",
        "reason": (
            "Phase 2 requires a true trainable warm-start from the Phase 1 policy. "
            "Current artifact is ONNX/BC NPZ, while PPO restore expects an Orbax checkpoint."
            if warmstart_status.startswith("HOLD")
            else "Trainable checkpoint exists; generated commands remain dry-run until invoked explicitly."
        ),
        "policy": {"path": str(policy), "sha256": sha256(policy)},
        "fit_json": {"path": str(fit_json), "sha256": sha256(fit_json)},
        "behavior_prior_mlp_npz": {
            "path": str(behavior_prior),
            "exists": behavior_prior.exists(),
            "sha256": sha256(behavior_prior),
        },
        "restore_checkpoint": {
            "path": str(checkpoint) if checkpoint else None,
            "exists": checkpoint.exists() if checkpoint else False,
        },
        "warmstart_status": warmstart_status,
        "corrected_envelope_gate": {
            "left_hip_pitch": 2.50,
            "left_knee": 3.25,
            "left_ankle": 2.75,
            "right_hip_pitch": 2.25,
            "right_knee": 2.75,
            "right_ankle": 2.00,
        },
        "acceptance_gate": {
            "x0.08": {
                "seeds": 8,
                "falls": 0,
                "corrected_velocity_excess": 0.0,
                "tracking_p95_max_rad": 0.20,
                "track_ratio_min": 0.40,
            },
            "x0.0": {
                "seeds": 8,
                "falls": 0,
                "mean_abs_vx_max_m_s": 0.005,
            },
            "additional_reports": [
                "mean speed",
                "track ratio",
                "push-recovery success",
                "terrain success",
                "foot clearance / swing peak",
            ],
        },
        "stages": stages,
        "missing_implementation": [
            "true trainable warm-start checkpoint or verified ONNX/NPZ-to-PPO conversion",
            "CLI-configurable friction/mass/COM/push/noise randomization ranges in Playground",
            "leg-length / geometry jitter hook",
            "stage-gated automation that advances only after corrected-bridge gates pass",
        ],
    }


def write_md(plan: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Domain-Randomized Robustness Plan",
        "",
        f"status: `{plan['status']}`",
        f"warmstart_status: `{plan['warmstart_status']}`",
        "",
        plan["reason"],
        "",
        "This plan is offline-only. It does not SSH, deploy, move the robot, or",
        "start training by itself.",
        "",
        "## Locked Inputs",
        "",
        f"- policy: `{plan['policy']['path']}`",
        f"- policy_sha256: `{plan['policy']['sha256']}`",
        f"- corrected_bridge: `{plan['fit_json']['path']}`",
        f"- corrected_bridge_sha256: `{plan['fit_json']['sha256']}`",
        f"- behavior_prior_mlp_npz: `{plan['behavior_prior_mlp_npz']['path']}`",
        f"- behavior_prior_mlp_npz_sha256: `{plan['behavior_prior_mlp_npz']['sha256']}`",
        "",
        "## Blocking Warm-Start Note",
        "",
        "The existing Playground PPO path restores from an Orbax checkpoint. The",
        "Phase 1 candidate is currently preserved as ONNX plus BC MLP NPZ. Using",
        "the NPZ as a frozen behavior prior is useful, but it is not the same as",
        "warm-starting trainable PPO parameters. Do not launch Phase 2 as a scratch",
        "run.",
        "",
        "## Stages",
        "",
        "| stage | task | friction | mass | COM | push | bridge velocity | purpose |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for stage in plan["stages"]:
        lines.append(
            f"| `{stage['id']}` | `{stage['task']}` | `{stage['friction']}` | "
            f"`{stage['mass_scale']}` | `{stage['com_offset_m']}` | "
            f"`{stage['push']}` | `{stage['bridge']['velocity_limit_rad_s']}` | "
            f"{stage['purpose']} |"
        )
    lines.extend(["", "## Commands", ""])
    for stage in plan["stages"]:
        lines.extend(
            [
                f"### {stage['id']}",
                "",
                "```bash",
                stage["command_shell"],
                "```",
                "",
            ]
        )
    lines.extend(["## Missing Implementation", ""])
    lines.extend(f"- {item}" for item in plan["missing_implementation"])
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "Each stage must pass corrected-bridge seed gates before the next stage:",
            "",
            "- `x=0.08`: 8/8 seeds, no falls, zero corrected velocity excess,",
            "  max pitch-chain tracking p95 <= 0.20 rad, track ratio >= 0.40",
            "- `x=0.0`: 8/8 seeds, no falls, mean |vx| <= 0.005 m/s",
            "- report mean speed, track ratio, push recovery, terrain success, and",
            "  foot clearance / swing peak",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--fit-json", default=str(DEFAULT_FIT))
    parser.add_argument(
        "--behavior-prior-mlp-npz",
        default=str(
            ROOT
            / "outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz"
        ),
    )
    parser.add_argument("--restore-checkpoint", default=None)
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--env-python", default=str(DEFAULT_ENV_PYTHON))
    parser.add_argument("--output-root", default="outputs/phase2_domain_randomization")
    parser.add_argument("--platform", choices=["cpu", "gpu"], default="gpu")
    parser.add_argument("--jax-platforms", default="cuda")
    parser.add_argument("--stage-timesteps", type=int, default=1_000_000)
    parser.add_argument("--export-min-step", type=int, default=100_000)
    parser.add_argument("--ppo-num-envs", type=int, default=512)
    parser.add_argument("--ppo-num-evals", type=int, default=8)
    parser.add_argument("--ppo-episode-length", type=int, default=750)
    parser.add_argument("--ppo-unroll-length", type=int, default=20)
    parser.add_argument("--ppo-batch-size", type=int, default=4096)
    parser.add_argument("--ppo-num-minibatches", type=int, default=8)
    parser.add_argument("--ppo-num-updates-per-batch", type=int, default=4)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    plan = build_plan(args)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    write_md(plan, output_md)
    print(plan["status"])
    print(plan["warmstart_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
