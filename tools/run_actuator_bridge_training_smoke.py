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
import re
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
TASK_XML_RELATIVE_PATHS = {
    "flat_terrain": Path("playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml"),
    "rough_terrain": Path("playground/open_duck_mini_v2/xmls/scene_rough_terrain.xml"),
    "flat_terrain_backlash": Path(
        "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    ),
    "rough_terrain_backlash": Path(
        "playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml"
    ),
}


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def env_shell_prefix(env_set: dict[str, str], env_unset: list[str]) -> str:
    parts = ["env"]
    for name in env_unset:
        parts.extend(["-u", name])
    parts.extend(f"{name}={value}" for name, value in env_set.items())
    return shell_join(parts)


def cli_value(value: Any) -> str:
    """Format values so argparse never mistakes negative floats for flags."""
    if isinstance(value, float):
        return format(value, ".12f").rstrip("0").rstrip(".")
    return str(value)


def append_optional(command: list[str], flag: str, value: Any) -> None:
    if value is not None:
        command.extend([flag, cli_value(value)])


def resolve_rdk_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    if path.exists():
        return path.resolve()
    return (ROOT / path).resolve()


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
        "--ppo_desired_kl": args.ppo_desired_kl,
        "--ppo_learning_rate_schedule": args.ppo_learning_rate_schedule,
        "--ppo_learning_rate_schedule_min_lr": args.ppo_learning_rate_schedule_min_lr,
        "--ppo_learning_rate_schedule_max_lr": args.ppo_learning_rate_schedule_max_lr,
        "--restore_policy_kl_scale": args.restore_policy_kl_scale,
    }
    for flag, value in optional_ppo_overrides.items():
        append_optional(command, flag, value)
    optional_policy_network_overrides = {
        "--ppo_policy_network": args.ppo_policy_network,
        "--phase_modulated_policy_hidden_sizes": args.phase_modulated_policy_hidden_sizes,
        "--phase_modulated_context_hidden_sizes": args.phase_modulated_context_hidden_sizes,
        "--phase_modulated_context_indices": args.phase_modulated_context_indices,
        "--phase_modulated_activation": args.phase_modulated_activation,
        "--phase_modulated_scale": args.phase_modulated_scale,
        "--phase_modulated_init_scale_logit": args.phase_modulated_init_scale_logit,
    }
    for flag, value in optional_policy_network_overrides.items():
        append_optional(command, flag, value)
    optional_runner_overrides = {
        "--joint_target_tracking_scale": args.joint_target_tracking_scale,
        "--joint_target_tracking_huber_delta": (
            args.joint_target_tracking_huber_delta
        ),
        "--joint_target_tracking_joint_indices": (
            args.joint_target_tracking_joint_indices
        ),
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
        "--push_recovery_actuator_tracking_huber_delta": (
            args.push_recovery_actuator_tracking_huber_delta
        ),
        "--forward_shortfall_huber_delta": args.forward_shortfall_huber_delta,
        "--forward_overshoot_huber_delta": args.forward_overshoot_huber_delta,
        "--forward_wrong_direction_huber_delta": (
            args.forward_wrong_direction_huber_delta
        ),
        "--forward_pitch_huber_delta": args.forward_pitch_huber_delta,
        "--forward_pitch_rate_huber_delta": args.forward_pitch_rate_huber_delta,
        "--forward_swing_clearance_huber_delta": (
            args.forward_swing_clearance_huber_delta
        ),
        "--forward_phase_swing_lift_huber_delta": (
            args.forward_phase_swing_lift_huber_delta
        ),
        "--forward_swing_phase_advance_ticks": (
            args.forward_swing_phase_advance_ticks
        ),
        "--forward_swing_advance_huber_delta": (
            args.forward_swing_advance_huber_delta
        ),
        "--forward_swing_target_rate_limit_huber_delta": (
            args.forward_swing_target_rate_limit_huber_delta
        ),
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
        "--forward_single_support_scale": args.forward_single_support_scale,
        "--forward_double_support_scale": args.forward_double_support_scale,
        "--forward_contact_transition_scale": args.forward_contact_transition_scale,
        "--forward_contact_transition_min_progress_ratio": (
            args.forward_contact_transition_min_progress_ratio
        ),
        "--forward_double_support_dwell_scale": (
            args.forward_double_support_dwell_scale
        ),
        "--forward_double_support_dwell_grace_steps": (
            args.forward_double_support_dwell_grace_steps
        ),
        "--forward_swing_clearance_scale": args.forward_swing_clearance_scale,
        "--forward_swing_clearance_target_m": args.forward_swing_clearance_target_m,
        "--forward_phase_swing_lift_scale": args.forward_phase_swing_lift_scale,
        "--forward_phase_swing_lift_target_m": (
            args.forward_phase_swing_lift_target_m
        ),
        "--forward_phase_single_support_scale": (
            args.forward_phase_single_support_scale
        ),
        "--forward_phase_single_support_swing_contact_weight": (
            args.forward_phase_single_support_swing_contact_weight
        ),
        "--forward_phase_single_support_stance_no_contact_weight": (
            args.forward_phase_single_support_stance_no_contact_weight
        ),
        "--forward_swing_balance_scale": args.forward_swing_balance_scale,
        "--forward_swing_balance_grace_steps": (
            args.forward_swing_balance_grace_steps
        ),
        "--forward_swing_advance_scale": args.forward_swing_advance_scale,
        "--forward_swing_advance_target_m": args.forward_swing_advance_target_m,
        "--forward_swing_target_rate_limit_scale": (
            args.forward_swing_target_rate_limit_scale
        ),
        "--forward_swing_target_rate_limit_joint_indices": (
            args.forward_swing_target_rate_limit_joint_indices
        ),
        "--forward_swing_target_rate_limit_values": (
            args.forward_swing_target_rate_limit_values
        ),
        "--push_recovery_actuator_tracking_scale": (
            args.push_recovery_actuator_tracking_scale
        ),
        "--push_recovery_tracking_window_steps": (
            args.push_recovery_tracking_window_steps
        ),
        "--push_recovery_tracking_joint_indices": (
            args.push_recovery_tracking_joint_indices
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
        "--reset_base_xy_jitter_m": args.reset_base_xy_jitter_m,
        "--reset_yaw_jitter_rad": args.reset_yaw_jitter_rad,
        "--reset_actuator_qpos_multiplier_min": (
            args.reset_actuator_qpos_multiplier_min
        ),
        "--reset_actuator_qpos_multiplier_max": (
            args.reset_actuator_qpos_multiplier_max
        ),
        "--reset_base_qvel_jitter": args.reset_base_qvel_jitter,
        "--dr_friction_min": args.dr_friction_min,
        "--dr_friction_max": args.dr_friction_max,
        "--dr_frictionloss_scale_min": args.dr_frictionloss_scale_min,
        "--dr_frictionloss_scale_max": args.dr_frictionloss_scale_max,
        "--dr_armature_scale_min": args.dr_armature_scale_min,
        "--dr_armature_scale_max": args.dr_armature_scale_max,
        "--dr_com_jitter_m": args.dr_com_jitter_m,
        "--dr_mass_scale_min": args.dr_mass_scale_min,
        "--dr_mass_scale_max": args.dr_mass_scale_max,
        "--dr_torso_mass_delta_min": args.dr_torso_mass_delta_min,
        "--dr_torso_mass_delta_max": args.dr_torso_mass_delta_max,
        "--dr_qpos_jitter_rad": args.dr_qpos_jitter_rad,
        "--dr_actuator_gain_scale_min": args.dr_actuator_gain_scale_min,
        "--dr_actuator_gain_scale_max": args.dr_actuator_gain_scale_max,
        "--dr_leg_geometry_jitter_scale": args.dr_leg_geometry_jitter_scale,
        "--push_interval_min_s": args.push_interval_min_s,
        "--push_interval_max_s": args.push_interval_max_s,
        "--push_magnitude_min": args.push_magnitude_min,
        "--push_magnitude_max": args.push_magnitude_max,
        "--noise_level": args.noise_level,
        "--noise_hip_pos": args.noise_hip_pos,
        "--noise_knee_pos": args.noise_knee_pos,
        "--noise_ankle_pos": args.noise_ankle_pos,
        "--noise_joint_vel": args.noise_joint_vel,
        "--noise_gravity": args.noise_gravity,
        "--noise_gyro": args.noise_gyro,
        "--noise_accelerometer": args.noise_accelerometer,
    }
    for flag, value in optional_runner_overrides.items():
        append_optional(command, flag, value)
    if args.push_enable is not None:
        command.append("--push_enable" if args.push_enable else "--no-push_enable")
    if args.command_progress_failure_enable:
        command.append("--command_progress_failure_enable")
    if args.enable_soft_prior:
        soft_prior_config_json = resolve_rdk_path(str(args.soft_prior_config_json))
        command.append("--enable_soft_prior")
        command.extend(
            [
                "--soft_prior_config_json",
                str(soft_prior_config_json),
                "--soft_prior_scale",
                cli_value(args.soft_prior_scale),
                "--soft_prior_huber_delta",
                cli_value(args.soft_prior_huber_delta),
                "--soft_prior_phase_source",
                args.soft_prior_phase_source,
            ]
        )
    if args.enable_behavior_prior:
        behavior_prior_mlp_npz = resolve_rdk_path(str(args.behavior_prior_mlp_npz))
        command.append("--enable_behavior_prior")
        command.extend(
            [
                "--behavior_prior_mlp_npz",
                str(behavior_prior_mlp_npz),
                "--behavior_prior_scale",
                cli_value(args.behavior_prior_scale),
                "--behavior_prior_huber_delta",
                cli_value(args.behavior_prior_huber_delta),
            ]
        )
        if args.behavior_prior_joint_weights:
            command.extend(
                [
                    "--behavior_prior_joint_weights",
                    args.behavior_prior_joint_weights,
                ]
            )
        if args.behavior_prior_temporal_rate_limit_rad_s > 0:
            command.extend(
                [
                    "--behavior_prior_temporal_rate_limit_rad_s",
                    cli_value(args.behavior_prior_temporal_rate_limit_rad_s),
                    "--behavior_prior_temporal_rate_limit_joint_indices",
                    args.behavior_prior_temporal_rate_limit_joint_indices,
                ]
            )
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
    if args.enable_soft_prior:
        if args.soft_prior_config_json is None:
            missing.append("--soft-prior-config-json")
        else:
            config_path = Path(args.soft_prior_config_json)
            if not config_path.is_absolute() and not config_path.exists():
                config_path = ROOT / config_path
            if not config_path.exists():
                missing.append(str(config_path))
    if args.enable_behavior_prior:
        if args.behavior_prior_mlp_npz is None:
            missing.append("--behavior-prior-mlp-npz")
        else:
            behavior_path = Path(args.behavior_prior_mlp_npz)
            if not behavior_path.is_absolute() and not behavior_path.exists():
                behavior_path = ROOT / behavior_path
            if not behavior_path.exists():
                missing.append(str(behavior_path))
    if args.restore_checkpoint_path is not None:
        restore_path = resolve_rdk_path(str(args.restore_checkpoint_path))
        if not restore_path.exists():
            missing.append(str(restore_path))
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


def scale_hfield_xml(text: str, z_scale: float, source: Path) -> str:
    pattern = re.compile(r'(<hfield\b[^>]*\bsize=")([^"]+)(")')
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"No hfield size attribute found in {source}")
    values = match.group(2).split()
    if len(values) != 4:
        raise SystemExit(f"Expected four hfield size values in {source}: {values}")
    values[2] = f"{float(z_scale):.8g}"
    return text[: match.start(2)] + " ".join(values) + text[match.end(2) :]


