#!/usr/bin/env python3
"""Run the frozen Winner-v12 decomposed-backend zero-PPO CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import jax.numpy as jnp
import numpy as np
import onnx
from onnx import TensorProto, helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v12_zero_ppo_decomposed_backend_preregistration.json"
sys.path.insert(0, str(ROOT / "patches"))
sys.path.insert(0, str(ROOT / "tools"))

import winner_v12_decomposed_backend_networks as networks  # noqa: E402
import check_winner_v11_zero_ppo_cpu_mechanics as v11  # noqa: E402


# Reuse the frozen physical fixtures with the v12 new-branch reference.
v11.networks = networks
v11.base.networks = networks


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def expose_response_delta(source: Path, destination: Path) -> None:
    """Create a checker-only graph output without changing deployable bytes."""

    model = onnx.load(source)
    if "v6_adapter_delta" in {value.name for value in model.graph.output}:
        raise ValueError("deployable graph unexpectedly exposes response delta")
    model.graph.output.extend(
        [
            helper.make_tensor_value_info(
                "v6_adapter_delta", TensorProto.FLOAT, [1, networks.ACTION_SIZE]
            )
        ]
    )
    model.graph.name = f"{model.graph.name}_checker_only_response_delta"
    onnx.checker.check_model(model)
    onnx.save(model, destination)


def check_response_branch(
    debug_path: Path,
    parameters: dict[str, jax.Array],
    *,
    seed: int,
    cases: int,
) -> dict[str, Any]:
    session = ort.InferenceSession(
        str(debug_path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.Generator(np.random.PCG64(seed))
    maximum_hidden_error = 0.0
    maximum_delta_error = 0.0
    maximum_delta_abs = 0.0
    all_finite = True
    for _ in range(cases):
        obs = rng.normal(0.0, 0.2, (1, networks.OBS_SIZE)).astype(np.float32)
        previous = rng.uniform(-1.0, 1.0, (1, networks.ACTION_SIZE)).astype(
            np.float32
        )
        hidden = rng.uniform(-1.0, 1.0, (1, networks.HIDDEN_SIZE)).astype(
            np.float32
        )
        context = rng.uniform(-1.0, 1.0, (1, networks.HIDDEN_SIZE)).astype(
            np.float32
        )
        expected_hidden, expected_delta = networks.response_branch_step(
            parameters,
            jnp.asarray(obs),
            jnp.asarray(previous),
            jnp.asarray(hidden),
            jnp.asarray(context),
        )
        actual_hidden, actual_delta = session.run(
            ["h_out", "v6_adapter_delta"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        maximum_hidden_error = max(
            maximum_hidden_error,
            v11.base.maximum_error(expected_hidden, actual_hidden),
        )
        maximum_delta_error = max(
            maximum_delta_error,
            v11.base.maximum_error(expected_delta, actual_delta),
        )
        maximum_delta_abs = max(maximum_delta_abs, float(np.max(np.abs(actual_delta))))
        all_finite &= bool(
            np.isfinite(actual_hidden).all() and np.isfinite(actual_delta).all()
        )
    return {
        "seed": seed,
        "cases": cases,
        "max_hidden_error": maximum_hidden_error,
        "max_response_delta_error": maximum_delta_error,
        "max_response_delta_abs": maximum_delta_abs,
        "all_finite": all_finite,
        "providers": session.get_providers(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists() or output.exists():
        raise FileExistsError("Winner-v12 formal output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    source_paths = {
        "half": args.policy_half.resolve(),
        "final": args.policy_final.resolve(),
    }
    policy_hashes = {name: sha256(path) for name, path in source_paths.items()}
    expected_policies = {
        name: row["sha256"] for name, row in prereg["protected_policies"].items()
    }
    if policy_hashes != expected_policies:
        raise ValueError("Winner-v12 protected Winner-v10 hashes changed")

    source_hashes = {}
    for name, row in prereg["sources"].items():
        path = ROOT / row["path"]
        source_hashes[name] = (
            sha256(path) if row["hash_mode"] == "raw sha256" else sha256_lf(path)
        )
    expected_sources = {
        name: row["sha256"] for name, row in prereg["sources"].items()
    }
    if source_hashes != expected_sources:
        raise ValueError("Winner-v12 frozen source hashes changed")

    protected_root = work_root / "protected"
    protected_root.mkdir()
    protected = {}
    for name, source in source_paths.items():
        destination = protected_root / f"winner_v10_{name}.onnx"
        shutil.copyfile(source, destination)
        protected[name] = destination

    boundary = v11.check_boundary_identity(protected)
    calibrator_parameters = networks.initialize_calibrator_parameters()
    response_parameters = networks.initialize_locomotion_adapter_parameters()
    calibrator_path = work_root / "winner_v12_calibrator_step_zero.onnx"
    networks.export_calibrator_onnx(calibrator_parameters, calibrator_path)
    calibrator_session = ort.InferenceSession(
        str(calibrator_path), providers=["CPUExecutionProvider"]
    )
    step_zero = v11.base.check_step_zero(calibrator_parameters, calibrator_session)
    auxiliary = v11.base.check_auxiliary_trainability(calibrator_parameters)
    calibration_chain, context, handoff_previous = v11.base.check_calibration_chain(
        calibrator_parameters, calibrator_session
    )
    fail_closed = v11.base.check_fail_closed(context)

    identities = []
    x0_chains = []
    physical_chains = []
    response_default = []
    deployable_paths = {}
    debug_paths = {}
    v11_reference_paths = {}
    for index, label in enumerate(("half", "final")):
        reference_path = work_root / f"winner_v11_reference_{label}.onnx"
        networks.base.export_locomotion_onnx(
            protected[label], response_parameters, reference_path
        )
        v11_reference_paths[label] = reference_path
        deployable_path = work_root / f"winner_v12_locomotion_{label}_step_zero.onnx"
        networks.export_locomotion_onnx(
            protected[label], response_parameters, deployable_path
        )
        deployable_paths[label] = deployable_path
        debug_path = work_root / f"winner_v12_locomotion_{label}_debug.onnx"
        expose_response_delta(deployable_path, debug_path)
        debug_paths[label] = debug_path
        identities.append(
            v11.check_default_off_identity(
                protected[label], deployable_path, 120140 + index * 10
            )
        )
        x0_chains.append(
            v11.check_x0_chain(
                protected[label],
                deployable_path,
                response_parameters,
                context,
                handoff_previous,
                120160 + index * 10,
            )
        )
        physical_chains.append(
            v11.check_physical_chain(
                protected[label],
                deployable_path,
                response_parameters,
                context,
                handoff_previous,
                120180 + index * 10,
            )
        )
        response_default.append(
            {
                "protected_label": label,
                **check_response_branch(
                    debug_path,
                    response_parameters,
                    seed=120200 + index * 10,
                    cases=66,
                ),
            }
        )

    sequence = v11.check_sequence_and_handoff(
        calibrator_session, context, handoff_previous, deployable_paths
    )
    stressed_calibrator, stressed_response = v11.base.stress_parameters(
        calibrator_parameters, response_parameters
    )
    stressed_calibrator_path = work_root / "winner_v12_calibrator_stress.onnx"
    networks.export_calibrator_onnx(stressed_calibrator, stressed_calibrator_path)
    response_stress = []
    full_stress = []
    for index, label in enumerate(("half", "final")):
        path = work_root / f"winner_v12_locomotion_{label}_stress.onnx"
        networks.export_locomotion_onnx(
            protected[label], stressed_response, path, adapter_enabled=True
        )
        debug_path = work_root / f"winner_v12_locomotion_{label}_stress_debug.onnx"
        expose_response_delta(path, debug_path)
        response_stress.append(
            {
                "protected_label": label,
                **check_response_branch(
                    debug_path,
                    stressed_response,
                    seed=120220 + index * 10,
                    cases=256,
                ),
            }
        )
        row = v11.check_strict_stress(stressed_calibrator_path, path, cases=256)
        row["protected_label"] = label
        full_stress.append(row)

    tolerance = float(prereg["test_population"]["new_branch_numeric_tolerance"])
    deployable_byte_identity = {
        label: networks.assert_deployable_export_unchanged(
            v11_reference_paths[label], deployable_paths[label]
        )
        for label in ("half", "final")
    }
    observed_population = {
        "step_zero_cases": step_zero["cases"],
        "calibration_ticks": calibration_chain["ticks"],
        "default_off_identity_cases_per_checkpoint": identities[0]["identity_cases"],
        "default_off_x0_ticks_per_checkpoint": x0_chains[0]["ticks"],
        "physical_chain_ticks_per_checkpoint": physical_chains[0]["ticks"],
        "default_response_cases_per_checkpoint": response_default[0]["cases"],
        "enabled_response_cases_per_checkpoint": response_stress[0]["cases"],
        "enabled_full_graph_cases_per_checkpoint": full_stress[0]["cases_per_graph"],
        "invalid_policy_handoff_cases": len(fail_closed["invalid_cases"]),
        "phase_period_ticks": physical_chains[0]["phase_period_ticks"],
        "action_history_lags": physical_chains[0]["action_history_lags"],
        "applied_target_source": physical_chains[0]["applied_target_source"],
        "new_branch_numeric_tolerance": tolerance,
        "optimizer_steps": 0,
        "formal_behavior_cells": 0,
    }
    both_rows_exact = bool(
        len(identities) == len(x0_chains) == len(physical_chains) == 2
        and all(row["identity_cases"] == 66 for row in identities)
        and all(row["ticks"] == 32 for row in x0_chains + physical_chains)
        and all(row["cases"] == 66 for row in response_default)
        and all(row["cases"] == 256 for row in response_stress)
        and all(row["cases_per_graph"] == 256 for row in full_stress)
    )
    graph_inputs = {
        value["name"]
        for value in v11.base.abi(deployable_paths["half"])["inputs"]
    }
    checks = {
        "frozen_source_hashes_exact": source_hashes == expected_sources,
        "protected_winner_v10_hashes_exact": policy_hashes == expected_policies,
        "protected_stored_and_inward_boundaries_exact": boundary["both_exact"],
        "deployable_exports_byte_exact_to_winner_v11": all(
            deployable_byte_identity.values()
        ),
        "calibrator_abi_exact": v11.base.abi(calibrator_path)
        == prereg["expected_abi"]["calibrator"],
        "deployable_locomotion_abis_exact": all(
            v11.base.abi(path) == prereg["expected_abi"]["locomotion"]
            for path in deployable_paths.values()
        ),
        "debug_output_absent_from_deployable_abi": all(
            "v6_adapter_delta"
            not in {row["name"] for row in v11.base.abi(path)["outputs"]}
            for path in deployable_paths.values()
        ),
        "jax_cpu_only": bool(jax.devices())
        and all(device.platform == "cpu" for device in jax.devices()),
        "onnxruntime_cpu_only": calibrator_session.get_providers()
        == ["CPUExecutionProvider"]
        and all(
            row["providers"] == ["CPUExecutionProvider"]
            for row in response_default + response_stress
        ),
        "calibrator_step_zero_and_chain_within_1e_7": max(
            step_zero["max_action_error"],
            step_zero["max_hidden_error"],
            calibration_chain["max_action_error"],
            calibration_chain["max_hidden_error"],
        )
        <= tolerance
        and step_zero["actions_exact_zero"],
        "calibrator_response_encoder_trainable": auxiliary[
            "response_encoder_receives_gradient"
        ]
        and auxiliary["all_gradients_finite"],
        "calibration_sequence_handoff_and_fail_closed_exact": sequence["all_exact"]
        and fail_closed["all_invalid_cases_rejected"],
        "protected_default_off_identity_bit_exact": all(
            row["protected_actions_bit_exact"]
            and row["protected_previous_action_state_bit_exact"]
            and row["context_branch_exact_zero_default_off"]
            for row in identities
        ),
        "x0_exact_zero_and_identity": all(
            row["exact_zero_and_identity"] and row["observation_contract_exact"]
            for row in x0_chains
        ),
        "default_response_branch_within_1e_7": all(
            row["max_hidden_error"] <= tolerance
            and row["max_response_delta_error"] <= tolerance
            and row["max_response_delta_abs"] == 0.0
            and row["all_finite"]
            for row in response_default
        ),
        "enabled_response_branch_within_1e_7": all(
            row["max_hidden_error"] <= tolerance
            and row["max_response_delta_error"] <= tolerance
            and row["max_response_delta_abs"] > 0.0
            and row["all_finite"]
            for row in response_stress
        ),
        "full_authoritative_onnx_bounds_hold": all(
            all(row["strict_stored_bounds"].values())
            and all(row["internal_roundoff_bounds"].values())
            and row["all_finite"]
            and row["state_equals_action_bit_exact"]
            for row in full_stress
        ),
        "physical_onnx_chains_exact_and_bounded": all(
            row["protected_and_expanded_bit_exact"]
            and row["strict_stored_bounds"]
            and row["internal_roundoff_bounds"]
            and row["observation_contract_exact"]
            and row["all_finite"]
            for row in physical_chains
        ),
        "recurrent_previous_action_precondition_held": all(
            row["recurrent_state_precondition_held"]
            for row in physical_chains + x0_chains
        ),
        "frozen_population_exact_for_both_checkpoints": observed_population
        == prereg["test_population"]
        and both_rows_exact,
        "no_configuration_or_debug_tensor_in_deployable_inputs": graph_inputs
        == {"obs", "previous_action", "h_in", "calibration_context"},
        "zero_optimizer_steps_and_behavior_cells": True,
    }
    if set(checks) != set(prereg["expected_result_checks"]):
        raise RuntimeError("Winner-v12 checker names differ from preregistration")
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    payload = {
        "schema_version": "winner_v12.zero_ppo_decomposed_backend_result.v1",
        "status": (
            "PASS_WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_MECHANICS"
            if passed
            else "HOLD_WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_MECHANICS"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_WINNER_V12_TRAINING_PREREGISTRATION_ONLY"
            if passed
            else "STOP_WINNER_V12_AND_REVIEW_DECOMPOSED_MECHANICS_FAILURE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "preregistration_sha256": sha256_lf(PREREGISTRATION),
        "source_hashes": source_hashes,
        "protected_policy_hashes": policy_hashes,
        "devices": [str(device) for device in jax.devices()],
        "versions": {
            "jax": jax.__version__,
            "numpy": np.__version__,
            "onnx": onnx.__version__,
            "onnxruntime": ort.__version__,
        },
        "boundary_identity": boundary,
        "step_zero": step_zero,
        "auxiliary_trainability": auxiliary,
        "calibration_chain": calibration_chain,
        "sequence_and_handoff": sequence,
        "fail_closed": fail_closed,
        "default_off_identities": identities,
        "default_off_x0_chains": x0_chains,
        "protected_physical_chains": physical_chains,
        "response_branch_default": response_default,
        "response_branch_enabled_stress": response_stress,
        "full_authoritative_onnx_stress": full_stress,
        "deployable_export_byte_identity": deployable_byte_identity,
        "legacy_full_protected_jax_onnx_record_only": [
            {
                "protected_label": label,
                "max_action_error": row["jax_onnx_max_action_error"],
                "max_hidden_error": row["jax_onnx_max_hidden_error"],
                "gating": False,
                "reason": "closed Winner-v11 quantity; protected ONNX is authoritative",
            }
            for label, row in zip(("half", "final"), physical_chains, strict=True)
        ],
        "observed_test_population": observed_population,
        "temporary_artifacts": {
            path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in sorted(work_root.glob("*.onnx"))
        },
        "execution_counts": {"optimizer_steps": 0, "formal_behavior_cells": 0},
        "authority": {
            "separate_training_preregistration_design": passed,
            "training_or_optimizer": False,
            "behavior_evaluation": False,
            "runtime_implementation": False,
            "robot_rdk_torque_motion_gate5_deployment": False,
            "robot_clearance": False,
        },
        "limitations": [
            "Winner-v11 remains closed and is not reclassified or rerun.",
            "Checker-only response-delta outputs are not deployable graph outputs.",
            "This run contains zero optimizer steps and zero behavior cells.",
        ],
    }
    output.write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    print(payload["status"])
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    for name in failed:
        print(f"FAILED={name}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
