"""Mask T95 optimizer updates to calibration FiLM plus the critic.

The protected source actor, recurrent dynamics, and action head remain exact.
Only the new context/state bilinear gain may change the deployed actor.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import jax
import jax.numpy as jnp
import optax


TRAINABLE_ACTOR_NAME = "context_film_scale"
FROZEN_ACTOR_NAMES = (
    "residual_trunk",
    "residual_location",
    "scale_logits",
    "adapter_obs_projection",
    "adapter_hidden_projection",
    "adapter_hidden_bias",
    "adapter_location",
)


def update_is_trainable(path: tuple[Any, ...]) -> bool:
    """Allow the FiLM kernel, critics, and non-actor training state only."""
    text = jax.tree_util.keystr(path)
    if TRAINABLE_ACTOR_NAME in text:
        return True
    if any(name in text for name in FROZEN_ACTOR_NAMES):
        return False
    return True


def mask_actor_updates(updates: Any) -> Any:
    """Zero every protected actor update exactly."""
    return jax.tree_util.tree_map_with_path(
        lambda path, value: (
            value if update_is_trainable(path) else jnp.zeros_like(value)
        ),
        updates,
    )


@contextmanager
def film_only_updates() -> Iterator[None]:
    """Install the exact T95 update mask for one training call."""
    original = optax.apply_updates

    def apply_updates(params: Any, updates: Any) -> Any:
        return original(params, mask_actor_updates(updates))

    optax.apply_updates = apply_updates
    try:
        yield
    finally:
        optax.apply_updates = original
