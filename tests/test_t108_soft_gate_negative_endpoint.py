from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t108_preregistration_freezes_exact_endpoint_when_present() -> None:
    path = ANALYSIS / "t108_soft_gate_negative_endpoint_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T108_SOFT_GATE_NEGATIVE_ENDPOINT"
    )
    assert value["condition"]["override"] == {
        "torso_com_offset_m": [-0.05, 0.0, 0.0]
    }
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["matrix"]["no_checkpoint_selection"] is True


def test_t108_result_obeys_frozen_decision_when_present() -> None:
    path = ANALYSIS / "t108_soft_gate_negative_endpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == (
            "PASS_T108_SOFT_GATE_NEGATIVE_ENDPOINT"
        )
        assert value["decision"] == (
            "EARN_T109_SOFT_GATE_FULL_R2_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == (
            "HOLD_T108_SOFT_GATE_NEGATIVE_ENDPOINT"
        )
        assert value["decision"] == "CLOSE_T100C_CONTINUOUS_GATE_TRANSFORM"
    assert value["interpretation"]["hosted_run_earned"] is False
