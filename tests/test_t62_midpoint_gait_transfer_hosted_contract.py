from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs"
    / "analysis"
    / "t62_midpoint_gait_transfer_hosted_preregistration.json"
)
PACKAGE = (
    ROOT
    / "outputs"
    / "analysis"
    / "t62_midpoint_gait_transfer_hosted_package_contract.json"
)
LAUNCH = (
    ROOT / "outputs" / "analysis" / "t62_colab_cli_launch_contract.json"
)


def test_t62_hosted_preregistration_is_one_frozen_sequence() -> None:
    if not PREREG.exists():
        pytest.skip("T62 hosted continuation has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    training = value["training"]
    assert training["session_count"] == 1
    assert training["midpoint_stage"]["timesteps"] == 1_003_520
    assert training["transfer_stage"]["timesteps"] == 2_007_040
    assert training["transfer_stage"]["exports"] == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert not training["retry"]
    assert not training["scalar_sweep"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t62_package_is_hash_frozen_and_offline() -> None:
    if not PACKAGE.exists():
        pytest.skip("T62 hosted package has not been built")
    value = json.loads(PACKAGE.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_PACKAGE"
    )
    assert value["failed_checks"] == []
    assert value["authority"]["one_hash_exact_hosted_continuation"]
    assert not value["authority"]["retry_or_resume"]
    assert not value["authority"]["gate5"]


def test_t62_launch_contract_opens_only_one_session() -> None:
    if not LAUNCH.exists():
        pytest.skip("T62 Colab launch has not been frozen")
    value = json.loads(LAUNCH.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T62_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert value["session"]["count"] == 1
    assert value["session"]["accelerator"] == "L4"
    assert not value["recovery"]["retry"]
    assert not value["recovery"]["resume"]
    assert not value["authority"]["gate5"]
