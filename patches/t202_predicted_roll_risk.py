"""Training-only predicted-roll risk objective.

T201B selected one runtime-observable, source-transferring signal:

    abs(roll + 0.08 * roll_rate)

The envelope is the next representable float above the maximum signal over
every row of all 18 frozen passing T170/T194 traces.  The scale is derived
once so the mean weighted cost over the 45 frozen violating rows in the two
known roll-collapse failures equals one existing alive-reward tick.

This module changes training reward only.  It adds no policy input, recurrent
state, action transform, deployment graph operation, or runtime behavior.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp


PREDICTION_HORIZON_S = 0.08
PASSING_ENVELOPE_RAD = 0.3541802655745987
ALIVE_REWARD_SCALE = 20.0
CONTROL_DT_S = 0.02
ALIVE_REWARD_PER_TICK = ALIVE_REWARD_SCALE * CONTROL_DT_S
FROZEN_FAILURE_EXCEEDANCE_ROWS = 45
FROZEN_FAILURE_SQUARED_EXCESS_INTEGRAL = 22.450151776859293
ROLL_RISK_SCALE = (
    ALIVE_REWARD_PER_TICK
    * FROZEN_FAILURE_EXCEEDANCE_ROWS
    / FROZEN_FAILURE_SQUARED_EXCESS_INTEGRAL
)


def quaternion_wxyz_to_roll(quaternion_wxyz: jax.Array) -> jax.Array:
    """Return the exact roll convention used by the frozen evaluator."""
    quaternion = jnp.asarray(quaternion_wxyz, dtype=jnp.float32)
    w, x, y, z = quaternion
    numerator = jnp.float32(2.0) * (w * x + y * z)
    denominator = jnp.float32(1.0) - jnp.float32(2.0) * (
        x * x + y * y
    )
    return jnp.arctan2(numerator, denominator)


def predicted_roll_rad(
    roll_rad: jax.Array,
    roll_rate_rad_s: jax.Array,
) -> jax.Array:
    """Predict roll over the frozen four-tick actuator horizon."""
    return jnp.asarray(roll_rad, dtype=jnp.float32) + jnp.float32(
        PREDICTION_HORIZON_S
    ) * jnp.asarray(roll_rate_rad_s, dtype=jnp.float32)


def predicted_roll_risk_rad(
    quaternion_wxyz: jax.Array,
    roll_rate_rad_s: jax.Array,
) -> jax.Array:
    """Return absolute predicted roll from simulator state."""
    return jnp.abs(
        predicted_roll_rad(
            quaternion_wxyz_to_roll(quaternion_wxyz),
            roll_rate_rad_s,
        )
    )


def roll_risk_excess_rad(risk_rad: jax.Array) -> jax.Array:
    """Return hinge excess above the pass-derived envelope."""
    return jnp.maximum(
        jnp.asarray(risk_rad, dtype=jnp.float32)
        - jnp.float32(PASSING_ENVELOPE_RAD),
        jnp.float32(0.0),
    )


def roll_risk_cost(risk_rad: jax.Array) -> jax.Array:
    """Return the derived reward-unit cost for one transition."""
    excess = roll_risk_excess_rad(risk_rad)
    return jnp.float32(ROLL_RISK_SCALE) * jnp.square(excess)


def curriculum_reward(
    original_clipped_reward: jax.Array,
    risk_cost: jax.Array,
) -> jax.Array:
    """Subtract risk outside the original positive reward clip."""
    return jnp.asarray(original_clipped_reward) - jnp.asarray(risk_cost)
