from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t177_preregistration_when_present() -> None:
    path = ANALYSIS / "t177_head_prefix_mean_full_r2_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T177_HEAD_PREFIX_MEAN_FULL_R2"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 320
    assert value["matrix"]["stop_after_first_failed_condition"] is True
    assert value["authority"]["gate5"] is False


def test_t177_result_when_present() -> None:
    path = ANALYSIS / "t177_head_prefix_mean_full_r2_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T177_HEAD_PREFIX_MEAN_FULL_R2",
        "HOLD_T177_HEAD_PREFIX_MEAN_FULL_R2",
    }
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["authority"]["gate5_hardware_authorized"] is False
