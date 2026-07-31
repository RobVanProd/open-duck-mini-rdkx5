from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v34_prefix_right_pitch_hard_intervention_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_UPDATE_DIRECT_PREFIX_INTERVENTION_ONLY"
    assert value["diagnostic"]["arms"] == {
        "CONTROL": [],
        "RIGHT_PITCH_REPLACED": [11, 12, 13],
    }
    assert value["diagnostic"]["replacement_ticks"] == list(range(8))
    assert value["diagnostic"]["duration_ticks"] == 250
    assert value["diagnostic"]["expected_cells"] == 120
    assert value["diagnostic"]["control_scalar_float_atol"] == 1.0e-12
    assert value["pass_rule"]["all_60_replacement_cells_pass_support"] is True
    assert value["pass_rule"]["closest_result_selection"] is False
    assert value["execution_now"] == {
        "control_cells": 0,
        "replacement_cells": 0,
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
