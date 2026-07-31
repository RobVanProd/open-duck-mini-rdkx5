#!/usr/bin/env python3
"""Alternating exact action projection across two measured actuator fits."""

from __future__ import annotations

from typing import Any, Callable, Sequence

import numpy as np

try:
    from exact_torque_oracle_all_tick import (
        ProjectionConstants,
        project_action,
    )
except ModuleNotFoundError:
    from tools.exact_torque_oracle_all_tick import (
        ProjectionConstants,
        project_action,
    )


Rollout = Callable[[np.ndarray], np.ndarray]


def horizon_force(
    rollout: Rollout,
    action: np.ndarray,
    horizons: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    rows = np.asarray(rollout(action.astype(np.float32)), dtype=np.float64)
    if (
        rows.ndim != 2
        or rows.shape[1] != action.size
        or rows.shape[0] <= int(np.max(horizons))
        or not np.all(np.isfinite(rows))
    ):
        raise ValueError("two-fit rollout must return finite [offset, joint]")
    selected = np.asarray(
        [rows[int(horizons[joint]), joint] for joint in range(action.size)],
        dtype=np.float64,
    )
    return selected, rows


def project_two_fit_action(
    *,
    base_action: Sequence[float],
    low_action: Sequence[float],
    high_action: Sequence[float],
    force_horizon_ticks: Sequence[int],
    primary_rollout: Rollout,
    shadow_rollout: Rollout,
    constants: ProjectionConstants = ProjectionConstants(),
    maximum_fit_passes: int = 14,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Find one action safe under both exact fit rollouts, or report conflict."""

    requested = np.asarray(base_action, dtype=np.float64)
    low = np.asarray(low_action, dtype=np.float64)
    high = np.asarray(high_action, dtype=np.float64)
    horizons = np.asarray(force_horizon_ticks, dtype=np.int64)
    if not (
        requested.ndim == 1
        and requested.shape == low.shape == high.shape == horizons.shape
    ):
        raise ValueError("two-fit projection arrays must have equal 1-D shape")
    if np.any(low > high) or np.any(horizons < 0):
        raise ValueError("two-fit projection received invalid bounds or horizon")
    if maximum_fit_passes < 1:
        raise ValueError("two-fit projection requires at least one fit pass")

    action = np.clip(requested, low, high)
    supreme_base = action.copy()
    diagnostics: list[dict[str, Any]] = []
    projected: set[int] = set()
    empty: set[int] = set()
    rollout_evaluations = 0
    converged = False
    for fit_pass in range(maximum_fit_passes):
        primary_force, _ = horizon_force(
            primary_rollout, action, horizons
        )
        shadow_force, _ = horizon_force(shadow_rollout, action, horizons)
        rollout_evaluations += 2
        primary_safe = np.abs(primary_force) <= (
            constants.torque_limit_nm + constants.force_tolerance_nm
        )
        shadow_safe = np.abs(shadow_force) <= (
            constants.torque_limit_nm + constants.force_tolerance_nm
        )
        if bool(np.all(primary_safe) and np.all(shadow_safe)):
            converged = True
            break
        prior = action.copy()
        for label, rollout, safe in (
            ("primary", primary_rollout, primary_safe),
            ("shadow", shadow_rollout, shadow_safe),
        ):
            if bool(np.all(safe)):
                continue
            action, row = project_action(
                base_action=action,
                low_action=low,
                high_action=high,
                force_horizon_ticks=horizons,
                rollout=rollout,
                constants=constants,
            )
            row["fit"] = label
            row["fit_pass"] = fit_pass
            diagnostics.append(row)
            rollout_evaluations += int(row["rollout_evaluations"])
            projected.update(
                int(joint) for joint in row["projected_joint_indices"]
            )
            empty.update(
                int(joint)
                for joint in row["empty_intersection_joint_indices"]
            )
        if np.array_equal(action, prior):
            break

    primary_force, primary_rows = horizon_force(
        primary_rollout, action, horizons
    )
    shadow_force, shadow_rows = horizon_force(
        shadow_rollout, action, horizons
    )
    rollout_evaluations += 2
    primary_excess = np.maximum(
        np.abs(primary_force) - constants.torque_limit_nm, 0.0
    )
    shadow_excess = np.maximum(
        np.abs(shadow_force) - constants.torque_limit_nm, 0.0
    )
    unresolved = np.flatnonzero(
        np.maximum(primary_excess, shadow_excess)
        > constants.force_tolerance_nm
    ).astype(int)
    if unresolved.size:
        empty.update(int(joint) for joint in unresolved)
    robust_safe = unresolved.size == 0
    changed = np.flatnonzero(
        np.abs(action - supreme_base) > 1.0e-12
    ).astype(int)
    projected.update(int(joint) for joint in changed)
    base_clip = supreme_base - requested
    torque_clip = action - supreme_base
    return action.astype(np.float32), {
        "status": (
            "PASS_EXACT_TWO_FIT_TORQUE_ORACLE"
            if robust_safe
            else "NO_COMMON_EXACT_TWO_FIT_TORQUE_ACTION"
        ),
        "robust_safe": robust_safe,
        "converged": converged and robust_safe,
        "base_action": requested.tolist(),
        "supreme_feasible_base_action": supreme_base.tolist(),
        "base_supreme_clip_linf": float(np.max(np.abs(base_clip))),
        "base_supreme_clip_l2": float(np.linalg.norm(base_clip)),
        "base_supreme_clipped_joint_indices": np.flatnonzero(
            np.abs(base_clip) > 0.0
        )
        .astype(int)
        .tolist(),
        "final_action": action.tolist(),
        "low_action": low.tolist(),
        "high_action": high.tolist(),
        "force_horizon_ticks": horizons.astype(int).tolist(),
        "predicted_force_nm": primary_force.tolist(),
        "predicted_shadow_force_nm": shadow_force.tolist(),
        "primary_force_rows_nm": primary_rows.tolist(),
        "shadow_force_rows_nm": shadow_rows.tolist(),
        "primary_excess_nm": primary_excess.tolist(),
        "shadow_excess_nm": shadow_excess.tolist(),
        "projected_joint_indices": sorted(projected),
        "empty_intersection_joint_indices": sorted(empty),
        "unresolved_robust_joint_indices": unresolved.tolist(),
        "fit_diagnostics": diagnostics,
        "fit_passes": len(diagnostics),
        "rollout_evaluations": rollout_evaluations,
        "torque_projection_clip_linf": float(
            np.max(np.abs(torque_clip))
        ),
        "torque_projection_clip_l2": float(np.linalg.norm(torque_clip)),
        "clip_linf": float(np.max(np.abs(action - requested))),
        "clip_l2": float(np.linalg.norm(action - requested)),
    }
