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


def test_reward_proof_compares_float32_terminal_bonus_directly() -> None:
    module = load_module()
    pitch = np.asarray([[-0.175, -0.1, 0.0]], dtype=np.float32)
    valid = np.ones_like(pitch, dtype=np.float32)
    expected = module.valid_transition_reward(pitch, enabled=True)
    rewards = expected.copy()
    rewards[0, 1] = np.float32(rewards[0, 1] + np.float32(250.0))
    penalties = (np.float32(1.0) - expected).astype(np.float32)
    proof = module.reward_evidence(
        {
            "valid_transition_mask": valid,
            "rewards": rewards,
            "applied_negative_pitch_penalty": penalties,
            "next_pitch_rad": pitch,
        }
    )
    assert proof["settled_bonus_count"] == 1
    assert proof["reward_formula_bit_exact"] is True
    assert proof["penalty_formula_bit_exact"] is True
