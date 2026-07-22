from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v74_update638_hidden_replay_numeric_audit.py"
RUNNER = ROOT / "tools/run_winner_v74_update638_hidden_replay_numeric_audit.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_transformed_source_reuses_functional_bounds_without_update() -> None:
    builder = load_module(BUILDER, "winner_v74_builder_test")
    transformed, digest = builder.transformed_source()
    compile(transformed, "winner_v74_transformed.py", "exec")
    assert len(digest) == 64
    assert "SOURCE_COMPLETED_UPDATES = 637" in transformed
    assert "UPDATES = 1" in transformed
    assert "eager_replay_bit_exact_to_rollout" in transformed
    assert "mean_action_delta_within_1e_6" in transformed
    assert "scan_exceeds_legacy_2e_6_guard" in transformed
    assert "committed_optimizer_updates" not in transformed
    numeric_return = transformed.index(
        "        return 0\n", transformed.index("eager_replay_bit_exact_to_rollout")
    )
    assert numeric_return < transformed.index("training.adam_step(")
    assert "--hardware-authorized" not in transformed


def test_runner_requires_explicit_cpu_audit_flags(
    monkeypatch, tmp_path: Path
) -> None:
    builder = load_module(BUILDER, "winner_v74_builder_flags_test")
    transformed, _ = builder.transformed_source()
    namespace = {"__file__": str(RUNNER), "__name__": "winner_v74_flags_test"}
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
