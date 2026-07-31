"""State composition for feasibility-preserving constrained PPO blocks."""

from __future__ import annotations

import copy
from typing import Any

import jax
import numpy as np


def interpolate_float_tree(source: Any, proposal: Any, alpha: float) -> Any:
    """Interpolates matching floating leaves and rejects ambiguous state."""
    if not 0.0 < float(alpha) <= 1.0:
        raise ValueError("alpha must be in (0, 1]")
    if jax.tree_util.tree_structure(source) != jax.tree_util.tree_structure(
        proposal
    ):
        raise ValueError("source/proposal tree structures differ")

    def interpolate(left: Any, right: Any) -> np.ndarray:
        left_array = np.asarray(left)
        right_array = np.asarray(right)
        if left_array.shape != right_array.shape:
            raise ValueError("source/proposal leaf shapes differ")
        if left_array.dtype != right_array.dtype:
            raise ValueError("source/proposal leaf dtypes differ")
        if not np.issubdtype(left_array.dtype, np.floating):
            if not np.array_equal(left_array, right_array):
                raise ValueError("changed nonfloating leaf cannot be blended")
            return np.array(left_array, copy=True)
        value = left_array.astype(np.float64) + float(alpha) * (
            right_array.astype(np.float64) - left_array.astype(np.float64)
        )
        return value.astype(left_array.dtype)

    return jax.tree_util.tree_map(interpolate, source, proposal)


def compose_accepted_checkpoint(
    source: list[Any], proposal: list[Any], alpha: float
) -> list[Any]:
    """Builds the deployable/reward checkpoint after exact backtracking.

    The mature source normalizer is frozen.  Only actor parameters are
    backtracked.  The proposal reward critic is retained because it is
    training-only and estimates the proposal rollouts that generated the
    accepted direction.
    """
    if len(source) != 3 or len(proposal) != 3:
        raise ValueError("expected normalizer/policy/reward-value checkpoints")
    accepted_policy = interpolate_float_tree(
        source[1], proposal[1], float(alpha)
    )
    return [
        copy.deepcopy(source[0]),
        accepted_policy,
        copy.deepcopy(proposal[2]),
    ]


def finite_tree(tree: Any) -> bool:
    """Returns true only when every numeric leaf is finite."""
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(tree)
    )
