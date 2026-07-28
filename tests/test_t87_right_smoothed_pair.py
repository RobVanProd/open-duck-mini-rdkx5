from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t87_prereg_attributes_one_stability_failure_and_freezes_rule() -> None:
    value = load("t87_right_smoothed_pair_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T87_RIGHT_SMOOTHED_ADAPTER_PAIR"
    )
    assert value["failed_checks"] == []
    assert value["attribution"]["classification"] == (
        "EARLY_ROLLING_WINDOW_FIT_SPECIFIC_STABILITY_GAP"
    )
    failed = value["attribution"]["only_failed_cell"]
    assert failed["checkpoint_id"] == "T84_ROLLING_HALF"
    assert failed["fit_id"] == "p30"
    assert failed["command_x_m_s"] == 0.08
    assert failed["samples"] == 479
    assert failed["termination_reason"] == "fall_or_nan"
    assert failed["pitch_tracking_p95_rad"] < 0.2
    assert failed["action_saturation_pct"] == 0.0
    assert failed["instant_rate_excess_rad_s"] == 0.0
    assert value["attribution"]["same_fit_later_window_x008_green"]
    transform = value["transform"]
    assert transform["coefficient"] == 0.5
    assert not transform["coefficient_sweep"]
    assert transform["terminal_edge_rule"] == "replicate_last"
    assert value["persistence_contract"]["both_required"]
    assert value["persistence_contract"]["no_checkpoint_selection"]
    assert value["authority"]["execute_one_cpu_graph_transform"]
    assert not value["authority"]["behavior_execution"]
    assert not value["authority"]["training"]
    assert not value["authority"]["gate5"]


def test_t87_transform_result_if_present() -> None:
    path = ANALYSIS / "t87_right_smoothed_pair_result.json"
    if not path.is_file():
        pytest.skip("T87 transform has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T87_RIGHT_SMOOTHED_ADAPTER_PAIR"
    assert value["failed_checks"] == []
    assert value["checks"]["right_smoothed_half_formula_exact"]
    assert value["checks"]["every_other_initializer_bit_exact"]
    assert value["checks"]["terminal_final_raw_byte_exact"]
    assert value["checks"]["terminal_final_deployment_byte_exact"]
    assert value["policies"]["right_smoothed_final"][
        "byte_exact_to_t84_rolling_final"
    ]
    assert value["authority"]["targeted_behavior_preregistration"]
    assert not value["authority"]["behavior_execution"]
    assert not value["authority"]["training"]
