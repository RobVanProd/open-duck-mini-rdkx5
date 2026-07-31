"""Read-only coordinate adapter for evaluating a normalized response head.

The reviewed Winner-v12 support gate expects the auxiliary head to emit raw
response coordinates before it computes normalized squared error. Winner-v22's
head emits normalized coordinates. This module projects only the three
training-only auxiliary-head leaves into raw coordinates in memory; recurrent
state, actions, the ONNX graph, saved checkpoint bytes, and physical support
evaluation remain unchanged.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np


AUXILIARY_KEYS = (
    "auxiliary_hidden_weight",
    "auxiliary_action_weight",
    "auxiliary_bias",
)
TARGET_DIMENSION = 50


def raw_coordinate_predictor_parameters(
    parameters: Mapping[str, Any], target_mean: Any, target_std: Any
) -> dict[str, Any]:
    """Return an in-memory raw-coordinate view of a normalized linear head."""

    if not all(name in parameters for name in AUXILIARY_KEYS):
        raise ValueError("Winner-v22 auxiliary predictor leaves are absent")
    mean_np = np.asarray(target_mean)
    std_np = np.asarray(target_std)
    if (
        mean_np.shape != (TARGET_DIMENSION,)
        or std_np.shape != (TARGET_DIMENSION,)
        or mean_np.dtype != np.dtype(np.float32)
        or std_np.dtype != np.dtype(np.float32)
        or not bool(np.all(np.isfinite(mean_np)))
        or not bool(np.all(np.isfinite(std_np)))
        or bool(np.any(std_np <= 0.0))
    ):
        raise ValueError("Winner-v22 normalized target statistics changed")
    hidden = np.asarray(parameters["auxiliary_hidden_weight"], dtype=np.float32)
    action = np.asarray(parameters["auxiliary_action_weight"], dtype=np.float32)
    bias = np.asarray(parameters["auxiliary_bias"], dtype=np.float32)
    if (
        hidden.ndim != 2
        or action.ndim != 2
        or hidden.shape[1] != TARGET_DIMENSION
        or action.shape[1] != TARGET_DIMENSION
        or bias.shape != (TARGET_DIMENSION,)
    ):
        raise ValueError("Winner-v22 auxiliary predictor shapes changed")
    mean = np.asarray(mean_np, dtype=np.float32)
    std = np.asarray(std_np, dtype=np.float32)
    adapted = dict(parameters)
    adapted["auxiliary_hidden_weight"] = hidden * std
    adapted["auxiliary_action_weight"] = action * std
    adapted["auxiliary_bias"] = bias * std + mean
    return adapted
