from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t243b_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t243b_abi_helper_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t243b_abi_helper_recovery.py"
    ).read_text(encoding="utf-8")
    assert "exactly_one_partial_half_graph" in builder
    assert "failure_is_exact_path_vs_model_helper_mismatch" in builder
    assert "failure_occurs_after_graph_save_before_inference" in builder
    assert "structure_from_existing" in runner
    assert "partial_graph_overwrites" in runner
    assert "source_transform_logic_changes" in runner
    assert '"simulator_steps": 0' in runner


def test_t243b_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t243b_abi_helper_recovery_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert not value["failed_checks"]
    assert value["recovery"]["reuse_partial_half_graph"]
    assert value["recovery"]["overwrite_partial_graph"] is False
    assert value["recovery"]["construct_only_missing_final_graph"]
    assert value["authority"]["gate5"] is False


def test_t243b_result_when_present() -> None:
    path = ANALYSIS / "t243b_abi_helper_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery"]["partial_graphs_reused"] == 1
    assert value["recovery"]["missing_graphs_constructed"] == 1
    assert value["recovery"]["partial_graph_overwrites"] == 0
    assert value["recovery"]["source_transform_logic_changes"] == 0
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "PASS_T243B_ABI_HELPER_RECOVERY":
        assert not value["failed_checks"]
        assert all(value["checks"].values())
        assert (
            value["decision"]
            == "EARN_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR_"
            "PREREGISTRATION_ONLY"
        )
        assert (
            value["authority"]["targeted_behavior_preregistration"]
            is True
        )
