from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v38_mirrored_pitch_shooting_feasibility_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V38_MIRRORED_PITCH_SHOOTING_FEASIBILITY"
    assert value["decision"] == "AUTHORIZE_ONE_CPU_ONLY_MIRRORED_PITCH_COM_X_NEG_SCREEN"
    screen = value["screen"]
    assert screen["configuration_ids"] == ["COM_X_NEG"]
    assert screen["controlled_action_indices"] == [2, 3, 4, 11, 12, 13]
    assert screen["search_dimensions_per_block"] == 3
    assert screen["mirror_basis"] == {
        "hip_pitch_magnitude": {"left_index_2": -1, "right_index_11": 1},
        "knee": {"left_index_3": 1, "right_index_12": 1},
        "ankle": {"left_index_4": 1, "right_index_13": 1},
    }
    assert screen["duration_ticks"] == 250
    assert screen["horizon_ticks"] == 8
    assert screen["action_block_ticks"] == 2
    assert screen["population"] == 64
    assert screen["elites"] == 8
    assert screen["iterations"] == 4
    assert screen["expected_cells"] == 2
    assert value["pass_rule"]["both_plants_pass_full_250_tick_support_gate"] is True
    assert value["pass_rule"]["closest_result_selection"] is False
    assert value["execution_now"] == {
        "oracle_support_cells": 0,
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
