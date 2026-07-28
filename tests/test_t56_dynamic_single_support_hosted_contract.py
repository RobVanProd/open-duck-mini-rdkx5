from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs"
    / "analysis"
    / "t56_dynamic_single_support_hosted_preregistration.json"
)
PACKAGE = (
    ROOT
    / "outputs"
    / "analysis"
    / "t56_dynamic_single_support_hosted_package_contract.json"
)
LAUNCH = (
    ROOT / "outputs" / "analysis" / "t56_colab_cli_launch_contract.json"
)


def test_t56_hosted_preregistration_is_one_frozen_sequence() -> None:
    if not PREREG.exists():
        pytest.skip("T56 hosted continuation has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T56_DYNAMIC_SINGLE_SUPPORT_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["session_count"] == 1
    assert value["training"]["balance_stage"]["timesteps"] == 1_003_520
    assert value["training"]["transfer_stage"]["timesteps"] == 2_007_040
    assert value["training"]["transfer_stage"]["exports"] == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert not value["training"]["retry"]
    assert not value["training"]["scalar_sweep"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t56_package_is_hash_frozen_and_offline() -> None:
    if not PACKAGE.exists():
        pytest.skip("T56 hosted package has not been built")
    value = json.loads(PACKAGE.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T56_DYNAMIC_SINGLE_SUPPORT_HOSTED_PACKAGE"
    )
    assert value["failed_checks"] == []
    assert value["authority"]["one_hash_exact_hosted_continuation"]
    assert not value["authority"]["retry_or_resume"]
    assert not value["authority"]["gate5"]


def test_t56_launch_contract_opens_only_one_session() -> None:
    if not LAUNCH.exists():
        pytest.skip("T56 Colab launch has not been frozen")
    value = json.loads(LAUNCH.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T56_COLAB_CLI_LAUNCH_CONTRACT"
    assert value["failed_checks"] == []
    assert value["session"]["count"] == 1
    assert value["session"]["accelerator"] == "L4"
    assert not value["recovery"]["retry"]
    assert not value["recovery"]["resume"]
    assert not value["authority"]["gate5"]
