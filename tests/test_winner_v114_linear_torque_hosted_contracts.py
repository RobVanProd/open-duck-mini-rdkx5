import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v114_preregistration_freezes_one_earned_continuation() -> None:
    value = load("winner_v114_linear_torque_hosted_preregistration.json")
    assert (
        value["status"]
        == "PREREGISTERED_WINNER_V114_LINEAR_TORQUE_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["training"]["source"] == "exact_v112_final_checkpoint"
    assert value["training"]["timesteps"] == 2_007_040
    assert value["training"]["exports"] == [0, 1_003_520, 2_007_040]
    assert value["training"]["linear_peak_torque_scale"] == (
        -307.48131091308585
    )
    assert value["training"]["squared_peak_torque_scale"] == 0.0
    assert value["training"]["scalar_sweep"] is False
    assert value["training"]["retry"] is False
    assert value["training"]["resume"] is False
    assert value["post_training"]["both_postupdate_checkpoints_must_pass"]
    assert value["authority"]["gate5"] is False
    assert value["authority"]["rdkx5_or_robot"] is False


def test_v114_package_is_hash_frozen_and_offline() -> None:
    value = load("winner_v114_linear_torque_hosted_package_contract.json")
    assert value["status"] == (
        "PASS_WINNER_V114_LINEAR_TORQUE_HOSTED_PACKAGE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["archive"]["bytes"] == 64_522_613
    assert value["archive"]["sha256"] == (
        "3f64c637f4395f7b131da6d252b4d3001aff62d65c23015f5708b6b059f4ddd5"
    )
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["authority"]["one_hash_exact_hosted_continuation"] is True
    assert value["authority"]["gate5"] is False
    assert value["authority"]["rdkx5_or_robot"] is False


def test_v114_launch_contract_allows_one_l4_session_only() -> None:
    value = load("winner_v114_colab_cli_launch_contract.json")
    assert value["status"] == (
        "PASS_WINNER_V114_COLAB_CLI_LAUNCH_CONTRACT"
    )
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
