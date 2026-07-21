from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v20_two_stage_authority_correction.json"


def canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def test_two_stage_authority_correction_is_exact() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V20_TWO_STAGE_AUTHORITY_CORRECTED_PRE_OUTCOME"
    )
    assert value["decision"] == "CALIBRATOR_GATE_CANNOT_SELECT_A_DEPLOYMENT_POLICY"
    assert value["execution"] == {
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "behavior_cells": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"] == {
        "robot_clearance": False,
        "deployment_checkpoint_selected": False,
        "calibrator_is_deployable_walking_policy": False,
        "no_manual_mass_com_inertia_measurements": True,
    }
    assert value["source_manifest_sha256"] == canonical_sha256(value["sources"])
    for item in value["sources"].values():
        path = ROOT / item["path"]
        observed = hashlib.sha256(
            path.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item == {
            "path": item["path"],
            "hash_mode": "lf",
            "sha256": observed,
        }
