from __future__ import annotations

import numpy as np

from tools.run_t181_count_weighted_head_interpolation import interpolate


def test_interpolation_uses_float64_then_single_float32_cast() -> None:
    source = np.asarray([0.1, -0.3], dtype=np.float32)
    transformed = np.asarray([0.5, 0.7], dtype=np.float32)
    actual = interpolate(source, transformed, 0.2)
    expected = (
        source.astype(np.float64)
        + 0.2
        * (transformed.astype(np.float64) - source.astype(np.float64))
    ).astype(np.float32)
    assert actual.dtype == np.float32
    assert np.array_equal(actual, expected)


def test_alpha_endpoints_are_exact() -> None:
    source = np.asarray([0.1, -0.3], dtype=np.float32)
    transformed = np.asarray([0.5, 0.7], dtype=np.float32)
    assert np.array_equal(interpolate(source, transformed, 0.0), source)
    assert np.array_equal(
        interpolate(source, transformed, 1.0), transformed
    )
