"""T77 joint recurrent-core plus adapter-output-head update mask.

The eight-stratum endpoint bank remains the frozen T66 randomizer.  T77 changes
only which actor leaves may receive optimizer updates: the recurrent adapter
core and its output head co-adapt, while the reference-residual base and action
scale remain bit-exact.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import jax
import jax.numpy as jnp
import optax


TRAINABLE_JOINT_ADAPTER_NAMES = (
    "adapter_obs_projection",
    "adapter_hidden_projection",
    "adapter_hidden_bias",
    "adapter_location",
)
FROZEN_BASE_ACTOR_NAMES = (
    "residual_trunk",
    "residual_location",
    "scale_logits",
)


def update_is_trainable(path: tuple[Any, ...]) -> bool:
    """Allow critics and the complete recurrent adapter only."""
    text = jax.tree_util.keystr(path)
    if any(name in text for name in TRAINABLE_JOINT_ADAPTER_NAMES):
        return True
    if any(name in text for name in FROZEN_BASE_ACTOR_NAMES):
        return False
    return True


def mask_base_actor_updates(updates: Any) -> Any:
    """Zero the frozen reference-residual base actor updates exactly."""
    return jax.tree_util.tree_map_with_path(
        lambda path, value: (
            value if update_is_trainable(path) else jnp.zeros_like(value)
        ),
        updates,
    )


@contextmanager
def joint_adapter_updates() -> Iterator[None]:
    """Mask optimizer updates to the complete recurrent adapter plus critic."""
    original = optax.apply_updates

    def apply_updates(params: Any, updates: Any) -> Any:
        return original(params, mask_base_actor_updates(updates))

    if original is apply_updates:
        raise RuntimeError("T77 actor-update mask is re-entrant")
    optax.apply_updates = apply_updates
    try:
        yield
    finally:
        optax.apply_updates = original
