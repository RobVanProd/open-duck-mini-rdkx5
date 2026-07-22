from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v44_static_target_teacher_source_gradient_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v44_static_target_teacher_source_gradient_contract.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v44_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_constants_match_source_gradient_contract() -> None:
    module = load()
    assert module.ROLLOUT_UPDATE_INDEX == 251
    assert float(module.PREFIX_ANCHOR_SCALE) == 197.3112030029297
    assert module.COMPOSITION_TOLERANCE == 4.0e-6
    assert module.BALANCE_RELATIVE_TOLERANCE == 2.0e-6
    assert len(module.TRAINING_TEACHER_IDS) == 11
    assert module.HELDOUT_TEACHER_IDS == (
        "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15",
    )


def test_runner_validates_frozen_contract_when_present() -> None:
    if not CONTRACT.exists():
        return
    module = load()
    module.validate_contract(json.loads(CONTRACT.read_text(encoding="utf-8")))


def test_runner_requires_both_offline_authority_flags(monkeypatch, tmp_path) -> None:
    module = load()
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER), "--playground-root", str(tmp_path),
            "--canonical-fit", str(tmp_path / "fit.json"),
            "--v32-training-work-root", str(tmp_path),
            "--v22-training-work-root", str(tmp_path),
            "--output", str(tmp_path / "result.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_runner_contains_no_optimizer_export_or_hardware_operation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "export_" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"optimizer_updates": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"deployable_graph_exports": 0' in source
    assert '"robot_or_rdk_access": 0' in source
