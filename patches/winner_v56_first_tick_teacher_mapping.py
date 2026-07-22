"""Training-only first-tick teacher mapping selected by Winner-v55b."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

import winner_v12_calibrator_training as training
import winner_v49_full_action_static_target_teacher as v49


RESET_TEACHER_SCALE = np.float32(v49.FULL_ACTION_TEACHER_SCALE)
PITCH_INDICES = jnp.asarray(v49.PITCH_ACTION_INDICES, dtype=jnp.int32)
NONPITCH_INDICES = jnp.asarray(v49.NONPITCH_ACTION_INDICES, dtype=jnp.int32)


def first_tick_actions(
    parameters: Mapping[str, jax.Array], observations: Any
) -> jax.Array:
    """Return graph-authoritative actions from zero previous action and h_in."""

    obs = jnp.asarray(observations, dtype=jnp.float32)
    if obs.ndim != 2 or obs.shape[1] != training.OBS_SIZE:
        raise ValueError("Winner-v56 reset observation shape changed")
    previous = jnp.zeros((obs.shape[0], training.ACTION_SIZE), dtype=jnp.float32)
    hidden_in = jnp.zeros((obs.shape[0], training.HIDDEN_SIZE), dtype=jnp.float32)
    realized = jnp.zeros_like(previous)

    def one(obs_row: jax.Array, previous_row: jax.Array, hidden_row: jax.Array):
        hidden, _ = training.response_step(
            parameters, obs_row, previous_row, hidden_row, realized[0]
        )
        mean, _ = training.stage2_mean_value(parameters, hidden)
        return training.bounded_action(mean, previous_row)

    return jax.vmap(one)(obs, previous, hidden_in)


def first_tick_teacher_loss(
    parameters: Mapping[str, jax.Array], batch: Mapping[str, Any]
) -> tuple[jax.Array, dict[str, jax.Array]]:
    observations = jnp.asarray(batch["observations"], dtype=jnp.float32)
    targets = jnp.asarray(batch["targets"], dtype=jnp.float32)
    variant = jnp.asarray(batch["variant"], dtype=jnp.int32)
    actions = first_tick_actions(parameters, observations)
    if targets.shape != actions.shape or variant.shape != (actions.shape[0],):
        raise ValueError("Winner-v56 reset-teacher batch shape changed")
    error = actions - targets
    loss = jnp.mean(jnp.square(error))
    raw_mask = variant == 0
    quantized_mask = variant == 1

    def subset_mse(mask: jax.Array) -> jax.Array:
        selected = jnp.where(mask[:, None], jnp.square(error), jnp.float32(0.0))
        denominator = jnp.maximum(
            jnp.sum(mask) * jnp.float32(training.ACTION_SIZE), jnp.float32(1.0)
        )
        return jnp.sum(selected) / denominator

    return loss, {
        "first_tick_teacher_loss": loss,
        "raw_reset_mse": subset_mse(raw_mask),
        "quantized_reset_mse": subset_mse(quantized_mask),
        "pitch_rms": jnp.sqrt(jnp.mean(jnp.square(error[:, PITCH_INDICES]))),
        "nonpitch_rms": jnp.sqrt(jnp.mean(jnp.square(error[:, NONPITCH_INDICES]))),
        "maximum_abs_error": jnp.max(jnp.abs(error)),
        "sample_count": jnp.asarray(actions.shape[0], dtype=jnp.int32),
        "selected_elements": jnp.asarray(actions.size, dtype=jnp.int32),
    }


def combine_objective(
    baseline_loss: jax.Array, reset_loss: jax.Array, *, enabled: bool
) -> jax.Array:
    if not enabled:
        return baseline_loss
    return baseline_loss + jnp.asarray(RESET_TEACHER_SCALE) * reset_loss
