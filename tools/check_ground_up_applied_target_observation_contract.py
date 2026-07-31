#!/usr/bin/env python3
"""CPU contract for the preregistered applied-target observation repair."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import jax
import jax.numpy as jnp
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from audit_ground_up_measured_bridge_integration import (  # noqa: E402
    DELAY_TICKS,
    TAU_S,
    VELOCITY_LIMIT_RAD_S,
)
from closed_loop_sim_eval import (  # noqa: E402
    inject_policy_applied_target_observation,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_cpu() -> None:
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")


def configure(joystick, reference_table: Path, enabled: bool):
    config = joystick.default_config()
    config.nominal_reference_bootstrap = True
    config.reference_start_phase = 0
    config.reference_feature_table_path = str(reference_table.resolve())
    config.ground_up_hard_vector_command_support = True
    config.ground_up_command_support_range = [.074, .080]
    config.ground_up_action_velocity_limits_rad_s = VELOCITY_LIMIT_RAD_S.tolist()
    config.ground_up_measured_actuator_bridge = True
    config.ground_up_applied_target_observation = enabled
    config.ground_up_actuator_bridge_delay_ticks = DELAY_TICKS.tolist()
    config.ground_up_actuator_bridge_tau_s = TAU_S.tolist()
    config.noise_config.level = 0.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 1
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 1
    config.push_config.enable = False
    return config


def transition_contract(joystick, reference_table: Path) -> dict:
    env_off = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference_table, False),
    )
    env_on = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference_table, True),
    )
    key = jax.random.PRNGKey(100)
    off = env_off.reset(key)
    on = env_on.reset(key)
    step_off = jax.jit(env_off.step)
    step_on = jax.jit(env_on.step)
    outside = np.r_[0:83, 97:115]
    default_off_slot_errors = []
    applied_slot_errors = []
    outside_errors = []
    physics_errors = []
    sent_applied_separation = []
    for tick in range(12):
        direction = 1.0 if tick % 2 == 0 else -1.0
        action = jnp.asarray(np.linspace(-direction, direction, 14), dtype=jnp.float32)
        off = step_off(off, action)
        on = step_on(on, action)
        sent = np.asarray(on.info["motor_targets"])
        applied = np.asarray(on.info["ground_up_actuator_bridge_applied_targets"])
        obs_off = np.asarray(off.obs["state"])
        obs_on = np.asarray(on.obs["state"])
        default_off_slot_errors.append(float(np.max(np.abs(obs_off[83:97] - sent))))
        applied_slot_errors.append(float(np.max(np.abs(obs_on[83:97] - applied))))
        outside_errors.append(float(np.max(np.abs(obs_off[outside] - obs_on[outside]))))
        physics_errors.append(
            float(np.max(np.abs(np.asarray(off.data.qpos) - np.asarray(on.data.qpos))))
        )
        sent_applied_separation.append(float(np.max(np.abs(sent - applied))))

    info_a = dict(on.info)
    info_b = dict(on.info)
    base_applied = on.info["ground_up_actuator_bridge_applied_targets"]
    fork_delta = jnp.full(14, 0.04, dtype=base_applied.dtype)
    info_a["ground_up_actuator_bridge_applied_targets"] = base_applied - fork_delta / 2
    info_b["ground_up_actuator_bridge_applied_targets"] = base_applied + fork_delta / 2
    contact = on.info["last_contact"]
    fork_a = np.asarray(env_on._get_obs(on.data, info_a, contact)["state"])
    fork_b = np.asarray(env_on._get_obs(on.data, info_b, contact)["state"])
    fork_diff = np.abs(fork_b - fork_a)
    evaluator_obs = {
        "state": jnp.arange(115, dtype=jnp.float32),
        "privileged_state": jnp.arange(140, dtype=jnp.float32),
    }
    evaluator_target = jnp.linspace(-0.2, 0.2, 14)
    evaluator_off = inject_policy_applied_target_observation(
        evaluator_obs, evaluator_target, False
    )
    evaluator_on = inject_policy_applied_target_observation(
        evaluator_obs, evaluator_target, True
    )
    evaluator_outside = np.r_[0:83, 97:115]
    checks = {
        "actor_observation_remains_115_dimensional": np.asarray(on.obs["state"]).shape == (115,),
        "default_off_slot_remains_sent_target": max(default_off_slot_errors) <= 1e-6,
        "enabled_slot_is_applied_target": max(applied_slot_errors) <= 1e-6,
        "toggle_changes_no_other_actor_observation_fields": max(outside_errors) <= 1e-6,
        "toggle_changes_no_physics": max(physics_errors) <= 1e-6,
        "test_exercised_distinct_sent_and_applied_targets": max(sent_applied_separation) >= 1e-4,
        "hidden_applied_state_is_now_observable": float(np.max(fork_diff[83:97])) >= 0.039,
        "hidden_state_fork_changes_only_replacement_slot": float(np.max(fork_diff[outside])) <= 1e-6,
        "evaluator_default_off_is_identity": evaluator_off is evaluator_obs,
        "evaluator_enabled_slot_is_applied_target": float(
            np.max(np.abs(np.asarray(evaluator_on["state"])[83:97] - np.asarray(evaluator_target)))
        ) <= 1e-7,
        "evaluator_enabled_changes_no_other_actor_fields": float(
            np.max(
                np.abs(
                    np.asarray(evaluator_on["state"])[evaluator_outside]
                    - np.asarray(evaluator_obs["state"])[evaluator_outside]
                )
            )
        ) <= 1e-7,
        "evaluator_privileged_slot_matches_actor_slot": float(
            np.max(
                np.abs(
                    np.asarray(evaluator_on["privileged_state"])[83:97]
                    - np.asarray(evaluator_target)
                )
            )
        ) <= 1e-7,
    }
    return {
        "checks": checks,
        "max_default_off_slot_error_rad": max(default_off_slot_errors),
        "max_applied_slot_error_rad": max(applied_slot_errors),
        "max_outside_slot_toggle_error": max(outside_errors),
        "max_physics_toggle_error": max(physics_errors),
        "max_sent_applied_separation_rad": max(sent_applied_separation),
        "hidden_fork_slot_difference_rad": float(np.max(fork_diff[83:97])),
        "hidden_fork_outside_slot_difference": float(np.max(fork_diff[outside])),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--composed-joystick", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--reference-table", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require_cpu()
    playground_root = args.playground_root.resolve()
    composed_joystick = args.composed_joystick.resolve()
    patch = args.patch.resolve()
    reference_table = args.reference_table.resolve()
    output = args.output.resolve()
    sys.path.insert(0, str(playground_root))
    from playground.open_duck_mini_v2 import joystick

    previous_cwd = Path.cwd()
    os.chdir(playground_root)
    try:
        transition = transition_contract(joystick, reference_table)
    finally:
        os.chdir(previous_cwd)
    source = composed_joystick.read_text()
    source_checks = {
        "feature_is_default_off": "ground_up_applied_target_observation=False" in source,
        "feature_requires_measured_bridge": (
            "self._config.ground_up_measured_actuator_bridge\n"
            "                    & self._config.ground_up_applied_target_observation"
        ) in source,
        "applied_state_replaces_only_motor_target_slot": (
            'info["ground_up_actuator_bridge_applied_targets"]' in source
            and 'info["motor_targets"]' in source
        ),
        "no_reward_or_cost_added": (
            "applied_target_observation" not in source[source.find("def _get_reward(") :]
        ),
    }
    checks = {**transition["checks"], **source_checks}
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_CPU_APPLIED_TARGET_OBSERVATION_CONTRACT"
        if not failed
        else "FAIL_CPU_APPLIED_TARGET_OBSERVATION_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_applied_target_observation_contract.v1",
        "status": status,
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "rdk_access": False,
            "local_gpu_access": False,
            "colab_access": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "transition_contract": transition,
        "source_checks": source_checks,
        "inputs": {
            "playground_root": str(playground_root),
            "composed_joystick": {
                "path": str(composed_joystick),
                "sha256": sha256(composed_joystick),
            },
            "patch": {"path": str(patch), "sha256": sha256(patch)},
            "reference_table": {
                "path": str(reference_table),
                "sha256": sha256(reference_table),
            },
        },
        "authority": {
            "colab_training_authorized_by_this_result": False,
            "robot_or_rdk_authorized": False,
            "gpu_authorized": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
