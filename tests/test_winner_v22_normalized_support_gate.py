from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

jnp = pytest.importorskip("jax.numpy")


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "patches"))

import winner_v22_normalized_support_gate as gate


def parameters() -> dict[str, jnp.ndarray]:
    return {
        "auxiliary_hidden_weight": jnp.arange(150, dtype=jnp.float32).reshape(3, 50) / 100.0,
        "auxiliary_action_weight": jnp.arange(100, dtype=jnp.float32).reshape(2, 50) / 50.0,
        "auxiliary_bias": jnp.linspace(-0.25, 0.25, 50, dtype=jnp.float32),
        "action_weight": jnp.ones((3, 2), dtype=jnp.float32),
    }


def test_raw_projection_is_algebraically_identical_to_denormalization() -> None:
    source = parameters()
    mean = np.linspace(-2.0, 2.0, 50, dtype=np.float32)
    std = np.linspace(0.25, 1.75, 50, dtype=np.float32)
    hidden = jnp.asarray([0.25, -0.5, 0.75], dtype=jnp.float32)
    action = jnp.asarray([-0.4, 0.2], dtype=jnp.float32)
    normalized = (
        hidden @ source["auxiliary_hidden_weight"]
        + action @ source["auxiliary_action_weight"]
        + source["auxiliary_bias"]
    )
    adapted = gate.raw_coordinate_predictor_parameters(source, mean, std)
    raw = (
        hidden @ adapted["auxiliary_hidden_weight"]
        + action @ adapted["auxiliary_action_weight"]
        + adapted["auxiliary_bias"]
    )
    expected = normalized * jnp.asarray(std) + jnp.asarray(mean)
    np.testing.assert_allclose(np.asarray(raw), np.asarray(expected), rtol=2.0e-6, atol=2.0e-6)
    assert adapted["action_weight"] is source["action_weight"]


@pytest.mark.parametrize("bad_std", [np.zeros(50, dtype=np.float32), np.ones(49, dtype=np.float32)])
def test_projection_rejects_invalid_target_statistics(bad_std: np.ndarray) -> None:
    with pytest.raises(ValueError):
        gate.raw_coordinate_predictor_parameters(
            parameters(), np.zeros(50, dtype=np.float32), bad_std
        )


def test_projection_has_no_hardware_surface() -> None:
    source = (ROOT / "patches/winner_v22_normalized_support_gate.py").read_text(
        encoding="utf-8"
    )
    assert "serial" not in source
    assert "gpio" not in source.lower()
    assert "torque" not in source.lower()
    assert "ssh" not in source.lower()
