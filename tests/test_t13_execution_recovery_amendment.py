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


def test_t13_recovery_is_narrow_and_partial_weight_is_zero() -> None:
    value = json.loads(
        (
            ANALYSIS / "t13_execution_recovery_amendment.json"
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
    assert value["failed_execution"]["completed_prefix_cells"] == 1
    assert value["failed_execution"]["formal_result_written"] is False
    assert value["failed_execution"]["decision_weight"] == 0
    assert value["failed_execution"]["selection_use_forbidden"] is True
    assert value["authorized_recovery"]["attempts_exact"] == 1
    assert (
        value["authorized_recovery"]["reuse_partial_v1_forbidden"]
        is True
    )
    assert value["correction"]["mechanism_changed"] is False
    assert value["correction"]["thresholds_changed"] is False
    assert value["correction"]["matrix_changed"] is False
    assert value["execution_now"] == {
        "formal_decision_cells": 0,
        "scored_behavior_cells": 0,
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }
