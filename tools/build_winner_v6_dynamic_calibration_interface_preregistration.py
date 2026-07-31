#!/usr/bin/env python3
"""Freeze the winner-v6 dynamic-calibration interface for runtime review."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v6_dynamic_calibration_interface_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V6_DYNAMIC_CALIBRATION_INTERFACE_PREREGISTRATION_20260720.md"


def source_bytes(relative_path: str) -> bytes:
    path = ROOT / relative_path
    if path.is_file():
        return path.read_bytes()
    completed = subprocess.run(
        ["git", "show", f"HEAD:{relative_path}"], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if completed.returncode:
        raise FileNotFoundError(relative_path)
    return completed.stdout


def source_json(relative_path: str) -> dict[str, Any]:
    return json.loads(source_bytes(relative_path))


def source_record(relative_path: str) -> dict[str, str]:
    return {
        "path": relative_path,
        "sha256": hashlib.sha256(source_bytes(relative_path)).hexdigest(),
    }


def tensor(name: str, shape: list[int]) -> dict[str, Any]:
    return {"name": name, "dtype": "float32", "shape": shape}


def main() -> int:
    v3_result_path = "outputs/analysis/winner_v3_variable_configuration_result_corrected.json"
    v3_attribution_path = "outputs/analysis/winner_v3_failure_attribution.json"
    current_gate_path = "outputs/analysis/winner_v3_current_gate_application_contract.json"
    v4_interface_path = "outputs/analysis/winner_v4_response_interface_preregistration.json"
    v4_result_path = "outputs/analysis/winner_v4_response_identifiability_result.json"
    v5_result_path = "outputs/analysis/winner_v5_automatic_support_recovery_result.json"
    v3_result = source_json(v3_result_path)
    v4_result = source_json(v4_result_path)
    v5_result = source_json(v5_result_path)
    if v3_result["decision"] != "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT":
        raise ValueError("winner-v3 replacement is not closed")
    if v4_result["status"] != "HOLD_RESPONSE73_PRETRAINING_FALSIFICATION_FAILED":
        raise ValueError("response73 is not closed")
    if v5_result["decision"] != "CLOSE_ONE_SHOT_IMU_THRESHOLD_FIXED_RECOVERY":
        raise ValueError("winner-v5 fixed recovery is not closed")

    result = {
        "schema_version": "winner_v6.dynamic_calibration_interface_preregistration.v1",
        "status": "PREREGISTERED_PENDING_RUNTIME_REVIEW",
        "decision": "REQUEST_RUNTIME_V2_DYNAMIC_CALIBRATION_SCHEMA_REVIEW_NO_IMPLEMENTATION",
        "causal_hypothesis": (
            "The old recurrent actor had no calibration-only objective and its exact x=0 "
            "deadband prevented corrective startup action. The response73 procedure fell "
            "before profiling, while winner-v5 proved that a one-shot decision and one fixed "
            "pose are non-universal. A dedicated response policy that changes its bounded "
            "action every tick and exports its learned sensor-history state may stabilize "
            "the support phase and expose configuration response without manual measurement."
        ),
        "closed_routes_not_reopened": [
            "blind walking-time R64 recurrent adapter",
            "open-loop response73 joint excitation from unsupported home",
            "one-shot IMU threshold plus fixed recovery target",
            "manual mass, center-of-mass, dimension, or component inventory",
            "true configuration parameters as actor inputs",
        ],
        "authority": {
            "runtime_review_only": True,
            "runtime_implementation": False,
            "training_ppo_or_colab": False,
            "gpu_or_igpu": False,
            "rdkx5_robot_torque_or_motion": False,
            "gate5_or_deployment": False,
            "robot_clearance": False,
        },
        "versioning": {
            "runtime_v1_101x14_contract_unchanged": True,
            "required_path": "default-off versioned runtime-v2 only",
            "observation_contract": "winner-v2-115d",
            "reason": (
                "The existing runtime review proves winner-v2 115-D semantics are not "
                "interchangeable with frozen v1 101-D semantics. No shared-slice shortcut "
                "or silent 101/115 conversion is permitted."
            ),
        },
        "graphs": {
            "calibrator": {
                "id": "winner-v6-dynamic-support-calibrator",
                "inputs": [
                    tensor("obs", [1, 115]),
                    tensor("previous_action", [1, 14]),
                    tensor("h_in", [1, 64]),
                ],
                "outputs": [
                    tensor("calibration_actions", [1, 14]),
                    tensor("previous_action_out", [1, 14]),
                    tensor("h_out", [1, 64]),
                ],
                "action_semantics": "unchanged normalized 14-action logical order",
                "initial_state": "h_in and previous_action exact float32 zeros",
                "state_update": (
                    "learned recurrent response encoder consumes only deployable observation, "
                    "previous action, and previous hidden state; h_out is tanh-bounded"
                ),
                "action_head": (
                    "new calibration-only residual head; graph-owned conservative measured "
                    "per-joint hard-vector projection; no x=0 deadband"
                ),
                "training_only_auxiliary_head": (
                    "predict next deployable joint-state, IMU, contact, and applied-target "
                    "observation fields from h_out and the realized bounded action; not exported"
                ),
            },
            "locomotion": {
                "id": "winner-v6-response-conditioned-locomotion",
                "inputs": [
                    tensor("obs", [1, 115]),
                    tensor("previous_action", [1, 14]),
                    tensor("h_in", [1, 64]),
                    tensor("calibration_context", [1, 64]),
                ],
                "outputs": [
                    tensor("continuous_actions", [1, 14]),
                    tensor("previous_action_out", [1, 14]),
                    tensor("h_out", [1, 64]),
                ],
                "initialization": (
                    "protected G1/T2 locomotion actor plus an exact-zero context branch; "
                    "default-off action and recurrent outputs must be bit-exact"
                ),
                "context_semantics": (
                    "the exact final calibrator h_out, immutable for the locomotion episode; "
                    "no runtime scaling, interpretation, substitution, or default"
                ),
                "locomotion_state_reset": "h_in exact zero at handoff",
            },
        },
        "calibration_sequence": {
            "duration_ticks": 250,
            "frequency_hz": 50,
            "command_vector": "all seven command fields exact zero",
            "phase": "held at winner-v2 phase index zero [1,0] throughout calibration",
            "projected_reference": "x=0 reference action in obs[101:115] throughout calibration",
            "support_mode": (
                "flat rigid floor, both feet initially loaded, no torso/limb/head support or "
                "external applied force; passive fall catch mechanically clear"
            ),
            "per_tick_order": [
                "fresh servo, IMU, and contact samples",
                "compose exact versioned 115-D observation",
                "infer calibrator with chained previous_action and h",
                "apply graph-bounded target through the selected measured actuator transition",
                "commit state only after confirmed target send",
            ],
            "handoff": [
                "require every calibration tick and support/safety predicate to pass",
                "freeze final h_out as calibration_context",
                "carry final calibration action as locomotion previous_action",
                "retain the final applied-target observer in obs[83:97]",
                "reset locomotion h_in to zero and locomotion phase to [1,0]",
            ],
            "start_paused_semantics": (
                "calibration is a separate explicitly authorized startup mode; after a valid "
                "handoff the runtime remains paused and holds the final safe target until the "
                "controller explicitly unpauses"
            ),
        },
        "context_contract": {
            "dimension": 64,
            "dtype": "float32",
            "field_order": [f"learned_response_latent[{index}]" for index in range(64)],
            "bounds": [-1.0, 1.0],
            "runtime_scaling": "none",
            "immutable_after_successful_handoff": True,
            "hash_binding": (
                "calibrator graph, locomotion graph, raw per-tick calibration evidence, "
                "duck_config, runtime build, and supported configuration envelope"
            ),
            "invalid_if": [
                "missing, stale, nonfinite, out of [-1,1], wrong shape/order",
                "calibration timing or support-mode mismatch",
                "any failed bus transaction, stale sensor, lost contact, watchdog event, or safety gate",
                "configuration changed after calibration",
            ],
            "manual_or_true_configuration_fields": [],
        },
        "required_runtime_review": [
            "Can a default-off runtime-v2 run the calibrator without weakening v1 101x14?",
            "Can it preserve winner-v2 obs[83:97], projected-reference, phase, and action-state semantics for every calibration tick?",
            "Can it freeze and pass h_out[64] byte-for-byte as locomotion calibration_context[64] with no Python scaling?",
            "Can it carry final previous_action and applied-target observer state across the graph handoff exactly once?",
            "Can start_paused remain true after calibration while holding the last safe target?",
            "Can every stale/failed/nonfinite/support-mode path prevent arming and torque off safely?",
            "Does any proposed behavior conflict with the frozen v1 path or existing hardware-gate authority?",
        ],
        "after_runtime_review_only": {
            "cpu_software_contract": [
                "calibrator and locomotion ABI names/shapes/dtypes exact",
                "calibrator initial action exact zero while hidden response state remains trainable",
                "locomotion default-off protected action/state bit-exact for fixed and pseudorandom inputs",
                "auxiliary predictor receives no true configuration label",
                "all exported actions obey the conservative per-joint vector",
                "JAX and ONNX chained calibration/handoff/locomotion agree within 1e-7",
            ],
            "training_order": [
                "train only the calibrator/response encoder on support and self-supervised next-response prediction",
                "freeze it and require a complete unseen support gate under both actuator fits",
                "only after support passes, train one response-conditioned locomotion continuation",
                "evaluate both persistent checkpoints on the unchanged full behavior/current matrix",
            ],
            "support_pass": {
                "all cells": True,
                "duration_ticks": 250,
                "minimum_base_z_m": 0.10,
                "maximum_abs_tilt_rad": 0.35,
                "two_foot_contact_failure_ticks": 0,
                "maximum_final_window_gyro_rad_s": 0.05,
                "current_rule": "prospective documented stall/2A-for-2s protection contract",
            },
        },
        "stop_rules": [
            "no training before runtime review and zero-PPO CPU software contract pass",
            "close if the calibrator cannot pass every unseen support cell under both fits",
            "do not tune locomotion using a failed or closest calibration checkpoint",
            "do not append true mass, COM, inertia, component identity, scale, or caliper data",
            "do not weaken the completed winner-v3, response73, or winner-v5 results",
            "no runtime implementation, robot, RDK, torque, motion, Gate 5, or deployment from this artifact",
        ],
        "sources": {
            "winner_v3_result": source_record(v3_result_path),
            "winner_v3_failure_attribution": source_record(v3_attribution_path),
            "current_gate_application": source_record(current_gate_path),
            "winner_v4_interface": source_record(v4_interface_path),
            "winner_v4_result": source_record(v4_result_path),
            "winner_v5_result": source_record(v5_result_path),
        },
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result_sha = hashlib.sha256(OUTPUT_JSON.read_bytes()).hexdigest()
    OUTPUT_MD.write_text(
        "# Winner-v6 Dynamic Calibration Interface Preregistration\n\n"
        f"status: `{result['status']}`\n\n"
        f"JSON SHA-256: `{result_sha}`\n\n"
        "Winner-v5 closed the one-shot threshold/fixed-pose controller. This proposal "
        "uses a separate 250-tick recurrent support calibrator whose action changes "
        "every tick and whose final 64-D learned response state conditions locomotion. "
        "It uses only deployable sensor/action history—no mass, COM, dimensions, component "
        "inventory, scales, or calipers.\n\n"
        "The frozen runtime-v1 101x14 path remains unchanged. This is a default-off, "
        "versioned runtime-v2 schema request only. No training or implementation is "
        "authorized until runtime reviews the exact graph, state, phase, handoff, pause, "
        "and fail-closed semantics.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "sha256": result_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
