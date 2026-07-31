from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v79b_preregistration_path_correction.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v79b_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_preregistration_path_correction_only() -> None:
    builder = load_builder()
    original, _ = builder.v79.transformed_source()
    corrected, digest = builder.corrected_source()
    assert len(digest) == 64
    assert original.count(builder.OLD) == 1
    assert corrected.count(builder.NEW) == 1
    assert corrected == original.replace(builder.OLD, builder.NEW)
    assert '"diagnostic_cells": 36' in corrected
    assert 'teacher_table["COM_CORNER_07"] = extension_action' in corrected
    assert "--hardware-authorized" not in corrected
