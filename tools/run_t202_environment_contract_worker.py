#!/usr/bin/env python3
"""CPU worker for T202 default-off and enabled environment contracts."""

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


def configure(joystick, reference: Path, *, t202_enabled: bool):
    config = configure_environment(
        joystick,
        reference,
        enabled=True,
        deviation_scale=0.0,
    )
    config.winner_t31_action_margin_trainthrough = True
    if hasattr(config, "winner_t202_predicted_roll_risk"):
        config.winner_t202_predicted_roll_risk = t202_enabled
    elif t202_enabled:
        raise ValueError("enabled T202 worker loaded a non-T202 playground")
    return config


def default_off(playground: Path, reference: Path) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference, t202_enabled=False),
    )
    state = jax.jit(env.reset)(jax.random.PRNGKey(20200))
    digests = [tree_digest(state, prefix="t202_default_off")]
    actions = np.linspace(
        -0.35, 0.35, num=8 * 14, dtype=np.float32
    ).reshape(8, 14)
    step = jax.jit(env.step)
    for action in actions:
        state = step(state, jnp.asarray(action))
        digests.append(tree_digest(state, prefix="t202_default_off"))
    observation = np.asarray(jax.device_get(state.obs["state"]))
    return {
        "mode": "default_off",
        "playground": str(playground),
        "trajectory_digests": digests,
        "observation_shape": list(observation.shape),
        "finite": bool(np.isfinite(observation).all()),
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def metric_errors(env, state, t202) -> dict[str, float]:
    base_qpos = int(env._floating_base_qpos_addr)
    base_qvel = int(env._floating_base_qvel_addr)
    expected_risk = t202.predicted_roll_risk_rad(
        state.data.qpos[base_qpos + 3 : base_qpos + 7],
        state.data.qvel[base_qvel + 3],
    )
    expected_excess = t202.roll_risk_excess_rad(expected_risk)
    expected_cost = t202.roll_risk_cost(expected_risk)
    original = state.metrics["t202/original_clipped_reward"]
    expected_reward = t202.curriculum_reward(original, expected_cost)
    return {
        "risk": float(
            jnp.abs(
                state.metrics["t202/predicted_roll_risk_rad"]
                - expected_risk
            )
        ),
        "excess": float(
            jnp.abs(
                state.metrics["t202/roll_risk_excess_rad"]
                - expected_excess
            )
        ),
        "cost": float(
            jnp.abs(
                state.metrics["cost/t202_predicted_roll_risk"]
                - expected_cost
            )
        ),
        "reward": float(jnp.abs(state.reward - expected_reward)),
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
    from playground.common import t202_predicted_roll_risk as t202
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference, t202_enabled=True),
    )
    reset = jax.jit(env.reset)
    step = jax.jit(env.step)
    state = reset(jax.random.PRNGKey(seed))
    session = ort.InferenceSession(
        str(source_onnx), providers=["CPUExecutionProvider"]
    )
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    maximum_errors = {
        "risk": 0.0,
        "excess": 0.0,
        "cost": 0.0,
        "reward": 0.0,
    }
    maximum_risk = 0.0
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
        errors = metric_errors(env, state, t202)
        maximum_errors = {
            name: max(maximum_errors[name], value)
            for name, value in errors.items()
        }
        risk = float(
            state.metrics["t202/predicted_roll_risk_rad"]
        )
        cost = float(state.metrics["cost/t202_predicted_roll_risk"])
        reward = float(state.reward)
        maximum_risk = max(maximum_risk, risk)
        maximum_cost = max(maximum_cost, cost)
        minimum_reward = min(minimum_reward, reward)
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

    synthetic = reset(jax.random.PRNGKey(seed + 1))
    base_qvel = int(env._floating_base_qvel_addr)
    qvel = synthetic.data.qvel.at[base_qvel + 3].set(
        jnp.float32(10.0)
    )
    synthetic = synthetic.replace(
        data=synthetic.data.replace(qvel=qvel)
    )
    synthetic = step(synthetic, jnp.zeros(14, dtype=jnp.float32))
    synthetic_errors = metric_errors(env, synthetic, t202)
    synthetic_risk = float(
        synthetic.metrics["t202/predicted_roll_risk_rad"]
    )
    synthetic_cost = float(
        synthetic.metrics["cost/t202_predicted_roll_risk"]
    )
    synthetic_original = float(
        synthetic.metrics["t202/original_clipped_reward"]
    )
    synthetic_reward = float(synthetic.reward)

    checks = {
        "cpu_only": sorted(
            {device.platform for device in jax.devices()}
        )
        == ["cpu"],
        "observation_abi_115": observation.shape == (1, 115),
        "normal_policy_metric_and_reward_exact": all(
            value <= 1.0e-7 for value in maximum_errors.values()
        ),
        "synthetic_metric_and_reward_exact": all(
            value <= 1.0e-7 for value in synthetic_errors.values()
        ),
        "synthetic_path_exceeds_envelope": (
            synthetic_risk > t202.PASSING_ENVELOPE_RAD
            and synthetic_cost > 0.0
        ),
        "cost_is_outside_positive_reward_clip": (
            synthetic_reward
            == pytest_approx_subtraction(
                synthetic_original, synthetic_cost
            )
            and synthetic_reward < synthetic_original
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
        "maximum_policy_risk_rad": maximum_risk,
        "maximum_policy_cost": maximum_cost,
        "minimum_policy_reward": minimum_reward,
        "synthetic": {
            "roll_rate_seed_rad_s": 10.0,
            "risk_rad": synthetic_risk,
            "cost": synthetic_cost,
            "original_clipped_reward": synthetic_original,
            "final_reward": synthetic_reward,
            "metric_errors": synthetic_errors,
        },
        "done_ticks": done_ticks,
        "simulator_transitions": ticks + 1,
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def pytest_approx_subtraction(left: float, right: float) -> float:
    """Float32-equivalent subtraction used by the JAX environment."""
    return float(np.float32(left) - np.float32(right))


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
    parser.add_argument("--seed", type=int, default=202)
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
