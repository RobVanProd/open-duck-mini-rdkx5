from __future__ import annotations

import importlib.util
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "patches" / "t66_endpoint_core_continuation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("t66_mechanism", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_endpoint_categories_are_exact_and_uniform() -> None:
    module = load_module()
    counts = module.endpoint_category_counts(256)
    assert list(counts) == list(module.ENDPOINT_NAMES)
    assert set(counts.values()) == {32}
    np.testing.assert_array_equal(
        np.asarray(module.ENDPOINT_OFFSETS_M),
        np.asarray(
            [
                [0, 0, 0],
                [0, 0, 0],
                [-0.05, 0, 0],
                [0.05, 0, 0],
                [0, -0.05, 0],
                [0, 0.05, 0],
                [0, 0, -0.05],
                [0, 0, 0.05],
            ],
            dtype=np.float32,
        ),
    )


def test_update_mask_freezes_only_noncore_actor_groups() -> None:
    module = load_module()
    updates = {
        "policy": {
            "params": {
                "residual_trunk": {"kernel": jnp.ones((2, 2))},
                "residual_location": {"bias": jnp.ones((2,))},
                "scale_logits": {"bias": jnp.ones((2,))},
                "adapter_location": {"kernel": jnp.ones((2, 2))},
                "adapter_obs_projection": {"kernel": jnp.ones((2, 2))},
                "adapter_hidden_projection": {"kernel": jnp.ones((2, 2))},
                "adapter_hidden_bias": jnp.ones((2,)),
            }
        },
        "value": {"params": {"kernel": jnp.ones((2, 2))}},
    }
    masked = module.mask_noncore_actor_updates(updates)
    policy = masked["policy"]["params"]
    for name in module.FROZEN_ACTOR_NAMES:
        leaves = jax.tree_util.tree_leaves(policy[name])
        assert all(np.all(np.asarray(leaf) == 0) for leaf in leaves)
    for name in module.TRAINABLE_ACTOR_CORE_NAMES:
        leaves = jax.tree_util.tree_leaves(policy[name])
        assert all(np.all(np.asarray(leaf) == 1) for leaf in leaves)
    assert np.all(np.asarray(masked["value"]["params"]["kernel"]) == 1)
