from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v15_pitch_margin_objective_attribution.json"


def test_attribution_selects_only_bounded_pitch_margin_cpu_contract() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V15_PITCH_MARGIN_OBJECTIVE_ATTRIBUTION"
    assert value["decision"] == "PREREGISTER_ONE_SIDED_NEGATIVE_PITCH_MARGIN_CPU_CONTRACT"
    diagnosis = value["diagnosis"]
    assert diagnosis["all_five_scales_failed"] is True
    assert diagnosis["persistent_failures_present_in_training_population"] == [
        "COM_CORNER_01",
        "COM_CORNER_03",
        "COM_X_NEG",
        "DISCOVERY_03",
    ]
    assert set(diagnosis["terminal_failed_check_counts"]) == {"roll_pitch"}
    assert diagnosis["failure_tick_range"] == [28, 71]
    assert diagnosis["all_nonzero_scales_preserve_heldout_context"] is True
    assert diagnosis["corrected_predictor_beats_constant_at_every_scale_checkpoint"] is True
    change = value["selected_single_change"]
    assert change["valid_transition_reward"] == (
        "1 - square(clip(max(0, -next_pitch_rad) / 0.35, 0, 1))"
    )
    assert value["deferred_architecture"]["flat_long_range_kernel"] == "not selected"
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["robot_clearance"] is False
