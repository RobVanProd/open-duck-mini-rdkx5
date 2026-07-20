import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "build_winner_v4_response_interface_preregistration.py"
SPEC = importlib.util.spec_from_file_location("response_interface_prereg", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_response_context_order_is_complete_and_stable() -> None:
    fields = MODULE.feature_order()
    assert len(fields) == 73
    assert len(set(fields)) == 73
    assert fields[:5] == [
        "joint_response.left_hip_yaw.delay_ticks",
        "joint_response.left_hip_yaw.gain_ratio",
        "joint_response.left_hip_yaw.time_constant_s",
        "joint_response.left_hip_yaw.tracking_p95_rad",
        "joint_response.left_hip_yaw.current_p95_a",
    ]
    assert fields[-3:] == [
        "body_response.pitch_rate_p95_rad_s",
        "body_response.roll_rate_p95_rad_s",
        "body_response.acceleration_norm_p95_m_s2",
    ]


def test_abi_keeps_observation_and_action_semantics_separate() -> None:
    prereg = MODULE.build_preregistration()
    abi = prereg["policy_abi"]
    assert abi["canonical_observation_unchanged"] is True
    assert abi["action_semantics_unchanged"] is True
    assert abi["response_context_is_separate_input"] is True
    assert abi["inputs"][-1] == {
        "name": "response_context",
        "dtype": "float32",
        "shape": [1, 73],
    }


def test_preregistration_does_not_authorize_training_or_hardware() -> None:
    authority = MODULE.build_preregistration()["authority"]
    assert authority["runtime_review_only"] is True
    assert authority["training"] is False
    assert authority["hosted_compute"] is False
    assert authority["rdkx5_or_robot"] is False
    assert authority["torque_or_motion"] is False
