from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v35_full_horizon_source_continuation_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_UPDATE_FULL_HORIZON_SOURCE_CONTINUATION_ONLY"
    diagnostic = value["diagnostic"]
    assert diagnostic["prefix_ticks"] == list(range(8))
    assert diagnostic["prefix_replaced_action_indices"] == [11, 12, 13]
    assert diagnostic["source_continuation_ticks"] == {"first": 8, "last": 249}
    assert diagnostic["duration_ticks"] == 250
    assert diagnostic["expected_hybrid_cells"] == 60
    assert value["pass_rule"]["all_60_hybrid_cells_pass_support"] is True
    assert value["pass_rule"]["closest_result_selection"] is False
    assert value["execution_now"] == {
        "hybrid_support_cells": 0,
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
