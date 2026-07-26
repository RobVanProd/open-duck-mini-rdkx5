"""Exact T18 support-coordinate transition and episode-reset helpers.

This module is copied into a composed playground tree by the T19 composer.
The feature is default-off and exists only to CPU-contract a train-through
continuation before any hosted run can be considered.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from brax.envs.wrappers import training as brax_training
import jax
import jax.numpy as jnp
import numpy as np
from mujoco_playground._src import collision
from mujoco_playground._src import mjx_env
from mujoco_playground._src import wrapper as playground_wrapper


ACTION_SIZE = 14
OBS_SIZE = 115
CALIBRATION_TICKS = 250
ACTION_SCALE_RAD = np.float32(0.25)
SUPPORT_ACTION = np.asarray(
    [
        0.0,
        0.0,
        -0.5,
        0.25,
        0.25,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.5,
        0.25,
        0.25,
    ],
    dtype=np.float32,
)
CALIBRATOR_MAX_ACTION_DELTA = np.asarray(
    [
        0.07999950647354126,
        0.05999951437115669,
        0.11999950557947159,
        0.11999950557947159,
        0.11999950557947159,
        0.03999951481819153,
        0.03999951481819153,
        0.03999951481819153,
        0.03999951481819153,
        0.03999951481819153,
        0.05999951437115669,
        0.09999950230121613,
        0.07999950647354126,
        0.09999950230121613,
    ],
    dtype=np.float32,
)
RATE_LIMITS_RAD_S = np.asarray(
    [
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
    ],
    dtype=np.float32,
)
SOURCE_RATE_LIMITS_RAD_S = np.asarray(
    [
        1.0,
        0.75,
        1.4736209064722061,
        1.4300791546702385,
        1.3976470567286015,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.75,
        1.25,
        1.0,
        1.2215287424623966,
    ],
    dtype=np.float32,
)
MAX_ACTION_DELTA = (
    RATE_LIMITS_RAD_S * np.float32(0.02) / ACTION_SCALE_RAD
).astype(np.float32)
SOURCE_MAX_ACTION_DELTA = (
    SOURCE_RATE_LIMITS_RAD_S * np.float32(0.02) / ACTION_SCALE_RAD
).astype(np.float32)


def forward_action(source_action: jax.Array) -> jax.Array:
    """Map source action coordinates into the bounded support coordinate."""
    source = jnp.asarray(source_action, dtype=jnp.float32)
    support = jnp.asarray(SUPPORT_ACTION, dtype=jnp.float32)
    slope = jnp.where(
        source >= jnp.float32(0.0),
        jnp.float32(1.0) - support,
        jnp.float32(1.0) + support,
    )
    return support + source * slope


def inverse_action(final_action: jax.Array) -> jax.Array:
    """Map a physical support-coordinate action back to source coordinates."""
    final = jnp.asarray(final_action, dtype=jnp.float32)
    support = jnp.asarray(SUPPORT_ACTION, dtype=jnp.float32)
    slope = jnp.where(
        final >= support,
        jnp.float32(1.0) - support,
        jnp.float32(1.0) + support,
    )
    return (final - support) / slope


def inverse_joint_position(
    final_position_rad: jax.Array,
    home_position_rad: jax.Array,
) -> jax.Array:
    """Map physical joint position through T17's observation inverse."""
    home = jnp.asarray(home_position_rad, dtype=jnp.float32)
    final = jnp.asarray(final_position_rad, dtype=jnp.float32)
    normalized = (final - home) / jnp.float32(ACTION_SCALE_RAD)
    return home + inverse_action(normalized) * jnp.float32(ACTION_SCALE_RAD)


def _observation_parameters(
    home_position_rad: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array, jax.Array]:
    center = jnp.zeros(OBS_SIZE, dtype=jnp.float32)
    base = jnp.zeros(OBS_SIZE, dtype=jnp.float32)
    upper = jnp.ones(OBS_SIZE, dtype=jnp.float32)
    lower = jnp.ones(OBS_SIZE, dtype=jnp.float32)
    support = jnp.asarray(SUPPORT_ACTION, dtype=jnp.float32)
    support_rad = support * jnp.float32(ACTION_SCALE_RAD)
    home = jnp.asarray(home_position_rad, dtype=jnp.float32)

    center = center.at[13:27].set(support_rad)
    upper = upper.at[13:27].set(jnp.float32(1.0) - support)
    lower = lower.at[13:27].set(jnp.float32(1.0) + support)
    for start in (41, 55, 69):
        center = center.at[start : start + ACTION_SIZE].set(support)
        upper = upper.at[start : start + ACTION_SIZE].set(
            jnp.float32(1.0) - support
        )
        lower = lower.at[start : start + ACTION_SIZE].set(
            jnp.float32(1.0) + support
        )
    center = center.at[83:97].set(home + support_rad)
    base = base.at[83:97].set(home)
    upper = upper.at[83:97].set(jnp.float32(1.0) - support)
    lower = lower.at[83:97].set(jnp.float32(1.0) + support)
    return center, base, upper, lower


