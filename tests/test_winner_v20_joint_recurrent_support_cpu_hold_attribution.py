from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_cpu_hold_attribution.json"
)


def test_zero_action_head_selects_exactly_two_proof_updates() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_HOLD_ATTRIBUTION"
    )
    assert value["decision"] == (
        "PREREGISTER_EXACT_TWO_UPDATE_JOINT_RECURRENT_CPU_CONTRACT"
    )
    causal = value["causal_interpretation"]
    assert causal["source_action_head_exact_zero"] is True
    assert causal["classification"] == "ZERO_ACTION_HEAD_CHAIN_RULE_GATE"
    assert set(causal["update_1_recurrent_gradients_exact_zero"].values()) == {0.0}
    assert set(causal["update_1_recurrent_deltas_exact_zero"].values()) == {0.0}
    assert value["next_contract"]["optimizer_updates"] == 2
    assert value["next_contract"]["optimizer_updates_authorized_now"] == 0


def test_replay_fix_masks_padding_without_relaxing_threshold() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    replay = value["replay_metric_correction"]
    assert replay["correct_population"] == "valid_mask == 1 sampled ticks only"
    assert replay["threshold"] == 1.0e-6
    assert replay["threshold_change"] is False
    assert replay["training_loss_change"] is False
    assert value["authority"]["joint_recurrent_training_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
