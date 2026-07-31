from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t24_preregisters_only_exact_cpu_postexport_transform() -> None:
    value = load("t24_t23_postexport_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T24_T23_POSTEXPORT_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert list(map(int, value["raw_graphs"])) == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert value["postupdate_steps"] == [1_003_520, 2_007_040]
    assert value["authority"]["one_cpu_only_postexport_transform"] is True
    assert value["authority"]["behavior_evaluation"] is False
    assert value["authority"]["gate5"] is False


def test_t24_transform_passes_without_behavior_authority() -> None:
    value = load("t24_t23_postexport_result.json")
    assert value["status"] == "PASS_T24_T23_POSTEXPORT_TRANSFORM"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"] == {
        "onnx_graphs_transformed": 3,
        "optimizer_steps": 0,
        "simulator_locomotion_steps": 0,
        "formal_behavior_cells": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["decision"] == "EARN_T24_NOMINAL_MATRIX_PREREGISTRATION"
    assert value["authority"]["nominal_matrix_preregistration_authorized"]
    assert value["authority"]["behavior_evaluation_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
