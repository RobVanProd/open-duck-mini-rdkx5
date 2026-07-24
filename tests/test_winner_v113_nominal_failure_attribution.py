import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v113_nominal_failure_attribution.json"
)


def test_v113_attribution_selects_boundary_linear_hinge_only() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V113_NOMINAL_FAILURE_ATTRIBUTION"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["summary"]["failing_cells"] == 11
    counts = value["summary"]["failure_joint_cell_counts"]
    assert counts["left_knee"] == 3
    assert counts["left_ankle"] == 11
    assert sum(count for name, count in counts.items() if name not in {
        "left_knee",
        "left_ankle",
    }) == 0
    assert value["summary"]["maximum_exceeding_ticks_per_cell"] == 12
    objective = value["objective_diagnosis"]
    assert objective["default_off_scale"] == 0.0
    assert objective["training_scale"] < 0.0
    assert "linear torque exceedance" in objective["selected_option"]
    assert value["decision"] == (
        "PREREGISTER_LINEAR_TORQUE_EXCEEDANCE_CPU_CONTRACT"
    )
    assert value["authority"]["training_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
