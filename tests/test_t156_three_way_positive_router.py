import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t156_preregistration_contract() -> None:
    path = ANALYSIS / "t156_three_way_positive_router_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T156_THREE_WAY_POSITIVE_ROUTER_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert value["classifier"]["scalar_search"] is False
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["execution_now"]["hosted_compute_units"] == 0
    assert value["execution_now"]["robot_or_rdk_access"] == 0


def test_t156_result_contract() -> None:
    path = ANALYSIS / "t156_three_way_positive_router_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T156_THREE_WAY_POSITIVE_ROUTER_TRANSFORM",
        "HOLD_T156_THREE_WAY_POSITIVE_ROUTER_TRANSFORM",
    }
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["checks"]["two_positive_contexts_hash_exact"]
        assert value["checks"]["all_selected_source_outputs_bit_exact"]
