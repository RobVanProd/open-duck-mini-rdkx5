from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v86b_formal_cell_map_correction.py"
RUNNER = ROOT / "tools/run_winner_v86b_formal_cell_map_correction.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v86b_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_correction_changes_only_formal_population_lookup() -> None:
    builder = load_builder()
    source, original_hash, corrected_hash = builder.corrected_source()
    assert len(original_hash) == len(corrected_hash) == 64
    assert original_hash != corrected_hash
    assert builder.OLD not in source
    assert builder.NEW in source
    assert source.count("v48.InterventionSession") == 1
    assert source.count('"diagnostic_cells": len(all_cells)') == 1
    compile(source, "winner_v86b_corrected.py", "exec")


def test_wrapper_uses_frozen_corrected_source() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "builder.corrected_source()" in source
    assert "exec(compile(source" in source
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
