import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v115_v2_reporting_correction_changes_no_vector() -> None:
    value = load(
        "winner_v115_nominal_failure_attribution_v2_correction.json"
    )
    assert value["status"] == (
        "PASS_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2_REPORTING_CORRECTED"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    scope = value["correction_scope"]
    assert scope["classification"] == "reporting_only"
    assert scope["derived_vector_changed"] is False
    assert scope["policy_changed"] is False
    assert scope["training_run"] is False
    assert scope["behavior_cells"] == 0
    assert value["authority"]["rate_projection_preregistration_authorized"]


def test_v116_projection_is_preregistered_as_one_vector() -> None:
    value = load("winner_v116_rate_projection_preregistration.json")
    assert value["status"] == "PREREGISTERED_WINNER_V116_RATE_PROJECTION"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["projection"]["candidate_vectors"] == 1
    assert value["projection"]["scalar_search"] is False
    assert value["projection"]["apply_identically_to_both_checkpoints"]
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_v116_pre_guard_initializer_placement_is_held() -> None:
    value = load("winner_v116_rate_projection_contract.json")
    assert value["status"] == "HOLD_WINNER_V116_RATE_PROJECTION_CONTRACT"
    assert value["failed_checks"] == ["all_inference_contracts_pass"]
    assert value["checks"]["only_max_action_delta_changed"] is True
    assert value["checks"]["graph_nodes_bit_exact"] is True
    assert value["checks"]["all_inference_contracts_pass"] is False
    assert value["formal_behavior_cells_executed"] == 0
    assert value["authority"]["nominal_behavior_preregistration_authorized"] is False
