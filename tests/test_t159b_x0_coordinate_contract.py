import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t159b_preregistration_contract() -> None:
    path = (
        ANALYSIS / "t159b_x0_coordinate_contract_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T159B_X0_COORDINATE_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["correction"]["graph_or_mechanics_change"] is False
    assert value["execution_now"]["graphs_changed"] == 0
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t159b_result_contract() -> None:
    path = ANALYSIS / "t159b_x0_coordinate_contract_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T159B_X0_COORDINATE_CONTRACT",
        "HOLD_T159B_X0_COORDINATE_CONTRACT",
    }
    assert value["execution"]["graphs_changed"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["checks"]["both_checkpoints_x0_bit_exact"]
