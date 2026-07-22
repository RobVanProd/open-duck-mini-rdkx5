from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v77_residual_teacher_causal_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v77_residual_teacher_causal.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_transformed_source_binds_nine_final_failures() -> None:
    builder = load_module(BUILDER, "winner_v77_builder_test")
    transformed, digest = builder.transformed_source()
    compile(transformed, "winner_v77_transformed.py", "exec")
    assert len(digest) == 64
    assert '"diagnostic_cells": 36' in transformed
    assert '"failed_pair_count": 9' in transformed
    assert 'snapshot["metadata"]["completed_updates"] != 655' in transformed
    assert '"exact_36_cells"' in transformed
    assert '"all_9_graph_cells_bit_exact_to_v76"' in transformed
    assert "optimizer_updates" in transformed
    assert "--hardware-authorized" not in transformed


def test_runner_requires_explicit_cpu_diagnostic_flags(
    monkeypatch, tmp_path: Path
) -> None:
    builder = load_module(BUILDER, "winner_v77_builder_flags_test")
    transformed, _ = builder.transformed_source()
    namespace = {"__file__": str(RUNNER), "__name__": "winner_v77_flags_test"}
    exec(compile(transformed, str(RUNNER), "exec"), namespace)
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--training-work-root",
            str(tmp_path),
            "--playground-root",
            str(tmp_path),
            "--canonical-fit",
            str(tmp_path),
            "--output",
            str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        namespace["main"]()
