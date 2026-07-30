from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t200_t194_command_chord import window_metrics  # noqa: E402


ANALYSIS = ROOT / "outputs" / "analysis"


def test_window_metrics_zero_curvature() -> None:
    value = window_metrics(
        np.zeros((2, 14), np.float64),
        np.zeros((2, 64), np.float64),
        np.zeros((2, 14), np.float64),
        [f"joint_{index}" for index in range(14)],
    )
    assert value["rows"] == 2
    assert value["action"]["rms"] == 0.0
    assert value["hidden"]["maximum_abs"] == 0.0
    assert len(value["action_joints"]) == 14


def test_t200_preregistration_when_present() -> None:
    path = ANALYSIS / "t200_t194_command_chord_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T200_T194_COMMAND_CHORD"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["analysis"]["commands_x_m_s"] == [0.074, 0.077, 0.08]
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False


def test_t200_result_when_present() -> None:
    path = ANALYSIS / "t200_t194_command_chord_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T200_T194_COMMAND_CHORD"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["behavior"] is False
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
