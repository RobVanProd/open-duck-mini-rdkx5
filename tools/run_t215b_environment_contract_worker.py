#!/usr/bin/env python3
"""CPU worker for T215B default-off and enabled environment contracts."""

from __future__ import annotations

import argparse
import json
import math
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


def configure(joystick, reference: Path, *, enabled: bool):
    config = configure_environment(
        joystick,
        reference,
        enabled=True,
        deviation_scale=0.0,
    )
    config.winner_t31_action_margin_trainthrough = True
    for name in (
        "winner_t202_predicted_roll_risk",
        "winner_t209_dual_roll_cost",
    ):
        if hasattr(config, name):
            setattr(config, name, False)
    if hasattr(config, "winner_v127_constrained_cost"):
        config.winner_v127_constrained_cost = enabled
    elif enabled:
        raise ValueError("enabled T215B worker loaded a pre-V127 playground")
    if hasattr(config, "winner_t215b_axis_complete_tilt_cost"):
        config.winner_t215b_axis_complete_tilt_cost = enabled
    elif enabled:
        raise ValueError("enabled T215B worker loaded a non-T215B playground")
    return config


def default_off(playground: Path, reference: Path) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference, enabled=False),
    )
    state = jax.jit(env.reset)(jax.random.PRNGKey(21500))
    digests = [tree_digest(state, prefix="t215b_default_off")]
    actions = np.linspace(
        -0.35, 0.35, num=8 * 14, dtype=np.float32
    ).reshape(8, 14)
    step = jax.jit(env.step)
    for action in actions:
        state = step(state, jnp.asarray(action))
        digests.append(tree_digest(state, prefix="t215b_default_off"))
    observation = np.asarray(jax.device_get(state.obs["state"]))
    return {
        "mode": "default_off",
        "playground": str(playground),
        "trajectory_digests": digests,
        "observation_shape": list(observation.shape),
        "finite": bool(np.isfinite(observation).all()),
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def metric_errors(env, state, tilt) -> dict[str, float]:
    base_qpos = int(env._floating_base_qpos_addr)
    base_qvel = int(env._floating_base_qvel_addr)
    expected_roll, expected_pitch = tilt.predicted_axis_risks_rad(
        state.data.qpos[base_qpos + 3 : base_qpos + 7],
        state.data.qvel[base_qvel + 3],
        state.data.qvel[base_qvel + 4],
    )
    expected_roll_norm, expected_pitch_norm = (
        tilt.normalized_axis_risks(expected_roll, expected_pitch)
    )
    expected_score = jnp.maximum(
        expected_roll_norm, expected_pitch_norm
    )
    expected_excess = tilt.tilt_box_excess(expected_score)
    expected_cost = jnp.square(expected_excess)
    recorded_cost = state.info[
        "winner_v127_dense_torque_exceedance_cost"
    ]
    pairs = {
        "roll_risk": (
            state.metrics["t215b/predicted_roll_risk_rad"],
            expected_roll,
        ),
        "pitch_risk": (
            state.metrics["t215b/predicted_pitch_risk_rad"],
            expected_pitch,
        ),
        "roll_normalized": (
            state.metrics["t215b/normalized_roll_risk"],
            expected_roll_norm,
        ),
        "pitch_normalized": (
            state.metrics["t215b/normalized_pitch_risk"],
            expected_pitch_norm,
        ),
        "score": (
            state.metrics["t215b/tilt_box_score"],
            expected_score,
        ),
        "excess": (
            state.metrics["t215b/tilt_box_excess"],
            expected_excess,
        ),
        "cost_metric": (
            state.metrics["cost/t215b_predicted_tilt_box"],
            expected_cost,
        ),
        "cost_collector": (recorded_cost, expected_cost),
        "reward": (
            state.reward,
            state.metrics["t215b/original_clipped_reward"],
        ),
    }
    return {
        name: float(jnp.abs(actual - expected))
        for name, (actual, expected) in pairs.items()
    }


def synthetic_axis(
    *,
    env,
    reset,
    step,
    tilt,
    seed: int,
    axis: str,
) -> dict[str, Any]:
    state = reset(jax.random.PRNGKey(seed))
    base_qvel = int(env._floating_base_qvel_addr)
    rate_index = base_qvel + (3 if axis == "roll" else 4)
    qvel = state.data.qvel.at[rate_index].set(jnp.float32(10.0))
    state = state.replace(data=state.data.replace(qvel=qvel))
    state = step(state, jnp.zeros(14, dtype=jnp.float32))
    errors = metric_errors(env, state, tilt)
    return {
        "axis": axis,
        "seed_rate_rad_s": 10.0,
        "roll_risk_rad": float(
            state.metrics["t215b/predicted_roll_risk_rad"]
        ),
        "pitch_risk_rad": float(
            state.metrics["t215b/predicted_pitch_risk_rad"]
        ),
        "roll_normalized": float(
            state.metrics["t215b/normalized_roll_risk"]
        ),
        "pitch_normalized": float(
            state.metrics["t215b/normalized_pitch_risk"]
        ),
        "score": float(state.metrics["t215b/tilt_box_score"]),
        "excess": float(state.metrics["t215b/tilt_box_excess"]),
        "cost": float(state.metrics["cost/t215b_predicted_tilt_box"]),
        "original_clipped_reward": float(
            state.metrics["t215b/original_clipped_reward"]
        ),
        "final_reward": float(state.reward),
        "metric_errors": errors,
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
    from playground.common import t215b_axis_complete_tilt as tilt
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference, enabled=True),
    )
    reset = jax.jit(env.reset)
    step = jax.jit(env.step)
    state = reset(jax.random.PRNGKey(seed))
    session = ort.InferenceSession(
        str(source_onnx), providers=["CPUExecutionProvider"]
    )
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    error_names = (
        "roll_risk",
        "pitch_risk",
        "roll_normalized",
        "pitch_normalized",
        "score",
        "excess",
        "cost_metric",
        "cost_collector",
        "reward",
    )
    maximum_errors = {name: 0.0 for name in error_names}
    maximum_score = 0.0
    maximum_cost = 0.0
    minimum_reward = math.inf
    finite = True
    done_ticks: list[int] = []

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
        errors = metric_errors(env, state, tilt)
        maximum_errors = {
            name: max(maximum_errors[name], errors[name])
            for name in error_names
        }
        maximum_score = max(
            maximum_score,
            float(state.metrics["t215b/tilt_box_score"]),
        )
        maximum_cost = max(
            maximum_cost,
            float(state.metrics["cost/t215b_predicted_tilt_box"]),
        )
        minimum_reward = min(minimum_reward, float(state.reward))
        if bool(np.asarray(jax.device_get(state.done))):
            done_ticks.append(tick)
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

    synthetic = {
        axis: synthetic_axis(
            env=env,
            reset=reset,
            step=step,
            tilt=tilt,
            seed=seed + index + 1,
            axis=axis,
        )
        for index, axis in enumerate(("roll", "pitch"))
    }
    tolerance = 1.0e-7
    checks = {
        "cpu_only": sorted(
            {device.platform for device in jax.devices()}
        )
        == ["cpu"],
        "observation_abi_115": observation.shape == (1, 115),
        "normal_policy_metric_and_reward_exact": all(
            value <= tolerance for value in maximum_errors.values()
        ),
        "both_synthetic_axes_metric_and_reward_exact": all(
            value <= tolerance
            for item in synthetic.values()
            for value in item["metric_errors"].values()
        ),
        "both_synthetic_axes_exceed_box": all(
            item["score"] > 1.0
            and item["excess"] > 0.0
            and item["cost"] > 0.0
            for item in synthetic.values()
        ),
        "synthetic_dominant_axis_exact": (
            synthetic["roll"]["roll_normalized"]
            > synthetic["roll"]["pitch_normalized"]
            and synthetic["pitch"]["pitch_normalized"]
            > synthetic["pitch"]["roll_normalized"]
        ),
        "cost_is_unscaled_squared_box_excess": all(
            math.isclose(
                item["cost"],
                item["excess"] * item["excess"],
                rel_tol=1.0e-6,
                abs_tol=tolerance,
            )
            for item in synthetic.values()
        ),
        "cost_is_outside_and_does_not_change_reward": all(
            item["final_reward"] == item["original_clipped_reward"]
            for item in synthetic.values()
        ),
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
        "maximum_metric_errors": maximum_errors,
        "maximum_policy_box_score": maximum_score,
        "maximum_policy_cost": maximum_cost,
        "minimum_policy_reward": minimum_reward,
        "synthetic": synthetic,
        "done_ticks": done_ticks,
        "simulator_transitions": ticks + 2,
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
    parser.add_argument("--seed", type=int, default=215)
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
