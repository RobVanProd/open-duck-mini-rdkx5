import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t168_preregistration_contract() -> None:
    path = (
        ANALYSIS
        / "t168_nominal_adapter_persistence_attribution_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert len(value["traces"]) == 16
    assert sum(row["rows"] for row in value["traces"]) == 8152
    assert value["frozen_test"]["formal_behavior"] is False
    assert value["frozen_test"]["simulator"] is False
    assert value["frozen_test"]["optimizer"] is False


def test_t168_result_contract() -> None:
    path = (
        ANALYSIS / "t168_nominal_adapter_persistence_attribution_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["failed_checks"]:
        assert (
            value["status"]
            == "HOLD_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
        )
        return
    assert (
        value["status"]
        == "PASS_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
    )
    assert (
        value["decision"]
        == "EARN_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT_"
        "PREREGISTRATION_ONLY"
    )
    replay = value["stored_trace_replay"]
    assert replay["rows"] == 8152
    assert replay["nominal_hybrid_matches_final_rows"] == 8152
    assert all(
        rows == 8152
        for rows in replay["inactive_hybrid_matches_half_rows"].values()
    )
    assert replay["half_final_action_different_rows"] > 0
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
