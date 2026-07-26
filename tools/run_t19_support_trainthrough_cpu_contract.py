#!/usr/bin/env python3
"""Run T19's default-off, support-prefix, and full-reset CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS
    / "t19_support_trainthrough_cpu_recovery_preregistration.json"
)
RESULT = ANALYSIS / "t19_support_trainthrough_cpu_result.json"
MARKDOWN = ANALYSIS / "T19_SUPPORT_TRAINTHROUGH_CPU_RESULT_20260726.md"
COMMON_INFO_KEYS = (
    "rng",
    "step",
    "command",
    "last_act",
    "last_last_act",
    "last_last_last_act",
    "motor_targets",
    "ground_up_actuator_bridge_target_history",
    "ground_up_actuator_bridge_applied_targets",
    "action_history",
    "imitation_i",
    "imitation_phase",
    "policy_hidden",
    "winner_v3_actuator_gain_ratio",
    "winner_v3_actuator_tau_s",
    "winner_v3_actuator_delay_ticks",
    "winner_v3_additional_action_delay_ticks",
    "winner_v3_imu_delay_ticks",
    "winner_v3_native_quantization",
)
RESET_INFO_KEYS = (
    "step",
    "command",
    "last_act",
    "last_last_act",
    "last_last_last_act",
    "motor_targets",
    "ground_up_actuator_bridge_target_history",
    "ground_up_actuator_bridge_applied_targets",
    "action_history",
    "imitation_i",
    "imitation_phase",
    "policy_hidden",
    "t19_source_motor_targets",
    "t19_support_prefix_valid",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def _array_digest(items: list[tuple[str, np.ndarray]]) -> str:
    digest = hashlib.sha256()
    for name, value in items:
        array = np.ascontiguousarray(value)
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(str(array.dtype).encode())
        digest.update(b"\0")
        digest.update(json.dumps(list(array.shape)).encode())
        digest.update(b"\0")
        digest.update(array.tobytes())
        digest.update(b"\0")
    return digest.hexdigest()


def tree_digest(value: Any, *, prefix: str = "root") -> str:
    import jax

    leaves, _ = jax.tree_util.tree_flatten(value)
    items = [
        (f"{prefix}/{index}", np.asarray(jax.device_get(leaf)))
        for index, leaf in enumerate(leaves)
    ]
    items.append(
        (
            f"{prefix}/leaf_count",
            np.asarray([len(leaves)], dtype=np.int64),
        )
    )
    return _array_digest(items)


def tree_difference(left: Any, right: Any) -> dict[str, Any]:
    import jax

    left_leaves, left_structure = jax.tree_util.tree_flatten(left)
    right_leaves, right_structure = jax.tree_util.tree_flatten(right)
    if left_structure != right_structure:
        return {
            "structure_exact": False,
            "leaf_count": [len(left_leaves), len(right_leaves)],
            "mismatches": [],
        }
    mismatches = []
    for index, (left_leaf, right_leaf) in enumerate(
        zip(left_leaves, right_leaves, strict=True)
    ):
        left_array = np.asarray(jax.device_get(left_leaf))
        right_array = np.asarray(jax.device_get(right_leaf))
        if np.array_equal(left_array, right_array, equal_nan=True):
            continue
        if (
            left_array.shape == right_array.shape
            and np.issubdtype(left_array.dtype, np.number)
            and np.issubdtype(right_array.dtype, np.number)
        ):
            finite = np.isfinite(left_array) & np.isfinite(right_array)
            maximum = (
                float(
                    np.max(
                        np.abs(
                            left_array[finite].astype(float)
                            - right_array[finite].astype(float)
                        )
                    )
                )
                if np.any(finite)
                else None
            )
        else:
            maximum = None
        mismatches.append(
            {
                "leaf": index,
                "left_shape": list(left_array.shape),
                "right_shape": list(right_array.shape),
                "left_dtype": str(left_array.dtype),
                "right_dtype": str(right_array.dtype),
                "maximum_finite_absolute_difference": maximum,
            }
        )
    return {
        "structure_exact": True,
        "leaf_count": len(left_leaves),
        "mismatches": mismatches,
    }


def configure_environment(
    joystick,
    reference: Path,
    *,
    enabled: bool,
    deviation_scale: float,
):
    config = joystick.default_config()
    config.reference_feature_table_path = str(reference)
    config.recurrent_hidden_dim = 64
    config.nominal_reference_bootstrap = True
    config.ground_up_hard_vector_command_support = True
    config.ground_up_command_support_range = [0.074, 0.080]
    config.ground_up_action_velocity_limits_rad_s = [
        1.0,
        0.75,
        1.5,
        1.5,
        1.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.75,
        1.25,
        1.0,
        1.25,
    ]
    config.ground_up_measured_actuator_bridge = True
    config.ground_up_applied_target_observation = True
    config.reference_start_phase = 0
    config.ground_up_signed_progress_objective = True
    config.winner_v3_variable_configuration = True
    config.winner_v3_deviation_scale = deviation_scale
    config.winner_v119_train_transition_match = True
    if hasattr(config, "winner_t19_support_trainthrough"):
        config.winner_t19_support_trainthrough = enabled
    elif enabled:
        raise ValueError("T19 enabled worker loaded a non-T19 playground")
    config.noise_config.level = deviation_scale
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 3
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 3
    config.push_config.enable = False
    return config


def state_contract_digest(state) -> str:
    info = {
        name: state.info[name]
        for name in COMMON_INFO_KEYS
        if name in state.info
    }
    return tree_digest(
        (
            state.data,
            state.obs,
            state.reward,
            state.done,
            state.metrics,
            info,
        ),
        prefix="state",
    )


def default_off_worker(
    playground: Path,
    reference: Path,
) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    import jax
    import jax.numpy as jnp
    from playground.open_duck_mini_v2 import joystick

    config = configure_environment(
        joystick,
        reference,
        enabled=False,
        deviation_scale=0.0,
    )
    env = joystick.Joystick(
        task="flat_terrain_backlash", config=config
    )
    state = jax.jit(env.reset)(jax.random.PRNGKey(100))
    digests = [state_contract_digest(state)]
    actions = np.linspace(
        -0.35, 0.35, num=8 * 14, dtype=np.float32
    ).reshape(8, 14)
    step = jax.jit(env.step)
    for action in actions:
        state = step(state, jnp.asarray(action))
        digests.append(state_contract_digest(state))
    return {
        "mode": "default_off",
        "playground": str(playground),
        "trajectory_digests": digests,
        "observation_shape": list(
            np.asarray(jax.device_get(state.obs["state"])).shape
        ),
        "finite": bool(
            np.isfinite(
                np.asarray(jax.device_get(state.obs["state"]))
            ).all()
        ),
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def _max_abs(value: np.ndarray, expected: np.ndarray) -> float:
    return float(np.max(np.abs(value.astype(float) - expected.astype(float))))


def enabled_worker(
    playground: Path,
    reference: Path,
    *,
    env_count: int,
    seed: int,
) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    import jax
    import jax.numpy as jnp
    from playground.common import t19_support_trainthrough as t19
    from playground.common import winner_v3_variable_configuration as winner_v3
    from playground.open_duck_mini_v2 import joystick

    config = configure_environment(
        joystick,
        reference,
        enabled=True,
        deviation_scale=1.0,
    )
    env = joystick.Joystick(
        task="flat_terrain_backlash", config=config
    )
    prefix_env = t19.SupportPrefixWrapper(env)
    randomizer = winner_v3.make_winner_v3_configuration_randomizer(
        torso_body_id=winner_v3.TORSO_BODY_ID,
        deviation_scale=1.0,
    )
    model_keys = jax.random.split(
        jax.random.PRNGKey(seed + 1), env_count
    )
    model_v, in_axes = randomizer(env.mjx_model, model_keys)

    def frozen_randomizer(_):
        return model_v, in_axes

    wrapped = t19.wrap_for_brax_training(
        prefix_env,
        episode_length=2,
        action_repeat=1,
        randomization_fn=frozen_randomizer,
    )
    reset_keys = jax.random.split(jax.random.PRNGKey(seed), env_count)
    state = jax.jit(wrapped.reset)(reset_keys)
    home = np.asarray(env._default_actuator, dtype=np.float32)
    support = np.asarray(t19.SUPPORT_ACTION, dtype=np.float32)
    last_action = np.asarray(jax.device_get(state.info["last_act"]))
    motor_targets = np.asarray(
        jax.device_get(state.info["motor_targets"])
    )
    source_targets = np.asarray(
        jax.device_get(state.info["t19_source_motor_targets"])
    )
    action_history = np.asarray(
        jax.device_get(state.info["action_history"])
    )
    phase = np.asarray(
        jax.device_get(state.info["imitation_phase"])
    )
    hidden = np.asarray(jax.device_get(state.info["policy_hidden"]))
    valid = np.asarray(
        jax.device_get(state.info["t19_support_prefix_valid"])
    )
    source_obs = np.asarray(jax.device_get(state.obs["state"]))
    applied = np.asarray(
        jax.device_get(
            state.info["ground_up_actuator_bridge_applied_targets"]
        )
    )
    expected_applied_source = (
        home[None, :]
        + np.asarray(
            t19.inverse_action(
                jnp.asarray((applied - home[None, :]) / 0.25)
            )
        )
        * np.float32(0.25)
    )
    snapshot_data = tree_digest(state.data, prefix="reset_data")
    snapshot_data_value = state.data
    snapshot_obs = tree_digest(state.obs, prefix="reset_obs")
    snapshot_info = tree_digest(
        {name: state.info[name] for name in RESET_INFO_KEYS},
        prefix="reset_info",
    )

    zero_source = jnp.zeros((env_count, 14), dtype=jnp.float32)
    step = jax.jit(wrapped.step)
    state = step(state, zero_source)
    state = step(state, zero_source)
    done = np.asarray(jax.device_get(state.done))
    reset_data = tree_digest(state.data, prefix="reset_data")
    reset_obs = tree_digest(state.obs, prefix="reset_obs")
    reset_info = tree_digest(
        {name: state.info[name] for name in RESET_INFO_KEYS},
        prefix="reset_info",
    )
    reset_data_difference = tree_difference(
        snapshot_data_value, state.data
    )

    checks = {
        "cpu_only": sorted(
            {device.platform for device in jax.devices()}
        )
        == ["cpu"],
        "all_prefixes_valid": bool(np.all(valid)),
        "final_support_action_exact": np.array_equal(
            last_action,
            np.broadcast_to(support, last_action.shape),
        ),
        "final_motor_target_exact": (
            _max_abs(
                motor_targets,
                np.broadcast_to(
                    home + support * np.float32(0.25),
                    motor_targets.shape,
                ),
            )
            <= 32 * np.finfo(np.float32).eps
        ),
        "source_target_returns_home": (
            _max_abs(
                source_targets,
                np.broadcast_to(home, source_targets.shape),
            )
            <= 32 * np.finfo(np.float32).eps
        ),
        "source_delay_history_zero": np.count_nonzero(action_history)
        == 0,
        "phase_reset_exact": np.array_equal(
            phase,
            np.broadcast_to(
                np.asarray([1.0, 0.0], dtype=np.float32),
                phase.shape,
            ),
        ),
        "policy_hidden_reset_exact": np.count_nonzero(hidden) == 0,
        "applied_target_observation_exact": (
            _max_abs(source_obs[:, 83:97], expected_applied_source)
            <= 32 * np.finfo(np.float32).eps
        ),
        "all_observations_finite": bool(np.isfinite(source_obs).all()),
        "episode_boundary_reached": bool(np.all(done != 0)),
        "full_reset_data_exact": (
            reset_data_difference["structure_exact"]
            and reset_data_difference["mismatches"] == []
        ),
        "full_reset_observation_exact": reset_obs == snapshot_obs,
        "full_reset_dynamic_info_exact": reset_info == snapshot_info,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    return {
        "mode": "enabled",
        "playground": str(playground),
        "env_count": env_count,
        "seed": seed,
        "checks": checks,
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
        "maximum_errors": {
            "motor_target_rad": _max_abs(
                motor_targets,
                np.broadcast_to(
                    home + support * np.float32(0.25),
                    motor_targets.shape,
                ),
            ),
            "source_target_rad": _max_abs(
                source_targets,
                np.broadcast_to(home, source_targets.shape),
            ),
            "applied_target_observation_rad": _max_abs(
                source_obs[:, 83:97], expected_applied_source
            ),
        },
        "prefix_valid_count": int(np.count_nonzero(valid)),
        "episode_reset_count": int(np.count_nonzero(done)),
        "reset_data_difference": reset_data_difference,
        "reset_data_byte_digest_exact": reset_data == snapshot_data,
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def worker_main(args: argparse.Namespace) -> int:
    playground = args.playground.resolve()
    reference = args.reference.resolve()
    if args.worker == "default_off":
        value = default_off_worker(playground, reference)
    elif args.worker == "enabled":
        value = enabled_worker(
            playground,
            reference,
            env_count=args.env_count,
            seed=args.seed,
        )
    else:
        raise ValueError(args.worker)
    args.worker_output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(value, allow_nan=False, sort_keys=True))
    return 0


def verify_receipt(value: dict[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T19 frozen receipt changed: {label}")


def run_worker(
    mode: str,
    playground: Path,
    reference: Path,
    output: Path,
    *,
    env_count: int,
    seed: int,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        mode,
        "--playground",
        str(playground),
        "--reference",
        str(reference),
        "--env-count",
        str(env_count),
        "--seed",
        str(seed),
        "--worker-output",
        str(output),
    ]
    environment = dict(os.environ)
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
            "JAX_COMPILATION_CACHE_DIR": str(
                Path(
                    "D:/CodexArtifacts/open-duck-policy/"
                    "jax_compilation_cache"
                )
            ),
        }
    )
    completed = subprocess.run(
        command,
        cwd=playground,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T19 worker failed mode={mode} rc={completed.returncode}\n"
            f"{completed.stdout[-12000:]}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def formal_main(args: argparse.Namespace) -> int:
    if not args.execute:
        raise SystemExit("T19 formal contract requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T19 path: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    basis = {
        key: prereg[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "playgrounds",
            "contract",
            "decision_rule",
            "authority",
            "execution_now",
        )
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T19_SUPPORT_TRAINTHROUGH_CPU_RECOVERY"
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T19 preregistration identity changed")
    for name, value in prereg["sources"].items():
        verify_receipt(value, name)
    args.work_root.mkdir(parents=True)
    reference = Path(prereg["contract"]["reference_path"])
    base = Path(prereg["playgrounds"]["base"]["path"])
    composed = Path(prereg["playgrounds"]["composed"]["path"])
    base_value = run_worker(
        "default_off",
        base,
        reference,
        args.work_root / "base_default_off.json",
        env_count=1,
        seed=prereg["contract"]["seed"],
    )
    composed_value = run_worker(
        "default_off",
        composed,
        reference,
        args.work_root / "composed_default_off.json",
        env_count=1,
        seed=prereg["contract"]["seed"],
    )
    enabled_value = run_worker(
        "enabled",
        composed,
        reference,
        args.work_root / "enabled.json",
        env_count=prereg["contract"]["variable_configuration_envs"],
        seed=prereg["contract"]["seed"],
    )
    checks = {
        "default_off_trajectory_bit_exact": (
            base_value["trajectory_digests"]
            == composed_value["trajectory_digests"]
        ),
        "default_off_shapes_exact": (
            base_value["observation_shape"]
            == composed_value["observation_shape"]
            == [115]
        ),
        "default_off_finite": (
            base_value["finite"] and composed_value["finite"]
        ),
        "all_enabled_checks_pass": enabled_value["failed_checks"] == [],
        "cpu_only": (
            base_value["platforms"]
            == composed_value["platforms"]
            == enabled_value["platforms"]
            == ["cpu"]
        ),
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result_basis = {
        "schema_version": "open_duck.t19_support_cpu_result.v1",
        "status": (
            "PASS_T19_SUPPORT_TRAINTHROUGH_CPU_CONTRACT"
            if not failed
            else "HOLD_T19_SUPPORT_TRAINTHROUGH_CPU_CONTRACT"
        ),
        "decision": (
            "EARN_T19_ONE_UPDATE_CPU_CONTRACT"
            if not failed
            else "CLOSE_T19_SUPPORT_TRAINTHROUGH_IMPLEMENTATION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "default_off": {
            "base": base_value,
            "composed": composed_value,
        },
        "enabled": enabled_value,
        "execution": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T19 support train-through CPU result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Variable-configuration support prefixes: "
                    f"`{enabled_value['prefix_valid_count']}/"
                    f"{enabled_value['env_count']}`"
                ),
                (
                    "- Complete episode resets: "
                    f"`{enabled_value['episode_reset_count']}/"
                    f"{enabled_value['env_count']}`"
                ),
                "- Optimizer/hosted/robot execution: `0/0/0`",
                f"- Result SHA-256: `{value['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--worker",
        choices=("default_off", "enabled"),
    )
    parser.add_argument("--playground", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--env-count", type=int, default=64)
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--worker-output", type=Path)
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.worker:
        required = (
            args.playground,
            args.reference,
            args.worker_output,
        )
        if any(value is None for value in required):
            raise SystemExit("T19 worker arguments are incomplete")
        return worker_main(args)
    if args.work_root is None:
        raise SystemExit("T19 formal contract requires --work-root")
    return formal_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
