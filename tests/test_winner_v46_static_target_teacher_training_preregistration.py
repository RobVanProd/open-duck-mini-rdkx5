from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v46_static_target_teacher_training_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING"
    assert value["decision"] == "AUTHORIZE_ONE_100_UPDATE_STATIC_TARGET_TEACHER_ARM_ONLY"
    assert value["frozen_training"]["source_completed_updates"] == 252
    assert value["frozen_training"]["persistent_checkpoints"] == {"half": 302, "final": 352}
    assert value["frozen_training"]["static_target_teacher_scale"] == 58.436370849609375
    assert value["objective"]["static_target_teacher"]["heldout_ids_excluded"] == [
        "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15",
    ]
    assert value["execution_now"] == {
        "optimizer_updates": 0, "formal_support_cells": 0,
        "locomotion_steps": 0, "robot_or_rdk_access": 0,
    }


def test_source_manifest_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256((ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
    canonical = hashlib.sha256(json.dumps(value["sources"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert canonical == value["source_manifest_sha256"]


def test_workflow_is_first_attempt_cpu_only() -> None:
    source = (ROOT / ".github/workflows/winner-v46-static-target-teacher-training.yml").read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v46_static_target_teacher_training_preregistration.json" in trigger
    assert "workflow_dispatch" not in trigger
    assert 'test "${{ github.run_attempt }}" = "1"' in source
    assert "--offline-cpu-only" in source
    assert "--static-target-teacher-training-authorized" in source
    assert "--hardware-authorized" not in source

