from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "t17_support_homeomorphism_onnx.py"
SPEC = importlib.util.spec_from_file_location(
    "t17_support_homeomorphism",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
T17 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T17)


def test_action_homeomorphism_endpoints_center_and_roundtrip() -> None:
    source = np.stack(
        [
            np.full(14, -1.0, dtype=np.float32),
            np.zeros(14, dtype=np.float32),
            np.full(14, 1.0, dtype=np.float32),
            np.linspace(-0.9, 0.9, 14, dtype=np.float32),
        ]
    )
    final = T17.forward_action(source)
    assert np.array_equal(final[0], source[0])
    assert np.array_equal(final[1], T17.SUPPORT_ACTION)
    assert np.array_equal(final[2], source[2])
    assert np.max(np.abs(T17.inverse_action(final) - source)) <= (
        T17.CONTRACT_TOLERANCE
    )
    assert np.all(np.diff(final, axis=0)[:2] >= 0.0)


def test_observation_homeomorphism_changes_only_frozen_slices() -> None:
    parameters = T17.observation_parameters()
    changed = np.flatnonzero(
        np.any(
            np.stack(
                [
                    parameters["center"] != 0.0,
                    parameters["base"] != 0.0,
                    parameters["upper_slope"] != 1.0,
                    parameters["lower_slope"] != 1.0,
                ]
            ),
            axis=0,
        )[0]
    )
    support_joints = np.flatnonzero(T17.SUPPORT_ACTION)
    expected = np.unique(
        np.concatenate(
            [
                13 + support_joints,
                41 + support_joints,
                55 + support_joints,
                69 + support_joints,
                83
                + np.flatnonzero(
                    (T17.HOME_ACTION_RAD != 0.0)
                    | (T17.SUPPORT_ACTION != 0.0)
                ),
            ]
        )
    )
    assert np.array_equal(changed, expected)

    source = np.zeros((1, 115), dtype=np.float32)
    source[0, 83:97] = T17.HOME_ACTION_RAD
    final = T17.forward_observation(source)
    expected_final = source.copy()
    expected_final[0, 13:27] = (
        T17.SUPPORT_ACTION * T17.ACTION_SCALE_RAD
    )
    expected_final[0, 41:55] = T17.SUPPORT_ACTION
    expected_final[0, 55:69] = T17.SUPPORT_ACTION
    expected_final[0, 69:83] = T17.SUPPORT_ACTION
    expected_final[0, 83:97] = (
        T17.HOME_ACTION_RAD
        + T17.SUPPORT_ACTION * T17.ACTION_SCALE_RAD
    )
    assert np.array_equal(final, expected_final)
    assert np.max(
        np.abs(T17.inverse_observation(final) - source)
    ) <= T17.CONTRACT_TOLERANCE


def test_map_is_canonical_and_has_no_free_scalar() -> None:
    assert T17.CONTRACT_TOLERANCE == (
        32.0 * np.finfo(np.float32).eps
    )
    assert np.all(np.abs(T17.SUPPORT_ACTION) < 1.0)
    assert np.array_equal(
        np.float32(1.0) - T17.SUPPORT_ACTION,
        np.asarray(
            [
                1.0,
                1.0,
                1.5,
                0.75,
                0.75,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                0.5,
                0.75,
                0.75,
            ],
            dtype=np.float32,
        ),
    )
