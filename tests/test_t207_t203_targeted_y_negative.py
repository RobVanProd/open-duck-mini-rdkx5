from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t207_preregistration_when_present() -> None:
    path = ANALYSIS / "t207_t203_targeted_y_negative_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T207_T203_TARGETED_Y_NEGATIVE"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["matrix"]["checkpoint_cherry_pick"] is False
    assert value["condition"]["id"] == "TORSO_COM_Y_NEG"
    assert value["condition"]["override"] == {
        "torso_com_offset_m": [0.0, -0.05, 0.0]
    }
    assert value["authority"]["full_r2"] is False
    assert value["authority"]["gate5"] is False


def test_t207_result_when_present() -> None:
    path = ANALYSIS / "t207_t203_targeted_y_negative_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    passed = value["status"] == "PASS_T207_T203_TARGETED_Y_NEGATIVE"
    assert value["status"] in {
        "PASS_T207_T203_TARGETED_Y_NEGATIVE",
        "HOLD_T207_T203_TARGETED_Y_NEGATIVE",
    }
    assert value["decision"] == (
        "EARN_T208_T203_FULL_R2_PREREGISTRATION_ONLY"
        if passed
        else "CLOSE_T203_PREDICTED_ROLL_RISK_CONTINUATION"
    )
    assert value["condition"]["condition_green"] is passed
    assert 0 <= value["condition"]["green_cells"] <= 16
    assert (value["condition"]["green_cells"] == 16) is passed
    assert value["execution"]["behavior_cells"] == 16
    assert value["authority"]["full_r2_preregistration"] is passed
    assert value["authority"]["gate5"] is False
