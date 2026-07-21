from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = ROOT / "outputs/analysis/winner_v23_negative_x_response_use_diagnostic_preregistration.json"
WORKFLOW = ROOT / ".github/workflows/winner-v23-negative-x-response-use-diagnostic.yml"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREGISTRATION.exists():
        return
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
    assert value["decision"] == "AUTHORIZE_ONE_READ_ONLY_20_PAIR_CELL_DIAGNOSTIC_ONLY"
    diagnostic = value["diagnostic"]
    assert diagnostic["paired_cells"] == 20
    assert diagnostic["physics_rollouts"] == 40
    assert diagnostic["early_analysis_ticks"] == 25
    assert diagnostic["minimum_cells_for_branch"] == 16
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["execution_now"]["robot_or_rdk_access"] == 0
    assert value["authority"]["training_authorized"] is False


def test_workflow_is_dormant_until_preregistration_commit() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v23_negative_x_response_use_diagnostic_preregistration.json" in trigger
    assert "--read-only-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
