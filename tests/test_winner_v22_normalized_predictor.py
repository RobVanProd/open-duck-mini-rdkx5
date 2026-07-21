from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

jax = pytest.importorskip("jax")
import jax.numpy as jnp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "patches"))

import winner_v12_calibrator_training as training
import winner_v22_normalized_predictor as v22


def test_evaluator_matches_normalized_coordinate_definition() -> None:
    mean = np.linspace(-0.4, 0.6, 50, dtype=np.float32)
    std = np.linspace(0.01, 0.5, 50, dtype=np.float32)
    target = mean + 0.25 * std
    prediction = np.full((50,), 0.2, dtype=np.float32)
    learned = v22.normalized_prediction_squared_error(prediction, target, mean, std)
    constant = v22.normalized_constant_squared_error(target, mean, std)
    np.testing.assert_allclose(learned, np.full((50,), 0.0025), rtol=0, atol=2e-8)
    np.testing.assert_allclose(constant, np.full((50,), 0.0625), rtol=0, atol=2e-8)


def test_corrected_loss_uses_target_mean_and_stored_successor_mask() -> None:
    rng = np.random.default_rng(2201)
    parameters = training.initialize_training_parameters(2202)
    observations = rng.normal(size=(2, 4, training.OBS_SIZE)).astype(np.float32)
    previous = rng.normal(size=(2, 4, training.ACTION_SIZE)).astype(np.float32)
    realized = rng.normal(size=(2, 4, training.ACTION_SIZE)).astype(np.float32)
    valid = np.ones((2, 4), dtype=np.float32)
    valid[1, 2:] = 0.0
    batch = {
        "observations": jnp.asarray(observations),
        "previous_actions": jnp.asarray(previous),
        "realized_actions": jnp.asarray(realized),
        "valid_mask": jnp.asarray(valid),
        "valid_transition_mask": jnp.asarray(valid),
    }
    mean = np.linspace(-0.2, 0.2, 50, dtype=np.float32)
    std = np.linspace(0.05, 0.4, 50, dtype=np.float32)
    loss, metrics = v22.normalized_predictor_loss(
        parameters, batch, jnp.asarray(mean), jnp.asarray(std)
    )
    assert np.isfinite(float(loss))
    assert float(loss) > 0.0
    assert int(metrics["stored_successor_transition_count"]) == 4


def test_evaluator_rejects_nonpositive_scale() -> None:
    with pytest.raises(ValueError, match="normalization changed"):
        v22.normalized_prediction_squared_error(
            np.zeros((50,)), np.zeros((50,)), np.zeros((50,)), np.zeros((50,))
        )
