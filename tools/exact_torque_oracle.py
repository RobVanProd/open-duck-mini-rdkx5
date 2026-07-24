#!/usr/bin/env python3
"""Deterministic action projection against an exact simulator rollout callback.

The projector is deliberately simulator-agnostic.  Its caller owns complete
state snapshot/restore and supplies a pure ``rollout(action)`` callback whose
result is actuator force for control offsets ``0..max(horizon)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

import numpy as np


Rollout = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class ProjectionConstants:
    torque_limit_nm: float = 1.91229675
    force_tolerance_nm: float = 5.0e-6
    monotonicity_tolerance_nm: float = 5.0e-6
    monotonicity_grid_points: int = 9
    bisection_iterations: int = 32
    maximum_coordinate_passes: int = 14


def supreme_action_bounds(
    *,
    actual_position_rad: Sequence[float],
    home_position_rad: Sequence[float],
    previous_action: Sequence[float],
    action_scale_rad: float,
    action_delta: Sequence[float],
    guard_joint_indices: Sequence[int],
    guard_rad: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Intersect absolute, previous-action rate, and actual-centered bounds."""

    actual = np.asarray(actual_position_rad, dtype=np.float64)
    home = np.asarray(home_position_rad, dtype=np.float64)
    previous = np.asarray(previous_action, dtype=np.float64)
    delta = np.asarray(action_delta, dtype=np.float64)
    if not (
        actual.shape == home.shape == previous.shape == delta.shape
        and actual.ndim == 1
    ):
        raise ValueError("oracle action-bound arrays must be equal 1-D shapes")
    if not np.all(np.isfinite(np.concatenate((actual, home, previous, delta)))):
        raise ValueError("oracle action-bound arrays must be finite")
    if float(action_scale_rad) <= 0.0 or float(guard_rad) <= 0.0:
        raise ValueError("oracle action scale and guard must be positive")
    if np.any(delta < 0.0):
        raise ValueError("oracle action deltas must be nonnegative")

    low = np.maximum(-1.0, previous - delta)
    high = np.minimum(1.0, previous + delta)
    indices = np.asarray(tuple(guard_joint_indices), dtype=np.int64)
    if np.any(indices < 0) or np.any(indices >= actual.size):
        raise ValueError("oracle guard index outside action contract")
    guard_low = (actual[indices] - float(guard_rad) - home[indices]) / float(
        action_scale_rad
    )
    guard_high = (actual[indices] + float(guard_rad) - home[indices]) / float(
        action_scale_rad
    )
    low[indices] = np.maximum(low[indices], guard_low)
    high[indices] = np.minimum(high[indices], guard_high)
    if np.any(low > high):
        raise ValueError("supreme oracle action bounds have an empty intersection")
    return low, high


def _force_at_horizon(
    rollout: Rollout,
    action: np.ndarray,
    *,
    joint: int,
    horizon: int,
    action_dim: int,
) -> tuple[float, np.ndarray]:
    force = np.asarray(rollout(action.astype(np.float32)), dtype=np.float64)
    if (
        force.ndim != 2
        or force.shape[1] != action_dim
        or force.shape[0] <= horizon
        or not np.all(np.isfinite(force))
    ):
        raise ValueError(
            "oracle rollout must return finite [offsets, action_dim] force"
        )
    return float(force[horizon, joint]), force


def _monotone_direction(values: np.ndarray, tolerance: float) -> int:
    differences = np.diff(values)
    nondecreasing = bool(np.all(differences >= -float(tolerance)))
    nonincreasing = bool(np.all(differences <= float(tolerance)))
    if nondecreasing and not nonincreasing:
        return 1
    if nonincreasing and not nondecreasing:
        return -1
    if nondecreasing and nonincreasing:
        return 0
    raise ValueError("action-to-torque map is not monotone on the supreme interval")


