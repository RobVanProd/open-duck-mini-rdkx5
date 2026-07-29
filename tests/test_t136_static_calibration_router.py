from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t136_preregistration_when_present() -> None:
    path = ANALYSIS / "t136_static_calibration_router_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM"
    )
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t136_result_when_present() -> None:
    path = ANALYSIS / "t136_static_calibration_router_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert value["checks"]["all_calibration_labels_exact"]
    assert value["checks"]["all_x0_paths_exact_zero"]
    assert value["execution"]["formal_behavior_cells"] == 0
