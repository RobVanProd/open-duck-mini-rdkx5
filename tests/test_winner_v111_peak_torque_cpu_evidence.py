import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_original_hold_is_preserved_and_narrow() -> None:
    value = load("winner_v111_peak_torque_cpu_result.json")
    assert value["status"] == "HOLD_WINNER_V111_PEAK_TORQUE_CPU_SMOKE"
    assert value["failed_checks"] == ["objective_metric_present"]
    assert value["checks"]["every_policy_leaf_updated"] is True
    assert value["checks"]["source_restore_parameters_bit_exact"] is True
    assert value["checks"]["onnx_abi_exact"] is True


def test_reporting_correction_uses_frozen_event_evidence() -> None:
    value = load("winner_v111_peak_torque_cpu_correction.json")
    assert (
        value["status"]
        == "PASS_WINNER_V111_PEAK_TORQUE_CPU_SMOKE_REPORTING_CORRECTED"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["correction_scope"] == {
        "classification": "reporting_only",
        "original_check": (
            "searched captured stdout for peak_torque_exceedance"
        ),
        "correct_source": "TensorBoard scalar event stream",
        "training_rerun": False,
        "policy_change": False,
        "checkpoint_change": False,
        "gate_change": False,
    }
    evidence = value["objective_metric_evidence"]
    assert evidence["tag"] == "eval/episode_cost/peak_torque_exceedance"
    assert [row["step"] for row in evidence["events"]] == [0, 1024]
    assert [row["value"] for row in evidence["events"]] == [
        68.95680236816406,
        27.76718521118164,
    ]
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
