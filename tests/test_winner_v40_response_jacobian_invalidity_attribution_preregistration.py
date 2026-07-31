from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs/analysis/winner_v40_response_jacobian_invalidity_attribution_preregistration.json"
)


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION"
    )
    assert value["decision"] == (
        "AUTHORIZE_ONE_SAVED_RESULT_ONLY_V39_INVALIDITY_ATTRIBUTION"
    )
    assert value["audit"] == {
        "source_status": "INVALID_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY",
        "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "response_horizon_ticks": 8,
        "maximum_terminal_fringe_ticks": 2,
        "expected_source_cells": 2,
        "expected_source_support_passes": 0,
        "expected_source_terminal_ticks": [32, 31],
        "expected_v38_terminal_ticks": [69, 161],
    }
    assert all(value["pass_rule"].values())
    assert value["execution_now"] == {
        "saved_result_audits": 0,
        "simulation_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["v39_rerun_authorized"] is False


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