def _nearest_safe_scalar(
    *,
    action: np.ndarray,
    joint: int,
    horizon: int,
    low: float,
    high: float,
    rollout: Rollout,
    constants: ProjectionConstants,
) -> tuple[float | None, dict[str, Any], int]:
    grid = np.linspace(
        float(low),
        float(high),
        int(constants.monotonicity_grid_points),
        dtype=np.float64,
    )
    grid_force = np.empty_like(grid)
    evaluations = 0
    for index, value in enumerate(grid):
        candidate = action.copy()
        candidate[joint] = value
        grid_force[index], _ = _force_at_horizon(
            rollout,
            candidate,
            joint=joint,
            horizon=horizon,
            action_dim=action.size,
        )
        evaluations += 1
    direction = _monotone_direction(
        grid_force, constants.monotonicity_tolerance_nm
    )
    current_force, _ = _force_at_horizon(
        rollout,
        action,
        joint=joint,
        horizon=horizon,
        action_dim=action.size,
    )
    evaluations += 1
    limit = float(constants.torque_limit_nm)
    if abs(current_force) <= limit + float(constants.force_tolerance_nm):
        return float(action[joint]), {
            "grid_action": grid.tolist(),
            "grid_force_nm": grid_force.tolist(),
            "monotone_direction": direction,
            "current_force_nm": current_force,
            "already_safe": True,
        }, evaluations

    if current_force > limit:
        endpoint = float(low if direction >= 0 else high)
        target = limit

        def safe_when(value: float) -> bool:
            return value <= target

    else:
        endpoint = float(high if direction >= 0 else low)
        target = -limit

        def safe_when(value: float) -> bool:
            return value >= target
    endpoint_action = action.copy()
    endpoint_action[joint] = endpoint
    endpoint_force, _ = _force_at_horizon(
        rollout,
        endpoint_action,
        joint=joint,
        horizon=horizon,
        action_dim=action.size,
    )
    evaluations += 1
    diagnostic = {
        "grid_action": grid.tolist(),
        "grid_force_nm": grid_force.tolist(),
        "monotone_direction": direction,
        "current_force_nm": current_force,
        "endpoint_action": endpoint,
        "endpoint_force_nm": endpoint_force,
        "already_safe": False,
    }
    if not safe_when(endpoint_force):
        diagnostic["empty_intersection"] = True
        return None, diagnostic, evaluations

    unsafe_action = float(action[joint])
    safe_action = endpoint
    for _ in range(int(constants.bisection_iterations)):
        midpoint = 0.5 * (unsafe_action + safe_action)
        candidate = action.copy()
        candidate[joint] = midpoint
        midpoint_force, _ = _force_at_horizon(
            rollout,
            candidate,
            joint=joint,
            horizon=horizon,
            action_dim=action.size,
        )
        evaluations += 1
        if safe_when(midpoint_force):
            safe_action = midpoint
        else:
            unsafe_action = midpoint
    candidate = action.copy()
    candidate[joint] = safe_action
    safe_force, _ = _force_at_horizon(
        rollout,
        candidate,
        joint=joint,
        horizon=horizon,
        action_dim=action.size,
    )
    evaluations += 1
    diagnostic.update(
        {
            "empty_intersection": False,
            "projected_action": safe_action,
            "projected_force_nm": safe_force,
        }
    )
    if abs(safe_force) > limit + float(constants.force_tolerance_nm):
        raise ValueError("bisection did not return a torque-safe action")
    return safe_action, diagnostic, evaluations


