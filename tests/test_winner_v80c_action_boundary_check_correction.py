from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v80c_action_boundary_check_correction.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v80c_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_action_boundary_checker_correction_only() -> None:
    builder = load_builder()
    original, _ = builder.v80b.corrected_source()
    corrected, digest = builder.corrected_source()
    assert len(digest) == 64
    assert original.count(builder.OLD) == 1
    assert corrected.count(builder.NEW) == 1
    assert corrected == original.replace(builder.OLD, builder.NEW)
    assert 'boundary["realized_equals_numpy_bit_exact"]' in corrected
    assert 'boundary["numpy_equals_jax_bit_exact"]' in corrected
    assert "--hardware-authorized" not in corrected
