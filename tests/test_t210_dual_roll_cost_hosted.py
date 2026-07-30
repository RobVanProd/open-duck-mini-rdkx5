from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t210_driver_freezes_only_selected_constraint_mechanism() -> None:
    text = (
        ROOT / "tools" / "colab_t210_dual_roll_cost_continuation.py"
    ).read_text(encoding="utf-8")
    assert "--winner_v127_constrained_cost" in text
    assert "--winner_t209_dual_roll_cost" in text
    assert "--winner_t202_predicted_roll_risk" in text
    assert '"--winner_t202_predicted_roll_risk" not in command' in text
    assert "legacy_constraint_reward_penalties_zero" in text
    assert "exact_policy_cost_aux_and_onnx_exports" in text
    assert '"retry": False' in text
    assert '"same_run_resume": False' in text


def test_t210_preregistration_when_present() -> None:
    path = ANALYSIS / "t210_dual_roll_cost_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T210_DUAL_ROLL_COST_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["timesteps"] == 2_007_040
    assert value["training"]["exports"] == [0, 1_003_520, 2_007_040]
    assert value["training"]["cost"] == "unscaled_squared_excess"
    assert value["training"]["cost_critic"] == "separate"
    assert value["training"]["legacy_constraint_reward_penalties"] == 0.0
    assert value["training"]["retry"] is False
    assert value["training"]["same_run_resume"] is False
    assert value["authority"]["checkpoint_selection"] is False
    assert value["authority"]["gate5"] is False


def test_t210_package_contract_when_present() -> None:
    path = ANALYSIS / "t210_dual_roll_cost_hosted_package_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T210_DUAL_ROLL_COST_HOSTED_PACKAGE"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions_opened"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0


def test_t210_launch_contract_when_present() -> None:
    path = ANALYSIS / "t210_colab_cli_launch_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T210_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert value["session"]["accelerator"] == "L4"
    assert value["session"]["count"] == 1
    assert value["recovery"]["retry"] is False
    assert value["recovery"]["same_run_resume"] is False
    assert value["authority"]["behavior_evaluation"] is False
    assert value["authority"]["gate5"] is False
