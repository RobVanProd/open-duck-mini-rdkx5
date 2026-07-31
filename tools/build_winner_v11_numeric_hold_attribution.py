#!/usr/bin/env python3
"""Attribute the frozen Winner-v11 hold without rerunning its population."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_preregistration.json"
RESULT = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_result.json"
HANDOFF_ROOT = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"
GOLDEN_EVIDENCE = HANDOFF_ROOT / "golden_evidence.json"
HANDOFF_README = HANDOFF_ROOT / "README.md"
HANDOFF_MANIFEST = HANDOFF_ROOT / "manifest.json"
OUTPUT_JSON = ANALYSIS / "winner_v11_numeric_hold_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V11_NUMERIC_HOLD_ATTRIBUTION_20260720.md"

EXPECTED_HASHES = {
    "preregistration": "adac3d194d6751b1f8a8119f3d77d4e97603834d782a477c3c88137e523162ca",
    "result": "f946b79b16a6769c87ebf31e4134d1c80c83bc6071bbeb5d61ecade387895a0a",
    "runtime_golden_evidence": "3e9d501e087e8ef415beb2a8f0462f5ac1f1852a61aa968e490e8a65f0442a3f",
    "runtime_handoff_readme": "2c0854ad8c13afb903e5ea85e1b9d03996fcd0745d2f13d3c0898b1693b36042",
    "runtime_handoff_manifest": "d771d188218152c782c7d688440e2dd2083b47fd9b883749123f89226c6827c5",
}


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    sources = {
        "preregistration": PREREGISTRATION,
        "result": RESULT,
        "runtime_golden_evidence": GOLDEN_EVIDENCE,
        "runtime_handoff_readme": HANDOFF_README,
        "runtime_handoff_manifest": HANDOFF_MANIFEST,
    }
    observed_hashes = {name: sha256_lf(path) for name, path in sources.items()}
    if observed_hashes != EXPECTED_HASHES:
        raise ValueError("Winner-v11 attribution input hashes changed")

    preregistration = load(PREREGISTRATION)
    result = load(RESULT)
    golden = load(GOLDEN_EVIDENCE)
    failed = {
        "jax_onnx_chains_within_tolerance",
        "physical_chain_jax_onnx_within_tolerance",
    }
    false_checks = {name for name, passed in result["checks"].items() if not passed}
    physical = result["protected_physical_chains"]
    x0 = result["default_off_x0_chains"]
    stress = result["enabled_stress"]
    maximum_action_error = max(row["jax_onnx_max_action_error"] for row in physical)
    maximum_hidden_error = max(row["jax_onnx_max_hidden_error"] for row in physical)
    epsilon = float(np.finfo(np.float32).eps)
    runtime_moving = {
        int(row["step"]): row
        for row in golden["cells"]
        if float(row["command_x"]) == 0.08
    }
    runtime_jax_errors = {
        str(step): float(row["independent_jax_from_onnx_initializers_max_abs_error"])
        for step, row in sorted(runtime_moving.items())
    }
    runtime_tolerance = float(
        golden["tolerances"]["independent_JAX_replay_max_abs"]
    )
    preregistered_tolerance = float(preregistration["test_population"]["numeric_tolerance"])
    checks = {
        "formal_result_remains_hold": result["status"]
        == "HOLD_WINNER_V11_ZERO_PPO_CPU_MECHANICS",
        "only_two_full_action_backend_checks_failed": false_checks == failed
        and set(result["failed_checks"]) == failed,
        "all_27_other_frozen_checks_passed": len(result["checks"]) == 29
        and sum(bool(value) for value in result["checks"].values()) == 27,
        "exact_onnx_wrapper_identity_passed": all(
            row["protected_and_expanded_bit_exact"] for row in physical + x0
        ),
        "new_hidden_math_remained_within_1e_7": maximum_hidden_error
        <= preregistered_tolerance,
        "calibrator_jax_onnx_remained_within_1e_7": max(
            result["step_zero"]["max_action_error"],
            result["step_zero"]["max_hidden_error"],
            result["calibration_chain"]["max_action_error"],
            result["calibration_chain"]["max_hidden_error"],
        )
        <= preregistered_tolerance,
        "x0_action_state_exact_zero": all(
            row["exact_zero_and_identity"] for row in x0
        ),
        "observation_phase_history_p30_contract_exact": result[
            "sequence_and_handoff"
        ]["all_exact"]
        and all(row["observation_contract_exact"] for row in physical + x0),
        "stored_and_inward_bounds_passed": all(
            row["strict_stored_bounds"] and row["internal_roundoff_bounds"]
            for row in physical + x0
        )
        and all(
            all(row["strict_stored_bounds"].values())
            and all(row["internal_roundoff_bounds"].values())
            for row in stress
        ),
        "population_and_cpu_authority_exact": result["checks"][
            "frozen_test_population_exact"
        ]
        and result["devices"] == ["TFRT_CPU_0"]
        and result["execution_counts"]
        == {"optimizer_steps": 0, "formal_behavior_cells": 0},
        "moving_action_difference_is_four_float32_epsilons": maximum_action_error
        / epsilon
        == 4.0,
        "runtime_handoff_previously_froze_1e_6_backend_scope": runtime_tolerance
        == 1.0e-6,
        "winner_v11_error_below_both_frozen_runtime_observations": all(
            maximum_action_error <= value for value in runtime_jax_errors.values()
        ),
        "runtime_onnx_golden_identity_is_exact": all(
            float(row["onnx_to_frozen_trace_max_abs_error"]) == 0.0
            and float(row["onnx_action_to_state_output_max_abs_error"]) == 0.0
            for row in golden["cells"]
        ),
        "winner_v11_close_rule_preserved": "Do not change seeds, populations, thresholds"
        in preregistration["no_retry_or_tuning"],
    }
    failed_attribution = sorted(name for name, passed in checks.items() if not passed)
    if failed_attribution:
        raise ValueError(f"Winner-v11 attribution checks failed: {failed_attribution}")

    payload = {
        "schema_version": "winner_v11.numeric_hold_attribution.v1",
        "status": "PASS_WINNER_V11_HOLD_ATTRIBUTED_TO_PROTECTED_BACKEND_COMPARISON",
        "decision": "PREREGISTER_DISTINCT_WINNER_V12_DECOMPOSED_BACKEND_CONTRACT_ONLY",
        "completed_winner_v11_reclassified_or_retried": False,
        "checks": checks,
        "failed_checks": [],
        "inputs": {
            name: {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256_lf": observed_hashes[name],
            }
            for name, path in sources.items()
        },
        "numeric_evidence": {
            "float32_epsilon": epsilon,
            "winner_v11_frozen_tolerance": preregistered_tolerance,
            "winner_v11_moving_max_action_error": maximum_action_error,
            "winner_v11_moving_max_hidden_error": maximum_hidden_error,
            "winner_v11_action_error_in_float32_epsilons": maximum_action_error
            / epsilon,
            "runtime_handoff_frozen_independent_jax_tolerance": runtime_tolerance,
            "runtime_handoff_moving_independent_jax_errors": runtime_jax_errors,
            "normalized_action_error_as_target_rad": maximum_action_error * 0.25,
        },
        "causal_attribution": {
            "failed_quantity": (
                "full protected-policy JAX transcription versus the authoritative "
                "ONNX Runtime action on moving chains"
            ),
            "not_failed": [
                "calibrator JAX/ONNX action and hidden math",
                "new locomotion hidden-state math",
                "protected ONNX versus default-off expanded ONNX identity",
                "x=0 action and recurrent state",
                "27-tick phase and t-2/t-3/t-4 histories",
                "P30 applied-target ordering and projected reference",
                "stored and inward-rounded graph action boundaries",
                "CPU-only population and zero-PPO authority",
            ],
            "interpretation": (
                "The hold does not identify a calibration-mechanics, runtime, or "
                "physical-bound failure. It identifies an over-coupled comparison: "
                "new response mechanics were gated by the old protected actor's "
                "cross-backend floating-point reproduction even though deployment "
                "executes the exact ONNX graph and wrapper identity is bit-exact."
            ),
        },
        "distinct_winner_v12_hypothesis": {
            "change": (
                "Decompose backend validation. Gate protected behavior by exact "
                "ONNX-to-ONNX wrapper identity; gate only the newly introduced "
                "calibrator/response branch JAX-to-ONNX tensors at the unchanged "
                "1e-7 tolerance; gate the final authoritative ONNX action by the "
                "unchanged stored/inward physical boundaries."
            ),
            "debug_mechanism": (
                "Use a checker-only copy of the graph exposing the internal response "
                "delta. The deployable locomotion ABI remains unchanged."
            ),
            "tolerance_change": False,
            "protected_policy_or_physics_change": False,
            "runtime_abi_change": False,
            "first_gate": "new zero-PPO CPU decomposed-backend mechanics contract only",
            "pass_authorizes_only": (
                "a separately frozen Winner-v12 calibrator-training preregistration"
            ),
            "why_distinct": (
                "Winner-v11 remains closed under its full-action backend rule. "
                "Winner-v12 changes the gated quantity and adds an explicit "
                "new-branch diagnostic output instead of changing the failed "
                "tolerance or rerunning the same contract."
            ),
        },
        "authority": {
            "winner_v12_preregistration_design": True,
            "winner_v12_contract_run": False,
            "training_or_optimizer": False,
            "behavior_evaluation": False,
            "runtime_implementation": False,
            "robot_rdk_torque_motion_gate5_deployment": False,
            "robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    output_sha = sha256_lf(OUTPUT_JSON)
    OUTPUT_MD.write_bytes(
        (
            "# Winner-v11 Numeric Hold Attribution\n\n"
            f"Status: `{payload['status']}`\n\n"
            f"Decision: `{payload['decision']}`\n\n"
            f"JSON SHA-256: `{output_sha}`\n\n"
            "Winner-v11 remains closed and is not rerun. Its only failed quantity "
            "was the full protected-policy JAX/ONNX action comparison on moving "
            f"chains: `{maximum_action_error}` (`{maximum_action_error / epsilon}` "
            "float32 epsilons) against the frozen `1e-7` rule. The calibrator, new "
            "hidden-state math, exact ONNX wrapper identity, x=0, 27-tick phase, "
            "action histories, P30 observer, and all action boundaries passed.\n\n"
            "The distinct Winner-v12 hypothesis does not relax that threshold. It "
            "separates exact protected ONNX identity from the new response branch's "
            "JAX/ONNX comparison, while keeping the deployable ABI and physical "
            "bounds unchanged. Only a new zero-PPO mechanics preregistration may be "
            "designed next; no run, training, behavior evaluation, runtime, or "
            "robot action is authorized.\n"
        ).encode("utf-8")
    )
    print(json.dumps({"status": payload["status"], "sha256": output_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
