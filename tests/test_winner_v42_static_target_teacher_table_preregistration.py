from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v42_static_target_teacher_table_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
    assert value["decision"] == "AUTHORIZE_ONE_CPU_ONLY_15_CONFIGURATION_TEACHER_TABLE"
    screen = value["screen"]
    assert len(screen["configuration_ids"]) == 15
    assert screen["targets_per_configuration"] == 729
    assert screen["maximum_candidate_plant_cells"] == 21_870
    assert screen["duration_ticks"] == 250
    assert value["pass_rule"]["closest_result_selection"] is False
    assert value["execution_now"] == {
        "configuration_tables": 0,
        "static_target_candidates": 0,
        "candidate_plant_cells": 0,
        "selected_target_replay_cells": 0,
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
