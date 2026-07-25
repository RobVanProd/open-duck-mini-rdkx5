from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v127_cpu_preregistration_freezes_the_selected_mechanism() -> None:
    value = load("winner_v127_constrained_cpu_preregistration.json")
    assert (
        value["status"]
        == "PREREGISTERED_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["objective"]["cost_added_to_reward"] is False
    assert value["objective"]["cost_discount"] == 1.0
    assert value["objective"]["actor_advantage"] == (
        "(A_R-lambda*A_C)/(1+lambda)"
    )
    assert value["dual"]["eta"] == "1/(ceil(K/4)*J_C0)"
    assert value["dual"]["J_C0"] == (
        "first positive continuation rollout batch cost, used once"
    )
    assert value["dual"]["tunable_dual_scalars"] == 0
    assert value["hosted_gate"]["authorized_now"] is False
    assert value["hosted_gate"]["continuations"] == 1
    assert value["hosted_gate"]["retry_or_resume"] is False
    assert value["authority"]["cpu_contract_authorized"] is True
    assert value["authority"]["colab_authorized"] is False


def test_v127_restore_claim_matches_the_actual_checkpoint_boundary() -> None:
    restore = load("winner_v127_constrained_cpu_preregistration.json")[
        "restore_correction"
    ]
    assert restore["restored_bit_exact"] == [
        "normalizer",
        "policy",
        "reward-value critic",
    ]
    assert restore["not_present_in_source"] == [
        "optimizer state",
        "RNG state",
        "cost critic",
    ]
    assert restore["forbidden_claim"] == (
        "optimizer or RNG restored from V121"
    )


def test_v127_training_source_has_separate_cost_state() -> None:
    train = (
        ROOT / "training/winner_v127_constrained_ppo_train.py"
    ).read_text(encoding="utf-8")
    losses = (
        ROOT / "training/winner_v127_constrained_ppo_losses.py"
    ).read_text(encoding="utf-8")
    patch = (
        ROOT / "patches/winner_v127_constrained_cost_channel.patch"
    ).read_text(encoding="utf-8")
    assert "cost_value: Params" in losses
    assert "discount=1.0" in losses
    assert "reward_advantages - dual_lambda * cost_advantages" in losses
    assert "winner_v127_dual_update" in train
    assert "first_positive" in train
    assert "winner_v127_dense_torque_exceedance_cost" in patch
    assert '"winner_v127_dense_torque_exceedance_cost"' in patch
    assert "winner-v127 cost must remain outside the clipped reward" in patch


def test_v127_cpu_result_when_present_is_decisive() -> None:
    path = ANALYSIS / "winner_v127_constrained_cpu_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["decision"] == "EARN_ONE_V127_HOSTED_PREREGISTRATION"
    assert value["authority"]["hosted_preregistration_authorized"] is True
    assert value["authority"]["hosted_run_authorized"] is False
    assert value["authority"]["robot_or_rdk"] is False


def test_v127_hosted_contract_is_one_run_without_selection_authority() -> None:
    prereg = load("winner_v127_hosted_preregistration.json")
    package = load("winner_v127_hosted_package_contract.json")
    launch = load("winner_v127_colab_cli_launch_contract.json")
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V127_HOSTED_CONTINUATION"
    )
    assert prereg["failed_checks"] == []
    assert prereg["training"]["timesteps"] == 2_007_040
    assert prereg["training"]["exports"] == [0, 1_003_520, 2_007_040]
    assert prereg["training"]["old_squared_torque_scale"] == 0.0
    assert prereg["training"]["old_linear_torque_scale"] == 0.0
    assert prereg["training"]["dual_scalars_searched"] == 0
    assert prereg["training"]["retry"] is False
    assert prereg["training"]["resume"] is False
    assert prereg["authority"]["behavior_evaluation"] is False
    assert package["status"] == "PASS_WINNER_V127_HOSTED_PACKAGE"
    assert package["failed_checks"] == []
    assert package["authority"]["one_hash_exact_hosted_continuation"] is True
    assert launch["status"] == "PASS_WINNER_V127_COLAB_CLI_LAUNCH_CONTRACT"
    assert launch["failed_checks"] == []
    assert launch["session"]["accelerator"] == "L4"
    assert launch["session"]["count"] == 1
    assert launch["authority"]["one_exact_cli_launch"] is True
    assert launch["authority"]["behavior_evaluation"] is False


def test_v127_chunked_transport_preserves_the_frozen_training_payload() -> None:
    correction = load("winner_v127_upload_transport_correction.json")
    launch = load("winner_v127b_chunked_colab_launch_contract.json")
    assert correction["status"] == (
        "PASS_WINNER_V127_UPLOAD_TRANSPORT_CORRECTION"
    )
    assert correction["failed_checks"] == []
    assert correction["checks"]["training_payload_unchanged"] is True
    assert correction["prior_prelaunch_attempt"]["executor_started"] is False
    assert correction["prior_prelaunch_attempt"]["optimizer_steps"] == 0
    assert correction["prior_prelaunch_attempt"]["session_stopped"] is True
    assert len(correction["chunks"]) == 4
    assert correction["reconstruction"]["sha256"] == (
        correction["package"]["sha256"]
    )
    assert launch["status"] == (
        "PASS_WINNER_V127B_CHUNKED_COLAB_LAUNCH_CONTRACT"
    )
    assert launch["failed_checks"] == []
    assert launch["authority"]["one_exact_chunked_cli_launch"] is True
    assert launch["authority"]["training_retry"] is False
    assert launch["authority"]["training_resume"] is False


def test_v127c_is_a_pretraining_path_correction_not_a_training_retry() -> None:
    correction = load("winner_v127_pretraining_launch_correction.json")
    prereg = load("winner_v127c_hosted_preregistration.json")
    launch = load("winner_v127c_colab_launch_contract.json")
    assert correction["status"] == (
        "PASS_WINNER_V127_PRETRAINING_LAUNCH_CORRECTION"
    )
    assert correction["failed_checks"] == []
    assert correction["checks"]["optimizer_steps_zero"] is True
    assert correction["checks"]["simulator_locomotion_steps_zero"] is True
    assert correction["correction"]["training_command_unchanged"] is True
    assert correction["correction"]["old"] != correction["correction"]["new"]
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V127C_HOSTED_CONTINUATION"
    )
    assert prereg["failed_checks"] == []
    assert prereg["training"]["retry"] is False
    assert prereg["training"]["resume"] is False
    assert launch["status"] == "PASS_WINNER_V127C_COLAB_LAUNCH_CONTRACT"
    assert launch["failed_checks"] == []
    assert launch["authority"]["one_corrected_exact_cli_launch"] is True
    assert launch["authority"]["training_retry"] is False
