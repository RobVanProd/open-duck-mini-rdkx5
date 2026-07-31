from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t103_preregistration_is_exact_when_present() -> None:
    path = ANALYSIS / "t103_t100c_negative_endpoint_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T103_T100C_NEGATIVE_ENDPOINT_MATRIX"
    )
    assert value["condition"]["override"] == {
        "torso_com_offset_m": [-0.05, 0.0, 0.0]
    }
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["matrix"]["checkpoint_cherry_pick"] is False


def test_t103_result_obeys_frozen_decision_when_present() -> None:
    path = ANALYSIS / "t103_t100c_negative_endpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == (
            "PASS_T103_T100C_NEGATIVE_ENDPOINT_MATRIX"
        )
        assert value["decision"] == (
            "EARN_T104_FULL_R2_REVALIDATION_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == (
            "HOLD_T103_T100C_NEGATIVE_ENDPOINT_MATRIX"
        )
        assert value["decision"] == "CLOSE_T100C_HIDDEN_EXPERT_CONTINUATION"
