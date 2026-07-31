from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t39_interruption_has_zero_decision_weight() -> None:
    value = load("t39_interrupted_execution_attribution.json")
    assert value["status"] == "PASS_T39_INTERRUPTED_EXECUTION_ATTRIBUTION"
    assert value["failed_checks"] == []
    assert value["classification"]["completed_cells"] == 8
    assert value["classification"]["missing_cells"] == 8
    assert value["classification"]["policy_decision_weight"] == 0
    assert not value["classification"]["policy_pass"]
    assert not value["classification"]["policy_failure"]
    assert not value["classification"]["t39_retry"]
    assert value["recovery_rule"]["do_not_reexecute_completed_blocks"]
    assert not value["recovery_rule"][
        "inspect_completed_cell_outcomes_before_preregistration"
    ]
    assert value["authority"]["t40_exact_recovery_preregistration"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t40_preregisters_exact_two_cached_two_new_blocks() -> None:
    value = load("t40_t39_exact_recovery_preregistration.json")
    assert value["status"] == "PREREGISTERED_T40_T39_EXACT_RECOVERY"
    assert value["failed_checks"] == []
    recovery = value["recovery"]
    assert recovery["completed_blocks"] == 2
    assert recovery["completed_cells"] == 8
    assert not recovery["reexecute_completed_blocks"]
    assert recovery["new_blocks_to_execute"] == 2
    assert recovery["new_cells_to_execute"] == 8
    assert recovery["aggregate_cells"] == 16
    assert recovery["one_attempt"]
    assert not recovery["retry"]
    assert value["decision_rule"]["both_checkpoints_required"]
    assert value["decision_rule"]["no_checkpoint_selection"]
    assert value["authority"]["execute_one_exact_cpu_recovery"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t40_result_reuses_and_executes_exactly_eight_cells_if_present() -> None:
    path = ANALYSIS / "t40_t39_exact_recovery_result.json"
    if not path.is_file():
        pytest.skip("formal T40 recovery has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    execution = value["execution"]
    assert execution["aggregated_formal_behavior_cells"] == 16
    assert execution["reused_formal_behavior_cells"] == 8
    assert execution["new_formal_behavior_cells"] == 8
    assert execution["cache_hits"] == 2
    assert execution["new_blocks"] == 2
    assert execution["training_steps"] == 0
    assert execution["hosted_compute_units"] == 0
    if value["status"].startswith("PASS_"):
        assert value["condition"]["green_cells"] == 16
        assert value["authority"]["robustness_preregistration"]
    else:
        assert value["condition"]["green_cells"] < 16
        assert not value["authority"]["robustness_preregistration"]
    assert not value["authority"]["robustness_execution"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
