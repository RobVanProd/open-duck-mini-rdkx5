from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t43_is_zero_weight_worker_contract_invalidation() -> None:
    value = json.loads(
        (ANALYSIS / "t43_worker_contract_invalidation.json").read_text(
            encoding="utf-8"
        )
    )
    assert value["status"] == (
        "PASS_T43_ZERO_CELL_WORKER_CONTRACT_INVALIDATION"
    )
    assert value["decision"] == (
        "CLOSE_T43_ZERO_WEIGHT_NO_RETRY_"
        "EARN_T44_CORRECTED_X008_FACTORIAL_PREREGISTRATION"
    )
    assert value["failed_checks"] == []
    assert value["classification"]["formal_behavior_cells"] == 0
    assert value["classification"]["policy_decision_weight"] == 0
    assert not value["classification"]["policy_pass"]
    assert not value["classification"]["policy_failure"]
    assert not value["classification"]["t43_retry"]
    assert value["correction"]["reuse_t43_variant_assets_exact"]
    assert value["correction"]["execute_all_three_cells"]
    assert value["authority"]["t44_corrected_factorial_preregistration"]
    assert not value["authority"]["t44_execution"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t44_worker_freezes_only_x008() -> None:
    text = (
        ROOT / "tools" / "evaluate_t44_t43_x008_causal_cell.py"
    ).read_text(encoding="utf-8")
    assert "worker.FORMAL_COMMANDS = (0.08,)" in text
    assert "0.077" not in text
