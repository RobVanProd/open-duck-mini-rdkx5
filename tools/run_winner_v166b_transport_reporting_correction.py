#!/usr/bin/env python3
"""Launch unchanged V166 with the explicit nominal transport mapping."""

from __future__ import annotations

from typing import Any

from tools import run_winner_v166_continuous_reference as original


_run_cell = original.run_cell


def run_cell_with_transport(**kwargs: Any) -> dict[str, Any]:
    row = dict(kwargs["row"])
    row["transport"] = {
        "additional_action_delay_ticks": 0,
        "imu_delay_ticks": 0,
        "native_quantization": False,
        "sensor_noise_scales": None,
    }
    kwargs["row"] = row
    return _run_cell(**kwargs)


original.run_cell = run_cell_with_transport


if __name__ == "__main__":
    raise SystemExit(original.main())
