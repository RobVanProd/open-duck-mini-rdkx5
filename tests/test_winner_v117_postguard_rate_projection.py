import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v117_projection_is_preregistered_without_training() -> None:
    value = load(
        "winner_v117_postguard_rate_projection_preregistration.json"
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V117_POSTGUARD_RATE_PROJECTION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    projection = value["projection"]
    assert projection["candidate_vectors"] == 1
    assert projection["scalar_search"] is False
    assert projection["training_steps"] == 0
    assert projection["placement"] == (
        "after_G3_before_restored_x0_deadband"
    )
    assert projection["final_state_feedback"] == "final_bounded_action"
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["execution_now"]["colab_compute_units"] == 0


def test_v117_postguard_projection_contract_passes() -> None:
    value = load("winner_v117_postguard_rate_projection_contract.json")
    assert value["status"] == (
        "PASS_WINNER_V117_POSTGUARD_RATE_PROJECTION_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["policies"]) == 2
    assert value["formal_behavior_cells_executed"] == 0
    for policy in value["policies"]:
        assert policy["source_nodes_preserved"]
        assert policy["source_initializers_preserved"]
        assert policy["selected_delta_exact"]
        assert policy["appended_node_count"] == 9
        assert policy["inference"]["pass"]
        assert policy["inference"]["max_state_error"] == 0.0
        assert policy["inference"]["max_hidden_error"] == 0.0
        assert policy["inference"]["max_zero_action"] == 0.0
        assert policy["inference"]["max_zero_previous"] == 0.0
        assert policy["inference"]["changed_projection_is_exercised"]
    assert value["authority"][
        "nominal_behavior_preregistration_authorized"
    ]
