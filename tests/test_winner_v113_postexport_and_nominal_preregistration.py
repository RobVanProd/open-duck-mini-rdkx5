import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v113_transform_contract_is_exact_and_behavior_free() -> None:
    prereg = load("winner_v113_postexport_transform_preregistration.json")
    contract = load("winner_v113_postexport_transform_contract.json")
    assert prereg["status"] == "PREREGISTERED_WINNER_V113_POSTEXPORT_TRANSFORM"
    assert prereg["failed_checks"] == []
    assert all(prereg["checks"].values())
    assert contract["status"] == "PASS_WINNER_V113_POSTEXPORT_TRANSFORM_CONTRACT"
    assert contract["failed_checks"] == []
    assert all(contract["checks"].values())
    assert contract["formal_behavior_cells_executed"] == 0
    assert [row["step"] for row in contract["policies"]] == [
        1_003_520,
        2_007_040,
    ]
    assert all(row["inference"]["pass"] for row in contract["policies"])
    assert contract["authority"]["behavior_evaluation_authorized"] is False
    assert contract["authority"]["gate5_authorized"] is False


def test_v113_nominal_matrix_freezes_both_checkpoints_and_plants() -> None:
    value = load("winner_v113_nominal_behavior_preregistration.json")
    assert value["status"] == "PREREGISTERED_WINNER_V113_NOMINAL_BEHAVIOR"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    rows = value["matrix"]["rows"]
    assert len(rows) == 16
    assert {row["step"] for row in rows} == {1_003_520, 2_007_040}
    assert {row["plant"] for row in rows} == {
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
    }
    assert {row["command_x_m_s"] for row in rows} == {
        0.0,
        0.074,
        0.077,
        0.080,
    }
    assert value["authority"]["formal_behavior_cells_authorized"] == 16
    assert value["authority"]["full_matrix_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
