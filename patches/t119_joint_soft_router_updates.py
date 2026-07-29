"""T119 joint soft-router and negative-expert update mask."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import jax
import jax.numpy as jnp
import optax


TRAINABLE_ACTOR_NAMES = (
    "negative_adapter_location",
    "soft_router_coefficient_delta",
    "soft_router_intercept_delta",
)
FROZEN_ACTOR_NAMES = (
    "adapter_obs_projection",
    "adapter_hidden_projection",
    "adapter_hidden_bias",
    "adapter_location",
    "residual_trunk",
    "residual_location",
    "scale_logits",
)


def update_is_trainable(path: tuple[Any, ...]) -> bool:
    """Allow only the soft router, its expert, and the critic."""
    text = jax.tree_util.keystr(path)
    if any(name in text for name in TRAINABLE_ACTOR_NAMES):
        return True
    if any(name in text for name in FROZEN_ACTOR_NAMES):
        return False
    return True


def mask_protected_actor_updates(updates: Any) -> Any:
    """Zero every protected mature-actor update."""
    return jax.tree_util.tree_map_with_path(
        lambda path, value: (
            value if update_is_trainable(path) else jnp.zeros_like(value)
        ),
        updates,
    )


@contextmanager
def hidden_expert_updates() -> Iterator[None]:
    """Install T119's exact parameter-update mask."""
    original = optax.apply_updates

    def apply_updates(params: Any, updates: Any) -> Any:
        return original(params, mask_protected_actor_updates(updates))

    if original is apply_updates:
        raise RuntimeError("T119 actor-update mask is re-entrant")
    optax.apply_updates = apply_updates
    try:
        yield
    finally:
        optax.apply_updates = original
