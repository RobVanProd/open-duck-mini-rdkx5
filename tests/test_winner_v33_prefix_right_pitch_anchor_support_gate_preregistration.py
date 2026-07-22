from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v33_prefix_right_pitch_anchor_support_gate_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE"
    assert value["decision"] == "AUTHORIZE_ONE_FROZEN_WINNER_V33_248_CELL_GATE_ONLY"
    assert value["future_frozen_support_gate"]["cells_per_checkpoint"] == 124
    assert value["future_frozen_support_gate"]["checkpoint_labels"] == ["half", "final"]
    assert value["pass_rule"]["closest_checkpoint_selection"] is False
    assert value["execution_now"] == {
        "formal_support_cells": 0,
        "heldout_repeat_cells": 0,
        "locomotion_steps": 0,
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
