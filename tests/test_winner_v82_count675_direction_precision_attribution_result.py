from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v82_count675_direction_precision_attribution_result.json"
)


def test_result_selects_negative_gradient_step_proof_only() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V82_COUNT675_DIRECTION_PRECISION_ATTRIBUTION"
    )
    assert value["classification"] == (
        "ADAM_GEOMETRY_STALLED_NEGATIVE_GRADIENT_DESCENDS"
    )
    assert value["decision"] == (
        "PREREGISTER_ONE_COUNT675_NEGATIVE_GRADIENT_STEP_PROOF"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["committed_optimizer_updates"] == 0
    assert value["execution"]["snapshots_written"] == 0
    assert value["execution"]["onnx_graphs_written"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_geometry_reproduces_stop_and_isolates_descent() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    geometry = value["loss_geometry"]
    assert geometry["teacher_loss_before"] == 0.007218536455184221
    assert geometry["teacher_loss_float32_ulp"] == 4.656612873077393e-10
    assert geometry["teacher_gradient_dot_adam_delta"] < 0.0
    adam = geometry["adam_fraction_rows"]
    assert len(adam) == 21
    assert all(row["loss"] >= geometry["teacher_loss_before"] for row in adam)
    assert any(row["changed_parameter_elements"] > 0 for row in adam)
    negative = geometry["negative_gradient_norm_matched_fraction_rows"]
    assert len(negative) == 13
    descending = [row for row in negative if row["loss"] < geometry["teacher_loss_before"]]
    assert [row["fraction"] for row in descending] == [
        0.5,
        0.25,
        0.125,
        0.0625,
        0.03125,
        0.015625,
        0.0078125,
        0.00390625,
        0.001953125,
        0.0009765625,
        0.00048828125,
        0.000244140625,
    ]
    assert min(negative, key=lambda row: row["loss"])["fraction"] == 0.5
