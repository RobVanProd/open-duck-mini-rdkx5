"""Command-aware V96 universal-response prefix for T95."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
from pathlib import Path
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np
from mujoco_playground._src import collision
from mujoco_playground._src import mjx_env
from mujoco_playground._src import wrapper

from playground.common.t10_response_conditioned_v121_networks import (
    ACTION_SIZE,
    CONTEXT_OBSERVATION_KEY,
    HIDDEN_OBSERVATION_KEY,
    HIDDEN_SIZE,
    PREVIOUS_ACTION_OBSERVATION_KEY,
    V121_DEADBAND_ABS_X,
)


CALIBRATION_TICKS = 250
COMMAND_SLICE = slice(6, 13)
PHASE_SLICE = slice(99, 101)
REFERENCE_SLICE = slice(101, 115)
UNIVERSAL_TARGET = np.asarray(
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
CALIBRATOR_ONNX_SHA256 = (
    "0f3aebfd9946a6271fdb14adec3d68d556648f270984639d372c973a7d7dc576"
)


def load_calibrator_onnx(path: str | Path) -> dict[str, np.ndarray]:
    import onnx

    source = Path(path)
    if hashlib.sha256(source.read_bytes()).hexdigest() != (
        CALIBRATOR_ONNX_SHA256
    ):
        raise ValueError("T95 V96 response calibrator SHA-256 changed")
    model = onnx.load(source)
    if [item.name for item in model.graph.input] != [
        "obs",
        "previous_action",
        "h_in",
    ]:
        raise ValueError("T95 response calibrator input ABI changed")
    if [item.name for item in model.graph.output] != [
        "calibration_actions",
        "previous_action_out",
        "h_out",
    ]:
        raise ValueError("T95 response calibrator output ABI changed")
    values = {
        item.name: np.asarray(
            onnx.numpy_helper.to_array(item),
            dtype=np.float32,
        )
        for item in model.graph.initializer
    }
    required = {
        "cal_obs_weight": (115, 64),
        "cal_previous_action_weight": (14, 64),
        "cal_hidden_weight": (64, 64),
        "cal_hidden_bias": (64,),
        "cal_max_action_delta": (1, 14),
    }
    for name, shape in required.items():
        if name not in values or values[name].shape != shape:
            raise ValueError(f"T10 calibrator initializer changed: {name}")
    return {name: values[name] for name in required}


def calibrator_step(
    parameters: Mapping[str, jax.Array],
    observation: jax.Array,
    previous_action: jax.Array,
    hidden_in: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    hidden = jnp.tanh(
        observation @ parameters["cal_obs_weight"]
        + previous_action @ parameters["cal_previous_action_weight"]
        + hidden_in @ parameters["cal_hidden_weight"]
        + parameters["cal_hidden_bias"]
    )
    target = jnp.asarray(UNIVERSAL_TARGET)
    maximum_delta = parameters["cal_max_action_delta"][0]
    lower = jnp.maximum(previous_action - maximum_delta, -1.0)
    upper = jnp.minimum(previous_action + maximum_delta, 1.0)
    action = jnp.maximum(jnp.minimum(target, upper), lower)
    return action, hidden


def calibration_observation(observation: jax.Array) -> jax.Array:
    value = observation.at[COMMAND_SLICE].set(
        jnp.zeros(7, dtype=jnp.float32)
    )
    value = value.at[PHASE_SLICE].set(
        jnp.asarray([1.0, 0.0], dtype=jnp.float32)
    )
    return value.at[REFERENCE_SLICE].set(
        jnp.zeros(ACTION_SIZE, dtype=jnp.float32)
    )


class CommandAwareResponseWrapper(wrapper.Wrapper):
    """Run 250 response ticks only when the deployed graph can locomote."""

    def __init__(
        self,
        env: Any,
        calibrator_parameters: Mapping[str, np.ndarray],
        *,
        calibration_ticks: int = CALIBRATION_TICKS,
        home_return_ticks: int = 0,
        zero_command_bypass: bool = True,
    ):
        super().__init__(env)
        if calibration_ticks != CALIBRATION_TICKS:
            raise ValueError("T10 calibration must remain exactly 250 ticks")
        if home_return_ticks != 0:
            raise ValueError("T10 state-coherent handoff requires zero return")
        if not zero_command_bypass:
            raise ValueError("T10 command-aware x=0 bypass must remain enabled")
        self._calibrator = {
            name: jnp.asarray(value, dtype=jnp.float32)
            for name, value in calibrator_parameters.items()
        }
        self._calibration_ticks = calibration_ticks

    @property
    def observation_size(self) -> Mapping[str, tuple[int, ...]]:
        sizes = dict(self.env.observation_size)
        sizes[HIDDEN_OBSERVATION_KEY] = (HIDDEN_SIZE,)
        sizes[CONTEXT_OBSERVATION_KEY] = (HIDDEN_SIZE,)
        sizes[PREVIOUS_ACTION_OBSERVATION_KEY] = (ACTION_SIZE,)
        return sizes

    def _calibration_info(self, state: mjx_env.State) -> dict[str, Any]:
        info = dict(state.info)
        info["command"] = jnp.zeros(7, dtype=jnp.float32)
        info["imitation_i"] = jnp.asarray(
            0,
            dtype=jnp.asarray(info["imitation_i"]).dtype,
        )
        info["imitation_phase"] = jnp.asarray(
            [1.0, 0.0],
            dtype=jnp.float32,
        )
        if info["current_reference_motion"].size:
            info[
                "current_reference_motion"
            ] = self.env.PRM.get_reference_motion(0.0, 0.0, 0.0, 0)
        return info

    def _locomotion_observation(
        self,
        state: mjx_env.State,
        info: dict[str, Any],
    ) -> Mapping[str, jax.Array]:
        contact = jnp.asarray(
            [
                collision.geoms_colliding(
                    state.data,
                    geom_id,
                    self.env._floor_geom_id,
                )
                for geom_id in self.env._feet_geom_id
            ]
        )
        return self.env._get_obs(state.data, info, contact)

    def reset(self, rng: jax.Array) -> mjx_env.State:
        initial = self.env.reset(rng)
        locomotion_command = initial.info["command"]
        bypass = (
            jnp.abs(locomotion_command[0])
            <= jnp.float32(V121_DEADBAND_ABS_X)
        )
        initial = initial.replace(info=self._calibration_info(initial))
        previous = jnp.zeros(ACTION_SIZE, dtype=jnp.float32)
        hidden = jnp.zeros(HIDDEN_SIZE, dtype=jnp.float32)
        valid = jnp.asarray(True)

        def calibration_body(carry, _):
            state, previous_action, hidden_in, support_valid = carry
            info = self._calibration_info(state)
            state = state.replace(info=info)
            observation = calibration_observation(state.obs["state"])
            action, hidden_out = calibrator_step(
                self._calibrator,
                observation,
                previous_action,
                hidden_in,
            )

            def apply_prefix(_):
                next_state = self.env.step(state, action)
                return (
                    next_state,
                    action,
                    hidden_out,
                    support_valid & (next_state.done == 0),
                )

            def preserve_home(_):
                return state, previous_action, hidden_in, support_valid

            return jax.lax.cond(
                bypass,
                preserve_home,
                apply_prefix,
                operand=None,
            ), None

        (state, _, calibration_context, valid), _ = jax.lax.scan(
            calibration_body,
            (initial, previous, hidden, valid),
            xs=None,
            length=self._calibration_ticks,
        )
        calibration_context = jnp.where(
            bypass,
            jnp.zeros(HIDDEN_SIZE, dtype=jnp.float32),
            calibration_context,
        )
        info = dict(state.info)
        info["step"] = jnp.zeros_like(info["step"])
        info["command"] = locomotion_command
        info["imitation_i"] = jnp.asarray(
            0,
            dtype=jnp.asarray(info["imitation_i"]).dtype,
        )
        info["imitation_phase"] = jnp.asarray(
            [1.0, 0.0],
            dtype=jnp.float32,
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
        info["policy_hidden"] = jnp.zeros(
            HIDDEN_SIZE,
            dtype=jnp.float32,
        )
        info["response_calibration_context"] = calibration_context
        info["response_calibration_valid"] = valid
        info["response_calibration_bypassed"] = bypass
        info["response_calibration_ticks"] = jnp.where(
            bypass,
            jnp.asarray(0, dtype=jnp.int32),
            jnp.asarray(self._calibration_ticks, dtype=jnp.int32),
        )
        state = state.replace(info=info)
        observation = dict(self._locomotion_observation(state, info))
        observation[HIDDEN_OBSERVATION_KEY] = jnp.zeros(
            HIDDEN_SIZE,
            dtype=jnp.float32,
        )
        observation[CONTEXT_OBSERVATION_KEY] = calibration_context
        observation[PREVIOUS_ACTION_OBSERVATION_KEY] = info["last_act"]
        metrics = jax.tree_util.tree_map(jnp.zeros_like, state.metrics)
        return state.replace(
            obs=observation,
            reward=jnp.zeros_like(state.reward),
            done=jnp.zeros_like(state.done),
            metrics=metrics,
        )

    def step(
        self,
        state: mjx_env.State,
        action: jax.Array,
    ) -> mjx_env.State:
        next_state = self.env.step(state, action)
        info = dict(next_state.info)
        context = state.obs[CONTEXT_OBSERVATION_KEY]
        valid = info["response_calibration_valid"]
        observation = dict(next_state.obs)
        observation[HIDDEN_OBSERVATION_KEY] = state.obs[
            HIDDEN_OBSERVATION_KEY
        ]
        observation[CONTEXT_OBSERVATION_KEY] = context
        observation[PREVIOUS_ACTION_OBSERVATION_KEY] = info["last_act"]
        done = jnp.maximum(
            next_state.done,
            1 - valid.astype(next_state.done.dtype),
        )
        reward = jnp.where(
            valid,
            next_state.reward,
            jnp.zeros_like(next_state.reward),
        )
        return next_state.replace(
            obs=observation,
            info=info,
            done=done,
            reward=reward,
        )


def wrap_command_aware_response(
    env: Any,
    calibrator_path: str | Path,
    *,
    calibration_ticks: int = CALIBRATION_TICKS,
    home_return_ticks: int = 0,
    zero_command_bypass: bool = True,
) -> CommandAwareResponseWrapper:
    return CommandAwareResponseWrapper(
        env,
        load_calibrator_onnx(calibrator_path),
        calibration_ticks=calibration_ticks,
        home_return_ticks=home_return_ticks,
        zero_command_bypass=zero_command_bypass,
    )
