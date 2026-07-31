from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v78_missing_teacher_extension_result.json"


def test_result_extends_the_teacher_table_for_the_sole_missing_configuration() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V78_MISSING_TEACHER_EXTENSION"
    assert value["decision"] == (
        "AUTHORIZE_SEPARATELY_PREREGISTERED_RESIDUAL_TEACHER_DIAGNOSTIC_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"] == {
        "configuration_tables": 1,
        "static_target_candidates": 729,
        "candidate_plant_cells": 1458,
        "selected_target_replay_cells": 2,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }
    row = value["configuration_result"]
    assert row["configuration_id"] == "COM_CORNER_07"
    assert row["shared_support_pass_count"] == 207
    assert row["per_plant_support_pass_counts"] == {
        "P30_ALL_JOINT": 213,
        "P31_34_PITCH_WITH_P30_NONPITCH": 210,
    }
    assert row["selected_candidate_index"] == 437
    assert row["selected_coordinates"] == [0.25, -0.25, 0.25]
    assert row["selected_replay_exact"] is True
    assert all(item["support_pass"] for item in row["selected_replay_results"])
    assert all(item["terminal"] is None for item in row["selected_replay_results"])
    assert value["teacher_table_extension"] == {
        "COM_CORNER_07": {
            "candidate_index": 437,
            "coordinates": [0.25, -0.25, 0.25],
            "coordinates_sha256": (
                "4798d921bafaaf2a3ffcb74fbc5296d64bb05ab4c4bcd6f8a7b3243a7bd8d8f9"
            ),
            "shared_support_pass": True,
        }
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["training_authorized"] is False
