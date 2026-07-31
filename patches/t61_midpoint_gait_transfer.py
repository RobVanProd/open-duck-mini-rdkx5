"""Training-only midpoint between balance and full gait objectives.

The locomotion coefficient is the arithmetic midpoint of the already closed
T56 stage endpoints, zero (balance only) and one (full transfer).  It is a
fixed causal test, not a tunable reward scale.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp


BALANCE_LOCOMOTION_WEIGHT = 0.0
FULL_TRANSFER_LOCOMOTION_WEIGHT = 1.0
MIDPOINT_LOCOMOTION_WEIGHT = (
    BALANCE_LOCOMOTION_WEIGHT + FULL_TRANSFER_LOCOMOTION_WEIGHT
) / 2.0


def midpoint_transfer_reward(
    original_reward: jax.Array,
    support_reward: jax.Array,
) -> jax.Array:
    """Return support plus the fixed midpoint locomotion objective."""
    return (
        jnp.asarray(support_reward, dtype=jnp.float32)
        + jnp.float32(MIDPOINT_LOCOMOTION_WEIGHT)
        * jnp.asarray(original_reward, dtype=jnp.float32)
    )
