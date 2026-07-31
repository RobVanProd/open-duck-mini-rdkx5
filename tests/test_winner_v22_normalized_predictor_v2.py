from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

jax = pytest.importorskip("jax")
import jax.numpy as jnp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "patches"))

import winner_v21_predictor_preserving_joint_support as v21
import winner_v22_normalized_predictor_v2 as v22v2


def test_frozen_scale_matches_zero_update_result() -> None:
    assert float(v22v2.FROZEN_PREDICTOR_SCALE) == 380.9135437011719


def test_explicit_gradient_composition_is_per_leaf() -> None:
    ppo = {
        key: jnp.asarray(np.full((2,), index + 1, dtype=np.float32))
        for index, key in enumerate(v21.JOINT_TRAINABLE_KEYS)
    }
    predictor = {
        key: jnp.asarray(np.full((2,), index + 2, dtype=np.float32))
        for index, key in enumerate(v21.JOINT_TRAINABLE_KEYS)
    }
    result = v22v2.compose_gradients(ppo, predictor)
    for key in v21.JOINT_TRAINABLE_KEYS:
        expected = np.asarray(ppo[key]) + np.float32(380.9135437011719) * np.asarray(
            predictor[key]
        )
        np.testing.assert_array_equal(np.asarray(result[key]), expected)
