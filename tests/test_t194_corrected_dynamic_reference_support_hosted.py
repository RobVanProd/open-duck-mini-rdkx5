from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t194_driver_changes_only_training_objective_flag() -> None:
    text = (
        ROOT
        / "tools"
        / "colab_t194_corrected_dynamic_reference_support_"
        "continuation.py"
    ).read_text(encoding="utf-8")
    assert "--winner_t193_corrected_dynamic_reference_support" in text
    assert "--winner_t185_in_episode_single_support_prefix" not in text
    assert "phase_heuristic" in text
    assert '"retry": False' in text
    assert '"same_run_resume": False' in text


def test_t194_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t194_corrected_dynamic_reference_support_hosted_"
        "preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
        "HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["timesteps"] == 2_007_040
    assert value["training"]["exports"] == [0, 1_003_520, 2_007_040]
    assert value["training"]["reference_contact_channels"] == [32, 34]
    assert value["training"]["phase_sign_heuristic"] is False
    assert value["training"]["retry"] is False
    assert value["training"]["same_run_resume"] is False
    assert value["authority"]["checkpoint_selection"] is False
    assert value["authority"]["gate5"] is False


def test_t194_package_contract_when_present() -> None:
    path = (
        ANALYSIS
        / "t194_corrected_dynamic_reference_support_hosted_"
        "package_contract.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PASS_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_HOSTED_PACKAGE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["hosted_sessions_opened"] == 0
    assert value["execution_now"]["robot_or_rdk_access"] == 0


def test_t194_launch_contract_when_present() -> None:
    path = ANALYSIS / "t194_colab_cli_launch_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T194_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["session"]["accelerator"] == "L4"
    assert value["session"]["count"] == 1
    assert value["recovery"]["retry"] is False
    assert value["recovery"]["same_run_resume"] is False
    assert value["authority"]["behavior_evaluation"] is False
    assert value["authority"]["gate5"] is False
