from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING"
    assert value["decision"] == "AUTHORIZE_ONE_100_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_ARM_ONLY"
    frozen = value["frozen_training"]
    assert frozen["source_completed_updates"] == 201
    assert frozen["continuation_optimizer_updates"] == 100
    assert frozen["final_optimizer_count"] == 301
    assert frozen["anchor_scale"] == 197.3112030029297
    assert frozen["persistent_checkpoints"] == {"half": 251, "final": 301}
    assert value["execution_now"] == {
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["training_authorized"] is True


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
