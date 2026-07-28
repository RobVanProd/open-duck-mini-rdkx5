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


def test_t71_preregistration_is_frozen_when_present() -> None:
    path = ANALYSIS / "t71_t67_com_hidden_causal_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T71_T67_COM_HIDDEN_CAUSAL_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert value["population"] == {
        "checkpoints": 2,
        "fits": 2,
        "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
        "paired_trace_streams": 16,
        "moving_trace_streams": 12,
        "sample_ticks": [0, 8, 16, 32, 64, 80],
        "moving_postreset_samples": 60,
    }
    assert value["decision_rule"]["no_hosted_run_earned"] is True
    assert (
        canonical_sha256(value, "preregistered_contract_sha256")
        == value["preregistered_contract_sha256"]
    )


def test_t71_result_obeys_frozen_decision_when_present() -> None:
    path = ANALYSIS / "t71_t67_com_hidden_causal_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "new_simulator_cells": 0,
        "optimizer_steps": 0,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }
    if not value["failed_checks"]:
        assert (
            value["status"]
            == "PASS_T71_COM_SIGNAL_PRESENT_AND_CAUSALLY_USED"
        )
        assert (
            value["classification"]
            == "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
        )
        assert (
            value["decision"]
            == "SELECT_TRANSITION_CONTROL_RESCUE_FALSIFIER"
        )
    assert (
        canonical_sha256(value, "result_sha256")
        == value["result_sha256"]
    )
