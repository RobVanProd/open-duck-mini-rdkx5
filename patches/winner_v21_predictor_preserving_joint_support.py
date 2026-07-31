"""Predictor-preserving joint recurrent support objective for Winner-v21.

This module adds no deployable parameters and does not alter the ONNX ABI.  It
extends Winner-v20's trainable view to include the existing response-prediction
head, then combines the unchanged PPO loss with the existing normalized
next-response loss on stored-successor transitions.
"""

from __future__ import annotations

from typing import Any, Mapping

import jax
import jax.numpy as jnp
import numpy as np

import winner_v12_calibrator_training as training
import winner_v20_joint_recurrent_support as v20


PREDICTOR_KEYS = v20.FROZEN_AUXILIARY_KEYS
JOINT_TRAINABLE_KEYS = v20.JOINT_TRAINABLE_KEYS + PREDICTOR_KEYS
POLICY_HEAD_KEYS = ("action_weight", "action_bias")
PPO_ONLY_KEYS = (
    "action_weight",
    "action_bias",
    "training_only_log_std",
    "training_only_value_weight",
    "training_only_value_bias",
)
RECURRENT_KEYS = v20.RECURRENT_CORE_KEYS


def _select(
    parameters: Mapping[str, Any], keys: tuple[str, ...]
) -> dict[str, jax.Array]:
    if set(keys) - set(parameters):
        raise KeyError(f"missing parameter keys: {sorted(set(keys) - set(parameters))}")
    return {key: jnp.asarray(parameters[key], dtype=jnp.float32) for key in keys}


def joint_trainable_parameters(parameters: Mapping[str, Any]) -> dict[str, jax.Array]:
    return _select(parameters, JOINT_TRAINABLE_KEYS)


def merge_joint_trainable(
    parameters: Mapping[str, Any], trainable: Mapping[str, Any]
) -> dict[str, jax.Array]:
    if set(trainable) != set(JOINT_TRAINABLE_KEYS):
        raise ValueError("Winner-v21 joint-trainable parameter schema changed")
    merged = {
        key: jnp.asarray(value, dtype=jnp.float32)
        for key, value in parameters.items()
    }
    merged.update(
        {key: jnp.asarray(value, dtype=jnp.float32) for key, value in trainable.items()}
    )
    return merged


def stored_successor_mask(batch: Mapping[str, jax.Array]) -> jax.Array:
    """Mask valid transitions whose successor observation is stored in-batch."""

    valid = jnp.asarray(batch["valid_transition_mask"], dtype=jnp.float32)
    sampled = jnp.asarray(batch["valid_mask"], dtype=jnp.float32)
    if valid.ndim != 2 or sampled.shape != valid.shape or valid.shape[1] < 2:
        raise ValueError("Winner-v21 transition masks must have shape [E,T>=2]")
    return valid[:, :-1] * sampled[:, 1:]


def predictor_loss(
    parameters: Mapping[str, jax.Array],
    batch: Mapping[str, jax.Array],
    target_std: jax.Array,
) -> tuple[jax.Array, dict[str, jax.Array]]:
    observations = jnp.asarray(batch["observations"], dtype=jnp.float32)
    previous_actions = jnp.asarray(batch["previous_actions"], dtype=jnp.float32)
    realized_actions = jnp.asarray(batch["realized_actions"], dtype=jnp.float32)
    if (
        observations.ndim != 3
        or observations.shape[-1] != training.OBS_SIZE
        or previous_actions.shape != (*observations.shape[:2], training.ACTION_SIZE)
        or realized_actions.shape != previous_actions.shape
    ):
        raise ValueError("Winner-v21 predictor batch shape changed")
    target_std = jnp.asarray(target_std, dtype=jnp.float32)
    if target_std.shape != (len(training.AUXILIARY_INDICES),):
        raise ValueError("Winner-v21 target standard-deviation shape changed")
    hidden = v20.recurrent_hidden_trajectory(
        parameters, observations, previous_actions
    )
    predictions = (
        hidden @ parameters["auxiliary_hidden_weight"]
        + realized_actions @ parameters["auxiliary_action_weight"]
        + parameters["auxiliary_bias"]
    )
    targets = observations[:, 1:, training.AUXILIARY_INDICES]
    predictions = predictions[:, :-1]
    mask = stored_successor_mask(batch)[..., None]
    normalized_error = (predictions - targets) / target_std
    denominator = jnp.maximum(
        jnp.sum(mask) * jnp.float32(len(training.AUXILIARY_INDICES)),
        jnp.float32(1.0),
    )
    loss = jnp.sum(jnp.square(normalized_error) * mask) / denominator
    return loss, {
        "predictor_loss": loss,
        "stored_successor_transition_count": jnp.sum(mask),
    }


def _tree_rms(gradients: Mapping[str, jax.Array], keys: tuple[str, ...]) -> float:
    total = 0.0
    count = 0
    for key in keys:
        value = np.asarray(gradients[key], dtype=np.float64)
        total += float(np.sum(np.square(value), dtype=np.float64))
        count += int(value.size)
    if count <= 0:
        raise ValueError("Winner-v21 gradient reference is empty")
    return float(np.sqrt(total / count))


def gradient_balance_scale(
    ppo_gradients: Mapping[str, jax.Array],
    predictor_gradients: Mapping[str, jax.Array],
) -> tuple[np.float32, dict[str, float]]:
    """Balance existing action-head and predictor-head gradient RMS once."""

    if set(ppo_gradients) != set(JOINT_TRAINABLE_KEYS) or set(
        predictor_gradients
    ) != set(JOINT_TRAINABLE_KEYS):
        raise ValueError("Winner-v21 gradient tree schema changed")
    ppo_rms = _tree_rms(ppo_gradients, POLICY_HEAD_KEYS)
    predictor_rms = _tree_rms(predictor_gradients, PREDICTOR_KEYS)
    if not np.isfinite(ppo_rms) or not np.isfinite(predictor_rms):
        raise FloatingPointError("Winner-v21 gradient reference is nonfinite")
    if ppo_rms <= 0.0 or predictor_rms <= 0.0:
        raise ValueError("Winner-v21 gradient reference did not open")
    scale = np.float32(ppo_rms / predictor_rms)
    if not np.isfinite(scale) or scale <= 0.0:
        raise ValueError("Winner-v21 balance scale is invalid")
    return scale, {
        "ppo_action_head_gradient_rms": ppo_rms,
        "predictor_head_gradient_rms": predictor_rms,
        "predictor_scale": float(scale),
    }


def combined_loss(
    parameters: Mapping[str, jax.Array],
    batch: Mapping[str, jax.Array],
    target_std: jax.Array,
    predictor_scale: jax.Array,
    *,
    clip_epsilon: float,
    value_coefficient: float,
    entropy_coefficient: float,
) -> tuple[jax.Array, dict[str, jax.Array]]:
    ppo_loss, ppo_metrics = v20.joint_recurrent_ppo_loss(
        parameters,
        batch,
        clip_epsilon=clip_epsilon,
        value_coefficient=value_coefficient,
        entropy_coefficient=entropy_coefficient,
    )
    response_loss, response_metrics = predictor_loss(parameters, batch, target_std)
    scale = jnp.asarray(predictor_scale, dtype=jnp.float32)
    total = ppo_loss + scale * response_loss
    return total, {
        **ppo_metrics,
        **response_metrics,
        "ppo_loss": ppo_loss,
        "predictor_scale": scale,
        "scaled_predictor_loss": scale * response_loss,
    }
