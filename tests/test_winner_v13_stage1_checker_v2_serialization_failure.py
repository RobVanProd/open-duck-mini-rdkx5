from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT
    / "outputs/analysis/winner_v13_stage1_checker_v2_cpu_serialization_failure_attribution.json"
)


def test_failed_run_has_no_result_and_no_authority() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == "INVALID_ZERO_RESULT_SERIALIZATION_FAILURE"
    assert value["artifact"]["result_present"] is False
    assert value["artifact"]["inventory"] == [
        "winner-v13-stage1-checker-v2-work/winner_v13_stage1_checker_v2_zero_cell.onnx"
    ]
    assert value["attribution"]["scientific_decision_available"] is False
    assert value["authority"]["support_controller_training_authorized"] is False
    assert value["execution"]["optimizer_updates"] == 0


def test_failure_is_only_serialization_and_requires_fresh_run() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["attribution"]["phase"] == "post-comparison result serialization"
    assert "numpy.bool_" in value["attribution"]["mechanism"]
    assert value["decision"] == (
        "CORRECT_SERIALIZATION_AND_LAUNCH_FRESH_ZERO_CELL_CONTRACT"
    )
