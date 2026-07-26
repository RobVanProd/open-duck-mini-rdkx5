from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
MODULE_PATH = ROOT / "tools" / "t18_rate_coherent_support_onnx.py"
SPEC = importlib.util.spec_from_file_location(
    "t18_rate_coherent_support",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
T18 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T18)


def test_rate_vector_and_normalized_delta_are_frozen() -> None:
    expected_rates = np.asarray(
        [
            1.0,
            0.75,
            1.5,
            1.5,
            1.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.75,
            1.25,
            1.0,
            1.25,
        ],
        dtype=np.float32,
    )
    assert np.array_equal(T18.RATE_LIMITS_RAD_S, expected_rates)
    assert np.array_equal(
        T18.MAX_ACTION_DELTA,
        expected_rates * np.float32(0.08),
    )


def test_rate_projection_is_exact_and_bounded() -> None:
    previous = np.asarray(
        [[-0.9, -0.5, -0.2, 0.0, 0.3, 0.9, 0.0] * 2],
        dtype=np.float32,
    )
    target = -previous
    final = T18.rate_project(target, previous)
    assert np.all(final >= -1.0)
    assert np.all(final <= 1.0)
    assert np.all(
        np.abs(final - previous)
        <= T18.MAX_ACTION_DELTA[None, :] + np.finfo(np.float32).eps
    )


def test_support_is_fixed_point_of_rate_projection() -> None:
    support = T18.SUPPORT_ACTION[None, :]
    assert np.array_equal(
        T18.rate_project(support, support),
        support,
    )
