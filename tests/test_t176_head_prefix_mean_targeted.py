from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t176_preregistration_when_present() -> None:
    path = ANALYSIS / "t176_head_prefix_mean_targeted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T176_HEAD_PREFIX_MEAN_TARGETED"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["authority"]["full_r2"] is False


def test_t176_result_when_present() -> None:
    path = ANALYSIS / "t176_head_prefix_mean_targeted_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T176_HEAD_PREFIX_MEAN_TARGETED"
    assert value["condition"]["condition_green"] is True
    assert value["condition"]["green_cells"] == 16
    assert value["execution"]["behavior_cells"] == 16
    assert value["authority"]["gate5"] is False
