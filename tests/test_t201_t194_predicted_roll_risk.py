from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t201_t194_predicted_roll_risk import (  # noqa: E402
    predicted_roll_risk,
)


ANALYSIS = ROOT / "outputs" / "analysis"


def test_predicted_roll_risk() -> None:
    roll = np.asarray([0.1, -0.2], np.float64)
    rate = np.asarray([1.0, -1.0], np.float64)
    actual = predicted_roll_risk(roll, rate, 0.08)
    np.testing.assert_allclose(actual, [0.18, 0.28])


def test_t201_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t201_t194_predicted_roll_risk_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T201_T194_PREDICTED_ROLL_RISK"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["traces"]) == 16
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False


def test_t201_result_when_present() -> None:
    path = ANALYSIS / "t201_t194_predicted_roll_risk_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T201_T194_PREDICTED_ROLL_RISK"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["behavior"] is False
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
