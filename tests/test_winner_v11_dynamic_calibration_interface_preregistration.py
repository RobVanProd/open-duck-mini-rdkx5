from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "outputs/analysis/winner_v11_dynamic_calibration_interface_preregistration.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_winner_v11_is_a_review_only_request_on_the_distinct_winner_v10_base() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PREREGISTERED_PENDING_RUNTIME_REVIEW"
    assert artifact["decision"] == (
        "REQUEST_READ_ONLY_WINNER_V11_RUNTIME_SCHEMA_REREVIEW_AFTER_LF_CORRECTION"
    )
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
    tensor = lambda name, shape: {"name": name, "dtype": "float32", "shape": shape}
    assert interface["calibrator"] == {
        "inputs": [
            tensor("obs", [1, 115]),
            tensor("previous_action", [1, 14]),
            tensor("h_in", [1, 64]),
        ],
        "outputs": [
            tensor("calibration_actions", [1, 14]),
            tensor("previous_action_out", [1, 14]),
            tensor("h_out", [1, 64]),
        ],
    }
    assert interface["locomotion"] == {
        "inputs": [
            tensor("obs", [1, 115]),
            tensor("previous_action", [1, 14]),
            tensor("h_in", [1, 64]),
            tensor("calibration_context", [1, 64]),
        ],
        "outputs": [
            tensor("continuous_actions", [1, 14]),
            tensor("previous_action_out", [1, 14]),
            tensor("h_out", [1, 64]),
        ],
    }
    sequence = interface["sequence_inherited_from_reviewed_winner_v6"]
    assert sequence["frequency_hz"] == 50
    assert sequence["calibrator_initial_previous_action"] == "exact float32 zeros[1,14]"
    assert sequence["calibrator_initial_hidden_state"] == "exact float32 zeros[1,64]"
    assert sequence["calibration_command"] == "exact float32 zeros[7]"
    assert sequence["calibration_phase"] == [1.0, 0.0]
    assert sequence["calibration_phase_advances"] is False
    assert sequence["context_bounds_inclusive"] == [-1.0, 1.0]
    assert sequence["runtime_remains_paused_after_handoff"] is True


def test_winner_v11_sources_and_terminal_hold_are_hash_bound() -> None:
    artifact = load(ARTIFACT)
    for source in artifact["sources"].values():
        path = ROOT / source["path"]
        assert path.is_file()
        assert source["hash_mode"] == "sha256 after CRLF-to-LF normalization"
        assert lf_sha256(path) == source["sha256"]
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


def test_winner_v11_correction_is_metadata_only_and_pre_execution() -> None:
    artifact = load(ARTIFACT)
    correction = artifact["pre_execution_hash_correction"]
    assert correction == {
        "correction_scope": "metadata and LF-stable receipt hashes only",
        "graph_abi_gate_or_authority_changed": False,
        "runtime_hold_artifact_sha256": "a5496d7f23195975f83c2536cd0b5a962a074eaf9afdf7b4455b33f496c7c080",
        "runtime_hold_commit": "9d9410f9ff892e467551e75332dd17bcdcd9f819",
        "runtime_hold_status": "SCHEMA_FEASIBLE_HOLD_WINNER_V11_ZERO_PPO_HASH_BINDING",
        "superseded_claimed_crlf_sha256": "045342b676d96557d451c6a85383f1381c3e3b2489cad3c2b943d85e0778adc6",
        "superseded_committed_lf_sha256": "738cdfe131b5ba70eebbac3333c1b04016c7abdcb8a370c4c682bc3bc9a65424",
        "superseded_policy_commit": "ed3385dbaf30a8cd1580baf452ff0d8406a1121b",
        "zero_ppo_run_started": False,
    }
    assert artifact["authority"]["zero_ppo_execution"] is False


def test_winner_v11_x0_is_graph_authoritative_only_when_enabled() -> None:
    semantics = load(ARTIFACT)["requested_interface"]["x0_semantics"]
    assert semantics["default_off"] == "byte-exact Winner-v10 zero-action deadband"
    assert semantics["future_enabled"] == "graph-authoritative and may be nonzero"
    assert semantics["host_forces_zero"] is False
    assert semantics["future_enabled_requires_separate_behavior_gate"] is True


def test_winner_v11_artifacts_are_lf_stable() -> None:
    markdown = ROOT / "outputs/analysis/WINNER_V11_DYNAMIC_CALIBRATION_INTERFACE_PREREGISTRATION_20260720.md"
    assert lf_sha256(ARTIFACT) in markdown.read_text(encoding="utf-8")
