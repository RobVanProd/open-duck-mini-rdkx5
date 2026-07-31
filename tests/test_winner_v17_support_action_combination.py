from __future__ import annotations

import numpy as np
import pytest

from patches import winner_v17_support_action_combination as combination


def test_baseline_is_exact() -> None:
    source = np.linspace(-0.2, 0.2, 14, dtype=np.float32)
    delta = np.full((14,), 0.2, dtype=np.float32)
    observed = combination.intervene(source, source, delta, None, 0)
    assert np.array_equal(observed, source)


def test_triple_applies_the_evidence_selected_sign_vector() -> None:
    source = np.zeros((14,), dtype=np.float32)
    delta = np.full((14,), 0.2, dtype=np.float32)
    observed = combination.intervene(
        source,
        source,
        delta,
        ["HIP_MAG_NEG", "KNEE_POS", "ANKLE_POS"],
        1,
    )
    expected = np.zeros((14,), dtype=np.float32)
    expected[[2, 3, 4]] = np.float32(0.12)
    expected[[11, 12, 13]] = np.asarray([-0.12, 0.12, 0.12], dtype=np.float32)
    assert np.array_equal(observed, expected)


def test_combination_reapplies_absolute_and_tick_bounds() -> None:
    source = np.ones((14,), dtype=np.float32)
    previous = np.zeros((14,), dtype=np.float32)
    delta = np.full((14,), 0.05, dtype=np.float32)
    value = combination.intervene(
        source, previous, delta, ["KNEE_POS", "ANKLE_POS"], 1
    )
    assert np.array_equal(value, delta)


@pytest.mark.parametrize(
    "axes,direction",
    [([], 1), (["HIP_MAG_POS"], 1), (["KNEE_POS", "KNEE_POS"], 1), (["KNEE_POS"], -1)],
)
def test_unselected_or_malformed_combination_is_rejected(
    axes: list[str], direction: int
) -> None:
    with pytest.raises(ValueError, match="unsupported"):
        combination.intervene(
            np.zeros(14), np.zeros(14), np.ones(14), axes, direction
        )
