#!/usr/bin/env python3
"""Run the zero-cell integration contract for the Winner-v12 support gate."""

from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
from typing import Any, Mapping


os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import build_winner_v12_calibrator_support_gate_cpu_contract as builder  # noqa: E402


EXPECTED_EXECUTION = {
    "formal_support_cells": 0,
    "heldout_repeat_cells": 0,
    "locomotion_training_steps": 0,
    "robot_or_rdk_access": 0,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate_contract_header(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_version")
        != "winner_v12.calibrator_support_gate_cpu_contract.v1"
        or contract.get("status")
        != "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT_FROZEN"
        or contract.get("decision")
        != "AUTHORIZE_ONE_ZERO_CELL_SUPPORT_GATE_CPU_CONTRACT_RUN_ONLY"
    ):
        raise ValueError("support-gate CPU contract is not frozen and passing")
    if contract.get("execution_now") != EXPECTED_EXECUTION:
        raise ValueError("support-gate CPU-contract execution authority changed")
    authority = contract.get("authority")
    if (
        not isinstance(authority, dict)
        or authority.get("robot_clearance") is not False
        or authority.get("rdkx5_robot_serial_gpio_i2c_torque_motion") is not False
    ):
        raise ValueError("support-gate CPU-contract robot authority changed")
    gate = contract.get("formal_gate_after_contract")
    if gate != {
        "checkpoint_labels": ["half", "final"],
        "main_cells_per_checkpoint": 124,
        "main_cells_total": 248,
        "heldout_repeat_cells_total": 64,
        "duration_ticks_per_cell": 250,
        "all_cells_at_both_checkpoints_must_pass": True,
    }:
        raise ValueError("formal support-gate dimensions changed")
    checkpoints = contract.get("verified_checkpoints")
    if not isinstance(checkpoints, dict) or set(checkpoints) != {"half", "final"}:
        raise ValueError("support-gate checkpoint identity set changed")


def verify_sources(contract: Mapping[str, Any]) -> bool:
    sources = contract.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("support-gate source manifest is missing")
    for name, item in sources.items():
        if set(item) != {"path", "hash_mode", "sha256"} or item["hash_mode"] != "lf":
            raise ValueError(f"support-gate source identity changed: {name}")
        path = ROOT / item["path"]
        if not path.is_file() or lf_sha256(path) != item["sha256"]:
            raise ValueError(f"support-gate source hash changed: {name}")
    if builder.canonical_sha256(sources) != contract.get("source_manifest_sha256"):
        raise ValueError("support-gate source manifest hash changed")
    return True


def verify_immutable_inputs(
    contract: Mapping[str, Any], playground_root: Path, canonical_fit: Path
) -> dict[str, str]:
    expected = contract.get("immutable_gate_inputs")
    if not isinstance(expected, dict) or set(expected) != {
        "canonical_p30_fit",
        "playground_model",
        "playground_scene",
    }:
        raise ValueError("immutable gate-input schema changed")
    fit = expected["canonical_p30_fit"]
    if (
        fit["path"] != "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
        or canonical_fit.read_bytes().replace(b"\r\n", b"\n")
        != (ROOT / fit["path"]).read_bytes().replace(b"\r\n", b"\n")
        or lf_sha256(canonical_fit) != fit["lf_sha256"]
    ):
        raise ValueError("canonical P30 fit changed")
    observed = {"canonical_p30_fit_lf_sha256": lf_sha256(canonical_fit)}
    for key in ("playground_model", "playground_scene"):
        item = expected[key]
        path = playground_root / item["relative_path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise ValueError(f"{key} changed")
        observed[f"{key}_sha256"] = sha256(path)
    return observed


def verify_training_files(
    contract: Mapping[str, Any], training_work_root: Path
) -> dict[str, dict[str, str | int]]:
    if training_work_root.name != builder.EXPECTED_WORK_ROOT_NAME:
        raise ValueError("training work-root identity changed")
    observed = {}
    for label in ("half", "final"):
        identity = contract["verified_checkpoints"][label]
        expected_update = {"half": 50, "final": 100}[label]
        if identity["label"] != label or identity["update"] != expected_update:
            raise ValueError(f"{label} checkpoint boundary changed")
        observed[label] = {}
        for kind in ("checkpoint", "onnx", "receipt"):
            expected = identity[kind]
            path = training_work_root / expected["file"]
            actual = {
                "file": path.name,
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            if actual != expected:
                raise ValueError(f"{label} {kind} identity changed")
            observed[label][f"{kind}_sha256"] = actual["sha256"]
    return observed


def software_versions_exact(expected: Mapping[str, str]) -> dict[str, Any]:
    observed = {
        "python": platform.python_version(),
        "jax": metadata.version("jax"),
        "jaxlib": metadata.version("jaxlib"),
        "mujoco": metadata.version("mujoco"),
        "numpy": metadata.version("numpy"),
        "onnx": metadata.version("onnx"),
        "onnxruntime": metadata.version("onnxruntime"),
    }
    return {
        "expected": dict(expected),
        "observed": observed,
        "exact": observed == expected,
    }


def transport_primitive_contract(gate: Any, smoke: Any) -> dict[str, bool]:
    import numpy as np

    raw = np.linspace(-0.75, 0.75, 115, dtype=np.float32)
    quantized = gate.native_quantize_observation(raw)
    unchanged = np.r_[6:13, 41:115]
    quantization_slots_exact = np.array_equal(quantized[unchanged], raw[unchanged])
    identity = gate.ObservationTransport(None, None)
    identity_exact = np.array_equal(identity.observe(raw), raw)
    delayed_imu = gate.ObservationTransport(
        {"id": "IMU_DELAY_1", "imu_delay_ticks": 1}, None
    )
    first = delayed_imu.observe(raw)
    second_raw = raw + np.float32(0.125)
    second = delayed_imu.observe(second_raw)
    imu_delay_exact = (
        np.array_equal(first[0:6], np.zeros((6,), dtype=np.float32))
        and np.array_equal(first[6:], raw[6:])
        and np.array_equal(second[0:6], raw[0:6])
        and np.array_equal(second[6:], second_raw[6:])
    )
    action0 = np.linspace(-0.2, 0.2, 14, dtype=np.float32)
    action1 = action0 + np.float32(0.01)
    delay = gate.DelayedActionQueue(1)
    action_delay_exact = np.array_equal(
        delay.push(action0), np.zeros((14,), dtype=np.float32)
    ) and np.array_equal(delay.push(action1), action0)
    threshold_summary = {
        "valid_ticks": gate.TICKS,
        "initial_contacts": [1, 1],
        "minimum_base_z_m": smoke.MINIMUM_BASE_Z_M,
        "maximum_abs_tilt_rad": smoke.MAXIMUM_ABS_TILT_RAD,
        "maximum_torque_nm": smoke.TORQUE_LIMIT_NM,
        "maximum_current_a": smoke.CURRENT_LIMIT_A,
        "maximum_overcurrent_streak_ticks": smoke.OVERCURRENT_TRIP_TICKS - 1,
        "maximum_final_window_gyro_xy_norm_rad_s": smoke.FINAL_GYRO_LIMIT_RAD_S,
    }
    boundary_inclusive = gate.support_pass(threshold_summary)
    over = dict(threshold_summary)
    over["maximum_abs_tilt_rad"] = math.nextafter(smoke.MAXIMUM_ABS_TILT_RAD, math.inf)
    boundary_rejects_excess = not gate.support_pass(over)
    return {
        "identity_transport_exact": bool(identity_exact),
        "native_quantization_changes_only_declared_slots": bool(
            quantization_slots_exact
        ),
        "one_tick_imu_delay_exact": bool(imu_delay_exact),
        "one_tick_action_delay_exact": bool(action_delay_exact),
        "support_thresholds_inclusive": bool(boundary_inclusive),
        "support_threshold_rejects_first_excess": bool(boundary_rejects_excess),
    }


def checkpoint_graph_contract(
    *,
    label: str,
    training_work_root: Path,
    snapshot: Mapping[str, Any],
    smoke: Any,
    training: Any,
    gate: Any,
) -> dict[str, Any]:
    import jax.numpy as jnp
    import numpy as np
    import onnxruntime as ort

    graph_path = training_work_root / f"winner_v12_calibrator_{label}.onnx"
    update = {"half": 50, "final": 100}[label]
    flat = np.arange(gate.TICKS * training.OBS_SIZE, dtype=np.int64)
    observations = (
        ((flat + update * 17) % 257).astype(np.float32) - np.float32(128.0)
    ).reshape(gate.TICKS, training.OBS_SIZE) / np.float32(128.0)
    parameters = training.deployable_parameters(snapshot["parameters"])
    independent = smoke.onnx_contract(graph_path, parameters, observations)
    session_options = ort.SessionOptions()
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1
    session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session = ort.InferenceSession(
        str(graph_path),
        sess_options=session_options,
        providers=["CPUExecutionProvider"],
    )
    previous = np.zeros((14,), dtype=np.float32)
    hidden = np.zeros((64,), dtype=np.float32)
    hidden_error = 0.0
    previous_exact = True
    graph_boundary_exact = True
    all_finite = True
    for observation in observations:
        action, previous_out, h_out = [
            np.asarray(value[0], dtype=np.float32)
            for value in session.run(
                ["calibration_actions", "previous_action_out", "h_out"],
                {
                    "obs": observation[None, :],
                    "previous_action": previous[None, :],
                    "h_in": hidden[None, :],
                },
            )
        ]
        jax_h, prediction = training.response_step(
            snapshot["parameters"],
            jnp.asarray(observation),
            jnp.asarray(previous),
            jnp.asarray(hidden),
            jnp.asarray(action),
        )
        jax_h_np = np.asarray(jax_h, dtype=np.float32)
        prediction_np = np.asarray(prediction, dtype=np.float32)
        all_finite &= bool(
            np.all(np.isfinite(action))
            and np.all(np.isfinite(h_out))
            and np.all(np.isfinite(prediction_np))
        )
        hidden_error = max(hidden_error, float(np.max(np.abs(jax_h_np - h_out))))
        previous_exact &= np.array_equal(previous_out, action)
        graph_boundary_exact &= np.array_equal(
            action, smoke.bounded_action_numpy(action, previous)
        )
        previous = previous_out
        hidden = h_out
    return {
        "label": label,
        "update": update,
        "independent_onnx_contract": independent,
        "support_runner_chain_ticks": gate.TICKS,
        "support_runner_all_outputs_finite": bool(all_finite),
        "support_runner_previous_action_chain_bit_exact": bool(previous_exact),
        "support_runner_graph_boundary_exact": bool(graph_boundary_exact),
        "support_runner_jax_onnx_h_max_abs_error": hidden_error,
        "support_runner_jax_onnx_h_at_most_1e_7": hidden_error <= 1.0e-7,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--zero-cell-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.zero_cell_contract_authorized:
        raise PermissionError(
            "zero-cell contract requires --offline-cpu-only "
            "--zero-cell-contract-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite zero-cell result: {args.output}")
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    validate_contract_header(contract)
    source_exact = verify_sources(contract)
    immutable_inputs = verify_immutable_inputs(
        contract, args.playground_root, args.canonical_fit
    )
    training_files = verify_training_files(contract, args.training_work_root)

    import jax
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as gate
    import run_winner_v12_full_calibrator_training as full_training
    import winner_v12_calibrator_training as training

    versions = software_versions_exact(contract["software_versions"])
    cpu_only = jax.default_backend() == "cpu" and all(
        device.platform == "cpu" for device in jax.devices()
    )
    if not cpu_only or not versions["exact"]:
        raise ValueError("zero-cell support contract environment changed")
    scene = args.playground_root / builder.SCENE_RELATIVE
    nominal = gate.nominal_configuration(mujoco, scene)
    nominal_exact = (
        nominal["id"] == "NOMINAL_MODEL"
        and nominal["all_link_mass_scale"] == 1.0
        and nominal["torso_mass_add_kg"] == 0.0
        and nominal["torso_com_offset_m"] == [0.0, 0.0, 0.0]
    )
    smoke.load_runtime_observer(args.canonical_fit)
    primitives = transport_primitive_contract(gate, smoke)
    graph_contracts = []
    for label in ("half", "final"):
        checkpoint = args.training_work_root / f"winner_v12_calibrator_{label}.npz"
        snapshot = full_training.load_snapshot(checkpoint)
        full_training.validate_resume(snapshot)
        expected_update = {"half": 50, "final": 100}[label]
        if (
            snapshot["metadata"]["stage"] != "stage2"
            or snapshot["metadata"]["completed_updates"] != expected_update
        ):
            raise ValueError(f"{label} snapshot boundary changed")
        graph_contracts.append(
            checkpoint_graph_contract(
                label=label,
                training_work_root=args.training_work_root,
                snapshot=snapshot,
                smoke=smoke,
                training=training,
                gate=gate,
            )
        )
    checks = {
        "contract_header_exact": True,
        "source_manifest_exact": source_exact,
        "immutable_inputs_exact": bool(immutable_inputs),
        "training_files_match_artifact_verifier": set(training_files)
        == {"half", "final"},
        "software_versions_exact": versions["exact"],
        "jax_cpu_only": cpu_only,
        "nominal_model_identity_exact": nominal_exact,
        "all_transport_primitives_exact": all(primitives.values()),
        "both_checkpoint_graphs_checked": [row["label"] for row in graph_contracts]
        == ["half", "final"],
        "all_independent_graph_contracts_pass": all(
            row["independent_onnx_contract"]["abi_exact"]
            and row["independent_onnx_contract"]["all_initializers_finite"]
            and row["independent_onnx_contract"]["all_chain_outputs_finite"]
            and row["independent_onnx_contract"]["training_only_tensors_absent"]
            and row["independent_onnx_contract"]["jax_onnx_at_most_1e_7"]
            and row["independent_onnx_contract"][
                "previous_action_out_equals_action_bit_exact"
            ]
            for row in graph_contracts
        ),
        "all_support_runner_graph_chains_pass": all(
            row["support_runner_all_outputs_finite"]
            and row["support_runner_previous_action_chain_bit_exact"]
            and row["support_runner_graph_boundary_exact"]
            and row["support_runner_jax_onnx_h_at_most_1e_7"]
            for row in graph_contracts
        ),
        "formal_cells_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v12.calibrator_support_gate_cpu_contract_result.v1",
        "status": (
            "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_ONE_FROZEN_248_CELL_SUPPORT_GATE_RUN_ONLY"
            if not failed
            else "DO_NOT_RUN_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
        ),
        "contract_lf_sha256": lf_sha256(args.contract),
        "checks": checks,
        "failed_checks": failed,
        "software_versions": versions,
        "immutable_inputs": immutable_inputs,
        "training_files": training_files,
        "transport_primitives": primitives,
        "checkpoint_graph_contracts": graph_contracts,
        "execution": EXPECTED_EXECUTION,
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen 248-cell support-gate run",
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
