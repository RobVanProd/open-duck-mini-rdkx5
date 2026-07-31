from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t152_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t152_reflected_positive_expert_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T152_REFLECTED_POSITIVE_EXPERT"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["reflection_formula"] == (
        "positive=2*nominal-negative"
    )
    assert value["mechanism"]["reflection_scale"] == -1.0
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["execution_now"]["hosted_compute_units"] == 0


def test_t152_result_when_present() -> None:
    path = ANALYSIS / "t152_reflected_positive_expert_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "HOLD_T152_REFLECTED_POSITIVE_EXPERT"
    )
    assert value["failed_checks"] == [
        "reflected_actions_finite_and_bound",
        "x0_exact_zero_and_feedback",
    ]
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
