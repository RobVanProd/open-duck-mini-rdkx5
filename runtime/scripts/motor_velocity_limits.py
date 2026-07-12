"""Default-off target slew-limit contract shared by runtime launchers."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def parse_motor_velocity_limits(
    value: str | Sequence[float] | None,
    *,
    joint_count: int = 14,
) -> list[float] | None:
    if value is None:
        return None
    if isinstance(value, str):
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    else:
        values = [float(item) for item in value]
    array = np.asarray(values, dtype=float)
    if array.shape != (joint_count,) or not np.all(np.isfinite(array)) or np.any(array <= 0):
        raise ValueError(f"motor velocity limits require {joint_count} finite positive values")
    return array.tolist()

