from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t42_attributes_one_late_stability_failure() -> None:
    value = json.loads(
        (
            ANALYSIS / "t42_t41_condition3_failure_attribution.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PASS_T42_T41_CONDITION3_FAILURE_ATTRIBUTION"
    )
    assert value["decision"] == (
        "EARN_T43_HALF_FORWARD_ACTOR_BLOCK_FACTORIAL_PREREGISTRATION"
    )
    assert value["failed_checks"] == []
    failed = value["failed_cell"]
    assert failed["condition_id"] == "JOINT_FRICTIONLOSS_LO"
    assert failed["checkpoint_id"] == "T39_UNIFORM_NORMALIZER_HALF"
    assert failed["fit_id"] == "p30"
    assert failed["command_x_m_s"] == 0.08
    assert failed["behavior"]["samples"] == 583
    assert failed["behavior"]["replacement_quality_pass"]
    assert failed["protection"]["duration_protection_pass"]
    onset = value["trace_summaries"]["failure"]["onset_ticks"]
    assert onset == {
        "abs_pitch_gt_0p25": 555,
        "abs_roll_gt_0p25": 530,
        "abs_roll_or_pitch_gt_0p5": 569,
        "base_height_lt_0p12": 574,
    }
    assert all(
        item["rows"] == 600 and not item["done"]
        for name, item in value["trace_summaries"].items()
        if name != "failure"
    )
    assert value["checks"][
        "endpoint_drift_is_exactly_base_plus_adapter"
    ]
    assert value["checks"]["normalizer_equal_across_endpoints"]
    assert value["factorial"]["run_all_variants"]
    assert value["factorial"]["no_early_stop"]
    assert value["execution"]["new_formal_behavior_cells"] == 0
    assert value["authority"]["t43_factorial_preregistration"]
    assert not value["authority"]["t43_behavior_execution"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
