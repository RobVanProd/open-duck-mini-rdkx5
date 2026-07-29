from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t150_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t150_negative_command_plateau_endpoint_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T150_NEGATIVE_COMMAND_PLATEAU_ENDPOINT"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"]


def test_t150_result_when_present() -> None:
    path = ANALYSIS / "t150_negative_command_plateau_endpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T150_NEGATIVE_COMMAND_PLATEAU_ENDPOINT"
    )
    assert value["condition"]["green_cells"] == 16
    assert value["execution"]["hosted_compute_units"] == 0
