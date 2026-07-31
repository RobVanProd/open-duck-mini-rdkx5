"""Versioned scoring and graph-equivalent action transform for Winner-v14.

This module is diagnostic-only.  The action transform models an append-only
graph wrapper: scale the source graph's final action, then reapply the existing
absolute and per-tick bounds against the graph input ``previous_action``.
"""

from __future__ import annotations

from typing import Any

import numpy as np


ACTION_SIZE = 14
SCALES = (0.0, 0.25, 0.5, 0.75, 1.0)


def _float32_array(name: str, value: Any) -> np.ndarray:
    array = np.asarray(value, dtype=np.float32)
    if array.shape[-1:] != (ACTION_SIZE,):
        raise ValueError(f"{name} must end in {ACTION_SIZE} values: {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains nonfinite values")
    return array


def scale_and_rebound_action(
    source_action: Any,
    previous_action: Any,
    maximum_delta: Any,
    scale: float,
) -> np.ndarray:
    """Apply a fixed action scale and the inherited graph bounds in float32."""

    source = _float32_array("source_action", source_action)
    previous = _float32_array("previous_action", previous_action)
    delta = _float32_array("maximum_delta", maximum_delta)
    if source.shape != previous.shape:
        raise ValueError("source_action and previous_action shapes differ")
    if delta.ndim != 1 or np.any(delta <= 0.0):
        raise ValueError("maximum_delta must be a positive 14-vector")
    if not np.isfinite(scale) or not 0.0 <= scale <= 1.0:
        raise ValueError("scale must be finite and inside [0, 1]")
    candidate = source * np.float32(scale)
    lower = np.maximum(previous - delta, np.float32(-1.0))
    upper = np.minimum(previous + delta, np.float32(1.0))
    return np.maximum(np.minimum(candidate, upper), lower).astype(
        np.float32, copy=False
    )


def normalized_prediction_squared_error(
    prediction_normalized: Any,
    target_raw: Any,
    target_mean: Any,
    target_std: Any,
) -> np.ndarray:
    """Score a normalized-coordinate prediction against the normalized target."""

    prediction = np.asarray(prediction_normalized, dtype=np.float32)
    target = np.asarray(target_raw, dtype=np.float32)
    mean = np.asarray(target_mean, dtype=np.float32)
    std = np.asarray(target_std, dtype=np.float32)
    if not (prediction.shape == target.shape == mean.shape == std.shape):
        raise ValueError("normalized prediction scoring shapes differ")
    if prediction.shape[-1:] != (50,):
        raise ValueError("normalized prediction scoring requires 50 response fields")
    if not all(np.all(np.isfinite(value)) for value in (prediction, target, mean, std)):
        raise ValueError("normalized prediction scoring contains nonfinite values")
    if np.any(std <= 0.0):
        raise ValueError("target_std must be strictly positive")
    target_normalized = (target - mean) / std
    return np.square(prediction - target_normalized)


def constant_prediction_squared_error(
    target_raw: Any, target_mean: Any, target_std: Any
) -> np.ndarray:
    """Score the frozen constant-mean baseline in normalized coordinates."""

    target = np.asarray(target_raw, dtype=np.float32)
    mean = np.asarray(target_mean, dtype=np.float32)
    std = np.asarray(target_std, dtype=np.float32)
    if not (target.shape == mean.shape == std.shape):
        raise ValueError("constant prediction scoring shapes differ")
    if target.shape[-1:] != (50,):
        raise ValueError("constant prediction scoring requires 50 response fields")
    if not all(np.all(np.isfinite(value)) for value in (target, mean, std)):
        raise ValueError("constant prediction scoring contains nonfinite values")
    if np.any(std <= 0.0):
        raise ValueError("target_std must be strictly positive")
    return np.square((target - mean) / std)
