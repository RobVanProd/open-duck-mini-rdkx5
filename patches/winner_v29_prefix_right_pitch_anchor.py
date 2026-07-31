"""Winner-v29 early right-pitch-chain source-anchor mechanics.

This module encodes only the mechanism selected by the frozen Winner-v28
causal screen: on the exact negative-X training configurations, compare the
candidate's deterministic bounded right hip-pitch/knee/ankle actions at ticks
0-7 with Winner-v22 evaluated on the same candidate observation and realized
previous-action history.  It does not replace actions or modify transitions.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import jax
import jax.numpy as jnp
import numpy as np

import winner_v12_calibrator_training as training
import winner_v20_joint_recurrent_support as v20
import winner_v21_predictor_preserving_joint_support as v21


PREFIX_TICKS = 8
RIGHT_PITCH_ACTION_INDICES = (11, 12, 13)
SELECTED_TRAINING_CONFIGURATION_IDS = (
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "DISCOVERY_03",
    "DISCOVERY_09",
    "DISCOVERY_10",
)
ANCHOR_GRADIENT_KEYS = v20.RECURRENT_CORE_KEYS + training.DEPLOYABLE_ACTION_KEYS
NON_ANCHOR_GRADIENT_KEYS = tuple(
    key for key in v21.JOINT_TRAINABLE_KEYS if key not in ANCHOR_GRADIENT_KEYS
)
EXPECTED_SELECTED_EPISODES = 16
EXPECTED_ANCHOR_ELEMENTS = (
    EXPECTED_SELECTED_EPISODES * PREFIX_TICKS * len(RIGHT_PITCH_ACTION_INDICES)
)


def build_anchor_mask(
    population: Sequence[Mapping[str, Any]], valid_mask: Any
) -> np.ndarray:
    """Return the exact [E,T,14] mask selected by the V28 intervention."""

    valid = np.asarray(valid_mask, dtype=np.float32)
    if valid.ndim != 2 or valid.shape[0] != len(population):
        raise ValueError("Winner-v29 valid-mask/population shape changed")
    if valid.shape[1] < PREFIX_TICKS:
        raise ValueError("Winner-v29 rollout is shorter than the frozen prefix")
    identifiers = [str(row.get("id")) for row in population]
    selected = set(SELECTED_TRAINING_CONFIGURATION_IDS)
    if set(identifiers) & selected != selected:
        raise ValueError("Winner-v29 selected training configurations are absent")
    counts = {name: identifiers.count(name) for name in selected}
    if any(count != 2 for count in counts.values()):
        raise ValueError("Winner-v29 selected configurations are not two-plant pairs")

    mask = np.zeros((*valid.shape, training.ACTION_SIZE), dtype=np.float32)
    for environment, identifier in enumerate(identifiers):
        if identifier not in selected:
            continue
        for action_index in RIGHT_PITCH_ACTION_INDICES:
            mask[environment, :PREFIX_TICKS, action_index] = valid[
                environment, :PREFIX_TICKS
            ]
    if int(np.sum(mask, dtype=np.float64)) != EXPECTED_ANCHOR_ELEMENTS:
        raise ValueError("Winner-v29 selected prefix contains a stale/invalid sample")
    return mask


def deterministic_bounded_actions(
    parameters: Mapping[str, Any], observations: Any, previous_actions: Any
) -> tuple[jax.Array, jax.Array]:
    """Return recurrent hidden states and graph-authoritative bounded means."""

    observations_jax = jnp.asarray(observations, dtype=jnp.float32)
    previous_jax = jnp.asarray(previous_actions, dtype=jnp.float32)
    hidden = v20.recurrent_hidden_trajectory(
        parameters, observations_jax, previous_jax
    )
    raw_mean = jnp.tanh(
        hidden @ jnp.asarray(parameters["action_weight"], dtype=jnp.float32)
        + jnp.asarray(parameters["action_bias"], dtype=jnp.float32)
    )
    bounded = training.bounded_action(raw_mean, previous_jax)
    return hidden, bounded


def prefix_anchor_loss(
    candidate_parameters: Mapping[str, Any],
    source_parameters: Mapping[str, Any],
    batch: Mapping[str, Any],
    anchor_mask: Any,
) -> tuple[jax.Array, dict[str, jax.Array]]:
    """Mean-square the selected bounded actions against a stopped source."""

    mask = jnp.asarray(anchor_mask, dtype=jnp.float32)
    observations = jnp.asarray(batch["observations"], dtype=jnp.float32)
    previous_actions = jnp.asarray(batch["previous_actions"], dtype=jnp.float32)
    if mask.shape != (*observations.shape[:2], training.ACTION_SIZE):
        raise ValueError("Winner-v29 anchor mask shape changed")
    candidate_hidden, candidate_actions = deterministic_bounded_actions(
        candidate_parameters, observations, previous_actions
    )
    source_hidden, source_actions = deterministic_bounded_actions(
        source_parameters, observations, previous_actions
    )
    source_actions = jax.lax.stop_gradient(source_actions)
    source_hidden = jax.lax.stop_gradient(source_hidden)
    denominator = jnp.maximum(jnp.sum(mask), jnp.float32(1.0))
    error = candidate_actions - source_actions
    selected_abs = jnp.where(mask > 0, jnp.abs(error), jnp.float32(0.0))
    loss = jnp.sum(jnp.square(error) * mask) / denominator
    return loss, {
        "prefix_anchor_loss": loss,
        "selected_elements": jnp.sum(mask),
        "maximum_selected_action_delta": jnp.max(selected_abs),
        "candidate_hidden_max_abs": jnp.max(jnp.abs(candidate_hidden)),
        "source_hidden_max_abs": jnp.max(jnp.abs(source_hidden)),
    }


def tree_rms(gradients: Mapping[str, Any], keys: Sequence[str]) -> float:
    """Compute one frozen float64 RMS over the named gradient leaves."""

    if set(gradients) != set(v21.JOINT_TRAINABLE_KEYS):
        raise ValueError("Winner-v29 gradient tree schema changed")
    total = 0.0
    count = 0
    for key in keys:
        value = np.asarray(gradients[key], dtype=np.float64)
        total += float(np.sum(np.square(value), dtype=np.float64))
        count += int(value.size)
    if count <= 0:
        raise ValueError("Winner-v29 gradient reference is empty")
    return float(np.sqrt(total / count))


def gradient_balance_scale(
    baseline_gradients: Mapping[str, Any], anchor_gradients: Mapping[str, Any]
) -> tuple[np.float32, dict[str, float]]:
    """Match anchor and existing-objective RMS on the same six policy leaves."""

    baseline_rms = tree_rms(baseline_gradients, ANCHOR_GRADIENT_KEYS)
    anchor_rms = tree_rms(anchor_gradients, ANCHOR_GRADIENT_KEYS)
    if not np.isfinite(baseline_rms) or not np.isfinite(anchor_rms):
        raise FloatingPointError("Winner-v29 gradient reference is nonfinite")
    if baseline_rms <= 0.0 or anchor_rms <= 0.0:
        raise ValueError("Winner-v29 gradient reference did not open")
    scale = np.float32(baseline_rms / anchor_rms)
    if not np.isfinite(scale) or scale <= 0.0:
        raise ValueError("Winner-v29 balance scale is invalid")
    return scale, {
        "baseline_policy_gradient_rms": baseline_rms,
        "raw_anchor_policy_gradient_rms": anchor_rms,
        "anchor_scale": float(scale),
        "scaled_anchor_policy_gradient_rms": tree_rms(
            {
                key: jnp.asarray(anchor_gradients[key], dtype=jnp.float32)
                * jnp.asarray(scale, dtype=jnp.float32)
                for key in v21.JOINT_TRAINABLE_KEYS
            },
            ANCHOR_GRADIENT_KEYS,
        ),
    }


def compose_gradients(
    baseline_gradients: Mapping[str, Any],
    anchor_gradients: Mapping[str, Any],
    anchor_scale: Any,
    *,
    enabled: bool,
) -> dict[str, jax.Array]:
    """Add the frozen anchor gradient, or preserve the baseline bit-exactly."""

    expected = set(v21.JOINT_TRAINABLE_KEYS)
    if set(baseline_gradients) != expected or set(anchor_gradients) != expected:
        raise ValueError("Winner-v29 composed gradient tree schema changed")
    if not enabled:
        return {
            key: jnp.asarray(baseline_gradients[key], dtype=jnp.float32)
            for key in v21.JOINT_TRAINABLE_KEYS
        }
    scale = jnp.asarray(anchor_scale, dtype=jnp.float32)
    return {
        key: jnp.asarray(baseline_gradients[key], dtype=jnp.float32)
        + scale * jnp.asarray(anchor_gradients[key], dtype=jnp.float32)
        for key in v21.JOINT_TRAINABLE_KEYS
    }
