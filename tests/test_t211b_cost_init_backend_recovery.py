from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t211b_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t211b_cost_init_backend_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t211b_cost_init_backend_recovery.py"
    ).read_text(encoding="utf-8")
    assert "step_zero_cost_tree_reproducible_bit_exact" in builder
    assert "np.finfo(np.float32).eps" in builder
    assert "post_hoc_tolerance_tuning" in builder
    assert "maximum_delta_within_one_float32_epsilon" in runner
    assert "checkpoint_restores" in runner
    assert '"optimizer_steps": 0' in runner
    assert '"simulator_transitions": 0' in runner
    assert '"onnx_inferences": 0' in runner
    assert '"behavior_cells": 0' in runner


def test_t211b_result_when_present() -> None:
    path = ANALYSIS / "t211b_cost_init_backend_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T211B_COST_INIT_BACKEND_RECOVERY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "RECOVER_T211_AND_EARN_T212_T210_POSTEXPORT_"
        "COMPOSITION_PREREGISTRATION_ONLY"
    )
    assert (
        value["comparison"]["maximum_absolute_leaf_delta"]
        <= value["comparison"]["absolute_tolerance"]
    )
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["onnx_inferences"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["behavior"] is False
    assert value["authority"]["gate5"] is False
