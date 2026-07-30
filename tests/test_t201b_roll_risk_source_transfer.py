from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t201b_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t201b_roll_risk_source_transfer_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T201B_ROLL_RISK_SOURCE_TRANSFER"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["traces"]) == 20
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False


def test_t201b_result_when_present() -> None:
    path = ANALYSIS / "t201b_roll_risk_source_transfer_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T201B_ROLL_RISK_SOURCE_TRANSFER"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["failure_summaries"]) == 2
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
