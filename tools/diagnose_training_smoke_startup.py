#!/usr/bin/env python3
"""Diagnose where the cloud GPU training smoke disappears.

This helper is offline-only. It does not touch the robot, SSH, deploy files, or
produce a deployable policy. It creates its output directory before running any
heavy imports, then records one result file per startup stage so a disappearing
Colab runtime has a useful last-known-good marker.
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
DEFAULT_OUTPUT_DIR = ROOT / "outputs/analysis/training_smoke_startup_diagnostic"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def build_env(args: argparse.Namespace) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["JAX_PLATFORM_NAME"] = args.platform
    if args.jax_platforms:
        env["JAX_PLATFORMS"] = args.jax_platforms
    elif args.platform == "cpu":
        env["JAX_PLATFORMS"] = "cpu"
    else:
        env.pop("JAX_PLATFORMS", None)
    return env


def run_stage(
    *,
    name: str,
    command: list[str],
    cwd: Path,
    env: dict[str, str],
    output_dir: Path,
    timeout_s: int,
    summary: list[dict[str, Any]],
) -> dict[str, Any]:
    stage_dir = output_dir / name
    stage_dir.mkdir(parents=True, exist_ok=True)
    stage = {
        "name": name,
        "command": command,
        "command_shell": shell_join(command),
        "cwd": str(cwd),
        "started_at": timestamp(),
        "status": "RUNNING",
    }
    write_json(stage_dir / "stage.json", stage)
    start = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
            check=False,
        )
        stage.update(
            {
                "status": "PASS" if completed.returncode == 0 else "HOLD",
                "returncode": completed.returncode,
                "elapsed_s": time.monotonic() - start,
            }
        )
        (stage_dir / "stdout.txt").write_text(completed.stdout or "")
        (stage_dir / "stderr.txt").write_text(completed.stderr or "")
    except subprocess.TimeoutExpired as exc:
        stage.update(
            {
                "status": "TIMEOUT",
                "returncode": 124,
                "elapsed_s": time.monotonic() - start,
                "timeout_s": timeout_s,
            }
        )
        (stage_dir / "stdout.txt").write_text(exc.stdout or "")
        (stage_dir / "stderr.txt").write_text(exc.stderr or "")
    stage["finished_at"] = timestamp()
    write_json(stage_dir / "stage.json", stage)
    summary.append(stage)
    write_json(output_dir / "startup_diagnostic.json", {"stages": summary})
    return stage


def smoke_command(args: argparse.Namespace, output_root: Path, *, run_smoke: bool) -> list[str]:
    command = [
        str(Path(args.env_python)),
        str(ROOT / "tools" / "run_actuator_bridge_training_smoke.py"),
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--platform",
        args.platform,
        "--output-root",
        str(output_root),
        "--num-timesteps",
        str(args.smoke_num_timesteps),
        "--export-min-step",
        str(args.export_min_step),
        "--ppo-num-envs",
        str(args.ppo_num_envs),
        "--ppo-num-evals",
        "1",
        "--ppo-episode-length",
        "50",
        "--ppo-unroll-length",
        "5",
        "--ppo-batch-size",
        str(args.ppo_batch_size),
        "--ppo-num-minibatches",
        "1",
        "--ppo-num-updates-per-batch",
        "1",
        "--target-rate-scale",
        "-0.01",
        "--actuator-tracking-scale",
        "0.0",
        "--timeout-s",
        str(args.smoke_timeout_s),
    ]
    if args.jax_platforms:
        command.extend(["--jax-platforms", args.jax_platforms])
    if run_smoke:
        command.append("--run")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--env-python", default=str(DEFAULT_ENV_PYTHON))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--platform", choices=["cpu", "gpu"], default="cpu")
    parser.add_argument("--jax-platforms", default=None)
    parser.add_argument("--timeout-s", type=int, default=300)
    parser.add_argument("--smoke-timeout-s", type=int, default=1200)
    parser.add_argument("--smoke-num-timesteps", type=int, default=64)
    parser.add_argument("--export-min-step", type=int, default=1)
    parser.add_argument("--ppo-num-envs", type=int, default=8)
    parser.add_argument("--ppo-batch-size", type=int, default=8)
    parser.add_argument(
        "--run-smoke",
        action="store_true",
        help="run the tiny PPO smoke after import/preflight stages",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    env = build_env(args)
    summary: list[dict[str, Any]] = []
    metadata = {
        "status": "RUNNING",
        "started_at": timestamp(),
        "robot_touched": False,
        "deploy_performed": False,
        "platform": args.platform,
        "jax_platform_env": {
            "JAX_PLATFORM_NAME": env.get("JAX_PLATFORM_NAME"),
            "JAX_PLATFORMS": env.get("JAX_PLATFORMS"),
        },
        "playground_path": str(Path(args.playground_path).expanduser().resolve()),
        "env_python": str(Path(args.env_python).expanduser()),
    }
    write_json(output_dir / "startup_diagnostic.json", metadata | {"stages": summary})

    py = str(Path(args.env_python))
    playground = Path(args.playground_path)
    stages = [
        (
            "00_python_jax_device",
            [
                py,
                "-c",
                (
                    "import jax, jax.numpy as jnp; "
                    "print('jax', jax.__version__); "
                    "print('backend', jax.default_backend()); "
                    "print('devices', jax.devices()); "
                    "x=jnp.sum(jnp.ones((1024,), dtype=jnp.float32)); "
                    "x.block_until_ready(); print('sum', float(x))"
                ),
            ],
            ROOT,
            args.timeout_s,
        ),
        (
            "01_import_training_stack",
            [
                py,
                "-c",
                (
                    "import brax, jax, mujoco, mujoco_playground; "
                    "import playground.open_duck_mini_v2.joystick as joystick; "
                    "print('imports_ok'); print(joystick.__file__)"
                ),
            ],
            playground,
            args.timeout_s,
        ),
        (
            "02_smoke_dry_run",
            smoke_command(args, output_dir / "smoke_outputs", run_smoke=False),
            ROOT,
            args.timeout_s,
        ),
    ]
    if args.run_smoke:
        stages.append(
            (
                "03_smoke_run",
                smoke_command(args, output_dir / "smoke_outputs", run_smoke=True),
                ROOT,
                args.smoke_timeout_s + 60,
            )
        )

    exit_code = 0
    for name, command, cwd, timeout_s in stages:
        stage = run_stage(
            name=name,
            command=command,
            cwd=cwd,
            env=env,
            output_dir=output_dir,
            timeout_s=timeout_s,
            summary=summary,
        )
        if stage["status"] != "PASS":
            exit_code = int(stage.get("returncode") or 1)
            break

    metadata["status"] = "PASS" if exit_code == 0 else "HOLD"
    metadata["finished_at"] = timestamp()
    write_json(output_dir / "startup_diagnostic.json", metadata | {"stages": summary})
    print(json.dumps(metadata | {"stages": summary}, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
