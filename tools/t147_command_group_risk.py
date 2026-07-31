"""Parameter-free worst-command-group PPO actor objective."""

from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp


COMMAND_ANCHORS = jnp.asarray([0.074, 0.077, 0.080], dtype=jnp.float32)
COMMAND_BOUNDARIES = jnp.asarray(
    [
        (0.074 + 0.077) / 2.0,
        (0.077 + 0.080) / 2.0,
    ],
    dtype=jnp.float32,
)


def command_group_ids(command_x: jax.Array) -> jax.Array:
    """Map command x to its nearest frozen gate anchor."""
    value = jnp.asarray(command_x, dtype=jnp.float32)
    return jnp.where(
        value < COMMAND_BOUNDARIES[0],
        0,
        jnp.where(value < COMMAND_BOUNDARIES[1], 1, 2),
    ).astype(jnp.int32)


def grouped_policy_loss(
    clipped_surrogate: jax.Array,
    command_x: jax.Array,
) -> tuple[jax.Array, dict[str, Any]]:
    """Return the largest per-command-group PPO policy loss.

    `clipped_surrogate` is `min(rho*A, clip(rho)*A)` after the frozen global
    advantage normalization. Minimizing the maximum negative group mean makes
    the weakest command group authoritative for the actor update while leaving
    the critic and entropy terms unchanged.
    """
    surrogate = jnp.asarray(clipped_surrogate, dtype=jnp.float32)
    groups = command_group_ids(command_x)
    if surrogate.shape != groups.shape:
        raise ValueError(
            f"T147 surrogate/group shape mismatch: {surrogate.shape}, "
            f"{groups.shape}"
        )
    flat_surrogate = surrogate.reshape(-1)
    flat_groups = groups.reshape(-1)
    losses = []
    counts = []
    for group_id in range(3):
        mask = (flat_groups == group_id).astype(jnp.float32)
        count = jnp.sum(mask)
        mean = jnp.sum(mask * flat_surrogate) / jnp.maximum(count, 1.0)
        losses.append(jnp.where(count > 0.0, -mean, -jnp.inf))
        counts.append(count)
    group_losses = jnp.stack(losses)
    group_counts = jnp.stack(counts)
    selected = jnp.argmax(group_losses)
    loss = group_losses[selected]
    return loss, {
        "group_losses": group_losses,
        "group_counts": group_counts,
        "selected_group": selected,
        "all_groups_present": jnp.all(group_counts > 0.0),
    }
