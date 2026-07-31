from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v38_mirrored_pitch_shooting_feasibility.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v38_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mirrored_screen_preserves_v36_scope_and_compute() -> None:
    module = load()
    assert module.CONFIGURATION_IDS == ("COM_X_NEG",)
    assert module.PITCH_INDICES == (2, 3, 4, 11, 12, 13)
    assert module.MIRRORED_DIMENSIONS == 3
    assert module.TICKS == 250
    assert module.HORIZON_TICKS == 8
    assert module.ACTION_BLOCK_TICKS == 2
    assert module.POPULATION == 64
    assert module.ELITES == 8
    assert module.ITERATIONS == 4
    assert module.INITIAL_STD == 0.20
    assert module.MINIMUM_STD == 0.03
    assert module.ROOT_SEED == 120120


def test_mirror_basis_and_block_expansion_are_exact() -> None:
    module = load()
    blocks = np.arange(12, dtype=np.float32).reshape(4, 3) / np.float32(12.0)
    expanded = module.expand_mirrored_blocks(blocks)
    assert expanded.shape == (8, 14)
    for tick in range(0, 8, 2):
        block = blocks[tick // 2]
        np.testing.assert_array_equal(expanded[tick], expanded[tick + 1])
        assert expanded[tick, 2] == -block[0]
        assert expanded[tick, 11] == block[0]
        assert expanded[tick, 3] == expanded[tick, 12] == block[1]
        assert expanded[tick, 4] == expanded[tick, 13] == block[2]
    nonpitch = sorted(set(range(14)) - set(module.PITCH_INDICES))
    np.testing.assert_array_equal(expanded[:, nonpitch], np.zeros((8, 8), dtype=np.float32))


def test_previous_action_projection_is_reviewed_mirror_average() -> None:
    module = load()
    previous = np.zeros(14, dtype=np.float32)
    previous[[2, 3, 4, 11, 12, 13]] = [-0.4, 0.2, 0.6, 0.2, 0.4, 0.0]
    projected = module.project_previous_to_mirrored(previous)
    np.testing.assert_array_equal(projected, np.asarray([0.3, 0.3, 0.3], dtype=np.float32))


def test_runner_has_no_optimizer_training_hardware_or_closest_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "training.adam_step" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"runtime_oracle_or_action_wrapper_authorized": False' in source
    assert "closest" not in source.lower()
