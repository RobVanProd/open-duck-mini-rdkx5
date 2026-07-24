from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from exact_torque_oracle import (  # noqa: E402
    ProjectionConstants,
    project_action,
    supreme_action_bounds,
)


def test_supreme_bounds_intersect_absolute_rate_and_guard() -> None:
    low, high = supreme_action_bounds(
        actual_position_rad=[0.10, 0.0],
        home_position_rad=[0.0, 0.0],
        previous_action=[0.2, -0.9],
        action_scale_rad=0.25,
        action_delta=[0.1, 0.2],
        guard_joint_indices=[0],
        guard_rad=0.05,
    )
    np.testing.assert_allclose(low, [0.2, -1.0])
    np.testing.assert_allclose(high, [0.3, -0.7])


def test_linear_rollout_projects_nearest_safe_action() -> None:
    def rollout(action: np.ndarray) -> np.ndarray:
        force = np.zeros((3, 2), dtype=np.float64)
        force[2, 0] = 3.0 * float(action[0])
        force[1, 1] = -4.0 * float(action[1])
        return force

    projected, audit = project_action(
        base_action=[1.0, -1.0],
        low_action=[-1.0, -1.0],
        high_action=[1.0, 1.0],
        force_horizon_ticks=[2, 1],
        rollout=rollout,
        constants=ProjectionConstants(
            torque_limit_nm=1.0,
            force_tolerance_nm=1.0e-8,
            monotonicity_tolerance_nm=1.0e-10,
            bisection_iterations=40,
        ),
    )
    np.testing.assert_allclose(projected, [1.0 / 3.0, -0.25], atol=2.0e-7)
    assert audit["empty_intersection_joint_indices"] == []
    assert audit["projected_joint_indices"] == [0, 1]
    assert max(abs(value) for value in audit["predicted_force_nm"]) <= 1.0 + 1.0e-8


def test_empty_intersection_is_reported_without_fabricating_safety() -> None:
    def rollout(action: np.ndarray) -> np.ndarray:
        del action
        return np.asarray([[2.0]], dtype=np.float64)

    projected, audit = project_action(
        base_action=[0.0],
        low_action=[-0.2],
        high_action=[0.2],
        force_horizon_ticks=[0],
        rollout=rollout,
        constants=ProjectionConstants(torque_limit_nm=1.0),
    )
    np.testing.assert_array_equal(projected, np.zeros(1, dtype=np.float32))
    assert audit["empty_intersection_joint_indices"] == [0]
    assert audit["predicted_force_nm"] == [2.0]


def test_nonmonotone_map_fails_closed() -> None:
    def rollout(action: np.ndarray) -> np.ndarray:
        return np.asarray([[2.0 + np.sin(8.0 * float(action[0]))]], dtype=np.float64)

    with pytest.raises(ValueError, match="not monotone"):
        project_action(
            base_action=[0.0],
            low_action=[-1.0],
            high_action=[1.0],
            force_horizon_ticks=[0],
            rollout=rollout,
            constants=ProjectionConstants(torque_limit_nm=1.0),
        )
