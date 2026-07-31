from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t60_t59_persistence_hold_attribution.json"
)


def test_t60_attributes_transition_consolidation_gap() -> None:
    if not RESULT.exists():
        pytest.skip("T60 attribution has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T60_T59_PERSISTENCE_HOLD_ATTRIBUTION"
    )
    assert value["decision"] == (
        "EARN_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT_"
        "PREREGISTRATION_ONLY"
    )
    assert value["classification"] == (
        "ABRUPT_TRANSFER_CONSOLIDATION_GAP"
    )
    assert value["failed_checks"] == []
    summary = value["summary"]
    assert summary["green_cells"] == 10
    assert summary["half_x0_green"] == 2
    assert summary["half_moving_green"] == 0
    assert summary["final_green"] == 8
    assert summary["half_velocity_command_ratio"]["minimum"] > 1.0
    assert (
        summary["final_velocity_command_ratio"]["maximum"]
        < summary["half_velocity_command_ratio"]["minimum"]
    )
    successor = value["successor_constraints"]
    assert successor["midpoint_formula"] == (
        "support_reward + 0.5 * complete_frozen_locomotion_reward"
    )
    assert not successor["hosted_training_authorized"]
    assert value["authority"]["t61_cpu_contract_preregistration"]
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]
