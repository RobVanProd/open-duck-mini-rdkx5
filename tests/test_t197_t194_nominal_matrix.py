from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t197_preregistration_when_present() -> None:
    path = ANALYSIS / "t197_t194_nominal_matrix_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T197_T194_NOMINAL_MATRIX"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["execution_now"]["behavior_cells"] == 0


def test_t197_result_when_present() -> None:
    path = ANALYSIS / "t197_t194_nominal_matrix_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T197_T194_NOMINAL_MATRIX",
        "HOLD_T197_T194_NOMINAL_MATRIX",
    }
    assert value["condition"]["total_cells"] == 16
    assert value["execution"]["behavior_cells"] == 16
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    assert value["authority"]["rdkx5_or_robot"] is False
