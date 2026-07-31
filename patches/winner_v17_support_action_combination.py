"""Bounded diagnostic-only combinations of evidence-selected support directions."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np


ACTION_SIZE = 14
ACTION_SCALE_RAD = 0.25
TARGET_OFFSET_RAD = 0.03
NORMALIZED_OFFSET = TARGET_OFFSET_RAD / ACTION_SCALE_RAD
SELECTED_DIRECTIONS = {
    # These are the three signs that outlived both baseline and their opposite
    # in all 24 Winner-v16 checkpoint/plant/configuration comparisons.
    "HIP_MAG_NEG": {2: 1, 11: -1},
    "KNEE_POS": {3: 1, 12: 1},
    "ANKLE_POS": {4: 1, 13: 1},
}


def intervene(
    source_action: Any,
    previous_action: Any,
    maximum_delta: Any,
    axis: Sequence[str] | None,
    direction: int,
) -> np.ndarray:
    """Apply one nonempty subset of selected directions and reapply graph bounds."""

    source = np.asarray(source_action, dtype=np.float32)
    previous = np.asarray(previous_action, dtype=np.float32)
    delta = np.asarray(maximum_delta, dtype=np.float32)
    if source.shape != (ACTION_SIZE,) or previous.shape != (ACTION_SIZE,):
        raise ValueError("support combination requires two 14-vectors")
    if delta.shape != (ACTION_SIZE,) or np.any(delta <= 0.0):
        raise ValueError("support combination requires a positive 14-vector bound")
    if not all(np.all(np.isfinite(value)) for value in (source, previous, delta)):
        raise ValueError("support combination contains nonfinite values")
    if axis is None:
        if direction != 0:
            raise ValueError("baseline direction must be zero")
        candidate = source
    else:
        active = tuple(axis)
        if (
            direction != 1
            or not active
            or len(active) != len(set(active))
            or any(name not in SELECTED_DIRECTIONS for name in active)
        ):
            raise ValueError("unsupported sign-consistent support combination")
        candidate = source.copy()
        for name in active:
            for joint_index, sign in SELECTED_DIRECTIONS[name].items():
                candidate[joint_index] += np.float32(sign * NORMALIZED_OFFSET)
    absolute = np.clip(candidate, np.float32(-1.0), np.float32(1.0))
    lower = np.maximum(previous - delta, np.float32(-1.0))
    upper = np.minimum(previous + delta, np.float32(1.0))
    return np.maximum(np.minimum(absolute, upper), lower).astype(
        np.float32, copy=False
    )
