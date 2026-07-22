from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v47_static_target_teacher_support_gate.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v47_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checkpoint_constants_are_frozen() -> None:
    module = load()
    assert module.SOURCE_SNAPSHOT_SHA256 == "72c2e0bf895e8968a0d851ee1079435daca6125a572943b557fe766fc6e4832b"
    assert module.TEACHER_SNAPSHOT_SHA256 == "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"


def test_runner_requires_explicit_cpu_gate_flags(monkeypatch, tmp_path) -> None:
    module = load()
    monkeypatch.setattr("sys.argv", [
        str(RUNNER), "--training-work-root", str(tmp_path),
        "--playground-root", str(tmp_path), "--canonical-fit", str(tmp_path),
        "--output", str(tmp_path / "out.json"),
    ])
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_runner_has_no_training_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"robot_clearance": False' in source

