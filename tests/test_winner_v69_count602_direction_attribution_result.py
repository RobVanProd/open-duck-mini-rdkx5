from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v69_count602_direction_attribution_result.json"
RESULT_SHA256 = "cd1c25f0adf89597297a8fa5a52cd1a03a9da5e4743ad92a32fbaa23caf85b75"


def test_v69_result_identity_and_zero_commit() -> None:
    assert hashlib.sha256(RESULT.read_bytes()).hexdigest() == RESULT_SHA256
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V69_COUNT602_DIRECTION_ATTRIBUTION"
    assert value["classification"] == (
        "INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER"
    )
    assert value["decision"] == (
        "PREREGISTER_ONE_FRESH_MOMENT_TEACHER_STEP_PROOF"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    execution = value["execution"]
    assert execution["committed_optimizer_updates"] == 0
    assert execution["snapshots_written"] == 0
    assert execution["onnx_graphs_written"] == 0
    assert execution["formal_support_cells"] == 0
    assert execution["robot_or_rdk_access"] == 0


def test_v69_result_geometry_selects_fresh_moments() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    geometry = value["loss_geometry"]
    before = geometry["teacher_loss_before"]
    assert geometry["teacher_gradient_dot_adam_delta"] > 0.0
    adam = geometry["adam_fraction_rows"]
    assert all(row["loss"] >= before for row in adam[:5])
    negative = geometry["negative_gradient_norm_matched_fraction_rows"]
    assert all(row["loss"] < before for row in negative)
    assert negative[0]["loss_delta"] < -8.0e-7
    authority = value["authority"]
    assert authority["attention_or_flat_transport_selected"] is False
    assert authority["checkpoint_selection_authorized"] is False
    assert authority["deployment_authorized"] is False
    assert authority["robot_clearance"] is False
