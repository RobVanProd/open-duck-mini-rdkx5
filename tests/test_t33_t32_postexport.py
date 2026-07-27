from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t33_preregistration_is_cpu_transform_only() -> None:
    value = load("t33_t32_postexport_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T33_T32_POSTEXPORT_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert value["postupdate_steps"] == [1_003_520, 2_007_040]
    assert value["authority"]["one_cpu_only_postexport_transform"]
    assert not value["authority"]["behavior_evaluation"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t33_transform_reproduces_t31_and_earns_nominal_prereg() -> None:
    value = load("t33_t32_postexport_result.json")
    assert value["status"] == "PASS_T33_T32_POSTEXPORT_TRANSFORM"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["onnx_graphs_transformed"] == 3
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["decision"] == "EARN_T33_NOMINAL_MATRIX_PREREGISTRATION"
    assert value["authority"]["nominal_matrix_preregistration_authorized"]
    assert not value["authority"]["behavior_evaluation_authorized"]
    assert not value["authority"]["gate5_authorized"]
    assert not value["authority"]["rdkx5_or_robot"]
