from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v66_failed_step_attribution_result.json"
RESULT_SHA256 = "dc25ee23ecfaa7910c39e3a3ff4c00b7f97f52a9a0b11d630e9d0dff3cfc25de"


def test_v66_result_hash_identity_and_zero_commit() -> None:
    assert hashlib.sha256(RESULT.read_bytes()).hexdigest() == RESULT_SHA256
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V66_FAILED_STEP_ATTRIBUTION"
    assert value["classification"] == "INHERITED_ADAM_FULL_STEP_OVERSHOOT"
    assert value["decision"] == (
        "PREREGISTER_ONE_DETERMINISTIC_BACKTRACKED_ADAM_STEP_PROOF"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    execution = value["execution"]
    assert execution["committed_optimizer_updates"] == 0
    assert execution["snapshots_written"] == 0
    assert execution["onnx_graphs_written"] == 0
    assert execution["formal_support_cells"] == 0
    assert execution["robot_or_rdk_access"] == 0


def test_v66_result_geometry_selects_backtracking_not_attention() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    geometry = value["loss_geometry"]
    before = geometry["teacher_loss_before"]
    assert geometry["inherited_adam_full_loss"] >= before
    assert geometry["inherited_adam_full_loss_delta"] > 0.0
    assert geometry["teacher_gradient_dot_inherited_adam_delta"] < 0.0
    inherited = geometry["inherited_adam_fraction_rows"]
    assert [row["fraction"] for row in inherited] == [
        0.0625,
        0.125,
        0.25,
        0.5,
        0.75,
        1.0,
    ]
    assert all(row["loss"] < before for row in inherited[:3])
    assert all(row["loss"] >= before for row in inherited[3:])
    assert min(inherited, key=lambda row: row["loss"])["fraction"] == 0.25
    negative_gradient = geometry[
        "negative_gradient_norm_matched_fraction_rows"
    ]
    assert all(row["loss"] < before for row in negative_gradient)
    authority = value["authority"]
    assert authority["attention_or_flat_transport_selected"] is False
    assert authority["checkpoint_selection_authorized"] is False
    assert authority["deployment_authorized"] is False
    assert authority["robot_clearance"] is False
