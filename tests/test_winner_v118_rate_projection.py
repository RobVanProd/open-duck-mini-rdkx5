import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v118_is_one_preregistered_cpu_vector() -> None:
    value = load("winner_v118_rate_projection_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_WINNER_V118_RATE_PROJECTION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["projection"]["candidate_vectors"] == 1
    assert value["projection"]["scalar_search"] is False
    assert value["projection"]["training_steps"] == 0
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["execution_now"]["colab_compute_units"] == 0
    assert value["authority"]["training_authorized"] is False


def test_v118_changes_only_the_postguard_delta_initializer() -> None:
    value = load("winner_v118_rate_projection_contract.json")
    assert value["status"] == (
        "PASS_WINNER_V118_RATE_PROJECTION_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["policies"]) == 2
    assert value["formal_behavior_cells_executed"] == 0
    for policy in value["policies"]:
        assert policy["graph_nodes_bit_exact"]
        assert policy["changed_initializer_names"] == [
            "v117_max_action_delta"
        ]
        assert policy["selected_delta_exact"]
        assert policy["all_other_initializers_bit_exact"]
        assert policy["inference"]["pass"]
        assert policy["inference"]["max_state_error"] == 0.0
        assert policy["inference"]["max_hidden_error"] == 0.0
        assert policy["inference"]["max_zero_action"] == 0.0
        assert policy["inference"]["max_zero_previous"] == 0.0
        assert policy["inference"]["changed_projection_is_exercised"]
    assert value["authority"][
        "nominal_behavior_preregistration_authorized"
    ]
    assert value["authority"]["training_authorized"] is False
