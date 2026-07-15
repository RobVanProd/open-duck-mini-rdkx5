#!/usr/bin/env python3
"""Contract and run the preregistered reset torso-COM estimator feasibility curve."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
INIT_TOOL = REPO / "tools/run_ground_up_torso_com_mjx_initialization_order_audit.py"
BASE_TOOL = REPO / "tools/run_ground_up_torso_com_signed_response.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_FEASIBILITY_PREREGISTRATION_20260715.md"
EAGER_RESULT = REPO / "outputs/analysis/ground_up_torso_com_eager_mjx_accelerometer_map_result.json"
DECODE_CORRECTION = REPO / "outputs/analysis/ground_up_torso_com_decode_interpretation_correction.json"
SIGNED_RESULT = REPO / "outputs/analysis/ground_up_torso_com_signed_response_result.json"
CROSSED_RESULT = REPO / "outputs/analysis/ground_up_torso_com_crossed_phase_result.json"

EXPECTED_HASHES = {
    "init_tool": "53821c1deb30ec2eb98dcfdb5ae380ebf17009ae5b22734bcc6499e6aa7e2e08",
    "base_tool": "6e25285e9b12b8763aac0723e16c6d5ca63cac9e1956205fd44bdff714179b4d",
    "prereg": "706a1463372622f66e9640cff77474c25d67b210568a2bf30cca1ea61757c70e",
    "eager_result": "05a12700ca6d9af6479fcb97a3c64109412a139efc24e369110c60ce8c1a9149",
    "decode_correction": "ef62ea7e479c1734dd8b416ce4bcb4636de9d4b5bf40c55cf729c8a536af1f37",
    "signed_result": "8c09ada8ce392c09fcee3cd9e7f449be5b1c50ca28b1640a4a3103755cc3b814",
    "crossed_result": "9c0823c7fce7bd409acbc53176c412dc45863f9c9ebaa27fa00a4f4597984ef0",
}
OFFSETS = (-0.05, -0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05)
ANCHORS = (-0.05, 0.0, 0.05)
HELD_OUT = (-0.04, -0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.04)
ORACLE = {
    -0.05: np.asarray([-13.04679012298584, 0.7727481126785278, 28.672449111938477]),
    0.0: np.asarray([-11.879271507263184, 0.8971166610717773, 29.650177001953125]),
    0.05: np.asarray([-10.715840339660645, 1.0117170810699463, 30.856430053710938]),
}
ANCHOR_TOLERANCE_M_S2 = 1e-3
SEPARATION_FLOOR_M_S2 = 1e-3
ERROR_CEILING_M = 0.005


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_init_tool() -> Any:
    spec = importlib.util.spec_from_file_location("init_order_audit", INIT_TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load initialization-order environment source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_paths() -> dict[str, Path]:
    return {
        "init_tool": INIT_TOOL, "base_tool": BASE_TOOL, "prereg": PREREG,
        "eager_result": EAGER_RESULT, "decode_correction": DECODE_CORRECTION,
        "signed_result": SIGNED_RESULT, "crossed_result": CROSSED_RESULT,
    }


def model_for_offset(nominal: Any, offset: float) -> Any:
    body_ipos = nominal.body_ipos.at[2, 0].add(float(offset))
    return nominal.replace(body_ipos=body_ipos)


def run_contract(output: Path) -> int:
    actual_hashes = {name: sha256(path) for name, path in source_paths().items()}
    init = load_init_tool()
    base = init.load_base()
    jax, env, nominal, _negative, _positive, reset = init.models_and_reset(base)
    checks: dict[str, bool] = {}
    checks["frozen_source_hashes_exact"] = actual_hashes == EXPECTED_HASHES
    checks["upstream_decisions_exact"] = (
        json.loads(EAGER_RESULT.read_text()).get("decision")
        == "SUPPORT_PREREGISTERED_MATCHED_SENSOR_ACTOR_RESPONSE_STUDY"
        and json.loads(DECODE_CORRECTION.read_text()).get("decision")
        == "SUPERSEDE_DECODE_SELECTION_NO_ARM_FAMILY_SELECTED"
        and json.loads(SIGNED_RESULT.read_text()).get("decision")
        == "MIXED_SIGN_NO_POLICY_FAMILY_SELECTED"
        and json.loads(CROSSED_RESULT.read_text()).get("decision")
        == "CROSSED_LOCALIZATION_UNRESOLVED_NO_FAMILY_SELECTED"
    )
    checks["cpu_only"] = (
        os.environ.get("CUDA_VISIBLE_DEVICES") == ""
        and os.environ.get("JAX_PLATFORMS") == "cpu"
        and jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    sensor = init.sensor_contract(env.mj_model)
    checks["body_and_sensor_identity_exact"] = (
        int(env.mj_model.body("trunk_assembly").id) == 2
        and float(env.mj_model.body_mass[2]) > 0.0
        and sensor["name"] == "accelerometer" and sensor["address"] == 6
        and sensor["dimension"] == 3 and sensor["site_name"] == "imu"
    )
    qpos, qvel, ctrl = reset
    checks["home_reset_exact"] = (
        np.asarray(qpos).shape == (int(nominal.nq),)
        and np.asarray(qvel).shape == (int(nominal.nv),)
        and np.asarray(ctrl).shape == (int(nominal.nu),)
        and np.count_nonzero(np.asarray(qvel)) == 0
        and all(np.isfinite(np.asarray(value)).all() for value in reset)
    )
    checks["offset_and_split_cardinality_exact"] = (
        len(OFFSETS) == 11 and tuple(sorted(OFFSETS)) == OFFSETS
        and set(ANCHORS).isdisjoint(HELD_OUT)
        and set(ANCHORS) | set(HELD_OUT) == set(OFFSETS)
        and len(HELD_OUT) == 8
    )
    mutations_exact = True
    base_ipos = np.asarray(nominal.body_ipos)
    for offset in OFFSETS:
        model = model_for_offset(nominal, offset)
        delta = np.asarray(model.body_ipos) - base_ipos
        nonzero = int(np.count_nonzero(delta))
        expected_x = np.asarray(
            base_ipos[2, 0] + np.asarray(offset, dtype=base_ipos.dtype),
            dtype=base_ipos.dtype,
        )
        if offset == 0.0:
            mutations_exact = mutations_exact and nonzero == 0
        else:
            mutations_exact = mutations_exact and (
                nonzero == 1
                and np.asarray(model.body_ipos)[2, 0] == expected_x
            )
    checks["body2_x_only_offset_models_exact"] = bool(mutations_exact)
    source = Path(__file__).read_text()
    checks["frozen_estimator_source_structure_exact"] = all(fragment in source for fragment in (
        "tn = float(np.clip(np.dot(delta, un) / np.dot(un, un), 0.0, 1.0))",
        "tp = float(np.clip(np.dot(delta, up) / np.dot(up, up), 0.0, 1.0))",
        "choose_negative = residual_negative <= residual_positive",
        "ERROR_CEILING_M = 0.005",
        "SEPARATION_FLOOR_M_S2 = 1e-3",
    ))
    init_fragment = "data = " + "mjx_env.init(model, qpos=qpos, qvel=qvel, ctrl=ctrl)"
    sensor_fragment = "jax.device_get(" + "data.sensordata[6:9])"
    checks["one_eager_sensor_read_per_offset_source_contract"] = (
        source.count(init_fragment) == 1 and source.count(sensor_fragment) == 1
        and "jax.jit(" not in source and "mjx.step(" not in source
    )
    checks["formal_offset_sensor_reads_zero"] = True
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_RESET_COM_ESTIMATOR_FEASIBILITY_CONTRACT"
        if not failed else "FAIL_RESET_COM_ESTIMATOR_FEASIBILITY_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_reset_estimator_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "details": {
            "tool_sha256": sha256(Path(__file__)), "source_hashes": actual_hashes,
            "sensor": sensor, "offsets_m": list(OFFSETS),
            "anchors_m": list(ANCHORS), "held_out_m": list(HELD_OUT),
            "devices": [str(device) for device in jax.devices()],
        },
        "execution": {
            "cpu_only": True, "formal_offset_sensor_reads": 0,
            "dynamic_steps": 0, "actor_calls": 0, "training": False,
            "robot_or_rdk": False,
        },
        "authority": {
            "eleven_point_reset_curve_if_pass": True, "dynamic_steps": False,
            "actor_calls": False, "training": False, "gpu_or_igpu": False,
            "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


def estimate_offset(
    sensor: np.ndarray, negative: np.ndarray, nominal: np.ndarray, positive: np.ndarray
) -> dict[str, float | str]:
    un = negative - nominal
    up = positive - nominal
    delta = sensor - nominal
    tn = float(np.clip(np.dot(delta, un) / np.dot(un, un), 0.0, 1.0))
    tp = float(np.clip(np.dot(delta, up) / np.dot(up, up), 0.0, 1.0))
    estimate_negative = -0.05 * tn
    estimate_positive = 0.05 * tp
    residual_negative = float(np.linalg.norm(sensor - (nominal + tn * un)))
    residual_positive = float(np.linalg.norm(sensor - (nominal + tp * up)))
    choose_negative = residual_negative <= residual_positive
    return {
        "estimate_m": estimate_negative if choose_negative else estimate_positive,
        "selected_segment": "NEGATIVE" if choose_negative else "POSITIVE",
        "negative_fraction": tn, "positive_fraction": tp,
        "negative_residual_m_s2": residual_negative,
        "positive_residual_m_s2": residual_positive,
    }


def run_study(contract_path: Path, output: Path, markdown: Path) -> int:
    contract = json.loads(contract_path.read_text())
    if contract.get("status") != "PASS_RESET_COM_ESTIMATOR_FEASIBILITY_CONTRACT":
        raise ValueError("passing reset-COM estimator contract required")
    if contract["details"]["tool_sha256"] != sha256(Path(__file__)):
        raise ValueError("reset-COM estimator tool changed after contract")
    init = load_init_tool()
    base = init.load_base()
    jax, env, nominal, _negative, _positive, reset = init.models_and_reset(base)
    from mujoco_playground._src import mjx_env

    qpos, qvel, ctrl = reset
    sensor_values: dict[float, np.ndarray] = {}
    model_checks: dict[str, bool] = {}
    base_ipos = np.asarray(nominal.body_ipos)
    for offset in OFFSETS:
        model = model_for_offset(nominal, offset)
        delta = np.asarray(model.body_ipos) - base_ipos
        expected_nonzero = 0 if offset == 0.0 else 1
        expected_x = np.asarray(
            base_ipos[2, 0] + np.asarray(offset, dtype=base_ipos.dtype),
            dtype=base_ipos.dtype,
        )
        model_checks[str(offset)] = bool(
            np.count_nonzero(delta) == expected_nonzero
            and np.asarray(model.body_ipos)[2, 0] == expected_x
        )
        data = mjx_env.init(model, qpos=qpos, qvel=qvel, ctrl=ctrl)
        sensor_values[offset] = np.asarray(
            jax.device_get(data.sensordata[6:9]), dtype=float
        )

    anchor_errors = {
        str(offset): float(np.max(np.abs(sensor_values[offset] - ORACLE[offset])))
        for offset in ANCHORS
    }
    finite = all(np.isfinite(sensor).all() for sensor in sensor_values.values())
    method_validity = {
        "all_anchor_vectors_match_oracle": max(anchor_errors.values()) <= ANCHOR_TOLERANCE_M_S2,
        "all_body2_x_only_model_mutations_exact": all(model_checks.values()),
        "all_sensor_and_estimator_values_finite": finite,
        "cpu_only_contract_passed": bool(contract["checks"]["cpu_only"]),
    }

    estimates: dict[float, dict[str, float | str]] = {}
    for offset in HELD_OUT:
        estimates[offset] = estimate_offset(
            sensor_values[offset], sensor_values[-0.05],
            sensor_values[0.0], sensor_values[0.05],
        )
    estimate_values = [float(estimates[offset]["estimate_m"]) for offset in HELD_OUT]
    sign_correct = all(
        float(estimates[offset]["estimate_m"]) * offset > 0.0 for offset in HELD_OUT
    )
    strictly_ordered = all(
        left < right for left, right in zip(estimate_values, estimate_values[1:])
    )
    errors = {
        str(offset): abs(float(estimates[offset]["estimate_m"]) - offset)
        for offset in HELD_OUT
    }
    separations = {
        f"{left:.2f}_to_{right:.2f}": float(
            np.linalg.norm(sensor_values[right] - sensor_values[left])
        )
        for left, right in zip(OFFSETS, OFFSETS[1:])
    }
    maximum_error = max(errors.values())
    minimum_separation = min(separations.values())
    estimators_finite = all(
        math.isfinite(float(value))
        for estimate in estimates.values()
        for key, value in estimate.items()
        if key != "selected_segment"
    )
    method_validity["all_sensor_and_estimator_values_finite"] = finite and estimators_finite
    valid = all(method_validity.values())
    separation_pass = minimum_separation > SEPARATION_FLOOR_M_S2
    error_pass = maximum_error <= ERROR_CEILING_M
    if not valid:
        status = "INVALID_RESET_COM_ESTIMATOR_FEASIBILITY"
        decision = status
    elif sign_correct and strictly_ordered and separation_pass and error_pass:
        status = "PASS_RESET_COM_ESTIMATOR_FEASIBILITY_COMPLETE"
        decision = "SUPPORT_RESET_LATCHED_PIECEWISE_LINEAR_COM_ESTIMATOR_ARM"
    elif sign_correct and strictly_ordered and separation_pass:
        status = "PASS_RESET_COM_ESTIMATOR_FEASIBILITY_COMPLETE"
        decision = "SUPPORT_RESET_LATCHED_NONLINEAR_COM_ESTIMATOR_ARM"
    else:
        status = "PASS_RESET_COM_ESTIMATOR_FEASIBILITY_COMPLETE"
        decision = "RESET_ACCELEROMETER_CURVE_INSUFFICIENT_NO_ESTIMATOR_FAMILY_SELECTED"

    cells = []
    for offset in OFFSETS:
        cell: dict[str, Any] = {
            "offset_m": offset, "role": "ANCHOR" if offset in ANCHORS else "HELD_OUT",
            "accelerometer_m_s2": sensor_values[offset].tolist(),
            "model_mutation_exact": model_checks[str(offset)],
        }
        if offset in ANCHORS:
            cell["anchor_max_abs_error_m_s2"] = anchor_errors[str(offset)]
        else:
            cell.update(estimates[offset])
            cell["absolute_offset_error_m"] = errors[str(offset)]
            cell["sign_correct"] = float(estimates[offset]["estimate_m"]) * offset > 0.0
        cells.append(cell)
    payload = {
        "schema_version": "ground_up_torso_com_reset_estimator_feasibility.v1",
        "status": status, "decision": decision, "effective_sample_size": 1,
        "validity": {**method_validity, "valid": valid},
        "metrics": {
            "all_held_out_signs_correct": sign_correct,
            "held_out_estimates_strictly_ordered": strictly_ordered,
            "maximum_held_out_absolute_error_m": maximum_error,
            "error_ceiling_m": ERROR_CEILING_M, "error_ceiling_pass": error_pass,
            "minimum_adjacent_sensor_separation_m_s2": minimum_separation,
            "separation_floor_m_s2": SEPARATION_FLOOR_M_S2,
            "separation_floor_pass": separation_pass,
            "anchor_max_abs_errors_m_s2": anchor_errors,
            "held_out_absolute_errors_m": errors,
            "adjacent_sensor_separations_m_s2": separations,
        },
        "cells": cells,
        "inputs": {
            "contract": str(contract_path), "contract_sha256": sha256(contract_path),
            "tool_sha256": sha256(Path(__file__)), "source_hashes": EXPECTED_HASHES,
        },
        "execution": {
            "cpu_only": True, "formal_offset_sensor_reads": len(OFFSETS),
            "dynamic_steps": 0, "actor_calls": 0, "training": False,
            "robot_or_rdk": False, "p_value": None,
        },
        "authority": {
            "named_estimator_arm_preregistration_only": decision.startswith("SUPPORT_"),
            "training": False, "gpu_or_igpu": False, "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    rows = []
    for cell in cells:
        if cell["role"] == "ANCHOR":
            rows.append(
                f"| {cell['offset_m']:+.2f} | anchor | — | — | "
                f"{cell['anchor_max_abs_error_m_s2']:.9g} |"
            )
        else:
            rows.append(
                f"| {cell['offset_m']:+.2f} | held-out | {cell['estimate_m']:+.9f} | "
                f"{cell['absolute_offset_error_m']:.9g} | — |"
            )
    markdown.write_text(
        "# Ground-Up Torso-COM Reset Estimator Feasibility Result\n\n"
        f"status: `{status}`\n\n"
        f"decision: `{decision}`\n\n"
        "This is one deterministic reset curve (effective n=1), not a statistical or hardware-robustness result.\n\n"
        "| actual offset (m) | role | estimate (m) | absolute error (m) | anchor sensor error (m/s^2) |\n"
        "|---:|---|---:|---:|---:|\n" + "\n".join(rows) + "\n\n"
        f"All held-out signs correct: `{str(sign_correct).lower()}`. Strictly ordered: "
        f"`{str(strictly_ordered).lower()}`. Maximum error: `{maximum_error:.9g}` m. "
        f"Minimum adjacent sensor separation: `{minimum_separation:.9g}` m/s^2.\n\n"
        "A passing decision authorizes only a separate preregistration for the named estimator arm. "
        "It is not policy, training, deployment, or robot clearance.\n"
    )
    print(json.dumps({
        "status": status, "decision": decision,
        "maximum_error_m": maximum_error, "minimum_separation_m_s2": minimum_separation,
        "sign_correct": sign_correct, "strictly_ordered": strictly_ordered,
    }, sort_keys=True))
    return 0 if valid else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("contract", "study"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    if args.mode == "contract":
        return run_contract(args.output)
    if args.contract is None or args.markdown is None:
        parser.error("study mode requires --contract and --markdown")
    return run_study(args.contract, args.output, args.markdown)


if __name__ == "__main__":
    raise SystemExit(main())
