import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t169b_preregistration_contract() -> None:
    path = ANALYSIS / "t169b_cpu_diagnostic_validity_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T169B_CPU_DIAGNOSTIC_VALIDITY_AUDIT"
    )
    assert value["failed_checks"] == []
    assert value["audit"]["random_population"]["rows"] == 256
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t169b_result_contract() -> None:
    path = ANALYSIS / "t169b_cpu_diagnostic_validity_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["failed_checks"]:
        assert (
            value["status"]
            == "HOLD_T169B_CPU_DIAGNOSTIC_VALIDITY_AUDIT"
        )
        return
    assert value["status"] == "PASS_T169B_CPU_DIAGNOSTIC_VALIDITY_AUDIT"
    assert (
        value["decision"]
        == "EARN_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION_"
        "PREREGISTRATION_ONLY"
    )
    assert value["endpoint_representation"]["float32_bit_exact"] is True
    random = value["random_population"]
    assert random["gate_active_rows"] > 0
    assert random["head_changed_rows"] == random["rows"] == 256
    assert random["conditional_changed_rows"] == random["gate_active_rows"]
    assert random["anchored_changed_rows"] == random["gate_active_rows"]
    assert random["raw_changed_rows"] == 0
    assert (
        random["changed_elements_raw_exact_saturation"]
        == random["anchored_changed_elements"]
    )
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
