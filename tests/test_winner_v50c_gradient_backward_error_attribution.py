from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v50c_gradient_backward_error_attribution.py"
RUNNER = ROOT / "tools/run_winner_v50c_gradient_backward_error_attribution.py"
CONTRACT = ROOT / "outputs/analysis/winner_v50c_gradient_backward_error_attribution_contract.json"
RESULT = ROOT / "outputs/analysis/winner_v50c_gradient_backward_error_attribution_result.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_relative_bound_is_exact_sqrt_float32_epsilon() -> None:
    runner = load(RUNNER, "winner_v50c_bound")
    assert runner.FLOAT32_EPSILON == float(np.finfo(np.float32).eps)
    assert runner.RELATIVE_ERROR_BOUND == math.sqrt(runner.FLOAT32_EPSILON)


def test_backward_error_evidence_is_scale_aware() -> None:
    runner = load(RUNNER, "winner_v50c_scale")
    left = np.asarray([100.0, -50.0, 0.0], dtype=np.float32)
    right = left.copy()
    right[0] = np.nextafter(right[0], np.float32(np.inf))
    evidence = runner.tree_backward_error_evidence({"x": left}, {"x": right})["x"]
    assert evidence["maximum_relative_error"] < runner.RELATIVE_ERROR_BOUND
    assert evidence["rms_relative_error"] < runner.RELATIVE_ERROR_BOUND
    assert evidence["material_sign_change_count"] == 0


def test_backward_error_rejects_material_sign_change() -> None:
    runner = load(RUNNER, "winner_v50c_sign")
    evidence = runner.tree_backward_error_evidence(
        {"x": np.asarray([1.0], dtype=np.float32)},
        {"x": np.asarray([-1.0], dtype=np.float32)},
    )
    assert not runner.all_leaves_within_bound(evidence)
    assert evidence["x"]["material_sign_change_count"] == 1


def test_backward_error_rejects_non_float32() -> None:
    runner = load(RUNNER, "winner_v50c_dtype")
    with pytest.raises(ValueError, match="finite float32"):
        runner.tree_backward_error_evidence(
            {"x": np.asarray([1.0], dtype=np.float64)},
            {"x": np.asarray([1.0], dtype=np.float64)},
        )


def test_builder_binds_frozen_v50b_hold() -> None:
    builder = load(BUILDER, "winner_v50c_builder")
    frozen = json.loads(builder.V50B_RESULT.read_text(encoding="utf-8"))
    assert builder.sha256(builder.V50B_RESULT) == builder.EXPECTED_V50B_RESULT_SHA256
    assert frozen["status"] == "HOLD_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION"


def test_generated_contract_is_source_bound_when_present() -> None:
    if not CONTRACT.exists():
        return
    runner = load(RUNNER, "winner_v50c_generated")
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    runner.validate_contract(value)
    assert value["frozen_holds"]["results_rewritten"] is False
    assert value["frozen_holds"]["absolute_or_ulp_limits_changed"] is False
    assert value["authority"]["one_update_authorized"] is False


def test_result_remains_zero_update_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION",
        "HOLD_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION",
    }
    assert value["execution"]["optimizer_updates"] == 0
    assert value["authority"]["one_update_authorized"] is False


def test_runner_requires_explicit_cpu_authority(monkeypatch, tmp_path: Path) -> None:
    runner = load(RUNNER, "winner_v50c_authority")
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
    assert '"robot_or_rdk_access": 0' in source
