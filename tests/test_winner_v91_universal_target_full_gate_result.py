from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v91_universal_target_full_gate_result.json"


def test_result_passes_complete_universal_target_gate() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V91_UNIVERSAL_TARGET_FULL_GATE"
    assert value["decision"] == "PREREGISTER_UNIVERSAL_TARGET_POLICY_MECHANISM_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert value["failed_cells"] == []
    assert all(value["checks"].values())
    assert len(value["core_model_plant_cells"]) == 112
    assert len(value["sensor_transport_plant_cells"]) == 12
    assert all(
        cell["support_pass"]
        for cell in value["core_model_plant_cells"]
        + value["sensor_transport_plant_cells"]
    )


def test_target_chain_and_physical_envelope_are_green() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    cells = value["core_model_plant_cells"] + value["sensor_transport_plant_cells"]
    assert value["maximum_bounded_target_action_error"] == 0.0
    assert max(cell["episode"]["maximum_abs_tilt_rad"] for cell in cells) == 0.14471233755934648
    assert max(cell["episode"]["maximum_current_a"] for cell in cells) == 1.8309623642600787
    assert max(cell["episode"]["maximum_torque_nm"] for cell in cells) == 1.4364485655576882
    assert (
        max(
            cell["episode"]["maximum_final_window_gyro_xy_norm_rad_s"]
            for cell in cells
        )
        == 0.030829921804258479
    )
    assert min(cell["episode"]["minimum_base_z_m"] for cell in cells) == 0.15


def test_result_selects_no_checkpoint_or_hardware_action() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "formal_support_cells": 124,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
    }
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["deployment_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
