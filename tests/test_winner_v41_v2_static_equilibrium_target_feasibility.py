from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v41_v2_static_equilibrium_target_feasibility.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v41_v2_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_corrected_expansion_is_exact_reviewed_mirror_matrix() -> None:
    module = load()
    expanded = module.expand_static_target(
        np.asarray([[0.25, -0.50, 0.75]], dtype=np.float32)
    )
    expected = np.zeros((1, 14), dtype=np.float32)
    expected[0, [2, 3, 4, 11, 12, 13]] = [-0.25, -0.50, 0.75, 0.25, -0.50, 0.75]
    np.testing.assert_array_equal(expanded, expected)


def test_corrected_expansion_rejects_v38_four_block_shape() -> None:
    module = load()
    with pytest.raises(ValueError, match="static target shape changed"):
        module.expand_static_target(np.zeros((4, 3), dtype=np.float32))


def test_wrapper_changes_only_expansion_and_result_attribution() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "v41.v38.expand_mirrored_blocks = expand_static_target" in source
    assert "v41.main()" in source
    assert "candidate_coordinates" not in source
    assert "Episode(" not in source
    assert "bounded_action_numpy" not in source
    assert "support_pass" not in source
    assert "training.adam_step" not in source
    assert '"optimizer_updates": 0' in source
    assert "hardware-authorized" not in source
