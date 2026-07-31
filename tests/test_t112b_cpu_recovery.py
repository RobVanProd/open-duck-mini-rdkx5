from __future__ import annotations

import json
from pathlib import Path

from tools import build_t112_always_on_trainthrough_preregistration as t112


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t112b_preregistration_when_present() -> None:
    path = ANALYSIS / "t112b_cpu_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == t112.canonical_sha256(
        basis
    )
    assert value["status"] == "PREREGISTERED_T112B_READ_ONLY_CPU_RECOVERY"
    assert value["failed_checks"] == []
    assert value["recovery"]["additional_optimizer_steps"] == 0
    assert value["authority"]["hosted_training"] is False


def test_t112b_result_when_present() -> None:
    path = ANALYSIS / "t112b_cpu_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item for key, item in value.items() if key != "result_sha256"
    }
    assert value["result_sha256"] == t112.canonical_sha256(basis)
    assert value["status"] in {
        "PASS_T112B_READ_ONLY_CPU_RECOVERY",
        "HOLD_T112B_READ_ONLY_CPU_RECOVERY",
    }
    assert value["execution"]["additional_optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
