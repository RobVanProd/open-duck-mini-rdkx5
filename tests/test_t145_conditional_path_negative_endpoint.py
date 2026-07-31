from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t145_preregistration_when_present() -> None:
    path = ANALYSIS / "t145_conditional_path_negative_endpoint_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
    )
    assert value["matrix"]["cells"] == 16
    assert "repository_inputs" in value


def test_t145_result_when_present() -> None:
    path = ANALYSIS / "t145_conditional_path_negative_endpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["behavior_cells"] == 16
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["status"] in {
        "PASS_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX",
        "HOLD_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX",
    }
