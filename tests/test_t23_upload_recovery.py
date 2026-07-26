from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_first_t23_session_is_a_zero_weight_preexecution_hold() -> None:
    value = load("t23_upload_transport_hold_attribution.json")
    assert value["status"] == (
        "PASS_T23_UPLOAD_TRANSPORT_HOLD_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["attempt"]["upload_returncode"] == 1
    assert value["attempt"]["upload_completed"] is False
    assert value["attempt"]["executor_started"] is False
    assert value["attempt"]["optimizer_steps"] == 0
    assert value["attempt"]["simulator_locomotion_steps"] == 0
    assert value["attempt"]["decision_weight"] == 0
    assert value["attempt"]["session_stopped"] is True
    assert value["discovered_package_inflation"]["files"] == 2_638
    assert (
        value["discovered_package_inflation"]["uncompressed_bytes"]
        == 132_813_251
    )
    assert (
        value["discovered_package_inflation"]["caused_transport_reset"]
        == "NOT_ESTABLISHED"
    )


def test_t23_recovery_is_one_narrow_cache_free_transport_attempt() -> None:
    value = load("t23_upload_recovery_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T23_CACHE_FREE_UPLOAD_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    correction = value["frozen_correction"]
    assert correction["training_source"] == "BYTE_IDENTICAL"
    assert correction["source_checkpoint"] == "BYTE_IDENTICAL"
    assert correction["hosted_driver"] == "BYTE_IDENTICAL"
    assert correction["removed_path"] == "playground/.tmp"
    assert correction["upload_attempts_exact"] == 1
    assert correction["training_retry"] is False
    assert correction["training_resume"] is False
    assert value["authority"]["one_cache_free_transport_recovery"] is True
    assert value["authority"]["gate5"] is False


def test_recovery_package_is_cache_free_and_training_identical() -> None:
    value = load(
        "t23_support_trainthrough_hosted_package_recovery_contract.json"
    )
    assert value["status"] == (
        "PASS_T23_SUPPORT_TRAINTHROUGH_HOSTED_RECOVERY_PACKAGE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["checks"]["temporary_cache_excluded"] is True
    assert value["checks"]["training_payload_unchanged"] is True
    assert value["recovery"]["excluded_path"] == "playground/.tmp"
    assert value["recovery"]["training_retry"] is False
    assert value["authority"]["gate5"] is False


def test_t23b_launch_is_one_exact_cache_free_colab_session() -> None:
    value = load("t23_colab_cli_recovery_contract.json")
    assert value["status"] == (
        "PASS_T23B_COLAB_CLI_RECOVERY_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["package_bytes"] == 3_408_121
    assert value["session"]["fresh_session_count"] == 1
    assert (
        value["session"]["prior_preexecution_transport_session_count"]
        == 1
    )
    assert value["recovery"]["cache_free_package"] is True
    assert value["recovery"]["training_payload_unchanged"] is True
    assert value["recovery"]["retry"] is False
    assert value["recovery"]["resume"] is False
    assert value["authority"]["one_exact_cache_free_cli_launch"] is True
    assert value["authority"]["behavior_evaluation"] is False
    assert value["authority"]["gate5"] is False
