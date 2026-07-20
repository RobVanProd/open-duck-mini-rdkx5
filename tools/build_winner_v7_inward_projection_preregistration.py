#!/usr/bin/env python3
"""Freeze the winner-v7 inward-rounded protected-base graph contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v7_inward_projection_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V7_INWARD_PROJECTION_PREREGISTRATION_20260720.md"
RUNNER = ROOT / "tools/run_winner_v7_inward_projection_contract.py"
IMPORTER = ROOT / "tools/import_winner_v7_inward_projection_contract.py"
ATTRIBUTION = ANALYSIS / "winner_v6b_numeric_hold_attribution.json"
PROTECTED = {
    "half": ROOT / (
        "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/"
        "T2_EQUAL_512000.onnx"
    ),
    "final": ROOT / (
        "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/"
        "T2_EQUAL_1024000.onnx"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tensor(name: str, shape: list[int]) -> dict[str, object]:
    return {"name": name, "dtype": "float32", "shape": shape}


def main() -> int:
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if attribution["decision"] != "PREREGISTER_DISTINCT_V7_INWARD_PROJECTION_TRANSFORM_ONLY":
        raise ValueError("winner-v7 transform is not authorized by the numeric audit")
    if not attribution["winner_v6_dynamic_calibration_closed"]:
        raise ValueError("winner-v6 must remain closed")
    margin = float(np.float32(4.0) * np.finfo(np.float32).eps)
    maximum_perturbation = float(np.float32(8.0) * np.finfo(np.float32).eps)
    protected = {
        label: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(path),
        }
        for label, path in PROTECTED.items()
    }
    input_hashes = {
        "runner": sha256(RUNNER),
        "importer": sha256(IMPORTER),
        "numeric_attribution": sha256(ATTRIBUTION),
        "protected_half": protected["half"]["sha256"],
        "protected_final": protected["final"]["sha256"],
    }
    expected_abi = {
        "inputs": [tensor("obs", [1, 115]), tensor("previous_action", [1, 14])],
        "outputs": [
            tensor("continuous_actions", [1, 14]),
            tensor("previous_action_out", [1, 14]),
        ],
    }
    result = {
        "schema_version": "winner_v7.inward_projection_transform_preregistration.v1",
        "status": "PREREGISTERED_NOT_RUN",
        "decision": "AUTHORIZE_ONE_EXACT_CPU_ONLY_GRAPH_TRANSFORM_CONTRACT",
        "causal_hypothesis": (
            "A final projection placed after the protected actual-centered guard and "
            "inset by a fixed analytic float32 margin will make the stored winner-v2 "
            "delta contract representation-safe without changing tolerance."
        ),
        "distinct_from_closed_v6": {
            "winner_v6_dynamic_calibration_closed": True,
            "v6_or_v6b_retry": False,
            "protected_output_changed": True,
            "calibrator_or_context_graph_present": False,
            "requires_full_behavior_revalidation_before_any_calibrator": True,
        },
        "input_hashes": input_hashes,
        "protected_checkpoints": protected,
        "expected_abi": expected_abi,
        "transform": {
            "location": "after actual-centered guard and zero-command deadband",
            "source_delta_initializer": "max_action_delta",
            "safe_delta_equation": "float32(max_action_delta - 4*float32_epsilon)",
            "inward_margin_normalized_action": margin,
            "inward_margin_target_rad": margin * 0.25,
            "inward_margin_rate_rad_s": margin * 0.25 / 0.02,
            "maximum_allowed_action_perturbation": maximum_perturbation,
            "maximum_perturbation_derivation": "8*float32_epsilon",
            "maximum_perturbation_population": (
                "physically chained x=0 and moving cases only; arbitrary independent "
                "stress tensors carry no source-output identity requirement"
            ),
            "tolerance_change": False,
            "all_source_initializers_preserved": True,
            "all_source_nodes_preserved_except_final_output_tensor_rename": True,
            "appended_nodes": ["Clip", "Sub", "Add", "Min", "Max", "Identity"],
            "appended_initializers": [
                "v7_action_maximum",
                "v7_action_minimum",
                "v7_inward_margin",
                "v7_safe_max_action_delta",
            ],
        },
        "test_population": {
            "arbitrary_stress_cases_per_checkpoint": 4096,
            "arbitrary_stress_seeds": [60770, 60771],
            "x0_chain_ticks_per_checkpoint": 256,
            "x0_chain_seeds": [60780, 60781],
            "moving_chain_ticks_per_checkpoint": 32,
            "moving_chain_seeds": [60742, 60752],
            "moving_command_x": 0.077,
        },
        "pass_rule": [
            "all frozen input hashes and both output ABIs match",
            "source initializers and nodes are exact apart from reviewed output renames and append",
            "all 8192 arbitrary stress cases obey absolute and stored source-delta bounds with zero tolerance",
            "the transformation changes at least one arbitrary stress output in each checkpoint",
            "both 256-tick x=0 chains emit exact-zero action and state",
            "both 32-tick physically consistent moving chains obey bounds with zero tolerance",
            "maximum source-to-transformed action perturbation on the physically chained x=0 and moving populations is at most eight float32 epsilons; arbitrary independent stress tensors have no protected-identity claim",
            "no behavior evaluator, simulator outcome gate, calibrator, or optimizer runs",
        ],
        "all_or_nothing": True,
        "no_retry_or_tuning": (
            "A failed graph contract closes this exact inward-margin route. Do not "
            "change the margin, perturbation cap, seeds, population, checkpoint, or rule."
        ),
        "pass_authorizes_only": (
            "write and review a separate complete behavior-revalidation preregistration"
        ),
        "authority": {
            "one_exact_local_cpu_graph_contract": True,
            "behavior_evaluation": False,
            "dynamic_calibrator_or_training": False,
            "colab_hosted_gpu_or_igpu": False,
            "runtime_v2_implementation": False,
            "rdkx5_robot_torque_motion_gate5_deployment": False,
            "robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result_sha = sha256(OUTPUT_JSON)
    OUTPUT_MD.write_text(
        "# Winner-v7 Inward-Projection Preregistration\n\n"
        f"Status: `{result['status']}`\n\n"
        f"JSON SHA-256: `{result_sha}`\n\n"
        "Winner-v6/v6b remains closed. This distinct route changes the protected base "
        "itself by appending a final projection inset by exactly four float32 epsilons. "
        "The first gate is graph mechanics only: 8,192 arbitrary stress cases, exact x=0, "
        "physically chained motion tensors, and an eight-epsilon perturbation cap.\n\n"
        "A pass authorizes only a separate complete behavior-revalidation preregistration. "
        "No behavior run, calibrator, training, Colab, GPU, runtime implementation, robot "
        "access, torque, motion, Gate 5, deployment, or clearance is authorized.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "sha256": result_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
