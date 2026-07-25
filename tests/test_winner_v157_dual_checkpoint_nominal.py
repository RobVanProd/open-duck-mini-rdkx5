from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v157_preregistration_when_present() -> None:
    path = ANALYSIS / "winner_v157_dual_checkpoint_nominal_preregistration.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v157_dual_checkpoint_nominal_preregistration.json"
    ) == "4c68a315d14d1504d633fff7b196bf03d70e88a5cfa1bd3d2a779a22df1ccbb0"
    assert result["status"] == (
        "PREREGISTERED_WINNER_V157_DUAL_CHECKPOINT_NOMINAL"
    )
    assert result["failed_checks"] == []
    assert result["matrix"]["reused_half_cells"] == 8
    assert len(result["matrix"]["reused_final_cells"]) == 2
    assert len(result["matrix"]["new_final_rows"]) == 6
    assert result["matrix"]["combined_required"] == 16
    assert result["authority"]["new_final_behavior_cells"] == 6
    assert result["authority"]["gate5"] is False


def test_v157_result_when_present() -> None:
    path = ANALYSIS / "winner_v157_dual_checkpoint_nominal_result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v157_dual_checkpoint_nominal_result.json"
    ) == "430df5f76cc60f69bfa189a19d6d58e9b856c415c5006ab31ff981adef8fdc9d"
    assert result["status"] == "HOLD_WINNER_V157_DUAL_CHECKPOINT_NOMINAL"
    assert result["failed_checks"] == [
        "combined_reused_and_new_cells_16_of_16"
    ]
    assert result["summary"]["combined_cells_passing"] == 10
    assert result["summary"]["combined_cells_required"] == 16
    assert result["summary"]["new_final_cells_completed"] == 1
    assert result["summary"]["new_final_cells_passing"] == 0
    assert result["new_final_cells"][0]["failure_reasons"] == [
        "torque_peak_at_most_1p91229675_nm"
    ]
    assert result["decision"] == "CLOSE_VELOCITY_GATED_PHASE_RESIDUAL"
    assert result["authority"]["policy_deployment"] is False
