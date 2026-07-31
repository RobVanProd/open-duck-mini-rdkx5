#!/usr/bin/env python3
"""Freeze the Winner-v11 zero-PPO CPU mechanics contract before execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V11_ZERO_PPO_CPU_MECHANICS_PREREGISTRATION_20260720.md"
INTERFACE = ANALYSIS / "winner_v11_dynamic_calibration_interface_preregistration.json"
RUNTIME_RECEIPT = ANALYSIS / "winner_v11_runtime_rereview_receipt.json"
NETWORK_SOURCE = ROOT / "patches/winner_v11_dynamic_calibration_networks.py"
BASE_NETWORK_SOURCE = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
CHECKER = ROOT / "tools/check_winner_v11_zero_ppo_cpu_mechanics.py"
BASE_CHECKER = ROOT / "tools/check_winner_v6_zero_ppo_cpu_contract.py"
IMPORTER = ROOT / "tools/import_winner_v11_zero_ppo_cpu_mechanics.py"
CLOSED_V6B = ANALYSIS / "winner_v6b_zero_ppo_cpu_contract_result.json"
V6B_ATTRIBUTION = ANALYSIS / "winner_v6b_numeric_hold_attribution.json"
V10_REPRESENTATION = ANALYSIS / "winner_v10_inward_torque_contract_result.json"
V10_NOMINAL = ANALYSIS / "winner_v10_nominal_behavior_result.json"
V10_R2_CONDITION7 = ANALYSIS / "winner_v10_r2_condition7_result.json"
HANDOFF_ROOT = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"
OBSERVER_SOURCE = HANDOFF_ROOT / "observer/winner_v2_contract.py"
P30_FIT = HANDOFF_ROOT / "observer/p30_actuator_fit.json"
REFERENCE_TABLE = HANDOFF_ROOT / "reference/ground_up_projected_reference_feature_table.npz"
POLICY_CONTRACT = HANDOFF_ROOT / "policy_contract.json"
OBSERVATION_MAP = HANDOFF_ROOT / "observation_map.json"

EXPECTED_INTERFACE_SHA256 = (
    "2500c731a3413b08568e6e88b57300d2c8c86b61f9fe7418f3efa21ab639c8a2"
)
EXPECTED_RUNTIME_RESULT_SHA256 = (
    "6c4f05830d2f1b661bd27297a40e05da5256c701427d929cf1a480d731bfcf57"
)


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def sha256_raw(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tensor(name: str, shape: list[int]) -> dict[str, object]:
    return {"name": name, "dtype": "float32", "shape": shape}


def main() -> int:
    interface = json.loads(INTERFACE.read_text(encoding="utf-8"))
    receipt = json.loads(RUNTIME_RECEIPT.read_text(encoding="utf-8"))
    v10 = json.loads(V10_REPRESENTATION.read_text(encoding="utf-8"))
    closed_v6b = json.loads(CLOSED_V6B.read_text(encoding="utf-8"))
    if sha256_lf(INTERFACE) != EXPECTED_INTERFACE_SHA256:
        raise ValueError("Winner-v11 interface changed after runtime rereview")
    if receipt["artifact_sha256"] != EXPECTED_RUNTIME_RESULT_SHA256:
        raise ValueError("runtime rereview receipt identifies the wrong artifact")
    if (
        receipt["decision"]
        != "AUTHORIZE_POLICY_WINNER_V11_ZERO_PPO_CPU_MECHANICS_CONTRACT_ONLY"
    ):
        raise ValueError("runtime did not authorize the Winner-v11 mechanics contract")
    if closed_v6b["status"] != "HOLD_WINNER_V6B_ZERO_PPO_CPU_SOFTWARE_CONTRACT":
        raise ValueError("the closed Winner-v6b result must remain held")
    if v10["status"] != "PASS_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT":
        raise ValueError("Winner-v10 protected representation is not passing")

    expected_abi = {
        "calibrator": interface["requested_interface"]["calibrator"],
        "locomotion": interface["requested_interface"]["locomotion"],
    }
    policy_hashes = interface["policy_hashes"]
    if policy_hashes != {
        "half": "cf001269908d86e47eaa145ffda1d87e946a314ecf51056dc086c4cf10164ab6",
        "final": "d52b63241340d9d56671b95c58bb0fc72af0998fd47d4684719f6cd44f244a10",
    }:
        raise ValueError("Winner-v10 protected hashes changed")

    sources = {
        label: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_lf(path),
            "hash_mode": "sha256 after CRLF-to-LF normalization",
        }
        for label, path in {
            "builder": Path(__file__),
            "checker": CHECKER,
            "importer": IMPORTER,
            "network_source": NETWORK_SOURCE,
            "base_v6_network_source": BASE_NETWORK_SOURCE,
            "base_v6_checker": BASE_CHECKER,
            "interface_preregistration": INTERFACE,
            "runtime_rereview_receipt": RUNTIME_RECEIPT,
            "closed_v6b_result": CLOSED_V6B,
            "v6b_numeric_attribution": V6B_ATTRIBUTION,
            "winner_v10_representation": V10_REPRESENTATION,
            "winner_v10_nominal": V10_NOMINAL,
            "winner_v10_r2_condition7": V10_R2_CONDITION7,
            "winner_v2_observer_source": OBSERVER_SOURCE,
            "winner_v2_p30_fit": P30_FIT,
            "winner_v2_policy_contract": POLICY_CONTRACT,
            "winner_v2_observation_map": OBSERVATION_MAP,
        }.items()
    }
    sources["winner_v2_reference_table"] = {
        "path": str(REFERENCE_TABLE.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256_raw(REFERENCE_TABLE),
        "hash_mode": "raw sha256",
    }
    result = {
        "schema_version": "winner_v11.zero_ppo_cpu_mechanics_preregistration.v1",
        "status": "PREREGISTERED_NOT_RUN",
        "decision": "AUTHORIZE_ONE_EXACT_WINNER_V11_ZERO_PPO_CPU_MECHANICS_RUN",
        "contract_id": "winner-v11-zero-ppo-mechanics-r64",
        "hypothesis": (
            "The reviewed automatic-calibration ABI can be initialized on the exact "
            "Winner-v10 protected graphs with no default-off action/state change, while "
            "the response state evolves and both future graph paths enforce the exact "
            "stored and inward-rounded measured action boundary."
        ),
        "not_a_v6_or_v6b_retry": {
            "both_closed_results_preserved": True,
            "closed_v6b_sha256": sha256_lf(CLOSED_V6B),
            "distinct_contract_name": "winner-v11-zero-ppo-mechanics-r64",
            "distinct_protected_base": "Winner-v10 inward-torque representation",
            "winner_v10_policy_hashes": policy_hashes,
            "winner_v10_stored_bound_repair_required": True,
        },
        "runtime_review": {
            "receipt_path": sources["runtime_rereview_receipt"]["path"],
            "receipt_sha256": sources["runtime_rereview_receipt"]["sha256"],
            "review_commit": receipt["review_commit"],
            "result_sha256": receipt["artifact_sha256"],
            "decision": receipt["decision"],
        },
        "sources": sources,
        "protected_policies": {
            label: {
                "sha256": policy_hashes[label],
                "role": f"exact Winner-v10 protected {label} checkpoint",
                "committed_binary": False,
            }
            for label in ("half", "final")
        },
        "expected_abi": expected_abi,
        "expected_result_checks": [
            "frozen_lf_source_hashes_exact",
            "protected_winner_v10_hashes_exact",
            "protected_stored_and_inward_boundaries_exact",
            "new_graphs_use_inward_boundary_exact",
            "jax_cpu_only",
            "onnxruntime_cpu_only",
            "calibrator_abi_exact",
            "locomotion_abis_exact",
            "calibrator_action_head_exact_zero",
            "calibrator_step_zero_actions_exact_zero",
            "calibrator_hidden_finite_bounded_and_evolves",
            "calibrator_response_encoder_trainable",
            "calibrator_250_tick_chain_exact",
            "sequence_and_handoff_exact",
            "calibration_context_immutable_finite_bounded",
            "failed_calibration_never_armable",
            "locomotion_context_heads_exact_zero",
            "default_off_arbitrary_input_identity_bit_exact",
            "default_off_x0_exact_zero_and_identity",
            "jax_onnx_chains_within_tolerance",
            "enabled_graphs_strict_stored_bounds",
            "protected_physical_chains_strict_and_exact",
            "physical_chain_jax_onnx_within_tolerance",
            "recurrent_previous_action_precondition_held",
            "frozen_test_population_exact",
            "no_true_configuration_graph_input",
            "auxiliary_targets_deployable_observation_only",
            "both_protected_checkpoints_checked",
            "zero_optimizer_steps_and_behavior_cells",
        ],
        "exact_sequence": {
            "frequency_hz": 50,
            "calibration_ticks": 250,
            "calibrator_initial_previous_action": "exact float32 zeros[1,14]",
            "calibrator_initial_hidden": "exact float32 zeros[1,64]",
            "calibration_command": "exact float32 zeros[7]",
            "calibration_phase": [1.0, 0.0],
            "calibration_phase_advances": False,
            "context_source": "exact final successful calibrator h_out",
            "context_shape": [1, 64],
            "context_dtype": "float32",
            "context_bounds_inclusive": [-1.0, 1.0],
            "context_runtime_scaling": "none",
            "context_session_local_immutable_nonpersistent": True,
            "previous_action_handoff": "final confirmed previous_action_out",
            "p30_applied_target_handoff": "final confirmed obs[83:97]",
            "locomotion_initial_hidden": "exact float32 zeros[1,64]",
            "locomotion_phase_reset": [1.0, 0.0],
            "runtime_remains_paused_after_handoff": True,
            "paused_hold_target": "final confirmed safe calibration target",
        },
        "test_population": {
            "step_zero_cases": 66,
            "calibration_ticks": 250,
            "default_off_identity_cases_per_checkpoint": 66,
            "default_off_x0_cases_per_checkpoint": 32,
            "locomotion_jax_onnx_ticks_per_checkpoint": 32,
            "physical_chain_ticks_per_checkpoint": 32,
            "phase_period_ticks": 27,
            "action_history_lags": [2, 3, 4],
            "applied_target_source": "exact frozen P30 forward observer",
            "enabled_stress_cases_per_graph": 256,
            "invalid_handoff_cases": 9,
            "invalid_handoff_scope": "policy-side calibration context validation only",
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "numeric_tolerance": 1.0e-7,
        },
        "action_boundary": {
            "stored_delta_initializer": "max_action_delta",
            "inward_delta_initializer": "v7_safe_max_action_delta",
            "new_graphs_use_inward_delta": True,
            "all_reported_actions_judged_against_stored_delta": True,
            "strict_maximum_excess": 0.0,
            "maximum_internal_roundoff_excess": (
                "at most two float32 epsilons while stored-bound excess remains zero"
            ),
            "host_projection_or_limiter": False,
            "inward_torque_is_plant_xml_semantics": True,
        },
        "recurrent_state_precondition": {
            "previous_action_shape": [1, 14],
            "previous_action_dtype": "float32",
            "previous_action_finite": True,
            "previous_action_bounds_inclusive": [-1.0, 1.0],
            "source": (
                "exact zero at reset, then the immediately preceding validated "
                "previous_action_out from the same graph"
            ),
            "out_of_range_runtime_input": "reject before inference; not graph-clamped",
        },
        "pass_rule": [
            "all LF-stable source hashes, protected policy hashes, ABIs, and CPU-only assertions match",
            "all step-zero calibrator actions/action-state are exact zero while hidden state evolves and receives a finite nonzero observation-only auxiliary gradient",
            "the exact 250-tick calibrator and both 32-tick locomotion JAX/ONNX chains agree within 1e-7",
            "the calibration sequence and policy-side calibration-to-locomotion state/context/applied-target handoff are exact",
            "all nine policy-side invalid context handoffs fail before a context is returned; runtime failure modes remain explicitly unexecuted",
            "both protected Winner-v10 default-off graphs preserve action and previous_action_out bit-for-bit on arbitrary finite inputs",
            "both protected default-off x0 populations remain exact-zero and bit-identical",
            "both deliberately enabled stress graphs and calibrator obey the stored Winner-v10 action boundary with zero measured excess",
            "both physically chained protected populations remain bit-identical and obey the stored boundary with zero measured excess",
            "every recurrent previous_action input begins at exact zero or is the preceding finite graph state within [-1,1]",
            "no true configuration label enters either graph or the auxiliary target",
        ],
        "all_or_nothing": True,
        "mechanics_scope_boundary": {
            "policy_graph_handoff_executed": True,
            "runtime_process_persistence_executed": False,
            "runtime_paused_hold_executed": False,
            "runtime_arming_or_torque_off_executed": False,
            "physical_support_mode_defined_or_executed": False,
            "runtime_fail_closed_rules_executed": False,
        },
        "runtime_requirements_preserved_but_not_executed": interface[
            "required_fail_closed_rules"
        ],
        "no_retry_or_tuning": (
            "A failed formal run is recorded as a Winner-v11 hold. Do not change "
            "seeds, populations, thresholds, weights, ABI, protected hashes, or pass "
            "rules and rerun."
        ),
        "pass_authorizes_only": (
            "write and review a separate calibrator-training preregistration; no "
            "optimizer step or support-mode behavior"
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
            "# Winner-v11 Zero-PPO CPU Mechanics Preregistration\n\n"
            f"Status: `{result['status']}`\n\n"
            f"JSON SHA-256: `{result_sha}`\n\n"
            "This freezes one CPU-only mechanics run against both exact Winner-v10 "
            "graphs. It executes 250 calibration ticks, zero optimizer steps, and zero "
            "formal behavior cells. Default-off outputs must remain bit-exact; enabled "
            "outputs must obey the stored/inward-rounded graph boundary with zero "
            "measured excess.\n\n"
            "A pass authorizes only a separately reviewed training preregistration. "
            "It does not authorize training, runtime implementation, hardware, motion, "
            "Gate 5, deployment, or robot clearance.\n"
        ).encode("utf-8")
    )
    print(json.dumps({"status": result["status"], "sha256": result_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
