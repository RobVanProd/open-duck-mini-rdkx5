from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t149_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t149_negative_context_command_plateau_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["external_command"] == "unchanged"
    assert value["mechanism"]["cap_m_s"] == 0.074


def test_t149_result_when_present() -> None:
    path = ANALYSIS / "t149_negative_context_command_plateau_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["environment_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
