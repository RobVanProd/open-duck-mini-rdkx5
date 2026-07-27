import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t28_failure_attribution_and_transform_are_frozen() -> None:
    payload = load("t28_t23_action_margin_preregistration.json")
    census = payload["causal_attribution"]["event_census"]
    transform = payload["transform"]
    assert payload["status"] == "PREREGISTERED_T28_T23_ACTION_MARGIN_REPAIR"
    assert payload["failed_checks"] == []
    assert payload["causal_attribution"]["failed_cells"] == 6
    assert payload["causal_attribution"]["failure_is_only_zero_saturation"]
    assert census["event_count"] == 39
    assert census["event_checkpoint_counts"] == {"T23_SUPPORT_FINAL": 39}
    assert set(census["event_joint_counts"]) == {
        "left_ankle",
        "right_hip_pitch",
    }
    assert census["maximum_absolute_action_all_cells"] < 1.0
    expected = np.nextafter(np.float32(0.98), np.float32(0.0))
    assert transform["stored_float32_limit_abs"] == float(expected)
    assert transform["no_training"]
    assert transform["no_parameter_search"]


def test_t28_transform_contract_is_exact_and_cpu_only() -> None:
    payload = load("t28_t23_action_margin_transform_contract.json")
    assert (
        payload["status"]
        == "PASS_T28_T23_ACTION_MARGIN_TRANSFORM_CONTRACT"
    )
    assert payload["failed_checks"] == []
    assert payload["checks"]["all_policy_contracts_pass"]
    assert payload["checks"]["half_is_interior_on_frozen_samples"]
    assert payload["checks"]["final_transform_activates_on_frozen_samples"]
    assert len(payload["policies"]) == 2
    for policy in payload["policies"]:
        assert policy["pass"]
        assert all(policy["checks"].values())
        assert policy["inputs"] == [
            "obs",
            "previous_action",
            "h_in",
            "calibration_context",
        ]
        assert policy["outputs"] == [
            "continuous_actions",
            "previous_action_out",
            "h_out",
        ]
    assert not payload["authority"]["training"]
    assert not payload["authority"]["rdkx5_or_robot"]


def test_t28_condition_is_exactly_sixteen_cells() -> None:
    payload = load(
        "t28_t23_action_margin_condition_preregistration.json"
    )
    assert (
        payload["status"]
        == "PREREGISTERED_T28_T23_ACTION_MARGIN_CONDITION"
    )
    assert payload["failed_checks"] == []
    assert payload["conditions"] == [
        {
            "condition_index": 1,
            "id": "FLOOR_FRICTION_LO",
            "override": {"floor_friction": 0.5},
        }
    ]
    assert payload["matrix"]["maximum_cells"] == 16
    assert payload["matrix"]["condition_must_complete"]
    assert payload["decision_rule"]["both_checkpoints_required"]
    assert payload["decision_rule"]["no_checkpoint_selection"]
    assert not payload["authority"]["training"]
    assert not payload["authority"]["gate5"]
