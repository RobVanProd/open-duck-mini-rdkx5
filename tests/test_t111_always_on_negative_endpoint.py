from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t111_preregistration_when_present() -> None:
    path = ANALYSIS / "t111_always_on_negative_endpoint_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T111_ALWAYS_ON_NEGATIVE_ENDPOINT"
    )
    assert value["condition"]["override"] == {
        "torso_com_offset_m": [-0.05, 0.0, 0.0]
    }
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True


def test_t111_result_when_present() -> None:
    path = ANALYSIS / "t111_always_on_negative_endpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == (
            "PASS_T111_ALWAYS_ON_NEGATIVE_ENDPOINT"
        )
        assert value["decision"] == (
            "EARN_T112_ALWAYS_ON_FULL_R2_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == (
            "HOLD_T111_ALWAYS_ON_NEGATIVE_ENDPOINT"
        )
        assert value["decision"] == "CLOSE_T100C_ALWAYS_ON_EXPERT"
