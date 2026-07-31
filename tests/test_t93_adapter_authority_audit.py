from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT / "outputs" / "analysis" / "t93_adapter_authority_preregistration.json"
)
RESULT = ROOT / "outputs" / "analysis" / "t93_adapter_authority_result.json"


def test_t93_preregistration_has_no_behavior_or_training_authority() -> None:
    if not PREREG.exists():
        pytest.skip("T93 preregistration has not run")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T93_ADAPTER_AUTHORITY_AUDIT"
    assert value["failed_checks"] == []
    assert len(value["traces"]) == 32
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["deployment"]
    assert not value["authority"]["rdkx5_or_robot"]
    assert value["execution_now"]["simulator_steps"] == 0


def test_t93_result_is_exact_read_only_trace_attribution() -> None:
    if not RESULT.exists():
        pytest.skip("T93 formal audit has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T93_ADAPTER_AUTHORITY_AUDIT"
    assert value["failed_checks"] == []
    assert value["checks"]["all_trace_outputs_replay_exact"]
    assert value["checks"]["calibration_context_is_unused_compatibility_input"]
    assert value["checks"]["all_32_frozen_traces_replayed"]
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
