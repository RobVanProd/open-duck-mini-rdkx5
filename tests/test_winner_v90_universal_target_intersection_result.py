from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v90_universal_target_intersection_result.json"


def test_result_finds_and_selects_universal_target() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V90_UNIVERSAL_TARGET_INTERSECTION_AUDIT"
    assert value["classification"] == "UNIVERSAL_STATIC_TARGETS_EXIST_IN_CAPTURED_GRID"
    assert value["decision"] == "PREREGISTER_FULL_124_CELL_UNIVERSAL_TARGET_FEASIBILITY_GATE"
    assert value["intersection_count"] == 25
    assert len(value["intersection_candidate_indices"]) == 25
    selected = value["selected_universal_target"]
    assert selected["candidate_index"] == 536
    assert selected["coordinates"] == [0.5, 0.25, 0.25]
    assert selected["support_pass_count"] == 30
    assert selected["minimum_valid_ticks"] == 250
    assert selected["sum_valid_ticks"] == 7500


def test_every_intersection_candidate_passes_all_captured_cells() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert all(value["checks"].values())
    assert len(value["universal_candidates"]) == 25
    for candidate in value["universal_candidates"]:
        assert candidate["support_pass_count"] == 30
        assert candidate["minimum_valid_ticks"] == 250
        assert candidate["sum_valid_ticks"] == 7500


def test_result_is_saved_only_and_grants_no_policy_or_hardware_authority() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "new_simulation_cells": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "saved_candidate_receipts_read": 10935,
        "snapshot_or_onnx_writes": 0,
    }
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["support_gate_authorized_now"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
