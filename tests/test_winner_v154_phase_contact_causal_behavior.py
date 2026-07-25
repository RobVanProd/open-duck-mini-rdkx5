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


def test_v154_preregisters_only_the_original_causal_cell() -> None:
    prereg = load(
        "winner_v154_phase_contact_causal_behavior_preregistration.json"
    )
    assert sha256(
        "winner_v154_phase_contact_causal_behavior_preregistration.json"
    ) == "0bf06e7821095c9167e38dff40a9ac7b134adf95a7cba0137b9947cd5d102ae2"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR"
    )
    assert prereg["failed_checks"] == []
    assert prereg["matrix"]["rows"] == 1
    row = prereg["matrix"]["row"]
    assert row["plant"] == "P30_ALL_JOINT"
    assert row["command_x_m_s"] == 0.074
    assert row["seed"] == 167_931_544
    assert row["duration_ticks"] == 600
    assert prereg["authority"]["behavior_cells"] == 1
    assert prereg["authority"]["additional_behavior"] is False
    assert prereg["authority"]["training"] is False
    assert prereg["authority"]["policy_deployment"] is False


def test_v154_closes_phase_only_trigger_after_torque_worsens() -> None:
    result = load("winner_v154_phase_contact_causal_behavior_result.json")
    assert sha256(
        "winner_v154_phase_contact_causal_behavior_result.json"
    ) == "ae5d4348222d16adae8dc34b61d135ea3fdd76c9c154bc09daaf0301bc69df7b"
    assert result["status"] == (
        "HOLD_WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR"
    )
    assert result["failed_checks"] == [
        "cell_all_frozen_gates_pass",
        "torque_gate_green",
    ]
    assert result["causal_contract"]["failed_checks"] == []
    assert result["causal_contract"]["first_activation_tick"] == 43
    assert result["causal_contract"]["gate"]["active_ticks"] == list(
        range(43, 584, 27)
    )
    assert result["causal_contract"]["state_prefix_obs_linf"] == 0
    assert result["cell"]["metrics"]["candidate_gate_status"] == (
        "PASS_CANDIDATE_SIM_GATE"
    )
    assert 1.971 < result["cell"]["torque_gate"][
        "worst_peak_torque_nm"
    ] < 1.972
    assert result["decision"] == "CLOSE_PHASE_CONTACT_RESIDUAL"
    assert result["authority"]["additional_behavior"] is False
