from __future__ import annotations

import numpy as np

from tools.run_t180_transform_route_attribution import (
    aggregate_banks,
    classify_route,
    cosine,
)


def _bank(joint: str, value: float) -> dict:
    joints = [
        "left_hip_yaw",
        "left_hip_roll",
        "left_hip_pitch",
        "left_knee",
        "left_ankle",
        "neck_pitch",
        "head_pitch",
        "head_yaw",
        "head_roll",
        "right_hip_yaw",
        "right_hip_roll",
        "right_hip_pitch",
        "right_knee",
        "right_ankle",
    ]
    vector = [value if name == joint else 0.0 for name in joints]
    return {
        "signed_mean_delta": vector,
        "per_joint_rms_delta": {
            name: abs(component) for name, component in zip(joints, vector)
        },
    }


def test_cosine_handles_parallel_and_zero_vectors() -> None:
    assert cosine([1.0, 0.0], [2.0, 0.0]) == 1.0
    assert cosine([0.0, 0.0], [2.0, 0.0]) == 0.0


def test_aggregate_localizes_dominant_joint() -> None:
    result = aggregate_banks(
        [_bank("left_knee", 0.2), _bank("left_knee", 0.1)]
    )
    assert result["dominant_joint"] == "left_knee"
    assert result["dominant_joint_rms"] == np.mean([0.2, 0.1])


def test_shared_direction_earns_only_interpolation_preregistration() -> None:
    helpful = aggregate_banks([_bank("left_knee", 0.2)])
    harmful = aggregate_banks([_bank("left_knee", -0.1)])
    classification, decision = classify_route(
        replay_max_error=1.0e-8,
        helpful=helpful,
        harmful=harmful,
        signed_cosine=-1.0,
        cosine_threshold=0.90,
    )
    assert classification == "SHARED_HEAD_DIRECTION_CONTEXT_AMPLITUDE_TRADEOFF"
    assert "INTERPOLATION_FEASIBILITY" in decision


def test_replay_failure_authorizes_nothing() -> None:
    helpful = aggregate_banks([_bank("left_knee", 0.2)])
    harmful = aggregate_banks([_bank("left_knee", -0.1)])
    classification, decision = classify_route(
        replay_max_error=2.0e-6,
        helpful=helpful,
        harmful=harmful,
        signed_cosine=-1.0,
        cosine_threshold=0.90,
    )
    assert classification == "INVALID_ONNX_TRACE_REPLAY"
    assert decision == "NO_SUCCESSOR_AUTHORIZED"
