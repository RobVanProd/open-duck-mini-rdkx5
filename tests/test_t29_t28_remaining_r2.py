import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def plan(payload: dict) -> list[dict]:
    return [
        {
            "cell_index": index,
            "condition_index": condition["condition_index"],
            "condition_id": condition["id"],
            "checkpoint_id": policy["checkpoint_id"],
            "fit_id": fit["fit_id"],
            "command_x_m_s": float(command),
        }
        for index, (condition, policy, fit, command) in enumerate(
            (
                (condition, policy, fit, command)
                for condition in payload["conditions"]
                for policy in payload["policies"]
                for fit in payload["fits"]
                for command in payload["commands_x_m_s"]
            ),
            start=1,
        )
    ]


def test_t29_is_exactly_original_conditions_two_through_twenty() -> None:
    payload = load("t29_t28_remaining_r2_preregistration.json")
    original = load("t27_t23_robustness_matrix_preregistration.json")
    assert payload["status"] == "PREREGISTERED_T29_T28_REMAINING_R2_MATRIX"
    assert payload["failed_checks"] == []
    assert payload["conditions"] == original["conditions"][1:]
    assert [item["condition_index"] for item in payload["conditions"]] == list(
        range(2, 21)
    )
    assert payload["behavior_contract"] == original["behavior_contract"]
    assert payload["protection_contract"] == original["protection_contract"]
    assert payload["support_handoff"] == original["support_handoff"]


def test_t29_plan_is_frozen_at_304_cells() -> None:
    payload = load("t29_t28_remaining_r2_preregistration.json")
    cells = plan(payload)
    assert len(cells) == 304
    assert payload["matrix"]["maximum_new_cells"] == 304
    assert payload["matrix"]["total_r2_cells_with_condition_one"] == 320
    digest = hashlib.sha256(
        json.dumps(
            cells,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    assert digest == payload["matrix"]["plan_sha256"]
    assert payload["matrix"]["sequential_conditions"]
    assert payload["matrix"][
        "complete_current_sixteen_cell_condition_before_stop"
    ]
    assert payload["matrix"]["stop_after_first_failed_condition"]
    assert payload["matrix"]["no_skip"]
    assert payload["matrix"]["no_retry"]


def test_t29_authority_remains_cpu_only() -> None:
    payload = load("t29_t28_remaining_r2_preregistration.json")
    assert payload["condition_one_basis"]["green_cells"] == 16
    assert payload["decision_rule"]["both_checkpoints_required"]
    assert payload["decision_rule"]["no_checkpoint_selection"]
    assert payload["authority"]["execute_remaining_cpu_matrix"]
    assert not payload["authority"]["training"]
    assert not payload["authority"]["colab"]
    assert not payload["authority"]["gate5_hardware"]
    assert not payload["authority"]["rdkx5_or_robot"]
    assert not payload["authority"]["torque_or_motion"]
