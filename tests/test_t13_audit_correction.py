from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def test_t13_audit_correction_cannot_change_the_hold() -> None:
    value = json.loads(
        (
            ANALYSIS / "t13_audit_correction_amendment.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "amendment_contract_sha256"
    }
    assert canonical_sha256(basis) == value[
        "amendment_contract_sha256"
    ]
    unchanged = value["unchanged"]
    assert (
        unchanged["formal_status"]
        == "HOLD_T13_SHADOW_HIDDEN_RESPONSE_CONTRACT"
    )
    assert (
        unchanged["formal_decision"]
        == "CLOSE_EXISTING_RECURRENT_SHADOW_HANDOFF"
    )
    assert unchanged["failed_checks"] == [
        "both_plant_hidden_states_actionable"
    ]
    assert unchanged["behavior_authorization"] is False
    assert unchanged["training_authorization"] is False
    assert value["authority"] == {
        "simulator_cells": 0,
        "scored_behavior_cells": 0,
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }
