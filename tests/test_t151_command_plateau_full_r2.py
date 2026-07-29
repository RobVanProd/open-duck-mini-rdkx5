from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t151_preregistration_when_present() -> None:
    path = ANALYSIS / "t151_command_plateau_full_r2_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T151_COMMAND_PLATEAU_FULL_R2"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 320
    assert value["matrix"]["maximum_new_conditions_per_invocation"] == 1


def test_t151_result_when_present() -> None:
    path = ANALYSIS / "t151_command_plateau_full_r2_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T151_COMMAND_PLATEAU_FULL_R2",
        "HOLD_T151_COMMAND_PLATEAU_FULL_R2",
    }
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["authority"]["gate5_hardware_authorized"] is False
