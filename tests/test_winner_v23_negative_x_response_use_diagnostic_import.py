from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v23_negative_x_response_use_diagnostic.py"
RESULT = ROOT / "outputs/analysis/winner_v23_negative_x_response_use_diagnostic_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v23_diagnostic_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_result_artifact_names_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v23-negative-x-response-use-diagnostic-result.json"
    assert module.RAW_RECEIPT_NAME == "winner-v23-negative-x-response-use-diagnostic-result.sha256"


def test_repository_attribution_is_strict() -> None:
    module = load()
    digest = "a" * 64
    value = module.repository_attribution(
        run_id=123,
        run_attempt=1,
        run_head_sha="b" * 40,
        artifact_id=456,
        artifact_name="winner-v23-negative-x-response-use-diagnostic-123",
        artifact_digest=f"sha256:{digest}",
        artifact_zip_sha256=digest,
    )
    assert value["repository"] == "RobVanProd/open-duck-mini-rdkx5"


def test_persistent_crossing_is_independently_rederived() -> None:
    module = load()
    values = [0.0] * 4 + [2.0] * 5 + [0.0] * 16
    assert module.first_persistent_crossing(values, 1.0) == 4


def synthetic_result(module):
    trace_hashes = {
        "actions": "a" * 64,
        "hidden": "b" * 64,
        "observations": "c" * 64,
        "predictions": "d" * 64,
    }
    rows = []
    for checkpoint, update, plant, negative_id, positive_id in module._expected_sequence():
        rows.append(
            {
                "checkpoint": checkpoint,
                "update": update,
                "plant": plant,
                "negative_configuration_id": negative_id,
                "positive_configuration_id": positive_id,
                "negative_support_pass": False,
                "positive_support_pass": True,
                "negative_terminal": {"tick": 27, "reason": "roll_pitch"},
                "positive_terminal": None,
                "negative_trace_hashes": trace_hashes,
                "positive_trace_hashes": trace_hashes,
                "common_valid_transition_prefix_ticks": 28,
                "early_analysis_ticks": 25,
                "hidden_linf_by_tick": [2.0e-7] * 25,
                "actual_action_linf_by_tick": [0.0] * 25,
                "same_input_hidden_fork_action_linf_by_tick": [2.0e-5] * 25,
                "hidden_first_persistent_crossing_tick": 0,
                "fork_action_first_persistent_crossing_tick": 0,
                "response_encoded_early": True,
                "response_used_by_action_early": True,
                "negative_early_learned_normalized_prediction_mse": 0.5,
                "negative_early_constant_normalized_prediction_mse": 1.0,
                "positive_early_learned_normalized_prediction_mse": 0.5,
                "positive_early_constant_normalized_prediction_mse": 1.0,
                "predictor_beats_constant_both_signs_early": True,
            }
        )
    checks = {
        "exact_20_paired_cells": True,
        "exact_40_unchanged_physics_rollouts": True,
        "all_25_tick_windows_present": True,
        "all_metrics_finite": True,
        "all_positive_sign_controls_pass_support": True,
        "at_least_16_negative_sign_cells_reproduce_support_failure": True,
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    return {
        "schema_version": "winner_v23.negative_x_response_use_diagnostic_result.v1",
        "status": "PASS_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC",
        "decision": "AUTHORIZE_NEGATIVE_X_SUPPORT_CONTROL_OBJECTIVE_CPU_CONTRACT_ONLY",
        "classification": "RESPONSE_STATE_PRESENT_AND_USED_SUPPORT_CONTROL_INADEQUATE",
        "checks": checks,
        "failed_checks": [],
        "population": {
            "configuration_pairs": [list(pair) for pair in module.PAIR_IDS],
            "checkpoint_labels": ["half", "final"],
            "actuator_plants": list(module.PLANTS),
            "paired_cells": 20,
            "physics_rollouts": 40,
            "early_analysis_ticks": 25,
        },
        "thresholds": {
            "minimum_persistent_ticks": 5,
            "hidden_linf": 1.0e-7,
            "same_input_hidden_fork_action_linf": 1.0e-5,
            "minimum_cells_for_branch": 16,
        },
        "aggregate": {
            "response_encoded_early_cells": 20,
            "response_used_by_action_early_cells": 20,
            "predictor_beats_constant_both_signs_early_cells": 20,
            "negative_support_failure_cells": 20,
            "positive_support_failure_cells": 0,
        },
        "paired_results": rows,
        "execution": {
            "paired_cells": 20,
            "physics_rollouts": 40,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": module.lf_sha256(module.PREREGISTRATION),
            "training_result_lf_sha256": module.lf_sha256(module.TRAINING_RESULT),
            "hold_attribution_lf_sha256": module.lf_sha256(module.HOLD_ATTRIBUTION),
            "domain_lf_sha256": module.lf_sha256(module.DOMAIN),
            "base_gate_runner_lf_sha256": module.lf_sha256(module.BASE_GATE_RUNNER),
            "v22_gate_runner_lf_sha256": module.lf_sha256(module.V22_GATE_RUNNER),
            "runner_lf_sha256": module.lf_sha256(module.RUNNER),
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": "the single CPU contract named by the frozen decision tree",
        },
    }


def test_complete_synthetic_result_and_decision_are_rederived() -> None:
    module = load()
    value = synthetic_result(module)
    module.validate_result(value)
    value["decision"] = "AUTHORIZE_RESPONSE_ACTION_COUPLING_CPU_CONTRACT_ONLY"
    with pytest.raises(ValueError, match="decision changed"):
        module.validate_result(value)


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1


def test_imported_result_rejects_unrecognized_fields_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    value["unexpected"] = True
    with pytest.raises(ValueError, match="schema changed"):
        module.validate_result(value)
