from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t242b_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t242b_interrupted_reporter_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t242b_interrupted_reporter_recovery.py"
    ).read_text(encoding="utf-8")
    assert "exactly_one_completed_first_block" in builder
    assert "no_unmanifested_partial_cache_files" in builder
    assert "KeyError: 'evaluation_path'" in builder
    assert "run_missing_cells" in builder
    assert "reporter_alias_in_memory_only" in runner
    assert '"simulator_calls": 0' in runner
    assert '"remaining_cells_not_run": 12' in runner


def test_t242b_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t242b_interrupted_reporter_recovery_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert not value["failed_checks"]
    assert len(value["completed_blocks"]) == 1
    assert value["recovery"]["read_only"]
    assert value["recovery"]["rerun_completed_cells"] is False
    assert value["recovery"]["run_missing_cells"] is False
    assert value["authority"]["gate5"] is False


def test_t242b_result_when_present() -> None:
    path = (
        ANALYSIS / "t242b_interrupted_reporter_recovery_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery"]["completed_blocks_reused"] == 1
    assert value["recovery"]["completed_cells_reused"] == 4
    assert value["recovery"]["new_behavior_cells"] == 0
    assert value["recovery"]["remaining_cells_not_run"] == 12
    assert value["execution"]["simulator_calls"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "HOLD_T242B_INTERRUPTED_REPORTER_RECOVERY":
        assert value["block"]["green_cells"] < 4
        assert value["decision"].startswith(
            "CLOSE_BOUNDED_POSITIVE_ROUTER"
        )
        assert (
            value["authority"][
                "t242c_missing_block_recovery_preregistration"
            ]
            is False
        )
