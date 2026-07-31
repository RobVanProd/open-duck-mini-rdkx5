"""T153 exact-positive-COM randomizer and isolated expert update mask.

This training-only mechanism is the sign-symmetric counterpart of T128.  It
preserves the frozen mature actor, policy ABI, reward, action transition, and
always-on linear expert topology.  Every environment receives the exact
+0.05 m torso-COM endpoint, and only the existing linear expert slot plus the
critic may update.  The slot is exported later as a distinct positive expert;
the frozen nominal and negative deployment graphs are never modified.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

import jax
import jax.numpy as jnp
from mujoco import mjx
import optax


TORSO_BODY_ID = 2
POSITIVE_COM_OFFSET_M = jnp.asarray([0.05, 0.0, 0.0], dtype=jnp.float32)
TRAINABLE_ACTOR_NAME = "negative_adapter_location"
FROZEN_ACTOR_NAMES = (
    "adapter_obs_projection",
    "adapter_hidden_projection",
    "adapter_hidden_bias",
    "adapter_location",
    "residual_trunk",
    "residual_location",
    "scale_logits",
)
MODEL_FIELDS = (
    "geom_friction",
    "dof_frictionloss",
    "dof_armature",
    "body_mass",
    "body_ipos",
    "body_inertia",
    "body_iquat",
)


def positive_only_offsets(population: int) -> jax.Array:
    """Return the exact positive torso-COM offset for every environment."""
    if population <= 0:
        raise ValueError("T153 population must be positive")
    return jnp.broadcast_to(POSITIVE_COM_OFFSET_M, (population, 3))


def make_positive_only_randomizer(
    base_randomizer: Callable[[mjx.Model, jax.Array], tuple[mjx.Model, Any]],
    *,
    torso_body_id: int,
) -> Callable[[mjx.Model, jax.Array], tuple[mjx.Model, Any]]:
    """Replace mixed body configurations with one exact positive-COM model."""
    torso_body_id = int(torso_body_id)
    if torso_body_id != TORSO_BODY_ID:
        raise ValueError(
            f"T153 torso id must be {TORSO_BODY_ID}, got {torso_body_id}"
        )

    def randomizer(
        model: mjx.Model,
        rng: jax.Array,
    ) -> tuple[mjx.Model, Any]:
        randomized, in_axes = base_randomizer(model, rng)
        population = int(rng.shape[0])
        replacements = {
            name: jnp.broadcast_to(
                getattr(model, name),
                getattr(randomized, name).shape,
            )
            for name in MODEL_FIELDS
        }
        replacements["body_ipos"] = replacements["body_ipos"].at[
            :, torso_body_id, :
        ].add(positive_only_offsets(population))
        return randomized.tree_replace(replacements), in_axes

    return randomizer


def update_is_trainable(path: tuple[Any, ...]) -> bool:
    """Allow only the isolated expert slot and critic to update."""
    text = jax.tree_util.keystr(path)
    if TRAINABLE_ACTOR_NAME in text:
        return True
    if any(name in text for name in FROZEN_ACTOR_NAMES):
        return False
    return True


def mask_protected_actor_updates(updates: Any) -> Any:
    """Zero every mature-actor update while leaving critic updates intact."""
    return jax.tree_util.tree_map_with_path(
        lambda path, value: (
            value if update_is_trainable(path) else jnp.zeros_like(value)
        ),
        updates,
    )


@contextmanager
def isolated_positive_expert_updates() -> Iterator[None]:
    """Install T153's exact parameter-update mask."""
    original = optax.apply_updates

    def apply_updates(params: Any, updates: Any) -> Any:
        return original(params, mask_protected_actor_updates(updates))

    if original is apply_updates:
        raise RuntimeError("T153 actor-update mask is re-entrant")
    optax.apply_updates = apply_updates
    try:
        yield
    finally:
        optax.apply_updates = original


# The frozen T112 runner imports this historical symbol.
hidden_expert_updates = isolated_positive_expert_updates
