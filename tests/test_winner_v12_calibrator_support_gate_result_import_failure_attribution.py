from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT
    / "outputs/analysis/"
    "winner_v12_calibrator_support_gate_result_import_failure_attribution.json"
)


def test_import_failure_is_read_only_and_exactly_attributed() -> None:
    result = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert result["status"] == (
        "ATTRIBUTED_WINNER_V12_FORMAL_RESULT_IMPORT_FAILURE"
    )
    assert result["decision"] == (
        "AUTHORIZE_ONE_READ_ONLY_IMPORTER_SOURCE_BINDING_CORRECTION_ONLY"
    )
    assert result["artifact"]["github_run_id"] == 29816212367
    assert result["artifact"]["github_run_attempt"] == 1
    assert result["artifact"]["raw_status"] == (
        "HOLD_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
    )
    assert result["artifact"]["raw_decision"] == (
        "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
    )
    assert result["checks"] and all(result["checks"].values())
    assert result["failed_checks"] == []
    assert result["execution"] == {
        "additional_formal_support_cells": 0,
        "additional_heldout_repeat_cells": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert result["authority"]["formal_gate_rerun"] is False
    assert result["authority"]["robot_clearance"] is False
