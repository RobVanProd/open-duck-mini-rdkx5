from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t109_preregistration_is_uniform_when_present() -> None:
    path = ANALYSIS / "t109_always_on_expert_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T109_ALWAYS_ON_EXPERT_TRANSFORM"
    )
    assert value["transform"]["head_scale"] == 1.0
    assert value["transform"]["scalar_search"] is False
    assert value["transform"]["new_input_or_output"] is False
    assert value["transform"]["new_recurrent_state"] is False
    assert value["authority"]["training"] is False


def test_t109_result_requires_exact_contract_when_present() -> None:
    path = ANALYSIS / "t109_always_on_expert_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["failed_checks"]:
        assert value["status"] == "HOLD_T109_ALWAYS_ON_EXPERT_TRANSFORM"
        assert value["decision"] == "CLOSE_T100C_ALWAYS_ON_EXPERT"
    else:
        assert value["status"] == "PASS_T109_ALWAYS_ON_EXPERT_TRANSFORM"
        assert value["decision"] == (
            "EARN_T110_ALWAYS_ON_EXPERT_NOMINAL_PREREGISTRATION_ONLY"
        )
        assert all(value["checks"].values())
