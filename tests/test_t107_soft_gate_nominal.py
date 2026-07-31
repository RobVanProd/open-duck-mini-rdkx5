from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t107_preregistration_requires_both_checkpoints_when_present() -> None:
    path = ANALYSIS / "t107_soft_gate_nominal_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T107_SOFT_GATE_NOMINAL_MATRIX"
    )
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["matrix"]["no_checkpoint_selection"] is True
    assert value["authority"]["training"] is False


def test_t107_result_obeys_frozen_decision_when_present() -> None:
    path = ANALYSIS / "t107_soft_gate_nominal_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T107_SOFT_GATE_NOMINAL_MATRIX"
        assert value["decision"] == (
            "EARN_T108_SOFT_GATE_NEGATIVE_ENDPOINT_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T107_SOFT_GATE_NOMINAL_MATRIX"
        assert value["decision"] == "CLOSE_T100C_CONTINUOUS_GATE_TRANSFORM"
    assert value["interpretation"]["hosted_run_earned"] is False
