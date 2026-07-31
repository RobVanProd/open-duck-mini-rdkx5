from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v24_baseline_anchored_cpu_result.py"
CONTRACT = ROOT / "outputs/analysis/winner_v24_baseline_anchored_cpu_contract.json"
RESULT = ROOT / "outputs/analysis/winner_v24_baseline_anchored_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v24_baseline_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_result_artifact_names_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v24-baseline-anchored-cpu-result.json"
    assert module.RAW_RECEIPT_NAME == "winner-v24-baseline-anchored-cpu-result.sha256"


def test_repository_attribution_is_strict() -> None:
    module = load()
    digest = "a" * 64
    value = module.repository_attribution(
        run_id=123,
        run_attempt=1,
        run_head_sha="b" * 40,
        artifact_id=456,
        artifact_name="winner-v24-baseline-anchored-cpu-contract-123",
        artifact_digest=f"sha256:{digest}",
        artifact_zip_sha256=digest,
    )
    assert value["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    with pytest.raises(ValueError, match="attribution changed"):
        module.repository_attribution(
            run_id=123,
            run_attempt=2,
            run_head_sha="b" * 40,
            artifact_id=456,
            artifact_name="winner-v24-baseline-anchored-cpu-contract-123",
            artifact_digest=f"sha256:{digest}",
            artifact_zip_sha256=digest,
        )


def synthetic_result(module):
    receipt = module.final_snapshot_receipt()
    gradients = {key: 1.0 for key in module.GRADIENT_KEYS}
    population = {
        "episode_slots": 80,
        "roll_pitch_failure_count": 12,
        "settled_success_count": 22,
        "episode_receipts_sha256": "8" * 64,
    }
    disabled = {
        "anchor": "recorded_baseline_returns_and_rederived_values",
        "enabled": False,
        "modified_batch_keys": [],
        "penalty": -250.0,
        "roll_pitch_failure_count": 12,
        "roll_pitch_failure_mask_sha256": "1" * 64,
    }
    enabled = {
        **disabled,
        "enabled": True,
        "modified_batch_keys": ["advantages", "returns", "rewards"],
        "analytical_terminal_delta_max": 0.0,
        "analytical_terminal_delta_min": -250.0,
        "analytical_terminal_delta_nonzero_count": 120,
        "analytical_terminal_delta_sha256": "9" * 64,
        "baseline_raw_advantages_sha256": "a" * 64,
    }
    batch = {
        "action_boundary": {
            "realized_equals_numpy_bit_exact": True,
            "numpy_equals_jax_bit_exact": True,
        },
        "all_other_rewards_bit_exact": True,
        "analytical_terminal_delta_and_renormalization_exact": True,
        "analytical_terminal_delta_nonzero_count": 120,
        "analytical_terminal_delta_sha256": "9" * 64,
        "baseline_advantages_sha256": "2" * 64,
        "baseline_returns_sha256": "3" * 64,
        "baseline_reward": {"reward_formula_bit_exact": True},
        "baseline_rewards_sha256": "4" * 64,
        "changed_keys": ["advantages", "returns", "rewards"],
        "default_off_batch_bit_exact": True,
        "disabled": disabled,
        "enabled": enabled,
        "objective_advantages_sha256": "5" * 64,
        "objective_returns_sha256": "6" * 64,
        "objective_rewards_sha256": "7" * 64,
        "parameters_unchanged": True,
        "terminal_failure_penalty_exact": True,
    }
    gradient = {
        "baseline_normalized_predictor_loss": 0.1,
        "baseline_ppo_gradient_max_abs": gradients,
        "baseline_ppo_loss": 1.0,
        "combined_delta_minus_ppo_delta_max_abs_error": 0.0,
        "combined_gradient_delta_max_abs": gradients,
        "objective_normalized_predictor_loss": 0.1,
        "objective_ppo_gradient_max_abs": gradients,
        "objective_ppo_loss": 2.0,
        "ppo_gradient_delta_max_abs": gradients,
        "predictor_gradients_bit_exact": True,
    }
    checks = {
        "source_final_snapshot_exact": True,
        "one_ulp_attribution_authority_exact": True,
        "exact_80_episode_population": True,
        "episode_receipts_exact": True,
        "action_boundary_exact": True,
        "baseline_pitch_margin_reward_exact": True,
        "recorded_baseline_is_authoritative_no_gae_reconstruction": True,
        "default_off_batch_bit_exact": True,
        "roll_pitch_failures_and_settled_successes_both_present": True,
        "enabled_changes_only_rewards_returns_advantages": True,
        "terminal_failure_penalty_exact": True,
        "all_other_rewards_bit_exact": True,
        "analytical_terminal_delta_and_renormalization_exact": True,
        "analytical_terminal_delta_is_nonzero": True,
        "predictor_loss_and_gradients_bit_exact": True,
        "ppo_action_head_gradient_changes": True,
        "ppo_recurrent_gradient_changes": True,
        "combined_delta_matches_ppo_delta_at_most_2e_6": True,
        "all_losses_metrics_and_gradients_finite": True,
        "parameters_unchanged_no_optimizer_step": True,
        "optimizer_updates_zero": True,
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    return {
        "schema_version": "winner_v24.baseline_anchored_cpu_result.v1",
        "status": "PASS_WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT",
        "decision": "AUTHORIZE_SEPARATE_ONE_UPDATE_BASELINE_ANCHORED_CPU_PROOF_PREREGISTRATION_ONLY",
        "checks": checks,
        "failed_checks": [],
        "source_checkpoint": {
            "label": "final",
            "completed_updates": 100,
            "sha256": receipt["sha256"],
            "bytes": receipt["bytes"],
        },
        "objective": module.expected_objective(),
        "population": population,
        "batch_evidence": batch,
        "gradient_evidence": gradient,
        "execution": {
            "rollout_episode_slots": 80,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "environment": {"jax_backend": "cpu", "jax_devices": ["TFRT_CPU_0"]},
        "sources": {
            "contract_lf_sha256": module.lf_sha256(module.CONTRACT),
            "attribution_lf_sha256": module.lf_sha256(module.ATTRIBUTION),
            "v22_training_lf_sha256": module.lf_sha256(module.V22_TRAINING),
            "mechanics_lf_sha256": module.lf_sha256(module.MECHANICS),
            "runner_lf_sha256": module.lf_sha256(module.RUNNER),
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separate one-update baseline-anchored CPU-proof preregistration"
            ),
        },
    }


def test_complete_synthetic_result_and_decision_are_rederived() -> None:
    if not CONTRACT.exists():
        return
    module = load()
    value = synthetic_result(module)
    module.validate_result(value)
    value["decision"] = "DO_NOT_RUN_WINNER_V24_BASELINE_ANCHORED_OPTIMIZER_UPDATE"
    with pytest.raises(ValueError, match="decision changed"):
        module.validate_result(value)


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1
