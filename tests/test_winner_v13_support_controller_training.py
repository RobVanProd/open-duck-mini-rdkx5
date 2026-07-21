from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v13_support_controller_training.py"
PREREG = ROOT / "outputs/analysis/winner_v13_support_controller_training_preregistration.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_support_training", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preregistration_is_exact_source_bound_and_offline() -> None:
    module = load()
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    module.validate_preregistration(value)
    assert value["frozen_training"]["optimizer_updates"] == 100
    assert value["frozen_training"]["environments_per_update"] == 80
    assert value["future_gate"]["cells_per_checkpoint"] == 124
    assert value["execution_now"]["robot_or_rdk_access"] == 0


def test_runner_freezes_stage1_and_does_not_execute_formal_gate() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "tree_equal(source_stage1" in source
    assert "formal_support_cells\": 0" in source
    assert "--support-controller-training-authorized" in source
    assert "--hardware-authorized" not in source
    assert "stage2_ppo_loss" in source


def test_workflow_triggers_only_from_frozen_preregistration() -> None:
    workflow = ROOT / ".github/workflows/winner-v13-support-controller-training.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v13_support_controller_training_preregistration.json" in trigger
    assert "run_winner_v13_support_controller_training.py" in source
    assert "--support-controller-training-authorized" in source
    assert "--hardware-authorized" not in source
