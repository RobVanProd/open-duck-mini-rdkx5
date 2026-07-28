from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def canonical_sha256(value: Any, hash_key: str) -> str:
    payload = dict(value)
    payload.pop(hash_key, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def test_t76_preregistration_is_frozen_when_present() -> None:
    path = ANALYSIS / "t76_com_hidden_geometry_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T76_COM_HIDDEN_GEOMETRY"
    assert value["failed_checks"] == []
    assert value["population"]["h_out_pairs_per_checkpoint"] == 30
    assert (
        value["population"]["basis_rule"]["pairs_per_checkpoint"] == 10
    )
    assert (
        value["population"]["heldout_rule"]["pairs_per_checkpoint"] == 20
    )
    assert value["geometry"]["no_rank_or_threshold_search"] is True
    assert value["decision_rule"]["no_hosted_run_earned"] is True
    assert (
        canonical_sha256(value, "preregistered_contract_sha256")
        == value["preregistered_contract_sha256"]
    )


def test_t76_result_obeys_frozen_decision_when_present() -> None:
    path = ANALYSIS / "t76_com_hidden_geometry_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "new_simulator_cells": 0,
        "optimizer_steps": 0,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }
    passed = not value["failed_checks"]
    assert len(value["checkpoint_results"]) == 2
    assert all(
        item["basis_pairs"] == 10 and item["heldout_pairs"] == 20
        for item in value["checkpoint_results"]
    )
    if passed:
        assert value["status"] == "PASS_T76_COM_HIDDEN_GEOMETRY"
        assert (
            value["decision"]
            == "EARN_T77_EXACT_COM_AXIS_OUTPUT_HEAD_REFLECTION_PREREGISTRATION"
        )
    else:
        assert value["status"] == "HOLD_T76_COM_HIDDEN_GEOMETRY"
        assert (
            value["decision"] == "CLOSE_COM_AXIS_OUTPUT_HEAD_REFLECTION"
        )
    assert (
        canonical_sha256(value, "result_sha256")
        == value["result_sha256"]
    )
