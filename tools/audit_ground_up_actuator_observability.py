#!/usr/bin/env python3
"""Audit whether the 115-D actor state is Markov for the fitted bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np


DELAY_TICKS = np.asarray([3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 2, 3, 2, 3])
TAU_S = np.asarray(
    [.015, .015, .005, .010, .010, .120, .120, .120, .120, .020, .035, .010, .030, .005]
)
VELOCITY_LIMITS = np.asarray(
    [5.24, 5.24, 1.50, 1.50, 1.75, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 1.25, 1.00, 1.25]
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_cpu() -> None:
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU device visible: {jax.devices()}")


def configure(joystick, reference_feature_table: Path):
    config = joystick.default_config()
    config.nominal_reference_bootstrap = True
    config.reference_start_phase = 0
    config.ground_up_hard_vector_command_support = True
    config.ground_up_command_support_range = [.074, .080]
    config.ground_up_action_velocity_limits_rad_s = VELOCITY_LIMITS.tolist()
    config.ground_up_measured_actuator_bridge = True
    config.ground_up_actuator_bridge_delay_ticks = DELAY_TICKS.tolist()
    config.ground_up_actuator_bridge_tau_s = TAU_S.tolist()
    config.reference_feature_table_path = str(reference_feature_table)
    config.noise_config.level = 0.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 1
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 1
    config.push_config.enable = False
    return config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--composed-joystick", type=Path, required=True)
    parser.add_argument("--reference-feature-table", type=Path, required=True)
    args = parser.parse_args()
    require_cpu()

    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, args.reference_feature_table.resolve()),
    )
    state = env.reset(jax.random.PRNGKey(100))
    step = jax.jit(env.step)
    home = np.asarray(env._default_actuator)
    scale = float(env._config.action_scale)
    redundancy_errors = []
    history_errors = []
    for tick in range(48):
        phase = tick / 7.0 + np.arange(14) * .31
        requested = jnp.asarray(.8 * np.sin(phase), dtype=jnp.float32)
        state = step(state, requested)
        obs = np.asarray(state.obs["state"])
        sent_from_action = home + scale * obs[41:55]
        redundancy_errors.append(
            float(np.max(np.abs(obs[83:97] - sent_from_action)))
        )
        history = np.asarray(
            state.info["ground_up_actuator_bridge_target_history"]
        ).reshape((-1, 14))
        sent_histories = np.vstack(
            [
                home + scale * obs[41:55],
                home + scale * obs[55:69],
                home + scale * obs[69:83],
            ]
        )
        history_errors.append(float(np.max(np.abs(history[:3] - sent_histories))))

    current_obs = np.asarray(state.obs["state"]).copy()
    info_a = dict(state.info)
    info_b = dict(state.info)
    applied_a = np.asarray(info_a["ground_up_actuator_bridge_applied_targets"])
    perturbation = np.zeros(14, dtype=np.float32)
    perturbation[[2, 3, 4, 11, 12, 13]] = [.04, -.04, .035, -.035, .03, -.03]
    info_b["ground_up_actuator_bridge_applied_targets"] = jnp.asarray(
        applied_a + perturbation
    )
    state_a = state.replace(info=info_a)
    state_b = state.replace(info=info_b)
    same_action = jnp.zeros(14, dtype=jnp.float32)
    next_a = step(state_a, same_action)
    next_b = step(state_b, same_action)
    fork = {
        "current_actor_observation_max_error": float(
            np.max(np.abs(np.asarray(state_a.obs["state"]) - np.asarray(state_b.obs["state"])))
        ),
        "hidden_applied_target_difference_rad": float(
            np.max(np.abs(perturbation))
        ),
        "next_applied_target_difference_rad": float(
            np.max(
                np.abs(
                    np.asarray(next_a.info["ground_up_actuator_bridge_applied_targets"])
                    - np.asarray(next_b.info["ground_up_actuator_bridge_applied_targets"])
                )
            )
        ),
        "next_physics_ctrl_difference_rad": float(
            np.max(np.abs(np.asarray(next_a.data.ctrl) - np.asarray(next_b.data.ctrl)))
        ),
        "next_qpos_difference_rad": float(
            np.max(np.abs(np.asarray(next_a.data.qpos) - np.asarray(next_b.data.qpos)))
        ),
        "next_actor_observation_difference": float(
            np.max(
                np.abs(
                    np.asarray(next_a.obs["state"]) - np.asarray(next_b.obs["state"])
                )
            )
        ),
    }

    source = args.composed_joystick.read_text()
    source_checks = {
        "actor_contains_three_sent_action_states": all(
            token in source
            for token in (
                'info["last_act"]',
                'info["last_last_act"]',
                'info["last_last_last_act"]',
            )
        ),
        "actor_contains_sent_motor_target": 'info["motor_targets"]' in source,
        "actor_omits_bridge_applied_target": (
            'info["ground_up_actuator_bridge_applied_targets"],'
            not in source[source.find("state_parts = [") : source.find("privileged_state =")]
        ),
        "bridge_transition_depends_on_previous_applied_target": (
            'previous_applied = info["ground_up_actuator_bridge_applied_targets"]'
            in source
        ),
    }
    checks = {
        "sent_motor_target_slot_is_affine_duplicate": max(redundancy_errors) <= 1e-6,
        "three_actor_action_states_cover_delay_history": max(history_errors) <= 1e-6,
        "fork_has_identical_current_actor_observation": fork[
            "current_actor_observation_max_error"
        ] == 0.0,
        "fork_hidden_applied_state_differs": fork[
            "hidden_applied_target_difference_rad"
        ] >= .03,
        "same_observation_and_action_yield_different_physics_control": fork[
            "next_physics_ctrl_difference_rad"
        ] > 1e-4,
        "same_observation_and_action_yield_different_next_state": fork[
            "next_actor_observation_difference"
        ] > 1e-6,
        **source_checks,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_SELECT_APPLIED_TARGET_STATE" if not failed else "FAIL_OBSERVABILITY_AUDIT"
    result = {
        "schema_version": "ground_up_actuator_observability_audit.v1",
        "status": status,
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "rdk_access": False,
            "local_gpu_access": False,
            "colab_access": False,
        },
        "actor_observation_layout": {
            "size": int(current_obs.size),
            "gyro": [0, 3],
            "accelerometer": [3, 6],
            "command": [6, 13],
            "joint_position": [13, 27],
            "joint_velocity": [27, 41],
            "last_sent_action": [41, 55],
            "second_last_sent_action": [55, 69],
            "third_last_sent_action": [69, 83],
            "sent_motor_target": [83, 97],
            "contact": [97, 99],
            "phase": [99, 101],
            "reference_action": [101, 115],
        },
        "checks": checks,
        "failed_checks": failed,
        "redundancy": {
            "max_sent_target_vs_home_plus_scaled_last_action_error_rad": max(
                redundancy_errors
            ),
            "max_bridge_history_vs_three_actor_action_states_error_rad": max(
                history_errors
            ),
        },
        "hidden_state_fork": fork,
        "source_checks": source_checks,
        "inputs": {
            "composed_joystick": {
                "path": str(args.composed_joystick),
                "sha256": sha256(args.composed_joystick),
            },
            "reference_feature_table": {
                "path": str(args.reference_feature_table.resolve()),
                "sha256": sha256(args.reference_feature_table.resolve()),
            },
        },
        "conclusion": (
            "The actor observation is non-Markov for the fitted first-order bridge: "
            "previous applied target changes the next transition but is absent. The "
            "discrete 2-3 tick sent-target history is already present. The absolute sent "
            "motor-target slot is an affine duplicate of last_sent_action, so replacing "
            "that 14-D slot with the deterministic bridge-applied target adds the missing "
            "causal state without changing observation size or requiring recurrence."
        ),
        "authority": {
            "training_authorized": False,
            "robot_or_rdk_authorized": False,
            "gpu_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed, "fork": fork}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
