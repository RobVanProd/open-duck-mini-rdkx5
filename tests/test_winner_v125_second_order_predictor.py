from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v125_second_order_predictor_is_preregistered() -> None:
    path = ANALYSIS / "winner_v125_second_order_predictor_preregistration.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "c3218e1c7b86e7d7131f90d563aff0573b2f092db7f18b538fbaef7b34f13b1f"
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V125_SECOND_ORDER_PREDICTOR"
    )
    assert value["failed_checks"] == []
    assert value["predictor"]["fit_parameters"] == 0
    assert value["predictor"]["clipping_or_tuned_smoothing"] is False
    assert value["execution_now"]["behavior_rollouts"] == 0


def test_v125_closes_low_order_predictive_box_without_rollout() -> None:
    path = ANALYSIS / "winner_v125_second_order_predictor_result.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "c9c49a860f704b0cdaf71138a4785cc806f900c7804f10d1821eb4fd56b88812"
    )
    assert value["status"] == "HOLD_WINNER_V125_SECOND_ORDER_PREDICTOR"
    assert value["checks"]["v121_event_precursors_exact_15"]
    assert not value["checks"]["positive_half_width_every_joint"]
    assert not value["checks"]["all_v121_event_precursors_feasible"]
    assert not value["checks"]["zero_empty_passing_intersections"]
    assert value["event_precursors"]["infeasible_count"] == 15
    assert value["feasibility"]["empty_intersections"] == 21925
    assert value["decision"]["status"] == (
        "CLOSE_LOW_ORDER_KINEMATIC_PREDICTIVE_BOX_FAMILY"
    )
    assert value["execution"]["behavior_rollouts"] == 0
    assert value["execution"]["training_steps"] == 0
    assert not value["authority"]["wrapper_preregistration_authorized"]
    assert not value["authority"]["hosted_training_authorized"]
