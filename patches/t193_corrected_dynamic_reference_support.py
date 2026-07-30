"""Training-only corrected dynamic reference-support objective.

The reference motion already labels left and right foot contact in channels
32 and 33.  T193 uses those labels directly throughout locomotion.  It does
not infer support from the sign of the phase vector, freeze phase, introduce
a separate optimizer stage, or change the deployment graph.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp


REFERENCE_LEFT_CONTACT_INDEX = 32
REFERENCE_RIGHT_CONTACT_INDEX = 33
REFERENCE_CONTACT_SLICE = slice(
    REFERENCE_LEFT_CONTACT_INDEX,
    REFERENCE_RIGHT_CONTACT_INDEX + 1,
)
PITCH_ROLL_GATE_RAD = 0.25
CONTROL_HORIZON_TICKS = 4
CONTROL_DT_S = 0.02
CONTROL_HORIZON_S = CONTROL_HORIZON_TICKS * CONTROL_DT_S
ALIVE_REWARD_SCALE = 20.0
ALIVE_REWARD_PER_TICK = ALIVE_REWARD_SCALE * CONTROL_DT_S


def reference_support_sides(reference_motion: jax.Array) -> jax.Array:
    """Return exact reference-requested [left, right] single-support sides."""
    reference = jnp.asarray(reference_motion, dtype=jnp.float32)
    contact = reference[REFERENCE_CONTACT_SLICE] > jnp.float32(0.5)
    return jnp.asarray(
        [
            contact[0] & ~contact[1],
            contact[1] & ~contact[0],
        ],
        dtype=jnp.bool_,
    )


def observed_support_sides(contact: jax.Array) -> jax.Array:
    """Return exact observed [left, right] single-support sides."""
    observed = jnp.asarray(contact, dtype=jnp.bool_)
    return jnp.asarray(
        [
            observed[0] & ~observed[1],
            observed[1] & ~observed[0],
        ],
        dtype=jnp.bool_,
    )


def matched_support_sides(
    contact: jax.Array,
    reference_motion: jax.Array,
) -> jax.Array:
    """Return separate exact reference/observation support matches."""
    return observed_support_sides(contact) & reference_support_sides(
        reference_motion
    )


def predicted_tilt_rad(
    projected_gravity: jax.Array,
    body_gyro_rad_s: jax.Array,
) -> jax.Array:
    """Predict roll/pitch tilt over the measured four-tick control horizon."""
    gravity = jnp.asarray(projected_gravity, dtype=jnp.float32)
    gyro = jnp.asarray(body_gyro_rad_s, dtype=jnp.float32)
    current_tilt = jnp.arcsin(
        jnp.clip(gravity[:2], jnp.float32(-1.0), jnp.float32(1.0))
    )
    return current_tilt + jnp.float32(CONTROL_HORIZON_S) * gyro[:2]


def single_support_balance_reward(
    projected_gravity: jax.Array,
    body_gyro_rad_s: jax.Array,
    contact: jax.Array,
    reference_motion: jax.Array,
) -> jax.Array:
    """Reward stable exact support when the reference asks for one foot.

    A perfect match is worth one existing alive-reward tick.  Double support,
    flight, the wrong foot, and reference rows that do not request exact
    single support receive zero from this additional objective.
    """
    tilt = predicted_tilt_rad(projected_gravity, body_gyro_rad_s)
    normalized = jnp.sum(
        jnp.square(tilt / jnp.float32(PITCH_ROLL_GATE_RAD))
    )
    quality = jnp.exp(-normalized)
    matched = jnp.any(matched_support_sides(contact, reference_motion))
    return (
        jnp.float32(ALIVE_REWARD_PER_TICK)
        * matched.astype(jnp.float32)
        * quality
    )


def curriculum_reward(
    original_reward: jax.Array,
    support_reward: jax.Array,
) -> jax.Array:
    """Add support credit to the unchanged locomotion objective."""
    return jnp.asarray(original_reward) + jnp.asarray(support_reward)
