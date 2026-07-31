from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v50b_gradient_composition_ulp_attribution.py"
RUNNER = ROOT / "tools/run_winner_v50b_gradient_composition_ulp_attribution.py"
CONTRACT = ROOT / "outputs/analysis/winner_v50b_gradient_composition_ulp_attribution_contract.json"
RESULT = ROOT / "outputs/analysis/winner_v50b_gradient_composition_ulp_attribution_result.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_signed_float32_ulp_distance_handles_both_signs() -> None:
    runner = load(RUNNER, "winner_v50b_ulp")
    positive = np.float32(1.0)
    negative = np.float32(-1.0)
    assert int(runner.signed_float32_ulp_distance(
        np.asarray([positive], dtype=np.float32),
        np.asarray([np.nextafter(positive, np.float32(np.inf))], dtype=np.float32),
    )[0]) == 1
    assert int(runner.signed_float32_ulp_distance(
        np.asarray([negative], dtype=np.float32),
        np.asarray([np.nextafter(negative, np.float32(-np.inf))], dtype=np.float32),
    )[0]) == 1
    assert int(runner.signed_float32_ulp_distance(
        np.asarray([np.float32(-0.0)], dtype=np.float32),
        np.asarray([np.float32(0.0)], dtype=np.float32),
    )[0]) == 1


def test_tree_ulp_evidence_rejects_non_float32() -> None:
    runner = load(RUNNER, "winner_v50b_tree")
    with pytest.raises(ValueError, match="finite float32"):
        runner.tree_ulp_evidence(
            {"x": np.asarray([1.0], dtype=np.float64)},
            {"x": np.asarray([1.0], dtype=np.float64)},
        )


def test_builder_binds_the_frozen_v50_hold() -> None:
    builder = load(BUILDER, "winner_v50b_builder")
    frozen = json.loads(builder.V50_RESULT.read_text(encoding="utf-8"))
    assert builder.sha256(builder.V50_RESULT) == builder.EXPECTED_V50_RESULT_SHA256
    assert frozen["failed_checks"] == builder.FAILED_V50_CHECKS
    assert builder.MAX_ULP_DISTANCE == 8


def test_generated_contract_is_source_bound_when_present() -> None:
    if not CONTRACT.exists():
        return
    runner = load(RUNNER, "winner_v50b_generated")
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    runner.validate_contract(value)
    assert value["frozen_hold"]["result_rewritten"] is False
    assert value["attribution_rule"]["v50_absolute_threshold_changed"] is False
    assert value["authority"]["one_update_authorized"] is False


def test_result_remains_zero_update_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION",
        "HOLD_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION",
    }
    assert value["execution"]["optimizer_updates"] == 0
    assert value["execution"]["formal_support_cells"] == 0
    assert value["authority"]["one_update_authorized"] is False


def test_runner_requires_explicit_cpu_authority(monkeypatch, tmp_path: Path) -> None:
    runner = load(RUNNER, "winner_v50b_authority")
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--playground-root", str(tmp_path),
            "--canonical-fit", str(tmp_path / "fit.json"),
            "--v46-training-work-root", str(tmp_path),
            "--v22-training-work-root", str(tmp_path),
            "--output", str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        runner.main()


def test_runner_has_no_optimizer_export_or_hardware_operation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "export_" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
