"""Frozen explicit-gradient mechanics for the Winner-v22 two-update proof."""

from __future__ import annotations

from typing import Any, Mapping

import jax
import jax.numpy as jnp
import numpy as np

import winner_v21_predictor_preserving_joint_support as v21
import winner_v21_predictor_preserving_joint_support_v2 as v21v2


FROZEN_PREDICTOR_SCALE = np.float32(380.9135437011719)
save_snapshot = v21v2.save_snapshot
load_snapshot = v21v2.load_snapshot


def compose_gradients(
    ppo_gradients: Mapping[str, Any], predictor_gradients: Mapping[str, Any]
) -> dict[str, jax.Array]:
    expected = set(v21.JOINT_TRAINABLE_KEYS)
    if set(ppo_gradients) != expected or set(predictor_gradients) != expected:
        raise ValueError("Winner-v22 gradient tree schema changed")
    scale = jnp.asarray(FROZEN_PREDICTOR_SCALE, dtype=jnp.float32)
    return {
        key: jnp.asarray(ppo_gradients[key], dtype=jnp.float32)
        + scale * jnp.asarray(predictor_gradients[key], dtype=jnp.float32)
        for key in v21.JOINT_TRAINABLE_KEYS
    }
