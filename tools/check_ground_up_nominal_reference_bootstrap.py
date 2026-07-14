#!/usr/bin/env python3
"""CPU contract check for the default-off nominal reference bootstrap."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import jax
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
    from playground.open_duck_mini_v2 import joystick

    phase_rows = []
    all_pass = True
    for phase in (0, 20):
        config = joystick.default_config()
        config.nominal_reference_bootstrap = True
        config.nominal_reference_command_x = 0.074
        config.reference_start_phase = phase
        config.noise_config.level = 0.0
        config.noise_config.action_min_delay = 0
        config.noise_config.action_max_delay = 1
        config.noise_config.imu_min_delay = 0
        config.noise_config.imu_max_delay = 1
        config.push_config.enable = False
        env = joystick.Joystick(task="flat_terrain_backlash", config=config)
        states = [env.reset(jax.random.PRNGKey(seed)) for seed in (100, 101)]
        expected_phase = np.array([
            np.cos(phase / env.PRM.nb_steps_in_period * 2 * np.pi),
            np.sin(phase / env.PRM.nb_steps_in_period * 2 * np.pi),
        ])
        expected_reference = np.asarray(
            env.PRM.get_reference_motion(0.074, 0.0, 0.0, phase)
        )
        checks = {
            "command_exact": all(
                np.allclose(
                    np.asarray(state.info["command"]),
                    np.array([0.074, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                )
                for state in states
            ),
            "phase_index_exact": all(
                int(state.info["imitation_i"]) == phase for state in states
            ),
            "phase_vector_exact": all(
                np.allclose(np.asarray(state.info["imitation_phase"]), expected_phase)
                for state in states
            ),
            "phase_vector_unit_norm": all(
                np.isclose(np.linalg.norm(np.asarray(state.info["imitation_phase"])), 1.0)
                for state in states
            ),
            "reference_frame_exact": all(
                np.allclose(np.asarray(state.info["current_reference_motion"]), expected_reference)
                for state in states
            ),
            "deterministic_qpos_across_seeds": np.array_equal(
                np.asarray(states[0].data.qpos), np.asarray(states[1].data.qpos)
            ),
            "deterministic_qvel_across_seeds": np.array_equal(
                np.asarray(states[0].data.qvel), np.asarray(states[1].data.qvel)
            ),
            "zero_reset_velocity": bool(
                np.allclose(np.asarray(states[0].data.qvel), 0.0)
            ),
            "deterministic_actor_observation_across_seeds": np.array_equal(
                np.asarray(states[0].obs["state"]), np.asarray(states[1].obs["state"])
            ),
            "observation_dim_101": int(np.asarray(states[0].obs["state"]).size) == 101,
            "noise_disabled": float(config.noise_config.level) == 0.0,
            "pushes_disabled": not bool(config.push_config.enable),
            "action_delay_fixed_zero": (
                int(config.noise_config.action_min_delay) == 0
                and int(config.noise_config.action_max_delay) == 1
            ),
            "imu_delay_fixed_zero": (
                int(config.noise_config.imu_min_delay) == 0
                and int(config.noise_config.imu_max_delay) == 1
            ),
        }
        passed = all(checks.values())
        all_pass &= passed
        phase_rows.append({"phase": phase, "status": "PASS" if passed else "FAIL", "checks": checks})

    payload = {
        "schema_version": "ground_up_nominal_reference_bootstrap_contract.v1",
        "status": "PASS_CPU_CONTRACT" if all_pass else "FAIL_CPU_CONTRACT",
        "execution": {
            "jax_platform": jax.default_backend(),
            "devices": [str(device) for device in jax.devices()],
        },
        "playground_root": str(root),
        "patch": str(args.patch.resolve()),
        "patch_sha256": sha256(args.patch.resolve()),
        "phases": phase_rows,
        "robot_access": False,
        "local_gpu_access": False,
    }
    lines = [
        "# Ground-Up Nominal Reference Bootstrap CPU Contract",
        "",
        f"status: `{payload['status']}`",
        f"execution: `{jax.default_backend().upper()}_ONLY`",
        "",
        f"patch SHA-256: `{payload['patch_sha256']}`",
        "",
        "| start phase | status | failed checks |",
        "|---:|---|---|",
    ]
    for row in phase_rows:
        failed = [name for name, value in row["checks"].items() if not value]
        lines.append(f"| {row['phase']} | `{row['status']}` | {', '.join(failed) or 'none'} |")
    lines.extend([
        "",
        "This validates only the default-off reset/command/reference contract. It is not behavior evidence or robot clearance.",
        "",
    ])
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "phases": phase_rows}, sort_keys=True))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
