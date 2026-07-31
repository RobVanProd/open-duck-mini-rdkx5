"""Evidence-selected normalized-response training for Winner-v13.

Winner-v12 emitted a raw physical next-response prediction and divided its
error by the target standard deviation. Two constant contact targets therefore
received a 1e-6 scale while the zero-centered head had to learn a raw value of
one. Winner-v13 instead makes the auxiliary head predict the already normalized
target. The deployable recurrent/action graph, its ABI, and all action limits
remain unchanged; the auxiliary head is still training-only.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

import winner_v12_calibrator_training as v12


OBS_SIZE = v12.OBS_SIZE
ACTION_SIZE = v12.ACTION_SIZE
HIDDEN_SIZE = v12.HIDDEN_SIZE
AUXILIARY_INDICES = v12.AUXILIARY_INDICES
ENCODER_AUXILIARY_KEYS = v12.ENCODER_AUXILIARY_KEYS
DEPLOYABLE_ACTION_KEYS = v12.DEPLOYABLE_ACTION_KEYS
TRAINING_ONLY_STAGE2_KEYS = v12.TRAINING_ONLY_STAGE2_KEYS
DEPLOYABLE_CALIBRATOR_KEYS = v12.DEPLOYABLE_CALIBRATOR_KEYS
STAGE1_LEARNING_RATE = v12.STAGE1_LEARNING_RATE
ADAM_BETA1 = v12.ADAM_BETA1
ADAM_BETA2 = v12.ADAM_BETA2
ADAM_EPSILON = v12.ADAM_EPSILON

initialize_training_parameters = v12.initialize_training_parameters
stage1_parameters = v12.stage1_parameters
stage2_parameters = v12.stage2_parameters
merge_stage1 = v12.merge_stage1
merge_stage2 = v12.merge_stage2
deployable_parameters = v12.deployable_parameters
adam_initialize = v12.adam_initialize
adam_step = v12.adam_step
finite_tree = v12.finite_tree
leaf_max_abs_delta = v12.leaf_max_abs_delta


def normalized_target(
    target: jax.Array, target_mean: jax.Array, target_std: jax.Array
) -> jax.Array:
    """Map a raw 50-D response target into the frozen normalized coordinates."""

    return (target - target_mean) / target_std


def response_step(
    parameters: Mapping[str, jax.Array],
    observation: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
    realized_action: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    """Return h_out and a normalized-coordinate next-response prediction."""

    hidden_pre = (
        observation @ parameters["obs_weight"]
        + previous_action @ parameters["previous_action_weight"]
        + h_in @ parameters["hidden_weight"]
        + parameters["hidden_bias"]
    )
    h_out = jnp.tanh(hidden_pre)
    normalized_prediction = (
        h_out @ parameters["auxiliary_hidden_weight"]
        + realized_action @ parameters["auxiliary_action_weight"]
        + parameters["auxiliary_bias"]
    )
    return h_out, normalized_prediction


def stage1_predictions(
    parameters: Mapping[str, jax.Array],
    observations: jax.Array,
    previous_actions: jax.Array,
    realized_actions: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array]:
    """Run the unchanged 250-tick recurrent scan for every environment."""

    def run_one(obs: jax.Array, previous: jax.Array, realized: jax.Array):
        def step(h_in: jax.Array, values: tuple[jax.Array, ...]):
            obs_t, previous_t, realized_t = values
            h_out, prediction = response_step(
                parameters, obs_t, previous_t, h_in, realized_t
            )
            return h_out, (h_out, prediction)

        initial = jnp.zeros((HIDDEN_SIZE,), dtype=jnp.float32)
        final_hidden, (hidden, prediction) = jax.lax.scan(
            step, initial, (obs, previous, realized)
        )
        return final_hidden, hidden, prediction

    return jax.vmap(run_one)(observations, previous_actions, realized_actions)


def stage1_loss(
    parameters: Mapping[str, jax.Array],
    batch: Mapping[str, jax.Array],
    target_mean: jax.Array,
    target_std: jax.Array,
) -> jax.Array:
    """Mean squared error entirely in normalized response coordinates."""

    _, _, prediction = stage1_predictions(
        parameters,
        batch["observations"],
        batch["previous_actions"],
        batch["realized_actions"],
    )
    target = normalized_target(batch["targets"], target_mean, target_std)
    mask = batch["valid_mask"][..., None]
    denominator = jnp.maximum(
        jnp.sum(mask) * jnp.float32(prediction.shape[-1]), jnp.float32(1.0)
    )
    return jnp.sum(jnp.square(prediction - target) * mask) / denominator


def stage1_contact_error_at_constant_target(
    prediction: np.ndarray,
    target: np.ndarray,
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> np.ndarray:
    """Checker-only NumPy form for the two constant contact dimensions."""

    prediction = np.asarray(prediction, dtype=np.float32)
    target = np.asarray(target, dtype=np.float32)
    target_mean = np.asarray(target_mean, dtype=np.float32)
    target_std = np.asarray(target_std, dtype=np.float32)
    if any(value.shape != (2,) for value in (prediction, target, target_mean, target_std)):
        raise ValueError("contact checker requires four two-element vectors")
    if not np.all(target_std > 0.0):
        raise ValueError("contact checker target scale is nonpositive")
    return np.square(prediction - (target - target_mean) / target_std)

