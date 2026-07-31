"""T66 endpoint-bank randomization and recurrent-core-only update mask.

This module changes training only.  It preserves the actor architecture,
reward, observations, deployment graph, and physical limits.
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
ENDPOINT_MAGNITUDE_M = jnp.float32(0.05)
ENDPOINT_OFFSETS_M = jnp.asarray(
    [
        [0.0, 0.0, 0.0],  # group 0 remains broad randomized
        [0.0, 0.0, 0.0],  # isolated nominal
        [-0.05, 0.0, 0.0],
        [0.05, 0.0, 0.0],
        [0.0, -0.05, 0.0],
        [0.0, 0.05, 0.0],
        [0.0, 0.0, -0.05],
        [0.0, 0.0, 0.05],
    ],
    dtype=jnp.float32,
)
ENDPOINT_NAMES = (
    "broad_random",
    "nominal",
    "torso_com_x_neg",
    "torso_com_x_pos",
    "torso_com_y_neg",
    "torso_com_y_pos",
    "torso_com_z_neg",
    "torso_com_z_pos",
)

TRAINABLE_ACTOR_CORE_NAMES = (
    "adapter_obs_projection",
    "adapter_hidden_projection",
    "adapter_hidden_bias",
)
FROZEN_ACTOR_NAMES = (
    "residual_trunk",
    "residual_location",
    "scale_logits",
    "adapter_location",
)


def endpoint_category_ids(population: int) -> jax.Array:
    """Assign eight structural strata without a sampled mixture scalar."""
    if population <= 0 or population % len(ENDPOINT_NAMES) != 0:
        raise ValueError("T66 population must be a positive multiple of eight")
    return jnp.arange(population, dtype=jnp.int32) % len(ENDPOINT_NAMES)


def endpoint_category_counts(population: int) -> dict[str, int]:
    categories = endpoint_category_ids(population)
    return {
        name: int(jnp.sum(categories == index))
        for index, name in enumerate(ENDPOINT_NAMES)
    }


def _broadcast_mask(mask: jax.Array, ndim: int) -> jax.Array:
    return mask.reshape((mask.shape[0],) + (1,) * (ndim - 1))


def _select_broad(
    broad: jax.Array,
    nominal: jax.Array,
    broad_mask: jax.Array,
) -> jax.Array:
    nominal_batch = jnp.broadcast_to(nominal, broad.shape)
    return jnp.where(
        _broadcast_mask(broad_mask, broad.ndim),
        broad,
        nominal_batch,
    )


def make_endpoint_bank_randomizer(
    base_randomizer: Callable[[mjx.Model, jax.Array], tuple[mjx.Model, Any]],
    *,
    torso_body_id: int,
) -> Callable[[mjx.Model, jax.Array], tuple[mjx.Model, Any]]:
    """Keep one broad stratum and add all isolated COM endpoints exactly."""
    torso_body_id = int(torso_body_id)
    if torso_body_id != TORSO_BODY_ID:
        raise ValueError(
            f"T66 torso id must be {TORSO_BODY_ID}, got {torso_body_id}"
        )

    def randomizer(
        model: mjx.Model,
        rng: jax.Array,
    ) -> tuple[mjx.Model, Any]:
        randomized, in_axes = base_randomizer(model, rng)
        population = int(rng.shape[0])
        categories = endpoint_category_ids(population)
        broad_mask = categories == 0

        endpoint_body_ipos = jnp.broadcast_to(
            model.body_ipos,
            randomized.body_ipos.shape,
        )
        offsets = ENDPOINT_OFFSETS_M[categories]
        endpoint_body_ipos = endpoint_body_ipos.at[
            :, torso_body_id, :
        ].add(offsets)

        return randomized.tree_replace(
            {
                "geom_friction": _select_broad(
                    randomized.geom_friction,
                    model.geom_friction,
                    broad_mask,
                ),
                "dof_frictionloss": _select_broad(
                    randomized.dof_frictionloss,
                    model.dof_frictionloss,
                    broad_mask,
                ),
                "dof_armature": _select_broad(
                    randomized.dof_armature,
                    model.dof_armature,
                    broad_mask,
                ),
                "body_mass": _select_broad(
                    randomized.body_mass,
                    model.body_mass,
                    broad_mask,
                ),
                "body_ipos": jnp.where(
                    _broadcast_mask(broad_mask, randomized.body_ipos.ndim),
                    randomized.body_ipos,
                    endpoint_body_ipos,
                ),
                "body_inertia": _select_broad(
                    randomized.body_inertia,
                    model.body_inertia,
                    broad_mask,
                ),
                "body_iquat": _select_broad(
                    randomized.body_iquat,
                    model.body_iquat,
                    broad_mask,
                ),
            }
        ), in_axes

    return randomizer


def update_is_trainable(path: tuple[Any, ...]) -> bool:
    """Allow critics and the three recurrent-core actor groups only."""
    text = jax.tree_util.keystr(path)
    if any(name in text for name in TRAINABLE_ACTOR_CORE_NAMES):
        return True
    if any(name in text for name in FROZEN_ACTOR_NAMES):
        return False
    return True


def mask_noncore_actor_updates(updates: Any) -> Any:
    """Zero every gait-base/output-head actor update exactly."""
    return jax.tree_util.tree_map_with_path(
        lambda path, value: (
            value if update_is_trainable(path) else jnp.zeros_like(value)
        ),
        updates,
    )


@contextmanager
def recurrent_core_only_updates() -> Iterator[None]:
    """Mask optimizer parameter updates for the frozen actor subtrees."""
    original = optax.apply_updates

    def apply_updates(params: Any, updates: Any) -> Any:
        return original(params, mask_noncore_actor_updates(updates))

    if original is apply_updates:
        raise RuntimeError("T66 actor-update mask is re-entrant")
    optax.apply_updates = apply_updates
    try:
        yield
    finally:
        optax.apply_updates = original
