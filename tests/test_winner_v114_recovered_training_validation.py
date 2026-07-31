import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v114_recovered_training_validation.json"
)


def test_v114_recovered_training_passes_every_frozen_check() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V114_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert [row["step"] for row in value["checkpoints"]] == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert [row["step"] for row in value["onnx"]] == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert all(
        row["every_policy_leaf_updated"]
        for row in value["trained_checkpoints"]
    )


def test_v114_validation_only_authorizes_transform_preregistration() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    authority = value["authority"]
    assert authority["postexport_transform_preregistration_authorized"]
    for name in (
        "behavior_evaluation_authorized",
        "checkpoint_selection_authorized",
        "gate5_authorized",
        "robot_clearance",
        "rdkx5_or_robot",
        "torque_or_motion",
    ):
        assert authority[name] is False
    classification = value["classification"]
    assert classification["training_retry"] is False
    assert classification["training_resume"] is False
    assert classification["behavior_cells"] == 0
