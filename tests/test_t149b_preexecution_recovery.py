from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t149b_preregistration_when_present() -> None:
    path = ANALYSIS / "t149b_preexecution_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T149B_PREEXECUTION_RECOVERY"
    assert value["failed_checks"] == []
    assert value["decision_rule"]["no_further_preexecution_recovery"]


def test_t149b_result_when_present() -> None:
    path = ANALYSIS / "t149b_negative_context_command_plateau_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T149B_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["environment_steps"] == 0
