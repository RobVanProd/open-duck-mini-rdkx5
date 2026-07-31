from __future__ import annotations

import numpy as np

from tools.exact_torque_oracle_all_tick import ProjectionConstants
from tools.exact_torque_oracle_two_fit import project_two_fit_action


def rollout(offset: float):
    def evaluate(action: np.ndarray) -> np.ndarray:
        return np.asarray([[2.0 * (float(action[0]) + offset)]])

    return evaluate


def test_two_fit_projection_finds_shared_safe_action() -> None:
    action, result = project_two_fit_action(
        base_action=[1.0],
        low_action=[-1.0],
        high_action=[1.0],
        force_horizon_ticks=[0],
        primary_rollout=rollout(0.0),
        shadow_rollout=rollout(0.1),
        constants=ProjectionConstants(torque_limit_nm=1.0),
    )
    assert result["robust_safe"] is True
    assert result["empty_intersection_joint_indices"] == []
    assert float(action[0]) <= 0.4 + 1.0e-6
    assert abs(result["predicted_force_nm"][0]) <= 1.0 + 5.0e-6
    assert abs(result["predicted_shadow_force_nm"][0]) <= 1.0 + 5.0e-6


def test_two_fit_projection_reports_conflicting_safe_sets() -> None:
    _, result = project_two_fit_action(
        base_action=[0.0],
        low_action=[-1.0],
        high_action=[1.0],
        force_horizon_ticks=[0],
        primary_rollout=rollout(1.0),
        shadow_rollout=rollout(-1.0),
        constants=ProjectionConstants(torque_limit_nm=0.5),
        maximum_fit_passes=4,
    )
    assert result["robust_safe"] is False
    assert result["status"] == "NO_COMMON_EXACT_TWO_FIT_TORQUE_ACTION"
    assert result["empty_intersection_joint_indices"] == [0]
