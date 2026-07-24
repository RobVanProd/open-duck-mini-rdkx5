import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def test_v117_nominal_gate_is_frozen_for_both_checkpoints() -> None:
    value = json.loads(
        (
            ANALYSIS
            / "winner_v117_nominal_behavior_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V117_NOMINAL_BEHAVIOR"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["matrix"]["cells"] == 16
    assert len(value["matrix"]["rows"]) == 16
    assert {row["step"] for row in value["matrix"]["rows"]} == {
        1_003_520,
        2_007_040,
    }
    assert {
        row["plant"] for row in value["matrix"]["rows"]
    } == {
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
    }
    assert {
        row["command_x_m_s"] for row in value["matrix"]["rows"]
    } == {0.0, 0.074, 0.077, 0.080}
    assert all(
        row["duration_ticks"] == 600
        and row["seed"] == 167931544
        for row in value["matrix"]["rows"]
    )
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["execution_now"]["training_steps"] == 0
    assert value["execution_now"]["colab_compute_units"] == 0
    assert value["authority"]["formal_behavior_cells_authorized"] == 16
    assert value["authority"]["full_matrix_authorized"] is False
