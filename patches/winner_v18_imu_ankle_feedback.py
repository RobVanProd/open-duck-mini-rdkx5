"""One-sided deployable IMU-proxy ankle feedback for a CPU-only diagnostic."""

from __future__ import annotations

from typing import Any

import numpy as np


ACTION_SIZE = 14
OBS_SIZE = 115
GYRO_PITCH_RATE_INDEX = 1
ACCELEROMETER_SLICE = slice(3, 6)
ANKLE_INDICES = (4, 13)
ACTION_SCALE_RAD = 0.25
MAXIMUM_TARGET_OFFSET_RAD = 0.03
MAXIMUM_NORMALIZED_OFFSET = MAXIMUM_TARGET_OFFSET_RAD / ACTION_SCALE_RAD
TILT_BOUNDARY_RAD = 0.35
RATE_REFERENCE_RAD_S = 1.75
MODES = {
    "BASELINE",
    "CONSTANT_ANKLE_POS",
    "TILT_BACKWARD",
    "TILT_OPPOSITE",
    "RATE_BACKWARD",
    "RATE_OPPOSITE",
    "TILT_RATE_BACKWARD",
}


def feedback_signals(observation: Any) -> tuple[np.float32, np.float32]:
    """Return deployable accelerometer pitch proxy and gyro-y pitch rate."""

    obs = np.asarray(observation, dtype=np.float32)
    if obs.shape != (OBS_SIZE,) or not np.all(np.isfinite(obs)):
        raise ValueError("IMU ankle feedback requires one finite 115-vector")
    accel = obs[ACCELEROMETER_SLICE]
    lateral_vertical = np.hypot(accel[1], accel[2])
    pitch_proxy = np.arctan2(-accel[0], lateral_vertical).astype(np.float32)
    pitch_rate = np.float32(obs[GYRO_PITCH_RATE_INDEX])
    return pitch_proxy, pitch_rate


def activation(observation: Any, mode: str) -> tuple[np.float32, np.float32, np.float32]:
    """Calculate a one-sided normalized activation in [0, 1]."""

    if mode not in MODES:
        raise ValueError("unsupported IMU ankle-feedback mode")
    pitch_proxy, pitch_rate = feedback_signals(observation)
    backward_tilt = np.clip(
        -pitch_proxy / np.float32(TILT_BOUNDARY_RAD),
        np.float32(0.0),
        np.float32(1.0),
    )
    opposite_tilt = np.clip(
        pitch_proxy / np.float32(TILT_BOUNDARY_RAD),
        np.float32(0.0),
        np.float32(1.0),
    )
    backward_rate = np.clip(
        -pitch_rate / np.float32(RATE_REFERENCE_RAD_S),
        np.float32(0.0),
        np.float32(1.0),
    )
    opposite_rate = np.clip(
        pitch_rate / np.float32(RATE_REFERENCE_RAD_S),
        np.float32(0.0),
        np.float32(1.0),
    )
    values = {
        "BASELINE": np.float32(0.0),
        "CONSTANT_ANKLE_POS": np.float32(1.0),
        "TILT_BACKWARD": backward_tilt,
        "TILT_OPPOSITE": opposite_tilt,
        "RATE_BACKWARD": backward_rate,
        "RATE_OPPOSITE": opposite_rate,
        "TILT_RATE_BACKWARD": np.maximum(backward_tilt, backward_rate),
    }
    return np.float32(values[mode]), pitch_proxy, pitch_rate


def intervene(
    source_action: Any,
    previous_action: Any,
    maximum_delta: Any,
    observation: Any,
    mode: str,
) -> tuple[np.ndarray, np.float32, np.float32, np.float32]:
    """Apply bounded positive-ankle feedback and reapply exact graph bounds."""

    source = np.asarray(source_action, dtype=np.float32)
    previous = np.asarray(previous_action, dtype=np.float32)
    delta = np.asarray(maximum_delta, dtype=np.float32)
    if source.shape != (ACTION_SIZE,) or previous.shape != (ACTION_SIZE,):
        raise ValueError("IMU ankle feedback requires two 14-vectors")
    if delta.shape != (ACTION_SIZE,) or np.any(delta <= 0.0):
        raise ValueError("IMU ankle feedback requires positive 14-vector bounds")
    if not all(np.all(np.isfinite(value)) for value in (source, previous, delta)):
        raise ValueError("IMU ankle feedback contains nonfinite action values")
    amount, pitch_proxy, pitch_rate = activation(observation, mode)
    candidate = source.copy()
    offset = np.float32(MAXIMUM_NORMALIZED_OFFSET) * amount
    for index in ANKLE_INDICES:
        candidate[index] += offset
    absolute = np.clip(candidate, np.float32(-1.0), np.float32(1.0))
    lower = np.maximum(previous - delta, np.float32(-1.0))
    upper = np.minimum(previous + delta, np.float32(1.0))
    realized = np.maximum(np.minimum(absolute, upper), lower).astype(
        np.float32, copy=False
    )
    return realized, amount, pitch_proxy, pitch_rate
