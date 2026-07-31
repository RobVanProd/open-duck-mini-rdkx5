from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t123_preregistration_when_present() -> None:
    path = ANALYSIS / "t123_t120_nominal_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T123_T120_NOMINAL_MATRIX"
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["authority"]["training"] is False


def test_t123_result_when_present() -> None:
    path = ANALYSIS / "t123_t120_nominal_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T123_T120_NOMINAL_MATRIX"
        assert value["decision"] == (
            "EARN_T124_T120_NEGATIVE_ENDPOINT_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T123_T120_NOMINAL_MATRIX"
        assert value["decision"] == (
            "CLOSE_T120_JOINT_SOFT_ROUTER_TRAINTHROUGH"
        )
