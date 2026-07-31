from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v83_count675_negative_gradient_step_result.json"


def test_result_proves_one_localized_negative_gradient_step() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V83_COUNT675_NEGATIVE_GRADIENT_STEP"
    assert value["decision"] == (
        "PREREGISTER_BOUNDED_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    optimization = value["optimization"]
    assert optimization["optimizer_count_before"] == 674
    assert optimization["optimizer_count_after"] == 675
    assert optimization["accepted_fraction"] == 0.5
    assert optimization["teacher_loss_after"] < optimization["teacher_loss_before"]
    assert optimization["predictor_loss_after"] == optimization["predictor_loss_before"]
    assert optimization["optimizer_m_and_v_bit_exact"] is True
    assert value["execution"]["optimizer_updates"] == 1
    assert value["execution"]["formal_support_cells"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_snapshot_and_graph_receipts_are_frozen() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["snapshot"]["completed_updates"] == 675
    assert value["snapshot"]["sha256"] == (
        "cae62d8f50005b30367ebef46ecbdc66d74c17b2b258f4991e2f8a8abf469827"
    )
    assert value["graph"]["completed_updates"] == 675
    assert value["graph"]["sha256"] == (
        "e1bc9fc02aab6253ab9d8c08b158cacd7bbbd96adab96a73dade90a229103539"
    )
    assert value["graph"]["contract"]["abi_exact"] is True
    assert value["graph"]["contract"]["jax_onnx_at_most_1e_7"] is True
    assert value["graph"]["contract"][
        "previous_action_out_equals_action_bit_exact"
    ] is True