def inverse_observation(
    final_observation: jax.Array,
    home_position_rad: jax.Array,
) -> jax.Array:
    """Map the 115-D physical observation into V121 source coordinates."""
    final = jnp.asarray(final_observation, dtype=jnp.float32)
    center, base, upper, lower = _observation_parameters(
        home_position_rad
    )
    slope = jnp.where(final >= center, upper, lower)
    return base + (final - center) / slope


def next_calibration_action(previous_action: jax.Array) -> jax.Array:
    """Reproduce the frozen universal calibrator's action branch exactly."""
    previous = jnp.asarray(previous_action, dtype=jnp.float32)
    target = jnp.asarray(SUPPORT_ACTION, dtype=jnp.float32)
    maximum_delta = jnp.asarray(
        CALIBRATOR_MAX_ACTION_DELTA, dtype=jnp.float32
    )
    lower = jnp.maximum(previous - maximum_delta, jnp.float32(-1.0))
    upper = jnp.minimum(previous + maximum_delta, jnp.float32(1.0))
    return jnp.maximum(jnp.minimum(target, upper), lower)


class SupportPrefixWrapper(playground_wrapper.Wrapper):
    """Create the exact unscored 250-tick T18 support handoff at reset."""

    def __init__(self, env: Any):
        super().__init__(env)

    def _prefix_info(self, state: mjx_env.State) -> dict[str, Any]:
        info = dict(state.info)
        info["command"] = jnp.zeros(7, dtype=jnp.float32)
        info["imitation_i"] = jnp.asarray(
            0, dtype=jnp.asarray(info["imitation_i"]).dtype
        )
        info["imitation_phase"] = jnp.asarray(
            [1.0, 0.0], dtype=jnp.float32
        )
        if info["current_reference_motion"].size:
            info[
                "current_reference_motion"
            ] = self.env.PRM.get_reference_motion(0.0, 0.0, 0.0, 0)
        return info

    def _refresh_observation(
        self,
        state: mjx_env.State,
        info: dict[str, Any],
    ) -> Any:
        contact = jnp.asarray(
            [
                collision.geoms_colliding(
                    state.data, geom_id, self.env._floor_geom_id
                )
                for geom_id in self.env._feet_geom_id
            ]
        )
        return self.env._get_obs(state.data, info, contact)

    def _execute_prefix(
        self,
        initial: mjx_env.State,
    ) -> tuple[
        mjx_env.State,
        jax.Array,
        jax.Array,
        jax.Array,
        jax.Array,
        jax.Array,
    ]:
        previous = jnp.zeros(ACTION_SIZE, dtype=jnp.float32)
        valid = jnp.asarray(True)

        def body(carry, _):
            state, previous_external, support_valid = carry
            state = state.replace(info=self._prefix_info(state))
            external_action = next_calibration_action(previous_external)
            next_state = self.env.step(
                state, inverse_action(external_action)
            )
            next_valid = support_valid & (next_state.done == 0)
            diagnostic = (
                external_action,
                next_state.info["motor_targets"],
                next_state.info["t19_source_motor_targets"],
            )
            return (next_state, external_action, next_valid), diagnostic

        (state, previous, valid), diagnostic = jax.lax.scan(
            body,
            (initial, previous, valid),
            xs=None,
            length=CALIBRATION_TICKS,
        )
        actions, motor_targets, source_motor_targets = diagnostic
        return (
            state,
            previous,
            valid,
            actions,
            motor_targets,
            source_motor_targets,
        )

    def prefix_diagnostic(self, rng: jax.Array) -> dict[str, jax.Array]:
        """Return the complete unscored prefix trace without finalizing reset."""
        initial = self.env.reset(rng)
        initial = initial.replace(info=self._prefix_info(initial))
        (
            _,
            _,
            valid,
            actions,
            motor_targets,
            source_motor_targets,
        ) = self._execute_prefix(initial)
        return {
            "valid": valid,
            "actions": actions,
            "motor_targets": motor_targets,
            "source_motor_targets": source_motor_targets,
        }

    def reset(self, rng: jax.Array) -> mjx_env.State:
        initial = self.env.reset(rng)
        locomotion_command = initial.info["command"]
        initial = initial.replace(info=self._prefix_info(initial))
        state, previous, valid, _, _, _ = self._execute_prefix(initial)
        info = dict(state.info)
        info["step"] = jnp.zeros_like(info["step"])
        info["command"] = locomotion_command
        info["imitation_i"] = jnp.asarray(
            0, dtype=jnp.asarray(info["imitation_i"]).dtype
        )
        info["imitation_phase"] = jnp.asarray(
            [1.0, 0.0], dtype=jnp.float32
        )
        if info["current_reference_motion"].size:
            info[
                "current_reference_motion"
            ] = self.env.PRM.get_reference_motion(
                locomotion_command[0],
                locomotion_command[1],
                locomotion_command[2],
                0,
            )
        info["policy_hidden"] = jnp.zeros_like(info["policy_hidden"])
        info["action_history"] = jnp.zeros_like(info["action_history"])
        info["t19_source_motor_targets"] = self.env._default_actuator
        info["t19_support_prefix_valid"] = valid
        state = state.replace(info=info)
        observation = self._refresh_observation(state, info)
        metrics = jax.tree_util.tree_map(jnp.zeros_like, state.metrics)
        return state.replace(
            obs=observation,
            reward=jnp.zeros_like(state.reward),
            done=jnp.zeros_like(state.done),
            metrics=metrics,
        )


