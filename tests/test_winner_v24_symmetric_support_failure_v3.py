from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
MECHANICS = PATCHES / "winner_v24_symmetric_support_failure_v3.py"


def load():
    sys.path.insert(0, str(PATCHES))
    spec = importlib.util.spec_from_file_location("winner_v24_symmetric_v3", MECHANICS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture():
    shape = (1, 3)
    values = np.asarray([[0.1, 0.2, 0.3]], dtype=np.float32)
    batch = {
        "rewards": np.asarray([[1, 2, 3]], dtype=np.float32),
        "returns": np.asarray([[4, 5, 6]], dtype=np.float32),
        "advantages": np.asarray([[0.1, 0.2, 0.3]], dtype=np.float32),
        "done": np.asarray([[0, 0, 1]], dtype=np.float32),
        "valid_mask": np.ones(shape, dtype=np.float32),
        "valid_transition_mask": np.asarray([[1, 1, 0]], dtype=np.float32),
        "actions": np.arange(42, dtype=np.float32).reshape(1, 3, 14),
    }
    return batch, values


def test_zero_failure_rollout_is_bit_exact_noop() -> None:
    module = load()
    batch, values = fixture()
    episodes = [{"environment": 0, "terminal": None}]
    result, evidence = module.apply_training_objective(
        batch, episodes, values, gamma=0.99, gae_lambda=0.95
    )
    assert evidence["roll_pitch_failure_count"] == 0
    assert evidence["zero_failure_bit_exact_noop"] is True
    assert evidence["analytical_terminal_delta_nonzero_count"] == 0
    assert evidence["modified_batch_keys"] == []
    assert all(np.array_equal(result[key], value) for key, value in batch.items())


def test_failure_rollout_delegates_to_baseline_anchored_objective() -> None:
    module = load()
    batch, values = fixture()
    batch["rewards"][0, 2] = np.float32(0.0)
    episodes = [
        {"environment": 0, "terminal": {"tick": 2, "checks": {"roll_pitch": False}}}
    ]
    result, evidence = module.apply_training_objective(
        batch, episodes, values, gamma=0.99, gae_lambda=0.95
    )
    assert evidence["roll_pitch_failure_count"] == 1
    assert evidence["zero_failure_bit_exact_noop"] is False
    assert evidence["modified_batch_keys"] == ["advantages", "returns", "rewards"]
    assert result["rewards"][0, 2] == np.float32(-250.0)
