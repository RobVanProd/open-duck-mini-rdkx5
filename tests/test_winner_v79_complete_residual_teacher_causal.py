from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v79_complete_residual_teacher_causal_preregistration.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v79_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_transformed_source_binds_complete_nine_pair_population() -> None:
    builder = load_builder()
    source, digest = builder.transformed_source()
    assert len(digest) == 64
    assert "winner_v79.residual_teacher_causal_preregistration.v1" in source
    assert "winner_v78_missing_teacher_extension_result.json" in source
    assert 'teacher_table["COM_CORNER_07"] = extension_action' in source
    assert '"diagnostic_cells": 36' in source
    assert '"failed_pair_count": 9' in source
    assert "exact_36_cells" in source
    assert "all_9_graph_cells_bit_exact_to_v76" in source
    assert "full_teacher_all_9_pass" in source
    assert "full_teacher_all_13_pass" not in source
    assert "--hardware-authorized" not in source


def test_runner_requires_explicit_cpu_diagnostic_authority() -> None:
    source = (
        ROOT / "tools/run_winner_v79_complete_residual_teacher_causal.py"
    ).read_text(encoding="utf-8")
    transformed, _ = load_builder().transformed_source()
    assert "--offline-cpu-only" in transformed
    assert "--causal-diagnostic-authorized" in transformed
    assert "--hardware-authorized" not in source
    assert "--hardware-authorized" not in transformed
    assert "optimizer_updates\": 0" in transformed
    assert "robot_or_rdk_access\": 0" in transformed
