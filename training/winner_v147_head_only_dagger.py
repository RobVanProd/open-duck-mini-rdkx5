"""Action-head-only DAgger update on the V145 aggregate."""

from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

import winner_v145_on_policy_dagger as v145


ACTION_SIZE = v145.ACTION_SIZE
HIDDEN_SIZE = v145.HIDDEN_SIZE
OBS_SIZE = v145.OBS_SIZE
STD_BACKTRACK_LIMIT = v145.STD_BACKTRACK_LIMIT
ARMIJO_FRACTION = v145.ARMIJO_FRACTION
LABELED_JOINTS = (0, 1, 3, 7, 8, 10, 13)
TRAINABLE_HEADS = ("adapter_location", "residual_location")

loss_components = v145.loss_components
gradient_norm = v145.gradient_norm
apply_gradient = v145.apply_gradient
deployed_actions = v145.deployed_actions
build_aggregated_dataset = v145.build_aggregated_dataset
load_shadow_dataset = v145.load_shadow_dataset
interpolate_policy = v145.interpolate_policy


def mask_head_gradients(grads: Any) -> Any:
    """Keep only labeled output columns of the two location heads."""
    zeroed = jax.tree_util.tree_map(jnp.zeros_like, grads)
    updated = dict(zeroed)
    params = dict(zeroed["params"])
    source = grads["params"]
    joint_mask = jnp.asarray(
        np.isin(np.arange(ACTION_SIZE), LABELED_JOINTS),
        dtype=jnp.float32,
    )
    for name in TRAINABLE_HEADS:
        layer = dict(params[name])
        layer["bias"] = source[name]["bias"] * joint_mask
        layer["kernel"] = source[name]["kernel"] * joint_mask[None, :]
        params[name] = layer
    updated["params"] = params
    return updated