def apply_terrain_hfield_override(
    args: argparse.Namespace, output_dir: Path
) -> dict[str, Any]:
    if args.terrain_hfield_z_scale is None:
        return {"enabled": False}
    if args.task not in TASK_XML_RELATIVE_PATHS:
        raise SystemExit(f"Unknown task for terrain override: {args.task}")
    destination = Path(args.playground_path) / TASK_XML_RELATIVE_PATHS[args.task]
    if not destination.exists():
        raise SystemExit(f"Missing terrain XML: {destination}")

    backup = output_dir / f"{destination.name}.original"
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(destination, backup)
    before_sha = sha256(destination)
    original_text = destination.read_text()
    scaled_text = scale_hfield_xml(
        original_text, float(args.terrain_hfield_z_scale), destination
    )
    destination.write_text(scaled_text)
    after_sha = sha256(destination)
    return {
        "enabled": True,
        "task": args.task,
        "terrain_hfield_z_scale": float(args.terrain_hfield_z_scale),
        "destination": str(destination),
        "destination_sha256_before": before_sha,
        "destination_sha256_after": after_sha,
        "backup": str(backup),
        "backup_sha256": sha256(backup),
        "restored": False,
    }


def restore_terrain_hfield_override(
    terrain_override: dict[str, Any]
) -> dict[str, Any]:
    if not terrain_override.get("enabled"):
        return terrain_override
    backup = Path(terrain_override["backup"])
    destination = Path(terrain_override["destination"])
    shutil.copy2(backup, destination)
    terrain_override["restored"] = True
    terrain_override["destination_sha256_restored"] = sha256(destination)
    return terrain_override


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


