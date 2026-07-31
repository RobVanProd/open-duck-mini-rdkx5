#!/usr/bin/env python3
"""Attribute the recorded winner-v6 zero-PPO contract hold without rerunning it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v6_zero_ppo_cpu_contract_result.json"
PREREGISTRATION = ANALYSIS / "winner_v6_zero_ppo_cpu_contract_preregistration.json"
CHECKER = ROOT / "tools/check_winner_v6_zero_ppo_cpu_contract.py"
PRIOR_TRANSFORM = ROOT / "tools/build_ground_up_dual_fit_conservative_envelope_repair.py"
OUTPUT_JSON = ANALYSIS / "winner_v6_zero_ppo_contract_hold_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V6_ZERO_PPO_CONTRACT_HOLD_ATTRIBUTION_20260720.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def model_facts(path: Path) -> dict[str, object]:
    model = onnx.load(path)
    initializers = {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }
    producers = {
        output: index
        for index, node in enumerate(model.graph.node)
        for output in node.output
    }
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
        "velocity_projection_node": producers["velocity_bounded_actions"],
        "actual_centered_guard_node": producers["deadband_source_actions"],
        "final_action_node": producers["continuous_actions"],
        "guard_is_downstream_of_velocity_projection": (
            producers["velocity_bounded_actions"]
            < producers["deadband_source_actions"]
            < producers["continuous_actions"]
        ),
        "max_action_delta": initializers["max_action_delta"].reshape(-1).tolist(),
    }


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    checker_text = CHECKER.read_text(encoding="utf-8")
    prior_text = PRIOR_TRANSFORM.read_text(encoding="utf-8")
    protected = [
        model_facts(ROOT / preregistration["protected_checkpoints"][label]["path"])
        for label in ("half", "final")
    ]
    expansions = result["protected_expansions"]
    evidence = {
        "formal_status_remains_hold": (
            result["status"] == "HOLD_WINNER_V6_ZERO_PPO_CPU_SOFTWARE_CONTRACT"
        ),
        "only_failed_check_was_combined_bound_check": (
            result["failed_checks"] == ["graph_owned_action_bounds_hold"]
        ),
        "nonzero_adapter_stress_passed_both_graphs": (
            result["stress_bounds"]["calibrator_bounds_hold"]
            and result["stress_bounds"]["locomotion_bounds_hold"]
        ),
        "default_off_protected_identity_passed_both_checkpoints": all(
            row["protected_actions_bit_exact"]
            and row["protected_previous_action_state_bit_exact"]
            and row["context_branch_exact_zero_default_off"]
            for row in expansions
        ),
        "only_default_off_chain_bound_subchecks_failed": all(
            not row["action_bounds_hold"] for row in expansions
        ),
        "jax_onnx_chain_itself_passed": result["checks"][
            "jax_onnx_full_handoff_chain_within_tolerance"
        ],
        "protected_guard_is_downstream_of_velocity_projection": all(
            row["guard_is_downstream_of_velocity_projection"] for row in protected
        ),
        "formal_fixture_randomizes_joint_state_independently": (
            "rng.normal(0.0, 0.04, (count, 1, networks.OBS_SIZE))" in checker_text
            and "observations[tick, 0, 13:27]" not in checker_text
        ),
        "prior_guard_contract_required_physical_joint_state_consistency": (
            "obs[:, 13:27] = previous * np.float32(0.25)" in prior_text
        ),
        "combined_pass_rule_conflated_disabled_and_enabled_paths": (
            'and all(row["action_bounds_hold"] for row in expansions)' in checker_text
            and 'stress_bounds["locomotion_bounds_hold"]' in checker_text
        ),
    }
    failed_evidence = sorted(name for name, value in evidence.items() if not value)
    attributed = not failed_evidence
    payload = {
        "schema_version": "winner_v6.zero_ppo_contract_hold_attribution.v1",
        "status": (
            "PASS_HOLD_ATTRIBUTED_TO_CONTRACT_FIXTURE_SEMANTICS"
            if attributed
            else "HOLD_ZERO_PPO_FAILURE_NOT_ATTRIBUTED"
        ),
        "decision": (
            "REQUEST_RUNTIME_BOUND_SEMANTICS_REVIEW_NO_RETRY"
            if attributed
            else "STOP_WINNER_V6_PATH"
        ),
        "completed_result_reclassified": False,
        "formal_contract_retry_authorized": False,
        "evidence": evidence,
        "failed_evidence": failed_evidence,
        "protected_graphs": protected,
        "causal_attribution": (
            "The exact-zero adapter was byte-for-byte inactive and its deliberately "
            "enabled stress graph obeyed the projection. The failing subcheck instead "
            "applied a previous-action slew assertion to the protected actor after its "
            "downstream actual-centered guard, using joint positions randomized "
            "independently of action state. That guard is intentionally downstream and "
            "can replace the upstream rate-bounded action when state and target diverge."
        ),
        "semantic_question_for_runtime": (
            "Should the reviewed requirement distinguish (A) arbitrary-input bit-exact "
            "default-off delegation to the already accepted protected graph, (B) "
            "arbitrary-input graph-owned bounds when the new adapter is enabled, and "
            "(C) the protected full action contract on physically valid chained "
            "observations, rather than requiring the upstream previous-action delta "
            "after an actual-centered guard on impossible independent state pairs?"
        ),
        "proposed_if_runtime_accepts": [
            "close the exact failed v3 contract permanently",
            "freeze a separately named v6b zero-PPO contract before execution",
            "do not change checkpoints, network weights, seeds, ABI, 1e-7 tolerance, or fail-closed cases",
            "keep arbitrary-input bit-exact default-off identity",
            "keep arbitrary-input enabled-adapter bound stress",
            "use physically chained observation/action state only for the protected full-action sequence assertion",
        ],
        "inputs": {
            "formal_result": {
                "path": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(RESULT),
            },
            "preregistration": {
                "path": str(PREREGISTRATION.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(PREREGISTRATION),
            },
            "checker": {
                "path": str(CHECKER.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(CHECKER),
            },
            "prior_transform": {
                "path": str(PRIOR_TRANSFORM.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(PRIOR_TRANSFORM),
            },
        },
        "authority": {
            "runtime_semantics_review_request": attributed,
            "new_or_revised_contract_run": False,
            "training_ppo_colab_gpu": False,
            "runtime_implementation": False,
            "rdkx5_robot_torque_motion_gate5_deployment": False,
            "robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    output_sha = sha256(OUTPUT_JSON)
    OUTPUT_MD.write_text(
        "# Winner-v6 Zero-PPO Contract Hold Attribution\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"JSON SHA-256: `{output_sha}`\n\n"
        "The completed formal result remains a hold and is not retried. The new "
        "adapter's enabled bound-stress graph passed, and its disabled graph preserved "
        "both protected checkpoints bit-exactly. The failed combined check applied an "
        "upstream previous-action delta rule after the protected graph's downstream "
        "actual-centered guard on independently randomized joint/action state.\n\n"
        "The next action is a runtime semantics review only. Training, a replacement "
        "contract run, Colab, GPU, runtime implementation, robot access, torque, motion, "
        "Gate 5, deployment, and robot clearance remain blocked.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": output_sha}, sort_keys=True))
    return 0 if attributed else 1


if __name__ == "__main__":
    raise SystemExit(main())
