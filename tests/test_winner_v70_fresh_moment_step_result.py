from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v70_fresh_moment_step_result.json"
RESULT_SHA256 = "36156741dde5afeae41c8218fb345cf7699ec474b5a3c552bc5d66a3a7140792"


def test_v70_result_identity_and_fresh_moment_step() -> None:
    assert hashlib.sha256(RESULT.read_bytes()).hexdigest() == RESULT_SHA256
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V70_FRESH_MOMENT_STEP"
    assert value["decision"] == (
        "PREREGISTER_BOUNDED_FRESH_MOMENT_SAFEGUARDED_CONTINUATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    optimization = value["optimization"]
    assert optimization["optimizer_count_before"] == 601
    assert optimization["optimizer_count_after"] == 602
    assert optimization["accepted_fraction"] == 0.125
    assert optimization["accepted_loss"] < optimization["loss_before"]
    assert optimization["accepted_loss_delta"] < -1.8e-6
    assert optimization["reset_moment_keys"] == [
        "action_bias",
        "action_weight",
        "hidden_bias",
        "hidden_weight",
        "obs_weight",
        "previous_action_weight",
    ]


def test_v70_result_artifacts_and_authority() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["snapshot"]["sha256"] == (
        "24fd0b25de5cd5e198a61288cff2d6e437e251a63fa1a05213d33d585838ec7b"
    )
    assert value["graph"]["sha256"] == (
        "45ac3122addc7938511bd255ca25fab0ced03f9ef5fd6aa969a83ca306ed9ac4"
    )
    assert value["graph"]["contract"]["abi_exact"]
    assert value["graph"]["contract"]["jax_onnx_at_most_1e_7"]
    assert value["graph"]["contract"][
        "previous_action_out_equals_action_bit_exact"
    ]
    assert value["execution"]["optimizer_updates"] == 1
    assert value["execution"]["continuation_optimizer_updates"] == 0
    assert value["execution"]["formal_support_cells"] == 0
    assert value["authority"]["continuation_authorized_now"] is False
    assert value["authority"]["deployment_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
