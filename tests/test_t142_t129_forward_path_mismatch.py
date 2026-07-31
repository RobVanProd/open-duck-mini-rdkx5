from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t142_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t142_t129_forward_path_mismatch_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T142_T129_FORWARD_PATH_MISMATCH_AUDIT"
    )
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t142_result_when_present() -> None:
    path = ANALYSIS / "t142_t129_forward_path_mismatch_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T142_T129_FORWARD_PATH_MISMATCH_AUDIT"
    )
    assert value["failed_checks"] == []
    assert value["classification"] == (
        "T129_TRAINED_ALWAYS_ON_BUT_EVALUATED_HARD_GATED"
    )
    assert value["execution"]["formal_behavior_cells"] == 0
