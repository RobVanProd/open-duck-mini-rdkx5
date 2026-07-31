from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t191_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t191_t186_failure_exchange_autopsy_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T191_T186_FAILURE_EXCHANGE_AUTOPSY"
    )
    assert value["failed_checks"] == []
    assert len(value["traces"]) == 4
    assert value["analysis"]["gait_period_ticks"] == 27
    assert value["analysis"]["terminal_window_ticks"] == 54
    assert value["authority"]["behavior"] is False
    assert value["authority"]["gate5"] is False


def test_t191_result_when_present() -> None:
    path = ANALYSIS / "t191_t186_failure_exchange_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    passed = value["status"] == (
        "PASS_T191_T186_FAILURE_EXCHANGE_AUTOPSY"
    )
    assert value["status"] in {
        "PASS_T191_T186_FAILURE_EXCHANGE_AUTOPSY",
        "HOLD_T191_T186_FAILURE_EXCHANGE_AUTOPSY",
    }
    assert (value["failed_checks"] == []) is passed
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["authority"]["head_switch_preregistration"]:
        assert value["decision"] == (
            "EARN_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY_"
            "PREREGISTRATION_ONLY"
        )
        assert value["new_t186_failure"]["support_proximal"] is True
        assert (
            value["new_t186_failure"]["state_compatible_head_change"]
            is True
        )
