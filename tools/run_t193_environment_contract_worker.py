#!/usr/bin/env python3
"""CPU worker for T193 default-off and enabled environment contracts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

import jax
import jax.numpy as jnp
import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t19_support_trainthrough_cpu_contract import (  # noqa: E402
    configure_environment,
    tree_digest,
)


def configure(joystick, reference: Path, *, t193_enabled: bool):
    config = configure_environment(
        joystick,
        reference,
        enabled=True,
        deviation_scale=0.0,
    )
    config.winner_t31_action_margin_trainthrough = True
    if hasattr(
        config, "winner_t193_corrected_dynamic_reference_support"
    ):
        config.winner_t193_corrected_dynamic_reference_support = (
            t193_enabled
        )
    elif t193_enabled:
        raise ValueError("enabled T193 worker loaded a non-T193 playground")
    return config


def default_off(playground: Path, reference: Path) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference, t193_enabled=False),
    )
    state = jax.jit(env.reset)(jax.random.PRNGKey(19300))
    digests = [tree_digest(state, prefix="t193_default_off")]
    actions = np.linspace(
        -0.35, 0.35, num=8 * 14, dtype=np.float32
    ).reshape(8, 14)
    step = jax.jit(env.step)
    for action in actions:
        state = step(state, jnp.asarray(action))
        digests.append(tree_digest(state, prefix="t193_default_off"))
    observation = np.asarray(jax.device_get(state.obs["state"]))
    return {
        "mode": "default_off",
        "playground": str(playground),
        "trajectory_digests": digests,
        "observation_shape": list(observation.shape),
        "finite": bool(np.isfinite(observation).all()),
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def enabled(
    playground: Path,
    reference: Path,
    source_onnx: Path,
    *,
    ticks: int,
    seed: int,
) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    from playground.common import (
        t193_corrected_dynamic_reference_support as t193,
    )
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference, t193_enabled=True),
    )
    reset = jax.jit(env.reset)
    step = jax.jit(env.step)
    state = reset(jax.random.PRNGKey(seed))
    session = ort.InferenceSession(
        str(source_onnx), providers=["CPUExecutionProvider"]
    )
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    requested = np.zeros(2, dtype=np.int64)
    matched = np.zeros(2, dtype=np.int64)
    reward_sum = 0.0
    maximum_metric_error = 0.0
    maximum_addition_error = 0.0
    finite = True
    done_ticks: list[int] = []
    command_rows: list[list[float]] = []

    for tick in range(ticks):
        observation = np.asarray(
            jax.device_get(state.obs["state"]), dtype=np.float32
        )[None, :]
        action, previous, hidden = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": previous,
                "h_in": hidden,
            },
        )
        state = step(state, jnp.asarray(action[0]))
        reference_motion = state.info["current_reference_motion"]
        contact = jnp.asarray(state.obs["state"][97:99] > 0.5)
        expected_reward = t193.single_support_balance_reward(
            env.get_gravity(state.data),
            env.get_gyro(state.data),
            contact,
            reference_motion,
        )
        expected_sides = t193.reference_support_sides(reference_motion)
        expected_matches = t193.matched_support_sides(
            contact, reference_motion
        )
        actual_reward = state.metrics[
            "reward/t193_reference_support_balance"
        ]
        actual_sides = jnp.asarray(
            [
                state.metrics["t193/reference_left_requested"],
                state.metrics["t193/reference_right_requested"],
            ]
        )
        actual_matches = jnp.asarray(
            [
                state.metrics["reward/t193_left_support_match"],
                state.metrics["reward/t193_right_support_match"],
            ]
        )
        original_reward = state.metrics["t193/original_reward"]
        metric_error = max(
            float(jnp.max(jnp.abs(actual_reward - expected_reward))),
            float(
                jnp.max(
                    jnp.abs(
                        actual_sides
                        - expected_sides.astype(jnp.float32)
                    )
                )
            ),
            float(
                jnp.max(
                    jnp.abs(
                        actual_matches
                        - expected_matches.astype(jnp.float32)
                    )
                )
            ),
        )
        addition_error = float(
            jnp.abs(
                state.reward
                - t193.curriculum_reward(
                    original_reward, expected_reward
                )
            )
        )
        maximum_metric_error = max(maximum_metric_error, metric_error)
        maximum_addition_error = max(
            maximum_addition_error, addition_error
        )
        requested += np.asarray(
            jax.device_get(expected_sides), dtype=np.int64
        )
        matched += np.asarray(
            jax.device_get(expected_matches), dtype=np.int64
        )
        reward_sum += float(jax.device_get(actual_reward))
        done = bool(np.asarray(jax.device_get(state.done)))
        if done:
            done_ticks.append(tick)
        command_rows.append(
            np.asarray(
                jax.device_get(state.info["command"][:3]),
                dtype=np.float64,
            ).tolist()
        )
        finite = finite and all(
            np.isfinite(value).all()
            for value in (
                observation,
                action,
                previous,
                hidden,
                np.asarray(jax.device_get(state.reward)),
            )
        )

    checks = {
        "cpu_only": sorted(
            {device.platform for device in jax.devices()}
        )
        == ["cpu"],
        "observation_abi_115": observation.shape == (1, 115),
        "reference_requests_both_support_sides": bool(
            np.all(requested > 0)
        ),
        "source_policy_matches_both_support_sides": bool(
            np.all(matched > 0)
        ),
        "support_reward_positive": reward_sum > 0.0,
        "environment_metric_matches_module_exact": (
            maximum_metric_error == 0.0
        ),
        "objective_addition_exact": maximum_addition_error == 0.0,
        "trajectory_finite": finite,
        "source_policy_survives_contract_window": not done_ticks,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "mode": "enabled",
        "playground": str(playground),
        "source_onnx": str(source_onnx),
        "ticks": ticks,
        "seed": seed,
        "checks": checks,
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
        "reference_requested_counts": {
            "left": int(requested[0]),
            "right": int(requested[1]),
        },
        "matched_support_counts": {
            "left": int(matched[0]),
            "right": int(matched[1]),
        },
        "support_reward_sum": reward_sum,
        "maximum_metric_error": maximum_metric_error,
        "maximum_objective_addition_error": maximum_addition_error,
        "done_ticks": done_ticks,
        "first_command": command_rows[0],
        "last_command": command_rows[-1],
        "simulator_transitions": ticks,
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("default_off", "enabled"), required=True
    )
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--source-onnx", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ticks", type=int, default=108)
    parser.add_argument("--seed", type=int, default=193)
    args = parser.parse_args()
    playground = args.playground.resolve()
    reference = args.reference.resolve()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.mode == "default_off":
        value = default_off(playground, reference)
    else:
        if args.source_onnx is None:
            raise ValueError("enabled mode requires --source-onnx")
        value = enabled(
            playground,
            reference,
            args.source_onnx.resolve(),
            ticks=args.ticks,
            seed=args.seed,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(value, allow_nan=False, sort_keys=True))
    return 0 if not value.get("failed_checks") else 1


if __name__ == "__main__":
    raise SystemExit(main())
