from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v51b_one_update_indexing_correction.py"
RUNNER = ROOT / "tools/run_winner_v51b_one_update_indexing_correction.py"
CONTRACT = ROOT / "outputs/analysis/winner_v51b_one_update_indexing_correction_contract.json"
RESULT = ROOT / "outputs/analysis/winner_v51b_full_action_teacher_one_update_cpu_result.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_changes_exactly_one_indexing_fragment() -> None:
    builder = load(BUILDER, "winner_v51b_builder")
    source = builder.V51_RUNNER.read_text(encoding="utf-8")
    assert source.count(builder.OLD_FRAGMENT) == 1
    assert builder.NEW_FRAGMENT not in source
    corrected, digest = builder.corrected_source()
    assert corrected.count(builder.NEW_FRAGMENT) == 1
    assert builder.OLD_FRAGMENT not in corrected
    assert digest


def test_generated_contract_is_source_bound_when_present() -> None:
    if not CONTRACT.exists():
        return
    runner = load(RUNNER, "winner_v51b_generated")
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    runner.validate_contract(value)
    assert value["correction"]["replacement_count"] == 1
    assert value["correction"]["optimizer_objective_artifact_or_gate_change"] is False
    runner.corrected_source(value)


def test_result_is_exactly_one_update_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V51B_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF",
        "HOLD_WINNER_V51B_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF",
    }
    assert value["execution"]["optimizer_updates"] == 1
    assert value["execution"]["formal_support_cells"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_runner_requires_explicit_cpu_authority(monkeypatch, tmp_path: Path) -> None:
    runner = load(RUNNER, "winner_v51b_authority")
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--playground-root", str(tmp_path),
            "--canonical-fit", str(tmp_path / "fit.json"),
            "--v46-training-work-root", str(tmp_path),
            "--v22-training-work-root", str(tmp_path),
            "--work-root", str(tmp_path / "work"),
            "--output", str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        runner.main()


def test_correction_runner_does_not_contain_optimizer_or_hardware_calls() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    assert "OLD_FRAGMENT" in source and "NEW_FRAGMENT" in source
