from __future__ import annotations

import json
from pathlib import Path

from tools import build_t98_hidden_expert_cpu_preregistration as build


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t98_preregistration_when_present() -> None:
    path = ANALYSIS / "t98_hidden_expert_cpu_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == build.canonical_sha256(
        basis
    )
    assert value["status"] == "PREREGISTERED_T98_HIDDEN_EXPERT_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert value["mechanism"]["trainable_actor_groups"] == [
        "negative_adapter_location"
    ]
    assert value["mechanism"]["policy_abi_change"] is False
    assert value["authority"]["hosted_training"] is False


def test_t98_result_when_present() -> None:
    path = ANALYSIS / "t98_hidden_expert_cpu_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {key: item for key, item in value.items() if key != "result_sha256"}
    assert value["result_sha256"] == build.canonical_sha256(basis)
    assert value["status"] in {
        "PASS_T98_HIDDEN_EXPERT_CPU_CONTRACT",
        "HOLD_T98_HIDDEN_EXPERT_CPU_CONTRACT",
    }
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
