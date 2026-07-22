from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v49_full_action_teacher_abi_cpu_contract.py"
RUNNER = ROOT / "tools/run_winner_v49_full_action_teacher_abi_cpu_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v49_full_action_teacher_abi_cpu_contract.json"
RESULT = ROOT / "outputs/analysis/winner_v49_full_action_teacher_abi_cpu_result.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_constants_match_full_action_contract() -> None:
    runner = load(RUNNER, "winner_v49_runner_constants")
    assert runner.ENVIRONMENTS == 30
    assert runner.TICKS == 250
    assert runner.SELECTED_ELEMENTS == 105_000
    assert runner.v49.ACTION_INDICES == tuple(range(14))


def test_builder_binds_causal_result() -> None:
    builder = load(BUILDER, "winner_v49_builder")
    value = json.loads(builder.V48C_RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V48C_CAUSAL_POPULATION_SCOPE_AUDIT"
    assert value["findings"]["full_teacher_support_pass_count"] == 32
    assert value["findings"]["classification_counts"]["pitch_nonpitch_interaction"] == 3


def test_generated_contract_is_exact_and_source_bound_when_present() -> None:
    if not CONTRACT.exists():
        return
    runner = load(RUNNER, "winner_v49_generated")
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    runner.validate_contract(value)
    assert value["teacher_abi"]["supervised_action_indices"] == list(range(14))
    assert value["teacher_abi"]["supervised_elements"] == 105_000
    assert not any(value["execution_now"].values())
    assert value["authority"]["training_authorized"] is False


def test_result_is_contract_only_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT",
        "HOLD_WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT",
    }
    assert value["execution"]["optimizer_updates"] == 0
    assert value["execution"]["simulator_behavior_ticks"] == 0
    assert value["authority"]["training_authorized"] is False


def test_runner_requires_explicit_cpu_authority(monkeypatch, tmp_path: Path) -> None:
    runner = load(RUNNER, "winner_v49_authority")
    monkeypatch.setattr(
        "sys.argv", [str(RUNNER), "--output", str(tmp_path / "out.json")]
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        runner.main()


def test_runner_has_no_optimizer_simulator_export_or_hardware_operation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "mujoco" not in source.lower()
    assert "onnxruntime" not in source.lower()
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"simulator_behavior_ticks": 0' in source
    assert '"robot_or_rdk_access": 0' in source
