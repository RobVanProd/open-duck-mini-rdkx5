from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v96_response_conditioned_mechanics_preregistration.json"
)
RESULT = ROOT / "outputs/analysis/winner_v96_response_conditioned_mechanics_result.json"
NETWORK = ROOT / "patches/winner_v96_response_conditioned_networks.py"
RUNNER = ROOT / "tools/run_winner_v96_response_conditioned_mechanics.py"


def test_preregistration_freezes_selected_sources_and_flat_transport_off() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS"
    assert value["binary_sources"]["protected_policy"]["sha256"] == (
        "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
    )
    assert value["source_evidence"]["v92_result_sha256"] == (
        "3f706f1a36b66f7cd5d1a78d693162bdfa47dcf02fa18bb5556c6936494ae652"
    )
    assert value["source_evidence"]["v95_result_sha256"] == (
        "034e2e65c6d4f92082bfba63f8b2c57f6e79d0d2b97627f1021ff727106cab55"
    )
    initialization = value["fixed_initialization"]
    assert initialization["flat_transport_feature_enabled"] is False
    assert initialization["stable_v95_readout_exported"] is False
    assert initialization["action_heads_and_context_paths"] == (
        "exact-zero at zero update"
    )


def test_preregistration_freezes_exact_population_and_authority() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["test_population"] == {
        "golden_commands_x": [0.0, 0.08],
        "golden_ticks": 1200,
        "invalid_handoff_cases": 9,
        "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "signed_calibration_cells": 4,
        "signed_configuration_ids": ["COM_X_NEG", "COM_X_POS"],
        "stress_cases": 256,
    }
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["deployment_authorized"] is False
    assert value["authority"]["robot_clearance"] is False


def test_network_handoff_is_immutable_and_fail_closed() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "patches"))
    import winner_v96_response_conditioned_networks as networks

    context = np.zeros((1, 64), dtype=np.float32)
    accepted = networks.validate_calibration_handoff(
        context,
        completed_ticks=250,
        all_ticks_valid=True,
        support_valid=True,
    )
    assert not accepted.flags.writeable
    invalid = [
        (context[:, :63], 250, True, True),
        (context.astype(np.float64), 250, True, True),
        (np.full_like(context, np.nan), 250, True, True),
        (np.full_like(context, -1.01), 250, True, True),
        (np.full_like(context, 1.01), 250, True, True),
        (context, 249, True, True),
        (context, 251, True, True),
        (context, 250, False, True),
        (context, 250, True, False),
    ]
    for candidate, ticks, valid, support in invalid:
        with pytest.raises(ValueError):
            networks.validate_calibration_handoff(
                candidate,
                completed_ticks=ticks,
                all_ticks_valid=valid,
                support_valid=support,
            )


def test_runner_has_no_training_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "--offline-cpu-only" in source
    assert "--formal-contract-authorized" in source
    assert "export_universal_calibrator_onnx" in source
    assert "export_locomotion_onnx" in source
    assert "flat_transport" not in NETWORK.read_text(encoding="utf-8")


def test_formal_result_passes_every_mechanics_check() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS"
    assert value["decision"] == "PREREGISTER_RESPONSE_CONDITIONED_LOCOMOTION_TRAINING"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert all(value["signed_calibration"]["checks"].values())
    assert all(value["golden_replay"]["checks"].values())
    assert all(value["nonzero_adapter_stress"]["checks"].values())


def test_formal_result_preserves_default_off_and_graph_boundaries() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    golden = value["golden_replay"]
    assert sum(row["ticks"] for row in golden["rows"]) == 1200
    assert all(row["adapter_disabled_action_and_state_bit_exact"] for row in golden["rows"])
    assert all(row["x0_actions_exact_zero"] for row in golden["rows"])
    stress = value["nonzero_adapter_stress"]
    assert stress["cases"] == 256
    assert stress["maximum_adapter_delta_magnitude"] > 1.0e-4
    assert stress["checks"]["absolute_and_rate_bounds_hold"]
    assert stress["checks"]["actual_centered_pitch_guard_holds"]
    assert stress["checks"]["x0_deadband_is_exact"]
    assert value["execution"] == {
        "golden_ticks": 1200,
        "onnx_exports": 4,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "simulator_cells": 4,
        "stress_cases": 256,
    }
