from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t246_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t246_checkpoint_adapter_autopsy_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t246_checkpoint_adapter_autopsy.py"
    ).read_text(encoding="utf-8")
    assert "t245_split_is_exact_half_pass_final_failure" in builder
    assert "expected_different_initializers" in builder
    assert "trajectory_equal" in runner
    assert "exactly_two_nominal_adapter_initializers_differ" in runner
    assert "half_adapter_counterfactual_is_action_sensitive" in runner
    assert '"simulator_steps": 0' in runner


def test_t246_result_when_present() -> None:
    path = ANALYSIS / "t246_checkpoint_adapter_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "PASS_T246_CHECKPOINT_ADAPTER_CAUSAL_SPLIT":
        assert not value["failed_checks"]
        assert all(value["checks"].values())
        assert value["graph_identity"]["changed_nodes"] == []
        assert value["graph_identity"]["changed_initializers"] == [
            "nominal_condition_negative_adapter_bias",
            "nominal_condition_negative_adapter_weight",
        ]
        assert (
            value["decision"]
            == "EARN_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE_"
            "PREREGISTRATION_ONLY"
        )
        assert value["authority"]["adapter_route_preregistration"]
