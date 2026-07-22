from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
MECHANICS = PATCHES / "winner_v24_symmetric_support_failure_v2.py"


def load():
    sys.path.insert(0, str(PATCHES))
    spec = importlib.util.spec_from_file_location("winner_v24_symmetric_v2", MECHANICS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture():
    shape = (2, 4)
    values = np.asarray([[0.1, 0.2, 0, 0], [0.2, 0.3, 0.4, 0]], dtype=np.float32)
    rewards = np.asarray([[1, 0, 0, 0], [1, 1, 251, 0]], dtype=np.float32)
    done = np.asarray([[0, 1, 0, 0], [0, 0, 1, 0]], dtype=np.float32)
    mask = np.asarray([[1, 1, 0, 0], [1, 1, 1, 0]], dtype=np.float32)
    # The baseline return bytes are authoritative; exact values need not be a
    # second implementation of GAE for this unit test.
    returns = np.asarray([[1.2, 0.2, 0, 0], [250.0, 250.5, 251.4, 0]], dtype=np.float32)
    batch = {
        "rewards": rewards,
        "returns": returns,
        "advantages": np.zeros(shape, dtype=np.float32),
        "done": done,
        "valid_mask": mask,
        "valid_transition_mask": np.asarray(
            [[1, 0, 0, 0], [1, 1, 1, 0]], dtype=np.float32
        ),
        "actions": np.arange(2 * 4 * 14, dtype=np.float32).reshape(2, 4, 14),
    }
    episodes = [
        {"environment": 0, "terminal": {"tick": 1, "checks": {"roll_pitch": False}}},
        {"environment": 1, "terminal": None},
    ]
    return batch, episodes, values


def test_default_off_preserves_authoritative_baseline_bytes() -> None:
    module = load()
    batch, episodes, values = fixture()
    result, evidence = module.apply_baseline_anchored_objective(
        batch, episodes, values, enabled=False, gamma=0.99, gae_lambda=0.95
    )
    assert evidence["anchor"] == "recorded_baseline_returns_and_rederived_values"
    assert evidence["modified_batch_keys"] == []
    assert all(np.array_equal(result[key], value) for key, value in batch.items())


def test_enabled_applies_only_analytic_terminal_delta() -> None:
    module = load()
    batch, episodes, values = fixture()
    result, evidence = module.apply_baseline_anchored_objective(
        batch, episodes, values, enabled=True, gamma=0.99, gae_lambda=0.95
    )
    factor = np.float32(0.99) * np.float32(0.95)
    baseline_raw = batch["returns"] - values
    expected_raw = baseline_raw.copy()
    expected_raw[0, 1] += np.float32(-250.0)
    expected_raw[0, 0] += factor * np.float32(-250.0)
    expected_returns = np.where(
        batch["valid_mask"] > 0, expected_raw + values, np.float32(0.0)
    ).astype(np.float32)
    assert np.array_equal(result["returns"], expected_returns)
    assert result["rewards"][0, 1] == np.float32(-250.0)
    assert result["rewards"][1, 2] == np.float32(251.0)
    assert evidence["analytical_terminal_delta_nonzero_count"] == 2
    assert evidence["analytical_terminal_delta_min"] == -250.0
    assert np.array_equal(result["actions"], batch["actions"])
