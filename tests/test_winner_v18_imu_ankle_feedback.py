from __future__ import annotations

import math

import numpy as np
import pytest

from patches import winner_v18_imu_ankle_feedback as feedback


def observation(pitch: float = 0.0, pitch_rate: float = 0.0) -> np.ndarray:
    value = np.zeros((115,), dtype=np.float32)
    value[1] = np.float32(pitch_rate)
    value[3] = np.float32(-9.81 * math.sin(pitch))
    value[5] = np.float32(9.81 * math.cos(pitch))
    return value


def test_backward_tilt_and_rate_reach_full_activation_at_frozen_references() -> None:
    tilt, proxy, rate = feedback.activation(
        observation(pitch=-0.35), "TILT_BACKWARD"
    )
    assert tilt == np.float32(1.0)
    assert abs(float(proxy) + 0.35) < 1.0e-6
    assert rate == np.float32(0.0)

    amount, _, observed_rate = feedback.activation(
        observation(pitch_rate=-1.75), "RATE_BACKWARD"
    )
    assert amount == np.float32(1.0)
    assert observed_rate == np.float32(-1.75)


def test_opposite_controls_are_one_sided() -> None:
    backward = observation(pitch=-0.2, pitch_rate=-0.8)
    assert feedback.activation(backward, "TILT_OPPOSITE")[0] == 0.0
    assert feedback.activation(backward, "RATE_OPPOSITE")[0] == 0.0
    assert feedback.activation(backward, "TILT_RATE_BACKWARD")[0] > 0.0


def test_feedback_changes_only_ankles_and_reapplies_bounds() -> None:
    source = np.zeros((14,), dtype=np.float32)
    previous = source.copy()
    delta = np.full((14,), 0.2, dtype=np.float32)
    realized, amount, _, _ = feedback.intervene(
        source, previous, delta, observation(pitch=-0.35), "TILT_BACKWARD"
    )
    expected = source.copy()
    expected[[4, 13]] = np.float32(0.12)
    assert amount == np.float32(1.0)
    assert np.array_equal(realized, expected)

    bounded, _, _, _ = feedback.intervene(
        np.ones((14,), dtype=np.float32),
        np.zeros((14,), dtype=np.float32),
        np.full((14,), 0.05, dtype=np.float32),
        observation(pitch=-0.35),
        "TILT_BACKWARD",
    )
    assert np.array_equal(bounded, np.full((14,), 0.05, dtype=np.float32))


def test_malformed_inputs_and_unknown_mode_are_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        feedback.activation(observation(), "UNKNOWN")
    with pytest.raises(ValueError, match="115-vector"):
        feedback.activation(np.zeros((114,), dtype=np.float32), "BASELINE")
