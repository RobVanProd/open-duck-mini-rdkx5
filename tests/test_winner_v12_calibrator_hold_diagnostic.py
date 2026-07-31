from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v12_calibrator_hold_diagnostic.py"
BUILDER = (
    ROOT / "tools/build_winner_v12_calibrator_hold_diagnostic_preregistration.py"
)
PREREGISTRATION = (
    ROOT
    / "outputs/analysis/winner_v12_calibrator_hold_diagnostic_preregistration.json"
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_auxiliary_mapping_ends_in_exact_contact_pair() -> None:
    runner = load(RUNNER, "winner_v12_hold_diagnostic")
    assert runner.EXPECTED_AUXILIARY_INDICES.tolist() == (
        list(range(0, 6)) + list(range(13, 41)) + list(range(83, 99))
    )
    assert runner.EXPECTED_AUXILIARY_INDICES[34:48].tolist() == list(range(83, 97))
    assert runner.EXPECTED_AUXILIARY_INDICES[48:50].tolist() == [97, 98]
    assert [runner.auxiliary_group(index) for index in (0, 6, 20, 34, 48)] == [
        "imu",
        "joint_position",
        "joint_velocity",
        "applied_target",
        "foot_contact",
    ]


def test_contact_floor_dominance_is_measured_separately() -> None:
    runner = load(RUNNER, "winner_v12_hold_prediction")
    observations = np.zeros((3, 115), dtype=np.float32)
    observations[:, 97:99] = 1.0
    predictions = observations[:, runner.EXPECTED_AUXILIARY_INDICES].copy()
    predictions[:, 48:50] = 0.5
    target_mean = np.zeros((50,), dtype=np.float32)
    target_mean[48:50] = 1.0
    target_std = np.ones((50,), dtype=np.float32)
    target_std[48:50] = np.float32(1.0e-6)
    cell = runner.prediction_cell_statistics(
        observations=observations,
        predictions=predictions,
        target_mean=target_mean,
        target_std=target_std,
    )
    aggregate = runner.aggregate_prediction_statistics([cell], target_std=target_std)
    assert aggregate["all_contact_targets_exactly_one"] is True
    assert aggregate["contact_target_std_exactly_1e_6"] is True
    assert aggregate["contact_fraction_at_least_0_99"] is True
    assert aggregate["learned_normalized_mse_noncontact_48"] == 0.0
    assert aggregate["per_dimension"][48]["observation_index"] == 97
    assert aggregate["per_dimension"][49]["observation_index"] == 98


def test_zero_action_wrapper_preserves_only_graph_hidden_state() -> None:
    runner = load(RUNNER, "winner_v12_hold_zero")

    class FakeSession:
        def run(self, output_names, inputs):
            del output_names, inputs
            return [
                np.ones((1, 14), dtype=np.float32),
                np.ones((1, 14), dtype=np.float32),
                np.full((1, 64), 0.25, dtype=np.float32),
            ]

    outputs = runner.ZeroActionSession(FakeSession()).run([], {})
    assert np.array_equal(outputs[0], np.zeros((1, 14), dtype=np.float32))
    assert np.array_equal(outputs[1], np.zeros((1, 14), dtype=np.float32))
    assert np.array_equal(outputs[2], np.full((1, 64), 0.25, dtype=np.float32))


def test_action_statistics_include_initial_zero_step() -> None:
    runner = load(RUNNER, "winner_v12_hold_action")
    values = np.zeros((2, 14), dtype=np.float32)
    values[0, 0] = 0.25
    values[1, 0] = 0.5
    result = runner.action_statistics(values)
    assert result["all_zero"] is False
    assert result["peak_abs_by_joint"][0] == 0.5
    assert result["peak_abs_step_by_joint"][0] == 0.25


def test_builder_binds_the_completed_hold_without_advancement() -> None:
    builder = load(BUILDER, "winner_v12_hold_builder")
    formal = json.loads(builder.FORMAL_RESULT.read_text(encoding="utf-8"))
    builder.validate_formal_hold(formal)
    assert builder.failed_configuration_ids(formal) == (
        builder.EXPECTED_FAILED_CONFIGURATION_IDS
    )


def test_generated_preregistration_is_exact_and_source_bound() -> None:
    runner = load(RUNNER, "winner_v12_hold_generated")
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC"
    assert value["decision"] == "AUTHORIZE_ONE_READ_ONLY_OFFLINE_HOLD_DIAGNOSTIC"
    assert value["frozen_population"]["graph_cells"] == 88
    assert value["frozen_population"]["zero_action_cells"] == 32
    assert value["execution_now"] == {
        "diagnostic_cells": 0,
        "training_steps": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    runner.validate_source_manifest(value)


def test_workflow_is_dormant_until_the_preregistration_is_committed() -> None:
    workflow = ROOT / ".github/workflows/winner-v12-calibrator-hold-diagnostic.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v12_calibrator_hold_diagnostic_preregistration.json" in trigger
    assert "--offline-cpu-only" in source
    assert "--hold-diagnostic-authorized" in source
    assert "--formal-gate-authorized" not in source
    assert "--hardware-authorized" not in source
    assert "--suspended-or-benched" not in source
    assert "/dev/tty" not in source
