#!/usr/bin/env python3
"""CPU contract for the preregistered ground-up measured actuator bridge."""

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

from actuator_bridge_model import ActuatorBridgeModel, JointActuatorParams  # noqa: E402
from audit_ground_up_measured_bridge_integration import (  # noqa: E402
    DELAY_TICKS,
    TAU_S,
    VELOCITY_LIMIT_RAD_S,
    make_sequences,
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


def configure(joystick):
    config = joystick.default_config()
    config.nominal_reference_bootstrap = True
    config.reference_start_phase = 0
    config.ground_up_hard_vector_command_support = True
    config.ground_up_command_support_range = [.074, .080]
    config.ground_up_action_velocity_limits_rad_s = VELOCITY_LIMIT_RAD_S.tolist()
    config.ground_up_measured_actuator_bridge = True
    config.ground_up_actuator_bridge_delay_ticks = DELAY_TICKS.tolist()
    config.ground_up_actuator_bridge_tau_s = TAU_S.tolist()
    config.noise_config.level = 0.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 1
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 1
    config.push_config.enable = False
    return config


def helper_parity(env, initial: np.ndarray, steps: int) -> dict:
    params = [
        JointActuatorParams(int(delay), float(tau), float(velocity))
        for delay, tau, velocity in zip(DELAY_TICKS, TAU_S, VELOCITY_LIMIT_RAD_S)
    ]

    def compiled_step(history, applied, sent):
        info = {
            "ground_up_actuator_bridge_target_history": history,
            "ground_up_actuator_bridge_applied_targets": applied,
        }
        output = env._apply_ground_up_measured_actuator_bridge(info, sent)
        return (
            output,
            info["ground_up_actuator_bridge_target_history"],
            info["ground_up_actuator_bridge_applied_targets"],
        )

    bridge_step = jax.jit(compiled_step)
    results = {}
    maximum = 0.0
    for name, targets in make_sequences(initial, steps, float(env.dt)).items():
        model = ActuatorBridgeModel(params, initial_target=initial)
        expected = np.vstack([model.step(target, float(env.dt)) for target in targets])
        history = jnp.tile(jnp.asarray(initial), int(DELAY_TICKS.max()) + 1)
        applied = jnp.asarray(initial)
        actual = []
        for sent in targets:
            output, history, applied = bridge_step(history, applied, jnp.asarray(sent))
            actual.append(np.asarray(output))
        actual_array = np.vstack(actual)
        error = np.abs(actual_array - expected)
        sequence_max = float(error.max())
        maximum = max(maximum, sequence_max)
        results[name] = {
            "finite": bool(np.isfinite(actual_array).all()),
            "max_abs_error_rad": sequence_max,
            "mean_abs_error_rad": float(error.mean()),
        }
    return {
        "threshold_rad": 1e-6,
        "global_max_abs_error_rad": maximum,
        "checks": {
            "all_sequences_finite": all(item["finite"] for item in results.values()),
            "all_sequences_within_1e_6_rad": maximum <= 1e-6,
        },
        "sequences": results,
    }


def environment_contract(env) -> dict:
    state = env.reset(jax.random.PRNGKey(100))
    home = np.asarray(env._default_actuator).copy()
    bridge_home = np.asarray(jnp.asarray(env._default_actuator)).copy()
    reset_history = np.asarray(
        state.info["ground_up_actuator_bridge_target_history"]
    ).reshape((-1, env._actuators)).copy()
    reset_applied = np.asarray(
        state.info["ground_up_actuator_bridge_applied_targets"]
    ).copy()
    reset_checks = {
        "sent_target_is_exact_home": bool(np.array_equal(np.asarray(state.info["motor_targets"]), home)),
        "history_has_four_rows": reset_history.shape == (4, 14),
        "history_is_exact_execution_dtype_home": bool(
            np.array_equal(reset_history, np.tile(bridge_home, (4, 1)))
        ),
        "history_home_quantization_below_1e_7_rad": bool(
            np.max(np.abs(reset_history - np.tile(home, (4, 1)))) <= 1e-7
        ),
        "applied_target_is_exact_home": bool(np.array_equal(reset_applied, home)),
    }

    model = ActuatorBridgeModel(
        [
            JointActuatorParams(int(delay), float(tau), float(velocity))
            for delay, tau, velocity in zip(DELAY_TICKS, TAU_S, VELOCITY_LIMIT_RAD_S)
        ],
        initial_target=home,
    )
    step = jax.jit(env.step)
    previous_sent = home.copy()
    errors = []
    rate_excess = []
    ctrl_errors = []
    action_history_errors = []
    obs_action_errors = []
    obs_target_errors = []
    for tick in range(10):
        requested = jnp.ones(14) if tick % 2 == 0 else -jnp.ones(14)
        state = step(state, requested)
        sent = np.asarray(state.info["motor_targets"])
        applied = np.asarray(state.info["ground_up_actuator_bridge_applied_targets"])
        expected = model.step(sent, float(env.dt))
        errors.append(float(np.max(np.abs(applied - expected))))
        rate_excess.append(
            float(np.max(np.abs(sent - previous_sent) - VELOCITY_LIMIT_RAD_S * float(env.dt)))
        )
        ctrl_errors.append(float(np.max(np.abs(np.asarray(state.data.ctrl) - applied))))
        realized_action = (sent - home) / float(env._config.action_scale)
        action_history_errors.append(
            float(np.max(np.abs(np.asarray(state.info["last_act"]) - realized_action)))
        )
        obs = np.asarray(state.obs["state"])
        obs_action_errors.append(float(np.max(np.abs(obs[41:55] - realized_action))))
        obs_target_errors.append(float(np.max(np.abs(obs[83:97] - sent))))
        previous_sent = sent

    metrics = set(state.metrics)
    reward_scales = set(env._config.reward_config.scales)
    checks = {
        **reset_checks,
        "bridge_output_matches_independent_model": max(errors) <= 1e-6,
        "sent_target_respects_hard_vector": max(rate_excess) <= 1e-6,
        "physics_ctrl_equals_bridged_applied_target": max(ctrl_errors) <= 1e-6,
        "policy_action_history_retains_sent_target": max(action_history_errors) <= 1e-6,
        "observation_retains_realized_sent_action": max(obs_action_errors) <= 1e-6,
        "observation_retains_sent_motor_target": max(obs_target_errors) <= 1e-6,
        "no_bridge_reward_or_cost_metric": not any("bridge" in name for name in metrics),
        "no_bridge_reward_scale": not any("bridge" in name for name in reward_scales),
        "state_and_reward_finite": bool(
            np.isfinite(float(state.reward))
            and np.isfinite(np.asarray(state.obs["state"])).all()
            and np.isfinite(np.asarray(state.data.qpos)).all()
        ),
    }
    return {
        "checks": checks,
        "reset_home_target_rad": home.tolist(),
        "reset_execution_dtype_home_target_rad": bridge_home.tolist(),
        "reset_history_rows_rad": reset_history.tolist(),
        "reset_history_max_error_rad": float(
            np.max(np.abs(reset_history - np.tile(home, (4, 1))))
        ),
        "max_bridge_model_error_rad": max(errors),
        "max_sent_rate_bound_excess_rad": max(rate_excess),
        "max_physics_ctrl_error_rad": max(ctrl_errors),
        "max_action_history_error": max(action_history_errors),
        "max_observation_action_error": max(obs_action_errors),
        "max_observation_target_error_rad": max(obs_target_errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--composed-joystick", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    args = parser.parse_args()
    require_cpu()

    from playground.open_duck_mini_v2 import joystick

    config = configure(joystick)
    env = joystick.Joystick(task="flat_terrain_backlash", config=config)
    initial = np.asarray(env._default_actuator, dtype=float)
    parity = helper_parity(env, initial, 256)
    transition = environment_contract(env)
    source = args.composed_joystick.read_text()
    source_checks = {
        "bridge_is_after_hard_sent_limit": source.find("motor_targets = jp.clip(")
        < source.find("_apply_ground_up_measured_actuator_bridge(", source.find("def step(")),
        "bridge_is_before_physics": source.find(
            "_apply_ground_up_measured_actuator_bridge(", source.find("def step(")
        ) < source.find("data = mjx_env.step(", source.find("def step(")),
        "physics_uses_applied_target": "state.data, applied_motor_targets, self.n_substeps" in source,
        "sent_target_is_preserved": "state.info[\"motor_targets\"] = motor_targets" in source,
        "no_tracking_penalty_implementation": "actuator_bridge_tracking_cost" not in source,
    }
    checks = {**parity["checks"], **transition["checks"], **source_checks}
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_CPU_MEASURED_BRIDGE_CONTRACT" if not failed else "FAIL_CPU_MEASURED_BRIDGE_CONTRACT"
    result = {
        "schema_version": "ground_up_measured_bridge_contract.v1",
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
        "helper_parity": parity,
        "environment_transition": transition,
        "source_checks": source_checks,
        "inputs": {
            "composed_joystick": {"path": str(args.composed_joystick), "sha256": sha256(args.composed_joystick)},
            "patch": {"path": str(args.patch), "sha256": sha256(args.patch)},
        },
        "authority": {
            "training_authorized": False,
            "robot_or_rdk_authorized": False,
            "gpu_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
