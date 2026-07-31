from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t192_preregistration_when_present() -> None:
    path = ANALYSIS / "t192_one_period_head_switch_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T192_ONE_PERIOD_HEAD_SWITCH"
    assert value["failed_checks"] == []
    assert value["switch_tick"] == 520
    assert value["commands_x_m_s"] == [0.080]
    assert value["condition"]["id"] == "TORSO_COM_Y_NEG"
    assert value["fit"]["fit_id"] == "p31_34"
    assert value["execution_contract"]["behavior_cells"] == 1
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False


def test_t192_result_when_present() -> None:
    path = ANALYSIS / "t192_one_period_head_switch_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    passed = value["status"] == (
        "PASS_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY"
    )
    assert value["status"] in {
        "PASS_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY",
        "HOLD_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY",
    }
    assert value["execution"]["new_behavior_cells"] == 1
    assert value["switch"]["tick"] == 520
    assert value["switch"]["pre_switch_prefix_rows_compared"] == 520
    assert value["authority"]["gate5"] is False
    if passed:
        assert all(value["integrity_checks"].values())
        assert value["cell"]["cell_green"] is True
        assert value["decision"] == (
            "EARN_T193_CHECKPOINT_CONSISTENCY_TEACHER_"
            "CONTRACT_PREREGISTRATION_ONLY"
        )
