from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t62_recovered_training_validation.json"
)


def test_t62_recovery_is_exact_before_behavior() -> None:
    if not RESULT.exists():
        pytest.skip("T62 recovered training has not been validated")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T62_RECOVERED_TRAINING_VALIDATION"
    assert value["failed_checks"] == []
    assert value["checks"]["midpoint_step_zero_source_bit_exact"]
    assert value["checks"]["transfer_step_zero_midpoint_final_bit_exact"]
    assert value["checks"]["all_midpoint_actor_and_critic_leaves_updated"]
    assert value["checks"]["all_transfer_actor_and_critic_leaves_updated"]
    assert value["checks"]["all_onnx_contracts_pass"]
    assert value["classification"]["behavior_cells"] == 0
    assert value["authority"]["postexport_transform_preregistration_authorized"]
    assert not value["authority"]["behavior_evaluation_authorized"]
    assert not value["authority"]["gate5_authorized"]
