from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_cpu_contract.py"


def test_runner_is_zero_update_and_baseline_anchored() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "ROLLOUT_UPDATE_INDEX = 100" in source
    assert "apply_baseline_anchored_objective" in source
    assert "recompute_gae(" not in source
    assert '"optimizer_updates": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "adam_step(" not in source
    assert "torso_com_offset_m" not in source
    assert "--hardware-authorized" not in source


def test_runner_preserves_predictor_gradient_composition() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "normalized_predictor_loss" in source
    assert "compose_gradients" in source
    assert "predictor_loss_and_gradients_bit_exact" in source
    assert "combined_delta_matches_ppo_delta_at_most_2e_6" in source
