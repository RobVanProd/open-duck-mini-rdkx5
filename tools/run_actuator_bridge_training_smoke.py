#!/usr/bin/env python3
"""Launch or print a tiny Open Duck actuator-bridge PPO smoke run.

This helper is offline-only. It does not touch the robot, SSH, deploy files, or
produce a deployable policy. By default it prints the exact command and exits.
Pass --run to execute the small smoke training command.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs/open-duck-playground/bin/python"
DEFAULT_OUTPUT_ROOT = Path("/tmp/open_duck_actuator_bridge_smoke")


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def append_optional(command: list[str], flag: str, value: Any) -> None:
    if value is not None:
        command.extend([flag, str(value)])


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
        str(args.target_rate_scale),
        "--actuator_tracking_scale",
        str(args.actuator_tracking_scale),
    ]
    optional_runner_overrides = {
        "--tracking_lin_vel_scale": args.tracking_lin_vel_scale,
        "--tracking_ang_vel_scale": args.tracking_ang_vel_scale,
        "--tracking_sigma": args.tracking_sigma,
        "--forward_progress_scale": args.forward_progress_scale,
        "--forward_progress_deadband": args.forward_progress_deadband,
        "--action_rate_scale": args.action_rate_scale,
        "--action_magnitude_scale": args.action_magnitude_scale,
        "--stand_still_scale": args.stand_still_scale,
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
    if not args.disable_actuator_bridge:
        command.append("--enable_actuator_bridge")
        command.extend(
            [
                "--actuator_bridge_delay_min_ticks",
                str(args.actuator_bridge_delay_min_ticks),
                "--actuator_bridge_delay_max_ticks",
                str(args.actuator_bridge_delay_max_ticks),
                "--actuator_bridge_tau_min_s",
                str(args.actuator_bridge_tau_min_s),
                "--actuator_bridge_tau_max_s",
                str(args.actuator_bridge_tau_max_s),
                "--actuator_bridge_velocity_limit_min_rad_s",
                str(args.actuator_bridge_velocity_limit_min_rad_s),
                "--actuator_bridge_velocity_limit_max_rad_s",
                str(args.actuator_bridge_velocity_limit_max_rad_s),
                "--actuator_bridge_per_joint_variation",
                str(args.actuator_bridge_per_joint_variation),
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
    parser.add_argument("--timeout-s", type=int, default=900)
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--env", default="joystick")
    parser.add_argument("--num-timesteps", type=int, default=256)
    parser.add_argument("--ppo-num-envs", type=int, default=16)
    parser.add_argument("--ppo-num-evals", type=int, default=1)
    parser.add_argument("--ppo-episode-length", type=int, default=100)
    parser.add_argument("--ppo-unroll-length", type=int, default=5)
    parser.add_argument("--ppo-batch-size", type=int, default=16)
    parser.add_argument("--ppo-num-minibatches", type=int, default=1)
    parser.add_argument("--ppo-num-updates-per-batch", type=int, default=1)
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
    parser.add_argument("--forward-progress-deadband", type=float, default=None)
    parser.add_argument("--action-rate-scale", type=float, default=None)
    parser.add_argument("--action-magnitude-scale", type=float, default=None)
    parser.add_argument("--stand-still-scale", type=float, default=None)
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
        "timeout_s": args.timeout_s,
        "actuator_bridge_enabled": not args.disable_actuator_bridge,
        "target_rate_scale": args.target_rate_scale,
        "actuator_tracking_scale": args.actuator_tracking_scale,
        "training_recipe_overrides": {
            "tracking_lin_vel_scale": args.tracking_lin_vel_scale,
            "tracking_ang_vel_scale": args.tracking_ang_vel_scale,
            "tracking_sigma": args.tracking_sigma,
            "forward_progress_scale": args.forward_progress_scale,
            "forward_progress_deadband": args.forward_progress_deadband,
            "action_rate_scale": args.action_rate_scale,
            "action_magnitude_scale": args.action_magnitude_scale,
            "stand_still_scale": args.stand_still_scale,
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
        "command_shell": f"JAX_PLATFORM_NAME={args.platform} {shell_join(command)}",
        "robot_touched": False,
        "deploy_performed": False,
    }

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if not args.run:
        print("\nDry-run only. Pass --run to execute this tiny smoke command.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    write_manifest(output_dir / "smoke_manifest.start.json", manifest)

    start_s = time.monotonic()
    stdout_path = output_dir / "stdout.txt"
    stderr_path = output_dir / "stderr.txt"
    with stdout_path.open("w") as stdout_handle, stderr_path.open("w") as stderr_handle:
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
    elapsed_s = time.monotonic() - start_s
    stdout_text = stdout_path.read_text(errors="replace")

    manifest.update(
        {
            "status": "PASS_SMOKE_RUN" if returncode == 0 else "HOLD_SMOKE_RUN",
            "returncode": returncode,
            "elapsed_s": elapsed_s,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
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
