from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"


def load_runner():
    try:
        spec = importlib.util.spec_from_file_location("winner_v12_support_gate", RUNNER)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except ModuleNotFoundError as error:
        if error.name == "jax":
            pytest.skip("local environment does not have the frozen JAX dependency")
        raise


def test_preregistered_gate_dimensions_are_unchanged() -> None:
    preregistration = json.loads(
        (
            ROOT
            / "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    gate = preregistration["future_frozen_support_gate"]
    assert gate["cells_per_checkpoint"] == 124
    assert gate["checkpoint_labels"] == ["half", "final"]
    assert gate["duration_ticks"] == 250
    assert gate["all_cells_at_both_checkpoints_must_pass"] is True


def test_episode_uses_separate_hash_bound_calibrator_design() -> None:
    runner = load_runner()
    full_training = json.loads(runner.PREREGISTRATION.read_text(encoding="utf-8"))
    assert "hidden_configuration_domain" not in full_training
    design = runner.load_calibrator_design(full_training)
    assert "hidden_configuration_domain" in design
    assert "continuous_training_domain" in design["hidden_configuration_domain"]
    source = RUNNER.read_text(encoding="utf-8")
    assert "design=preregistration" not in source
    assert source.count("calibrator_design=calibrator_design") == 3


def test_delayed_action_queue_is_exact() -> None:
    runner = load_runner()
    one = np.ones((14,), dtype=np.float32)
    two = np.full((14,), 2.0, dtype=np.float32)
    delay = runner.DelayedActionQueue(2)
    assert np.array_equal(delay.push(one), np.zeros((14,), dtype=np.float32))
    assert np.array_equal(delay.push(two), np.zeros((14,), dtype=np.float32))
    assert np.array_equal(delay.push(one * 3), one)


def test_imu_delay_observation_transport_is_exact() -> None:
    runner = load_runner()
    transport = runner.ObservationTransport(
        {"id": "IMU_DELAY_2", "imu_delay_ticks": 2}, None
    )
    first = np.zeros((115,), dtype=np.float32)
    first[0:6] = 1.0
    second = first.copy()
    second[0:6] = 2.0
    third = first.copy()
    third[0:6] = 3.0
    assert np.array_equal(transport.observe(first)[0:6], np.zeros((6,), np.float32))
    assert np.array_equal(transport.observe(second)[0:6], np.zeros((6,), np.float32))
    assert np.array_equal(transport.observe(third)[0:6], np.ones((6,), np.float32))


def test_native_quantization_changes_only_sensor_joint_slots() -> None:
    runner = load_runner()
    values = np.linspace(-0.7, 0.7, 115, dtype=np.float32)
    quantized = runner.native_quantize_observation(values)
    changed = np.flatnonzero(quantized != values)
    assert set(changed).issubset(set(range(0, 6)) | set(range(13, 41)))
    assert changed.size > 0
    assert np.array_equal(quantized[6:13], values[6:13])
    assert np.array_equal(quantized[41:115], values[41:115])


def test_support_pass_requires_every_frozen_boundary() -> None:
    runner = load_runner()
    summary = {
        "valid_ticks": 250,
        "initial_contacts": [1, 1],
        "minimum_base_z_m": runner.smoke.MINIMUM_BASE_Z_M,
        "maximum_abs_tilt_rad": runner.smoke.MAXIMUM_ABS_TILT_RAD,
        "maximum_torque_nm": runner.smoke.TORQUE_LIMIT_NM,
        "maximum_current_a": runner.smoke.CURRENT_LIMIT_A,
        "maximum_overcurrent_streak_ticks": 99,
        "maximum_final_window_gyro_xy_norm_rad_s": runner.smoke.FINAL_GYRO_LIMIT_RAD_S,
    }
    assert runner.support_pass(summary)
    summary["valid_ticks"] = 249
    assert not runner.support_pass(summary)


def test_runner_requires_explicit_offline_gate_authority() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--formal-gate-authorized" in source
    assert '"formal_support_cells": 248' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
