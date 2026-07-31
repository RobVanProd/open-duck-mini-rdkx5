from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v35_full_horizon_source_continuation.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v35_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_full_horizon_hybrid_scope_is_exact() -> None:
    module = load()
    assert len(module.CONFIGURATION_IDS) == 15
    assert module.CHECKPOINTS == (("half", 251), ("final", 301))
    assert module.RIGHT_PITCH_INDICES == (11, 12, 13)
    assert module.PREFIX_TICKS == 8
    assert module.TICKS == 250


def test_runner_has_no_optimizer_training_hardware_or_runtime_wrapper() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "training.adam_step" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"runtime_hybrid_or_action_wrapper_authorized": False' in source
    assert "if tick < PREFIX_TICKS" in source
    assert "realized = source_action.copy()" in source


def test_pass_requires_every_hybrid_cell() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"all_60_hybrid_cells_pass_support"' in source
    assert '"all_55_v34_failures_recovered"' in source
    assert '"all_5_v34_passes_preserved"' in source
    assert "closest" not in source.lower()
