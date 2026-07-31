from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t132_preregistration_when_present() -> None:
    path = ANALYSIS / "t132_t129_nominal_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T132_T129_NOMINAL_MATRIX"
    assert value["matrix"] == {
        "cells": 16,
        "both_checkpoints_required": True,
        "no_checkpoint_selection": True,
    }
    assert value["authority"]["training"] is False


def test_t132_result_when_present() -> None:
    path = ANALYSIS / "t132_t129_nominal_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T132_T129_NOMINAL_MATRIX"
        assert value["decision"] == (
            "EARN_T133_T129_NEGATIVE_ENDPOINT_PREREGISTRATION_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T132_T129_NOMINAL_MATRIX"
        assert value["decision"] == (
            "CLOSE_T129_NEGATIVE_ONLY_EXPERT_TRAINTHROUGH"
        )
