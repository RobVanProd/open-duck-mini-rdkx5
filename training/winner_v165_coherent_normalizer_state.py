"""Coherent running-statistics state for accepted constrained PPO steps."""

from __future__ import annotations

import copy
from typing import Any

import jax
import numpy as np

from training.winner_v164_feasibility_preserving_state import (
    interpolate_float_tree,
)


def uint64_dict_to_int(value: dict[str, Any]) -> int:
    """Converts Brax's restored UInt64 mapping to a Python integer."""
    return int(np.asarray(value["hi"])) * (2**32) + int(
        np.asarray(value["lo"])
    )


def int_to_uint64_dict(value: int) -> dict[str, np.ndarray]:
    """Builds the restored-checkpoint representation of Brax UInt64."""
    if value < 0 or value >= 2**64:
        raise ValueError("count is outside uint64")
    return {
        "hi": np.asarray(value >> 32, dtype=np.uint32),
        "lo": np.asarray(value & 0xFFFFFFFF, dtype=np.uint32),
    }


def compose_coherent_normalizer(
    source: dict[str, Any],
    proposal: dict[str, Any],
    alpha: float,
) -> dict[str, Any]:
    """Interpolates deployed mean/std and reconstructs valid Welford state."""
    required = {"count", "mean", "std", "std_eps", "summed_variance"}
    if set(source) != required or set(proposal) != required:
        raise ValueError("unexpected running-statistics checkpoint fields")
    source_count = uint64_dict_to_int(source["count"])
    proposal_count = uint64_dict_to_int(proposal["count"])
    if proposal_count <= source_count:
        raise ValueError("proposal normalizer count did not advance")
    count_delta = proposal_count - source_count
    accepted_increment = max(1, int(np.rint(float(alpha) * count_delta)))
    accepted_count = source_count + accepted_increment
    mean = interpolate_float_tree(
        source["mean"], proposal["mean"], float(alpha)
    )
    std = interpolate_float_tree(source["std"], proposal["std"], float(alpha))
    source_eps = float(np.asarray(source["std_eps"]))
    proposal_eps = float(np.asarray(proposal["std_eps"]))
    if source_eps != proposal_eps:
        raise ValueError("normalizer std_eps changed")

    def reconstruct(value: Any) -> np.ndarray:
        array = np.asarray(value)
        variance = np.maximum(
            array.astype(np.float64) ** 2 - source_eps, 0.0
        )
        return (variance * float(accepted_count)).astype(array.dtype)

    summed_variance = jax.tree_util.tree_map(reconstruct, std)
    return {
        "count": int_to_uint64_dict(accepted_count),
        "mean": mean,
        "std": std,
        "std_eps": copy.deepcopy(source["std_eps"]),
        "summed_variance": summed_variance,
    }


def compose_coherent_checkpoint(
    source: list[Any], proposal: list[Any], alpha: float
) -> list[Any]:
    """Composes accepted normalizer/actor and retains proposal reward critic."""
    if len(source) != 3 or len(proposal) != 3:
        raise ValueError("expected normalizer/policy/reward-value checkpoints")
    return [
        compose_coherent_normalizer(source[0], proposal[0], float(alpha)),
        interpolate_float_tree(source[1], proposal[1], float(alpha)),
        copy.deepcopy(proposal[2]),
    ]


def normalizer_consistency_error(normalizer: dict[str, Any]) -> float:
    """Checks that stored std is reproduced by variance/count algebra."""
    count = float(uint64_dict_to_int(normalizer["count"]))
    eps = float(np.asarray(normalizer["std_eps"]))
    errors = []
    for summed, std in zip(
        jax.tree_util.tree_leaves(normalizer["summed_variance"]),
        jax.tree_util.tree_leaves(normalizer["std"]),
        strict=True,
    ):
        expected = np.sqrt(
            np.maximum(np.asarray(summed, dtype=np.float64), 0.0) / count
            + eps
        )
        errors.append(
            float(np.max(np.abs(expected - np.asarray(std, dtype=np.float64))))
        )
    return max(errors, default=0.0)
