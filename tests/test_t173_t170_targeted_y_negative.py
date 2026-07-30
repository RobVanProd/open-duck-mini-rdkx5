from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t173_preregistration_when_present() -> None:
    path = ANALYSIS / "t173_t170_targeted_y_negative_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T173_T170_TARGETED_Y_NEGATIVE"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["condition"]["id"] == "TORSO_COM_Y_NEG"
    assert value["authority"]["full_r2"] is False


def test_t173_result_when_present() -> None:
    path = ANALYSIS / "t173_t170_targeted_y_negative_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_T173_T170_TARGETED_Y_NEGATIVE"
    assert value["decision"] == "CLOSE_T170_EIGHT_STRATUM_HEAD_CONTINUATION"
    assert value["condition"]["condition_green"] is False
    assert value["condition"]["green_cells"] == 15
    assert value["execution"]["behavior_cells"] == 16
    assert value["authority"]["gate5"] is False
