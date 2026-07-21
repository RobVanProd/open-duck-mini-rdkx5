from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "outputs/analysis/winner_v11_dynamic_calibration_interface_preregistration.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_winner_v11_is_a_review_only_request_on_the_distinct_winner_v10_base() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PREREGISTERED_PENDING_RUNTIME_REVIEW"
    assert artifact["decision"] == "REQUEST_READ_ONLY_WINNER_V11_RUNTIME_SCHEMA_REVIEW"
    assert artifact["not_a_v6_or_v6b_retry"] == {
        "behavior_revalidation": {
            "nominal_pass": True,
            "r2_condition_7_terminal_hold_preserved": True,
            "r2_conditions_1_through_6_pass": True,
        },
        "closed_result_preserved": True,
        "closed_result_sha256": artifact["sources"]["closed_v6b_result"]["sha256"],
        "new_protected_base": "Winner-v10 inward-torque representation",
        "new_protected_policy_hashes": artifact["policy_hashes"],
        "r2_resumption": False,
    }
    assert artifact["policy_hashes"] == {
        "half": "cf001269908d86e47eaa145ffda1d87e946a314ecf51056dc086c4cf10164ab6",
        "final": "d52b63241340d9d56671b95c58bb0fc72af0998fd47d4684719f6cd44f244a10",
    }
    assert artifact["authority"] == {
        "hosted_compute_gpu_or_igpu": False,
        "rdkx5_robot_serial_gpio_i2c": False,
        "robot_clearance": False,
        "runtime_implementation": False,
        "runtime_review_only": True,
        "torque_motion_gate5_deployment": False,
        "training_or_optimizer": False,
        "zero_ppo_execution": False,
    }


def test_winner_v11_preserves_the_reviewed_two_graph_abi() -> None:
    interface = load(ARTIFACT)["requested_interface"]
    assert interface["observation_contract"] == "winner-v2-115d"
    assert interface["runtime_v1_101x14_changed"] is False
    assert interface["runtime_v2_115d_semantics_changed"] is False
    assert interface["host_action_projection_or_limiter_added"] is False
    assert interface["calibration_ticks"] == 250
    assert [(row["name"], row["shape"]) for row in interface["calibrator"]["inputs"]] == [
        ("obs", [1, 115]),
        ("previous_action", [1, 14]),
        ("h_in", [1, 64]),
    ]
    assert [(row["name"], row["shape"]) for row in interface["locomotion"]["inputs"]] == [
        ("obs", [1, 115]),
        ("previous_action", [1, 14]),
        ("h_in", [1, 64]),
        ("calibration_context", [1, 64]),
    ]


def test_winner_v11_sources_and_terminal_hold_are_hash_bound() -> None:
    artifact = load(ARTIFACT)
    for source in artifact["sources"].values():
        path = ROOT / source["path"]
        assert path.is_file()
        assert sha256(path) == source["sha256"]
    condition7 = load(
        ROOT / artifact["sources"]["winner_v10_r2_condition7_hold"]["path"]
    )
    assert condition7["status"] == "HOLD_WINNER_V10_R2_CONDITION7_TORSO_COM_X_NEG"
    assert condition7["decision"] == "STOP_WINNER_V10_R2_AT_FIRST_FAILED_CONDITION"
    assert condition7["authority"]["later_condition_execution"] is False


def test_winner_v11_requires_no_manual_per_build_measurement() -> None:
    automatic = load(ARTIFACT)["automatic_configuration"]
    assert automatic["manual_measurements_required"] is False
    assert automatic["mass_com_inertia_dimensions_or_component_identity_inputs"] is False
    assert automatic["context_recomputed_each_process_start"] is True
    assert automatic["context_persisted_between_boots"] is False
