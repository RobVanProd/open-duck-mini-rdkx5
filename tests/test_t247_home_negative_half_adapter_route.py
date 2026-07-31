from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t247_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t247_home_negative_half_adapter_route_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t247_home_negative_half_adapter_route.py"
    ).read_text(encoding="utf-8")
    assert "only_two_nominal_adapter_tensors_differ" in builder
    assert "same_transform_both_checkpoints" in builder
    assert "t247_home_negative_half_adapter" in runner
    assert "all_tail_exact_half_source" in runner
    assert "failed_final_trace_maps_exactly_to_half" in runner
    assert '"simulator_steps": 0' in runner


def test_t247_result_when_present() -> None:
    path = ANALYSIS / "t247_home_negative_half_adapter_route_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "PASS_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE":
        assert not value["failed_checks"]
        assert all(value["checks"].values())
        assert (
            value["decision"]
            == "EARN_T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX_"
            "PREREGISTRATION_ONLY"
        )
        assert value["authority"]["behavior_matrix_preregistration"]
