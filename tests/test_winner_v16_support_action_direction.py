from __future__ import annotations

import numpy as np
import pytest

from patches import winner_v16_support_action_direction as direction


def test_baseline_is_exact_and_intervention_is_one_axis() -> None:
    source = np.linspace(-0.2, 0.2, 14, dtype=np.float32)
    previous = source.copy()
    delta = np.full((14,), 0.2, dtype=np.float32)
    baseline = direction.intervene(source, previous, delta, None, 0)
    assert np.array_equal(baseline, source)
    changed = direction.intervene(
        source, previous, delta, "hip_pitch_magnitude", 1
    )
    expected = source.copy()
    expected[2] -= np.float32(0.12)
    expected[11] += np.float32(0.12)
    assert np.array_equal(changed, expected)


def test_intervention_reapplies_absolute_and_tick_bounds() -> None:
    source = np.ones((14,), dtype=np.float32)
    previous = np.zeros((14,), dtype=np.float32)
    delta = np.full((14,), 0.05, dtype=np.float32)
    value = direction.intervene(source, previous, delta, "ankle", 1)
    assert np.array_equal(value, delta)
    assert np.all(value <= 1.0)
    assert np.all(value >= -1.0)


@pytest.mark.parametrize("axis", ["hip_yaw", "neck", "head", "unknown"])
def test_non_pitch_axis_is_rejected(axis: str) -> None:
    with pytest.raises(ValueError, match="unsupported"):
        direction.intervene(np.zeros(14), np.zeros(14), np.ones(14), axis, 1)
