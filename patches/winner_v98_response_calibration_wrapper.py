"""Automatic calibration-prefix wrapper for response-conditioned locomotion."""

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

from playground.common.winner_v98_response_conditioned_ppo_networks import (
    ACTION_SIZE,
    CONTEXT_OBSERVATION_KEY,
    HIDDEN_OBSERVATION_KEY,
    HIDDEN_SIZE,
    PREVIOUS_ACTION_OBSERVATION_KEY,
    graph_action_boundary,
)


CALIBRATION_TICKS = 250
HOME_RETURN_TICKS = 250
COMMAND_SLICE = slice(6, 13)
PHASE_SLICE = slice(99, 101)
REFERENCE_SLICE = slice(101, 115)
UNIVERSAL_TARGET = np.asarray(
    [0.0, 0.0, -0.5, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.25, 0.25],
    dtype=np.float32,
)
CALIBRATOR_ONNX_SHA256 = (
    "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
)


def load_calibrator_onnx(path: str | Path) -> dict[str, np.ndarray]:
    import onnx

    source = Path(path)
    if hashlib.sha256(source.read_bytes()).hexdigest() != CALIBRATOR_ONNX_SHA256:
        raise ValueError("response calibrator SHA-256 changed")
    model = onnx.load(source)
    if [item.name for item in model.graph.input] != ["obs", "previous_action", "h_in"]:
        raise ValueError("response calibrator input ABI changed")
    if [item.name for item in model.graph.output] != [
        "calibration_actions",
        "previous_action_out",
        "h_out",
    ]:
        raise ValueError("response calibrator output ABI changed")
    values = {
        item.name: np.asarray(onnx.numpy_helper.to_array(item), dtype=np.float32)
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
            raise ValueError(f"response calibrator initializer changed: {name}")
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
    value = observation.at[COMMAND_SLICE].set(jnp.zeros(7, dtype=jnp.float32))
    value = value.at[PHASE_SLICE].set(jnp.asarray([1.0, 0.0], dtype=jnp.float32))
    return value.at[REFERENCE_SLICE].set(jnp.zeros(ACTION_SIZE, dtype=jnp.float32))


class ResponseCalibrationWrapper(wrapper.Wrapper):
    """Run calibration and home-return inside reset, outside PPO transitions."""

    def __init__(
        self,
        env: Any,
        calibrator_parameters: Mapping[str, np.ndarray],
        *,
        calibration_ticks: int = CALIBRATION_TICKS,
        home_return_ticks: int = HOME_RETURN_TICKS,
    ):
        super().__init__(env)
        if calibration_ticks != CALIBRATION_TICKS:
            raise ValueError("response calibration must be exactly 250 ticks")
        if home_return_ticks != HOME_RETURN_TICKS:
            raise ValueError("response home return must be exactly 250 ticks")
        self._calibrator = {
            name: jnp.asarray(value, dtype=jnp.float32)
            for name, value in calibrator_parameters.items()
        }
        self._calibration_ticks = calibration_ticks
        self._home_return_ticks = home_return_ticks

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
            0, dtype=jnp.asarray(info["imitation_i"]).dtype
        )
        info["imitation_phase"] = jnp.asarray([1.0, 0.0], dtype=jnp.float32)
        if info["current_reference_motion"].size:
            info["current_reference_motion"] = self.env.PRM.get_reference_motion(
                0.0, 0.0, 0.0, 0
            )
        return info

    def _locomotion_observation(
        self, state: mjx_env.State, info: dict[str, Any]
    ) -> Mapping[str, jax.Array]:
        contact = jnp.asarray(
            [
                collision.geoms_colliding(
                    state.data, geom_id, self.env._floor_geom_id
                )
                for geom_id in self.env._feet_geom_id
            ]
        )
        return self.env._get_obs(state.data, info, contact)

    def reset(self, rng: jax.Array) -> mjx_env.State:
        initial = self.env.reset(rng)
        locomotion_command = initial.info["command"]
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
                self._calibrator, observation, previous_action, hidden_in
            )
            next_state = self.env.step(state, action)
            next_valid = support_valid & (next_state.done == 0)
            return (next_state, action, hidden_out, next_valid), None

        (state, previous, calibration_context, valid), _ = jax.lax.scan(
            calibration_body,
            (initial, previous, hidden, valid),
            xs=None,
            length=self._calibration_ticks,
        )

        def home_body(carry, _):
            state, support_valid = carry
            info = self._calibration_info(state)
            state = state.replace(info=info)
            next_state = self.env.step(
                state, jnp.zeros(ACTION_SIZE, dtype=jnp.float32)
            )
            return (next_state, support_valid & (next_state.done == 0)), None

        (state, valid), _ = jax.lax.scan(
            home_body,
            (state, valid),
            xs=None,
            length=self._home_return_ticks,
        )
        info = dict(state.info)
        info["step"] = jnp.zeros_like(info["step"])
        info["command"] = locomotion_command
        info["imitation_i"] = jnp.asarray(
            0, dtype=jnp.asarray(info["imitation_i"]).dtype
        )
        info["imitation_phase"] = jnp.asarray([1.0, 0.0], dtype=jnp.float32)
        if info["current_reference_motion"].size:
            info["current_reference_motion"] = self.env.PRM.get_reference_motion(
                locomotion_command[0], locomotion_command[1], locomotion_command[2], 0
            )
        info["policy_hidden"] = jnp.zeros(HIDDEN_SIZE, dtype=jnp.float32)
        info["response_calibration_context"] = calibration_context
        info["response_calibration_valid"] = valid
        info["response_calibration_ticks"] = jnp.asarray(
            self._calibration_ticks, dtype=jnp.int32
        )
        state = state.replace(info=info)
        observation = dict(self._locomotion_observation(state, info))
        observation[HIDDEN_OBSERVATION_KEY] = jnp.zeros(
            HIDDEN_SIZE, dtype=jnp.float32
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

    def step(self, state: mjx_env.State, action: jax.Array) -> mjx_env.State:
        bounded = graph_action_boundary(
            action,
            state.obs["state"],
            state.obs[PREVIOUS_ACTION_OBSERVATION_KEY],
        )
        next_state = self.env.step(state, bounded)
        info = dict(next_state.info)
        context = state.obs[CONTEXT_OBSERVATION_KEY]
        valid = info["response_calibration_valid"]
        observation = dict(next_state.obs)
        observation[HIDDEN_OBSERVATION_KEY] = state.obs[HIDDEN_OBSERVATION_KEY]
        observation[CONTEXT_OBSERVATION_KEY] = context
        observation[PREVIOUS_ACTION_OBSERVATION_KEY] = info["last_act"]
        done = jnp.maximum(next_state.done, 1 - valid.astype(next_state.done.dtype))
        reward = jnp.where(valid, next_state.reward, jnp.zeros_like(next_state.reward))
        return next_state.replace(
            obs=observation, info=info, done=done, reward=reward
        )


def wrap_response_calibration(
    env: Any,
    calibrator_path: str | Path,
    *,
    calibration_ticks: int = CALIBRATION_TICKS,
    home_return_ticks: int = HOME_RETURN_TICKS,
) -> ResponseCalibrationWrapper:
    return ResponseCalibrationWrapper(
        env,
        load_calibrator_onnx(calibrator_path),
        calibration_ticks=calibration_ticks,
        home_return_ticks=home_return_ticks,
    )
