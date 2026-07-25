"""V173 lexicographic cost-first and cost-tangent actor direction."""

from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp


def tree_dot(left: Any, right: Any) -> jax.Array:
    products = [
        jnp.vdot(jnp.asarray(a), jnp.asarray(b))
        for a, b in zip(
            jax.tree_util.tree_leaves(left),
            jax.tree_util.tree_leaves(right),
            strict=True,
        )
    ]
    return sum(products, jnp.asarray(0.0, dtype=jnp.float32))


def _scale(tree: Any, scalar: jax.Array) -> Any:
    return jax.tree_util.tree_map(lambda leaf: scalar * leaf, tree)


def _where(condition: jax.Array, when_true: Any, when_false: Any) -> Any:
    return jax.tree_util.tree_map(
        lambda left, right: jnp.where(condition, left, right),
        when_true,
        when_false,
    )


def select_actor_direction(
    reward_gradient: Any,
    cost_gradient: Any,
    *,
    batch_cost: jax.Array,
    cost_seen_before: jax.Array,
    max_grad_norm: float | None,
) -> tuple[Any, dict[str, jax.Array]]:
    """Selects and norm-clips V173's actor parameter direction.

    The returned tree is a parameter direction, not a loss gradient:

    * before any positive cost: reward descent;
    * on a positive-cost batch: cost descent;
    * after positive cost, on zero-cost batches: reward descent projected onto
      the first-order cost-nonincreasing half-space.
    """
    reward_descent = jax.tree_util.tree_map(
        lambda leaf: -leaf, reward_gradient
    )
    cost_descent = jax.tree_util.tree_map(lambda leaf: -leaf, cost_gradient)
    cost_norm_sq = tree_dot(cost_gradient, cost_gradient)
    reward_norm_sq = tree_dot(reward_descent, reward_descent)
    before = tree_dot(cost_gradient, reward_descent)
    projection_active = jnp.logical_and(before > 0.0, cost_norm_sq > 0.0)
    coefficient = jnp.where(
        projection_active,
        before / jnp.maximum(cost_norm_sq, jnp.finfo(jnp.float32).tiny),
        0.0,
    )
    tangent = jax.tree_util.tree_map(
        lambda direction, gradient: direction - coefficient * gradient,
        reward_descent,
        cost_gradient,
    )
    positive_cost = batch_cost > 0.0
    use_tangent = jnp.logical_and(
        jnp.logical_not(positive_cost), cost_seen_before
    )
    raw_direction = _where(
        positive_cost,
        cost_descent,
        _where(use_tangent, tangent, reward_descent),
    )
    raw_norm_sq = tree_dot(raw_direction, raw_direction)
    raw_norm = jnp.sqrt(jnp.maximum(raw_norm_sq, 0.0))
    if max_grad_norm is None:
        clip_scale = jnp.asarray(1.0, dtype=raw_norm.dtype)
    else:
        limit = jnp.asarray(max_grad_norm, dtype=raw_norm.dtype)
        clip_scale = jnp.minimum(
            1.0, limit / jnp.maximum(raw_norm, jnp.finfo(jnp.float32).tiny)
        )
    direction = _scale(raw_direction, clip_scale)
    direction_norm = jnp.sqrt(
        jnp.maximum(tree_dot(direction, direction), 0.0)
    )
    tangent_norm = jnp.sqrt(
        jnp.maximum(tree_dot(tangent, tangent), 0.0)
    )
    tangent_retention = jnp.where(
        reward_norm_sq > 0.0,
        tangent_norm / jnp.sqrt(reward_norm_sq),
        0.0,
    )
    return direction, {
        "reward_only_branch": jnp.logical_and(
            jnp.logical_not(positive_cost),
            jnp.logical_not(cost_seen_before),
        ).astype(jnp.float32),
        "cost_first_branch": positive_cost.astype(jnp.float32),
        "tangent_branch": use_tangent.astype(jnp.float32),
        "projection_active": projection_active.astype(jnp.float32),
        "reward_gradient_norm": jnp.sqrt(
            jnp.maximum(reward_norm_sq, 0.0)
        ),
        "cost_gradient_norm": jnp.sqrt(jnp.maximum(cost_norm_sq, 0.0)),
        "raw_direction_norm": raw_norm,
        "clipped_direction_norm": direction_norm,
        "clip_scale": clip_scale,
        "selected_cost_derivative": tree_dot(cost_gradient, direction),
        "tangent_cost_derivative": tree_dot(cost_gradient, tangent),
        "tangent_reward_retention": tangent_retention,
    }