def project_action(
    *,
    base_action: Sequence[float],
    low_action: Sequence[float],
    high_action: Sequence[float],
    force_horizon_ticks: Sequence[int],
    rollout: Rollout,
    constants: ProjectionConstants = ProjectionConstants(),
) -> tuple[np.ndarray, dict[str, Any]]:
    """Project to the nearest coordinate-wise exact-rollout torque-safe action.

    Empty intersections remain unchanged and are explicitly reported.  A
    non-monotone map or a safe-coordinate interaction that survives the fixed
    coordinate passes is an invalid oracle screen, never a policy result.
    """

    action = np.asarray(base_action, dtype=np.float64).copy()
    low = np.asarray(low_action, dtype=np.float64)
    high = np.asarray(high_action, dtype=np.float64)
    horizons = np.asarray(force_horizon_ticks, dtype=np.int64)
    if not (
        action.ndim == 1
        and action.shape == low.shape == high.shape == horizons.shape
    ):
        raise ValueError("oracle projection arrays must be equal 1-D shapes")
    if (
        np.any(low > high)
        or np.any(action < low - 1.0e-7)
        or np.any(action > high + 1.0e-7)
        or np.any(horizons < 0)
    ):
        raise ValueError("base action violates the supreme oracle interval")
    if (
        constants.monotonicity_grid_points < 3
        or constants.bisection_iterations < 1
        or constants.maximum_coordinate_passes < 1
    ):
        raise ValueError("oracle projection iteration constants are invalid")

    action = np.clip(action, low, high)
    base = action.copy()
    empty: set[int] = set()
    projected: set[int] = set()
    joint_diagnostics: list[dict[str, Any]] = []
    rollout_evaluations = 0
    final_force = None
    force_action: np.ndarray | None = None
    converged = False
    for coordinate_pass in range(int(constants.maximum_coordinate_passes)):
        _, force = _force_at_horizon(
            rollout,
            action,
            joint=0,
            horizon=int(horizons[0]),
            action_dim=action.size,
        )
        rollout_evaluations += 1
        force_action = action.copy()
        final_force = np.asarray(
            [force[int(horizons[joint]), joint] for joint in range(action.size)],
            dtype=np.float64,
        )
        violations = [
            joint
            for joint in range(action.size)
            if joint not in empty
            and abs(float(final_force[joint]))
            > float(constants.torque_limit_nm)
            + float(constants.force_tolerance_nm)
        ]
        if not violations:
            converged = True
            break
        joint = int(violations[0])
        projected_value, diagnostic, evaluations = _nearest_safe_scalar(
            action=action,
            joint=joint,
            horizon=int(horizons[joint]),
            low=float(low[joint]),
            high=float(high[joint]),
            rollout=rollout,
            constants=constants,
        )
        rollout_evaluations += evaluations
        diagnostic.update(
            {
                "coordinate_pass": coordinate_pass,
                "joint_index": joint,
                "horizon_ticks": int(horizons[joint]),
            }
        )
        joint_diagnostics.append(diagnostic)
        if projected_value is None:
            empty.add(joint)
        else:
            previous = float(action[joint])
            action[joint] = float(projected_value)
            projected.add(joint)
            if action[joint] == previous:
                raise ValueError("oracle projection made no progress")

    if (
        final_force is None
        or force_action is None
        or not np.array_equal(force_action, action)
    ):
        _, force = _force_at_horizon(
            rollout,
            action,
            joint=0,
            horizon=int(horizons[0]),
            action_dim=action.size,
        )
        rollout_evaluations += 1
        final_force = np.asarray(
            [
                force[int(horizons[joint]), joint]
                for joint in range(action.size)
            ],
            dtype=np.float64,
        )
    unresolved_nonempty = [
        joint
        for joint in range(action.size)
        if joint not in empty
        and abs(float(final_force[joint]))
        > float(constants.torque_limit_nm)
        + float(constants.force_tolerance_nm)
    ]
    if unresolved_nonempty:
        raise ValueError(
            "coordinate oracle failed to converge for non-empty intersections: "
            f"{unresolved_nonempty}"
        )
    return action.astype(np.float32), {
        "status": "PASS_EXACT_TORQUE_ORACLE_PROJECTION",
        "converged": converged or not unresolved_nonempty,
        "base_action": base.tolist(),
        "final_action": action.tolist(),
        "low_action": low.tolist(),
        "high_action": high.tolist(),
        "force_horizon_ticks": horizons.astype(int).tolist(),
        "predicted_force_nm": final_force.tolist(),
        "projected_joint_indices": sorted(projected),
        "empty_intersection_joint_indices": sorted(empty),
        "joint_diagnostics": joint_diagnostics,
        "rollout_evaluations": int(rollout_evaluations),
        "clip_linf": float(np.max(np.abs(action - base))),
        "clip_l2": float(np.linalg.norm(action - base)),
    }
