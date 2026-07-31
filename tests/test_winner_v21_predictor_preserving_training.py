from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v21_predictor_preserving_training.py"
PREREGISTRATION = ROOT / "outputs/analysis/winner_v21_predictor_preserving_training_preregistration.json"
WORKFLOW = ROOT / ".github/workflows/winner-v21-predictor-preserving-training.yml"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v21_training", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preregistration_freezes_one_predictor_preserving_arm() -> None:
    module = load_runner()
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V21_PREDICTOR_PRESERVING_TRAINING"
    assert value["decision"] == "AUTHORIZE_ONE_100_UPDATE_PREDICTOR_PRESERVING_ARM_ONLY"
    frozen = value["frozen_training"]
    assert frozen["optimizer_updates"] == 100
    assert frozen["persistent_checkpoints"] == {"half": 50, "final": 100}
    assert frozen["predictor_scale"] == 8.393629541414427e-11
    assert frozen["predictor_scale_evaluations"] == 0
    assert len(frozen["trainable_leaves"]) == 12
    assert value["single_change"]["flat_transport_equation_used"] is False
    module.validate_preregistration(value)


def test_runner_uses_explicit_gradient_composition_without_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "for update_index in range(UPDATES)" in source
    assert "v21v2.compose_gradients" in source
    assert "v21.predictor_loss" in source
    assert "v20.joint_recurrent_ppo_loss" in source
    assert "v21v2.save_snapshot" in source
    assert '"optimizer_updates": 100' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "flat_transport" not in source
    assert "--hardware-authorized" not in source


def test_workflow_is_dormant_until_preregistration_commit() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v21_predictor_preserving_training_preregistration.json" in trigger
    assert "8492593761" in source
    assert "--predictor-preserving-training-authorized" in source
    assert "--hardware-authorized" not in source
