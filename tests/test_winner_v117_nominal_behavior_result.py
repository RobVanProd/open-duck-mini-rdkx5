import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def test_v117_nominal_result_is_valid_but_not_persistent() -> None:
    value = json.loads(
        (
            ANALYSIS / "winner_v117_nominal_behavior_result.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PASS_WINNER_V117_NOMINAL_BEHAVIOR_VALID_RESULT"
    )
    assert value["failed_validity_checks"] == []
    assert all(value["validity_checks"].values())
    assert value["summary"]["cells"] == 16
    assert value["summary"]["passing_cells"] == 11
    assert value["summary"]["persistent_both_checkpoint_pass"] is False
    assert value["decision"]["status"] == "REJECT_V117_NOMINAL_POLICY"
    assert value["decision"]["persistent_both_checkpoint_pass"] is False
    checkpoints = {
        row["step"]: row for row in value["per_checkpoint"]
    }
    assert checkpoints[1_003_520]["passing_cells"] == 3
    assert checkpoints[1_003_520]["all_eight_cells_pass"] is False
    assert checkpoints[2_007_040]["passing_cells"] == 8
    assert checkpoints[2_007_040]["all_eight_cells_pass"] is True
    assert value["authority"][
        "full_frozen_matrix_preregistration_authorized"
    ] is False
    assert value["authority"]["gate5_authorized"] is False
