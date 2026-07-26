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


def test_t13_result_is_canonical_and_closes_the_handoff() -> None:
    value = json.loads(
        (
            ANALYSIS / "t13_shadow_hidden_result.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "result_sha256"
    }
    assert canonical_sha256(basis) == value["result_sha256"]
    assert (
        value["status"]
        == "HOLD_T13_SHADOW_HIDDEN_RESPONSE_CONTRACT"
    )
    assert (
        value["decision"]
        == "CLOSE_EXISTING_RECURRENT_SHADOW_HANDOFF"
    )
    assert value["failed_checks"] == [
        "both_plant_hidden_states_actionable"
    ]
    assert value["checks"]["all_cell_checks"] is True
    assert value["checks"]["both_plant_hidden_states_separate"] is True
    assert (
        value["checks"]["both_plant_hidden_states_actionable"]
        is False
    )
    assert value["execution"] == {
        "simulator_prefix_cells": 4,
        "scored_behavior_cells": 0,
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }


def test_t13_v2_audit_independently_reproduces_the_hold() -> None:
    value = json.loads(
        (
            ANALYSIS
            / "t13_shadow_hidden_independent_audit_v2.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "audit_sha256"
    }
    assert canonical_sha256(basis) == value["audit_sha256"]
    assert (
        value["status"]
        == "PASS_T13_SHADOW_HIDDEN_INDEPENDENT_AUDIT_V2"
    )
    assert (
        value["decision"]
        == "CLOSE_EXISTING_RECURRENT_SHADOW_HANDOFF"
    )
    assert value["issues"] == []
    assert value["recomputed_contract_failures"] == [
        "V121_TRAIN_MATCHED_HALF.plant_action_visibility"
    ]
    assert value["execution"] == {
        "simulator_prefix_cells": 0,
        "scored_behavior_cells": 0,
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }
