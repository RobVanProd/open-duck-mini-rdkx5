from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v78_missing_teacher_extension.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v78_runner_test", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_teacher_extension_scope_is_exact() -> None:
    module = load_runner()
    assert module.CONFIGURATION_ID == "COM_CORNER_07"
    assert module.PLANTS == (
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
    )
    assert module.TARGETS == 729
    assert module.TICKS == 250


def test_runner_reuses_reviewed_grid_selection_without_training_or_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "v41.candidate_coordinates()" in source
    assert "v41.candidate_key" in source
    assert "v41_v2.expand_static_target" in source
    assert "training.adam_step" not in source
    assert "np.random" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"closest_result_selection": False' not in source
