from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT
    / "tools/build_winner_v48b_evidence_comparator_correction_preregistration.py"
)
RUNNER = ROOT / "tools/run_winner_v48b_evidence_comparator_correction.py"
PREREGISTRATION = (
    ROOT
    / "outputs/analysis/winner_v48b_evidence_comparator_correction_preregistration.json"
)
RESULT = (
    ROOT / "outputs/analysis/winner_v48b_evidence_comparator_correction_result.json"
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_binds_only_the_invalid_comparator_check() -> None:
    builder = load(BUILDER, "winner_v48b_builder")
    v48 = json.loads(builder.V48_RESULT.read_text(encoding="utf-8"))
    v47b = json.loads(builder.V47B_RESULT.read_text(encoding="utf-8"))
    builder.validate_invalid_v48(v48)
    builder.validate_v47b_hold(v47b)
    assert builder.sha256(builder.V48_RESULT) == builder.V48_RESULT_SHA256


def test_corrected_comparator_separates_float_and_discrete_evidence() -> None:
    runner = load(RUNNER, "winner_v48b_compare")
    observed = {"tick": 3, "value": 1.0 + 1.0e-15, "hash": "same"}
    expected = {"tick": 3, "value": 1.0, "hash": "same"}
    result = runner.compare_evidence(observed, expected)
    assert result["discrete_exact"] is True
    assert result["float64_leaf_count"] == 1
    assert 0.0 < result["maximum_abs_float64_difference"] < 1.0e-12
    assert result["float64_within_absolute_1e_12"] is True


def test_corrected_comparator_rejects_discrete_or_large_float_changes() -> None:
    runner = load(RUNNER, "winner_v48b_reject")
    discrete = runner.compare_evidence({"tick": 4}, {"tick": 3})
    large = runner.compare_evidence({"value": 1.0 + 1.0e-9}, {"value": 1.0})
    assert discrete["discrete_exact"] is False
    assert large["float64_within_absolute_1e_12"] is False


def test_generated_preregistration_is_no_rerun_and_source_bound_when_present() -> None:
    if not PREREGISTRATION.exists():
        return
    runner = load(RUNNER, "winner_v48b_generated")
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION"
    assert value["decision"] == "AUTHORIZE_ONE_CAPTURED_EVIDENCE_AUDIT_ONLY"
    assert value["invalid_execution"]["rerun_authorized"] is False
    assert value["execution_now"]["new_diagnostic_cells"] == 0
    assert value["authority"]["training_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
    runner.validate_source_manifest(value)


def test_result_promotes_only_full_14d_mechanism_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION"
    assert value["decision"] == (
        "AUTHORIZE_FULL_14D_STATIC_TEACHER_MECHANISM_PREREGISTRATION_ONLY"
    )
    assert value["findings"]["full_teacher_support_pass_count"] == 32
    assert value["execution"]["new_diagnostic_cells"] == 0
    assert value["execution"]["optimizer_updates"] == 0
    assert value["authority"]["training_authorized"] is False


def test_runner_contains_no_physics_training_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "mujoco" not in source.lower()
    assert "onnxruntime" not in source.lower()
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    assert "/dev/tty" not in source
