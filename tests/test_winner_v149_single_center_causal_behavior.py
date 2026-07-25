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


def test_v149_preregisters_only_the_isolated_causal_cell() -> None:
    prereg = load(
        "winner_v149_single_center_causal_behavior_preregistration.json"
    )
    assert sha256(
        "winner_v149_single_center_causal_behavior_preregistration.json"
    ) == "6ace85b9dda7aff6502a54e2b873ebd64ba26b055fa8f7de49e13bf90df24321"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR"
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


def test_v149_closes_after_fixing_the_original_but_inducing_late_torque() -> None:
    result = load("winner_v149_single_center_causal_behavior_result.json")
    assert sha256(
        "winner_v149_single_center_causal_behavior_result.json"
    ) == "67ac7db8517bd72c32bf3b171e400aa40a73508d8acc3eaf8d33373fef0654f1"
    assert result["status"] == (
        "HOLD_WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR"
    )
    assert result["failed_checks"] == [
        "cell_all_frozen_gates_pass",
        "torque_event_removed",
    ]
    assert result["causal_contract"]["failed_checks"] == []
    assert result["causal_contract"]["gate"]["active_ticks"] == [394]
    assert result["causal_contract"]["state_prefix_obs_linf"] == 0
    assert result["causal_contract"]["state_prefix_hidden_linf"] == 0
    assert (
        result["causal_contract"]["center_action_linf_to_oracle"]
        <= 1.0e-7
    )
    assert 1.9200 < result["cell"]["torque_gate"][
        "worst_peak_torque_nm"
    ] < 1.9201
    assert result["cell"]["metrics"]["candidate_gate_status"] == (
        "PASS_CANDIDATE_SIM_GATE"
    )
    assert result["decision"] == "CLOSE_SINGLE_CENTER_LOCAL_RESIDUAL"
    assert result["authority"]["additional_behavior"] is False
