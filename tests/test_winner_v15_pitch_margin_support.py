from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "patches/winner_v15_pitch_margin_support.py"


def load_module():
    spec = importlib.util.spec_from_file_location("winner_v15_pitch_margin", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_off_is_exact_flat_alive_reward() -> None:
    module = load_module()
    pitches = np.asarray([-1.0, -0.35, -0.175, 0.0, 0.5], dtype=np.float32)
    assert np.array_equal(
        module.valid_transition_reward(pitches, enabled=False),
        np.ones_like(pitches),
    )


def test_enabled_reward_is_bounded_one_sided_and_analytic() -> None:
    module = load_module()
    pitches = np.asarray([-0.7, -0.35, -0.175, 0.0, 0.175], dtype=np.float32)
    expected = np.asarray([0.0, 0.0, 0.75, 1.0, 1.0], dtype=np.float32)
    observed = module.valid_transition_reward(pitches, enabled=True)
    assert np.array_equal(observed, expected)
    assert np.all((observed >= 0.0) & (observed <= 1.0))


def test_positive_pitch_is_not_penalized() -> None:
    module = load_module()
    pitches = np.linspace(0.0, 1.0, 1024, dtype=np.float32)
    assert np.array_equal(
        module.valid_transition_reward(pitches, enabled=True),
        np.ones_like(pitches),
    )
