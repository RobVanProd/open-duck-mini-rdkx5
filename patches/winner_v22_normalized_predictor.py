"""Correct normalized-coordinate predictor semantics for the Winner-v22 proof."""

from __future__ import annotations

from typing import Any, Mapping

import jax
import jax.numpy as jnp
import numpy as np

import winner_v12_calibrator_training as training
import winner_v20_joint_recurrent_support as v20
import winner_v21_predictor_preserving_joint_support as v21


JOINT_TRAINABLE_KEYS = v21.JOINT_TRAINABLE_KEYS
RECURRENT_KEYS = v21.RECURRENT_KEYS
PREDICTOR_KEYS = v21.PREDICTOR_KEYS
PPO_ONLY_KEYS = v21.PPO_ONLY_KEYS


def normalized_predictor_loss(
    parameters: Mapping[str, jax.Array],
    batch: Mapping[str, jax.Array],
    target_mean: jax.Array,
    target_std: jax.Array,
) -> tuple[jax.Array, dict[str, jax.Array]]:
    """Compare the inherited normalized head with normalized next responses."""

    observations = jnp.asarray(batch["observations"], dtype=jnp.float32)
    previous_actions = jnp.asarray(batch["previous_actions"], dtype=jnp.float32)
    realized_actions = jnp.asarray(batch["realized_actions"], dtype=jnp.float32)
    if (
        observations.ndim != 3
        or observations.shape[-1] != training.OBS_SIZE
        or previous_actions.shape != (*observations.shape[:2], training.ACTION_SIZE)
        or realized_actions.shape != previous_actions.shape
    ):
        raise ValueError("Winner-v22 predictor batch shape changed")
    target_mean = jnp.asarray(target_mean, dtype=jnp.float32)
    target_std = jnp.asarray(target_std, dtype=jnp.float32)
    expected = (len(training.AUXILIARY_INDICES),)
    if target_mean.shape != expected or target_std.shape != expected:
        raise ValueError("Winner-v22 normalization shape changed")
    hidden = v20.recurrent_hidden_trajectory(
        parameters, observations, previous_actions
    )
    prediction_normalized = (
        hidden @ parameters["auxiliary_hidden_weight"]
        + realized_actions @ parameters["auxiliary_action_weight"]
        + parameters["auxiliary_bias"]
    )[:, :-1]
    next_response_raw = observations[:, 1:, training.AUXILIARY_INDICES]
    target_normalized = (next_response_raw - target_mean) / target_std
    mask = v21.stored_successor_mask(batch)[..., None]
    denominator = jnp.maximum(
        jnp.sum(mask) * jnp.float32(len(training.AUXILIARY_INDICES)),
        jnp.float32(1.0),
    )
    loss = (
        jnp.sum(jnp.square(prediction_normalized - target_normalized) * mask)
        / denominator
    )
    return loss, {
        "predictor_loss": loss,
        "stored_successor_transition_count": jnp.sum(mask),
    }


def normalized_prediction_squared_error(
    prediction_normalized: np.ndarray,
    next_response_raw: np.ndarray,
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> np.ndarray:
    """Independent evaluator form of the corrected learned-predictor error."""

    prediction = np.asarray(prediction_normalized, dtype=np.float64)
    target = np.asarray(next_response_raw, dtype=np.float64)
    mean = np.asarray(target_mean, dtype=np.float64)
    std = np.asarray(target_std, dtype=np.float64)
    if prediction.shape != target.shape or mean.shape != std.shape:
        raise ValueError("Winner-v22 evaluator shape changed")
    if prediction.shape[-1:] != mean.shape or np.any(std <= 0.0):
        raise ValueError("Winner-v22 evaluator normalization changed")
    return np.square(prediction - (target - mean) / std)


def normalized_constant_squared_error(
    next_response_raw: np.ndarray,
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> np.ndarray:
    """Squared error of the frozen mean-response baseline in normalized space."""

    target = np.asarray(next_response_raw, dtype=np.float64)
    mean = np.asarray(target_mean, dtype=np.float64)
    std = np.asarray(target_std, dtype=np.float64)
    if target.shape[-1:] != mean.shape or mean.shape != std.shape or np.any(std <= 0.0):
        raise ValueError("Winner-v22 constant evaluator normalization changed")
    return np.square((target - mean) / std)
