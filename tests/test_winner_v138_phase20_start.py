from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v138_audit_correction_precedes_behavior() -> None:
    v1 = load("winner_v138_phase20_start_audit.json")
    v2 = load("winner_v138_phase20_start_audit_v2.json")
    assert v1["failed_checks"] == ["all_input_hashes_exact"]
    assert v1["authority"]["behavior_evaluation"] is False
    assert v2["supersedes"]["artifact"] == (
        "winner_v138_phase20_start_audit.json"
    )
    assert "transcribed incorrectly" in v2["supersedes"]["reason"]
    assert sha256("winner_v138_phase20_start_audit_v2.json") == (
        "9046d387dcc8bd59d1c2449138f4c72edea3ae13cdc46ebc6b6ae4f1cee145f7"
    )


def test_v138_phase20_is_selected_without_behavior_search() -> None:
    audit = load("winner_v138_phase20_start_audit_v2.json")
    assert audit["status"] == "PASS_WINNER_V138_PHASE20_START_AUDIT"
    assert audit["selection"]["selected_phase_index"] == 20
    assert audit["selection"]["phase_scan_authorized"] is False
    assert audit["selection"]["selection_weight_from_behavior_outcomes"] == 0
    assert audit["selection"]["selected_pitch_reference_linf"] < (
        audit["selection"]["phase_zero_pitch_reference_linf"]
    )
    assert audit["causal_evidence"] == {
        "v121_startup_torque_events": 13,
        "v121_torque_events": 15,
        "v131_projected_ticks": 17,
        "v131_startup_projected_ticks": 15,
    }


def test_v138_preregistration_freezes_single_phase_and_stop_rule() -> None:
    prereg = load("winner_v138_phase20_start_preregistration.json")
    assert sha256(
        "winner_v138_phase20_start_preregistration.json"
    ) == "f163fdef586739fe8c769727c06b2a056c308947c41744a685312f71b7889eb8"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V138_PHASE20_START_SCREEN"
    )
    assert prereg["failed_checks"] == []
    assert prereg["mechanism"]["reference_start_phase"] == 20
    assert prereg["matrix"]["cells"] == 16
    assert prereg["matrix"]["rows"][0]["checkpoint_id"] == (
        "V121_TRAIN_MATCHED_FINAL"
    )
    assert "first failing cell" in prereg["matrix"]["stop"]
    assert prereg["authority"]["other_phase_evaluation"] is False
    assert prereg["authority"]["runtime_contract_change"] is False
    assert prereg["authority"]["training"] is False


def test_v138_phase_identity_amendment_is_numeric_only() -> None:
    result = load("winner_v138_phase20_start_result.json")
    amendment = load("winner_v138_phase_identity_amendment.json")
    assert sha256("winner_v138_phase20_start_result.json") == (
        "c7b2fb1831dcf1bf1e9ba8d8d894e001765339fcef51f2564e3f93b400b3bd9b"
    )
    assert result["summary"]["cells_completed"] == 1
    assert result["cells"][0]["identity"]["command_x_m_s"] == 0.0
    assert result["cells"][0]["failure_reasons"] == [
        "phase20_first_observation_exact"
    ]
    assert sha256("winner_v138_phase_identity_amendment.json") == (
        "34320cb682d5b8462488a3bd7c506db5e2a6b2adc01d81336bb279914589aeaa"
    )
    assert amendment["status"] == (
        "PASS_WINNER_V138_PHASE_IDENTITY_AMENDMENT"
    )
    assert amendment["attribution"]["source_vs_observed_linf"] == 0.0
    assert amendment["amendment"]["selected_phase_changed"] is False
    assert amendment["amendment"]["behavior_thresholds_changed"] is False
    assert amendment["authority"]["moving_behavior"] is False


def test_v138_v2_preregistration_keeps_matrix_and_stop_rule() -> None:
    v1 = load("winner_v138_phase20_start_preregistration.json")
    v2 = load("winner_v138_phase20_start_preregistration_v2.json")
    assert sha256(
        "winner_v138_phase20_start_preregistration_v2.json"
    ) == "d43c308f570acfd732156123b148f990f40ad9a50cc1fdcfe9dab73e3cbee458"
    assert v2["status"] == (
        "PREREGISTERED_WINNER_V138_PHASE20_START_SCREEN_V2"
    )
    assert v2["supersedes"]["artifact"] == (
        "winner_v138_phase20_start_preregistration.json"
    )
    assert v2["matrix"] == v1["matrix"]
    assert v2["pass_rule"] == v1["pass_rule"]
    assert v2["stop_rule"] == v1["stop_rule"]
    assert v2["mechanism"] == v1["mechanism"]


def test_v138_phase20_closes_on_first_moving_cell() -> None:
    result = load("winner_v138_phase20_start_result_v2.json")
    assert sha256("winner_v138_phase20_start_result_v2.json") == (
        "8e0ee98ac9208496bc357ede853a2bee3269426b506666359f2a5267fc8a502d"
    )
    assert result["status"] == "HOLD_WINNER_V138_PHASE20_START_SCREEN"
    assert result["decision"] == "CLOSE_PHASE20_START"
    assert result["summary"]["cells_completed"] == 2
    assert result["summary"]["passing_cells"] == 1
    moving = result["cells"][1]
    assert moving["identity"]["command_x_m_s"] == 0.074
    assert moving["failure_reasons"] == [
        "current_peak_at_most_2p5",
        "torque_peak_at_most_1p91229675_nm",
    ]
    assert moving["torque_gate"]["worst_peak_torque_nm"] > 2.04
    assert moving["prospective_current_gate"]["worst_peak_current_a"] > 2.60
    assert moving["metrics"]["candidate_gate_status"] == (
        "PASS_CANDIDATE_SIM_GATE"
    )
    assert moving["metrics"]["worst_tracking_p95_rad"] < 0.15
    assert result["selection"]["other_phases_evaluated"] == []
    assert result["authority"]["training"] is False
