from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from exact_torque_oracle import (  # noqa: E402
    project_action as project_frozen_sparse_action,
)
from exact_torque_oracle_all_tick import (  # noqa: E402
    ProjectionConstants,
    project_action,
)


def linear_rollout(action: np.ndarray) -> np.ndarray:
    return np.asarray([[2.0 * float(action[0])]], dtype=np.float64)


def test_all_tick_projector_clips_requested_base_to_supreme_interval() -> None:
    projected, audit = project_action(
        base_action=[0.5],
        low_action=[-0.2],
        high_action=[0.2],
        force_horizon_ticks=[0],
        rollout=linear_rollout,
        constants=ProjectionConstants(torque_limit_nm=1.0),
    )
    np.testing.assert_allclose(projected, [0.2])
    assert audit["base_action"] == [0.5]
    assert audit["supreme_feasible_base_action"] == [0.2]
    assert audit["base_supreme_clipped_joint_indices"] == [0]
    assert audit["base_supreme_clip_linf"] == pytest.approx(0.3)
    assert audit["torque_projection_clip_linf"] == 0.0
    assert audit["clip_linf"] == pytest.approx(0.3)


def test_all_tick_projector_logs_feasibility_and_torque_clips_separately() -> None:
    projected, audit = project_action(
        base_action=[1.0],
        low_action=[-0.8],
        high_action=[0.8],
        force_horizon_ticks=[0],
        rollout=linear_rollout,
        constants=ProjectionConstants(
            torque_limit_nm=1.0,
            bisection_iterations=40,
        ),
    )
    np.testing.assert_allclose(projected, [0.5], atol=2.0e-7)
    assert audit["base_supreme_clip_linf"] == pytest.approx(0.2)
    assert audit["torque_projection_clip_linf"] == pytest.approx(
        0.3, abs=2.0e-7
    )
    assert audit["clip_linf"] == pytest.approx(0.5, abs=2.0e-7)


def test_frozen_sparse_projector_still_fails_outside_supreme_interval() -> None:
    with pytest.raises(
        ValueError, match="base action violates the supreme oracle interval"
    ):
        project_frozen_sparse_action(
            base_action=[0.5],
            low_action=[-0.2],
            high_action=[0.2],
            force_horizon_ticks=[0],
            rollout=linear_rollout,
        )
