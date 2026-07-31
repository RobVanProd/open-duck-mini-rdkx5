from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t47_attributes_one_isolated_adapter_endpoint_failure() -> None:
    path = ANALYSIS / "t47_t46_condition4_failure_attribution.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T47_T46_CONDITION4_FAILURE_ATTRIBUTION"
    )
    assert value["decision"] == (
        "EARN_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL_PREREGISTRATION"
    )
    assert value["failed_checks"] == []
    assert value["failure"]["checkpoint_id"] == (
        "T45_UNIFORM_FINAL_BASE_FINAL"
    )
    assert value["failure"]["fit_id"] == "p30"
    assert value["failure"]["command_x_m_s"] == 0.077
    assert value["failure"]["trace"]["last_tick"] == 493
    assert value["failure"]["trace"][
        "first_abs_pitch_over_0p25_tick"
    ] == 467
    assert all(
        item["cell_green"] and item["samples"] == 600
        for item in value["matched_controls"].values()
    )
    assert value["endpoint_attribution"]["differing_initializers"] == [
        "adapter_bias",
        "adapter_hidden_bias",
        "adapter_hidden_weight",
        "adapter_obs_weight",
        "adapter_weight",
    ]
    assert value["execution"]["new_behavior_cells"] == 0
    assert value["authority"]["adapter_core_head_factorial_preregistration"]
    assert not value["authority"]["factorial_execution"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
