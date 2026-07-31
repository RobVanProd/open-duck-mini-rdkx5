#!/usr/bin/env python3
"""CPU worker for T185 default-off and enabled environment contracts."""

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


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t19_support_trainthrough_cpu_contract import (  # noqa: E402
    configure_environment,
    tree_digest,
)


def configure(joystick, reference: Path, *, t185_enabled: bool):
    config = configure_environment(
        joystick,
        reference,
        enabled=True,
        deviation_scale=1.0,
    )
    config.winner_t31_action_margin_trainthrough = True
    if hasattr(config, "winner_t185_in_episode_single_support_prefix"):
        config.winner_t185_in_episode_single_support_prefix = t185_enabled
    elif t185_enabled:
        raise ValueError("enabled T185 worker loaded a non-T185 playground")
    return config


def default_off(playground: Path, reference: Path) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference, t185_enabled=False),
    )
    state = jax.jit(env.reset)(jax.random.PRNGKey(18500))
    digests = [tree_digest(state, prefix="t185_default_off")]
    actions = np.linspace(
        -0.35, 0.35, num=8 * 14, dtype=np.float32
    ).reshape(8, 14)
    step = jax.jit(env.step)
    for action in actions:
        state = step(state, jnp.asarray(action))
        digests.append(tree_digest(state, prefix="t185_default_off"))
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
    *,
    env_count: int,
    seed: int,
) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    from playground.common import t185_in_episode_single_support_prefix as t185
    from playground.open_duck_mini_v2 import joystick

    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=configure(joystick, reference, t185_enabled=True),
    )
    reset = jax.jit(jax.vmap(env.reset))
    step = jax.jit(jax.vmap(env.step))
    keys = jax.random.split(jax.random.PRNGKey(seed), env_count)
    state = reset(keys)
    sides = np.asarray(jax.device_get(state.info["t185_support_side"]))
    anchors = np.asarray(jax.device_get(state.info["t185_support_phase"]))
    phases = np.asarray(jax.device_get(state.info["imitation_i"]))
    phase_vectors = np.asarray(
        jax.device_get(state.info["imitation_phase"])
    )
    remaining = np.asarray(
        jax.device_get(state.info["t185_prefix_ticks_remaining"])
    )
    reference_contacts = (
        np.asarray(
            jax.device_get(state.info["current_reference_motion"])
        )[:, 32:34]
        > 0.5
    )
    target_contacts = np.stack([sides == 0, sides == 1], axis=-1)
    expected_anchors = np.asarray([2, 15], dtype=np.int32)[sides]
    expected_vectors = np.asarray(
        jax.device_get(
            jax.jit(jax.vmap(t185.phase_vector))(
                jnp.asarray(expected_anchors, dtype=jnp.int32)
            )
        )
    )
    phase_vector_maximum_abs_error = float(
        np.max(np.abs(phase_vectors - expected_vectors))
    )

    timeline = []
    action = jnp.zeros((env_count, env.action_size), dtype=jnp.float32)
    for tick in range(1, t185.PREFIX_TICKS + 2):
        state = step(state, action)
        timeline.append(
            {
                "tick": tick,
                "phase": np.asarray(
                    jax.device_get(state.info["imitation_i"])
                ),
                "remaining": np.asarray(
                    jax.device_get(
                        state.info["t185_prefix_ticks_remaining"]
                    )
                ),
                "reward": np.asarray(jax.device_get(state.reward)),
                "support_reward": np.asarray(
                    jax.device_get(
                        state.metrics[
                            "reward/t185_single_support_balance"
                        ]
                    )
                ),
                "original_reward": np.asarray(
                    jax.device_get(
                        state.metrics["t185/original_reward"]
                    )
                ),
                "prefix_active": np.asarray(
                    jax.device_get(state.metrics["t185/prefix_active"])
                ),
            }
        )

    prefix_rows = timeline[: t185.PREFIX_TICKS]
    resumed = timeline[t185.PREFIX_TICKS]
    prefix_phases_exact = all(
        np.array_equal(row["phase"], expected_anchors)
        for row in prefix_rows
    )
    prefix_remaining_exact = all(
        np.array_equal(
            row["remaining"],
            np.full(
                env_count,
                t185.PREFIX_TICKS - row["tick"],
                dtype=np.int32,
            ),
        )
        for row in prefix_rows
    )
    prefix_rewards_exact = all(
        np.array_equal(row["reward"], row["support_reward"])
        and np.array_equal(
            row["prefix_active"],
            np.ones(env_count, dtype=np.float32),
        )
        for row in prefix_rows
    )
    resumed_phase = (expected_anchors + 1) % t185.REFERENCE_PERIOD_TICKS
    resumed_exact = (
        np.array_equal(resumed["phase"], resumed_phase)
        and np.array_equal(
            resumed["remaining"], np.zeros(env_count, dtype=np.int32)
        )
        and np.array_equal(
            resumed["prefix_active"],
            np.zeros(env_count, dtype=np.float32),
        )
        and np.array_equal(
            resumed["reward"], resumed["original_reward"]
        )
    )
    observation = np.asarray(jax.device_get(state.obs["state"]))
    checks = {
        "cpu_only": sorted(
            {device.platform for device in jax.devices()}
        )
        == ["cpu"],
        "both_support_sides_sampled": set(sides.tolist()) == {0, 1},
        "reference_anchors_exact": np.array_equal(
            anchors, expected_anchors
        )
        and np.array_equal(phases, expected_anchors),
        "reference_phase_vectors_exact": np.array_equal(
            phase_vectors, expected_vectors
        ),
        "reference_contact_targets_exact": np.array_equal(
            reference_contacts, target_contacts
        ),
        "prefix_stays_at_anchor_for_27_ticks": prefix_phases_exact,
        "prefix_counter_exact": prefix_remaining_exact
        and np.array_equal(
            remaining,
            np.full(env_count, t185.PREFIX_TICKS, dtype=np.int32),
        ),
        "prefix_reward_is_support_only": prefix_rewards_exact,
        "same_episode_locomotion_resume_exact": resumed_exact,
        "observation_abi_115_and_finite": (
            observation.shape == (env_count, 115)
            and np.isfinite(observation).all()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "mode": "enabled",
        "playground": str(playground),
        "env_count": env_count,
        "seed": seed,
        "checks": checks,
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
        "side_counts": {
            "left": int(np.sum(sides == 0)),
            "right": int(np.sum(sides == 1)),
        },
        "anchors": {
            "left": 2,
            "right": 15,
        },
        "phase_vector_maximum_abs_error": (
            phase_vector_maximum_abs_error
        ),
        "prefix_ticks": t185.PREFIX_TICKS,
        "simulator_transitions": env_count * (t185.PREFIX_TICKS + 1),
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("default_off", "enabled"), required=True
    )
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--env-count", type=int, default=256)
    parser.add_argument("--seed", type=int, default=185)
    args = parser.parse_args()
    playground = args.playground.resolve()
    reference = args.reference.resolve()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.mode == "default_off":
        value = default_off(playground, reference)
    else:
        value = enabled(
            playground,
            reference,
            env_count=args.env_count,
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
