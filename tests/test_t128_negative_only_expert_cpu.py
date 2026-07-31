from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t128_cpu_preregistration_when_present() -> None:
    path = ANALYSIS / "t128_negative_only_expert_cpu_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T128_NEGATIVE_ONLY_EXPERT_CPU_CONTRACT"
    )
    assert value["mechanism"]["network_capacity_change"] is False
    assert value["mechanism"]["body_configuration_population"] == [
        {
            "fraction": 1.0,
            "name": "torso_com_x_neg",
            "torso_com_offset_m": [-0.05, 0.0, 0.0],
        }
    ]
    assert value["authority"]["hosted_training"] is False


def test_t128_cpu_result_when_present() -> None:
    path = ANALYSIS / "t128_negative_only_expert_cpu_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T128_NEGATIVE_ONLY_EXPERT_CPU_CONTRACT"
    )
    assert value["model_contract"]["offsets_bit_exact"] is True
    assert value["checks"]["only_negative_expert_actor_changed"] is True
    assert value["authority"]["hosted_training"] is False
