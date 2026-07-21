from __future__ import annotations

import math

import numpy as np
import pytest

from patches import winner_v19_imu_ankle_feedback_magnitude as magnitude


def observation(pitch: float = 0.0, pitch_rate: float = 0.0) -> np.ndarray:
    value = np.zeros((115,), dtype=np.float32)
    value[1] = np.float32(pitch_rate)
    value[3] = np.float32(-9.81 * math.sin(pitch))
    value[5] = np.float32(9.81 * math.cos(pitch))
    return value


def test_constant_magnitudes_are_exact_before_graph_clipping() -> None:
    source = np.zeros((14,), dtype=np.float32)
    delta = np.ones((14,), dtype=np.float32)
    expected = {"CONSTANT_003": 0.12, "CONSTANT_006": 0.24, "CONSTANT_009": 0.36}
    for mode, normalized in expected.items():
        realized, amount, _, _ = magnitude.intervene(
            source, source, delta, observation(), mode
        )
        assert amount == np.float32(1.0)
        assert realized[4] == np.float32(normalized)
        assert realized[13] == np.float32(normalized)
        assert np.count_nonzero(realized) == 2


def test_feedback_magnitudes_share_the_frozen_activation() -> None:
    source = np.zeros((14,), dtype=np.float32)
    delta = np.ones((14,), dtype=np.float32)
    obs = observation(pitch=-0.175)
    values = []
    activations = []
    for mode in ("TILT_RATE_003", "TILT_RATE_006", "TILT_RATE_009"):
        realized, amount, _, _ = magnitude.intervene(source, source, delta, obs, mode)
        values.append(float(realized[4]))
        activations.append(float(amount))
    assert max(activations) - min(activations) == 0.0
    assert np.allclose(values, [0.06, 0.12, 0.18], atol=1.0e-7)


def test_graph_tick_bounds_remain_authoritative() -> None:
    source = np.zeros((14,), dtype=np.float32)
    previous = source.copy()
    delta = np.full((14,), 0.05, dtype=np.float32)
    realized, _, _, _ = magnitude.intervene(
        source, previous, delta, observation(pitch=-0.35), "TILT_RATE_009"
    )
    expected = source.copy()
    expected[[4, 13]] = np.float32(0.05)
    assert np.array_equal(realized, expected)


def test_unknown_mode_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        magnitude.intervene(
            np.zeros(14), np.zeros(14), np.ones(14), observation(), "UNKNOWN"
        )
