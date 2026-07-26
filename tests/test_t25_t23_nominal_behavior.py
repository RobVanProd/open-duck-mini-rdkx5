from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t25_preregisters_unchanged_persistent_16_cell_gate() -> None:
    value = load("t25_t23_nominal_behavior_preregistration.json")
    assert value["status"] == "PREREGISTERED_T25_T23_NOMINAL_BEHAVIOR"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["matrix"]["cells"] == 16
    assert {row["step"] for row in value["matrix"]["rows"]} == {
        1_003_520,
        2_007_040,
    }
    assert {row["plant"] for row in value["matrix"]["rows"]} == {
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
    }
    assert {row["command_x_m_s"] for row in value["matrix"]["rows"]} == {
        0.0,
        0.074,
        0.077,
        0.080,
    }
    assert value["authority"]["formal_behavior_cells_authorized"] == 16
    assert value["authority"]["full_matrix_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False


def test_t25_result_is_valid_and_never_directly_opens_gate5() -> None:
    value = load("t25_t23_nominal_behavior_result.json")
    assert value["status"] == "PASS_T25_T23_NOMINAL_BEHAVIOR_VALID_RESULT"
    assert value["failed_validity_checks"] == []
    assert value["summary"]["cells"] == 16
    assert value["authority"]["behavior_evaluation_authorized"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
