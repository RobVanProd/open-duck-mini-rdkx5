from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest


jax = pytest.importorskip("jax")
jnp = pytest.importorskip("jax.numpy")


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "patches"))

import winner_v12_calibrator_training as training
import winner_v21_predictor_preserving_joint_support as v21


def parameters() -> dict[str, jax.Array]:
    return training.initialize_training_parameters(7)


def batch() -> dict[str, jax.Array]:
    observations = np.zeros((1, 3, training.OBS_SIZE), dtype=np.float32)
    observations[0, 1:, training.AUXILIARY_INDICES] = 0.1
    return {
        "observations": jnp.asarray(observations),
        "previous_actions": jnp.zeros((1, 3, training.ACTION_SIZE)),
        "realized_actions": jnp.zeros((1, 3, training.ACTION_SIZE)),
        "valid_mask": jnp.ones((1, 3)),
        "valid_transition_mask": jnp.ones((1, 3)),
    }


def test_trainable_scope_adds_only_existing_auxiliary_head() -> None:
    value = parameters()
    selected = v21.joint_trainable_parameters(value)
    assert tuple(selected) == v21.JOINT_TRAINABLE_KEYS
    assert len(selected) == 12
    assert set(v21.PREDICTOR_KEYS) == {
        "auxiliary_hidden_weight",
        "auxiliary_action_weight",
        "auxiliary_bias",
    }
    assert set(selected) <= set(value)


def test_predictor_loss_uses_only_stored_successor_transitions() -> None:
    value = parameters()
    data = batch()
    loss, metrics = v21.predictor_loss(
        value, data, jnp.ones((len(training.AUXILIARY_INDICES),))
    )
    assert np.isfinite(float(loss))
    assert float(loss) > 0.0
    assert float(metrics["stored_successor_transition_count"]) == 2.0


def test_gradient_balance_is_one_positive_deterministic_ratio() -> None:
    shape = {name: value.shape for name, value in parameters().items()}
    ppo = {
        name: jnp.ones(shape[name], dtype=jnp.float32)
        if name in v21.POLICY_HEAD_KEYS
        else jnp.zeros(shape[name], dtype=jnp.float32)
        for name in v21.JOINT_TRAINABLE_KEYS
    }
    predictor = {
        name: jnp.full(shape[name], 2.0, dtype=jnp.float32)
        if name in v21.PREDICTOR_KEYS
        else jnp.zeros(shape[name], dtype=jnp.float32)
        for name in v21.JOINT_TRAINABLE_KEYS
    }
    scale, receipt = v21.gradient_balance_scale(ppo, predictor)
    assert float(scale) == 0.5
    assert receipt["ppo_action_head_gradient_rms"] == 1.0
    assert receipt["predictor_head_gradient_rms"] == 2.0
