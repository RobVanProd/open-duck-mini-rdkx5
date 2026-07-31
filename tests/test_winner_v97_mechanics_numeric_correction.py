from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v97_mechanics_numeric_correction_preregistration.json"
)
RESULT = ROOT / "outputs/analysis/winner_v97_mechanics_numeric_correction_result.json"


def test_preregistration_changes_only_three_attributed_assertions() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V97_MECHANICS_NUMERIC_CORRECTION"
    assert value["source_hold"]["v96_result_sha256"] == (
        "5abba51f4ce65b672c6190e76a1dc79cdba02990fc0eadca4277dc2e74377a01"
    )
    assert set(value["corrections"]) == {
        "golden_same_input",
        "numeric_tolerance",
        "rate_boundary",
        "universal_target",
    }
    assert value["corrections"]["numeric_tolerance"] == 1.0e-6
    unchanged = value["unchanged"]
    assert unchanged["network_source"] is True
    assert unchanged["policy_and_calibrator_sources"] is True
    assert unchanged["adapter_seed_and_weights"] is True
    assert unchanged["thresholds_other_than_three_attributed_assertions"] is True
    assert unchanged["flat_transport_feature_enabled"] is False
    assert unchanged["optimizer_updates"] == 0


def test_preregistration_binds_all_four_v96_graph_hashes() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["unchanged"]["graph_artifact_sha256"] == {
        "winner_v96_locomotion_default_off.onnx": "a86fcb8e091b8e743772773fa2d3384856d0c6df215082ba73b04737c5441555",
        "winner_v96_locomotion_enabled_zero.onnx": "9a62b32c5cbf0f11801abe6f7dca4acf8ef31c825ed363e358ed075be5f94d6a",
        "winner_v96_locomotion_stress.onnx": "3db85000db7c53227f747befc8b320d95a1190a66c23878a2124ae363b389780",
        "winner_v96_universal_calibrator.onnx": "0f3aebfd9946a6271fdb14adec3d68d556648f270984639d372c973a7d7dc576",
    }
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["deployment_authorized"] is False
    assert value["authority"]["robot_clearance"] is False


def test_result_passes_corrected_and_unaffected_contract() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V97_MECHANICS_NUMERIC_CORRECTION"
    assert value["decision"] == "PREREGISTER_RESPONSE_CONDITIONED_LOCOMOTION_TRAINING"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["signed_target_correction"]["v92_exact_receipts"]
    assert value["signed_target_correction"]["v92_bounded_target_action_error"] == 0.0
    assert value["handoff_fail_closed"]["all_invalid_cases_rejected"]


def test_result_uses_frozen_numeric_tolerance_without_graph_change() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    same_input = value["same_input_numeric_correction"]
    assert same_input["all_at_most_frozen_1e_minus_6"]
    assert same_input["maximum_abs"] <= 1.0e-6
    stress = value["stress_boundary_numeric_correction"]
    assert stress["numeric_tolerance"] == 1.0e-6
    assert stress["absolute_and_rate_excess_at_most_1e_minus_6"]
    assert stress["maximum_rate_excess"] <= 1.0e-6
    assert value["artifact_sha256"] == json.loads(
        PREREGISTRATION.read_text(encoding="utf-8")
    )["unchanged"]["graph_artifact_sha256"]
    assert value["execution"] == {
        "golden_ticks": 1200,
        "onnx_exports": 4,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "simulator_cells": 4,
        "stress_cases": 256,
    }
