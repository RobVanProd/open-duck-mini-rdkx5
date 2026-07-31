from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t249_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t249_remaining_r2_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (ROOT / "tools/run_t249_remaining_r2.py").read_text(
        encoding="utf-8"
    )
    assert "conditions_1_through_16_green" in builder
    assert "condition_17_green_16_of_16" in builder
    assert "t241_non_home_routes_exact_t237_source" in builder
    assert "t243_non_target_routes_exact_t241_source" in builder
    assert "t247_non_tail_routes_exact_t243_source" in builder
    assert '"conditions_reused": 17' in builder
    assert '"cells_reused": 272' in builder
    assert '"cells_new_maximum": 48' in builder
    assert "maximum_new_conditions_per_invocation" in builder
    assert "reused_cells_rerun" in runner
    assert '"optimizer_steps": 0' in runner


def test_t249_result_when_present() -> None:
    path = ANALYSIS / "t249_remaining_r2_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["reuse"]["conditions_reused"] == 17
    assert value["reuse"]["cells_reused"] == 272
    assert value["reuse"]["reused_cells_rerun"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "PASS_T249_REMAINING_R2":
        assert value["summary"]["matrix_complete"]
        assert value["summary"]["all_twenty_conditions_green"]
        assert value["summary"]["green_conditions"] == 20
        assert value["summary"]["green_cells"] == 320
        assert (
            value["decision"]
            == "EARN_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_"
            "PREREGISTRATION_ONLY"
        )
        assert value["authority"][
            "offline_deployment_contract_audit_preregistration"
        ]
