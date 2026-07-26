from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "t16_support_coordinate_onnx.py"
SPEC = importlib.util.spec_from_file_location(
    "t16_support_coordinate",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
T16 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T16)


def test_observation_delta_exact_slices() -> None:
    delta = T16.observation_delta()
    assert delta.shape == (1, 115)
    target = T16.SUPPORT_ACTION * T16.ACTION_SCALE_RAD
    assert np.array_equal(delta[0, 13:27], target)
    assert np.array_equal(delta[0, 41:55], T16.SUPPORT_ACTION)
    assert np.array_equal(delta[0, 55:69], T16.SUPPORT_ACTION)
    assert np.array_equal(delta[0, 69:83], T16.SUPPORT_ACTION)
    assert np.array_equal(delta[0, 83:97], target)
    assert np.count_nonzero(delta[0, :13]) == 0
    assert np.count_nonzero(delta[0, 27:41]) == 0
    assert np.count_nonzero(delta[0, 97:115]) == 0


def test_support_action_changes_only_pitch_chain() -> None:
    expected_nonzero = {2, 3, 4, 11, 12, 13}
    observed = set(np.flatnonzero(T16.SUPPORT_ACTION).tolist())
    assert observed == expected_nonzero
    assert np.max(np.abs(T16.SUPPORT_ACTION)) == np.float32(0.5)
