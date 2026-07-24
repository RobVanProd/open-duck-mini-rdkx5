import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v112_preregistration_freezes_one_continuation() -> None:
    value = load("winner_v112_peak_torque_hosted_preregistration.json")
    assert (
        value["status"]
        == "PREREGISTERED_WINNER_V112_PEAK_TORQUE_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["training"]["timesteps"] == 2_007_040
    assert value["training"]["exports"] == [0, 1_003_520, 2_007_040]
    assert value["training"]["peak_torque_exceedance_scale"] == -1000.0
    assert value["training"]["retry"] is False
    assert value["training"]["resume"] is False
    assert value["post_training"]["both_postupdate_checkpoints_must_pass"]
    assert value["authority"]["gate5"] is False
    assert value["authority"]["rdkx5_or_robot"] is False


def test_v112_package_contract_is_offline_and_hash_frozen() -> None:
    value = load("winner_v112_peak_torque_hosted_package_contract.json")
    assert value["status"] == "PASS_WINNER_V112_PEAK_TORQUE_HOSTED_PACKAGE"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["archive"]["bytes"] == 51_971_655
    assert (
        value["archive"]["sha256"]
        == "f39bea69840436b5ca8cc2a3000b6006ceaac1fa403588c94024e6caa5709401"
    )
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["authority"]["one_hash_exact_hosted_continuation"] is True
    assert value["authority"]["gate5"] is False
    assert value["authority"]["rdkx5_or_robot"] is False


def test_v112_launch_contract_allows_one_l4_session_only() -> None:
    value = load("winner_v112_colab_cli_launch_contract.json")
    assert value["status"] == "PASS_WINNER_V112_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["session"]["accelerator"] == "L4"
    assert value["session"]["count"] == 1
    assert value["recovery"]["retry"] is False
    assert value["recovery"]["resume"] is False
    assert value["authority"]["one_exact_cli_launch"] is True
    for name in (
        "additional_attempt",
        "behavior_evaluation",
        "checkpoint_selection",
        "deployment",
        "gate5",
        "rdkx5_or_robot",
        "robot_clearance",
    ):
        assert value["authority"][name] is False
