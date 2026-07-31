from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v41_v2_runner_correction_preregistration.json"


def test_correction_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V41_V2_RUNNER_CORRECTION"
    assert value["decision"] == "AUTHORIZE_ONE_CORRECTED_CPU_ONLY_V41_SCREEN"
    assert value["correction"] == {
        "old_call": "v38.expand_mirrored_blocks(coordinates[None, :])",
        "new_call": "coordinates @ v38.MIRROR_MATRIX.T into the same six indices",
        "changed_behavior": "accept exactly one three-coordinate static target",
        "unchanged_behavior": (
            "grid, basis, action boundary, plants, duration, selection, pass rule, "
            "execution counts, and authority"
        ),
    }
    assert value["first_attempt"]["github_run"]["run_id"] == 29901924055
    assert value["first_attempt"]["artifact_count"] == 0
    assert value["first_attempt"]["work_executed"]["candidate_plant_cells"] == 0
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
