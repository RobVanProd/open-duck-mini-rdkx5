"""Training-only full-action teacher selected by Winner-v48c."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import jax
import jax.numpy as jnp
import numpy as np

import winner_v43_static_target_teacher as v43


ACTION_INDICES = tuple(range(14))
PITCH_ACTION_INDICES = v43.PITCH_ACTION_INDICES
NONPITCH_ACTION_INDICES = tuple(
    index for index in ACTION_INDICES if index not in PITCH_ACTION_INDICES
)
OLD_PITCH_TEACHER_SCALE = np.float32(58.436370849609375)
FULL_ACTION_TEACHER_SCALE = np.float32(136.35153198242188)


def build_teacher_batch(
    configuration_ids: Sequence[str],
    previous_actions: Any,
    valid_mask: Any,
    table: Mapping[str, np.ndarray],
) -> tuple[jax.Array, jax.Array, jax.Array]:
    """Return the exact V43 targets with every valid action element selected."""

    raw, bounded, _ = v43.build_teacher_batch(
        configuration_ids, previous_actions, valid_mask, table
    )
    previous = jnp.asarray(previous_actions, dtype=jnp.float32)
    valid = np.asarray(valid_mask, dtype=np.float32)
    if valid.shape != previous.shape[:2]:
        raise ValueError("Winner-v49 validity mask shape changed")
    mask = np.broadcast_to(valid[..., None], previous.shape).copy()
    return raw, bounded, jnp.asarray(mask, dtype=jnp.float32)


def full_action_teacher_loss(
    candidate_actions: Any,
    configuration_ids: Sequence[str],
    previous_actions: Any,
    valid_mask: Any,
    table: Mapping[str, np.ndarray],
) -> tuple[jax.Array, dict[str, jax.Array]]:
    candidate = jnp.asarray(candidate_actions, dtype=jnp.float32)
    raw, bounded, mask = build_teacher_batch(
        configuration_ids, previous_actions, valid_mask, table
    )
    if candidate.shape != bounded.shape:
        raise ValueError("Winner-v49 candidate action shape changed")
    denominator = jnp.sum(mask)
    if float(denominator) <= 0.0:
        raise ValueError("Winner-v49 teacher mask is empty")
    error = candidate - bounded
    selected_abs = jnp.where(mask > 0.0, jnp.abs(error), jnp.float32(0.0))
    loss = jnp.sum(jnp.square(error) * mask) / denominator
    nonpitch = jnp.asarray(NONPITCH_ACTION_INDICES, dtype=jnp.int32)
    pitch = jnp.asarray(PITCH_ACTION_INDICES, dtype=jnp.int32)
    return loss, {
        "full_action_teacher_loss": loss,
        "selected_elements": denominator,
        "maximum_selected_action_delta": jnp.max(selected_abs),
        "maximum_pitch_action_delta": jnp.max(jnp.abs(error[..., pitch])),
        "maximum_nonpitch_action_delta": jnp.max(jnp.abs(error[..., nonpitch])),
        "raw_target_max_abs": jnp.max(jnp.abs(raw)),
        "bounded_target_max_abs": jnp.max(jnp.abs(bounded)),
    }


def combine_objective(
    baseline_loss: jax.Array,
    teacher_loss: jax.Array,
    *,
    enabled: bool,
) -> jax.Array:
    return v43.combine_objective(
        baseline_loss,
        teacher_loss,
        jnp.asarray(FULL_ACTION_TEACHER_SCALE, dtype=jnp.float32),
        enabled=enabled,
    )


def per_element_scale_is_preserved() -> bool:
    old = OLD_PITCH_TEACHER_SCALE / np.float32(len(PITCH_ACTION_INDICES))
    new = FULL_ACTION_TEACHER_SCALE / np.float32(len(ACTION_INDICES))
    return bool(np.array_equal(old, new))
