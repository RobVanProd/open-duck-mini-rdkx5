from __future__ import annotations

import copy
import sys
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("D:/CodexProjects/Open_Duck_Playground-t98-hidden-expert-v1")
GATE = ROOT / "outputs" / "analysis" / "t98_hidden_gate_asset.json"
sys.path.insert(0, str(PLAYGROUND))

from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
    ReferenceResidualRecurrentAdapterPolicy,
)
from playground.common.t98_hidden_expert_continuation import (  # noqa: E402
    mask_protected_actor_updates,
)
from playground.common.t98_hidden_expert_ppo_networks import (  # noqa: E402
    T98HiddenExpertPolicy,
    load_hidden_gate_asset,
)


def modules() -> tuple[
    ReferenceResidualRecurrentAdapterPolicy,
    T98HiddenExpertPolicy,
]:
    gate = load_hidden_gate_asset(GATE)
    return (
        ReferenceResidualRecurrentAdapterPolicy(14, (8, 6), 64),
        T98HiddenExpertPolicy(
            14,
            (8, 6),
            64,
            tuple(gate["mean"]),
            tuple(gate["scale"]),
            tuple(gate["coefficient"]),
            float(gate["intercept"]),
        ),
    )


def test_zero_initialized_hidden_expert_is_exact_source_policy() -> None:
    source_module, expert_module = modules()
    inputs = (
        jnp.linspace(-1.0, 1.0, 115)[None, :],
        jnp.linspace(-0.5, 0.5, 14)[None, :],
        jnp.linspace(0.75, -0.75, 64)[None, :],
    )
    key = jax.random.PRNGKey(20260728)
    source = source_module.init(key, *inputs)
    expert = expert_module.init(key, *inputs)
    for name, value in source["params"].items():
        source_leaves = jax.tree_util.tree_leaves(value)
        expert_leaves = jax.tree_util.tree_leaves(
            expert["params"][name]
        )
        assert len(source_leaves) == len(expert_leaves)
        for source_leaf, expert_leaf in zip(
            source_leaves, expert_leaves, strict=True
        ):
            np.testing.assert_array_equal(source_leaf, expert_leaf)
    assert set(expert["params"]) == {
        *source["params"].keys(),
        "negative_adapter_location",
    }
    assert all(
        np.count_nonzero(np.asarray(value)) == 0
        for value in jax.tree_util.tree_leaves(
            expert["params"]["negative_adapter_location"]
        )
    )
    source_output = source_module.apply(source, *inputs)
    expert_output = expert_module.apply(expert, *inputs)
    for expected, actual in zip(source_output, expert_output, strict=True):
        np.testing.assert_array_equal(expected, actual)


def test_gate_routes_mutated_head_only_on_positive_hidden_states() -> None:
    _, expert_module = modules()
    gate = load_hidden_gate_asset(GATE)
    key = jax.random.PRNGKey(9)
    zeros = (
        jnp.zeros((1, 115)),
        jnp.zeros((1, 14)),
        jnp.zeros((1, 64)),
    )
    params = expert_module.init(key, *zeros)
    mutated = copy.deepcopy(params)
    mutated["params"]["negative_adapter_location"]["bias"] = jnp.full(
        (14,), 0.05
    )
    rng = np.random.default_rng(20260728)
    found: dict[int, tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]] = {}
    for _ in range(512):
        inputs = (
            jnp.asarray(rng.normal(size=(1, 115)), dtype=jnp.float32),
            jnp.asarray(rng.uniform(-0.5, 0.5, size=(1, 14)), dtype=jnp.float32),
            jnp.asarray(rng.normal(size=(1, 64)), dtype=jnp.float32),
        )
        _, hidden = expert_module.apply(params, *inputs)
        score = float(
            np.sum(
                (
                    (np.asarray(hidden)[0] - gate["mean"])
                    / gate["scale"]
                )
                * gate["coefficient"]
            )
            + gate["intercept"]
        )
        found.setdefault(1 if score >= 0.0 else -1, inputs)
        if len(found) == 2:
            break
    assert set(found) == {-1, 1}
    for label, inputs in found.items():
        baseline, baseline_hidden = expert_module.apply(params, *inputs)
        changed, changed_hidden = expert_module.apply(mutated, *inputs)
        np.testing.assert_array_equal(baseline_hidden, changed_hidden)
        if label == -1:
            np.testing.assert_array_equal(baseline, changed)
        else:
            assert float(np.max(np.abs(np.asarray(baseline - changed)))) > 0.01


def test_update_mask_allows_only_negative_head_and_critic() -> None:
    updates = {
        "policy": {
            "adapter_location": {"kernel": jnp.ones((2, 2))},
            "adapter_hidden_bias": jnp.ones((2,)),
            "negative_adapter_location": {
                "kernel": jnp.ones((2, 2)),
                "bias": jnp.ones((2,)),
            },
            "residual_location": {"bias": jnp.ones((2,))},
        },
        "critic": {"kernel": jnp.ones((2, 2))},
    }
    masked = mask_protected_actor_updates(updates)
    assert not np.any(masked["policy"]["adapter_location"]["kernel"])
    assert not np.any(masked["policy"]["adapter_hidden_bias"])
    assert not np.any(masked["policy"]["residual_location"]["bias"])
    assert np.all(masked["policy"]["negative_adapter_location"]["kernel"])
    assert np.all(masked["policy"]["negative_adapter_location"]["bias"])
    assert np.all(masked["critic"]["kernel"])
