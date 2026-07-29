import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t156b_preregistration_contract() -> None:
    path = (
        ANALYSIS / "t156b_positive_router_gap_midpoint_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T156B_POSITIVE_ROUTER_GAP_MIDPOINT"
    )
    assert value["failed_checks"] == []
    assert value["boundary_rule"]["scalar_search"] is False
    assert value["execution_now"]["calibration_prefixes"] == 0
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["hosted_compute_units"] == 0
    assert value["execution_now"]["robot_or_rdk_access"] == 0


def test_t156b_result_contract() -> None:
    path = ANALYSIS / "t156b_positive_router_gap_midpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T156B_POSITIVE_ROUTER_GAP_MIDPOINT",
        "HOLD_T156B_POSITIVE_ROUTER_GAP_MIDPOINT",
    }
    assert value["execution"]["calibration_prefixes"] == 0
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["checks"]["only_intercept_initializer_changed"]
        assert value["checks"]["all_selected_source_outputs_bit_exact"]
