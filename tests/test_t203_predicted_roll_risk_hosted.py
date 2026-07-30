from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t203_driver_changes_only_training_objective_flag() -> None:
    text = (
        ROOT
        / "tools"
        / "colab_t203_predicted_roll_risk_continuation.py"
    ).read_text(encoding="utf-8")
    assert "--winner_t202_predicted_roll_risk" in text
    assert "--winner_t193_corrected_dynamic_reference_support" not in text
    assert '"support_objective": False' in text
    assert '"deployment_graph_change": False' in text
    assert '"retry": False' in text
    assert '"same_run_resume": False' in text


def test_t203_preregistration_when_present() -> None:
    path = ANALYSIS / "t203_predicted_roll_risk_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T203_PREDICTED_ROLL_RISK_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["timesteps"] == 2_007_040
    assert value["training"]["exports"] == [0, 1_003_520, 2_007_040]
    assert value["training"]["passing_envelope_rad"] == 0.3541802655745987
    assert value["training"]["support_objective"] is False
    assert value["training"]["retry"] is False
    assert value["training"]["same_run_resume"] is False
    assert value["authority"]["checkpoint_selection"] is False
    assert value["authority"]["gate5"] is False


def test_t203_package_contract_when_present() -> None:
    path = (
        ANALYSIS / "t203_predicted_roll_risk_hosted_package_contract.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PASS_T203_PREDICTED_ROLL_RISK_HOSTED_PACKAGE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions_opened"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0


def test_t203_launch_contract_when_present() -> None:
    path = ANALYSIS / "t203_colab_cli_launch_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T203_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert value["session"]["accelerator"] == "L4"
    assert value["session"]["count"] == 1
    assert value["recovery"]["retry"] is False
    assert value["recovery"]["same_run_resume"] is False
    assert value["authority"]["behavior_evaluation"] is False
    assert value["authority"]["gate5"] is False
