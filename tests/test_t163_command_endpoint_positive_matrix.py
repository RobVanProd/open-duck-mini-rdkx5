from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t163_preregistration_contract() -> None:
    path = ANALYSIS / "t163_command_endpoint_positive_matrix_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T163_COMMAND_ENDPOINT_POSITIVE_MATRIX"
    )
    assert not value["failed_checks"]
    assert value["reference_slot"]["external_command_reference_preserved"]
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["hosted_compute_units"] == 0
    assert not value["authority"]["full_r2"]
    assert not value["authority"]["gate5"]


def test_t163_result_contract() -> None:
    path = ANALYSIS / "t163_command_endpoint_positive_matrix_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T163_COMMAND_ENDPOINT_POSITIVE_MATRIX",
        "HOLD_T163_COMMAND_ENDPOINT_POSITIVE_MATRIX",
    }
    assert value["execution"]["behavior_cells"] == 16
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert not value["authority"]["gate5"]
