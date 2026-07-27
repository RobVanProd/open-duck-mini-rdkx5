from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t35_preregisters_only_the_failed_t34_cell() -> None:
    payload = load("t35_t32_margin_causality_preregistration.json")
    assert payload["status"] == "PREREGISTERED_T35_T32_MARGIN_CAUSAL_AB"
    assert payload["failed_checks"] == []
    assert payload["cell"] == {
        "condition": {
            "condition_index": 2,
            "id": "FLOOR_FRICTION_HI",
            "override": {"floor_friction": 1.0},
        },
        "checkpoint_id": "T32_PRE_MARGIN_FINAL",
        "fit_id": "p31_34",
        "command_x_m_s": 0.077,
        "seed": 167931544,
        "duration_s": 12.0,
    }
    assert payload["wrapped_failure"]["samples"] == 494
    assert payload["pre_margin_policy"]["step"] == 2007040
    assert payload["authority"]["read_only_trace_attribution"]
    assert not payload["authority"]["training"]
    assert not payload["authority"]["colab"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]


def test_t35_result_has_zero_expanded_authority() -> None:
    path = ANALYSIS / "t35_t32_margin_causality_result.json"
    if not path.is_file():
        pytest.skip("formal T35 result has not run")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] in {
        "PASS_T35_NO_RUNTIME_MARGIN_INTERVENTION",
        "PASS_T35_T32_MARGIN_IS_CAUSAL",
        "PASS_T35_T32_MARGIN_NOT_SUFFICIENT_CAUSE",
    }
    assert payload["execution"]["formal_behavior_cells"] in {0, 1}
    assert payload["execution"]["optimizer_steps"] == 0
    assert not payload["authority"]["training"]
    assert not payload["authority"]["colab"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]
    assert not payload["authority"]["torque_or_motion"]
