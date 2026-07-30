from __future__ import annotations

import numpy as np
import pytest

from tools.run_t178_positive_z_failure_autopsy import (
    failure_onset,
    failure_signature,
    midpoint_residual_summary,
    replication_summary,
)


def _trace(samples: int = 200) -> dict:
    zeros14 = np.zeros((samples, 14), dtype=np.float64)
    return {
        "checkpoint_id": "half",
        "fit_id": "p30",
        "command_x_m_s": 0.077,
        "samples": samples,
        "action": zeros14.copy(),
        "applied": zeros14.copy(),
        "actual": zeros14.copy(),
        "force": zeros14.copy(),
        "tracking": zeros14.copy(),
        "pitch": np.zeros(samples),
        "roll": np.zeros(samples),
        "height": np.full(samples, 0.16),
        "contacts": [(1, 0)] * samples,
        "done": np.zeros(samples, dtype=bool),
    }


def test_midpoint_summary_localizes_exact_joint_and_phase() -> None:
    low = np.zeros((162, 14))
    high = np.full((162, 14), 2.0)
    middle = np.ones((162, 14))
    middle[31, 3] += 0.4
    result = midpoint_residual_summary(
        low,
        middle,
        high,
        prefix_ticks=162,
        gait_period_ticks=27,
    )
    assert result["l_inf"] == pytest.approx(0.4)
    assert result["maximum"]["tick"] == 31
    assert result["maximum"]["phase"] == 4
    assert result["maximum"]["joint"] == "left_knee"


def test_failure_onset_uses_first_frozen_threshold() -> None:
    trace = _trace()
    trace["roll"][61] = -0.3
    trace["height"][80] = 0.1
    tick, reasons = failure_onset(
        trace,
        angle_threshold_rad=0.25,
        height_threshold_m=0.12,
    )
    assert tick == 61
    assert reasons == ["roll"]


def test_signature_compares_fixed_prefall_window_to_x008() -> None:
    failed = _trace()
    passed = _trace()
    failed["roll"][100] = -0.3
    failed["action"][47:101, 3] = 0.2
    result = failure_signature(
        failed,
        passed,
        angle_threshold_rad=0.25,
        height_threshold_m=0.12,
        gait_period_ticks=27,
        phase_bucket_ticks=3,
        prefall_ticks=54,
    )
    assert result["onset_tick"] == 100
    assert result["prefall_window"] == {
        "start_tick": 47,
        "stop_tick_exclusive": 101,
    }
    assert (
        result["matched_x008_deltas"]["action"]["largest_joint"]
        == "left_knee"
    )


def test_replication_rule_requires_tilt_and_one_localizer() -> None:
    signatures = []
    for index in range(5):
        signatures.append(
            {
                "dominant_tilt": "roll_negative" if index < 4 else "pitch_positive",
                "onset_phase_bucket": 2 if index < 4 else 6,
                "contact_pattern": "10",
                "matched_x008_deltas": {
                    "action": {
                        "largest_joint": (
                            "left_knee" if index < 3 else "right_knee"
                        )
                    }
                },
            }
        )
    result = replication_summary(signatures, minimum_replicates=4)
    assert result["dominant_tilt"]["replicated"]
    assert result["onset_phase_bucket"]["replicated"]
    assert result["localized_shared_signature"]
