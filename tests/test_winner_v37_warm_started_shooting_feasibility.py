from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v37_warm_started_shooting_feasibility.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v37_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_warm_started_screen_preserves_v36_scope() -> None:
    module = load()
    assert module.CONFIGURATION_IDS == ("COM_X_NEG",)
    assert module.PITCH_INDICES == (2, 3, 4, 11, 12, 13)
    assert module.TICKS == 250
    assert module.HORIZON_TICKS == 8
    assert module.ACTION_BLOCK_TICKS == 2
    assert module.POPULATION == 64
    assert module.ELITES == 8
    assert module.ITERATIONS == 4
    assert module.INITIAL_STD == 0.20
    assert module.MINIMUM_STD == 0.03
    assert module.ROOT_SEED == 120120


def test_shift_winning_blocks_is_exact() -> None:
    module = load()
    blocks = np.arange(24, dtype=np.float32).reshape(4, 6)
    shifted = module.shift_winning_blocks(blocks)
    expanded = np.repeat(blocks, 2, axis=0)
    expected_ticks = np.concatenate([expanded[1:], expanded[-1:]], axis=0)
    expected = expected_ticks.reshape(4, 2, 6).mean(axis=1)
    np.testing.assert_array_equal(shifted, expected.astype(np.float32))


def test_only_proposal_mean_is_changed_from_v36() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "import run_winner_v36_support_oracle_shooting_feasibility as v36" in source
    for name in (
        "CONFIGURATION_IDS", "PITCH_INDICES", "TICKS", "HORIZON_TICKS",
        "ACTION_BLOCK_TICKS", "BLOCKS", "POPULATION", "ELITES", "ITERATIONS",
        "INITIAL_STD", "MINIMUM_STD", "ROOT_SEED",
    ):
        assert f"{name} = v36.{name}" in source
    assert "samples[0] = mean" in source
    assert "next_warm_mean = shift_winning_blocks(best_blocks)" in source
    assert '"all_first_actions_match_v36"' in source


def test_runner_has_no_optimizer_training_hardware_or_deployment_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "training.adam_step" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"runtime_oracle_or_action_wrapper_authorized": False' in source
    assert "closest" not in source.lower()
