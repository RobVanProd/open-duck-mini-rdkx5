from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v106_com_prefix_reproduction_is_cpu_only_and_pre_scored() -> None:
    path = ANALYSIS / "winner_v106_com_prefix_reproduction.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert digest(path) == (
        "ded813c4ca8e96862a6db377b4010c84eac1c49d741484767c5d430599de6581"
    )
    assert payload["status"] == "PASS_WINNER_V106_COM_PREFIX_REPRODUCTION"
    assert payload["failed_checks"] == []
    assert payload["formal_behavior_cells_executed"] == 0
    assert payload["cpu_environment"]["jax_backend"] == "cpu"
    assert payload["cpu_environment"]["device_platforms"] == ["cpu"]
    assert payload["observed"] == {
        "environment_readback_present": False,
        "result_keys": ["error", "mode", "policy", "status"],
        "scored_trace_created": False,
        "simulator_error": "calibration prefix terminated early",
        "simulator_status": "HOLD_RESPONSE_CALIBRATION_PREFIX",
    }


def test_v106_attribution_keeps_policy_and_evaluator_failures_separate() -> None:
    path = ANALYSIS / "winner_v106_response_gate_attribution.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert digest(path) == (
        "64f1c3130f8ffe5dc245202d1b6c029c79019cd2cc434324292d024ee43d38c8"
    )
    assert payload["status"] == (
        "HOLD_WINNER_V106_V105_POLICY_AND_V103_EVALUATOR"
    )
    assert payload["decision"] == (
        "AUTHORIZE_EVALUATOR_CORRECTION_AND_STAGE_BOUNDARY_DIAGNOSTIC"
    )
    assert payload["failed_checks"] == []
    evidence = payload["raw_cell_evidence"]
    assert evidence["cells"] == 1024
    assert evidence["cpu_label_only_cells"] == 100
    assert evidence["behavior_failure_cells"] == 924
    assert evidence["runner_exception_cells"] == 160
    assert payload["causal_attribution"]["policy_failure"]["present"] is True
    assert (
        payload["causal_attribution"]["cpu_detection_defect"][
            "policy_behavior_implicated"
        ]
        is False
    )
    assert (
        payload["causal_attribution"]["early_return_readback_defect"][
            "underlying_policy_or_calibration_failure_present"
        ]
        is True
    )
    assert payload["authority"] == {
        "checkpoint_selection_authorized": False,
        "evaluator_correction_authorized": True,
        "gate5_authorized": False,
        "hosted_training_authorized": False,
        "rdkx5_or_robot": False,
        "robot_clearance": False,
        "stage_boundary_diagnostic_authorized": True,
        "torque_or_motion": False,
    }
