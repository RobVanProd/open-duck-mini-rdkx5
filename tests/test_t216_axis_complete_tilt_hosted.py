from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t216_driver_freezes_only_selected_constraint_mechanism() -> None:
    text = (
        ROOT / "tools" / "colab_t216_axis_complete_tilt_continuation.py"
    ).read_text(encoding="utf-8")
    assert "--winner_v127_constrained_cost" in text
    assert "--winner_t215b_axis_complete_tilt_cost" in text
    assert '"--winner_t209_dual_roll_cost" not in command' in text
    assert "--winner_t202_predicted_roll_risk" in text
    assert '"--winner_t202_predicted_roll_risk" not in command' in text
    assert "legacy_constraint_reward_penalties_zero" in text
    assert "exact_policy_cost_aux_and_onnx_exports" in text
    assert "hosted_axis_complete_cost_exercised" in text
    assert "final_dual_price_not_below_half" in text
    assert '"retry": False' in text
    assert '"same_run_resume": False' in text


def test_t216_preregistration_when_present() -> None:
    path = ANALYSIS / "t216_axis_complete_tilt_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T216_AXIS_COMPLETE_TILT_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["timesteps"] == 2_007_040
    assert value["training"]["exports"] == [0, 1_003_520, 2_007_040]
    assert value["training"]["cost"] == "square(max(0,score-1))"
    assert value["training"]["passing_envelope_rad"] == {
        "pitch": 0.2379576557426921,
        "roll": 0.3541802655745987,
    }
    assert value["training"]["cost_critic"] == "separate"
    assert value["training"]["legacy_constraint_reward_penalties"] == 0.0
    assert value["training"]["retry"] is False
    assert value["training"]["same_run_resume"] is False
    assert value["post_training"][
        "positive_finite_tilt_cost_required_before_behavior"
    ]
    assert value["post_training"][
        "positive_finite_dual_eta_and_lambda_required_before_behavior"
    ]
    assert value["authority"]["checkpoint_selection"] is False
    assert value["authority"]["gate5"] is False


def test_t216_package_contract_when_present() -> None:
    path = ANALYSIS / "t216_axis_complete_tilt_hosted_package_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T216_AXIS_COMPLETE_TILT_HOSTED_PACKAGE"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions_opened"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0


def test_t216_launch_contract_when_present() -> None:
    path = ANALYSIS / "t216_colab_cli_launch_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T216_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert value["session"]["accelerator"] == "L4"
    assert value["session"]["count"] == 1
    assert value["recovery"]["retry"] is False
    assert value["recovery"]["same_run_resume"] is False
    assert value["authority"]["behavior_evaluation"] is False
    assert value["authority"]["gate5"] is False
