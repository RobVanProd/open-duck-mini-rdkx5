from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT / "outputs/analysis/winner_v14_support_action_episode_binding_failure_attribution.json"
)


def test_episode_binding_failure_completed_no_cells() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == "INVALID_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_EPISODE_BINDING"
    assert value["repository_attribution"]["github_run_id"] == 29833729219
    assert value["repository_attribution"]["artifact_count"] == 0
    assert value["failure"]["correction"] == (
        "replace only base.Episode with base.smoke.Episode"
    )
    assert value["execution"]["completed_main_cells"] == 0
    assert value["execution"]["completed_repeat_cells"] == 0
    assert value["execution"]["result_json_created"] is False
    assert value["authority"]["robot_clearance"] is False
