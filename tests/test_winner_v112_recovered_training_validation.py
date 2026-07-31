import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v112_recovered_training_validation.json"
)


def test_recovered_training_is_exact_and_behavior_remains_blocked() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V112_RECOVERED_TRAINING_VALIDATION"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["classification"] == {
        "hosted_result": "HOLD_WINNER_V112_PEAK_TORQUE_HOSTED_CONTINUATION",
        "failure_stage": "post_training_artifact_inspection",
        "training_completed": True,
        "training_retry": False,
        "training_resume": False,
        "correction_method": (
            "read-only CPU topology remap using the exact source tree as "
            "Orbax restore template"
        ),
    }
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
    assert all(row["every_policy_leaf_updated"] for row in value["trained_checkpoints"])
    torque = value["training_metric_evidence"][
        "eval/episode_cost/peak_torque_exceedance"
    ]
    assert [row["step"] for row in torque] == [0, 1_003_520, 2_007_040]
    assert torque[-1]["value"] < torque[0]["value"]
    authority = value["authority"]
    assert authority["postexport_transform_preregistration_authorized"] is True
    for name in (
        "behavior_evaluation_authorized",
        "checkpoint_selection_authorized",
        "gate5_authorized",
        "robot_clearance",
        "rdkx5_or_robot",
        "torque_or_motion",
    ):
        assert authority[name] is False
