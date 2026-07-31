from __future__ import annotations

import numpy as np

from tools.run_t183_hidden_gate_confidence import (
    confidence_threshold,
    hidden_gate_score,
)


def test_hidden_gate_score_matches_frozen_equation() -> None:
    hidden = np.asarray([[1.0, 3.0]], dtype=np.float32)
    initializers = {
        "hidden_gate_mean": np.asarray([0.5, 1.0], dtype=np.float32),
        "hidden_gate_scale": np.asarray([0.5, 2.0], dtype=np.float32),
        "hidden_gate_coefficient": np.asarray(
            [[2.0], [-1.0]], dtype=np.float32
        ),
        "hidden_gate_intercept": np.asarray([0.25], dtype=np.float32),
    }
    actual = hidden_gate_score(hidden, initializers)
    assert np.array_equal(actual, np.asarray([1.25], dtype=np.float32))


def test_confidence_threshold_is_exact_gap_midpoint() -> None:
    threshold, margin = confidence_threshold(
        [0.7, 0.8, 0.9], [0.1, 0.3, 0.4]
    )
    assert threshold == 0.55
    assert margin == 0.29999999999999993


def test_confidence_threshold_reports_overlap_without_search() -> None:
    threshold, margin = confidence_threshold([0.2, 0.5], [0.1, 0.3])
    assert threshold == 0.25
    assert margin < 0.0
