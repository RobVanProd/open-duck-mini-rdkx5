#!/usr/bin/env python3
"""Launch or print a tiny Open Duck actuator-bridge PPO smoke run.

This helper is offline-only. It does not touch the robot, SSH, deploy files, or
produce a deployable policy. By default it prints the exact command and exits.
Pass --run to execute the small smoke training command.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs/open-duck-playground/bin/python"
DEFAULT_OUTPUT_ROOT = Path("/tmp/open_duck_actuator_bridge_smoke")
REFERENCE_RELATIVE_PATH = Path(
    "playground/open_duck_mini_v2/data/polynomial_coefficients.pkl"
)


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def cli_value(value: Any) -> str:
    """Format values so argparse never mistakes negative floats for flags."""
    if isinstance(value, float):
        return format(value, ".12f").rstrip("0").rstrip(".")
    return str(value)


def append_optional(command: list[str], flag: str, value: Any) -> None:
    if value is not None:
        command.extend([flag, cli_value(value)])


def build_command(args: argparse.Namespace, output_dir: Path) -> list[str]:
    runner = Path(args.playground_path) / "playground/open_duck_mini_v2/runner.py"
    command = [
        str(Path(args.env_python)),
        str(runner),
        "--task",
        args.task,
        "--env",
        args.env,
        "--output_dir",
        str(output_dir),
        "--export_min_step",
        str(args.export_min_step),
        "--num_timesteps",
        str(args.num_timesteps),
        "--ppo_num_envs",
        str(args.ppo_num_envs),
        "--ppo_num_evals",
        str(args.ppo_num_evals),
        "--ppo_episode_length",
        str(args.ppo_episode_length),
        "--ppo_unroll_length",
        str(args.ppo_unroll_length),
        "--ppo_batch_size",
        str(args.ppo_batch_size),
        "--ppo_num_minibatches",
        str(args.ppo_num_minibatches),
        "--ppo_num_updates_per_batch",
        str(args.ppo_num_updates_per_batch),
        "--target_rate_scale",
        cli_value(args.target_rate_scale),
        "--actuator_tracking_scale",
        cli_value(args.actuator_tracking_scale),
    ]
    append_optional(command, "--restore_checkpoint_path", args.restore_checkpoint_path)
    optional_ppo_overrides = {
        "--ppo_learning_rate": args.ppo_learning_rate,
        "--ppo_entropy_cost": args.ppo_entropy_cost,
        "--ppo_clipping_epsilon": args.ppo_clipping_epsilon,
        "--ppo_max_grad_norm": args.ppo_max_grad_norm,
    }
    for flag, value in optional_ppo_overrides.items():
        append_optional(command, flag, value)
    optional_runner_overrides = {
        "--tracking_lin_vel_scale": args.tracking_lin_vel_scale,
        "--tracking_ang_vel_scale": args.tracking_ang_vel_scale,
        "--tracking_sigma": args.tracking_sigma,
        "--forward_progress_scale": args.forward_progress_scale,
        "--forward_shortfall_scale": args.forward_shortfall_scale,
        "--forward_overshoot_scale": args.forward_overshoot_scale,
        "--forward_wrong_direction_scale": args.forward_wrong_direction_scale,
        "--forward_progress_deadband": args.forward_progress_deadband,
        "--forward_shortfall_required_ratio": args.forward_shortfall_required_ratio,
        "--forward_overshoot_allowed_ratio": args.forward_overshoot_allowed_ratio,
        "--forward_wrong_direction_allowed_reverse_ratio": (
            args.forward_wrong_direction_allowed_reverse_ratio
        ),
        "--command_progress_scale": args.command_progress_scale,
        "--command_progress_shortfall_scale": args.command_progress_shortfall_scale,
        "--command_progress_failure_scale": args.command_progress_failure_scale,
        "--command_progress_required_ratio": args.command_progress_required_ratio,
        "--command_progress_warmup_steps": args.command_progress_warmup_steps,
        "--command_progress_failure_min_ratio": (
            args.command_progress_failure_min_ratio
        ),
        "--command_progress_failure_warmup_steps": (
            args.command_progress_failure_warmup_steps
        ),
        "--action_rate_huber_delta": args.action_rate_huber_delta,
        "--action_magnitude_huber_delta": args.action_magnitude_huber_delta,
        "--target_rate_huber_delta": args.target_rate_huber_delta,
        "--actuator_tracking_huber_delta": args.actuator_tracking_huber_delta,
        "--forward_shortfall_huber_delta": args.forward_shortfall_huber_delta,
        "--forward_overshoot_huber_delta": args.forward_overshoot_huber_delta,
        "--forward_wrong_direction_huber_delta": (
            args.forward_wrong_direction_huber_delta
        ),
        "--forward_pitch_huber_delta": args.forward_pitch_huber_delta,
        "--forward_pitch_rate_huber_delta": args.forward_pitch_rate_huber_delta,
        "--command_progress_shortfall_huber_delta": (
            args.command_progress_shortfall_huber_delta
        ),
        "--reward_clip_min": args.reward_clip_min,
        "--reward_clip_max": args.reward_clip_max,
        "--action_rate_scale": args.action_rate_scale,
        "--action_magnitude_scale": args.action_magnitude_scale,
        "--stand_still_scale": args.stand_still_scale,
        "--orientation_scale": args.orientation_scale,
        "--base_height_scale": args.base_height_scale,
        "--forward_pitch_scale": args.forward_pitch_scale,
        "--forward_pitch_rate_scale": args.forward_pitch_rate_scale,
        "--forward_contact_support_scale": args.forward_contact_support_scale,
        "--forward_contact_support_no_contact_weight": (
            args.forward_contact_support_no_contact_weight
        ),
        "--forward_contact_support_asymmetry_weight": (
            args.forward_contact_support_asymmetry_weight
        ),
        "--alive_scale": args.alive_scale,
        "--imitation_scale": args.imitation_scale,
        "--lin_vel_x_min": args.lin_vel_x_min,
        "--lin_vel_x_max": args.lin_vel_x_max,
        "--lin_vel_y_min": args.lin_vel_y_min,
        "--lin_vel_y_max": args.lin_vel_y_max,
        "--ang_vel_yaw_min": args.ang_vel_yaw_min,
        "--ang_vel_yaw_max": args.ang_vel_yaw_max,
        "--command_resample_steps": args.command_resample_steps,
        "--zero_command_probability": args.zero_command_probability,
        "--head_range_factor": args.head_range_factor,
    }
    for flag, value in optional_runner_overrides.items():
        append_optional(command, flag, value)
    if args.command_progress_failure_enable:
        command.append("--command_progress_failure_enable")
    if not args.disable_actuator_bridge:
        command.append("--enable_actuator_bridge")
        command.extend(
            [
                "--actuator_bridge_delay_min_ticks",
                str(args.actuator_bridge_delay_min_ticks),
                "--actuator_bridge_delay_max_ticks",
                str(args.actuator_bridge_delay_max_ticks),
                "--actuator_bridge_tau_min_s",
                cli_value(args.actuator_bridge_tau_min_s),
                "--actuator_bridge_tau_max_s",
                cli_value(args.actuator_bridge_tau_max_s),
                "--actuator_bridge_velocity_limit_min_rad_s",
                cli_value(args.actuator_bridge_velocity_limit_min_rad_s),
                "--actuator_bridge_velocity_limit_max_rad_s",
                cli_value(args.actuator_bridge_velocity_limit_max_rad_s),
                "--actuator_bridge_per_joint_variation",
                cli_value(args.actuator_bridge_per_joint_variation),
            ]
        )
    return command


def validate_paths(args: argparse.Namespace) -> None:
    playground = Path(args.playground_path)
    env_python = Path(args.env_python)
    runner = playground / "playground/open_duck_mini_v2/runner.py"
    joystick = playground / "playground/open_duck_mini_v2/joystick.py"

    missing = [
        str(path)
        for path in (playground, env_python, runner, joystick)
        if not path.exists()
    ]
    if missing:
        raise SystemExit("Missing required path(s):\n" + "\n".join(missing))


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_reference_override(args: argparse.Namespace, output_dir: Path) -> dict[str, Any]:
    if not args.reference_motion_override:
        return {"enabled": False}

    source = Path(args.reference_motion_override)
    if not source.is_absolute() and not source.exists():
        source = ROOT / source
    if not source.exists():
        raise SystemExit(f"Missing reference motion override: {source}")
    destination = Path(args.playground_path) / REFERENCE_RELATIVE_PATH
    if not destination.exists():
        raise SystemExit(f"Missing Playground reference file: {destination}")

    backup = output_dir / "polynomial_coefficients.original.pkl"
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(destination, backup)
    before_sha = sha256(destination)
    source_sha = sha256(source)
    shutil.copy2(source, destination)
    after_sha = sha256(destination)
    return {
        "enabled": True,
        "source": str(source),
        "source_sha256": source_sha,
        "destination": str(destination),
        "destination_sha256_before": before_sha,
        "destination_sha256_after": after_sha,
        "backup": str(backup),
        "backup_sha256": sha256(backup),
        "restored": False,
    }


def restore_reference_override(reference_override: dict[str, Any]) -> dict[str, Any]:
    if not reference_override.get("enabled"):
        return reference_override
    backup = Path(reference_override["backup"])
    destination = Path(reference_override["destination"])
    shutil.copy2(backup, destination)
    reference_override["restored"] = True
    reference_override["destination_sha256_restored"] = sha256(destination)
    return reference_override


def extract_summary(stdout: str) -> dict[str, Any]:
    step_lines = [line for line in stdout.splitlines() if line.startswith("STEP:")]
    export_lines = [
        line for line in stdout.splitlines() if "Model exported to" in line
    ]
    checkpoint_lines = [
        line
        for line in stdout.splitlines()
        if "Checkpoint saved at" in line or "checkpoint" in line.lower()
    ]
    return {
        "step_lines": step_lines[-10:],
        "export_lines": export_lines[-10:],
        "checkpoint_lines": checkpoint_lines[-10:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print or run a tiny actuator-bridge PPO smoke command."
    )
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--env-python", default=str(DEFAULT_ENV_PYTHON))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--run", action="store_true", help="Execute the smoke run.")
    parser.add_argument("--platform", choices=["cpu", "gpu"], default="cpu")
    parser.add_argument(
        "--jax-platforms",
        default=None,
        help=(
            "Optional JAX_PLATFORMS override. Use cpu for local CPU-only runs, "
            "cuda for NVIDIA/Colab GPU, and rocm for ROCm. If omitted, CPU "
            "runs force cpu and GPU runs leave JAX_PLATFORMS unset."
        ),
    )
    parser.add_argument("--timeout-s", type=int, default=900)
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--env", default="joystick")
    parser.add_argument("--num-timesteps", type=int, default=256)
    parser.add_argument(
        "--export-min-step",
        type=int,
        default=0,
        help=(
            "Pass through to runner.py --export_min_step. A value above 0 skips "
            "the step-0 checkpoint/ONNX export."
        ),
    )
    parser.add_argument("--ppo-num-envs", type=int, default=16)
    parser.add_argument("--ppo-num-evals", type=int, default=1)
    parser.add_argument("--ppo-episode-length", type=int, default=100)
    parser.add_argument("--ppo-unroll-length", type=int, default=5)
    parser.add_argument("--ppo-batch-size", type=int, default=16)
    parser.add_argument("--ppo-num-minibatches", type=int, default=1)
    parser.add_argument("--ppo-num-updates-per-batch", type=int, default=1)
    parser.add_argument("--ppo-learning-rate", type=float, default=None)
    parser.add_argument("--ppo-entropy-cost", type=float, default=None)
    parser.add_argument("--ppo-clipping-epsilon", type=float, default=None)
    parser.add_argument("--ppo-max-grad-norm", type=float, default=None)
    parser.add_argument(
        "--restore-checkpoint-path",
        default=None,
        help=(
            "Optional Orbax checkpoint path to pass through to the Playground "
            "runner for offline fine-tuning. The path must exist in the "
            "execution environment."
        ),
    )
    parser.add_argument(
        "--reference-motion-override",
        default=None,
        help=(
            "Optional training-only polynomial_coefficients.pkl override. The "
            "wrapper backs up the Playground reference file, copies this file "
            "before training, records hashes, and restores the original after "
            "the run. Default is unchanged behavior."
        ),
    )
    parser.add_argument("--disable-actuator-bridge", action="store_true")
    parser.add_argument("--actuator-bridge-delay-min-ticks", type=int, default=3)
    parser.add_argument("--actuator-bridge-delay-max-ticks", type=int, default=8)
    parser.add_argument("--actuator-bridge-tau-min-s", type=float, default=0.06)
    parser.add_argument("--actuator-bridge-tau-max-s", type=float, default=0.14)
    parser.add_argument(
        "--actuator-bridge-velocity-limit-min-rad-s", type=float, default=2.5
    )
    parser.add_argument(
        "--actuator-bridge-velocity-limit-max-rad-s", type=float, default=4.7
    )
    parser.add_argument("--actuator-bridge-per-joint-variation", type=float, default=0.15)
    parser.add_argument(
        "--target-rate-scale",
        type=float,
        default=0.0,
        help=(
            "Scale applied to the target-velocity cost. Use a negative value "
            "to penalize target velocity; positive values reward the cost."
        ),
    )
    parser.add_argument(
        "--actuator-tracking-scale",
        type=float,
        default=0.0,
        help=(
            "Scale applied to the sent-vs-applied actuator tracking cost. Use "
            "a negative value to penalize tracking error; positive values "
            "reward the cost."
        ),
    )
    parser.add_argument("--tracking-lin-vel-scale", type=float, default=None)
    parser.add_argument("--tracking-ang-vel-scale", type=float, default=None)
    parser.add_argument("--tracking-sigma", type=float, default=None)
    parser.add_argument("--forward-progress-scale", type=float, default=None)
    parser.add_argument("--forward-shortfall-scale", type=float, default=None)
    parser.add_argument("--forward-progress-deadband", type=float, default=None)
    parser.add_argument("--forward-shortfall-required-ratio", type=float, default=None)
    parser.add_argument("--forward-overshoot-scale", type=float, default=None)
    parser.add_argument("--forward-overshoot-allowed-ratio", type=float, default=None)
    parser.add_argument("--forward-wrong-direction-scale", type=float, default=None)
    parser.add_argument(
        "--forward-wrong-direction-allowed-reverse-ratio", type=float, default=None
    )
    parser.add_argument("--command-progress-scale", type=float, default=None)
    parser.add_argument("--command-progress-shortfall-scale", type=float, default=None)
    parser.add_argument("--command-progress-failure-scale", type=float, default=None)
    parser.add_argument("--command-progress-required-ratio", type=float, default=None)
    parser.add_argument("--command-progress-warmup-steps", type=int, default=None)
    parser.add_argument(
        "--command-progress-failure-enable",
        action="store_true",
        help=(
            "Enable default-off termination for positive-command episodes that "
            "remain below the command-progress floor after warmup."
        ),
    )
    parser.add_argument(
        "--command-progress-failure-min-ratio", type=float, default=None
    )
    parser.add_argument(
        "--command-progress-failure-warmup-steps", type=int, default=None
    )
    parser.add_argument("--action-rate-huber-delta", type=float, default=None)
    parser.add_argument("--action-magnitude-huber-delta", type=float, default=None)
    parser.add_argument("--target-rate-huber-delta", type=float, default=None)
    parser.add_argument("--actuator-tracking-huber-delta", type=float, default=None)
    parser.add_argument("--forward-shortfall-huber-delta", type=float, default=None)
    parser.add_argument("--forward-overshoot-huber-delta", type=float, default=None)
    parser.add_argument("--forward-wrong-direction-huber-delta", type=float, default=None)
    parser.add_argument("--forward-pitch-huber-delta", type=float, default=None)
    parser.add_argument("--forward-pitch-rate-huber-delta", type=float, default=None)
    parser.add_argument(
        "--command-progress-shortfall-huber-delta", type=float, default=None
    )
    parser.add_argument("--reward-clip-min", type=float, default=None)
    parser.add_argument("--reward-clip-max", type=float, default=None)
    parser.add_argument("--action-rate-scale", type=float, default=None)
    parser.add_argument("--action-magnitude-scale", type=float, default=None)
    parser.add_argument("--stand-still-scale", type=float, default=None)
    parser.add_argument("--orientation-scale", type=float, default=None)
    parser.add_argument("--base-height-scale", type=float, default=None)
    parser.add_argument("--forward-pitch-scale", type=float, default=None)
    parser.add_argument("--forward-pitch-rate-scale", type=float, default=None)
    parser.add_argument("--forward-contact-support-scale", type=float, default=None)
    parser.add_argument(
        "--forward-contact-support-no-contact-weight", type=float, default=None
    )
    parser.add_argument(
        "--forward-contact-support-asymmetry-weight", type=float, default=None
    )
    parser.add_argument("--alive-scale", type=float, default=None)
    parser.add_argument("--imitation-scale", type=float, default=None)
    parser.add_argument("--lin-vel-x-min", type=float, default=None)
    parser.add_argument("--lin-vel-x-max", type=float, default=None)
    parser.add_argument("--lin-vel-y-min", type=float, default=None)
    parser.add_argument("--lin-vel-y-max", type=float, default=None)
    parser.add_argument("--ang-vel-yaw-min", type=float, default=None)
    parser.add_argument("--ang-vel-yaw-max", type=float, default=None)
    parser.add_argument("--command-resample-steps", type=int, default=None)
    parser.add_argument("--zero-command-probability", type=float, default=None)
    parser.add_argument("--head-range-factor", type=float, default=None)
    args = parser.parse_args()

    validate_paths(args)

    output_root = Path(args.output_root)
    output_dir = output_root / f"smoke_{timestamp()}_{args.platform}"
    command = build_command(args, output_dir)
    env = os.environ.copy()
    env["JAX_PLATFORM_NAME"] = args.platform
    jax_platforms = args.jax_platforms
    if jax_platforms is None and args.platform == "cpu":
        jax_platforms = "cpu"
    if jax_platforms:
        env["JAX_PLATFORMS"] = jax_platforms
    else:
        env.pop("JAX_PLATFORMS", None)
    env["PYTHONUNBUFFERED"] = "1"

    manifest: dict[str, Any] = {
        "status": "RUN_PLANNED" if args.run else "DRY_RUN",
        "purpose": "offline actuator bridge PPO smoke; not a deployable policy",
        "timestamp": timestamp(),
        "playground_path": str(Path(args.playground_path).resolve()),
        "env_python_configured": str(Path(args.env_python)),
        "env_python_resolved": str(Path(args.env_python).resolve()),
        "output_dir": str(output_dir),
        "platform": args.platform,
        "jax_platform_env": {
            "JAX_PLATFORM_NAME": env["JAX_PLATFORM_NAME"],
            "JAX_PLATFORMS": env.get("JAX_PLATFORMS"),
        },
        "timeout_s": args.timeout_s,
        "export_min_step": args.export_min_step,
        "actuator_bridge_enabled": not args.disable_actuator_bridge,
        "restore_checkpoint_path": args.restore_checkpoint_path,
        "reference_motion_override": {
            "enabled": bool(args.reference_motion_override),
            "source": args.reference_motion_override,
        },
        "target_rate_scale": args.target_rate_scale,
        "actuator_tracking_scale": args.actuator_tracking_scale,
        "ppo_overrides": {
            "learning_rate": args.ppo_learning_rate,
            "entropy_cost": args.ppo_entropy_cost,
            "clipping_epsilon": args.ppo_clipping_epsilon,
            "max_grad_norm": args.ppo_max_grad_norm,
        },
        "training_recipe_overrides": {
            "tracking_lin_vel_scale": args.tracking_lin_vel_scale,
            "tracking_ang_vel_scale": args.tracking_ang_vel_scale,
            "tracking_sigma": args.tracking_sigma,
            "forward_progress_scale": args.forward_progress_scale,
            "forward_progress_deadband": args.forward_progress_deadband,
            "forward_shortfall_scale": args.forward_shortfall_scale,
            "forward_shortfall_required_ratio": args.forward_shortfall_required_ratio,
            "forward_overshoot_scale": args.forward_overshoot_scale,
            "forward_overshoot_allowed_ratio": args.forward_overshoot_allowed_ratio,
            "forward_wrong_direction_scale": args.forward_wrong_direction_scale,
            "forward_wrong_direction_allowed_reverse_ratio": (
                args.forward_wrong_direction_allowed_reverse_ratio
            ),
            "command_progress_scale": args.command_progress_scale,
            "command_progress_shortfall_scale": args.command_progress_shortfall_scale,
            "command_progress_failure_scale": args.command_progress_failure_scale,
            "command_progress_required_ratio": args.command_progress_required_ratio,
            "command_progress_warmup_steps": args.command_progress_warmup_steps,
            "command_progress_failure_enable": args.command_progress_failure_enable,
            "command_progress_failure_min_ratio": (
                args.command_progress_failure_min_ratio
            ),
            "command_progress_failure_warmup_steps": (
                args.command_progress_failure_warmup_steps
            ),
            "action_rate_huber_delta": args.action_rate_huber_delta,
            "action_magnitude_huber_delta": args.action_magnitude_huber_delta,
            "target_rate_huber_delta": args.target_rate_huber_delta,
            "actuator_tracking_huber_delta": args.actuator_tracking_huber_delta,
            "forward_shortfall_huber_delta": args.forward_shortfall_huber_delta,
            "forward_overshoot_huber_delta": args.forward_overshoot_huber_delta,
            "forward_wrong_direction_huber_delta": (
                args.forward_wrong_direction_huber_delta
            ),
            "forward_pitch_huber_delta": args.forward_pitch_huber_delta,
            "forward_pitch_rate_huber_delta": args.forward_pitch_rate_huber_delta,
            "command_progress_shortfall_huber_delta": (
                args.command_progress_shortfall_huber_delta
            ),
            "reward_clip_min": args.reward_clip_min,
            "reward_clip_max": args.reward_clip_max,
            "action_rate_scale": args.action_rate_scale,
            "action_magnitude_scale": args.action_magnitude_scale,
            "stand_still_scale": args.stand_still_scale,
            "orientation_scale": args.orientation_scale,
            "base_height_scale": args.base_height_scale,
            "forward_pitch_scale": args.forward_pitch_scale,
            "forward_pitch_rate_scale": args.forward_pitch_rate_scale,
            "forward_contact_support_scale": args.forward_contact_support_scale,
            "forward_contact_support_no_contact_weight": (
                args.forward_contact_support_no_contact_weight
            ),
            "forward_contact_support_asymmetry_weight": (
                args.forward_contact_support_asymmetry_weight
            ),
            "alive_scale": args.alive_scale,
            "imitation_scale": args.imitation_scale,
            "lin_vel_x_min": args.lin_vel_x_min,
            "lin_vel_x_max": args.lin_vel_x_max,
            "lin_vel_y_min": args.lin_vel_y_min,
            "lin_vel_y_max": args.lin_vel_y_max,
            "ang_vel_yaw_min": args.ang_vel_yaw_min,
            "ang_vel_yaw_max": args.ang_vel_yaw_max,
            "command_resample_steps": args.command_resample_steps,
            "zero_command_probability": args.zero_command_probability,
            "head_range_factor": args.head_range_factor,
        },
        "command": command,
        "command_shell": (
            f"JAX_PLATFORM_NAME={env['JAX_PLATFORM_NAME']} "
            f"JAX_PLATFORMS={env.get('JAX_PLATFORMS', '')} "
            f"{shell_join(command)}"
        ),
        "robot_touched": False,
        "deploy_performed": False,
    }

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if not args.run:
        print("\nDry-run only. Pass --run to execute this tiny smoke command.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    reference_override = apply_reference_override(args, output_dir)
    manifest["reference_motion_override"] = reference_override
    write_manifest(output_dir / "smoke_manifest.start.json", manifest)

    start_s = time.monotonic()
    stdout_path = output_dir / "stdout.txt"
    stderr_path = output_dir / "stderr.txt"
    try:
        with stdout_path.open("w") as stdout_handle, stderr_path.open(
            "w"
        ) as stderr_handle:
            process = subprocess.Popen(
                command,
                cwd=Path(args.playground_path),
                env=env,
                text=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
            )
            try:
                returncode = process.wait(timeout=args.timeout_s)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise
    finally:
        reference_override = restore_reference_override(reference_override)
    elapsed_s = time.monotonic() - start_s
    stdout_text = stdout_path.read_text(errors="replace")

    manifest.update(
        {
            "status": "PASS_SMOKE_RUN" if returncode == 0 else "HOLD_SMOKE_RUN",
            "returncode": returncode,
            "elapsed_s": elapsed_s,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "reference_motion_override": reference_override,
            "summary": extract_summary(stdout_text),
        }
    )
    write_manifest(output_dir / "smoke_manifest.final.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as exc:
        print(f"HOLD_SMOKE_TIMEOUT: timed out after {exc.timeout}s", file=sys.stderr)
        raise SystemExit(124) from exc
