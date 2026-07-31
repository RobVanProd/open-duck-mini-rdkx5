import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v114_linear_torque_cpu_result.json"
)


def test_v114_cpu_smoke_passes_every_frozen_check() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V114_LINEAR_TORQUE_CPU_SMOKE"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["training"]["checkpoint_steps"] == [0, 1024]
    assert value["training"]["onnx_steps"] == [0, 1024]
    assert len(value["training"]["policy_leaf_deltas"]) == 15
    assert all(
        delta > 0.0
        for delta in value["training"]["policy_leaf_deltas"].values()
    )


def test_v114_isolated_linear_objective_and_narrow_authority() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    analytic = value["analytic_objective"]
    assert analytic["default_linear_scale"] == 0.0
    assert analytic["default_squared_scale"] == 0.0
    assert analytic["observed"] == analytic["expected"]
    assert analytic["max_abs_error"] == 0.0

    metric = value["training"]["objective_metric"]
    assert metric["tag"] == (
        "eval/episode_cost/linear_peak_torque_exceedance"
    )
    assert [event["step"] for event in metric["events"]] == [0, 1024]
    assert all(event["value"] > 0.0 for event in metric["events"])

    authority = value["authority"]
    assert authority["hosted_preregistration_authorized"] is True
    for name in (
        "hosted_training_authorized",
        "behavior_evaluation_authorized",
        "checkpoint_selection_authorized",
        "gate5_authorized",
        "robot_clearance",
        "rdkx5_or_robot",
        "torque_or_motion",
    ):
        assert authority[name] is False
