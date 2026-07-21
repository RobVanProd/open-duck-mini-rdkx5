#!/usr/bin/env python3
"""Verify the corrected same-input Winner-v13 Stage-1 ONNX checker."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(PATCHES))
sys.path.insert(0, str(TOOLS))

CONTRACT = ANALYSIS / "winner_v13_stage1_checker_v2_cpu_contract.json"
INVALID_ATTRIBUTION = (
    ANALYSIS / "winner_v13_normalized_response_stage1_invalid_attribution.json"
)
CASES = 256
SEED = 131314


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_source_manifest(contract: Mapping[str, Any]) -> None:
    sources = contract.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v13 checker-v2 source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v13 checker-v2 source changed: {name}")
    if canonical_sha256(sources) != contract.get("source_manifest_sha256"):
        raise ValueError("Winner-v13 checker-v2 manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--zero-cell-checker-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.zero_cell_checker_contract_authorized:
        raise PermissionError(
            "checker-v2 contract requires --offline-cpu-only "
            "--zero-cell-checker-contract-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite checker-v2 CPU evidence")

    import jax
    import jax.numpy as jnp
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import winner_v12_decomposed_backend_networks as networks
    import winner_v13_normalized_calibrator_training as v13

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v13 checker-v2 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("status") != "FROZEN_WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT"
        or contract.get("decision") != "AUTHORIZE_ONE_ZERO_CELL_CHECKER_PROOF_ONLY"
        or contract.get("execution_now")
        != {
            "optimizer_updates": 0,
            "simulation_cells": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v13 checker-v2 contract changed")
    validate_source_manifest(contract)
    invalid = json.loads(INVALID_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        invalid.get("status") != "INVALID_WINNER_V13_STAGE1_DECISION_CONTRACT"
        or invalid.get("decision") != "DO_NOT_ADVANCE_REVALIDATE_CORRECTED_CHECKER"
        or invalid.get("required_correction", {}).get("learning_rate") != 0.0001
    ):
        raise ValueError("Winner-v13 invalid attribution changed")

    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v13_stage1_checker_v2_zero_cell.onnx"
    parameters = v13.initialize_training_parameters(seed=60720)
    networks.export_calibrator_onnx(v13.deployable_parameters(parameters), graph)
    session = ort.InferenceSession(str(graph), providers=["CPUExecutionProvider"])
    rng = np.random.Generator(np.random.PCG64(SEED))
    observations = rng.normal(0.0, 0.5, (CASES, 115)).astype(np.float32)
    previous_actions = rng.uniform(-0.95, 0.95, (CASES, 14)).astype(np.float32)
    hidden_inputs = rng.normal(0.0, 0.4, (CASES, 64)).astype(np.float32)
    maximum_errors = np.zeros(3, dtype=np.float64)
    graph_nonzero_actions = 0
    state_equals_action = True
    all_outputs_finite = True
    for observation, previous, hidden in zip(
        observations, previous_actions, hidden_inputs
    ):
        reference = networks.calibrator_step(
            v13.deployable_parameters(parameters),
            jnp.asarray(observation[None, :]),
            jnp.asarray(previous[None, :]),
            jnp.asarray(hidden[None, :]),
        )
        observed = session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {
                "obs": observation[None, :],
                "previous_action": previous[None, :],
                "h_in": hidden[None, :],
            },
        )
        for index, (left, right) in enumerate(zip(observed, reference)):
            right_np = np.asarray(right, dtype=np.float32)
            all_outputs_finite &= bool(
                np.all(np.isfinite(left)) and np.all(np.isfinite(right_np))
            )
            maximum_errors[index] = max(
                maximum_errors[index], float(np.max(np.abs(left - right_np)))
            )
        graph_nonzero_actions += int(np.any(observed[0] != 0.0))
        state_equals_action &= np.array_equal(observed[0], observed[1])

    zero_previous_action_exact = True
    for observation, hidden in zip(observations[:32], hidden_inputs[:32]):
        observed = session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {
                "obs": observation[None, :],
                "previous_action": np.zeros((1, 14), dtype=np.float32),
                "h_in": hidden[None, :],
            },
        )
        zero_previous_action_exact &= np.array_equal(
            observed[0], np.zeros((1, 14), dtype=np.float32)
        ) and np.array_equal(observed[1], observed[0])
    standard_graph = smoke.onnx_contract(graph, parameters, observations)
    action_parameters_zero = all(
        np.array_equal(
            np.asarray(parameters[key]),
            np.zeros_like(np.asarray(parameters[key])),
        )
        for key in v13.DEPLOYABLE_ACTION_KEYS
    )
    checks = {
        "exact_256_same_input_cases": len(observations) == CASES,
        "action_head_parameters_exact_zero": action_parameters_zero,
        "nonzero_previous_action_can_produce_nonzero_bounded_action": (
            graph_nonzero_actions > 0
        ),
        "zero_previous_action_produces_exact_zero_action": bool(
            zero_previous_action_exact
        ),
        "same_input_action_error_at_most_1e_7": maximum_errors[0] <= 1.0e-7,
        "same_input_previous_action_out_error_at_most_1e_7": (
            maximum_errors[1] <= 1.0e-7
        ),
        "same_input_hidden_error_at_most_1e_7": maximum_errors[2] <= 1.0e-7,
        "graph_previous_action_out_equals_action_bit_exact": bool(
            state_equals_action
        ),
        "all_outputs_finite": bool(all_outputs_finite),
        "standard_graph_contract_passes": all(
            standard_graph[name]
            for name in (
                "abi_exact",
                "training_only_tensors_absent",
                "jax_onnx_at_most_1e_7",
                "previous_action_out_equals_action_bit_exact",
            )
        ),
        "declared_learning_rate_matches_executed_constant": (
            v13.STAGE1_LEARNING_RATE == 0.0001
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if not all(math.isfinite(float(value)) for value in maximum_errors):
        raise FloatingPointError("checker-v2 produced a nonfinite comparison")
    result = {
        "schema_version": "winner_v13.stage1_checker_v2_cpu_result.v1",
        "status": (
            "PASS_WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_FRESH_STAGE1_V2_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_RERUN_STAGE1"
        ),
        "checks": checks,
        "failed_checks": failed,
        "proof": {
            "same_input_cases": CASES,
            "root_seed": SEED,
            "maximum_action_error": float(maximum_errors[0]),
            "maximum_previous_action_out_error": float(maximum_errors[1]),
            "maximum_hidden_error": float(maximum_errors[2]),
            "nonzero_graph_action_cases": graph_nonzero_actions,
            "standard_graph_contract": standard_graph,
            "executed_stage1_learning_rate": v13.STAGE1_LEARNING_RATE,
        },
        "execution": {
            "optimizer_updates": 0,
            "simulation_cells": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "contract_lf_sha256": lf_sha256(CONTRACT),
            "invalid_attribution_lf_sha256": lf_sha256(INVALID_ATTRIBUTION),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
            "v13_primitives_lf_sha256": lf_sha256(
                PATCHES / "winner_v13_normalized_calibrator_training.py"
            ),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a fresh corrected Stage-1 v2 preregistration",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
