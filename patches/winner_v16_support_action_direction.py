"""Bounded diagnostic-only pitch-chain action interventions for Winner-v16."""

from __future__ import annotations

from typing import Any

import numpy as np


ACTION_SIZE = 14
ACTION_SCALE_RAD = 0.25
TARGET_OFFSET_RAD = 0.03
NORMALIZED_OFFSET = TARGET_OFFSET_RAD / ACTION_SCALE_RAD
BILATERAL_AXES = {
    # Hip-pitch home coordinates have opposite signs, so magnitude symmetry is
    # left-negative/right-positive.  Knee and ankle home coordinates share sign.
    "hip_pitch_magnitude": {2: -1, 11: 1},
    "knee": {3: 1, 12: 1},
    "ankle": {4: 1, 13: 1},
}


def intervene(
    source_action: Any,
    previous_action: Any,
    maximum_delta: Any,
    axis: str | None,
    direction: int,
) -> np.ndarray:
    """Add one frozen joint offset and reapply exact graph action bounds."""

    source = np.asarray(source_action, dtype=np.float32)
    previous = np.asarray(previous_action, dtype=np.float32)
    delta = np.asarray(maximum_delta, dtype=np.float32)
    if source.shape != (ACTION_SIZE,) or previous.shape != (ACTION_SIZE,):
        raise ValueError("action intervention requires two 14-vectors")
    if delta.shape != (ACTION_SIZE,) or np.any(delta <= 0.0):
        raise ValueError("action intervention requires a positive 14-vector bound")
    if not all(np.all(np.isfinite(value)) for value in (source, previous, delta)):
        raise ValueError("action intervention contains nonfinite values")
    if axis is None:
        if direction != 0:
            raise ValueError("baseline intervention direction must be zero")
        candidate = source
    else:
        if axis not in BILATERAL_AXES or direction not in (-1, 1):
            raise ValueError("unsupported bilateral pitch-chain intervention")
        candidate = source.copy()
        for joint_index, parity in BILATERAL_AXES[axis].items():
            candidate[joint_index] += np.float32(
                direction * parity * NORMALIZED_OFFSET
            )
    absolute = np.clip(candidate, np.float32(-1.0), np.float32(1.0))
    lower = np.maximum(previous - delta, np.float32(-1.0))
    upper = np.minimum(previous + delta, np.float32(1.0))
    return np.maximum(np.minimum(absolute, upper), lower).astype(np.float32, copy=False)
