from __future__ import annotations

import json
from pathlib import Path

from tools import (
    build_t119b_random_binding_recovery_preregistration as build,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t119b_preregistration_when_present() -> None:
    path = ANALYSIS / "t119b_random_binding_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == (
        build.common.canonical_sha256(basis)
    )
    assert value["status"] == (
        "PREREGISTERED_T119B_READ_ONLY_BINDING_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert value["scope"]["optimizer_steps"] == 0
    assert value["authority"]["hosted_training"] is False


def test_t119b_result_when_present() -> None:
    path = ANALYSIS / "t119b_random_binding_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item for key, item in value.items() if key != "result_sha256"
    }
    assert value["result_sha256"] == build.common.canonical_sha256(basis)
    assert value["status"] in {
        "PASS_T119B_READ_ONLY_BINDING_RECOVERY",
        "HOLD_T119B_READ_ONLY_BINDING_RECOVERY",
    }
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
