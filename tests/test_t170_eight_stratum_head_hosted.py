import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t170_hosted_preregistration_contract() -> None:
    path = ANALYSIS / "t170_eight_stratum_head_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["body_configuration_strata"] == 8
    assert value["training"]["environments_per_stratum"] == 32
    assert value["training"]["actor_trainable_groups"] == [
        "negative_adapter_location"
    ]
    assert value["training"]["retry"] is False
    assert value["training"]["same_run_resume"] is False
    assert value["post_training"]["both_checkpoint_persistence_required"]


def test_t170_package_contract() -> None:
    path = ANALYSIS / "t170_eight_stratum_head_hosted_package_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T170_EIGHT_STRATUM_HEAD_HOSTED_PACKAGE"
    assert value["failed_checks"] == []
    assert value["checks"]["eight_stratum_readback_frozen"]
    assert value["checks"]["credentials_absent"]
    assert value["checks"]["robot_access_material_absent"]
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions_opened"] == 0


def test_t170_package_preflight_handles_split_readback_literal() -> None:
    text = (
        ROOT / "tools/build_t170_eight_stratum_head_hosted_package.py"
    ).read_text(encoding="utf-8")
    assert "'T98_HIDDEN_EXPERT_CONTINUATION=' in runner" in text
    assert "'strata=8,broad=1,isolated=7,' in runner" in text
    assert "'gate=fixed_live_hidden,' in runner" in text


def test_t170_launch_contract() -> None:
    path = ANALYSIS / "t170_colab_cli_launch_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T170_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert value["session"]["accelerator"] == "L4"
    assert value["session"]["count"] == 1
    assert value["recovery"]["retry"] is False
    assert value["recovery"]["same_run_resume"] is False
    assert value["execution_now"]["colab_sessions_opened"] == 0


def test_t170_executor_is_one_shot_and_robot_free() -> None:
    text = (ROOT / "tools/execute_t170_colab_cli.py").read_text(
        encoding="utf-8"
    )
    assert "PASS_T170_HOSTED_FULL_PREFLIGHT" in text
    assert '"retry": False' in text
    assert '"same_run_resume": False' in text
    assert '"robot_or_rdk_access": False' in text
    assert "T170 no-retry path exists" in text
