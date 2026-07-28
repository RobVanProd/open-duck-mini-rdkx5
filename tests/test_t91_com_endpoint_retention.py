from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t91_com_endpoint_retention_preregistration.json"
RESULT = ANALYSIS / "t91_com_endpoint_retention_result.json"


def test_t91_preregistration_is_exact_and_bounded() -> None:
    if not PREREG.exists():
        pytest.skip("T91 preregistration has not been built")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC"
    )
    assert value["failed_checks"] == []
    assert value["condition"] == {
        "condition_index": 7,
        "id": "TORSO_COM_X_NEG",
        "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
    }
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"]
    assert not value["matrix"]["checkpoint_cherry_pick"]
    assert value["execution_now"] == {
        "formal_behavior_cells": 0,
        "hosted_compute_units": 0,
        "optimizer_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_t91_result_follows_the_frozen_decision() -> None:
    if not RESULT.exists():
        pytest.skip("formal T91 diagnostic has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC",
        "HOLD_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC",
    }
    assert value["summary"]["completed_cells"] == 16
    assert value["summary"]["green_cells"] <= 16
    passed = value["summary"]["all_sixteen_green"]
    assert value["interpretation"]["exact_exposed_endpoint_retained"] == passed
    assert value["decision"] == (
        "EARN_T92_FULL_R2_ENDPOINT_REPLAY_CPU_CONTRACT_"
        "PREREGISTRATION_ONLY"
        if passed
        else "CLOSE_EXACT_ENDPOINT_REPLAY_AS_SUFFICIENT_MECHANISM"
    )
    assert not value["interpretation"]["hosted_run_earned"]
