from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t250b_source_contract() -> None:
    builder = (
        ROOT / "tools/build_t250b_reporter_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (ROOT / "tools/run_t250b_reporter_recovery.py").read_text(
        encoding="utf-8"
    )
    assert "failure_is_raw_response_schema_assumption" in builder
    assert "frozen_block_extractors_already_produce_full_handoff" in builder
    assert "corrected_extract_block" in runner
    assert "extract_block" in runner
    assert '"behavior_cells_rerun": 0' in runner
    assert 'golden_cell["handoff"]["response_audit"]' in runner
    assert '"gate5": False' in runner


def test_t250b_preregistration_when_present() -> None:
    path = ANALYSIS / "t250b_reporter_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert not value["failed_checks"]
    assert value["recovery_contract"]["reuse_all_320_behavior_cells"]
    assert value["recovery_contract"]["rerun_behavior_cells"] == 0
    assert not value["authority"]["gate5"]


def test_t250b_result_when_present() -> None:
    path = ANALYSIS / "t250b_reporter_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T250B_REPORTER_RECOVERY"
    assert value["recovery"]["behavior_cells_rerun"] == 0
    assert value["authority"]["versioned_runtime_integration_preregistration"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
