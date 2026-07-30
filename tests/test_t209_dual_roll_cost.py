from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_t209_patch_uses_separate_unscaled_roll_cost() -> None:
    text = (
        ROOT / "patches" / "winner_t209_dual_roll_cost.patch"
    ).read_text(encoding="utf-8")
    assert "winner_t209_dual_roll_cost=False" in text
    assert "constrained_cost = jp.square(roll_risk_excess)" in text
    assert "winner_v127_dense_torque_exceedance_cost" in text
    assert "reward_channel=unchanged" in text
    assert "not args.winner_t202_predicted_roll_risk" in text
    assert "reward = t202.curriculum_reward" not in text


def test_t209_patch_preserves_deployment_contract() -> None:
    text = (
        ROOT / "patches" / "winner_t209_dual_roll_cost.patch"
    ).read_text(encoding="utf-8")
    assert "deployment_graph=unchanged" in text
    assert "cost_critic=separate" in text
    assert "cost_discount=1.0" in text
    assert "dual_eta=1/(ceil(K/4)*J_C0)" in text
