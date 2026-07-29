from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t152b_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t152b_reflected_positive_expert_recovery_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY"
    )
    assert value["recovery_kind"] == (
        "OUT_OF_DISTRIBUTION_RANDOM_HARNESS_AND_FALSE_X0_INVARIANT"
    )
    assert value["failed_checks"] == []
    assert len(value["trace_population"]) == 16
    assert value["execution_now"]["new_behavior_cells"] == 0


def test_t152b_result_when_present() -> None:
    path = (
        ANALYSIS / "t152b_reflected_positive_expert_recovery_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["new_behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
