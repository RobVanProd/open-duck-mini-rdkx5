from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t192b_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t192b_switch_effect_attribution_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T192B_SWITCH_EFFECT_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert value["switch_tick"] == 520
    assert value["terminal_tick"] == 546
    assert value["comparison"]["row_range_inclusive"] == [520, 546]
    assert value["authority"]["behavior"] is False
    assert value["authority"]["gate5"] is False


def test_t192b_result_when_present() -> None:
    path = ANALYSIS / "t192b_switch_effect_attribution_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    passed = value["status"] == "PASS_T192B_SWITCH_EFFECT_ATTRIBUTION"
    assert value["status"] in {
        "PASS_T192B_SWITCH_EFFECT_ATTRIBUTION",
        "HOLD_T192B_SWITCH_EFFECT_ATTRIBUTION",
    }
    assert (value["failed_checks"] == []) is passed
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["inference_rows"] == 0
    assert value["authority"]["gate5"] is False
    if passed:
        assert value["classification"] == (
            "FINAL_HEAD_OUTPUT_EQUIVALENT_ON_COMMITTED_FAILURE_STATE"
        )
        assert value["decision"] == (
            "EARN_T193_CORRECTED_DYNAMIC_SUPPORT_CPU_CONTRACT_"
            "PREREGISTRATION_ONLY"
        )
        assert all(value["checks"].values())
