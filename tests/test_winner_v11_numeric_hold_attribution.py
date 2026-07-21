from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "outputs/analysis/winner_v11_numeric_hold_attribution.json"
MARKDOWN = ROOT / "outputs/analysis/WINNER_V11_NUMERIC_HOLD_ATTRIBUTION_20260720.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_winner_v11_hold_is_preserved_and_narrowly_attributed() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == (
        "PASS_WINNER_V11_HOLD_ATTRIBUTED_TO_PROTECTED_BACKEND_COMPARISON"
    )
    assert artifact["decision"] == (
        "PREREGISTER_DISTINCT_WINNER_V12_DECOMPOSED_BACKEND_CONTRACT_ONLY"
    )
    assert artifact["completed_winner_v11_reclassified_or_retried"] is False
    assert artifact["failed_checks"] == []
    assert all(artifact["checks"].values())


def test_attribution_inputs_are_hash_bound() -> None:
    artifact = load(ARTIFACT)
    for row in artifact["inputs"].values():
        path = ROOT / row["path"]
        assert path.is_file()
        assert lf_sha256(path) == row["sha256_lf"]
    assert lf_sha256(ARTIFACT) in MARKDOWN.read_text(encoding="utf-8")


def test_numeric_attribution_matches_frozen_results() -> None:
    evidence = load(ARTIFACT)["numeric_evidence"]
    assert evidence["winner_v11_frozen_tolerance"] == 1.0e-7
    assert evidence["winner_v11_moving_max_action_error"] == 4.76837158203125e-7
    assert evidence["winner_v11_moving_max_hidden_error"] == 8.940696716308594e-8
    assert evidence["winner_v11_action_error_in_float32_epsilons"] == 4.0
    assert evidence["runtime_handoff_frozen_independent_jax_tolerance"] == 1.0e-6
    assert evidence["runtime_handoff_moving_independent_jax_errors"] == {
        "512000": 8.344650268554688e-7,
        "1024000": 5.364418029785156e-7,
    }


def test_winner_v12_is_a_decomposed_contract_not_a_threshold_retry() -> None:
    artifact = load(ARTIFACT)
    hypothesis = artifact["distinct_winner_v12_hypothesis"]
    assert hypothesis["tolerance_change"] is False
    assert hypothesis["protected_policy_or_physics_change"] is False
    assert hypothesis["runtime_abi_change"] is False
    assert hypothesis["first_gate"] == (
        "new zero-PPO CPU decomposed-backend mechanics contract only"
    )
    assert artifact["authority"] == {
        "winner_v12_preregistration_design": True,
        "winner_v12_contract_run": False,
        "training_or_optimizer": False,
        "behavior_evaluation": False,
        "runtime_implementation": False,
        "robot_rdk_torque_motion_gate5_deployment": False,
        "robot_clearance": False,
    }
