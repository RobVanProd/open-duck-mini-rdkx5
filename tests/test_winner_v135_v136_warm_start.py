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


def test_v135_derives_one_phase_consistent_state_without_search() -> None:
    prereg = load("winner_v135_phase_consistent_hidden_preregistration.json")
    contract = load("winner_v135_phase_consistent_hidden_contract.json")
    vector = load("winner_v135_phase_consistent_hidden_vector.json")
    assert sha256("winner_v135_phase_consistent_hidden_contract.json") == (
        "068d8f450a72c584111b1855bd302f1be334367dd87f6a328e3be4f7c495dc85"
    )
    assert prereg["derivation"]["phase_period_ticks"] == 27
    assert prereg["derivation"]["selected_tick"] == 594
    assert contract["status"] == (
        "PASS_WINNER_V135_PHASE_CONSISTENT_HIDDEN_CONTRACT"
    )
    assert contract["failed_checks"] == []
    assert contract["cross_plant_hidden_linf"] == 0.0
    assert contract["checks"]["x0_action_exact_zero"] is True
    assert contract["checks"]["moving_first_action_rate_bound_exact"] is True
    assert len(vector["h_in"]) == 64
    assert contract["decision"] == (
        "EARN_ONE_V136_WARM_START_STARTUP_SCREEN_PREREGISTRATION"
    )


def test_v136_closes_static_warm_start_on_paired_torque_evidence() -> None:
    result = load("winner_v136_warm_start_startup_result.json")
    assert sha256("winner_v136_warm_start_startup_result.json") == (
        "9347cdc8e627aaced830ef0a2cd0bc096793f016dd614c1b85bafe6ae2b4347c"
    )
    assert result["status"] == "HOLD_WINNER_V136_WARM_START_STARTUP_SCREEN"
    assert set(result["failed_checks"]) == {
        "warm_peak_torque_no_worse_each_plant",
        "warm_zero_current_violations",
        "warm_zero_torque_violations",
        "zero_baseline_reproduces_startup_violation",
    }
    comparisons = {row["plant"]: row for row in result["comparisons"]}
    assert comparisons["P30_ALL_JOINT"]["baseline_violation_events"] == 0
    assert comparisons["P30_ALL_JOINT"]["warm_violation_events"] == 1
    assert comparisons["P30_ALL_JOINT"]["peak_torque_delta_nm"] > 0.0
    robust = comparisons["P31_34_PITCH_WITH_P30_NONPITCH"]
    assert robust["baseline_violation_events"] == 1
    assert robust["warm_violation_events"] == 1
    assert robust["peak_torque_delta_nm"] < 0.0
    assert result["decision"] == "CLOSE_PHASE_CONSISTENT_WARM_START"
    assert result["authority"]["v137_dual_checkpoint_preregistration"] is False
    assert result["authority"]["formal_behavior"] is False
