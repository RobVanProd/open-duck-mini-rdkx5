import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t158_preregistration_contract() -> None:
    path = (
        ANALYSIS
        / "t158_positive_expert_failure_autopsy_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T158_POSITIVE_EXPERT_FAILURE_AUTOPSY"
    )
    assert value["failed_checks"] == []
    assert value["populations"]["moving_pairs"] == 12
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["hosted_compute_units"] == 0
    assert value["execution_now"]["robot_or_rdk_access"] == 0


def test_t158_result_contract() -> None:
    path = ANALYSIS / "t158_positive_expert_failure_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T158_POSITIVE_EXPERT_FAILURE_AUTOPSY",
        "HOLD_T158_POSITIVE_EXPERT_FAILURE_AUTOPSY",
    }
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["summary"]["positive_pitch_leads_count"] == 12
