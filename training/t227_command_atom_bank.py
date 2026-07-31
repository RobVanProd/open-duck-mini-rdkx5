"""T227 deterministic command strata crossed with T216's endpoint bank.

This module is training-only.  It changes neither the policy observation/action
ABI nor the exported deployment graph.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from brax.envs.wrappers import training as brax_training
import jax
import jax.numpy as jnp
from mujoco import mjx
from mujoco_playground._src import mjx_env
from mujoco_playground._src import wrapper as playground_wrapper


AXIS_NAME = "t227_command_atom_environment"
CONFIGURATION_STRATA = 8
COMMAND_STRATA = 4
CARTESIAN_STRATA = CONFIGURATION_STRATA * COMMAND_STRATA
COMMAND_ATOMS_M_S = jnp.asarray(
    [0.074, 0.077, 0.080],
    dtype=jnp.float32,
)
COMMAND_STRATUM_NAMES = (
    "broad_continuous",
    "exact_x_0p074",
    "exact_x_0p077",
    "exact_x_0p080",
)


def validate_population(population: int) -> None:
    """Require exact, equally repeated 8x4 Cartesian coverage."""
    if population <= 0 or population % CARTESIAN_STRATA != 0:
        raise ValueError(
            "T227 population must be a positive multiple of "
            f"{CARTESIAN_STRATA}"
        )


def configuration_category_ids(population: int) -> jax.Array:
    """Match T66/T98's existing environment-index modulo-eight mapping."""
    validate_population(population)
    return (
        jnp.arange(population, dtype=jnp.int32)
        % CONFIGURATION_STRATA
    )


def command_category_ids(population: int) -> jax.Array:
    """Assign broad/.074/.077/.080 across every configuration stratum."""
    validate_population(population)
    indices = jnp.arange(population, dtype=jnp.int32)
    return (indices // CONFIGURATION_STRATA) % COMMAND_STRATA


def cartesian_counts(population: int) -> dict[str, int]:
    """Return exact population counts for every configuration/command pair."""
    configuration = configuration_category_ids(population)
    command = command_category_ids(population)
    return {
        f"configuration_{config}:{COMMAND_STRATUM_NAMES[command_id]}": int(
            jnp.sum(
                (configuration == config)
                & (command == command_id)
            )
        )
        for command_id in range(COMMAND_STRATA)
        for config in range(CONFIGURATION_STRATA)
    }


def select_forward_command(
    sampled_forward: jax.Array,
    environment_index: jax.Array,
) -> jax.Array:
    """Keep one broad stratum and replace the other three with exact atoms."""
    category = (
        jnp.asarray(environment_index, dtype=jnp.int32)
        // CONFIGURATION_STRATA
    ) % COMMAND_STRATA
    atom_index = jnp.maximum(category - 1, 0)
    atom = COMMAND_ATOMS_M_S[atom_index]
    return jnp.where(category == 0, sampled_forward, atom)


def select_named_axis_forward(sampled_forward: jax.Array) -> jax.Array:
    """Select the T227 command using the vectorized environment slot."""
    return select_forward_command(
        sampled_forward,
        jax.lax.axis_index(AXIS_NAME),
    )


class CommandAtomDomainRandomizationVmapWrapper(
    playground_wrapper.Wrapper
):
    """Name the environment vmap axis used by the command sampler."""

    def __init__(
        self,
        env: mjx_env.MjxEnv,
        randomization_fn: Callable[
            [mjx.Model], tuple[mjx.Model, mjx.Model]
        ],
    ):
        super().__init__(env)
        self._mjx_model_v, self._in_axes = randomization_fn(
            self.mjx_model
        )

    def _env_fn(self, mjx_model: mjx.Model) -> mjx_env.MjxEnv:
        env = self.env
        env.unwrapped._mjx_model = mjx_model
        return env

    def reset(self, rng: jax.Array) -> mjx_env.State:
        validate_population(int(rng.shape[0]))

        def reset(mjx_model, key):
            env = self._env_fn(mjx_model=mjx_model)
            return env.reset(key)

        return jax.vmap(
            reset,
            in_axes=[self._in_axes, 0],
            axis_name=AXIS_NAME,
        )(self._mjx_model_v, rng)

    def step(
        self,
        state: mjx_env.State,
        action: jax.Array,
    ) -> mjx_env.State:
        validate_population(int(action.shape[0]))

        def step(mjx_model, item, command):
            env = self._env_fn(mjx_model=mjx_model)
            return env.step(item, command)

        return jax.vmap(
            step,
            in_axes=[self._in_axes, 0, 0],
            axis_name=AXIS_NAME,
        )(self._mjx_model_v, state, action)


def wrap_for_brax_training(
    env: mjx_env.MjxEnv,
    vision: bool = False,
    num_vision_envs: int = 1,
    episode_length: int = 1000,
    action_repeat: int = 1,
    randomization_fn: Callable | None = None,
) -> playground_wrapper.Wrapper:
    """Preserve T19's full reset while adding a named vectorization axis."""
    from playground.common.t19_support_trainthrough import (
        FullHandoffAutoResetWrapper,
    )

    del num_vision_envs
    if vision:
        raise ValueError("T227 is proprioceptive only")
    if randomization_fn is None:
        raise ValueError("T227 requires T216's endpoint-bank randomizer")
    env = CommandAtomDomainRandomizationVmapWrapper(
        env,
        randomization_fn,
    )
    env = brax_training.EpisodeWrapper(
        env,
        episode_length,
        action_repeat,
    )
    return FullHandoffAutoResetWrapper(env)


def training_readback(population: int) -> str:
    """Return the exact log line used by CPU and hosted validators."""
    validate_population(population)
    repetitions = population // CARTESIAN_STRATA
    return (
        "T227_COMMAND_ATOM_BANK="
        "configuration_strata=8,"
        "command_strata=4,"
        "command_groups=broad|0.074|0.077|0.080,"
        f"cartesian_repetitions={repetitions},"
        "reward=unchanged,cost=unchanged,"
        "policy_abi=unchanged,deployment_graph=unchanged"
    )
