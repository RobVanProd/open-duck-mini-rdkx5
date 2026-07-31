from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v15_pitch_margin_support_training.py"
PREREG = ROOT / "outputs/analysis/winner_v15_pitch_margin_support_training_preregistration.json"
WORKFLOW = ROOT / ".github/workflows/winner-v15-pitch-margin-support-training.yml"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v15_pitch_training", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preregistration_freezes_one_100_update_arm() -> None:
    module = load_runner()
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING"
    assert value["decision"] == "AUTHORIZE_ONE_100_UPDATE_PITCH_MARGIN_SUPPORT_RUN_ONLY"
    assert value["frozen_training"]["optimizer_updates"] == 100
    assert value["frozen_training"]["objective_scale"] is None
    assert value["frozen_training"]["source_stage1_snapshot_sha256"] == (
        module.STAGE1_SNAPSHOT_SHA256
    )
    assert value["single_change"]["no_scale_search"] is True
    assert value["future_gate"]["executed_now"] is False
    module.validate_preregistration(value)


def test_runner_uses_only_pitch_margin_rollout_and_cpu() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "pitch_margin.stage2_rollout" in source
    assert "enabled=True" in source
    assert "range(UPDATES)" in source
    assert "UPDATES = 100" in source
    assert "stage1_parameters" in source
    assert "formal_support_cells" in source
    assert "--hardware-authorized" not in source


def test_workflow_recovers_exact_stage1_and_runs_once() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v15_pitch_margin_support_training_preregistration.json" in trigger
    assert "8492593761" in source
    assert "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af" in source
    assert "--pitch-margin-support-training-authorized" in source
    assert "--hardware-authorized" not in source