def tail_text(path: Path, *, max_chars: int = 12000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(errors="replace")
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def list_output_files(output_dir: Path) -> list[dict[str, Any]]:
    if not output_dir.exists():
        return []
    files = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_dir():
            continue
        try:
            stat = path.stat()
            files.append(
                {
                    "path": str(path.relative_to(output_dir)),
                    "size_bytes": stat.st_size,
                    "mtime": stat.st_mtime,
                }
            )
        except OSError:
            continue
    return files


def write_run_diagnostic(
    path: Path,
    *,
    status: str,
    command: list[str],
    output_dir: Path,
    stdout_path: Path,
    stderr_path: Path,
    start_s: float,
    process: subprocess.Popen[str] | None = None,
    returncode: int | None = None,
    error: BaseException | None = None,
) -> None:
    stdout_tail = tail_text(stdout_path)
    stderr_tail = tail_text(stderr_path)
    payload: dict[str, Any] = {
        "status": status,
        "elapsed_s": time.monotonic() - start_s,
        "pid": process.pid if process is not None else None,
        "poll_returncode": process.poll() if process is not None else None,
        "returncode": returncode,
        "command": command,
        "command_shell": shell_join(command),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
        "summary": extract_summary(stdout_tail),
        "output_files": list_output_files(output_dir),
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
    }
    if error is not None:
        payload["error"] = {
            "type": type(error).__name__,
            "message": str(error),
        }
    write_manifest(path, payload)


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
    parser.add_argument(
        "--local-rocm-safe-env",
        action="store_true",
        help=(
            "Apply the recorded local ROCm workaround preset: JAX_PLATFORMS=rocm, "
            "disable XLA GPU command buffers, disable XLA preallocation, set "
            "XLA_PYTHON_CLIENT_MEM_FRACTION=0.60, and unset "
            "HSA_OVERRIDE_GFX_VERSION unless explicitly overridden."
        ),
    )
    parser.add_argument(
        "--xla-flags",
        default=None,
        help=(
            "Optional XLA_FLAGS override recorded in the run manifest. For "
            "local ROCm, --xla-flags=--xla_gpu_enable_command_buffer= disables "
            "GPU command buffers."
        ),
    )
    parser.add_argument(
        "--xla-python-client-preallocate",
        choices=["true", "false"],
        default=None,
        help="Optional XLA_PYTHON_CLIENT_PREALLOCATE override.",
    )
    parser.add_argument(
        "--xla-python-client-mem-fraction",
        type=float,
        default=None,
        help="Optional XLA_PYTHON_CLIENT_MEM_FRACTION override.",
    )
    parser.add_argument(
        "--extra-env",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Additional environment override for the training subprocess. May "
            "be repeated. Values are recorded in the manifest."
        ),
    )
    parser.add_argument(
        "--unset-env",
        action="append",
        default=[],
        metavar="KEY",
        help=(
            "Environment variable to remove from the training subprocess. May "
            "be repeated. Useful for inherited ROCm overrides."
        ),
    )
    parser.add_argument(
        "--unset-hsa-override-gfx-version",
        action="store_true",
        help="Remove HSA_OVERRIDE_GFX_VERSION from the training subprocess env.",
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
    parser.add_argument("--ppo-desired-kl", type=float, default=None)
    parser.add_argument(
        "--ppo-learning-rate-schedule",
        choices=["NONE", "ADAPTIVE_KL"],
        default=None,
    )
    parser.add_argument("--ppo-learning-rate-schedule-min-lr", type=float, default=None)
    parser.add_argument("--ppo-learning-rate-schedule-max-lr", type=float, default=None)
    parser.add_argument(
        "--ppo-policy-network",
        choices=["mlp", "phase_modulated"],
        default=None,
        help="Optional Playground runner --ppo_policy_network override.",
    )
    parser.add_argument("--phase-modulated-policy-hidden-sizes", default=None)
    parser.add_argument("--phase-modulated-context-hidden-sizes", default=None)
    parser.add_argument("--phase-modulated-context-indices", default=None)
    parser.add_argument(
        "--phase-modulated-activation",
        choices=["swish", "tanh"],
        default=None,
    )
    parser.add_argument("--phase-modulated-scale", type=float, default=None)
    parser.add_argument("--phase-modulated-init-scale-logit", type=float, default=None)
    parser.add_argument(
        "--restore-policy-kl-scale",
        type=float,
        default=None,
        help=(
            "Optional Playground PPO loss coefficient for KL(current policy || "
            "restored checkpoint policy). Requires --restore-checkpoint-path."
        ),
    )
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
    parser.add_argument(
        "--terrain-hfield-z-scale",
        type=float,
        default=None,
        help=(
            "Optional training-only hfield vertical scale override for the "
            "selected --task XML. The wrapper backs up the XML, patches the "
            "hfield size z value before training, records hashes, and restores "
            "the original after the run."
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
    parser.add_argument("--joint-target-tracking-scale", type=float, default=None)
    parser.add_argument(
        "--joint-target-tracking-huber-delta", type=float, default=None
    )
    parser.add_argument(
        "--joint-target-tracking-joint-indices",
        default=None,
        help="Comma-separated actuator indices forwarded to the Playground runner.",
    )
    parser.add_argument(
        "--push-recovery-actuator-tracking-scale",
        type=float,
        default=None,
        help=(
            "Scale applied to actuator tracking cost only during the recovery "
            "window after push impulses. Use a negative value to penalize."
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
    parser.add_argument(
        "--enable-soft-prior",
        action="store_true",
        help=(
            "Enable the default-off Playground soft-prior hook. Requires "
            "--soft-prior-config-json and a patched Playground checkout."
        ),
    )
    parser.add_argument("--soft-prior-config-json", default=None)
    parser.add_argument("--soft-prior-scale", type=float, default=-0.05)
    parser.add_argument("--soft-prior-huber-delta", type=float, default=0.05)
    parser.add_argument(
        "--soft-prior-phase-source",
        choices=["imitation_i", "step"],
        default="imitation_i",
    )
    parser.add_argument(
        "--enable-behavior-prior",
        action="store_true",
        help=(
            "Enable the default-off Playground behavior-prior hook. Requires "
            "--behavior-prior-mlp-npz and a patched Playground checkout."
        ),
    )
    parser.add_argument("--behavior-prior-mlp-npz", default=None)
    parser.add_argument("--behavior-prior-scale", type=float, default=-0.05)
    parser.add_argument("--behavior-prior-huber-delta", type=float, default=0.05)
    parser.add_argument(
        "--behavior-prior-joint-weights",
        default=None,
        help=(
            "Optional 14-value comma-separated action-order weights forwarded "
            "to the default-off Playground behavior-prior cost."
        ),
    )
    parser.add_argument(
        "--behavior-prior-temporal-rate-limit-rad-s",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--behavior-prior-temporal-rate-limit-joint-indices",
        default="2,3,4,11,12,13",
    )
    parser.add_argument("--action-rate-huber-delta", type=float, default=None)
    parser.add_argument("--action-magnitude-huber-delta", type=float, default=None)
    parser.add_argument("--target-rate-huber-delta", type=float, default=None)
    parser.add_argument("--actuator-tracking-huber-delta", type=float, default=None)
    parser.add_argument(
        "--push-recovery-actuator-tracking-huber-delta",
        type=float,
        default=None,
    )
    parser.add_argument("--forward-shortfall-huber-delta", type=float, default=None)
    parser.add_argument("--forward-overshoot-huber-delta", type=float, default=None)
    parser.add_argument("--forward-wrong-direction-huber-delta", type=float, default=None)
    parser.add_argument("--forward-pitch-huber-delta", type=float, default=None)
    parser.add_argument("--forward-pitch-rate-huber-delta", type=float, default=None)
    parser.add_argument("--forward-swing-clearance-huber-delta", type=float, default=None)
    parser.add_argument("--forward-phase-swing-lift-huber-delta", type=float, default=None)
    parser.add_argument("--forward-swing-phase-advance-ticks", type=int, default=None)
    parser.add_argument("--forward-swing-advance-huber-delta", type=float, default=None)
    parser.add_argument(
        "--forward-swing-target-rate-limit-huber-delta",
        type=float,
        default=None,
    )
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
    parser.add_argument("--forward-single-support-scale", type=float, default=None)
    parser.add_argument("--forward-double-support-scale", type=float, default=None)
    parser.add_argument("--forward-contact-transition-scale", type=float, default=None)
    parser.add_argument(
        "--forward-contact-transition-min-progress-ratio",
        type=float,
        default=None,
    )
    parser.add_argument("--forward-double-support-dwell-scale", type=float, default=None)
    parser.add_argument(
        "--forward-double-support-dwell-grace-steps",
        type=int,
        default=None,
    )
    parser.add_argument("--forward-swing-clearance-scale", type=float, default=None)
    parser.add_argument("--forward-swing-clearance-target-m", type=float, default=None)
    parser.add_argument("--forward-phase-swing-lift-scale", type=float, default=None)
    parser.add_argument("--forward-phase-swing-lift-target-m", type=float, default=None)
    parser.add_argument("--forward-phase-single-support-scale", type=float, default=None)
    parser.add_argument(
        "--forward-phase-single-support-swing-contact-weight",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--forward-phase-single-support-stance-no-contact-weight",
        type=float,
        default=None,
    )
    parser.add_argument("--forward-swing-balance-scale", type=float, default=None)
    parser.add_argument("--forward-swing-balance-grace-steps", type=int, default=None)
    parser.add_argument("--forward-swing-advance-scale", type=float, default=None)
    parser.add_argument("--forward-swing-advance-target-m", type=float, default=None)
    parser.add_argument(
        "--forward-swing-target-rate-limit-scale",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--forward-swing-target-rate-limit-joint-indices",
        default=None,
        help=(
            "Comma-separated actuator indices for phase-commanded swing target-rate "
            "limit cost."
        ),
    )
    parser.add_argument(
        "--forward-swing-target-rate-limit-values",
        default=None,
        help=(
            "Comma-separated rad/s limits matching "
            "--forward-swing-target-rate-limit-joint-indices."
        ),
    )
    parser.add_argument("--push-recovery-tracking-window-steps", type=int, default=None)
    parser.add_argument(
        "--push-recovery-tracking-joint-indices",
        default=None,
        help="Comma-separated actuator indices for push-recovery tracking cost.",
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
    parser.add_argument("--reset-base-xy-jitter-m", type=float, default=None)
    parser.add_argument("--reset-yaw-jitter-rad", type=float, default=None)
    parser.add_argument("--reset-actuator-qpos-multiplier-min", type=float, default=None)
    parser.add_argument("--reset-actuator-qpos-multiplier-max", type=float, default=None)
    parser.add_argument("--reset-base-qvel-jitter", type=float, default=None)
    parser.add_argument("--dr-friction-min", type=float, default=None)
    parser.add_argument("--dr-friction-max", type=float, default=None)
    parser.add_argument("--dr-frictionloss-scale-min", type=float, default=None)
    parser.add_argument("--dr-frictionloss-scale-max", type=float, default=None)
    parser.add_argument("--dr-armature-scale-min", type=float, default=None)
    parser.add_argument("--dr-armature-scale-max", type=float, default=None)
    parser.add_argument("--dr-com-jitter-m", type=float, default=None)
    parser.add_argument("--dr-mass-scale-min", type=float, default=None)
    parser.add_argument("--dr-mass-scale-max", type=float, default=None)
    parser.add_argument("--dr-torso-mass-delta-min", type=float, default=None)
    parser.add_argument("--dr-torso-mass-delta-max", type=float, default=None)
    parser.add_argument("--dr-qpos-jitter-rad", type=float, default=None)
    parser.add_argument("--dr-actuator-gain-scale-min", type=float, default=None)
    parser.add_argument("--dr-actuator-gain-scale-max", type=float, default=None)
    parser.add_argument("--dr-leg-geometry-jitter-scale", type=float, default=None)
    parser.add_argument(
        "--push-enable",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable training push perturbations.",
    )
    parser.add_argument("--push-interval-min-s", type=float, default=None)
    parser.add_argument("--push-interval-max-s", type=float, default=None)
    parser.add_argument("--push-magnitude-min", type=float, default=None)
    parser.add_argument("--push-magnitude-max", type=float, default=None)
    parser.add_argument("--noise-level", type=float, default=None)
    parser.add_argument("--noise-hip-pos", type=float, default=None)
    parser.add_argument("--noise-knee-pos", type=float, default=None)
    parser.add_argument("--noise-ankle-pos", type=float, default=None)
    parser.add_argument("--noise-joint-vel", type=float, default=None)
    parser.add_argument("--noise-gravity", type=float, default=None)
    parser.add_argument("--noise-gyro", type=float, default=None)
    parser.add_argument("--noise-accelerometer", type=float, default=None)
    args = parser.parse_args()

    validate_paths(args)

    if args.restore_checkpoint_path is not None:
        args.restore_checkpoint_path = str(
            resolve_rdk_path(str(args.restore_checkpoint_path))
        )
    if args.local_rocm_safe_env and args.platform != "gpu":
        raise SystemExit("--local-rocm-safe-env requires --platform gpu")
    if args.local_rocm_safe_env:
        if args.jax_platforms is None:
            args.jax_platforms = "rocm"
        if args.xla_flags is None:
            args.xla_flags = "--xla_gpu_enable_command_buffer="
        if args.xla_python_client_preallocate is None:
            args.xla_python_client_preallocate = "false"
        if args.xla_python_client_mem_fraction is None:
            args.xla_python_client_mem_fraction = 0.60
        args.unset_hsa_override_gfx_version = True

    output_root = Path(args.output_root).expanduser()
    if not output_root.is_absolute():
        output_root = (ROOT / output_root).resolve()
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
    env_set: dict[str, str] = {
        "JAX_PLATFORM_NAME": env["JAX_PLATFORM_NAME"],
    }
    if env.get("JAX_PLATFORMS") is not None:
        env_set["JAX_PLATFORMS"] = str(env["JAX_PLATFORMS"])
    env_unset = list(dict.fromkeys(args.unset_env))
    if args.unset_hsa_override_gfx_version:
        env_unset.append("HSA_OVERRIDE_GFX_VERSION")
    env_unset = list(dict.fromkeys(env_unset))
    for name in env_unset:
        env.pop(name, None)
    if args.xla_flags is not None:
        env["XLA_FLAGS"] = args.xla_flags
        env_set["XLA_FLAGS"] = args.xla_flags
    if args.xla_python_client_preallocate is not None:
        env["XLA_PYTHON_CLIENT_PREALLOCATE"] = args.xla_python_client_preallocate
        env_set["XLA_PYTHON_CLIENT_PREALLOCATE"] = (
            args.xla_python_client_preallocate
        )
    if args.xla_python_client_mem_fraction is not None:
        mem_fraction = cli_value(args.xla_python_client_mem_fraction)
        env["XLA_PYTHON_CLIENT_MEM_FRACTION"] = mem_fraction
        env_set["XLA_PYTHON_CLIENT_MEM_FRACTION"] = mem_fraction
    for item in args.extra_env:
        if "=" not in item:
            raise SystemExit(f"--extra-env must be KEY=VALUE, got: {item}")
        name, value = item.split("=", 1)
        if not name:
            raise SystemExit(f"--extra-env must include a non-empty KEY: {item}")
        env[name] = value
        env_set[name] = value

    manifest: dict[str, Any] = {
        "status": "RUN_PLANNED" if args.run else "DRY_RUN",
        "purpose": "offline actuator bridge PPO smoke; not a deployable policy",
        "timestamp": timestamp(),
        "playground_path": str(Path(args.playground_path).resolve()),
        "env_python_configured": str(Path(args.env_python)),
        "env_python_resolved": str(Path(args.env_python).resolve()),
        "output_dir": str(output_dir),
        "platform": args.platform,
        "local_rocm_safe_env": args.local_rocm_safe_env,
        "jax_platform_env": {
            "JAX_PLATFORM_NAME": env["JAX_PLATFORM_NAME"],
            "JAX_PLATFORMS": env.get("JAX_PLATFORMS"),
        },
        "subprocess_env": {
            "set": env_set,
            "unset": env_unset,
        },
        "timeout_s": args.timeout_s,
        "export_min_step": args.export_min_step,
        "actuator_bridge_enabled": not args.disable_actuator_bridge,
        "restore_checkpoint_path": args.restore_checkpoint_path,
        "reference_motion_override": {
            "enabled": bool(args.reference_motion_override),
            "source": args.reference_motion_override,
        },
        "terrain_hfield_override": {
            "enabled": args.terrain_hfield_z_scale is not None,
            "task": args.task,
            "terrain_hfield_z_scale": args.terrain_hfield_z_scale,
        },
        "soft_prior": {
            "enabled": args.enable_soft_prior,
            "config_json": args.soft_prior_config_json,
            "scale": args.soft_prior_scale,
            "huber_delta": args.soft_prior_huber_delta,
            "phase_source": args.soft_prior_phase_source,
        },
        "behavior_prior": {
            "enabled": args.enable_behavior_prior,
            "mlp_npz": args.behavior_prior_mlp_npz,
            "scale": args.behavior_prior_scale,
            "huber_delta": args.behavior_prior_huber_delta,
            "joint_weights": args.behavior_prior_joint_weights,
            "temporal_rate_limit_rad_s": (
                args.behavior_prior_temporal_rate_limit_rad_s
            ),
            "temporal_rate_limit_joint_indices": (
                args.behavior_prior_temporal_rate_limit_joint_indices
            ),
        },
        "target_rate_scale": args.target_rate_scale,
        "actuator_tracking_scale": args.actuator_tracking_scale,
        "push_recovery_actuator_tracking": {
            "scale": args.push_recovery_actuator_tracking_scale,
            "huber_delta": args.push_recovery_actuator_tracking_huber_delta,
            "window_steps": args.push_recovery_tracking_window_steps,
            "joint_indices": args.push_recovery_tracking_joint_indices,
        },
        "ppo_overrides": {
            "learning_rate": args.ppo_learning_rate,
            "entropy_cost": args.ppo_entropy_cost,
            "clipping_epsilon": args.ppo_clipping_epsilon,
            "max_grad_norm": args.ppo_max_grad_norm,
            "desired_kl": args.ppo_desired_kl,
            "learning_rate_schedule": args.ppo_learning_rate_schedule,
            "learning_rate_schedule_min_lr": args.ppo_learning_rate_schedule_min_lr,
            "learning_rate_schedule_max_lr": args.ppo_learning_rate_schedule_max_lr,
            "restore_policy_kl_scale": args.restore_policy_kl_scale,
        },
        "policy_network": {
            "ppo_policy_network": args.ppo_policy_network,
            "phase_modulated_policy_hidden_sizes": args.phase_modulated_policy_hidden_sizes,
            "phase_modulated_context_hidden_sizes": args.phase_modulated_context_hidden_sizes,
            "phase_modulated_context_indices": args.phase_modulated_context_indices,
            "phase_modulated_activation": args.phase_modulated_activation,
            "phase_modulated_scale": args.phase_modulated_scale,
            "phase_modulated_init_scale_logit": args.phase_modulated_init_scale_logit,
        },
        "training_recipe_overrides": {
            "joint_target_tracking_scale": args.joint_target_tracking_scale,
            "joint_target_tracking_huber_delta": (
                args.joint_target_tracking_huber_delta
            ),
            "joint_target_tracking_joint_indices": (
                args.joint_target_tracking_joint_indices
            ),
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
            "push_recovery_actuator_tracking_huber_delta": (
                args.push_recovery_actuator_tracking_huber_delta
            ),
            "forward_shortfall_huber_delta": args.forward_shortfall_huber_delta,
            "forward_overshoot_huber_delta": args.forward_overshoot_huber_delta,
            "forward_wrong_direction_huber_delta": (
                args.forward_wrong_direction_huber_delta
            ),
            "forward_pitch_huber_delta": args.forward_pitch_huber_delta,
            "forward_pitch_rate_huber_delta": args.forward_pitch_rate_huber_delta,
            "forward_swing_clearance_huber_delta": (
                args.forward_swing_clearance_huber_delta
            ),
            "forward_phase_swing_lift_huber_delta": (
                args.forward_phase_swing_lift_huber_delta
            ),
            "forward_swing_phase_advance_ticks": (
                args.forward_swing_phase_advance_ticks
            ),
            "forward_swing_advance_huber_delta": (
                args.forward_swing_advance_huber_delta
            ),
            "forward_swing_target_rate_limit_huber_delta": (
                args.forward_swing_target_rate_limit_huber_delta
            ),
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
            "forward_single_support_scale": args.forward_single_support_scale,
            "forward_double_support_scale": args.forward_double_support_scale,
            "forward_contact_transition_scale": (
                args.forward_contact_transition_scale
            ),
            "forward_contact_transition_min_progress_ratio": (
                args.forward_contact_transition_min_progress_ratio
            ),
            "forward_double_support_dwell_scale": (
                args.forward_double_support_dwell_scale
            ),
            "forward_double_support_dwell_grace_steps": (
                args.forward_double_support_dwell_grace_steps
            ),
            "forward_swing_clearance_scale": args.forward_swing_clearance_scale,
            "forward_swing_clearance_target_m": args.forward_swing_clearance_target_m,
            "forward_phase_swing_lift_scale": args.forward_phase_swing_lift_scale,
            "forward_phase_swing_lift_target_m": (
                args.forward_phase_swing_lift_target_m
            ),
            "forward_phase_single_support_scale": (
                args.forward_phase_single_support_scale
            ),
            "forward_phase_single_support_swing_contact_weight": (
                args.forward_phase_single_support_swing_contact_weight
            ),
            "forward_phase_single_support_stance_no_contact_weight": (
                args.forward_phase_single_support_stance_no_contact_weight
            ),
            "forward_swing_balance_scale": args.forward_swing_balance_scale,
            "forward_swing_balance_grace_steps": (
                args.forward_swing_balance_grace_steps
            ),
            "forward_swing_advance_scale": args.forward_swing_advance_scale,
            "forward_swing_advance_target_m": args.forward_swing_advance_target_m,
            "forward_swing_target_rate_limit_scale": (
                args.forward_swing_target_rate_limit_scale
            ),
            "forward_swing_target_rate_limit_joint_indices": (
                args.forward_swing_target_rate_limit_joint_indices
            ),
            "forward_swing_target_rate_limit_values": (
                args.forward_swing_target_rate_limit_values
            ),
            "push_recovery_actuator_tracking_scale": (
                args.push_recovery_actuator_tracking_scale
            ),
            "push_recovery_tracking_window_steps": (
                args.push_recovery_tracking_window_steps
            ),
            "push_recovery_tracking_joint_indices": (
                args.push_recovery_tracking_joint_indices
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
            "reset_base_xy_jitter_m": args.reset_base_xy_jitter_m,
            "reset_yaw_jitter_rad": args.reset_yaw_jitter_rad,
            "reset_actuator_qpos_multiplier_min": (
                args.reset_actuator_qpos_multiplier_min
            ),
            "reset_actuator_qpos_multiplier_max": (
                args.reset_actuator_qpos_multiplier_max
            ),
            "reset_base_qvel_jitter": args.reset_base_qvel_jitter,
            "dr_friction_min": args.dr_friction_min,
            "dr_friction_max": args.dr_friction_max,
            "dr_frictionloss_scale_min": args.dr_frictionloss_scale_min,
            "dr_frictionloss_scale_max": args.dr_frictionloss_scale_max,
            "dr_armature_scale_min": args.dr_armature_scale_min,
            "dr_armature_scale_max": args.dr_armature_scale_max,
            "dr_com_jitter_m": args.dr_com_jitter_m,
            "dr_mass_scale_min": args.dr_mass_scale_min,
            "dr_mass_scale_max": args.dr_mass_scale_max,
            "dr_torso_mass_delta_min": args.dr_torso_mass_delta_min,
            "dr_torso_mass_delta_max": args.dr_torso_mass_delta_max,
            "dr_qpos_jitter_rad": args.dr_qpos_jitter_rad,
            "dr_actuator_gain_scale_min": args.dr_actuator_gain_scale_min,
            "dr_actuator_gain_scale_max": args.dr_actuator_gain_scale_max,
            "dr_leg_geometry_jitter_scale": args.dr_leg_geometry_jitter_scale,
            "push_enable": args.push_enable,
            "push_interval_min_s": args.push_interval_min_s,
            "push_interval_max_s": args.push_interval_max_s,
            "push_magnitude_min": args.push_magnitude_min,
            "push_magnitude_max": args.push_magnitude_max,
            "noise_level": args.noise_level,
            "noise_hip_pos": args.noise_hip_pos,
            "noise_knee_pos": args.noise_knee_pos,
            "noise_ankle_pos": args.noise_ankle_pos,
            "noise_joint_vel": args.noise_joint_vel,
            "noise_gravity": args.noise_gravity,
            "noise_gyro": args.noise_gyro,
            "noise_accelerometer": args.noise_accelerometer,
        },
        "command": command,
        "command_shell": f"{env_shell_prefix(env_set, env_unset)} {shell_join(command)}",
        "robot_touched": False,
        "deploy_performed": False,
    }

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if not args.run:
        print("\nDry-run only. Pass --run to execute this tiny smoke command.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    playground_cwd = Path(args.playground_path).resolve()
    (
        playground_cwd
        / ".tmp"
        / "jax_cache"
        / "xla_gpu_per_fusion_autotune_cache_dir"
    ).mkdir(parents=True, exist_ok=True)
    reference_override = {"enabled": False}
    terrain_hfield_override = {"enabled": False}
    reference_override = apply_reference_override(args, output_dir)
    terrain_hfield_override = apply_terrain_hfield_override(args, output_dir)
    manifest["reference_motion_override"] = reference_override
    manifest["terrain_hfield_override"] = terrain_hfield_override
    write_manifest(output_dir / "smoke_manifest.start.json", manifest)

    start_s = time.monotonic()
    stdout_path = output_dir / "stdout.txt"
    stderr_path = output_dir / "stderr.txt"
    live_manifest_path = output_dir / "smoke_manifest.live.json"
    final_manifest_path = output_dir / "smoke_manifest.final.json"
    process: subprocess.Popen[str] | None = None
    returncode: int | None = None
    try:
        with stdout_path.open("w") as stdout_handle, stderr_path.open(
            "w"
        ) as stderr_handle:
            process = subprocess.Popen(
                command,
                cwd=playground_cwd,
                env=env,
                text=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
            )
            write_run_diagnostic(
                live_manifest_path,
                status="RUNNING",
                command=command,
                output_dir=output_dir,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                start_s=start_s,
                process=process,
            )
            deadline = time.monotonic() + args.timeout_s
            while True:
                returncode = process.poll()
                if returncode is not None:
                    break
                if time.monotonic() >= deadline:
                    timeout_exc = subprocess.TimeoutExpired(command, args.timeout_s)
                    write_run_diagnostic(
                        final_manifest_path,
                        status="HOLD_SMOKE_TIMEOUT",
                        command=command,
                        output_dir=output_dir,
                        stdout_path=stdout_path,
                        stderr_path=stderr_path,
                        start_s=start_s,
                        process=process,
                        error=timeout_exc,
                    )
                    process.kill()
                    process.wait()
                    raise timeout_exc
                write_run_diagnostic(
                    live_manifest_path,
                    status="RUNNING",
                    command=command,
                    output_dir=output_dir,
                    stdout_path=stdout_path,
                    stderr_path=stderr_path,
                    start_s=start_s,
                    process=process,
                )
                time.sleep(min(30.0, max(1.0, deadline - time.monotonic())))
    except BaseException as exc:
        if not final_manifest_path.exists():
            write_run_diagnostic(
                final_manifest_path,
                status="HOLD_SMOKE_EXCEPTION",
                command=command,
                output_dir=output_dir,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                start_s=start_s,
                process=process,
                returncode=returncode,
                error=exc,
            )
        raise
    finally:
        reference_override = restore_reference_override(reference_override)
        terrain_hfield_override = restore_terrain_hfield_override(
            terrain_hfield_override
        )
    elapsed_s = time.monotonic() - start_s
    stdout_text = stdout_path.read_text(errors="replace")
    stderr_text = stderr_path.read_text(errors="replace")

    manifest.update(
        {
            "status": "PASS_SMOKE_RUN" if returncode == 0 else "HOLD_SMOKE_RUN",
            "returncode": returncode,
            "elapsed_s": elapsed_s,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "stdout_tail": stdout_text[-12000:],
            "stderr_tail": stderr_text[-12000:],
            "output_files": list_output_files(output_dir),
            "reference_motion_override": reference_override,
            "terrain_hfield_override": terrain_hfield_override,
            "summary": extract_summary(stdout_text),
        }
    )
    write_manifest(final_manifest_path, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as exc:
        print(f"HOLD_SMOKE_TIMEOUT: timed out after {exc.timeout}s", file=sys.stderr)
        raise SystemExit(124) from exc
