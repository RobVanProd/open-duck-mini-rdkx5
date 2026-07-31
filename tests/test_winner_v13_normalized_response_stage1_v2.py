from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v13_normalized_response_stage1_v2.py"
PREREG = ROOT / "outputs/analysis/winner_v13_normalized_response_stage1_v2_preregistration.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_stage1_v2", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preregistration_is_fresh_exact_and_source_bound() -> None:
    module = load()
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    module.validate_preregistration(value)
    assert value["status"] == "PREREGISTERED_WINNER_V13_NORMALIZED_RESPONSE_STAGE1_V2"
    assert value["frozen_training"]["learning_rate"] == 0.0001
    assert value["correction_from_invalid_run"]["training_change"].startswith("none")
    assert value["execution_now"]["stage1_optimizer_updates"] == 0


def test_corrected_evaluator_has_same_input_checks() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "networks.calibrator_step" in source
    assert "maximum_same_input_errors" in source
    assert "checker_same_input_all_outputs_at_most_1e_7" in source
    assert "checker_nonzero_bounded_action_observed" in source
    assert "checker_zero_previous_action_exact_zero" in source
    assert "checker_onnx_action_exact_zero" not in source
    assert "--hardware-authorized" not in source


def test_workflow_is_dormant_until_v2_preregistration_commit() -> None:
    workflow = ROOT / ".github/workflows/winner-v13-normalized-response-stage1-v2.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v13_normalized_response_stage1_v2_preregistration.json" in trigger
    assert "run_winner_v13_normalized_response_stage1_v2.py" in source
    assert "--stage1-training-authorized" in source
    assert "--hardware-authorized" not in source
