#!/usr/bin/env python3
"""CPU contract for the gate-aligned signed command-progress objective."""

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    root = args.playground_root.resolve()
    sys.path.insert(0, str(root))
    from playground.common.rewards import (
        reward_signed_command_progress,
        reward_tracking_lin_vel,
    )
    from playground.open_duck_mini_v2 import joystick

    command_x = 0.074
    ratios = [-1.0, 0.0, 0.5, 1.0, 1.5]
    expected = [-1.0, 0.0, 0.5, 1.0, 1.0]
    observed = [
        float(reward_signed_command_progress(
            jp.array([command_x, 0.0, 0.0]),
            jp.array([ratio * command_x, 0.0, 0.0]),
        ))
        for ratio in ratios
    ]
    config = joystick.default_config()
    canonical_stationary = float(reward_tracking_lin_vel(
        jp.array([command_x, 0.0, 0.0]), jp.zeros(3),
        config.reward_config.tracking_sigma,
    ))
    canonical_zero = float(reward_tracking_lin_vel(
        jp.zeros(3), jp.zeros(3), config.reward_config.tracking_sigma,
    ))

    config.nominal_reference_bootstrap = True
    config.nominal_reference_command_x = command_x
    config.reference_start_phase = 0
    config.ground_up_signed_progress_objective = True
    config.noise_config.level = 0.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 1
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 1
    config.push_config.enable = False
    env = joystick.Joystick(task="flat_terrain_backlash", config=config)
    state = env.reset(jax.random.PRNGKey(100))
    next_state = env.step(state, jp.zeros(env.action_size))

    checks = {
        "signed_curve_exact": bool(np.allclose(observed, expected, atol=1e-6)),
        "reverse_is_negative": observed[0] < 0.0,
        "stationary_is_zero": observed[1] == 0.0,
        "target_is_one": observed[3] == 1.0,
        "overspeed_clipped_one": observed[4] == 1.0,
        "existing_scale_preserved": float(config.reward_config.scales.tracking_lin_vel) == 2.5,
        "canonical_stationary_unchanged": bool(np.isclose(canonical_stationary, np.exp(-(command_x**2) / 0.01))),
        "canonical_zero_unchanged": canonical_zero == 1.0,
        "one_step_reward_finite": bool(np.isfinite(float(next_state.reward))),
        "observation_dim_unchanged": int(np.asarray(next_state.obs["state"]).size) == 101,
        "action_dim_unchanged": int(env.action_size) == 14,
        "cpu_only": jax.default_backend() == "cpu",
    }
    passed = all(checks.values())
    payload = {
        "schema_version": "ground_up_signed_progress_objective_contract.v1",
        "status": "PASS_CPU_CONTRACT" if passed else "FAIL_CPU_CONTRACT",
        "patch": str(args.patch.resolve()),
        "patch_sha256": sha256(args.patch.resolve()),
        "command_x": command_x,
        "velocity_ratios": ratios,
        "expected_scores": expected,
        "observed_scores": observed,
        "canonical_stationary_score": canonical_stationary,
        "canonical_zero_score": canonical_zero,
        "tracking_scale": float(config.reward_config.scales.tracking_lin_vel),
        "checks": checks,
        "devices": [str(device) for device in jax.devices()],
        "robot_access": False,
        "local_gpu_access": False,
    }
    failed = [name for name, value in checks.items() if not value]
    lines = [
        "# Ground-Up Signed Progress Objective CPU Contract",
        "",
        f"status: `{payload['status']}`",
        "execution: `CPU_ONLY`",
        "",
        f"patch SHA-256: `{payload['patch_sha256']}`",
        "",
        "| vx / command | expected | observed |",
        "|---:|---:|---:|",
    ]
    for ratio, expected_value, observed_value in zip(ratios, expected, observed):
        lines.append(f"| {ratio:.1f} | {expected_value:.3f} | {observed_value:.3f} |")
    lines.extend([
        "",
        f"Existing tracking scale remains `2.5`. Canonical stationary Gaussian score remains `{canonical_stationary:.6f}` when the feature is disabled, and x=0 remains `{canonical_zero:.1f}`.",
        "",
        f"Failed checks: `{', '.join(failed) or 'none'}`.",
        "",
        "This is wiring evidence only, not learned behavior or policy clearance.",
        "",
    ])
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "observed_scores": observed, "failed": failed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
