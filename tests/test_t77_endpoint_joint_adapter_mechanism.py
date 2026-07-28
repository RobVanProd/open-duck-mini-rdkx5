from __future__ import annotations

import jax.numpy as jnp

from patches.t77_endpoint_joint_adapter_continuation import (
    FROZEN_BASE_ACTOR_NAMES,
    TRAINABLE_JOINT_ADAPTER_NAMES,
    mask_base_actor_updates,
)


def test_t77_exact_actor_group_partition() -> None:
    assert TRAINABLE_JOINT_ADAPTER_NAMES == (
        "adapter_obs_projection",
        "adapter_hidden_projection",
        "adapter_hidden_bias",
        "adapter_location",
    )
    assert FROZEN_BASE_ACTOR_NAMES == (
        "residual_trunk",
        "residual_location",
        "scale_logits",
    )


def test_t77_masks_only_base_actor_groups() -> None:
    updates = {
        "policy": {
            "params": {
                "adapter_obs_projection": {"kernel": jnp.ones((2, 2))},
                "adapter_hidden_projection": {"kernel": jnp.ones((2, 2))},
                "adapter_hidden_bias": jnp.ones((2,)),
                "adapter_location": {
                    "kernel": jnp.ones((2, 2)),
                    "bias": jnp.ones((2,)),
                },
                "residual_trunk": {"kernel": jnp.ones((2, 2))},
                "residual_location": {"kernel": jnp.ones((2, 2))},
                "scale_logits": {"kernel": jnp.ones((2, 2))},
            }
        },
        "critic": {"params": {"dense": {"kernel": jnp.ones((2, 2))}}},
    }
    masked = mask_base_actor_updates(updates)
    params = masked["policy"]["params"]
    for name in TRAINABLE_JOINT_ADAPTER_NAMES:
        leaves = (
            params[name].values()
            if isinstance(params[name], dict)
            else (params[name],)
        )
        assert all(bool(jnp.all(value == 1.0)) for value in leaves)
    for name in FROZEN_BASE_ACTOR_NAMES:
        assert all(
            bool(jnp.all(value == 0.0))
            for value in params[name].values()
        )
    assert bool(
        jnp.all(masked["critic"]["params"]["dense"]["kernel"] == 1.0)
    )
