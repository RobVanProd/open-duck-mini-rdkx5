from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/t56_recovered_training_validation.json"
)


def test_t56_recovered_training_is_cpu_valid_before_behavior() -> None:
    if not RESULT.exists():
        pytest.skip("T56 recovered training has not been validated")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T56_RECOVERED_TRAINING_VALIDATION"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["classification"]["training_completed"] is True
    assert value["classification"]["training_retry"] is False
    assert value["classification"]["training_resume"] is False
    assert value["classification"]["behavior_cells"] == 0
    assert value["classification"]["balance_first"] is True
    assert value["classification"]["gait_transfer"] is True
    assert [
        row["step"] for row in value["stages"]["balance"]["checkpoints"]
    ] == [0, 1_003_520]
    assert [
        row["step"] for row in value["stages"]["transfer"]["checkpoints"]
    ] == [0, 1_003_520, 2_007_040]
    assert all(
        row["every_policy_leaf_updated"]
        and row["every_critic_leaf_updated"]
        for stage in value["stages"].values()
        for row in stage["trained_checkpoints"]
    )
    assert value["authority"][
        "postexport_transform_preregistration_authorized"
    ]
    assert not value["authority"]["behavior_evaluation_authorized"]
    assert not value["authority"]["gate5_authorized"]
