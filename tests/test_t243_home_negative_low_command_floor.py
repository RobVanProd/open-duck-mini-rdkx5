from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t243_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t243_home_negative_low_command_floor_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t243_home_negative_low_command_floor.py"
    ).read_text(encoding="utf-8")
    assert "automatic_context_high_tail_is_only_home_negative" in builder
    assert "reference_feature_atom_same_for_three_commands" in builder
    assert "t243_home_negative_low_command_gate" in runner
    assert "t234_exact_command_gate" in runner
    assert "all_non_targets_exact_source" in runner
    assert "transformed_exact_source_x0077" in runner
    assert '"simulator_steps": 0' in runner
    assert '"optimizer_steps": 0' in runner


def test_t243_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t243_home_negative_low_command_floor_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert not value["failed_checks"]
    assert len(value["graphs"]) == 2
    assert len(value["router"]["tail_rows"]) == 2
    assert {
        row["condition_id"] for row in value["router"]["tail_rows"]
    } == {"HOME_JOINT_OFFSET_NEG"}
    assert value["router"]["manual_measurements"] is False
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["authority"]["gate5"] is False


def test_t243_result_when_present() -> None:
    path = ANALYSIS / "t243_home_negative_low_command_floor_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "PASS_T243_HOME_NEGATIVE_LOW_COMMAND_FLOOR":
        assert not value["failed_checks"]
        assert all(value["checks"].values())
        assert (
            value["decision"]
            == "EARN_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR_"
            "PREREGISTRATION_ONLY"
        )
        assert (
            value["authority"]["targeted_behavior_preregistration"]
            is True
        )
