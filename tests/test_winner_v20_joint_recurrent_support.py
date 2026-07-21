from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/winner_v20_joint_recurrent_support.py"


def assignments() -> dict[str, object]:
    tree = ast.parse(PATCH.read_text(encoding="utf-8"))
    values: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                try:
                    values[target.id] = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    pass
    return values


def test_trainable_and_frozen_leaf_boundary_is_exact() -> None:
    value = assignments()
    assert value["RECURRENT_CORE_KEYS"] == (
        "obs_weight",
        "previous_action_weight",
        "hidden_weight",
        "hidden_bias",
    )
    assert value["FROZEN_AUXILIARY_KEYS"] == (
        "auxiliary_hidden_weight",
        "auxiliary_action_weight",
        "auxiliary_bias",
    )


def test_joint_loss_recomputes_hidden_and_rollout_retains_observations() -> None:
    source = PATCH.read_text(encoding="utf-8")
    assert "jax.lax.scan" in source
    assert "jax.vmap" in source
    assert 'batch["observations"]' in source
    assert 'batch["valid_mask"][..., None] > 0' in source
    assert '"sampled_hidden_replay_max_abs_error"' in source
    assert 'recurrent_batch["hidden"] = hidden' in source
    assert '"observations": observations' in source
    assert "v15.valid_transition_reward" in source
    assert "maximum_target_offset" not in source
    assert "flat_transport" not in source


def test_joint_snapshot_reader_requires_exact_stage_and_optimizer_schema() -> None:
    source = PATCH.read_text(encoding="utf-8")
    assert 'metadata.get("stage") != "joint_recurrent_stage2"' in source
    assert "optimizer_keys = set(JOINT_TRAINABLE_KEYS)" in source
    assert "base.DEPLOYABLE_CALIBRATOR_KEYS + base.TRAINING_ONLY_STAGE2_KEYS" in source
    assert "Winner-v20 snapshot member schema changed" in source
