from __future__ import annotations

import json
from pathlib import Path

from tools import build_t99_deployment_coordinate_audit_preregistration as t99


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t99_preregistration_when_present() -> None:
    path = ANALYSIS / "t99_deployment_coordinate_audit_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == t99.canonical_sha256(
        basis
    )
    assert value["status"] == "PREREGISTERED_T99_DEPLOYMENT_COORDINATE_AUDIT"
    assert value["failed_checks"] == []
    assert value["invalidation"]["optimizer_rerun"] is False
    assert value["invalidation"]["threshold_change"] is False
    assert value["authority"]["hosted_training"] is False


def test_t99_result_when_present() -> None:
    path = ANALYSIS / "t99_deployment_coordinate_audit_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {key: item for key, item in value.items() if key != "result_sha256"}
    assert value["result_sha256"] == t99.canonical_sha256(basis)
    assert value["status"] in {
        "PASS_T99_DEPLOYMENT_COORDINATE_AUDIT",
        "HOLD_T99_DEPLOYMENT_COORDINATE_AUDIT",
    }
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
