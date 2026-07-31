from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t118_preregistration_when_present() -> None:
    path = ANALYSIS / "t118_routing_failure_attribution_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T118_ROUTING_FAILURE_ATTRIBUTION"
    )
    assert value["decision_rule"]["hosted_training"] is False
    assert value["authority"]["rdkx5_or_robot"] is False


def test_t118_result_when_present() -> None:
    path = ANALYSIS / "t118_routing_failure_attribution_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if not value["failed_checks"]:
        assert value["status"] == "PASS_T118_ROUTING_FAILURE_ATTRIBUTION"
        assert value["classification"] == (
            "FIXED_ROUTER_UNTRAINED_FOR_CLOSED_LOOP"
        )
        assert value["decision"] == (
            "EARN_T119_JOINT_SOFT_ROUTER_EXPERT_CPU_PREREGISTRATION_ONLY"
        )
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
