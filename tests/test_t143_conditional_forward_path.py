from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t143_preregistration_when_present() -> None:
    path = ANALYSIS / "t143_conditional_forward_path_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T143_CONDITIONAL_FORWARD_PATH_TRANSFORM"
    )
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t143_result_when_present() -> None:
    path = ANALYSIS / "t143_conditional_forward_path_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T143_CONDITIONAL_FORWARD_PATH_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert value["checks"]["all_selected_source_outputs_bit_exact"]
    assert value["checks"]["all_graph_transforms_exact"]
    assert value["execution"]["formal_behavior_cells"] == 0
