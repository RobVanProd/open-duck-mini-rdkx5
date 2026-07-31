from __future__ import annotations

from tools.run_t182_shared_failure_single_cell import decision


def test_green_cell_earns_only_dual_condition_preregistration() -> None:
    status, next_decision = decision(True)
    assert status == "PASS_T182_SHARED_FAILURE_SINGLE_CELL"
    assert next_decision == (
        "EARN_T183_DUAL_CONDITION_32_CELL_PREREGISTRATION_ONLY"
    )


def test_failed_cell_closes_alpha_without_retry() -> None:
    status, next_decision = decision(False)
    assert status == "HOLD_T182_SHARED_FAILURE_SINGLE_CELL"
    assert next_decision == (
        "CLOSE_COUNT_WEIGHTED_ALPHA_0P2_WITHOUT_MORE_BEHAVIOR"
    )
