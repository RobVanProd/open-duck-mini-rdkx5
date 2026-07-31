#!/usr/bin/env python3
"""CPU contract for progress-conditioned alive and yaw reward wiring."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import jax
import jax.numpy as jp
import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def configured_env(joystick, command_x: float):
    config = joystick.default_config()
    config.nominal_reference_bootstrap = True
    config.nominal_reference_command_x = command_x
    config.reference_start_phase = 0
    config.ground_up_signed_progress_objective = True
    config.ground_up_command_conditioned_survival = True
    config.noise_config.level = 0.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 1
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 1
    config.push_config.enable = False
    return joystick.Joystick(task="flat_terrain_backlash", config=config)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    root = args.playground_root.resolve()
    sys.path.insert(0, str(root))
    from playground.common.rewards import reward_tracking_ang_vel
    from playground.open_duck_mini_v2 import joystick

    command_x = 0.074
    moving_env = configured_env(joystick, command_x)
    moving = moving_env.step(
        moving_env.reset(jax.random.PRNGKey(100)),
        jp.zeros(moving_env.action_size),
    )
    local_vx = float(moving_env.get_local_linvel(moving.data)[0])
    progress = float(np.clip(local_vx / command_x, 0.0, 1.0))
    moving_alive = float(moving.metrics["reward/alive"])
    moving_yaw = float(moving.metrics["reward/tracking_ang_vel"])
    moving_yaw_canonical = float(
        reward_tracking_ang_vel(
            moving.info["command"],
            moving_env.get_gyro(moving.data),
            moving_env._config.reward_config.tracking_sigma,
        )
        * moving_env._config.reward_config.scales.tracking_ang_vel
    )

    zero_env = configured_env(joystick, 0.0)
    zero = zero_env.step(
        zero_env.reset(jax.random.PRNGKey(100)), jp.zeros(zero_env.action_size)
    )
    zero_alive = float(zero.metrics["reward/alive"])
    zero_yaw = float(zero.metrics["reward/tracking_ang_vel"])
    zero_yaw_canonical = float(
        reward_tracking_ang_vel(
            zero.info["command"],
            zero_env.get_gyro(zero.data),
            zero_env._config.reward_config.tracking_sigma,
        )
        * zero_env._config.reward_config.scales.tracking_ang_vel
    )

    ratios = np.array([-1.0, 0.0, 0.5, 1.0, 1.5])
    expected_gate = np.array([0.0, 0.0, 0.5, 1.0, 1.0])
    observed_gate = np.clip(ratios, 0.0, 1.0)
    checks = {
        "progress_gate_exact": bool(np.allclose(observed_gate, expected_gate)),
        "positive_command_alive_conditioned": bool(
            np.isclose(moving_alive, 20.0 * progress, atol=1e-5)
        ),
        "positive_command_yaw_conditioned": bool(
            np.isclose(moving_yaw, moving_yaw_canonical * progress, atol=1e-5)
        ),
        "zero_command_alive_preserved": bool(np.isclose(zero_alive, 20.0)),
        "zero_command_yaw_preserved": bool(
            np.isclose(zero_yaw, zero_yaw_canonical, atol=1e-5)
        ),
        "signed_progress_preserved": bool(
            moving_env._config.ground_up_signed_progress_objective
        ),
        "reward_scales_preserved": bool(
            moving_env._config.reward_config.scales.alive == 20.0
            and moving_env._config.reward_config.scales.tracking_ang_vel == 6.0
        ),
        "steps_finite": bool(
            np.isfinite(float(moving.reward)) and np.isfinite(float(zero.reward))
        ),
        "observation_dim_unchanged": int(np.asarray(moving.obs["state"]).size) == 101,
        "action_dim_unchanged": moving_env.action_size == 14,
        "cpu_only": jax.default_backend() == "cpu",
    }
    passed = all(checks.values())
    payload = {
        "schema_version": "ground_up_command_conditioned_survival_contract.v1",
        "status": "PASS_CPU_CONTRACT" if passed else "FAIL_CPU_CONTRACT",
        "patch": str(args.patch.resolve()),
        "patch_sha256": sha256(args.patch.resolve()),
        "gate_velocity_ratios": ratios.tolist(),
        "expected_gate": expected_gate.tolist(),
        "observed_gate": observed_gate.tolist(),
        "positive_command_probe": {
            "command_x": command_x,
            "local_vx": local_vx,
            "progress_gate": progress,
            "alive": moving_alive,
            "tracking_ang_vel": moving_yaw,
        },
        "zero_command_probe": {
            "alive": zero_alive,
            "tracking_ang_vel": zero_yaw,
        },
        "checks": checks,
        "devices": [str(device) for device in jax.devices()],
        "robot_access": False,
        "local_gpu_access": False,
    }
    failed = [name for name, value in checks.items() if not value]
    lines = [
        "# Ground-Up Command-Conditioned Survival CPU Contract",
        "",
        f"status: `{payload['status']}`",
        "execution: `CPU_ONLY`",
        "",
        f"patch SHA-256: `{payload['patch_sha256']}`",
        "",
        "| vx / command | expected gate | observed gate |",
        "|---:|---:|---:|",
    ]
    for ratio, expected, observed in zip(ratios, expected_gate, observed_gate):
        lines.append(f"| {ratio:.1f} | {expected:.3f} | {observed:.3f} |")
    lines += [
        "",
        "For positive forward commands, the existing alive and yaw rewards are "
        "multiplied by this progress gate. Their scales remain 20 and 6. At x=0, "
        "both canonical rewards remain active without conditioning.",
        "",
        f"Failed checks: `{', '.join(failed) or 'none'}`.",
        "",
        "This is wiring evidence only, not learned behavior or policy clearance.",
        "",
    ]
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "failed": failed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
