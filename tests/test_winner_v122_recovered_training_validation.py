import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v122_recovered_training_validation.json"
)


def test_v122_recovered_training_is_cpu_valid_before_behavior() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V122_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["classification"]["training_completed"] is True
    assert value["classification"]["training_retry"] is False
    assert value["classification"]["training_resume"] is False
    assert value["classification"]["prelaunch_transport_correction"] is True
    assert value["classification"]["behavior_cells"] == 0
    assert [row["step"] for row in value["checkpoints"]] == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert all(
        len(row["policy_leaf_deltas"]) == 15
        and row["every_policy_leaf_updated"]
        for row in value["trained_checkpoints"]
    )
    assert all(
        row["abi_exact"]
        and row["initializers_finite"]
        and row["cpu_provider_exact"]
        and row["chain_256_finite"]
        for row in value["onnx"]
    )
    assert value["authority"][
        "deployment_transform_preregistration_authorized"
    ] is True
    assert value["authority"]["behavior_evaluation_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
