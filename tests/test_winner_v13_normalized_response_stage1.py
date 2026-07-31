from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v13_normalized_response_stage1_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v13_normalized_response_stage1.py"
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v13_normalized_response_stage1_preregistration.json"
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cpu_result_exactly_authorizes_stage1_preregistration() -> None:
    builder = load(BUILDER, "winner_v13_stage1_builder")
    value = json.loads(builder.CPU_RESULT.read_text(encoding="utf-8"))
    builder.validate_cpu_authorization(value)
    assert value["decision"] == "AUTHORIZE_NORMALIZED_RESPONSE_STAGE1_PREREGISTRATION_ONLY"
    assert value["execution"]["full_training_updates"] == 0


def test_preregistration_is_source_bound_and_has_no_execution() -> None:
    runner = load(RUNNER, "winner_v13_stage1_runner")
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
    assert value["decision"] == "AUTHORIZE_ONE_100_UPDATE_STAGE1_RUN_ONLY"
    assert value["execution_now"] == {
        "stage1_optimizer_updates": 0,
        "stage2_optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    runner.validate_preregistration(value)


def test_stage1_training_scope_and_gate_are_exact() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    training = value["frozen_training"]
    gate = value["heldout_gate"]
    assert training["optimizer_updates"] == 100
    assert training["environments_per_update"] == 80
    assert training["ticks_per_environment"] == 250
    assert training["training_episode_slots"] == 2_000_000
    assert training["action_head"] == "initialized at exact zero and bit-exact frozen"
    assert training["persistent_checkpoints"] == {"final": 100, "half": 50}
    assert gate["cells"] == 64
    assert gate["deterministic_repeat_cells"] == 64
    assert len(gate["required_per_checkpoint_checks"]) == 9
    assert value["required_run_checks"] == [
        "exact_100_optimizer_updates",
        "exact_100_immutable_snapshots",
        "half_and_final_evaluated",
        "both_checkpoints_pass_heldout_gate",
        "action_head_bit_exact",
    ]


def test_runner_contains_only_stage1_and_fail_closed_heldout_rules() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "for update_index in range(UPDATES)" in source
    assert "UPDATES = 100" in source
    assert 'CHECKPOINTS = {50: "half", 100: "final"}' in source
    assert "learned_strictly_below_constant" in source
    assert "separation > 1.0e-7" in source
    assert '"stage2_optimizer_updates": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"locomotion_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "--stage1-training-authorized" in source
    assert "--hardware-authorized" not in source


def test_workflow_is_cpu_only_and_dormant_until_preregistration_commit() -> None:
    workflow = ROOT / ".github/workflows/winner-v13-normalized-response-stage1.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v13_normalized_response_stage1_preregistration.json" in trigger
    assert "winner_v13_normalized_response_stage1.py" not in trigger
    assert "--offline-cpu-only" in source
    assert "--stage1-training-authorized" in source
    assert "--hardware-authorized" not in source
    assert "sleep 60" in source
