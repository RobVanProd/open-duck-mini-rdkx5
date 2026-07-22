from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v87b_teacher_population_correction.py"
RUNNER = ROOT / "tools/run_winner_v87b_teacher_population_correction.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v87b_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_correction_uses_exact_selected_teacher_population() -> None:
    builder = load_builder()
    source, original_hash, corrected_hash = builder.corrected_source()
    assert len(original_hash) == len(corrected_hash) == 64
    assert original_hash != corrected_hash
    assert 'len(teacher_ids) != 12' in source
    assert 'np.count_nonzero(selected_environment)) != 24' in source
    assert 'row["teacher_episodes"] == 24' in source
    assert 'len(row["teacher_configuration_ids"]) == 12' in source
    assert '"least_squares_fits": 26' in source
    assert "np.linalg.lstsq" in source
    assert '"optimizer_updates": 0' in source
    compile(source, "winner_v87b_corrected.py", "exec")


def test_wrapper_executes_only_frozen_corrected_source() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "builder.corrected_source()" in source
    assert "exec(compile(source" in source
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
