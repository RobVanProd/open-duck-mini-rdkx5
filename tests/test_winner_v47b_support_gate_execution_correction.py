from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v47b_support_gate_execution_correction.py"
ORIGINAL_PREREG = (
    ROOT
    / "outputs/analysis/winner_v47_static_target_teacher_support_gate_preregistration.json"
)
BASE_PREREG = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
)


def load():
    spec = importlib.util.spec_from_file_location("winner_v47b_runner_test", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_original_failure_and_corrected_provenance_are_reproduced() -> None:
    module = load()
    base = module._load_module("winner_v47b_base_test", module.BASE_RUNNER)
    original = json.loads(ORIGINAL_PREREG.read_text(encoding="utf-8"))
    reviewed = json.loads(BASE_PREREG.read_text(encoding="utf-8"))

    with pytest.raises(ValueError, match="calibrator-design provenance changed"):
        base.load_calibrator_design(original)
    design = base.load_calibrator_design(reviewed)
    assert design["status"] == "PREREGISTERED_IMPLEMENTATION_NOT_RUN"
    assert "continuous_training_domain" in design["hidden_configuration_domain"]


def test_corrected_runner_requires_explicit_cpu_gate_flags(
    monkeypatch, tmp_path: Path
) -> None:
    module = load()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(RUNNER),
            "--training-work-root",
            str(tmp_path),
            "--playground-root",
            str(tmp_path),
            "--canonical-fit",
            str(tmp_path),
            "--output",
            str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_result_adapter_changes_only_versioned_status_and_sources() -> None:
    module = load()
    value = {
        "authority": {"robot_clearance": False},
        "checkpoint_results": [],
        "checks": {},
        "decision": "AUTHORIZE_RESPONSE_CONDITIONED_LOCOMOTION_PREREGISTRATION_ONLY",
        "execution": {},
        "failed_checks": [],
        "reviewed_v47_sources": {"frozen": "source"},
        "status": "PASS_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION",
    }
    adapted = module._adapt_to_v47(value)
    assert adapted == {
        "authority": value["authority"],
        "checkpoint_results": [],
        "checks": {},
        "decision": value["decision"],
        "execution": {},
        "failed_checks": [],
        "schema_version": "winner_v47.static_target_teacher_support_gate_result.v1",
        "status": "PASS_WINNER_V47_STATIC_TARGET_TEACHER_SUPPORT_GATE",
        "sources": {"frozen": "source"},
    }


def test_corrected_runner_has_no_training_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert "gate_population_threshold_seed_checkpoint_or_policy_change" in source

