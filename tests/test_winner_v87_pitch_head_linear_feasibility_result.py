from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v87_pitch_head_linear_feasibility_result.json"


def test_result_rejects_frozen_hidden_linear_head_route() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V87_PITCH_HEAD_LINEAR_FEASIBILITY_AUDIT"
    assert value["classification"] == "FROZEN_HIDDEN_LINEAR_PITCH_HEAD_INSUFFICIENT"
    assert value["decision"] == "PREREGISTER_RECURRENT_REPRESENTATION_DIAGNOSTIC"
    assert value["next_source_checkpoint_for_mechanism_proof"] is None
    assert value["failed_checks"] == []
    assert value["execution"] == {
        "formal_support_cells": 0,
        "least_squares_fits": 26,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
        "stage2_rollout_episodes": 160,
    }


def test_both_endpoints_improve_in_sample_but_regress_heldout() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert [row["label"] for row in value["endpoints"]] == ["half", "final"]
    for row in value["endpoints"]:
        source = row["source_bounded_pitch_error"]
        fitted = row["full_fit_bounded_pitch_error"]
        heldout = row["leave_one_configuration_out"]["aggregate_bounded_pitch_error"]
        assert row["full_fit"]["rank"] == 65
        assert row["repeat_solves_bit_exact"] is True
        assert fitted["mse"] < source["mse"] < heldout["mse"]
        assert row["endpoint_feasible"] is False


def test_result_grants_no_policy_or_hardware_authority() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert all(value["checks"].values())
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["support_gate_authorized_now"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["deployment_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["rdkx5_robot_serial_gpio_i2c_torque_motion"] is False
