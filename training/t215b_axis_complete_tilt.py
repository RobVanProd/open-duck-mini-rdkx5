"""Training-only axis-complete predicted-tilt safety-box cost.

T214B froze two independent 80 ms prediction envelopes from every row of
33 historical passing traces.  Normalizing each axis before taking the
componentwise maximum prevents a constrained policy from trading lateral
stability for sagittal instability (or vice versa).

This module changes training cost only.  It adds no observation, recurrent
state, action transform, deployment graph operation, or runtime behavior.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp


PREDICTION_HORIZON_S = 0.08
ROLL_PASSING_ENVELOPE_RAD = 0.3541802655745987
PITCH_PASSING_ENVELOPE_RAD = 0.2379576557426921


def quaternion_wxyz_to_roll_pitch(
    quaternion_wxyz: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    """Return the exact evaluator roll and pitch conventions."""
    quaternion = jnp.asarray(quaternion_wxyz, dtype=jnp.float32)
    w, x, y, z = quaternion
    two = jnp.float32(2.0)
    one = jnp.float32(1.0)
    roll = jnp.arctan2(
        two * (w * x + y * z),
        one - two * (x * x + y * y),
    )
    sin_pitch = two * (w * y - z * x)
    pitch = jnp.arcsin(
        jnp.clip(sin_pitch, jnp.float32(-1.0), jnp.float32(1.0))
    )
    return roll, pitch


def predicted_axis_risks_rad(
    quaternion_wxyz: jax.Array,
    roll_rate_rad_s: jax.Array,
    pitch_rate_rad_s: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    """Return absolute roll and pitch predicted over the frozen horizon."""
    roll, pitch = quaternion_wxyz_to_roll_pitch(quaternion_wxyz)
    horizon = jnp.float32(PREDICTION_HORIZON_S)
    roll_risk = jnp.abs(
        roll + horizon * jnp.asarray(roll_rate_rad_s, dtype=jnp.float32)
    )
    pitch_risk = jnp.abs(
        pitch + horizon * jnp.asarray(pitch_rate_rad_s, dtype=jnp.float32)
    )
    return roll_risk, pitch_risk


def normalized_axis_risks(
    roll_risk_rad: jax.Array,
    pitch_risk_rad: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    """Normalize each predicted tilt axis by its pass-derived envelope."""
    return (
        jnp.asarray(roll_risk_rad, dtype=jnp.float32)
        / jnp.float32(ROLL_PASSING_ENVELOPE_RAD),
        jnp.asarray(pitch_risk_rad, dtype=jnp.float32)
        / jnp.float32(PITCH_PASSING_ENVELOPE_RAD),
    )


def tilt_box_score(
    roll_risk_rad: jax.Array,
    pitch_risk_rad: jax.Array,
) -> jax.Array:
    """Return the componentwise normalized safety-box score."""
    roll_normalized, pitch_normalized = normalized_axis_risks(
        roll_risk_rad,
        pitch_risk_rad,
    )
    return jnp.maximum(roll_normalized, pitch_normalized)


def tilt_box_excess(score: jax.Array) -> jax.Array:
    """Return normalized hinge excess outside the pass-derived box."""
    return jnp.maximum(
        jnp.asarray(score, dtype=jnp.float32) - jnp.float32(1.0),
        jnp.float32(0.0),
    )


def tilt_box_cost(score: jax.Array) -> jax.Array:
    """Return the unscaled squared box-exceedance training cost."""
    return jnp.square(tilt_box_excess(score))
