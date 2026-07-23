#!/usr/bin/env python3
"""Run the frozen Winner-v96 zero-update response-conditioned CPU contract."""

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
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import build_winner_v96_response_conditioned_mechanics_preregistration as builder  # noqa: E402
import run_winner_v92_universal_target_response_observer as v92  # noqa: E402
import winner_v96_response_conditioned_networks as networks  # noqa: E402


PREREGISTRATION = (
    ANALYSIS / "winner_v96_response_conditioned_mechanics_preregistration.json"
)
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
POLICY = builder.POLICY
GOLDENS = (builder.GOLDEN_ZERO, builder.GOLDEN_MOVING)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def maximum_error(left: Any, right: Any) -> float:
    return float(np.max(np.abs(np.asarray(left) - np.asarray(right))))


def trace_sha256(value: Any) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def describe_abi(model_path: Path) -> dict[str, list[dict[str, Any]]]:
    import onnx

    model = onnx.load(model_path)

    def describe(values: Any) -> list[dict[str, Any]]:
        rows = []
        for value in values:
            tensor = value.type.tensor_type
            rows.append(
                {
                    "name": value.name,
                    "dtype": (
                        "float32"
                        if tensor.elem_type == onnx.TensorProto.FLOAT
                        else onnx.TensorProto.DataType.Name(tensor.elem_type).lower()
                    ),
                    "shape": [dimension.dim_value for dimension in tensor.shape.dim],
                }
            )
        return rows

    return {"inputs": describe(model.graph.input), "outputs": describe(model.graph.output)}


