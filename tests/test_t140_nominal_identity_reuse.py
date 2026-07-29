from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t140_preregistration_when_present() -> None:
    path = ANALYSIS / "t140_nominal_identity_reuse_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T140_NOMINAL_IDENTITY_REUSE"
    )
    assert value["execution_now"]["new_behavior_cells"] == 0


def test_t140_result_when_present() -> None:
    path = ANALYSIS / "t140_nominal_identity_reuse_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T140_NOMINAL_IDENTITY_REUSE"
    assert value["failed_checks"] == []
    assert value["inherited_evidence"]["cells"] == 16
    assert value["execution"]["new_behavior_cells"] == 0
