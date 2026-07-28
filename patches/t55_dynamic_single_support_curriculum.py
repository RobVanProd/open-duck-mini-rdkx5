"""Training-only bilateral single-support curriculum primitives.

The mechanism uses quantities already produced by simulation: projected
gravity, body angular velocity, contact bits, and the observed gait phase.
It deliberately uses no manual mass, center-of-mass, or foot measurement.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp


PITCH_ROLL_GATE_RAD = 0.25
CONTROL_HORIZON_TICKS = 4
CONTROL_DT_S = 0.02
CONTROL_HORIZON_S = CONTROL_HORIZON_TICKS * CONTROL_DT_S
ALIVE_REWARD_SCALE = 20.0
ALIVE_REWARD_PER_TICK = ALIVE_REWARD_SCALE * CONTROL_DT_S


def phase_target_support(
    imitation_phase: jax.Array,
) -> jax.Array:
    """Return [left, right] target support from the observed gait phase.

    The frozen reference period uses the negative sine half-cycle for left
    support and the positive sine half-cycle for right support.  The zero
    boundary belongs to left support, matching the green phase-zero traces.
    """
    phase = jnp.asarray(imitation_phase, dtype=jnp.float32)
    target_left = phase[1] <= jnp.float32(0.0)
    return jnp.asarray([target_left, ~target_left], dtype=jnp.bool_)


def exact_target_single_support(
    contact: jax.Array,
    imitation_phase: jax.Array,
) -> jax.Array:
    """Indicate exact one-foot contact on the phase-selected side."""
    observed = jnp.asarray(contact, dtype=jnp.bool_)
    target = phase_target_support(imitation_phase)
    one_foot = jnp.logical_xor(observed[0], observed[1])
    return one_foot & jnp.all(observed == target)


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
    imitation_phase: jax.Array,
) -> jax.Array:
    """Reward stable, phase-correct unilateral support on either side.

    The scale is derived from the existing alive reward: a perfect matched
    support tick is worth exactly one alive-reward tick.  The smooth quality
    reaches exp(-1) when the predicted roll/pitch norm reaches the unchanged
    0.25-rad behavior boundary.
    """
    tilt = predicted_tilt_rad(projected_gravity, body_gyro_rad_s)
    normalized = jnp.sum(
        jnp.square(tilt / jnp.float32(PITCH_ROLL_GATE_RAD))
    )
    quality = jnp.exp(-normalized)
    matched = exact_target_single_support(contact, imitation_phase)
    return (
        jnp.float32(ALIVE_REWARD_PER_TICK)
        * matched.astype(jnp.float32)
        * quality
    )


def curriculum_reward(
    original_reward: jax.Array,
    support_reward: jax.Array,
    *,
    balance_stage: bool,
    transfer_stage: bool,
) -> jax.Array:
    """Select the frozen two-stage objective with exact default-off behavior."""
    if balance_stage and transfer_stage:
        raise ValueError("T55 stages are mutually exclusive")
    if balance_stage:
        return support_reward
    if transfer_stage:
        return original_reward + support_reward
    return original_reward