def validate_preregistration(value: Mapping[str, Any]) -> None:
    source = value.get("source_evidence", {})
    initialization = value.get("fixed_initialization", {})
    population = value.get("test_population", {})
    if (
        value.get("schema_version")
        != "winner_v96.response_conditioned_mechanics_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS"
        or source.get("v92_result_sha256") != builder.V92_RESULT_SHA256
        or source.get("v95_result_sha256") != builder.V95_RESULT_SHA256
        or source.get("universal_target_candidate") != 536
        or source.get("universal_target_action") != list(builder.UNIVERSAL_TARGET)
        or initialization.get("adapter_seed") != 60721
        or initialization.get("adapter_max_normalized") != 0.25
        or initialization.get("flat_transport_feature_enabled") is not False
        or initialization.get("stable_v95_readout_exported") is not False
        or population.get("signed_calibration_cells") != 4
        or population.get("golden_ticks") != 1200
        or population.get("stress_cases") != 256
        or value.get("execution_now")
        != {
            "simulator_cells": 0,
            "golden_ticks": 0,
            "stress_cases": 0,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v96 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v96 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v96 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v96 source manifest changed")
    binary = value.get("binary_sources", {})
    for name in ("protected_policy", "golden_x0", "golden_x008"):
        item = binary[name]
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v96 binary source changed: {name}")


def session(path: Path, output_names: list[str] | None = None) -> Any:
    import onnxruntime as ort

    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    value = ort.InferenceSession(
        str(path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    if output_names is not None and [row.name for row in value.get_outputs()] != output_names:
        raise ValueError(f"unexpected ONNX outputs for {path.name}")
    return value


def stress_parameters(parameters: Mapping[str, Any]) -> dict[str, Any]:
    import jax.numpy as jnp

    rng = np.random.Generator(np.random.PCG64(60796))
    result = dict(parameters)
    result["context_hidden_weight"] = jnp.asarray(
        rng.normal(0.0, 0.02, (64, 64)).astype(np.float32)
    )
    result["hidden_action_weight"] = jnp.asarray(
        rng.normal(0.0, 0.05, (64, 14)).astype(np.float32)
    )
    result["context_action_weight"] = jnp.asarray(
        rng.normal(0.0, 0.05, (64, 14)).astype(np.float32)
    )
    result["action_bias"] = jnp.asarray(
        rng.normal(0.0, 0.01, 14).astype(np.float32)
    )
    return result


def check_fail_closed(context: np.ndarray) -> dict[str, Any]:
    invalid = {
        "wrong_shape": (context[:, :63], 250, True, True),
        "wrong_dtype": (context.astype(np.float64), 250, True, True),
        "nonfinite": (np.full_like(context, np.nan), 250, True, True),
        "below_bound": (np.full_like(context, -1.01), 250, True, True),
        "above_bound": (np.full_like(context, 1.01), 250, True, True),
        "short_run": (context, 249, True, True),
        "long_run": (context, 251, True, True),
        "invalid_tick": (context, 250, False, True),
        "invalid_support": (context, 250, True, False),
    }
    rejected = []
    for name, (candidate, ticks, tick_valid, support_valid) in invalid.items():
        try:
            networks.validate_calibration_handoff(
                candidate,
                completed_ticks=ticks,
                all_ticks_valid=tick_valid,
                support_valid=support_valid,
            )
        except ValueError:
            rejected.append(name)
    return {
        "invalid_cases": sorted(invalid),
        "rejected_cases": sorted(rejected),
        "all_invalid_cases_rejected": sorted(invalid) == sorted(rejected),
    }


def run_signed_calibration(
    args: argparse.Namespace,
    calibrator_session: Any,
    preregistration: Mapping[str, Any],
) -> tuple[dict[str, Any], list[np.ndarray]]:
    import mujoco

    smoke, gate, v22_gate = v92.configure_v22_gate()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v96 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v96 canonical P30 fit changed")
    checkpoint_path, graph_path = v22_gate.checkpoint_paths(args.training_work_root, "final")
    if (
        sha256(checkpoint_path) != builder.CALIBRATOR_SNAPSHOT_SHA256
        or sha256(graph_path) != builder.CALIBRATOR_ONNX_SHA256
    ):
        raise ValueError("Winner-v96 calibrator artifact changed")
    snapshot = v22_gate.load_snapshot_for_reviewed_gate(checkpoint_path)
    v22_gate.validate_snapshot_for_reviewed_gate(snapshot)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    matrix = json.loads(DOMAIN.read_text(encoding="utf-8"))["evaluation_matrix"]
    configurations = {
        item["id"]: item
        for item in matrix["fixed_anchors"]
        + matrix["discovery_samples"]
        + matrix["heldout_samples"]
        if item["id"] in builder.SIGNED_CONFIGURATION_IDS
    }
    if set(configurations) != set(builder.SIGNED_CONFIGURATION_IDS):
        raise ValueError("Winner-v96 signed configurations changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    receipts = {
        (item["configuration_id"], item["plant"]): item
        for item in preregistration["source_evidence"]["signed_response_receipts"]
    }
    cells = []
    contexts: dict[tuple[str, str], np.ndarray] = {}
    maximum_target_error = 0.0
    for configuration_id in builder.SIGNED_CONFIGURATION_IDS:
        for plant in builder.PLANTS:
            cell = gate.run_cell(
                mujoco=mujoco,
                scene=scene,
                calibrator_design=calibrator_design,
                observer_type=observer_type,
                canonical_fit=args.canonical_fit,
                session=calibrator_session,
                parameters=snapshot["parameters"],
                target_mean=np.asarray(snapshot["target_mean"], dtype=np.float32),
                target_std=np.asarray(snapshot["target_std"], dtype=np.float32),
                configuration=configurations[configuration_id],
                plant=plant,
            )
            receipt = receipts[(configuration_id, plant)]
            public = gate.public_cell(cell)
            previous = np.zeros((1, 14), dtype=np.float32)
            for actual in cell["_arrays"]["actions"]:
                expected = networks.bounded_universal_action(
                    np.asarray(builder.UNIVERSAL_TARGET, dtype=np.float32)[None, :],
                    previous,
                    np.asarray([0.4192, 0.4192, 0.12, 0.12, 0.12, 0.4192, 0.4192, 0.4192, 0.4192, 0.4192, 0.4192, 0.10, 0.08, 0.10], dtype=np.float32)[None, :],
                )
                maximum_target_error = max(maximum_target_error, maximum_error(actual, expected))
                previous = actual[None, :]
            final_context = np.asarray(cell["final_h_out"], dtype=np.float32)[None, :]
            immutable = networks.validate_calibration_handoff(
                final_context, completed_ticks=250, all_ticks_valid=True, support_valid=cell["support_pass"]
            )
            contexts[(configuration_id, plant)] = immutable
            public["receipt_exact"] = bool(
                public["configuration_sha256"] == receipt["configuration_sha256"]
                and public["trace_hashes"] == receipt["trace_hashes"]
                and np.array_equal(final_context[0], np.asarray(receipt["final_h_out"], dtype=np.float32))
            )
            public["context_read_only"] = not immutable.flags.writeable
            cells.append(public)
    separation = {}
    for plant in builder.PLANTS:
        value = maximum_error(
            contexts[("COM_X_NEG", plant)], contexts[("COM_X_POS", plant)]
        )
        separation[plant] = value
    checks = {
        "exact_four_signed_cells": len(cells) == 4,
        "all_support_pass": all(cell["support_pass"] for cell in cells),
        "all_previous_action_chains_exact": all(cell["previous_action_chain_exact"] for cell in cells),
        "all_jax_onnx_hidden_errors_at_most_1e_minus_7": all(cell["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for cell in cells),
        "all_v92_receipts_exact": all(cell["receipt_exact"] for cell in cells),
        "all_contexts_immutable": all(cell["context_read_only"] for cell in cells),
        "universal_target_chain_exact": maximum_target_error == 0.0,
        "signed_context_separation_at_least_0p15": all(value >= 0.15 for value in separation.values()),
    }
    return (
        {
            "checks": checks,
            "cells": cells,
            "maximum_universal_target_error": maximum_target_error,
            "same_plant_signed_context_linf_separation": separation,
        },
        [contexts[key] for key in sorted(contexts)],
    )


def check_golden_replay(
    base_session: Any,
    off_session: Any,
    zero_session: Any,
    parameters: Mapping[str, Any],
    context: np.ndarray,
) -> dict[str, Any]:
    import jax.numpy as jnp

    rows = []
    global_hidden_error = 0.0
    global_delta_error = 0.0
    for path in GOLDENS:
        golden = np.load(path)
        h_off = np.zeros((1, 64), dtype=np.float32)
        h_zero = np.zeros((1, 64), dtype=np.float32)
        default_exact = True
        source_matches_golden = True
        zero_x_exact = True
        maximum_zero_delta = 0.0
        for obs_row, previous_row, expected_row in zip(
            golden["obs"], golden["previous_action_in"], golden["final_action"], strict=True
        ):
            obs = obs_row[None, :]
            previous = previous_row[None, :]
            source_action, source_previous = base_session.run(
                ["continuous_actions", "previous_action_out"], {"obs": obs, "previous_action": previous}
            )
            off_action, off_previous, next_h_off = off_session.run(
                ["continuous_actions", "previous_action_out", "h_out"],
                {"obs": obs, "previous_action": previous, "h_in": h_off, "calibration_context": context},
            )
            zero_action, zero_previous, next_h_zero, zero_delta = zero_session.run(
                ["continuous_actions", "previous_action_out", "h_out", "v96_adapter_delta"],
                {"obs": obs, "previous_action": previous, "h_in": h_zero, "calibration_context": context},
            )
            expected_h, expected_delta = networks.response_branch_step(
                parameters, jnp.asarray(obs), jnp.asarray(previous), jnp.asarray(h_zero), jnp.asarray(context)
            )
            global_hidden_error = max(global_hidden_error, maximum_error(expected_h, next_h_zero))
            global_delta_error = max(global_delta_error, maximum_error(expected_delta, zero_delta))
            source_matches_golden &= bool(np.array_equal(source_action[0], expected_row))
            default_exact &= bool(np.array_equal(source_action, off_action) and np.array_equal(source_previous, off_previous))
            maximum_zero_delta = max(maximum_zero_delta, maximum_error(source_action, zero_action))
            if float(obs_row[6]) == 0.0:
                zero_x_exact &= bool(np.array_equal(zero_action, np.zeros_like(zero_action)))
            h_off, h_zero = next_h_off, next_h_zero
        rows.append(
            {
                "golden": path.relative_to(ROOT).as_posix(),
                "ticks": int(golden["obs"].shape[0]),
                "source_matches_golden_bit_exact": source_matches_golden,
                "adapter_disabled_action_and_state_bit_exact": default_exact,
                "enabled_zero_adapter_maximum_action_delta": maximum_zero_delta,
                "x0_actions_exact_zero": zero_x_exact,
            }
        )
    return {
        "rows": rows,
        "maximum_jax_onnx_hidden_error": global_hidden_error,
        "maximum_jax_onnx_adapter_delta_error": global_delta_error,
        "checks": {
            "exact_1200_ticks": sum(row["ticks"] for row in rows) == 1200,
            "source_graph_matches_both_goldens_bit_exact": all(row["source_matches_golden_bit_exact"] for row in rows),
            "adapter_disabled_action_and_state_bit_exact": all(row["adapter_disabled_action_and_state_bit_exact"] for row in rows),
            "enabled_zero_adapter_delta_at_most_1e_minus_6": all(row["enabled_zero_adapter_maximum_action_delta"] <= 1.0e-6 for row in rows),
            "x0_enabled_zero_actions_exact_zero": all(row["x0_actions_exact_zero"] for row in rows),
            "zero_adapter_jax_onnx_hidden_at_most_1e_minus_7": global_hidden_error <= 1.0e-7,
            "zero_adapter_delta_exact": global_delta_error == 0.0,
        },
    }


def check_stress(
    base_session: Any,
    stress_session: Any,
    parameters: Mapping[str, Any],
    contexts: list[np.ndarray],
) -> dict[str, Any]:
    import jax.numpy as jnp
    import onnx

    model = onnx.load(POLICY)
    initializers = {
        item.name: onnx.numpy_helper.to_array(item) for item in model.graph.initializer
    }
    zero = np.load(builder.GOLDEN_ZERO)
    moving = np.load(builder.GOLDEN_MOVING)
    rng = np.random.Generator(np.random.PCG64(60797))
    maximum_hidden_error = 0.0
    maximum_delta_error = 0.0
    maximum_action_error = 0.0
    maximum_delta_magnitude = 0.0
    bounds_hold = True
    guard_holds = True
    deadband_holds = True
    for index in range(256):
        use_zero = index % 4 == 0
        source = zero if use_zero else moving
        row = int(rng.integers(0, 600))
        obs = source["obs"][row : row + 1].copy()
        previous = source["previous_action_in"][row : row + 1].copy()
        if use_zero:
            obs[:, 6] = 0.0
            previous[:] = 0.0
        h_in = rng.uniform(-0.6, 0.6, (1, 64)).astype(np.float32)
        context = contexts[index % len(contexts)]
        protected_action = base_session.run(
            ["continuous_actions"], {"obs": obs, "previous_action": previous}
        )[0]
        actual_action, actual_previous, actual_h, actual_delta = stress_session.run(
            ["continuous_actions", "previous_action_out", "h_out", "v96_adapter_delta"],
            {"obs": obs, "previous_action": previous, "h_in": h_in, "calibration_context": context},
        )
        expected_h, expected_delta = networks.response_branch_step(
            parameters, jnp.asarray(obs), jnp.asarray(previous), jnp.asarray(h_in), jnp.asarray(context)
        )
        expected_action = networks.compose_final_action_numpy(
            protected_action, np.asarray(expected_delta), obs, previous, initializers
        )
        maximum_hidden_error = max(maximum_hidden_error, maximum_error(expected_h, actual_h))
        maximum_delta_error = max(maximum_delta_error, maximum_error(expected_delta, actual_delta))
        maximum_action_error = max(maximum_action_error, maximum_error(expected_action, actual_action), maximum_error(actual_action, actual_previous))
        maximum_delta_magnitude = max(maximum_delta_magnitude, float(np.max(np.abs(actual_delta))))
        max_delta = np.asarray(initializers["max_action_delta"], dtype=np.float32)
        bounds_hold &= bool(
            np.max(np.abs(actual_action)) <= 1.0 + 1.0e-7
            and np.all(np.abs(actual_action - previous) <= max_delta + 1.0e-7)
        )
        indices = np.asarray(initializers["guard_joint_obs_indices"], dtype=np.int64)
        home = np.asarray(initializers["guard_home"], dtype=np.float32)
        scale = np.asarray(initializers["guard_action_scale"], dtype=np.float32)
        actual_target = home + obs[:, indices]
        sent_target = home + actual_action * scale
        mask = np.asarray(initializers["guard_pitch_mask"], dtype=np.bool_)
        margin = np.asarray(initializers["guard_margin"], dtype=np.float32)
        guard_holds &= bool(np.all(np.abs(sent_target[mask] - actual_target[mask]) <= margin[mask] + 1.0e-6))
        if use_zero:
            deadband_holds &= bool(np.array_equal(actual_action, np.zeros_like(actual_action)))
    return {
        "cases": 256,
        "maximum_jax_onnx_hidden_error": maximum_hidden_error,
        "maximum_jax_onnx_adapter_delta_error": maximum_delta_error,
        "maximum_onnx_numpy_final_action_error": maximum_action_error,
        "maximum_adapter_delta_magnitude": maximum_delta_magnitude,
        "checks": {
            "adapter_stress_is_nontrivial": maximum_delta_magnitude > 1.0e-4,
            "stress_jax_onnx_hidden_at_most_1e_minus_6": maximum_hidden_error <= 1.0e-6,
            "stress_jax_onnx_delta_at_most_1e_minus_6": maximum_delta_error <= 1.0e-6,
            "stress_onnx_numpy_final_action_at_most_1e_minus_6": maximum_action_error <= 1.0e-6,
            "absolute_and_rate_bounds_hold": bounds_hold,
            "actual_centered_pitch_guard_holds": guard_holds,
            "x0_deadband_is_exact": deadband_holds,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.formal_contract_authorized:
        raise PermissionError("Winner-v96 requires explicit offline CPU contract authorization")
    if args.output.exists() or args.artifact_dir.exists():
        raise FileExistsError("refusing to overwrite Winner-v96 evidence or artifacts")

    import jax
    import onnx

    if jax.default_backend() != "cpu" or any(device.platform != "cpu" for device in jax.devices()):
        raise ValueError("Winner-v96 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    args.artifact_dir.mkdir(parents=True)
    calibrator_path = args.artifact_dir / "winner_v96_universal_calibrator.onnx"
    off_path = args.artifact_dir / "winner_v96_locomotion_default_off.onnx"
    zero_path = args.artifact_dir / "winner_v96_locomotion_enabled_zero.onnx"
    stress_path = args.artifact_dir / "winner_v96_locomotion_stress.onnx"
    source_calibrator = args.training_work_root / "graphs/winner_v22_final.onnx"
    zero_parameters = networks.initialize_locomotion_adapter_parameters(seed=60721)
    stressed_parameters = stress_parameters(zero_parameters)
    networks.export_universal_calibrator_onnx(
        source_calibrator, np.asarray(builder.UNIVERSAL_TARGET, dtype=np.float32), calibrator_path
    )
    networks.export_locomotion_onnx(POLICY, zero_parameters, off_path, adapter_enabled=False)
    networks.export_locomotion_onnx(POLICY, zero_parameters, zero_path, adapter_enabled=True, expose_adapter_delta=True)
    networks.export_locomotion_onnx(POLICY, stressed_parameters, stress_path, adapter_enabled=True, expose_adapter_delta=True)
    for path in (calibrator_path, off_path, zero_path, stress_path):
        onnx.checker.check_model(onnx.load(path))
    calibrator_session = session(calibrator_path)
    base_session = session(POLICY)
    off_session = session(off_path)
    zero_session = session(zero_path)
    stress_session = session(stress_path)
    signed, contexts = run_signed_calibration(args, calibrator_session, preregistration)
    fail_closed = check_fail_closed(contexts[0])
    golden = check_golden_replay(base_session, off_session, zero_session, zero_parameters, contexts[0])
    stress = check_stress(base_session, stress_session, stressed_parameters, contexts)
    abi = {
        "calibrator": describe_abi(calibrator_path),
        "locomotion_default_off": describe_abi(off_path),
        "locomotion_enabled_zero": describe_abi(zero_path),
    }
    expected_abi = preregistration["expected_abi"]
    abi_exact = bool(
        abi["calibrator"] == expected_abi["calibrator"]
        and abi["locomotion_default_off"] == expected_abi["locomotion"]
        and abi["locomotion_enabled_zero"]["inputs"] == expected_abi["locomotion"]["inputs"]
        and abi["locomotion_enabled_zero"]["outputs"][:3] == expected_abi["locomotion"]["outputs"]
        and abi["locomotion_enabled_zero"]["outputs"][3] == {"name": "v96_adapter_delta", "dtype": "float32", "shape": [1, 14]}
    )
    exported_models = [onnx.load(path) for path in (calibrator_path, off_path, zero_path, stress_path)]
    no_v95_readout = all(
        not any("auxiliary" in item.name.lower() or "readout" in item.name.lower() for item in model.graph.initializer)
        for model in exported_models
    )
    checks = {
        "cpu_only_execution": jax.default_backend() == "cpu",
        "exact_abis": abi_exact,
        "source_policy_hash_exact": sha256(POLICY) == builder.POLICY_SHA256,
        "calibrator_source_hash_exact": sha256(source_calibrator) == builder.CALIBRATOR_ONNX_SHA256,
        "all_signed_calibration_checks": all(signed["checks"].values()),
        "all_invalid_handoffs_fail_closed": fail_closed["all_invalid_cases_rejected"],
        "all_golden_replay_checks": all(golden["checks"].values()),
        "all_nonzero_stress_checks": all(stress["checks"].values()),
        "v95_readout_not_exported": no_v95_readout,
        "all_metrics_finite": all(
            math.isfinite(value)
            for value in (
                signed["maximum_universal_target_error"],
                *signed["same_plant_signed_context_linf_separation"].values(),
                golden["maximum_jax_onnx_hidden_error"],
                golden["maximum_jax_onnx_adapter_delta_error"],
                stress["maximum_jax_onnx_hidden_error"],
                stress["maximum_jax_onnx_adapter_delta_error"],
                stress["maximum_onnx_numpy_final_action_error"],
                stress["maximum_adapter_delta_magnitude"],
            )
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed_checks
    artifacts = {
        path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in (calibrator_path, off_path, zero_path, stress_path)
    }
    result = {
        "schema_version": "winner_v96.response_conditioned_mechanics_result.v1",
        "status": "PASS_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS" if passed else "HOLD_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS",
        "decision": "PREREGISTER_RESPONSE_CONDITIONED_LOCOMOTION_TRAINING" if passed else "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION",
        "checks": checks,
        "failed_checks": failed_checks,
        "signed_calibration": signed,
        "handoff_fail_closed": fail_closed,
        "golden_replay": golden,
        "nonzero_adapter_stress": stress,
        "abi": abi,
        "artifacts": artifacts,
        "stable_v95_readout_identity": preregistration["source_evidence"]["stable_readout"],
        "execution": {"simulator_cells": 4, "golden_ticks": 1200, "stress_cases": 256, "onnx_exports": 4, "optimizer_updates": 0, "robot_or_rdk_access": 0},
        "sources": preregistration["sources"],
        "source_manifest_sha256": preregistration["source_manifest_sha256"],
        "authority": preregistration["authority"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(f"failed_checks={failed_checks}")
    print(f"sha256={sha256(args.output)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
