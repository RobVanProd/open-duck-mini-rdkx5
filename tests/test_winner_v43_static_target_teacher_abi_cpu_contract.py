from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v43_static_target_teacher_abi_cpu_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v43_static_target_teacher_abi_cpu_contract.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v43_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_constants_match_teacher_abi() -> None:
    module = load()
    assert module.ENVIRONMENTS == 30
    assert module.TICKS == 250
    assert module.SELECTED_ELEMENTS == 45_000
    assert module.v43.PITCH_ACTION_INDICES == (2, 3, 4, 11, 12, 13)


def test_runner_validates_frozen_contract_when_present() -> None:
    if not CONTRACT.exists():
        return
    module = load()
    module.validate_contract(json.loads(CONTRACT.read_text(encoding="utf-8")))


def test_runner_requires_both_offline_authority_flags(monkeypatch, tmp_path) -> None:
    module = load()
    monkeypatch.setattr(
        "sys.argv", [str(RUNNER), "--output", str(tmp_path / "result.json")]
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_runner_has_no_optimizer_simulator_export_or_hardware_operation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "mujoco" not in source.lower()
    assert "onnx" not in source.lower()
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"optimizer_updates": 0' in source
    assert '"simulator_behavior_ticks": 0' in source
    assert '"deployable_graph_exports": 0' in source
    assert '"robot_or_rdk_access": 0' in source
