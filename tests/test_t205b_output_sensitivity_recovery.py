from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t205b_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t205b_output_sensitivity_recovery_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T205B_OUTPUT_SENSITIVITY_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution_now"]["inference_samples"] == 0
    assert value["execution_now"]["behavior_cells"] == 0


def test_t205b_result_when_present() -> None:
    path = ANALYSIS / "t205b_output_sensitivity_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T205B_OUTPUT_SENSITIVITY_RECOVERY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T206_T203_NOMINAL_BEHAVIOR_MATRIX_"
        "PREREGISTRATION_ONLY"
    )
    assert value["execution_now"]["inference_samples"] == 0
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["authority"]["behavior_matrix"] is False
    assert value["authority"]["gate5"] is False
