from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v15_pitch_margin_support_hold_attribution.json"


def test_hold_attribution_is_exact_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_HOLD_ATTRIBUTION"
    assert value["decision"] == "CLOSE_PITCH_MARGIN_OBJECTIVE_PREREGISTER_ACTION_DIRECTION_DIAGNOSTIC"
    assert value["comparison_to_v13"] == {
        "v13_failure_counts": {"half": 15, "final": 11},
        "v15_failure_counts": {"half": 12, "final": 12},
        "half_delta": -3,
        "final_delta": 1,
        "persistent_core_removed": False,
        "persistence_pass": False,
    }
    physical = value["physical_failure"]
    assert physical["persistent_failure_configuration_ids"] == [
        "COM_CORNER_01", "COM_CORNER_03", "COM_X_NEG", "DISCOVERY_03", "HELDOUT_04", "HELDOUT_09"
    ]
    assert physical["all_failures_are_roll_pitch_only"] is True
    assert physical["all_failures_have_negative_torso_com_x"] is True
    assert physical["sensor_transport_failures"] == 0
    for label in ("half", "final"):
        row = physical["checkpoint_results"][label]
        assert row["failure_count"] == 12
        assert row["failed_terminal_checks"] == {"roll_pitch": 12}
        assert row["all_16_contexts_separate"] is True
        assert row["all_32_repeats_bit_exact"] is True
    assert value["objective_decision"]["one_sided_negative_pitch_margin_closed"] is True
    assert value["evidence_selected_next_step"]["flat_transport_kernel_selected"] is False
    assert value["execution"] == {
        "new_optimizer_updates": 0,
        "new_behavior_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_attribution_builder_cannot_run_training_or_hardware() -> None:
    source = (ROOT / "tools/build_winner_v15_pitch_margin_support_hold_attribution.py").read_text(encoding="utf-8")
    assert "--hardware-authorized" not in source
    assert "--formal-gate-authorized" not in source
    assert "import jax" not in source
    assert "onnxruntime" not in source
