#!/usr/bin/env python3
"""Freeze the distinct Winner-v12 decomposed-backend CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = (
    ANALYSIS / "winner_v12_zero_ppo_decomposed_backend_preregistration.json"
)
OUTPUT_MD = (
    ANALYSIS / "WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_PREREGISTRATION_20260720.md"
)
V11_PREREGISTRATION = (
    ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_preregistration.json"
)
V11_RESULT = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_result.json"
V11_ATTRIBUTION = ANALYSIS / "winner_v11_numeric_hold_attribution.json"
RUNTIME_RECEIPT = ANALYSIS / "winner_v11_runtime_rereview_receipt.json"
V12_NETWORK = ROOT / "patches/winner_v12_decomposed_backend_networks.py"
V12_CHECKER = ROOT / "tools/check_winner_v12_zero_ppo_decomposed_backend.py"
V12_IMPORTER = ROOT / "tools/import_winner_v12_zero_ppo_decomposed_backend.py"
V11_NETWORK = ROOT / "patches/winner_v11_dynamic_calibration_networks.py"
V11_CHECKER = ROOT / "tools/check_winner_v11_zero_ppo_cpu_mechanics.py"
V6_NETWORK = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
V6_CHECKER = ROOT / "tools/check_winner_v6_zero_ppo_cpu_contract.py"
HANDOFF = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"

EXPECTED_ATTRIBUTION_SHA256 = (
    "e1ab186678e19ac36a029db9bba25126ea2b080f5c728fc4bc275ff03e017683"
)
EXPECTED_V11_RESULT_SHA256 = (
    "f946b79b16a6769c87ebf31e4134d1c80c83bc6071bbeb5d61ecade387895a0a"
)


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def sha256_raw(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    v11_prereg = json.loads(V11_PREREGISTRATION.read_text(encoding="utf-8"))
    v11_result = json.loads(V11_RESULT.read_text(encoding="utf-8"))
    attribution = json.loads(V11_ATTRIBUTION.read_text(encoding="utf-8"))
    if sha256_lf(V11_RESULT) != EXPECTED_V11_RESULT_SHA256:
        raise ValueError("the closed Winner-v11 result changed")
    if v11_result["status"] != "HOLD_WINNER_V11_ZERO_PPO_CPU_MECHANICS":
        raise ValueError("Winner-v11 must remain closed as a HOLD")
    if sha256_lf(V11_ATTRIBUTION) != EXPECTED_ATTRIBUTION_SHA256:
        raise ValueError("Winner-v11 numeric attribution changed")
    if attribution["decision"] != (
        "PREREGISTER_DISTINCT_WINNER_V12_DECOMPOSED_BACKEND_CONTRACT_ONLY"
    ):
        raise ValueError("numeric attribution does not authorize Winner-v12")
    if attribution["distinct_winner_v12_hypothesis"]["tolerance_change"]:
        raise ValueError("Winner-v12 may not relax the frozen numeric tolerance")

    text_sources = {
        "builder": Path(__file__),
        "checker": V12_CHECKER,
        "importer": V12_IMPORTER,
        "network_source": V12_NETWORK,
        "winner_v11_network_source": V11_NETWORK,
        "winner_v11_checker": V11_CHECKER,
        "base_v6_network_source": V6_NETWORK,
        "base_v6_checker": V6_CHECKER,
        "winner_v11_preregistration": V11_PREREGISTRATION,
        "closed_winner_v11_result": V11_RESULT,
        "winner_v11_numeric_attribution": V11_ATTRIBUTION,
        "runtime_rereview_receipt": RUNTIME_RECEIPT,
        "winner_v2_observer_source": HANDOFF / "observer/winner_v2_contract.py",
        "winner_v2_p30_fit": HANDOFF / "observer/p30_actuator_fit.json",
        "winner_v2_policy_contract": HANDOFF / "policy_contract.json",
        "winner_v2_observation_map": HANDOFF / "observation_map.json",
        "winner_v2_golden_evidence": HANDOFF / "golden_evidence.json",
        "winner_v2_handoff_readme": HANDOFF / "README.md",
        "winner_v2_handoff_manifest": HANDOFF / "manifest.json",
    }
    sources = {
        label: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_lf(path),
            "hash_mode": "sha256 after CRLF-to-LF normalization",
        }
        for label, path in text_sources.items()
    }
    reference = HANDOFF / "reference/ground_up_projected_reference_feature_table.npz"
    sources["winner_v2_reference_table"] = {
        "path": str(reference.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256_raw(reference),
        "hash_mode": "raw sha256",
    }

    expected_checks = [
        "frozen_source_hashes_exact",
        "protected_winner_v10_hashes_exact",
        "protected_stored_and_inward_boundaries_exact",
        "deployable_exports_byte_exact_to_winner_v11",
        "calibrator_abi_exact",
        "deployable_locomotion_abis_exact",
        "debug_output_absent_from_deployable_abi",
        "jax_cpu_only",
        "onnxruntime_cpu_only",
        "calibrator_step_zero_and_chain_within_1e_7",
        "calibrator_response_encoder_trainable",
        "calibration_sequence_handoff_and_fail_closed_exact",
        "protected_default_off_identity_bit_exact",
        "x0_exact_zero_and_identity",
        "default_response_branch_within_1e_7",
        "enabled_response_branch_within_1e_7",
        "full_authoritative_onnx_bounds_hold",
        "physical_onnx_chains_exact_and_bounded",
        "recurrent_previous_action_precondition_held",
        "frozen_population_exact_for_both_checkpoints",
        "no_configuration_or_debug_tensor_in_deployable_inputs",
        "zero_optimizer_steps_and_behavior_cells",
    ]
    policies = v11_prereg["protected_policies"]
    result = {
        "schema_version": (
            "winner_v12.zero_ppo_decomposed_backend_preregistration.v1"
        ),
        "status": "PREREGISTERED_NOT_RUN",
        "decision": "AUTHORIZE_ONE_EXACT_WINNER_V12_DECOMPOSED_BACKEND_CPU_RUN",
        "contract_id": "winner-v12-decomposed-backend-r64",
        "hypothesis": (
            "The exact Winner-v11 deployable ONNX wrapper can remain byte-identical "
            "while backend agreement is decomposed: only the new calibrator and "
            "response-branch tensors are gated at the unchanged 1e-7 tolerance, "
            "and the complete authoritative ONNX action is gated by the unchanged "
            "stored and inward-rounded physical action boundaries."
        ),
        "closed_winner_v11": {
            "remains_closed": True,
            "status": v11_result["status"],
            "result_sha256_lf": sha256_lf(V11_RESULT),
            "rerun_or_reclassification": False,
            "old_full_protected_jax_onnx_quantity": "record only; never gating",
        },
        "distinct_change": {
            "new_gated_quantity": (
                "checker-only response hidden state and response delta"
            ),
            "new_branch_tolerance": 1.0e-7,
            "tolerance_changed": False,
            "protected_policy_changed": False,
            "runtime_or_deployable_abi_changed": False,
            "checker_only_debug_output": "v6_adapter_delta",
            "debug_output_is_deployable": False,
            "complete_action_authority": "ONNX Runtime CPU output",
        },
        "sources": sources,
        "protected_policies": policies,
        "expected_abi": v11_prereg["expected_abi"],
        "expected_result_checks": expected_checks,
        "test_population": {
            "step_zero_cases": 66,
            "calibration_ticks": 250,
            "default_off_identity_cases_per_checkpoint": 66,
            "default_off_x0_ticks_per_checkpoint": 32,
            "physical_chain_ticks_per_checkpoint": 32,
            "default_response_cases_per_checkpoint": 66,
            "enabled_response_cases_per_checkpoint": 256,
            "enabled_full_graph_cases_per_checkpoint": 256,
            "invalid_policy_handoff_cases": 9,
            "phase_period_ticks": 27,
            "action_history_lags": [2, 3, 4],
            "applied_target_source": "exact frozen P30 forward observer",
            "new_branch_numeric_tolerance": 1.0e-7,
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
        },
        "pass_rule": [
            "all frozen source and exact Winner-v10 policy hashes match",
            "both deployable exports are byte-identical to the Winner-v11 exporter outputs",
            "the checker-only response-delta tensor is absent from each deployable ABI",
            "calibrator step-zero and 250-tick chain agree across JAX and ONNX within the unchanged 1e-7 tolerance",
            "default and enabled new response-branch hidden/delta tensors agree across JAX and ONNX within the unchanged 1e-7 tolerance",
            "default-off actions and recurrent state remain bit-exact to both protected ONNX checkpoints and exact zero at x=0",
            "all complete authoritative ONNX outputs obey the unchanged stored and inward-rounded physical boundaries",
            "all 32-tick physical chains preserve phase, t-2/t-3/t-4 action history, P30 applied target, projected reference, and recurrent preconditions",
            "the exact population runs CPU-only with zero optimizer steps and zero behavior cells",
        ],
        "explicit_non_gate": {
            "quantity": "full protected-policy JAX transcription versus ONNX",
            "reason": (
                "Winner-v11 already closed this over-coupled quantity; deployment "
                "uses the exact protected ONNX graph and byte-exact ONNX wrapper"
            ),
            "still_recorded": True,
        },
        "no_retry_or_tuning": (
            "A failed formal run is recorded as a Winner-v12 hold. Do not change "
            "seeds, populations, tolerance, graph ABI, protected hashes, bounds, "
            "or pass rules and rerun."
        ),
        "pass_authorizes_only": (
            "write and review a separate Winner-v12 calibrator-training "
            "preregistration; no optimizer step or behavior evaluation"
        ),
        "authority": {
            "one_exact_cpu_only_run": True,
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "training_or_ppo": False,
            "colab_hosted_gpu_or_igpu": False,
            "runtime_implementation": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "gate5_deployment_or_robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_bytes(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    result_sha = sha256_lf(OUTPUT_JSON)
    OUTPUT_MD.write_bytes(
        (
            "# Winner-v12 Decomposed-Backend CPU Preregistration\n\n"
            f"Status: `{result['status']}`\n\n"
            f"JSON SHA-256: `{result_sha}`\n\n"
            "Winner-v11 remains closed. This distinct zero-PPO run preserves its "
            "deployable graph bytes and unchanged 1e-7 threshold, but applies that "
            "threshold only to newly introduced calibrator/response tensors. The "
            "full deployable action is judged from authoritative ONNX Runtime output "
            "against the unchanged physical bounds.\n\n"
            "A pass authorizes only a separate training preregistration. It does not "
            "authorize training, runtime implementation, hardware, motion, Gate 5, "
            "deployment, or robot clearance.\n"
        ).encode("utf-8")
    )
    print(json.dumps({"status": result["status"], "sha256": result_sha}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
