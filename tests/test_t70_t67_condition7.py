from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t70_preregistration_is_exact_when_present() -> None:
    path = ANALYSIS / "t70_t67_condition7_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T70_T67_CONDITION7"
    assert value["failed_checks"] == []
    assert value["condition"] == {
        "condition_index": 7,
        "id": "TORSO_COM_X_NEG",
        "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
    }
    assert value["matrix"]["maximum_cells"] == 16
    assert value["decision_rule"]["both_checkpoints_required"] is True


def test_t70_result_obeys_decision_when_present() -> None:
    path = ANALYSIS / "t70_t67_condition7_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T70_T67_CONDITION7"
        assert (
            value["decision"]
            == "EARN_T71_T67_R2_REMAINDER_PREREGISTRATION"
        )
    else:
        assert value["status"] == "HOLD_T70_T67_CONDITION7"
        assert value["decision"] == "CLOSE_T67_ENDPOINT_CORE_CONTINUATION"
