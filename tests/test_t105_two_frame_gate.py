from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t105_preregistration_is_abi_preserving_when_present() -> None:
    path = ANALYSIS / "t105_two_frame_gate_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T105_TWO_FRAME_GATE_FALSIFIER"
    )
    assert len(value["traces"]) == 24
    assert value["population"]["paired_groups"] == 12
    assert value["candidate"]["new_state"] is False
    assert value["candidate"]["new_input_or_output"] is False
    assert value["candidate"]["scalar_search"] is False
    assert value["authority"]["behavior"] is False
    assert value["authority"]["training"] is False


def test_t105_result_obeys_frozen_decision_when_present() -> None:
    path = ANALYSIS / "t105_two_frame_gate_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["candidate_pass"]:
        assert value["status"] == "PASS_T105_TWO_FRAME_GATE_FALSIFIER"
        assert value["decision"] == (
            "EARN_T106_TWO_FRAME_GATE_GRAPH_TRANSFORM_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == "CLOSE_T105_TWO_FRAME_GATE_FALSIFIER"
        assert value["decision"] == (
            "CLOSE_TWO_FRAME_STATELESS_GATE_STABILIZATION"
        )
    assert value["interpretation"]["hosted_run_earned"] is False
    assert value["interpretation"]["behavior_rerun_earned"] is False
