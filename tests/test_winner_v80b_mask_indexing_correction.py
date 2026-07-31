from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v80b_mask_indexing_correction.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v80b_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_mask_indexing_correction_only() -> None:
    builder = load_builder()
    original = builder.BASE_RUNNER.read_text(encoding="utf-8")
    corrected, digest = builder.corrected_source()
    assert len(digest) == 64
    assert original.count(builder.OLD) == 1
    assert corrected.count(builder.NEW) == 1
    assert corrected == original.replace(builder.OLD, builder.NEW)
    assert "training.adam_step" in corrected
    assert "--hardware-authorized" not in corrected
