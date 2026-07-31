from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t104_preregistration_is_read_only_when_present() -> None:
    path = ANALYSIS / "t104_t100c_gate_dynamics_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T104_T100C_GATE_DYNAMICS_AUDIT"
    )
    assert len(value["traces"]) == 32
    assert value["measurements"]["warmup_ticks"] == 32
    assert value["decision_rule"]["training_selection_weight"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["rdkx5_or_robot"] is False


def test_t104_result_obeys_frozen_classification_when_present() -> None:
    path = ANALYSIS / "t104_t100c_gate_dynamics_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T104_T100C_GATE_DYNAMICS_AUDIT"
    inputs = value["decision_inputs"]
    if (
        inputs["nominal_false_active_fraction_post_warmup"] > 0.05
        or inputs[
            "negative_com_false_inactive_fraction_post_warmup"
        ]
        > 0.05
        or inputs["failing_trace_exceeds_transition_limit"]
    ):
        assert value["classification"] == (
            "HARD_GATE_DYNAMICS_INCONSISTENT"
        )
        assert value["decision"] == (
            "EARN_T105_GATE_STABILIZATION_CPU_PREREGISTRATION_ONLY"
        )
    elif (
        inputs["expert_effect_material"]
        and inputs["negative_com_failures_increase_half_to_final"]
    ):
        assert value["classification"] == (
            "ACTIVE_EXPERT_CLOSED_LOOP_DRIFT"
        )
        assert value["decision"] == (
            "EARN_T105_EXPERT_DRIFT_ATTRIBUTION_PREREGISTRATION_ONLY"
        )
    else:
        assert value["classification"] == "NO_HIDDEN_EXPERT_CAUSAL_TARGET"
        assert value["decision"] == (
            "CLOSE_T100C_WITHOUT_HIDDEN_EXPERT_SUCCESSOR"
        )
