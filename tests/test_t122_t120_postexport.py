from __future__ import annotations

import json
from pathlib import Path

from tools import build_t122_t120_postexport_preregistration as build


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t122_preregistration_when_present() -> None:
    path = ANALYSIS / "t122_t120_postexport_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == (
        build.canonical_sha256(basis)
    )
    assert value["failed_checks"] == []
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t122_result_when_present() -> None:
    path = ANALYSIS / "t122_t120_postexport_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T122_T120_POSTEXPORT_TRANSFORM",
        "HOLD_T122_T120_POSTEXPORT_TRANSFORM",
    }
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
