from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT / "outputs/analysis/winner_v14_support_action_preexecution_failure_attribution.json"
)


def test_failure_is_preexecution_and_correction_is_narrow() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == "INVALID_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_PREEXECUTION"
    assert value["decision"] == "CORRECT_ONLY_FORMAL_RESULT_HASH_MODE_AND_FRESHLY_PREREGISTER"
    assert value["repository_attribution"]["github_run_id"] == 29833400247
    assert value["repository_attribution"]["github_run_attempt"] == 1
    assert value["repository_attribution"]["artifact_count"] == 0
    assert value["execution"] == {
        "locomotion_steps": 0,
        "main_cells": 0,
        "optimizer_updates": 0,
        "repeat_cells": 0,
        "result_json_created": False,
        "robot_or_rdk_access": 0,
    }
    assert value["failure"]["formal_result_lf_sha256"] == (
        "ad6e0ea99cf0d96fbcd336d7984467efccdd430591201d6fd5242a328518ce05"
    )
    assert value["authority"]["robot_clearance"] is False
