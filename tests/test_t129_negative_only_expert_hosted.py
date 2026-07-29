from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t129_preregistration_when_present() -> None:
    path = ANALYSIS / "t129_negative_only_expert_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T129_NEGATIVE_ONLY_EXPERT_HOSTED_CONTINUATION"
    )
    assert value["training"]["body_configuration_strata"] == 1
    assert value["training"]["exact_torso_com_offset_m"] == [-0.05, 0.0, 0.0]
    assert value["training"]["retry"] is False
    assert value["post_training"]["both_checkpoint_persistence_required"]


def test_t129_package_when_present() -> None:
    path = (
        ANALYSIS
        / "t129_negative_only_expert_hosted_package_contract.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T129_NEGATIVE_ONLY_EXPERT_HOSTED_PACKAGE"
    )
    assert value["checks"]["exact_command_constructed_once"]
    assert value["execution"]["optimizer_steps"] == 0
