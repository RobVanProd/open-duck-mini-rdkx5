from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v46_static_target_teacher_training.py"
PREREG = ROOT / "outputs/analysis/winner_v46_static_target_teacher_training_preregistration.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v46_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_constants_are_frozen() -> None:
    module = load()
    assert module.UPDATES == 100
    assert module.SOURCE_COMPLETED_UPDATES == 252
    assert module.HALF_COMPLETED_UPDATES == 302
    assert module.FINAL_COMPLETED_UPDATES == 352
    assert float(module.FROZEN_TEACHER_SCALE) == 58.436370849609375


def test_runner_validates_preregistration_when_present() -> None:
    if not PREREG.exists():
        return
    module = load()
    module.validate_preregistration(json.loads(PREREG.read_text(encoding="utf-8")))


def test_runner_requires_explicit_cpu_training_flags(monkeypatch, tmp_path) -> None:
    module = load()
    monkeypatch.setattr("sys.argv", [
        str(RUNNER), "--playground-root", str(tmp_path), "--canonical-fit", str(tmp_path),
        "--source-snapshot", str(tmp_path), "--source-graph", str(tmp_path),
        "--teacher-snapshot", str(tmp_path), "--work-root", str(tmp_path / "work"),
        "--output", str(tmp_path / "out.json"),
    ])
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_runner_has_no_support_gate_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--static-target-teacher-training-authorized" in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source

