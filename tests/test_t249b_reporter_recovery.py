from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t249b_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t249b_reporter_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (ROOT / "tools/run_t249b_reporter_recovery.py").read_text(
        encoding="utf-8"
    )
    assert "failure_is_reporter_type_mismatch" in builder
    assert "condition_19_first_block_complete_and_cached" in builder
    assert "partial_behavior_is_not_rerun" in builder
    assert "extract_joint_offset_with_corrected_helper" in builder
    assert "extract_all_other_conditions_with_frozen_r2_helper" in builder
    assert "if \"joint_qpos0_offset_rad\" in condition[\"override\"]" in runner
    assert "block_manifests" in runner
    assert '"completed_cells_rerun": 0' in runner
    assert '"optimizer_steps": 0' in runner


def test_t249b_result_when_present() -> None:
    path = ANALYSIS / "t249b_reporter_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery"]["reporter_only"]
    assert value["recovery"]["completed_cells_rerun"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    assert len(value["block_manifests"]) in {4, 8, 12}
    if value["status"] == "PASS_T249B_REPORTER_RECOVERY":
        assert value["summary"]["all_twenty_conditions_green"]
        assert value["summary"]["green_conditions"] == 20
        assert value["summary"]["green_cells"] == 320
        assert len(value["block_manifests"]) == 12
        assert (
            value["decision"]
            == "EARN_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_"
            "PREREGISTRATION_ONLY"
        )
        assert value["authority"][
            "offline_deployment_contract_audit_preregistration"
        ]
