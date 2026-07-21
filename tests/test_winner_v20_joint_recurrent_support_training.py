from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v20_joint_recurrent_support_training.py"
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_training_preregistration.json"
)
WORKFLOW = ROOT / ".github/workflows/winner-v20-joint-recurrent-support-training.yml"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v20_training", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preregistration_freezes_the_one_variable_causal_ab() -> None:
    module = load_runner()
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING"
    )
    assert value["decision"] == (
        "AUTHORIZE_ONE_100_UPDATE_JOINT_RECURRENT_CAUSAL_AB_ONLY"
    )
    frozen = value["frozen_training"]
    assert frozen["source_stage1_snapshot_sha256"] == module.STAGE1_SNAPSHOT_SHA256
    assert frozen["source_stage1_snapshot_bytes"] == module.STAGE1_SNAPSHOT_BYTES
    assert frozen["optimizer_updates"] == 100
    assert frozen["persistent_checkpoints"] == {"half": 50, "final": 100}
    assert frozen["objective_scale"] is None
    assert frozen["hidden_replay_population"] == "valid_mask == 1 sampled ticks only"
    module.validate_preregistration(value)


def test_runner_trains_joint_core_without_wrapper_or_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "for update_index in range(UPDATES)" in source
    assert "v20.joint_recurrent_ppo_loss" in source
    assert "v20.joint_trainable_parameters" in source
    assert "v20.frozen_auxiliary_parameters" in source
    assert "v20.stage2_rollout" in source
    assert "maximum_target_offset" not in source
    assert "flat_transport" not in source
    assert '"optimizer_updates": 100' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "--hardware-authorized" not in source


def test_workflow_is_dormant_until_training_preregistration_commit() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v20_joint_recurrent_support_training_preregistration.json" in trigger
    assert "8492593761" in source
    assert "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af" in source
    assert "--joint-recurrent-support-training-authorized" in source
    assert "--hardware-authorized" not in source
