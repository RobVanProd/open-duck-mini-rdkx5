from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v88_flat_transport_representation_result.json"


def test_result_selects_no_tested_linear_representation() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V88_FLAT_TRANSPORT_REPRESENTATION_DIAGNOSTIC"
    assert value["classification"] == "NO_LINEAR_OBSERVABLE_REPRESENTATION_SELECTED"
    assert value["decision"] == "REJECT_TESTED_LINEAR_REPRESENTATION_FAMILIES"
    assert value["selected_source_checkpoint_for_mechanism_proof"] is None
    assert value["selected_feature_family_for_mechanism_proof"] is None
    assert value["failed_checks"] == []
    assert all(value["checks"].values())


def test_flat_transport_improves_half_but_fails_transfer_rule() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    half, final = value["endpoints"]
    assert half["label"] == "half"
    assert final["label"] == "final"
    half_current = half["families"]["current_observation"]
    half_flat = half["families"]["flat_transport_basis"]
    final_current = final["families"]["current_observation"]
    final_flat = final["families"]["flat_transport_basis"]
    assert half["flat_transport_incremental_over_current_observation"] is True
    assert final["flat_transport_incremental_over_current_observation"] is False
    assert (
        half_flat["leave_one_configuration_out"]["aggregate_bounded_pitch_error"][
            "mse"
        ]
        < half_current["leave_one_configuration_out"][
            "aggregate_bounded_pitch_error"
        ]["mse"]
    )
    assert (
        final_flat["leave_one_configuration_out"]["aggregate_bounded_pitch_error"][
            "mse"
        ]
        > final_current["leave_one_configuration_out"][
            "aggregate_bounded_pitch_error"
        ]["mse"]
    )
    for endpoint in value["endpoints"]:
        assert endpoint["selected_family"] is None
        assert all(not family["viable"] for family in endpoint["families"].values())


def test_result_is_zero_update_zero_artifact_zero_hardware() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "formal_support_cells": 0,
        "least_squares_fits": 78,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
        "stage2_rollout_episodes": 160,
    }
    assert value["authority"]["equation_policy_mechanism_authorized_now"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["deployment_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
