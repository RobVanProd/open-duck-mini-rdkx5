from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t80_preregistration_is_frozen_when_present() -> None:
    path = ANALYSIS / "t80_t78_nominal_matrix_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T80_T78_NOMINAL_MATRIX"
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 16
    assert value["decision_rule"]["both_checkpoints_required"] is True
    assert value["decision_rule"]["no_checkpoint_selection"] is True


def test_t80_result_obeys_frozen_decision_when_present() -> None:
    path = ANALYSIS / "t80_t78_nominal_matrix_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    green = value["condition"]["green_cells"]
    if green == 16:
        assert value["status"] == "PASS_T80_T78_NOMINAL_MATRIX"
        assert value["decision"] == (
            "EARN_T81_T78_R2_REVALIDATION_PREREGISTRATION"
        )
    else:
        assert value["status"] == "HOLD_T80_T78_NOMINAL_MATRIX"
        assert value["decision"] == (
            "CLOSE_T78_ENDPOINT_JOINT_ADAPTER_CONTINUATION"
        )
