import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t166_preregistration_contract() -> None:
    path = ANALYSIS / "t166_lateral_persistence_autopsy_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T166_LATERAL_PERSISTENCE_AUTOPSY"
    )
    assert value["failed_checks"] == []
    assert value["populations"]["protected_traces"] == 32
    assert len(value["traces"]) == 32
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["hosted_compute_units"] == 0
    assert value["execution_now"]["robot_or_rdk_access"] == 0


def test_t166_result_contract() -> None:
    path = ANALYSIS / "t166_lateral_persistence_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T166_LATERAL_PERSISTENCE_AUTOPSY",
        "HOLD_T166_LATERAL_PERSISTENCE_AUTOPSY",
    }
    assert value["summary"]["negative_lateral_half_green_cells"] == 3
    assert value["summary"]["negative_lateral_final_green_cells"] == 8
    assert value["summary"]["half_failures"] == 5
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["summary"]["half_roll_leading_failures"] >= 4
