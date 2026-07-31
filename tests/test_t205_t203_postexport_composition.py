from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t205_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t205_t203_postexport_composition_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T205_T203_POSTEXPORT_COMPOSITION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert [row["step"] for row in value["graphs"]] == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert value["composition"]["expected_changed_pair_for_all_three"]
    assert value["composition"]["new_runtime_inputs"] == 0
    assert value["composition"]["new_runtime_outputs"] == 0
    assert value["execution_now"]["behavior_cells"] == 0


def test_t205_result_when_present() -> None:
    path = ANALYSIS / "t205_t203_postexport_composition_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["status"] == "PASS_T205_T203_POSTEXPORT_COMPOSITION":
        assert value["failed_checks"] == []
        assert all(value["checks"].values())
        assert (
            value["decision"]
            == "EARN_T206_T203_NOMINAL_BEHAVIOR_MATRIX_"
            "PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T205_T203_POSTEXPORT_COMPOSITION"
        assert value["failed_checks"] == [
            "both_y_negative_fits_exercise_changed_moving_action"
        ]
        assert all(
            passed
            for name, passed in value["checks"].items()
            if name
            != "both_y_negative_fits_exercise_changed_moving_action"
        )
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["behavior_matrix"] is False
    assert value["authority"]["gate5"] is False
