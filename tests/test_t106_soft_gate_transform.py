from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t106_preregistration_is_exact_and_zero_training_when_present() -> None:
    path = ANALYSIS / "t106_soft_gate_transform_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T106_SOFT_GATE_TRANSFORM"
    assert value["transform"]["temperature"] == 1.0
    assert value["transform"]["new_input_or_output"] is False
    assert value["transform"]["new_recurrent_state"] is False
    assert value["transform"]["initializer_change"] is False
    assert value["transform"]["scalar_search"] is False
    assert value["authority"]["behavior"] is False
    assert value["authority"]["training"] is False


def test_t106_result_requires_every_contract_when_present() -> None:
    path = ANALYSIS / "t106_soft_gate_transform_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["failed_checks"]:
        assert value["status"] == "HOLD_T106_SOFT_GATE_TRANSFORM"
        assert value["decision"] == "CLOSE_T100C_CONTINUOUS_GATE_TRANSFORM"
    else:
        assert value["status"] == "PASS_T106_SOFT_GATE_TRANSFORM"
        assert value["decision"] == (
            "EARN_T107_SOFT_GATE_NOMINAL_MATRIX_PREREGISTRATION_ONLY"
        )
        assert all(value["checks"].values())
        assert value["metrics"]["maximum_step0_action_error"] <= 1.0e-7
        assert value["metrics"]["maximum_x0_action_error"] <= 1.0e-7
        assert value["interpretation"]["hosted_run_earned"] is False
