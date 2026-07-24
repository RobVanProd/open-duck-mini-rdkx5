import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v123_prereg_reuses_exact_v121_hierarchy() -> None:
    value = load("winner_v123_deployment_transform_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_WINNER_V123_DEPLOYMENT_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["sources"]) == 2
    assert {row["step"] for row in value["sources"]} == {
        1_003_520,
        2_007_040,
    }
    assert value["classification"]["new_training"] is False
    assert value["classification"]["new_transform_parameter"] is False
    assert value["classification"]["formal_behavior_cells"] == 0
    assert value["authority"]["transform_execution_authorized"] is True
    assert value["authority"]["behavior_evaluation_authorized"] is False


def test_v123_transform_contract_passes_both_graphs() -> None:
    value = load("winner_v123_deployment_transform_contract.json")
    assert value["status"] == (
        "PASS_WINNER_V123_DEPLOYMENT_TRANSFORM_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["formal_behavior_cells_executed"] == 0
    assert len(value["policies"]) == 2
    assert all(
        row["source_train_delta_exact"]
        and row["final_projection_delta_exact"]
        and row["inference"]["pass"]
        for row in value["policies"]
    )
    assert value["authority"][
        "nominal_behavior_preregistration_authorized"
    ] is True
    assert value["authority"]["behavior_evaluation_authorized"] is False


def test_v123_nominal_gate_freezes_both_checkpoints() -> None:
    value = load("winner_v123_nominal_behavior_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_WINNER_V123_NOMINAL_BEHAVIOR"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["matrix"]["cells"] == 16
    assert {row["step"] for row in value["matrix"]["rows"]} == {
        1_003_520,
        2_007_040,
    }
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["authority"]["formal_behavior_cells_authorized"] == 16
    assert value["authority"]["full_matrix_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
