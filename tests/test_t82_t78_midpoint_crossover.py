from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t82_preregistration_is_two_cells_and_diagnostic() -> None:
    path = ANALYSIS / "t82_t78_midpoint_crossover_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T82_T78_MIDPOINT_CROSSOVER"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 2
    assert value["commands_x_m_s"] == [0.08]
    assert value["decision_rule"]["candidate_promotion"] is False
    assert value["decision_rule"]["persistence_satisfied"] is False
    assert value["decision_rule"]["no_coefficient_search"] is True


def test_t82_result_obeys_frozen_decision() -> None:
    path = ANALYSIS / "t82_t78_midpoint_crossover_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 2:
        assert value["status"] == "PASS_T82_T78_MIDPOINT_CROSSOVER"
        assert value["decision"] == (
            "EARN_T83_FULL_MIDPOINT_DIAGNOSTIC_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T82_T78_MIDPOINT_CROSSOVER"
        assert value["decision"] == "CLOSE_EXACT_T78_ADAPTER_MIDPOINT"
    assert not value["authority"]["candidate_promotion"]
    assert not value["authority"]["gate5"]
