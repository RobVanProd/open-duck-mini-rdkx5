import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v119_recovered_training_is_valid_before_behavior() -> None:
    value = load("winner_v119_recovered_training_validation.json")
    assert value["status"] == (
        "PASS_WINNER_V119_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["classification"]["training_retry"] is False
    assert value["classification"]["training_resume"] is False
    assert value["classification"]["behavior_cells"] == 0
    assert [row["step"] for row in value["checkpoints"]] == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert all(
        row["every_policy_leaf_updated"]
        for row in value["trained_checkpoints"]
    )


def test_v120_hold_is_attributed_without_behavior_or_training() -> None:
    hold = load("winner_v120_deployment_transform_contract.json")
    attribution = load("winner_v120_deployment_hold_attribution.json")
    assert hold["status"] == (
        "HOLD_WINNER_V120_DEPLOYMENT_TRANSFORM_CONTRACT"
    )
    assert hold["failed_checks"] == [
        "all_source_train_rate_projections_exact"
    ]
    assert hold["formal_behavior_cells_executed"] == 0
    assert attribution["status"] == (
        "PASS_WINNER_V120_DEPLOYMENT_HOLD_ATTRIBUTION"
    )
    assert attribution["failed_checks"] == []
    assert all(attribution["checks"].values())
    assert attribution["decision"] == (
        "PREREGISTER_V121_EXACT_TRAIN_DELTA_DEPLOYMENT_TRANSFORM"
    )
    assert attribution["execution"]["training_steps"] == 0
    assert attribution["execution"]["formal_behavior_cells"] == 0


def test_v121_deployment_contract_matches_exact_trained_delta() -> None:
    prereg = load("winner_v121_deployment_transform_preregistration.json")
    contract = load("winner_v121_deployment_transform_contract.json")
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V121_DEPLOYMENT_TRANSFORM"
    )
    assert prereg["failed_checks"] == []
    assert all(prereg["checks"].values())
    assert contract["status"] == (
        "PASS_WINNER_V121_DEPLOYMENT_TRANSFORM_CONTRACT"
    )
    assert contract["failed_checks"] == []
    assert all(contract["checks"].values())
    assert contract["formal_behavior_cells_executed"] == 0
    assert len(contract["policies"]) == 2
    assert all(
        row["source_train_delta_exact"]
        and row["final_projection_delta_exact"]
        and row["inference"]["pass"]
        for row in contract["policies"]
    )


def test_v121_nominal_gate_is_frozen_for_both_checkpoints() -> None:
    value = load("winner_v121_nominal_behavior_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_WINNER_V121_NOMINAL_BEHAVIOR"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["matrix"]["cells"] == 16
    assert {row["step"] for row in value["matrix"]["rows"]} == {
        1_003_520,
        2_007_040,
    }
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["authority"]["gate5_authorized"] is False


def test_v121_nominal_result_is_valid_but_not_persistent() -> None:
    value = load("winner_v121_nominal_behavior_result.json")
    assert value["status"] == (
        "PASS_WINNER_V121_NOMINAL_BEHAVIOR_VALID_RESULT"
    )
    assert value["failed_validity_checks"] == []
    assert all(value["validity_checks"].values())
    assert value["summary"]["cells"] == 16
    assert value["summary"]["passing_cells"] == 11
    assert value["summary"]["persistent_both_checkpoint_pass"] is False
    checkpoints = {
        row["step"]: row for row in value["per_checkpoint"]
    }
    assert checkpoints[1_003_520]["passing_cells"] == 8
    assert checkpoints[2_007_040]["passing_cells"] == 3
    assert value["summary"]["worst_tracking_p95_rad"] < 0.20
    assert value["summary"]["minimum_moving_mean_vx_m_s"] > 0.0
    assert value["decision"]["status"] == "REJECT_V121_NOMINAL_POLICY"
    assert value["authority"]["gate5_authorized"] is False


def test_v121_peak_diagnosis_selects_exact_gate_objective() -> None:
    value = load("winner_v121_peak_objective_diagnosis.json")
    assert value["status"] == (
        "PASS_WINNER_V121_PEAK_OBJECTIVE_DIAGNOSIS"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["summary"] == {
        "cells": 16,
        "early_tick_0_31_events": 13,
        "failed_cells": 5,
        "joint_event_counts": {
            "left_knee": 13,
            "right_ankle": 2,
        },
        "max_peak_integral_identity_error_nm": 0.0,
        "simultaneous_exceed_ticks": 0,
        "torque_exceed_events": 15,
        "within_two_tick_rate_boundary_events": 3,
    }
    selected = value["selected_mechanism"]
    assert selected["name"] == (
        "episode_global_peak_torque_increment_integral"
    )
    assert selected["replace_linear_mean_hinge"] is True
    assert selected["scale_search"] is False
    assert selected["both_new_postupdate_checkpoints_required"] is True
    assert value["decision"] == (
        "PREREGISTER_V122_DEFAULT_OFF_EPISODE_PEAK_CPU_CONTRACT"
    )
    assert value["execution"]["colab_compute_units"] == 0
    assert value["authority"]["training_authorized"] is False
