from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v41_static_equilibrium_target_feasibility_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY"
    assert value["decision"] == "AUTHORIZE_ONE_CPU_ONLY_FULL_HORIZON_STATIC_TARGET_SCREEN"
    screen = value["screen"]
    assert screen["configuration_ids"] == ["COM_X_NEG"]
    assert screen["actuator_plants"] == [
        "P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"
    ]
    assert screen["controlled_action_indices"] == [2, 3, 4, 11, 12, 13]
    assert screen["coordinate_order"] == ["hip_pitch_magnitude", "knee", "ankle"]
    assert screen["grid_values"] == [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
    assert screen["candidate_count"] == 729
    assert screen["duration_ticks"] == 250
    assert value["pass_rule"]["closest_result_selection"] is False
    assert value["execution_now"] == {
        "static_target_candidates": 0,
        "candidate_plant_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_source_manifest_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
    canonical = hashlib.sha256(
        json.dumps(value["sources"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert canonical == value["source_manifest_sha256"]
