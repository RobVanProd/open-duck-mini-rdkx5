"""Training-only in-episode bilateral single-support prefix primitives.

T185 is mechanically distinct from the closed T55/T62 reward-homotopy
family:

* the support side and frozen phase come from the reference contact channels,
  not from a sign heuristic over the phase sine;
* the support objective occupies only the first reference period of every
  episode;
* normal locomotion resumes in the same episode, without a separate
  optimizer stage or checkpoint transfer.

No robot dimensions, mass, center of mass, or manually measured geometry
enter this mechanism.  The deployment graph does not call this module.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp


REFERENCE_PERIOD_TICKS = 27
PREFIX_TICKS = REFERENCE_PERIOD_TICKS
LEFT_SUPPORT_SIDE = 0
RIGHT_SUPPORT_SIDE = 1
REFERENCE_SUPPORT_PHASES = jnp.asarray([2, 15], dtype=jnp.int32)
PITCH_ROLL_GATE_RAD = 0.25
CONTROL_HORIZON_TICKS = 4
CONTROL_DT_S = 0.02
CONTROL_HORIZON_S = CONTROL_HORIZON_TICKS * CONTROL_DT_S
ALIVE_REWARD_SCALE = 20.0
ALIVE_REWARD_PER_TICK = ALIVE_REWARD_SCALE * CONTROL_DT_S


def phase_vector(
    phase_index: jax.Array | int,
    period_ticks: int = REFERENCE_PERIOD_TICKS,
) -> jax.Array:
    """Return the exact two-value phase observation for an integer index."""
    phase = (
        jnp.asarray(phase_index, dtype=jnp.float32)
        / jnp.float32(period_ticks)
        * jnp.float32(2.0 * jnp.pi)
    )
    return jnp.asarray([jnp.cos(phase), jnp.sin(phase)])


def sample_support_side(rng: jax.Array) -> jax.Array:
    """Choose left or right with the symmetry-derived Bernoulli(0.5) rule."""
    return jax.random.bernoulli(rng, p=0.5).astype(jnp.int32)


def support_phase_index(side: jax.Array | int) -> jax.Array:
    """Map the selected side to its reference-derived single-support phase."""
    side_index = jnp.asarray(side, dtype=jnp.int32)
    return REFERENCE_SUPPORT_PHASES[side_index]


def target_support(side: jax.Array | int) -> jax.Array:
    """Return exact [left, right] target contact for the selected side."""
    side_index = jnp.asarray(side, dtype=jnp.int32)
    return jnp.asarray(
        [
            side_index == LEFT_SUPPORT_SIDE,
            side_index == RIGHT_SUPPORT_SIDE,
        ],
        dtype=jnp.bool_,
    )


def phase_for_step(
    current_phase: jax.Array | int,
    support_phase: jax.Array | int,
    prefix_ticks_remaining: jax.Array | int,
    period_ticks: int = REFERENCE_PERIOD_TICKS,
) -> jax.Array:
    """Hold the support phase during the prefix, then resume normal advance."""
    current = jnp.asarray(current_phase, dtype=jnp.int32)
    anchor = jnp.asarray(support_phase, dtype=jnp.int32)
    remaining = jnp.asarray(prefix_ticks_remaining, dtype=jnp.int32)
    return jnp.where(
        remaining > 0,
        anchor,
        (current + jnp.int32(1)) % jnp.int32(period_ticks),
    )


def remaining_after_step(
    prefix_ticks_remaining: jax.Array | int,
) -> jax.Array:
    """Consume one prefix tick without underflow."""
    remaining = jnp.asarray(prefix_ticks_remaining, dtype=jnp.int32)
    return jnp.maximum(remaining - jnp.int32(1), jnp.int32(0))


def matched_support_sides(
    contact: jax.Array,
    side: jax.Array | int,
) -> jax.Array:
    """Return separate exact-match [left, right] support indicators."""
    observed = jnp.asarray(contact, dtype=jnp.bool_)
    expected = target_support(side)
    exact_single = jnp.asarray(
        [
            observed[0] & ~observed[1],
            observed[1] & ~observed[0],
        ]
    )
    return exact_single & expected


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
    side: jax.Array | int,
) -> jax.Array:
    """Reward stable exact single support on the selected reference side."""
    tilt = predicted_tilt_rad(projected_gravity, body_gyro_rad_s)
    normalized = jnp.sum(
        jnp.square(tilt / jnp.float32(PITCH_ROLL_GATE_RAD))
    )
    quality = jnp.exp(-normalized)
    matched = jnp.any(matched_support_sides(contact, side))
    return (
        jnp.float32(ALIVE_REWARD_PER_TICK)
        * matched.astype(jnp.float32)
        * quality
    )


def curriculum_reward(
    original_reward: jax.Array,
    support_reward: jax.Array,
    prefix_ticks_remaining: jax.Array | int,
) -> jax.Array:
    """Use support reward only during the prefix, then original reward."""
    return jnp.where(
        jnp.asarray(prefix_ticks_remaining, dtype=jnp.int32) > 0,
        support_reward,
        original_reward,
    )
