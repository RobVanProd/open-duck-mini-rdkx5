from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t172_preregistration_when_present() -> None:
    path = ANALYSIS / "t172_t170_postexport_composition_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T172_T170_POSTEXPORT_COMPOSITION"
    )
    assert value["failed_checks"] == []
    assert len(value["graphs"]) == 3
    assert len(value["contexts"]) == 40
    assert value["authority"]["targeted_behavior_matrix"] is False


def test_t172_result_when_present() -> None:
    path = ANALYSIS / "t172_t170_postexport_composition_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T172_T170_POSTEXPORT_COMPOSITION"
    assert value["failed_checks"] == []
    assert value["checks"]["step_zero_model_byte_exact_to_t164_final"]
    assert value["checks"]["trained_graphs_change_only_nominal_pair"]
    assert value["checks"]["all_inactive_routes_bit_exact"]
    assert value["checks"]["all_x0_outputs_bit_exact"]
    assert value["authority"]["behavior_matrix"] is False
