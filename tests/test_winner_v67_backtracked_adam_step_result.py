from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v67_backtracked_adam_step_result.json"
RESULT_SHA256 = "90614ecfe5a5383b1e27809049a737cfc6f59cb6abb1b29284c65416442c6b66"


def test_v67_result_identity_loss_and_artifacts() -> None:
    assert hashlib.sha256(RESULT.read_bytes()).hexdigest() == RESULT_SHA256
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V67_BACKTRACKED_ADAM_STEP"
    assert value["decision"] == (
        "PREREGISTER_BOUNDED_DETERMINISTIC_BACKTRACKED_ADAM_CONTINUATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    optimization = value["optimization"]
    assert optimization["optimizer_count_before"] == 574
    assert optimization["optimizer_count_after"] == 575
    assert optimization["accepted_fraction"] == 0.25
    assert optimization["accepted_loss"] < optimization["loss_before"]
    assert optimization["accepted_loss_delta"] < 0.0
    assert value["snapshot"]["sha256"] == (
        "c234bacde983728234d2b2a85cba5418263dc1adf383d9eb6dd59d48ff26654b"
    )
    assert value["graph"]["sha256"] == (
        "a21a1c07a8148b5ad5fbaa1da1217ea6a19c1228f6088f4ab9864142b71e331e"
    )
    assert value["graph"]["contract"]["abi_exact"]
    assert value["graph"]["contract"]["jax_onnx_at_most_1e_7"]
    assert value["graph"]["contract"][
        "previous_action_out_equals_action_bit_exact"
    ]


def test_v67_result_has_no_support_or_robot_authority() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    execution = value["execution"]
    assert execution == {
        "continuation_optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "optimizer_updates": 1,
        "robot_or_rdk_access": 0,
    }
    authority = value["authority"]
    assert authority["continuation_authorized_now"] is False
    assert authority["support_gate_authorized"] is False
    assert authority["checkpoint_selection_authorized"] is False
    assert authority["deployment_authorized"] is False
    assert authority["robot_clearance"] is False
