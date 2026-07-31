"""Frozen 1x/2x/3x magnitude variants of Winner-v18 IMU ankle feedback."""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    import winner_v18_imu_ankle_feedback as base
except ModuleNotFoundError:  # Package import in repository unit tests.
    from patches import winner_v18_imu_ankle_feedback as base


MODE_SPEC = {
    "BASELINE": ("BASELINE", 0.0),
    "CONSTANT_003": ("CONSTANT_ANKLE_POS", 0.03),
    "CONSTANT_006": ("CONSTANT_ANKLE_POS", 0.06),
    "CONSTANT_009": ("CONSTANT_ANKLE_POS", 0.09),
    "TILT_RATE_003": ("TILT_RATE_BACKWARD", 0.03),
    "TILT_RATE_006": ("TILT_RATE_BACKWARD", 0.06),
    "TILT_RATE_009": ("TILT_RATE_BACKWARD", 0.09),
}


def intervene(
    source_action: Any,
    previous_action: Any,
    maximum_delta: Any,
    observation: Any,
    mode: str,
) -> tuple[np.ndarray, np.float32, np.float32, np.float32]:
    """Apply one frozen feedback ceiling and exact graph bounds."""

    if mode not in MODE_SPEC:
        raise ValueError("unsupported feedback-magnitude mode")
    source = np.asarray(source_action, dtype=np.float32)
    previous = np.asarray(previous_action, dtype=np.float32)
    delta = np.asarray(maximum_delta, dtype=np.float32)
    if source.shape != (base.ACTION_SIZE,) or previous.shape != (base.ACTION_SIZE,):
        raise ValueError("feedback magnitude requires two 14-vectors")
    if delta.shape != (base.ACTION_SIZE,) or np.any(delta <= 0.0):
        raise ValueError("feedback magnitude requires positive 14-vector bounds")
    if not all(np.all(np.isfinite(value)) for value in (source, previous, delta)):
        raise ValueError("feedback magnitude contains nonfinite action values")
    feedback_mode, maximum_target_offset = MODE_SPEC[mode]
    amount, pitch_proxy, pitch_rate = base.activation(observation, feedback_mode)
    candidate = source.copy()
    normalized_ceiling = np.float32(maximum_target_offset / base.ACTION_SCALE_RAD)
    offset = normalized_ceiling * amount
    for index in base.ANKLE_INDICES:
        candidate[index] += offset
    absolute = np.clip(candidate, np.float32(-1.0), np.float32(1.0))
    lower = np.maximum(previous - delta, np.float32(-1.0))
    upper = np.minimum(previous + delta, np.float32(1.0))
    realized = np.maximum(np.minimum(absolute, upper), lower).astype(
        np.float32, copy=False
    )
    return realized, amount, pitch_proxy, pitch_rate
