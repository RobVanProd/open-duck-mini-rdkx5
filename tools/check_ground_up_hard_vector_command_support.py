#!/usr/bin/env python3
"""Verify hard-vector command support and stateful ONNX on CPU only."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from brax.training.acme import running_statistics
import jax
import jax.numpy as jnp
import numpy as np
import onnx
import onnxruntime as ort


ACTION_SIZE = 14
COMMAND_MIN_X = 0.074
COMMAND_MAX_X = 0.080
VELOCITY_LIMITS = np.array(
    [
        5.24,
        5.24,
        1.50,
        1.50,
        1.75,
        5.24,
        5.24,
        5.24,
        5.24,
        5.24,
        5.24,
        1.25,
        1.00,
        1.25,
    ],
    dtype=np.float32,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_cpu() -> None:
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu for this contract")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")


def configure_environment(joystick):
    config = joystick.default_config()
    config.nominal_reference_bootstrap = True
    config.reference_start_phase = 0
    config.ground_up_hard_vector_command_support = True
    config.ground_up_command_support_range = [COMMAND_MIN_X, COMMAND_MAX_X]
    config.ground_up_action_velocity_limits_rad_s = VELOCITY_LIMITS.tolist()
    config.noise_config.level = 0.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 1
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 1
    config.push_config.enable = False
    return config


def environment_contract(joystick) -> tuple[dict, object, object]:
    config = configure_environment(joystick)
    env = joystick.Joystick(task="flat_terrain_backlash", config=config)

    command_keys = jax.random.split(jax.random.PRNGKey(20260714), 4096)
    sample_commands = jax.jit(jax.vmap(env.sample_command))(command_keys)
    command_x = np.asarray(sample_commands[:, 0])
    command_checks = {
        "all_finite": bool(np.all(np.isfinite(command_x))),
        "all_within_frozen_support": bool(
            np.all(command_x >= COMMAND_MIN_X)
            and np.all(command_x < COMMAND_MAX_X)
        ),
        "nondegenerate_std": bool(np.std(command_x) > 1.0e-4),
        "other_command_axes_zero": bool(
            np.array_equal(np.asarray(sample_commands[:, 1:]), np.zeros((4096, 6)))
        ),
    }

    state = env.reset(jax.random.PRNGKey(100))
    reset_motor_targets = np.asarray(state.info["motor_targets"])
    default_actuator = np.asarray(env._default_actuator)
    reset_checks = {
        "home_motor_target_exact": bool(
            np.allclose(reset_motor_targets, default_actuator, atol=0.0, rtol=0.0)
        ),
        "zero_reset_velocity": bool(np.allclose(np.asarray(state.data.qvel), 0.0)),
        "zero_applied_action_history": bool(
            np.allclose(np.asarray(state.info["last_act"]), 0.0)
        ),
        "sampled_reset_command_in_support": bool(
            COMMAND_MIN_X <= float(state.info["command"][0]) < COMMAND_MAX_X
        ),
    }

    requested_action = jnp.ones(ACTION_SIZE)
    next_state = env.step(state, requested_action)
    targets = np.asarray(next_state.info["motor_targets"])
    target_delta = targets - reset_motor_targets
    max_target_delta = VELOCITY_LIMITS * float(env.dt)
    applied_action = np.asarray(next_state.info["last_act"])
    expected_applied_action = (targets - default_actuator) / float(config.action_scale)
    actor_obs = np.asarray(next_state.obs["state"])
    transition_checks = {
        "per_joint_target_delta_bounded": bool(
            np.all(np.abs(target_delta) <= max_target_delta + 1.0e-6)
        ),
        "aggressive_first_tick_hits_each_bound": bool(
            np.allclose(target_delta, max_target_delta, atol=1.0e-6, rtol=1.0e-6)
        ),
        "info_history_is_realized_action": bool(
            np.allclose(applied_action, expected_applied_action, atol=1.0e-6)
        ),
        "returned_observation_is_realized_action": bool(
            np.allclose(actor_obs[41:55], applied_action, atol=1.0e-6)
        ),
        "returned_observation_has_realized_targets": bool(
            np.allclose(actor_obs[83:97], targets, atol=1.0e-6)
        ),
        "reward_and_state_finite": bool(
            np.isfinite(float(next_state.reward))
            and np.all(np.isfinite(actor_obs))
            and np.all(np.isfinite(targets))
        ),
    }
    checks = {**command_checks, **reset_checks, **transition_checks}
    return (
        {
            "checks": checks,
            "command_x": {
                "count": int(command_x.size),
                "min": float(np.min(command_x)),
                "max": float(np.max(command_x)),
                "mean": float(np.mean(command_x)),
                "std": float(np.std(command_x)),
            },
            "control_dt": float(env.dt),
            "action_scale": float(config.action_scale),
            "velocity_limits_rad_s": VELOCITY_LIMITS.tolist(),
            "max_target_delta_rad": max_target_delta.tolist(),
            "measured_first_target_delta_rad": target_delta.tolist(),
            "measured_first_applied_action": applied_action.tolist(),
        },
        env,
        next_state,
    )


def onnx_contract(reference_module, env, state, output_onnx: Path) -> dict:
    obs_size = int(np.asarray(state.obs["state"]).size)
    hidden_sizes = (32, 16)
    network = reference_module.make_reference_residual_ppo_networks(
        {"state": (obs_size,), "privileged_state": (obs_size,)},
        ACTION_SIZE,
        preprocess_observations_fn=running_statistics.normalize,
        policy_hidden_layer_sizes=hidden_sizes,
        value_hidden_layer_sizes=hidden_sizes,
        value_obs_key="state",
    )
    policy = network.policy_network.init(jax.random.PRNGKey(707))
    specs = {
        "state": jax.ShapeDtypeStruct((obs_size,), jnp.float32),
        "privileged_state": jax.ShapeDtypeStruct((obs_size,), jnp.float32),
    }
    normalizer = running_statistics.init_state(specs)
    params = (normalizer, policy)
    export = reference_module.export_reference_residual_onnx(
        params,
        ACTION_SIZE,
        obs_size,
        output_onnx,
        hidden_sizes,
        action_velocity_limits_rad_s=VELOCITY_LIMITS,
        control_dt=float(env.dt),
        action_scale=float(env._config.action_scale),
    )

    model = onnx.load(output_onnx)
    onnx.checker.check_model(model)
    input_names = [value.name for value in model.graph.input]
    output_names = [value.name for value in model.graph.output]
    session = ort.InferenceSession(str(output_onnx), providers=["CPUExecutionProvider"])
    obs = np.asarray(state.obs["state"], dtype=np.float32)[None, :]
    previous = np.zeros((1, ACTION_SIZE), dtype=np.float32)
    max_action_delta = VELOCITY_LIMITS * float(env.dt) / float(env._config.action_scale)
    chain_errors = []
    state_output_errors = []
    first_action = None
    for index in range(8):
        varied_obs = obs.copy()
        if index % 2:
            varied_obs[:, -ACTION_SIZE:] *= -1.0
        action, previous_out = session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": varied_obs, "previous_action": previous},
        )
        if first_action is None:
            first_action = action.copy()
        chain_errors.append(
            float(np.max(np.abs(action - previous) - max_action_delta[None, :]))
        )
        state_output_errors.append(float(np.max(np.abs(previous_out - action))))
        previous = previous_out

    raw_reference = obs[:, -ACTION_SIZE:]
    expected_first = np.clip(
        raw_reference,
        -max_action_delta[None, :],
        max_action_delta[None, :],
    )
    first_reference_error = float(np.max(np.abs(first_action - expected_first)))

    rejected_invalid_dynamics = False
    try:
        reference_module.export_reference_residual_onnx(
            params,
            ACTION_SIZE,
            obs_size,
            output_onnx.with_suffix(".invalid.onnx"),
            hidden_sizes,
            action_velocity_limits_rad_s=VELOCITY_LIMITS,
            control_dt=0.0,
            action_scale=float(env._config.action_scale),
        )
    except ValueError:
        rejected_invalid_dynamics = True

    checks = {
        "stateful_interface_exact": input_names == ["obs", "previous_action"]
        and output_names == ["continuous_actions", "previous_action_out"],
        "export_self_check_passed": float(export["max_action_error"]) <= 1.0e-5,
        "first_tick_reference_is_bounded_from_home_zero": first_reference_error <= 1.0e-5,
        "eight_tick_chain_respects_every_joint_bound": max(chain_errors) <= 1.0e-6,
        "state_output_equals_applied_action": max(state_output_errors) <= 1.0e-7,
        "invalid_dynamics_rejected": rejected_invalid_dynamics,
    }
    return {
        "checks": checks,
        "path": str(output_onnx),
        "sha256": sha256(output_onnx),
        "graph_name": model.graph.name,
        "inputs": input_names,
        "outputs": output_names,
        "max_first_reference_error": first_reference_error,
        "max_chain_bound_excess": max(chain_errors),
        "max_state_output_error": max(state_output_errors),
        "export_self_check": export,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--runner-patch", type=Path, required=True)
    parser.add_argument("--network-source", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--output-onnx", type=Path, required=True)
    args = parser.parse_args()

    require_cpu()
    root = args.playground_root.resolve()
    sys.path.insert(0, str(root))
    from playground.common import reference_residual_ppo_networks
    from playground.open_duck_mini_v2 import joystick

    environment, env, state = environment_contract(joystick)
    args.output_onnx.parent.mkdir(parents=True, exist_ok=True)
    onnx_result = onnx_contract(
        reference_residual_ppo_networks, env, state, args.output_onnx.resolve()
    )
    all_checks = {**environment["checks"], **onnx_result["checks"]}
    passed = all(all_checks.values())
    payload = {
        "schema_version": "ground_up_hard_vector_command_support_contract.v1",
        "status": "PASS_CPU_HARD_VECTOR_COMMAND_SUPPORT_CONTRACT"
        if passed
        else "FAIL_CPU_HARD_VECTOR_COMMAND_SUPPORT_CONTRACT",
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "rdk_access": False,
            "local_gpu_access": False,
            "colab_access": False,
        },
        "pinned_playground": {
            "root": str(root),
            "commit": "b9be205ac64488c23504ca42e5ec790337adeec3",
        },
        "artifacts": {
            "runner_patch": {
                "path": str(args.runner_patch.resolve()),
                "sha256": sha256(args.runner_patch.resolve()),
            },
            "network_source": {
                "path": str(args.network_source.resolve()),
                "sha256": sha256(args.network_source.resolve()),
            },
        },
        "environment": environment,
        "onnx": onnx_result,
        "all_checks": all_checks,
        "interpretation": (
            "This proves the CPU software transition and stateful export contract only. "
            "It is not training evidence, policy qualification, or robot clearance."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    failed = [name for name, value in all_checks.items() if not value]
    lines = [
        "# Ground-Up Hard-Vector Command-Support CPU Contract",
        "",
        f"status: `{payload['status']}`",
        "",
        f"runner patch SHA-256: `{payload['artifacts']['runner_patch']['sha256']}`",
        f"network source SHA-256: `{payload['artifacts']['network_source']['sha256']}`",
        "",
        f"failed checks: `{', '.join(failed) if failed else 'none'}`",
        "",
        "## Measured contract",
        "",
        "- 4,096 sampled forward commands stayed inside `[0.074, 0.080)` with "
        f"standard deviation `{environment['command_x']['std']:.8f}`; all other "
        "command axes were exactly zero.",
        "- Reset targets equal home; reset velocity/history are zero; and the first "
        "aggressive transition hits without exceeding all 14 target-rate bounds.",
        "- State info, reward inputs, and the returned observation carry the realized "
        "bounded action/targets rather than the unachievable raw request.",
        "- Stateful ONNX uses `obs`/`previous_action` inputs and "
        "`continuous_actions`/`previous_action_out` outputs; the eight-tick chain "
        f"measured `{onnx_result['max_chain_bound_excess']}` bound excess.",
        "- The graph uses broadcast-safe elementwise `Min` then `Max`; JAX/ONNX "
        f"first-action error is `{onnx_result['max_first_reference_error']:.3g}`.",
        "",
        payload["interpretation"],
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "failed": failed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
