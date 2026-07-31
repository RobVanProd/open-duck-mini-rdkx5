from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t55_preexecution_velocity_hold_attribution.json"
)


def test_t55_preexecution_hold_has_zero_policy_decision_weight() -> None:
    if not RESULT.exists():
        pytest.skip("T55 pre-execution attribution has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T55_PREEXECUTION_VELOCITY_HOLD_ATTRIBUTION"
    )
    assert value["decision"] == (
        "EARN_T55B_EXACT_CPU_RECOVERY_PREREGISTRATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert value["observed"]["checkpoint_directories"] == 0
    assert value["observed"]["onnx_graphs"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["correction"]["curriculum_formula_change"] is False
    assert value["correction"]["source_checkpoint_change"] is False
    assert value["authority"]["t55b_cpu_recovery_preregistration"]
    assert not value["authority"]["cpu_recovery_execution"]
    assert not value["authority"]["hosted_training"]
