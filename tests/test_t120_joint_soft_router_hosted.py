from __future__ import annotations

import json
from pathlib import Path

from tools.build_t120_joint_soft_router_hosted_preregistration import (
    canonical_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t120_hosted_preregistration_when_present() -> None:
    path = ANALYSIS / "t120_joint_soft_router_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == canonical_sha256(basis)
    assert value["status"] == (
        "PREREGISTERED_T120_JOINT_SOFT_ROUTER_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["retry"] is False
    assert value["training"]["same_run_resume"] is False
    assert value["post_training"]["both_checkpoint_persistence_required"]


def test_t120_package_when_present() -> None:
    path = (
        ANALYSIS
        / "t120_joint_soft_router_hosted_package_contract.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T120_JOINT_SOFT_ROUTER_HOSTED_PACKAGE"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions_opened"] == 0
