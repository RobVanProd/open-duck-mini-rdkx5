from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t78_preregistration_is_green_when_present() -> None:
    path = (
        ANALYSIS / "t78_endpoint_joint_adapter_hosted_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T78_ENDPOINT_JOINT_ADAPTER_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["endpoint_strata"] == 8
    assert value["training"]["environments_per_stratum"] == 32
    assert value["training"]["actor_trainable_groups"] == [
        "adapter_obs_projection",
        "adapter_hidden_projection",
        "adapter_hidden_bias",
        "adapter_location",
    ]
    assert value["training"]["reward_change"] is False
    assert value["training"]["policy_abi_change"] is False
    assert value["training"]["runtime_change"] is False
    assert value["training"]["retry"] is False
    assert value["training"]["resume"] is False
    assert value["post_training"]["both_postupdate_checkpoints_must_pass"]


def test_t78_driver_is_exact_no_retry_two_checkpoint_run() -> None:
    text = (
        ROOT
        / "tools"
        / "colab_t78_endpoint_joint_adapter_continuation.py"
    ).read_text(encoding="utf-8")
    assert "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in text
    assert '"--winner_t77_endpoint_joint_adapter_continuation"' in text
    assert '"--winner_t37_freeze_observation_normalizer"' in text
    assert "no-retry path exists" in text
    assert "formal_behavior_cells_executed" in text


def test_t78_package_and_launch_contracts_are_green_when_present() -> None:
    package_path = (
        ANALYSIS
        / "t78_endpoint_joint_adapter_hosted_package_contract.json"
    )
    launch_path = ANALYSIS / "t78_colab_cli_launch_contract.json"
    if package_path.exists():
        package = json.loads(package_path.read_text(encoding="utf-8"))
        assert package["status"] == (
            "PASS_T78_ENDPOINT_JOINT_ADAPTER_HOSTED_PACKAGE"
        )
        assert package["failed_checks"] == []
        assert package["authority"]["retry_or_resume"] is False
    if launch_path.exists():
        launch = json.loads(launch_path.read_text(encoding="utf-8"))
        assert launch["status"] == "PASS_T78_COLAB_CLI_LAUNCH_CONTRACT"
        assert launch["failed_checks"] == []
        assert launch["session"]["accelerator"] == "L4"
        assert launch["recovery"]["retry"] is False
        assert launch["recovery"]["resume"] is False


def test_t78_recovery_validation_is_green_when_present() -> None:
    path = ANALYSIS / "t78_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T78_RECOVERED_TRAINING_VALIDATION"
    assert value["failed_checks"] == []
    assert value["classification"]["actor_update_scope"] == (
        "complete_recurrent_adapter"
    )
    assert value["classification"]["behavior_cells"] == 0
