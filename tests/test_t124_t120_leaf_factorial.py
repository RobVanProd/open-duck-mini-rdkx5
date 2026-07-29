from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t124_preregistration_when_present() -> None:
    path = ANALYSIS / "t124_t120_leaf_factorial_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T124_T120_LEAF_FACTORIAL"
    assert sorted(value["factorial"]["variants"]) == ["FF", "FH", "HF", "HH"]
    assert value["authority"]["training"] is False


def test_t124_result_when_present() -> None:
    path = ANALYSIS / "t124_t120_leaf_factorial_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T124_T120_LEAF_FACTORIAL"
    assert value["classification"] in {
        "ROUTER_DOMINANT",
        "EXPERT_DOMINANT",
        "INTERACTION_DOMINANT",
    }
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
