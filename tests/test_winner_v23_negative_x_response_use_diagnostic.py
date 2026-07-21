from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v23_negative_x_response_use_diagnostic.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v23_diagnostic", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_persistent_crossing_requires_five_ticks() -> None:
    module = load()
    values = np.asarray([0.0, 2.0, 2.0, 2.0, 2.0, 0.0, 2.0, 2.0, 2.0, 2.0, 2.0])
    assert module.first_persistent_crossing(values, 1.0) == 6


def test_runner_freezes_read_only_pair_and_fork_contract() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "EARLY_TICKS = 25" in source
    assert "MIN_PERSISTENT_TICKS = 5" in source
    assert "HIDDEN_LINF_THRESHOLD = 1.0e-7" in source
    assert "FORK_ACTION_LINF_THRESHOLD = 1.0e-5" in source
    assert "MIN_DECISION_CELLS = 16" in source
    assert "same_input_hidden_fork_action_linf_by_tick" in source
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "adam_step" not in source
    assert "--hardware-authorized" not in source
