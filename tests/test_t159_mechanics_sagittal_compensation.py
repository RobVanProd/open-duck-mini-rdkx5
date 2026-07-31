import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t159_preregistration_contract() -> None:
    path = (
        ANALYSIS
        / "t159_mechanics_sagittal_compensation_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T159_MECHANICS_SAGITTAL_COMPENSATION"
    )
    assert value["failed_checks"] == []
    assert value["mechanics"]["scalar_search"] is False
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["hosted_compute_units"] == 0
    assert value["execution_now"]["robot_or_rdk_access"] == 0


def test_t159_result_contract() -> None:
    path = ANALYSIS / "t159_mechanics_sagittal_compensation_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T159_MECHANICS_SAGITTAL_COMPENSATION",
        "HOLD_T159_MECHANICS_SAGITTAL_COMPENSATION",
    }
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["checks"]["mechanics_root_converged"]
        assert value["checks"]["all_selected_source_outputs_bit_exact"]
