from __future__ import annotations

import json
from pathlib import Path

from tools import build_t112_always_on_trainthrough_preregistration as common


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t114c_preregistration_when_present() -> None:
    path = ANALYSIS / "t114c_protobuf_presence_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == common.canonical_sha256(
        basis
    )
    assert value["failed_checks"] == []
    assert value["authority"]["behavior_evaluation"] is False


def test_t114c_result_when_present() -> None:
    path = ANALYSIS / "t114c_protobuf_presence_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item for key, item in value.items() if key != "result_sha256"
    }
    assert value["result_sha256"] == common.canonical_sha256(basis)
    if not value["failed_checks"]:
        assert value["status"] == (
            "PASS_T114C_PROTOBUF_PRESENCE_RECOVERY"
        )
        assert value["decision"] == (
            "EARN_T115_ALWAYS_ON_TRAINTHROUGH_NOMINAL_PREREGISTRATION_ONLY"
        )
        assert value["execution"]["formal_behavior_cells"] == 0
