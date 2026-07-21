from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v12_calibrator_support_gate_preregistration.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_gate_is_frozen_before_any_formal_cell() -> None:
    result = load()
    assert result["status"] == "PREREGISTERED_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
    assert result["decision"] == "AUTHORIZE_SUPPORT_GATE_CPU_CONTRACT_ONLY"
    assert result["execution_now"] == {
        "formal_support_cells": 0,
        "heldout_repeat_cells": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert result["authority"]["robot_clearance"] is False
    assert result["failed_checks"] == []
    assert result["checks"] and all(result["checks"].values())


def test_gate_matrix_and_no_closest_selection_are_exact() -> None:
    result = load()
    assert result["main_matrix"]["per_checkpoint"] == {
        "model_plant_cells": 112,
        "sensor_transport_plant_cells": 12,
        "total": 124,
    }
    assert result["main_matrix"]["both_checkpoints_total"] == 248
    assert len(result["main_matrix"]["model_configuration_ids"]) == 56
    assert result["selection"]["all_cells_at_both_checkpoints_must_pass"] is True
    assert result["selection"]["selection_by_closest_result"] is False
    assert result["selection"]["selection_by_training_reward"] is False


def test_context_repeat_and_prediction_rules_are_exact() -> None:
    context = load()["heldout_context_gate"]
    assert context["repeat_cells_both_checkpoints"] == 64
    assert context["repeat_outputs"] == [
        "observations",
        "actions",
        "auxiliary_predictions",
        "h_out",
    ]
    assert "strictly below" in context["required_prediction_rule"]
    assert "1e-7" in context["matched_plant_context_rule"]


def test_every_source_is_hash_bound() -> None:
    result = load()
    for item in result["sources"].values():
        path = ROOT / item["path"]
        observed = lf_sha256(path) if item["hash_mode"] == "lf" else sha256(path)
        assert observed == item["sha256"], item["path"]
