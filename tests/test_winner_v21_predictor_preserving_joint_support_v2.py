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
import winner_v21_predictor_preserving_joint_support_v2 as v21v2


def test_frozen_scale_is_exactly_the_imported_single_evaluation() -> None:
    assert float(v21v2.FROZEN_PREDICTOR_SCALE) == 8.393629541414427e-11


def test_optimizer_gradient_is_explicit_per_leaf_composition() -> None:
    parameters = training.initialize_training_parameters(7)
    shapes = {name: parameters[name].shape for name in v21.JOINT_TRAINABLE_KEYS}
    ppo = {
        name: jnp.ones(shape, dtype=jnp.float32) for name, shape in shapes.items()
    }
    predictor = {
        name: jnp.full(shape, 2.0, dtype=jnp.float32)
        for name, shape in shapes.items()
    }
    combined = v21v2.compose_gradients(ppo, predictor)
    expected = np.float32(1.0) + v21v2.FROZEN_PREDICTOR_SCALE * np.float32(2.0)
    assert tuple(combined) == v21.JOINT_TRAINABLE_KEYS
    assert all(np.all(np.asarray(value) == expected) for value in combined.values())


def test_twelve_leaf_snapshot_round_trip(tmp_path: Path) -> None:
    parameters = training.initialize_training_parameters(7)
    optimizer = training.adam_initialize(v21.joint_trainable_parameters(parameters))
    path = tmp_path / "proof.npz"
    receipt = v21v2.save_snapshot(
        path,
        parameters,
        optimizer,
        {"stage": "predictor_preserving_joint_stage2", "completed_updates": 2},
        np.zeros(3, dtype=np.float32),
        np.ones(3, dtype=np.float32),
    )
    loaded = v21v2.load_snapshot(path)
    assert receipt["completed_updates"] == 2
    assert loaded["metadata"]["completed_updates"] == 2
    assert set(loaded["optimizer"]["m"]) == set(v21.JOINT_TRAINABLE_KEYS)
    assert all(
        np.array_equal(loaded["parameters"][key], np.asarray(value))
        for key, value in parameters.items()
    )
