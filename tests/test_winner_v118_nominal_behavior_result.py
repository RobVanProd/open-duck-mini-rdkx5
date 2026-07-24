import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def test_v118_nominal_result_rejects_nonmonotonic_tightening() -> None:
    value = json.loads(
        (
            ANALYSIS / "winner_v118_nominal_behavior_result.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PASS_WINNER_V118_NOMINAL_BEHAVIOR_VALID_RESULT"
    )
    assert value["failed_validity_checks"] == []
    assert all(value["validity_checks"].values())
    assert value["summary"]["cells"] == 16
    assert value["summary"]["passing_cells"] == 10
    assert value["summary"]["persistent_both_checkpoint_pass"] is False
    assert value["decision"]["status"] == "REJECT_V118_NOMINAL_POLICY"
    checkpoints = {
        row["step"]: row for row in value["per_checkpoint"]
    }
    assert checkpoints[1_003_520]["passing_cells"] == 2
    assert checkpoints[1_003_520]["all_eight_cells_pass"] is False
    assert checkpoints[2_007_040]["passing_cells"] == 8
    assert checkpoints[2_007_040]["all_eight_cells_pass"] is True
    assert checkpoints[1_003_520]["worst_peak_torque_nm"] > (
        1.91229675
    )
    assert checkpoints[2_007_040]["worst_peak_torque_nm"] <= (
        1.91229675
    )
    assert value["authority"][
        "full_frozen_matrix_preregistration_authorized"
    ] is False
