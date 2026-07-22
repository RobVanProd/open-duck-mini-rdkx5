from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v77b_population_authorization_correction.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_population_authorization_correction_only() -> None:
    builder = load_module(BUILDER, "winner_v77b_builder_test")
    original, _ = builder.v77.transformed_source()
    corrected, digest = builder.corrected_source()
    assert len(digest) == 64
    assert original.count(builder.OLD) == 1
    assert corrected.count(builder.NEW) == 1
    assert corrected == original.replace(builder.OLD, builder.NEW)
    assert '"failed_pair_count": 9' in corrected
    assert '"diagnostic_cells": 36' in corrected
    assert "exact_36_cells" in corrected
    assert "--hardware-authorized" not in corrected
