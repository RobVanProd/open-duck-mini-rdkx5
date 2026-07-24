import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v122_hosted_prereg_is_one_no_retry_continuation() -> None:
    value = load("winner_v122_hosted_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_WINNER_V122_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    training = value["training"]
    assert training["source"] == "exact_v119_half_checkpoint"
    assert training["exports"] == [0, 1_003_520, 2_007_040]
    assert training["linear_peak_torque_scale"] == 0.0
    assert training["episode_peak_torque_increment_scale"] < 0.0
    assert training["retry"] is False
    assert training["resume"] is False
    assert training["scalar_sweep"] is False
    assert value["post_training"][
        "both_postupdate_checkpoints_must_pass"
    ] is True
    assert value["authority"][
        "one_hosted_gpu_continuation_after_package_contract"
    ] is True
    assert value["authority"]["additional_training_or_retry"] is False
    assert value["authority"]["gate5"] is False


def test_v122_package_contract_contains_no_behavior_authority() -> None:
    value = load("winner_v122_hosted_package_contract.json")
    assert value["status"] == "PASS_WINNER_V122_HOSTED_PACKAGE"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["archive"]["bytes"] > 0
    assert len(value["archive"]["sha256"]) == 64
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["authority"]["one_hash_exact_hosted_continuation"] is True
    assert value["authority"]["retry_or_resume"] is False
    assert value["authority"]["behavior_evaluation"] is False
    assert value["authority"]["gate5"] is False


def test_v122_colab_launch_is_exactly_one_l4_without_retry() -> None:
    value = load("winner_v122_colab_cli_launch_contract.json")
    assert value["status"] == (
        "PASS_WINNER_V122_COLAB_CLI_LAUNCH_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["session"]["accelerator"] == "L4"
    assert value["session"]["count"] == 1
    assert value["recovery"]["retry"] is False
    assert value["recovery"]["resume"] is False
    assert value["execution_now"]["colab_sessions_opened"] == 0
    assert value["authority"]["one_exact_cli_launch"] is True
    assert value["authority"]["additional_attempt"] is False
    assert value["authority"]["behavior_evaluation"] is False
    assert value["authority"]["gate5"] is False
