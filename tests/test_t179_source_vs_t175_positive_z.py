from __future__ import annotations

from tools.run_t179_source_vs_t175_positive_z import classify_ab


def _failure(checkpoint: str, command: float) -> dict:
    return {
        "checkpoint_id": checkpoint,
        "fit_id": "p30",
        "command_x_m_s": command,
    }


def test_source_green_attributes_regression_to_transform() -> None:
    classification, decision = classify_ab(
        source_green=16,
        transformed_green=11,
        source_failures=[],
        transformed_failures=[_failure("T175_HEAD_MEAN_HALF", 0.077)],
        identical_trace_count=0,
    )
    assert classification == (
        "T175_HEAD_PREFIX_MEAN_INTRODUCED_POSITIVE_Z_REGRESSION"
    )
    assert "TRANSFORM_ROUTE_ATTRIBUTION" in decision


def test_identical_failure_matrix_and_traces_exonerates_transform() -> None:
    source = [_failure("T170_SOURCE_HALF", 0.077)]
    transformed = [_failure("T175_HEAD_MEAN_HALF", 0.077)]
    classification, decision = classify_ab(
        source_green=11,
        transformed_green=11,
        source_failures=source,
        transformed_failures=transformed,
        identical_trace_count=16,
    )
    assert classification == (
        "T175_NO_EFFECT_POSITIVE_Z_FAILURE_PREDATES_TRANSFORM"
    )
    assert "BALANCE_MECHANISM_REVIEW" in decision


def test_transform_partial_improvement_is_not_a_pass() -> None:
    classification, decision = classify_ab(
        source_green=8,
        transformed_green=11,
        source_failures=[_failure("T170_SOURCE_HALF", 0.074)],
        transformed_failures=[_failure("T175_HEAD_MEAN_HALF", 0.077)],
        identical_trace_count=0,
    )
    assert classification == "T175_PARTIAL_POSITIVE_Z_IMPROVEMENT_INSUFFICIENT"
    assert "BALANCE_MECHANISM_REVIEW" in decision
