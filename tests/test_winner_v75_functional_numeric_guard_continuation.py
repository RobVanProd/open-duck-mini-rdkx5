from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v75_functional_numeric_guard_continuation.py"
RUNNER = ROOT / "tools/run_winner_v75_functional_numeric_guard_continuation.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_transformed_source_changes_only_numeric_guard_and_identity() -> None:
    builder = load_module(BUILDER, "winner_v75_builder_test")
    transformed, digest = builder.transformed_source()
    compile(transformed, "winner_v75_transformed.py", "exec")
    assert len(digest) == 64
    assert "UPDATES = 53" in transformed
    assert "SOURCE_COMPLETED_UPDATES = 602" in transformed
    assert "HALF_COMPLETED_UPDATES = 605" in transformed
    assert "FINAL_COMPLETED_UPDATES = 655" in transformed
    assert "hidden_replay_functional_evidence" in transformed
    assert '"all_53_hidden_replays_functionally_bounded"' in transformed
    assert '"all_53_hidden_replays_at_most_2e_6"' not in transformed
    assert "eager_hidden_max_abs_error" in transformed
    assert "PASS_WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION" in transformed
    assert "FROZEN_TEACHER_SCALE = np.float32(136.35153198242188)" in transformed
    assert "--hardware-authorized" not in transformed


def test_runner_requires_explicit_cpu_training_flags(
    monkeypatch, tmp_path: Path
) -> None:
    builder = load_module(BUILDER, "winner_v75_builder_flags_test")
    transformed, _ = builder.transformed_source()
    namespace = {"__file__": str(RUNNER), "__name__": "winner_v75_flags_test"}
    exec(compile(transformed, str(RUNNER), "exec"), namespace)
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--playground-root",
            str(tmp_path),
            "--canonical-fit",
            str(tmp_path),
            "--source-snapshot",
            str(tmp_path),
            "--source-graph",
            str(tmp_path),
            "--teacher-snapshot",
            str(tmp_path),
            "--work-root",
            str(tmp_path / "work"),
            "--output",
            str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        namespace["main"]()
