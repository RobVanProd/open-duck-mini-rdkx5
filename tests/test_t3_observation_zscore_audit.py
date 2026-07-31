from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_channel_map_is_frozen_101_contract():
    audit = load_module(
        "t3_audit",
        ROOT / "tools" / "run_t3_observation_zscore_audit.py",
    )
    names = audit.channel_names()
    assert len(names) == 101
    assert names[3] == "accel_x_m_s2"
    assert names[13] == "position_error_left_hip_yaw_rad"
    assert names[27] == "velocity_scaled_left_hip_yaw"
    assert names[41] == "action_t_minus_1_left_hip_yaw"
    assert names[83] == "previous_target_left_hip_yaw_rad"
    assert names[97:101] == [
        "contact_left",
        "contact_right",
        "phase_cos",
        "phase_sin",
    ]


def test_sustained_rule_is_consecutive_not_total_occupancy():
    audit = load_module(
        "t3_audit_runs",
        ROOT / "tools" / "run_t3_observation_zscore_audit.py",
    )
    values = np.asarray(
        [True] * 49 + [False] + [True] * 50 + [False] + [True] * 10
    )
    assert audit.longest_true_run(values) == 50


def test_normalization_error_fails_loudly():
    telemetry = load_module(
        "telemetry_for_t3",
        ROOT / "instrumentation" / "mini_bdx_runtime" / "telemetry.py",
    )
    with pytest.raises(RuntimeError, match="No module named 'onnx'"):
        telemetry.require_onnx_obs_normalization(
            {
                "mean": None,
                "std_recip": None,
                "error": 'ModuleNotFoundError("No module named \'onnx\'")',
            },
            "BEST_WALK_ONNX_2.onnx",
        )


def test_extracted_baseline_normalizer_is_required_and_exact():
    telemetry = load_module(
        "telemetry_for_t3_exact",
        ROOT / "instrumentation" / "mini_bdx_runtime" / "telemetry.py",
    )
    policy = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
    info = telemetry.extract_onnx_obs_normalization(policy)
    returned = telemetry.require_onnx_obs_normalization(info, policy)
    assert len(returned["mean"]) == 101
    assert len(returned["std_recip"]) == 101
    assert returned["mean"][3] == pytest.approx(-0.03789431229233742)
    assert returned["std_recip"][3] == pytest.approx(0.4973900616168976)


def test_capture_callers_require_normalization_before_logging():
    runtime_source = (
        ROOT / "runtime" / "scripts" / "v2_rl_walk_mujoco.py"
    ).read_text(encoding="utf-8")
    diagnostic_source = (
        ROOT / "instrumentation" / "scripts" / "sim2real_diagnostics.py"
    ).read_text(encoding="utf-8")
    assert "require_onnx_obs_normalization(" in runtime_source
    assert diagnostic_source.count("require_onnx_obs_normalization(") >= 2
