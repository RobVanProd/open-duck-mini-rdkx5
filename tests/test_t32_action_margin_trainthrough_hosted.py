from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRIVER = (
    ROOT / "tools" / "colab_t32_action_margin_trainthrough_continuation.py"
)
PREREGISTRATION = (
    ROOT
    / "outputs"
    / "analysis"
    / "t32_action_margin_trainthrough_hosted_preregistration.json"
)
PACKAGE_CONTRACT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t32_action_margin_trainthrough_hosted_package_contract.json"
)
LAUNCH_CONTRACT = (
    ROOT / "outputs" / "analysis" / "t32_colab_cli_launch_contract.json"
)
HOLD_ATTRIBUTION = (
    ROOT
    / "outputs"
    / "analysis"
    / "t32_preexecution_identity_hold_attribution.json"
)
RECOVERY_CONTRACT = (
    ROOT / "outputs" / "analysis" / "t32b_colab_cli_recovery_contract.json"
)
RECOVERED_VALIDATION = (
    ROOT / "outputs" / "analysis" / "t32_recovered_training_validation.json"
)
T31_RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t31_action_margin_trainthrough_cpu_result.json"
)


def test_t31_is_the_only_t32_hosted_preregistration_authority() -> None:
    value = json.loads(T31_RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
    )
    assert value["decision"] == (
        "EARN_T31_HOSTED_CONTINUATION_PREREGISTRATION"
    )
    assert value["failed_checks"] == []
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t32_driver_freezes_one_persistent_continuation() -> None:
    text = DRIVER.read_text(encoding="utf-8")
    assert "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in text
    assert '"2007040"' in text
    assert '"--winner_t19_support_trainthrough"' in text
    assert '"--winner_t31_action_margin_trainthrough"' in text
    assert '"--ppo_num_envs"' in text and '"256"' in text
    assert '"--ppo_episode_length"' in text and '"600"' in text
    assert "no-retry path exists" in text


def test_t32_preregistration_has_no_behavior_or_robot_authority() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T32_ACTION_MARGIN_TRAINTHROUGH_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["exports"] == [0, 1_003_520, 2_007_040]
    assert value["training"]["action_margin_trainthrough"]
    assert not value["training"]["retry"]
    assert not value["training"]["resume"]
    assert not value["authority"]["additional_training_or_retry"]
    assert not value["authority"]["behavior_evaluation_after_valid_artifact"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
    assert not value["authority"]["torque_or_motion"]


def test_t32_package_is_the_only_training_authority() -> None:
    value = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T32_ACTION_MARGIN_TRAINTHROUGH_HOSTED_PACKAGE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["authority"]["one_hash_exact_hosted_continuation"]
    assert not value["authority"]["retry_or_resume"]
    assert not value["authority"]["behavior_evaluation"]
    assert not value["authority"]["checkpoint_selection"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t32_launch_contract_is_one_l4_without_retry() -> None:
    value = json.loads(LAUNCH_CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T32_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["session"]["accelerator"] == "L4"
    assert value["session"]["count"] == 1
    assert value["authority"]["one_exact_cli_launch"]
    assert not value["authority"]["additional_attempt"]
    assert not value["authority"]["behavior_evaluation"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t32_identity_hold_is_zero_step_and_exactly_attributed() -> None:
    value = json.loads(HOLD_ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T32_PREEXECUTION_IDENTITY_HOLD_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert value["identity"]["mismatch_names"] == ["DRIVER_SHA256"]
    assert value["attempt"]["failed_before_dependency_install"]
    assert value["attempt"]["failed_before_training_driver"]
    assert value["attempt"]["optimizer_steps"] == 0
    assert value["attempt"]["formal_behavior_cells"] == 0
    assert value["attempt"]["session_stopped"]


def test_t32b_recovery_changes_only_the_truncated_hash() -> None:
    value = json.loads(RECOVERY_CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T32B_COLAB_CLI_RECOVERY_CONTRACT"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["correction"]["field"] == "DRIVER_SHA256"
    assert value["correction"]["before_hex_chars"] == 62
    assert value["correction"]["after_hex_chars"] == 64
    assert not value["correction"]["package_change"]
    assert not value["correction"]["training_change"]
    assert value["authority"]["one_exact_preexecution_recovery"]
    assert not value["authority"]["additional_attempt"]


def test_t32_recovered_training_passes_cpu_topology_validation() -> None:
    value = json.loads(RECOVERED_VALIDATION.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T32_RECOVERED_TRAINING_VALIDATION"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["classification"]["training_completed"]
    assert not value["classification"]["training_retry"]
    assert not value["classification"]["training_resume"]
    assert value["classification"]["action_margin_trainthrough"]
    assert value["classification"]["behavior_cells"] == 0
    assert value["authority"]["postexport_transform_preregistration_authorized"]
    assert not value["authority"]["behavior_evaluation_authorized"]
    assert not value["authority"]["gate5_authorized"]
    assert not value["authority"]["rdkx5_or_robot"]
