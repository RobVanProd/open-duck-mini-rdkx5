from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t117_preregistration_when_present() -> None:
    path = ANALYSIS / "t117_t113_negative_endpoint_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T117_T113_NEGATIVE_ENDPOINT"
    assert value["condition"]["id"] == "TORSO_COM_X_NEG"
    assert value["matrix"]["cells"] == 16
    assert value["authority"]["training"] is False


def test_t117_result_when_present() -> None:
    path = ANALYSIS / "t117_t113_negative_endpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T117_T113_NEGATIVE_ENDPOINT"
        assert value["decision"] == (
            "EARN_T118_T113_FULL_R2_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T117_T113_NEGATIVE_ENDPOINT"
        assert value["decision"] == "CLOSE_T113_ALWAYS_ON_TRAINTHROUGH"