_AUTO_RESET_EXCLUDED_INFO = frozenset(
    {
        "rng",
        "first_state",
        "first_obs",
        "steps",
        "truncation",
        "t19_reset_info",
    }
)


class FullHandoffAutoResetWrapper(playground_wrapper.Wrapper):
    """Reset actuator/history state as well as physics and observations."""

    def reset(self, rng: jax.Array) -> mjx_env.State:
        state = self.env.reset(rng)
        reset_info = {
            name: value
            for name, value in state.info.items()
            if name not in _AUTO_RESET_EXCLUDED_INFO
        }
        state.info["t19_reset_info"] = reset_info
        state.info["first_state"] = state.data
        state.info["first_obs"] = state.obs
        return state

    def step(
        self,
        state: mjx_env.State,
        action: jax.Array,
    ) -> mjx_env.State:
        if "steps" in state.info:
            steps = jnp.where(
                state.done,
                jnp.zeros_like(state.info["steps"]),
                state.info["steps"],
            )
            state.info.update(steps=steps)
        reset_info = state.info["t19_reset_info"]
        state = state.replace(done=jnp.zeros_like(state.done))
        state = self.env.step(state, action)

        def where_done(reset_value, current_value):
            done = state.done
            if done.shape:
                done = jnp.reshape(
                    done,
                    [reset_value.shape[0]]
                    + [1] * (len(reset_value.shape) - 1),
                )
            return jnp.where(done, reset_value, current_value)

        data = jax.tree.map(
            where_done, state.info["first_state"], state.data
        )
        obs = jax.tree.map(
            where_done, state.info["first_obs"], state.obs
        )
        for name, reset_value in reset_info.items():
            state.info[name] = jax.tree.map(
                where_done,
                reset_value,
                state.info[name],
            )
        state.info["t19_reset_info"] = reset_info
        return state.replace(data=data, obs=obs)


def wrap_for_brax_training(
    env: mjx_env.MjxEnv,
    vision: bool = False,
    num_vision_envs: int = 1,
    episode_length: int = 1000,
    action_repeat: int = 1,
    randomization_fn: Callable | None = None,
) -> playground_wrapper.Wrapper:
    """Use the standard wrappers with a complete T19 handoff reset."""
    del num_vision_envs
    if vision:
        raise ValueError("T19 support train-through is proprioceptive only")
    if randomization_fn is None:
        env = brax_training.VmapWrapper(env)
    else:
        env = playground_wrapper.BraxDomainRandomizationVmapWrapper(
            env, randomization_fn
        )
    env = brax_training.EpisodeWrapper(
        env, episode_length, action_repeat
    )
    return FullHandoffAutoResetWrapper(env)
