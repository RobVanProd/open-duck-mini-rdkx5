from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v36_support_oracle_shooting_feasibility.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v36_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_oracle_screen_scope_is_exact() -> None:
    module = load()
    assert module.CONFIGURATION_IDS == ("COM_X_NEG",)
    assert module.PITCH_INDICES == (2, 3, 4, 11, 12, 13)
    assert module.TICKS == 250
    assert module.HORIZON_TICKS == 8
    assert module.ACTION_BLOCK_TICKS == 2
    assert module.BLOCKS == 4
    assert module.POPULATION == 64
    assert module.ELITES == 8
    assert module.ITERATIONS == 4
    assert module.INITIAL_STD == 0.20
    assert module.MINIMUM_STD == 0.03
    assert module.ROOT_SEED == 120120


def test_block_expansion_controls_only_frozen_pitch_indices() -> None:
    module = load()
    blocks = np.arange(24, dtype=np.float32).reshape(4, 6) / np.float32(24.0)
    expanded = module.expand_blocks(blocks)
    assert expanded.shape == (8, 14)
    np.testing.assert_array_equal(expanded[0], expanded[1])
    np.testing.assert_array_equal(expanded[2], expanded[3])
    np.testing.assert_array_equal(expanded[4], expanded[5])
    np.testing.assert_array_equal(expanded[6], expanded[7])
    np.testing.assert_array_equal(expanded[:, list(module.PITCH_INDICES)][::2], blocks)
    nonpitch = sorted(set(range(14)) - set(module.PITCH_INDICES))
    np.testing.assert_array_equal(expanded[:, nonpitch], np.zeros((8, 8), dtype=np.float32))


def test_runner_has_no_optimizer_training_hardware_or_deployment_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "training.adam_step" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"runtime_oracle_or_action_wrapper_authorized": False' in source
    assert "smoke.bounded_action_numpy" in source


def test_pass_requires_both_full_horizon_anchor_cells() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"both_plants_pass_full_250_tick_support_gate"' in source
    assert 'row["support_pass"] for row in cells' in source
    assert '"all_selected_actions_graph_bounded"' in source
    assert '"all_cells_use_nonzero_control"' in source
    assert "closest" not in source.lower()
