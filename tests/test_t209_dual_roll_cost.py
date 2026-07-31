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


def test_t209_composer_restores_pure_v127_engine() -> None:
    text = (
        ROOT / "tools" / "compose_t209_dual_roll_cost_playground.py"
    ).read_text(encoding="utf-8")
    assert '["git", "show", f"HEAD:{path}"]' in text
    assert '"v173_tangent_selector_absent"' in text
    assert '"mixed_lagrangian_advantage_present"' in text


def test_t209_cpu_contract_freezes_scope_and_authority() -> None:
    builder = (
        ROOT
        / "tools"
        / "build_t209_dual_roll_cost_cpu_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools" / "run_t209_dual_roll_cost_cpu_contract.py"
    ).read_text(encoding="utf-8")
    assert '"source": "T203_HALF"' in builder
    assert '"cost_scale": 1.0' in builder
    assert '"deployment_graph_change": False' in builder
    assert '"hosted_training": False' in builder
    assert '"gate5": False' in builder
    assert '"--winner_v127_constrained_cost"' in runner
    assert '"--winner_t209_dual_roll_cost"' in runner
    assert "only_t203_negative_adapter_head_changes" in runner
    assert "every_cost_critic_leaf_changes" in runner
    assert "step_zero_raw_onnx_byte_exact" in runner
    assert "no_formal_behavior_hosted_or_hardware" in runner
