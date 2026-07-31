from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MECHANICS = ROOT / "patches/winner_v24_symmetric_support_failure.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v24_symmetric", MECHANICS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture():
    shape = (2, 4)
    batch = {
        "rewards": np.asarray([[1, 0, 0, 0], [1, 1, 251, 0]], dtype=np.float32),
        "returns": np.zeros(shape, dtype=np.float32),
        "advantages": np.zeros(shape, dtype=np.float32),
        "done": np.asarray([[0, 1, 0, 0], [0, 0, 1, 0]], dtype=np.float32),
        "valid_mask": np.asarray([[1, 1, 0, 0], [1, 1, 1, 0]], dtype=np.float32),
        "valid_transition_mask": np.asarray(
            [[1, 0, 0, 0], [1, 1, 1, 0]], dtype=np.float32
        ),
        "actions": np.arange(2 * 4 * 14, dtype=np.float32).reshape(2, 4, 14),
    }
    episodes = [
        {
            "environment": 0,
            "terminal": {"tick": 1, "checks": {"roll_pitch": False}},
        },
        {"environment": 1, "terminal": None},
    ]
    values = np.zeros(shape, dtype=np.float32)
    return batch, episodes, values


def test_default_off_is_bit_exact() -> None:
    module = load()
    batch, episodes, values = fixture()
    result, evidence = module.apply_symmetric_failure_objective(
        batch, episodes, values, enabled=False, gamma=0.99, gae_lambda=0.95
    )
    assert evidence["modified_batch_keys"] == []
    assert all(np.array_equal(result[key], value) for key, value in batch.items())


def test_enabled_changes_only_reward_returns_and_advantages() -> None:
    module = load()
    batch, episodes, values = fixture()
    result, evidence = module.apply_symmetric_failure_objective(
        batch, episodes, values, enabled=True, gamma=0.99, gae_lambda=0.95
    )
    assert result["rewards"][0, 1] == np.float32(-250.0)
    assert result["rewards"][1, 2] == np.float32(251.0)
    assert evidence["roll_pitch_failure_count"] == 1
    assert evidence["modified_batch_keys"] == ["advantages", "returns", "rewards"]
    assert np.array_equal(result["actions"], batch["actions"])
    assert not np.array_equal(result["returns"], batch["returns"])
    assert not np.array_equal(result["advantages"], batch["advantages"])
