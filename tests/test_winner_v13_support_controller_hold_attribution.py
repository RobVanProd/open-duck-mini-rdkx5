from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v13_support_controller_hold_attribution.py"
ATTRIBUTION = (
    ROOT / "outputs/analysis/winner_v13_support_controller_hold_attribution.json"
)
FORMAL = ROOT / "outputs/analysis/winner_v13_support_controller_gate_result.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v13_hold_attribution", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_formal_hold_is_bound_and_physical_failure_is_exact() -> None:
    module = load_builder()
    formal = json.loads(FORMAL.read_text(encoding="utf-8"))
    module.validate_formal_result(formal)
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["formal_result"]["sha256"] == module.EXPECTED_RESULT_SHA256
    physical = value["physical_failure"]
    assert physical["classification"] == "NEGATIVE_X_EARLY_PITCH_INSTABILITY"
    assert physical["all_failures_have_negative_torso_com_x"] is True
    assert physical["all_failures_are_roll_pitch_only"] is True
    assert physical["sensor_transport_failures"] == 0
    assert {
        label: row["failure_count"]
        for label, row in physical["checkpoint_results"].items()
    } == {"half": 15, "final": 11}
    for row in physical["checkpoint_results"].values():
        assert all(
            offset < 0.0
            for offset in row["failure_configuration_x_offsets_m"].values()
        )
        assert row["failed_terminal_checks"] == {
            "roll_pitch": row["failure_count"]
        }
        assert row["all_16_contexts_separate"] is True
        assert row["all_32_repeats_bit_exact"] is True


def test_reporting_bug_is_coordinate_only_and_does_not_select_transport() -> None:
    module = load_builder()
    checks = module.validate_reporting_path()
    assert all(checks.values())
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    reporting = value["reporting_defect"]
    assert reporting["classification"] == "NORMALIZED_PREDICTION_MISREAD_AS_RAW_RESPONSE"
    assert reporting["outcome_effect"] == "REPORTING_ONLY_ACTION_AND_PHYSICS_UNCHANGED"
    assert value["evidence_selected_next_step"]["flat_transport_kernel_selected"] is False
    assert value["authority"]["robot_clearance"] is False


def test_constant_contact_example_reproduces_legacy_amplification() -> None:
    prediction_normalized = np.zeros((2,), dtype=np.float32)
    target_raw = np.ones((2,), dtype=np.float32)
    target_mean = np.ones((2,), dtype=np.float32)
    target_std = np.full((2,), np.float32(1.0e-6), dtype=np.float32)
    legacy = np.square((prediction_normalized - target_raw) / target_std)
    corrected = np.square(
        prediction_normalized - ((target_raw - target_mean) / target_std)
    )
    assert np.allclose(legacy, np.full((2,), 1.0e12), rtol=2.0e-7)
    assert np.array_equal(corrected, np.zeros((2,), dtype=np.float32))
