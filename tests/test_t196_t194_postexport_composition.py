from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t196_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t196_t194_postexport_composition_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T196_T194_POSTEXPORT_COMPOSITION"
    )
    assert value["failed_checks"] == []
    assert len(value["graphs"]) == 3
    assert value["composition"]["new_runtime_inputs"] == 0
    assert value["composition"]["new_runtime_outputs"] == 0
    assert value["execution_now"]["behavior_cells"] == 0


def test_t196_result_when_present() -> None:
    path = ANALYSIS / "t196_t194_postexport_composition_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["status"] == "PASS_T196_T194_POSTEXPORT_COMPOSITION":
        assert value["failed_checks"] == []
        assert all(value["checks"].values())
        assert (
            value["decision"]
            == "EARN_T197_T194_NOMINAL_BEHAVIOR_MATRIX_"
            "PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T196_T194_POSTEXPORT_COMPOSITION"
        assert value["failed_checks"] == [
            "step_zero_model_byte_exact_to_t164_final"
        ]
        assert all(
            passed
            for name, passed in value["checks"].items()
            if name != "step_zero_model_byte_exact_to_t164_final"
        )
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["behavior_matrix"] is False
    assert value["authority"]["gate5"] is False
