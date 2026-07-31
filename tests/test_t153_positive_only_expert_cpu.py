from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t153_cpu_preregistration_when_present() -> None:
    path = ANALYSIS / "t153_positive_only_expert_cpu_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T153_POSITIVE_ONLY_EXPERT_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["body_configuration_population"] == [
        {
            "fraction": 1.0,
            "name": "torso_com_x_pos",
            "torso_com_offset_m": [0.05, 0.0, 0.0],
        }
    ]
    assert value["training"]["formal_behavior_cells"] == 0
    assert value["authority"]["hosted_training"] is False


def test_t153_cpu_result_when_present() -> None:
    path = ANALYSIS / "t153_positive_only_expert_cpu_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T153_POSITIVE_ONLY_EXPERT_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["checks"]["only_positive_expert_slot_actor_changed"] is True
    assert value["checks"]["source_is_same_as_t128"] is True
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
