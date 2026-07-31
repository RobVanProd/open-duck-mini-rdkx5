from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t51_selects_only_remaining_nonduplicating_cause() -> None:
    path = ANALYSIS / "t51_t50_half_core_failure_attribution.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T51_T50_HALF_CORE_FAILURE_ATTRIBUTION"
    )
    assert value["decision"] == (
        "EARN_T52_FINAL_WITH_HALF_HEAD_UNIFORM_TRANSFORM_"
        "QUALIFICATION_PREREGISTRATION"
    )
    assert value["failed_checks"] == []
    assert value["failure"]["fit_id"] == "p31_34"
    assert value["failure"]["command_x_m_s"] == 0.077
    assert value["failure"]["trace"]["last_tick"] == 162
    assert value["failure"]["trace"][
        "first_abs_pitch_over_0p25_tick"
    ] == 136
    successor = value["causal_successor"]
    assert successor["variant_id"] == "FINAL_WITH_HALF_HEAD"
    assert successor["original_failed_cell_green"]
    assert successor["only_remaining_nonduplicating_one_group_variant"]
    assert value["authority"]["half_head_qualification_preregistration"]
    assert not value["authority"]["qualification_execution"]
    assert not value["authority"]["gate5"]
