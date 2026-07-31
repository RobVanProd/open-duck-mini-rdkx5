from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v73_update638_contract_attribution.py"
RUNNER = ROOT / "tools/run_winner_v73_update638_contract_attribution.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_transformed_source_is_zero_update_diagnostic() -> None:
    builder = load_module(BUILDER, "winner_v73_builder_test")
    transformed, digest = builder.transformed_source()
    compile(transformed, "winner_v73_transformed.py", "exec")
    assert len(digest) == 64
    assert "SOURCE_COMPLETED_UPDATES = 637" in transformed
    assert "UPDATES = 1" in transformed
    assert "committed_optimizer_updates\": 0" in transformed
    diagnostic_return = transformed.index('        return 0\n', transformed.index('"committed_optimizer_updates": 0'))
    adam_proposal = transformed.index("training.adam_step(")
    assert diagnostic_return < adam_proposal
    assert "sampled_hidden_replay_at_most_2e_6" in transformed
    assert "--hardware-authorized" not in transformed


def test_runner_requires_explicit_cpu_diagnostic_flags(
    monkeypatch, tmp_path: Path
) -> None:
    builder = load_module(BUILDER, "winner_v73_builder_flags_test")
    transformed, _ = builder.transformed_source()
    namespace = {"__file__": str(RUNNER), "__name__": "winner_v73_flags_test"}
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
