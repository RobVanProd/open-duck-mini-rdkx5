from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t25_preregisters_unchanged_persistent_16_cell_gate() -> None:
    value = load("t25_t23_nominal_behavior_preregistration.json")
    assert value["status"] == "PREREGISTERED_T25_T23_NOMINAL_BEHAVIOR"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["matrix"]["cells"] == 16
    assert {row["step"] for row in value["matrix"]["rows"]} == {
        1_003_520,
        2_007_040,
    }
    assert {row["plant"] for row in value["matrix"]["rows"]} == {
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
    }
    assert {row["command_x_m_s"] for row in value["matrix"]["rows"]} == {
        0.0,
        0.074,
        0.077,
        0.080,
    }
    assert value["authority"]["formal_behavior_cells_authorized"] == 16
    assert value["authority"]["full_matrix_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False


def test_first_t25_result_is_invalid_and_has_zero_policy_weight() -> None:
    value = load("t25_t23_nominal_behavior_result.json")
    assert value["status"] == "INVALID_T25_T23_NOMINAL_BEHAVIOR_RESULT"
    assert sorted(value["failed_validity_checks"]) == [
        "complete_manufacturer_gate_reported",
        "no_runner_exceptions",
    ]
    assert value["summary"]["cells"] == 16
    assert value["summary"]["failures_by_reason"] == {
        "runner_exception_ValueError": 16
    }
    assert value["authority"]["behavior_evaluation_authorized"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False


def test_t25_zero_context_contract_and_attribution_are_green() -> None:
    contract = load("t25_zero_context_evaluator_contract.json")
    assert contract["status"] == (
        "PASS_T25_ZERO_CONTEXT_EVALUATOR_CONTRACT"
    )
    assert contract["failed_checks"] == []
    assert all(contract["checks"].values())
    assert contract["contract"]["value"] == "all_float32_zeros"
    assert contract["contract"]["graph_semantics"] == (
        "diagnostic_input_bit_exactly_ignored"
    )
    assert contract["execution"]["simulator_locomotion_ticks"] == 0
    attribution = load("t25_nominal_evaluator_invalidity_attribution.json")
    assert attribution["status"] == (
        "PASS_T25_NOMINAL_EVALUATOR_INVALIDITY_ATTRIBUTION"
    )
    assert attribution["failed_checks"] == []
    assert all(attribution["checks"].values())
    assert attribution["first_execution"]["formal_policy_decision_weight"] == 0
    assert attribution["first_execution"]["valid_behavior_cells"] == 0
    assert attribution["first_execution"]["policy_rejected"] is False


def test_t25b_recovery_is_one_exact_evaluator_only_matrix() -> None:
    value = load("t25b_nominal_evaluator_recovery_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T25B_NOMINAL_EVALUATOR_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["correction"]["policies"] == "BYTE_IDENTICAL"
    assert value["correction"]["matrix"] == "BYTE_IDENTICAL"
    assert value["correction"]["gate"] == "BYTE_IDENTICAL"
    assert value["correction"]["response_calibrator"] is False
    assert value["authority"]["one_cpu_matrix_recovery"] is True
    assert value["authority"]["training_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False


def test_t25b_valid_result_never_directly_opens_gate5() -> None:
    value = load("t25b_t23_nominal_behavior_result.json")
    assert value["status"] == (
        "PASS_T25B_T23_NOMINAL_BEHAVIOR_VALID_RESULT"
    )
    assert value["failed_validity_checks"] == []
    assert value["summary"]["cells"] == 16
    assert value["evaluator_recovery"]["policy_change"] is False
    assert value["evaluator_recovery"]["matrix_change"] is False
    assert value["evaluator_recovery"]["gate_change"] is False
    assert value["authority"]["behavior_evaluation_authorized"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
