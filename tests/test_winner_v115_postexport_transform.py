import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v115_transform_was_frozen_before_behavior() -> None:
    value = load("winner_v115_postexport_transform_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_WINNER_V115_POSTEXPORT_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert [row["step"] for row in value["sources"]] == [
        1_003_520,
        2_007_040,
    ]
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["authority"]["cpu_transform_authorized"] is True
    assert value["authority"]["behavior_evaluation_authorized"] is False


def test_v115_transform_preserves_sources_and_contract() -> None:
    value = load("winner_v115_postexport_transform_contract.json")
    assert value["status"] == (
        "PASS_WINNER_V115_POSTEXPORT_TRANSFORM_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["policies"]) == 2
    assert all(row["source_nodes_preserved"] for row in value["policies"])
    assert all(
        row["source_initializers_preserved"] for row in value["policies"]
    )
    assert all(
        row["source_rate_projection_exact"] for row in value["policies"]
    )
    assert all(row["inference"]["pass"] for row in value["policies"])
    assert value["formal_behavior_cells_executed"] == 0
    authority = value["authority"]
    assert authority["nominal_behavior_preregistration_authorized"] is True
    assert authority["behavior_evaluation_authorized"] is False
    assert authority["gate5_authorized"] is False
