from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v52_full_action_teacher_training_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v52_full_action_teacher_training.py"
CONTRACT = ROOT / "outputs/analysis/winner_v52_full_action_teacher_training_preregistration.json"
RESULT = ROOT / "outputs/analysis/winner_v52_full_action_teacher_training_result.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_transformed_source_has_exact_full_action_schedule() -> None:
    builder = load(BUILDER, "winner_v52_builder")
    source, receipts = builder.transformed_source()
    compile(source, str(builder.V46_RUNNER), "exec")
    assert len(receipts) == len(builder.TRANSFORMS)
    assert "SOURCE_COMPLETED_UPDATES = 353" in source
    assert "HALF_COMPLETED_UPDATES = 403" in source
    assert "FINAL_COMPLETED_UPDATES = 453" in source
    assert "full_training_teacher_loss" in source
    assert "build_full_training_teacher_batch" in source
    assert "list(v49.ACTION_INDICES)" in source
    assert "v44_runner.training_teacher_loss" not in source


def test_builder_binds_v51b_formal_source() -> None:
    builder = load(BUILDER, "winner_v52_source")
    result = json.loads(builder.V51B_RESULT.read_text(encoding="utf-8"))
    assert builder.sha256(builder.V51B_RESULT) == builder.V51B_RESULT_SHA256
    assert result["status"] == "PASS_WINNER_V51B_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"
    assert result["optimization"]["optimizer_count_after"] == 353


def test_generated_contract_is_source_bound_when_present() -> None:
    if not CONTRACT.exists():
        return
    runner = load(RUNNER, "winner_v52_generated")
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    runner.validate_contract(value)
    assert value["frozen_training"]["continuation_optimizer_updates"] == 100
    assert value["frozen_training"]["persistent_checkpoints"] == {
        "half": 403,
        "final": 453,
    }
    assert value["objective"]["full_action_static_target_teacher"][
        "action_indices"
    ] == list(range(14))
    assert value["authority"]["formal_support_gate_authorized"] is False


def test_result_has_both_unselected_checkpoints_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT",
        "HOLD_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT",
    }
    assert value["execution"]["optimizer_updates"] == 100
    assert [
        (row["label"], row["completed_updates"])
        for row in value["persistent_checkpoints"]
    ] == [("half", 403), ("final", 453)]
    assert value["authority"]["robot_clearance"] is False


def test_runner_requires_explicit_cpu_authority(monkeypatch, tmp_path: Path) -> None:
    runner = load(RUNNER, "winner_v52_authority")
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--playground-root", str(tmp_path),
            "--canonical-fit", str(tmp_path / "fit.json"),
            "--source-snapshot", str(tmp_path / "source.npz"),
            "--source-graph", str(tmp_path / "source.onnx"),
            "--teacher-snapshot", str(tmp_path / "teacher.npz"),
            "--work-root", str(tmp_path / "work"),
            "--output", str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        runner.main()


def test_wrapper_has_no_hardware_or_support_gate_operation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--hardware-authorized" not in source
    assert "run_winner_v52_full_action_teacher_support_gate" not in source
    assert '"robot_or_rdk_access"' not in source
