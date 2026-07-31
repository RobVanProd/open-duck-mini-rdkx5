#!/usr/bin/env python3
"""Freeze the Winner-v11 dynamic-calibration runtime review request."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v11_dynamic_calibration_interface_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V11_DYNAMIC_CALIBRATION_INTERFACE_PREREGISTRATION_20260720.md"

SOURCES = {
    "builder": Path(__file__).resolve(),
    "closed_v6b_result": ANALYSIS / "winner_v6b_zero_ppo_cpu_contract_result.json",
    "v6b_numeric_attribution": ANALYSIS / "winner_v6b_numeric_hold_attribution.json",
    "winner_v10_representation": ANALYSIS / "winner_v10_inward_torque_contract_result.json",
    "winner_v10_nominal": ANALYSIS / "winner_v10_nominal_behavior_result.json",
    "winner_v10_r2_condition6": ANALYSIS / "winner_v10_r2_condition6_result.json",
    "winner_v10_r2_condition7_hold": ANALYSIS / "winner_v10_r2_condition7_result.json",
    "v6_network_source": ROOT / "patches/winner_v6_dynamic_calibration_networks.py",
    "runtime_hash_review_receipt": ANALYSIS / "winner_v11_runtime_hash_review_receipt.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def tensor(name: str, shape: list[int]) -> dict[str, Any]:
    return {"name": name, "dtype": "float32", "shape": shape}


def load(name: str) -> dict[str, Any]:
    return json.loads(SOURCES[name].read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=OUTPUT_MD)
    args = parser.parse_args()
    output_json = args.output_json.resolve()
    output_md = args.output_md.resolve()
    if output_json.exists() or output_md.exists():
        raise FileExistsError("Winner-v11 interface request is already frozen")

    half = args.policy_half.resolve()
    final = args.policy_final.resolve()
    if not half.is_file() or not final.is_file():
        raise FileNotFoundError("both exact Winner-v10 ONNX checkpoints are required")

    v6b = load("closed_v6b_result")
    attribution = load("v6b_numeric_attribution")
    representation = load("winner_v10_representation")
    nominal = load("winner_v10_nominal")
    condition6 = load("winner_v10_r2_condition6")
    condition7 = load("winner_v10_r2_condition7_hold")
    runtime_receipt = load("runtime_hash_review_receipt")
    if v6b["status"] != "HOLD_WINNER_V6B_ZERO_PPO_CPU_SOFTWARE_CONTRACT":
        raise ValueError("Winner-v6b must remain held")
    if not attribution["winner_v6_or_v6b_retry_authorized"] is False:
        raise ValueError("Winner-v6/v6b closure changed")
    if representation["status"] != "PASS_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT":
        raise ValueError("Winner-v10 representation is not proven")
    if nominal["status"] != "PASS_WINNER_V10_NOMINAL_BEHAVIOR":
        raise ValueError("Winner-v10 nominal behavior is not proven")
    if condition6["status"] != "PASS_WINNER_V10_R2_CONDITION6_ARMATURE_HI":
        raise ValueError("Winner-v10 R2 condition 6 is not proven")
    if (
        condition7["status"]
        != "HOLD_WINNER_V10_R2_CONDITION7_TORSO_COM_X_NEG"
        or condition7["decision"] != "STOP_WINNER_V10_R2_AT_FIRST_FAILED_CONDITION"
    ):
        raise ValueError("Winner-v10 R2 terminal hold is not the reviewed result")
    if (
        runtime_receipt["status"]
        != "SCHEMA_FEASIBLE_HOLD_WINNER_V11_ZERO_PPO_HASH_BINDING"
        or runtime_receipt["decision"]
        != "REQUEST_POLICY_LF_STABLE_HASH_CORRECTION_BEFORE_ZERO_PPO"
        or not runtime_receipt["authority"][
            "metadata_only_lf_stable_policy_correction"
        ]
    ):
        raise ValueError("runtime did not authorize this metadata-only correction")

    policy_hashes = {"half": sha256(half), "final": sha256(final)}
    expected_policy_hashes = {
        "half": "cf001269908d86e47eaa145ffda1d87e946a314ecf51056dc086c4cf10164ab6",
        "final": "d52b63241340d9d56671b95c58bb0fc72af0998fd47d4684719f6cd44f244a10",
    }
    if policy_hashes != expected_policy_hashes:
        raise ValueError("Winner-v10 policy hashes do not match the frozen gate")

    calibrator_abi = {
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
    }
    locomotion_abi = {
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
    }
    sources = {
        name: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": lf_sha256(path),
            "hash_mode": "sha256 after CRLF-to-LF normalization",
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v11.dynamic_calibration_interface_preregistration.v2",
        "status": "PREREGISTERED_PENDING_RUNTIME_REVIEW",
        "decision": "REQUEST_READ_ONLY_WINNER_V11_RUNTIME_SCHEMA_REREVIEW_AFTER_LF_CORRECTION",
        "causal_hypothesis": (
            "Winner-v10's separately contracted inward projection, stored graph-owned "
            "bounds, inward torque representation, and complete nominal revalidation "
            "remove the protected float32-boundary defect that closed Winner-v6/v6b. "
            "The unchanged reviewed dynamic-calibration ABI can therefore be tested "
            "mechanically against this distinct protected base before any training."
        ),
        "not_a_v6_or_v6b_retry": {
            "closed_result_preserved": True,
            "closed_result_sha256": sources["closed_v6b_result"]["sha256"],
            "new_protected_base": "Winner-v10 inward-torque representation",
            "new_protected_policy_hashes": policy_hashes,
            "behavior_revalidation": {
                "nominal_pass": True,
                "r2_conditions_1_through_6_pass": True,
                "r2_condition_7_terminal_hold_preserved": True,
            },
            "r2_resumption": False,
        },
        "pre_execution_hash_correction": {
            "correction_scope": "metadata and LF-stable receipt hashes only",
            "graph_abi_gate_or_authority_changed": False,
            "zero_ppo_run_started": False,
            "superseded_policy_commit": runtime_receipt["reviewed_policy_commit"],
            "superseded_claimed_crlf_sha256": runtime_receipt[
                "reviewed_policy_artifact_claimed_sha256"
            ],
            "superseded_committed_lf_sha256": runtime_receipt[
                "reviewed_policy_artifact_committed_sha256"
            ],
            "runtime_hold_commit": runtime_receipt["review_commit"],
            "runtime_hold_artifact_sha256": runtime_receipt["artifact_sha256"],
            "runtime_hold_status": runtime_receipt["status"],
        },
        "requested_interface": {
            "contract_id": "winner-v11-dynamic-calibration-r64",
            "observation_contract": "winner-v2-115d",
            "calibrator": calibrator_abi,
            "locomotion": locomotion_abi,
            "calibration_ticks": 250,
            "context_handoff": (
                "final successful calibrator h_out becomes immutable session-local "
                "locomotion calibration_context without scaling or persistence"
            ),
            "previous_action_and_applied_target_handoff": "carry final confirmed values",
            "locomotion_hidden_and_phase_start": "h_in=zeros[1,64]; phase=[1,0] exactly once",
            "runtime_v1_101x14_changed": False,
            "runtime_v2_115d_semantics_changed": False,
            "host_action_projection_or_limiter_added": False,
            "normalization_location": "inside future ONNX graph",
            "sequence_inherited_from_reviewed_winner_v6": {
                "frequency_hz": 50,
                "calibrator_initial_previous_action": "exact float32 zeros[1,14]",
                "calibrator_initial_hidden_state": "exact float32 zeros[1,64]",
                "calibration_command": "exact float32 zeros[7]",
                "calibration_phase": [1.0, 0.0],
                "calibration_phase_advances": False,
                "context_order": "learned_response_latent[0:64]",
                "context_bounds_inclusive": [-1.0, 1.0],
                "runtime_remains_paused_after_handoff": True,
                "paused_hold_target": "final confirmed safe calibration target",
            },
            "x0_semantics": {
                "default_off": "byte-exact Winner-v10 zero-action deadband",
                "future_enabled": "graph-authoritative and may be nonzero",
                "host_forces_zero": False,
                "future_enabled_requires_separate_behavior_gate": True,
                "evidence": (
                    "all four Winner-v10 condition-7 x0 traces are byte-identical, "
                    "exact-zero action/state, and terminate after 47 samples"
                ),
            },
        },
        "zero_ppo_contract_requested_after_review_only": {
            "optimizer_steps": 0,
            "default_off_action_and_previous_state_bit_exact_to_winner_v10": True,
            "arbitrary_finite_default_off_population": True,
            "enabled_graph_owns_absolute_and_delta_action_guards": True,
            "winner_v10_inward_torque_is_plant_xml_not_runtime_abi": True,
            "calibrator_and_locomotion_jax_onnx_chain": True,
            "invalid_handoffs_fail_closed": True,
            "cpu_only": True,
            "formal_behavior_cells": 0,
        },
        "automatic_configuration": {
            "manual_measurements_required": False,
            "mass_com_inertia_dimensions_or_component_identity_inputs": False,
            "context_recomputed_each_process_start": True,
            "context_persisted_between_boots": False,
            "future_support_mode_must_be_separately_preregistered": True,
            "future_calibration_action_must_be_graph_bounded": True,
        },
        "required_fail_closed_rules": [
            "wrong policy, source, contract, reference, fit, config, or runtime hash",
            "missing, stale, mixed-epoch, nonfinite, wrong-shape, or out-of-bound input",
            "failed or ambiguous send, lost contact, bus, sensor, watchdog, or timing failure",
            "missing, mutable, persisted, scaled, or invalid calibration context",
            "any invalid handoff prevents locomotion arming",
            "every future abort path torque-offs before exit",
        ],
        "runtime_review_questions": [
            "Does the unchanged two-graph ABI remain implementable with the exact Winner-v10 base hashes?",
            "Can default-off delegation preserve Winner-v10 action and previous_action_out byte-for-byte without a host limiter?",
            "Can runtime carry the final confirmed previous action and applied-target observer state across the calibration-to-locomotion handoff?",
            "Can every context remain session-local, immutable, nonpersistent, and mandatory before locomotion arming?",
            "Does Winner-v10's plant/XML inward torque representation require no runtime semantic change?",
            "Can runtime keep default-off x=0 byte-exact while leaving future enabled x=0 output graph-authoritative?",
            "May policy freeze one zero-PPO CPU mechanics contract before any support-mode or training proposal?",
        ],
        "policy_hashes": policy_hashes,
        "sources": sources,
        "stop_rules": [
            "do not run the zero-PPO contract before runtime review",
            "do not retry or reclassify Winner-v6/v6b",
            "do not continue R2 after the frozen condition-7 failure",
            "do not define a physical support-mode excitation or train from this request",
            "do not select a deployment checkpoint or set robot_clearance true",
        ],
        "authority": {
            "runtime_review_only": True,
            "zero_ppo_execution": False,
            "training_or_optimizer": False,
            "hosted_compute_gpu_or_igpu": False,
            "runtime_implementation": False,
            "rdkx5_robot_serial_gpio_i2c": False,
            "torque_motion_gate5_deployment": False,
            "robot_clearance": False,
        },
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    result_sha = sha256(output_json)
    markdown = (
        "# Winner-v11 Dynamic-Calibration Interface Preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"JSON SHA-256: `{result_sha}`\n\n"
        "Winner-v6/v6b remains closed. This request attaches the already-reviewed "
        "automatic per-session calibration ABI to the distinct Winner-v10 protected "
        "base, whose inward projection, stored bounds, torque representation, and "
        "nominal behavior were separately revalidated. It asks runtime only whether "
        "the unchanged schema can support a new zero-PPO mechanics contract.\n\n"
        "No scales, calipers, mass, COM, inertia, dimensions, component identity, or "
        "manual per-build input is used. No zero-PPO run, training, hosted compute, "
        "runtime implementation, X5/robot access, torque, motion, Gate 5, deployment, "
        "checkpoint selection, or robot clearance is authorized.\n"
    )
    output_md.write_bytes(markdown.encode("utf-8"))
    print(json.dumps({"status": payload["status"], "sha256": result_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
