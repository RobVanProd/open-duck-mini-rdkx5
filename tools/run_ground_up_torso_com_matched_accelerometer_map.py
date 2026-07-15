#!/usr/bin/env python3
"""Contract and run the preregistered matched torso-COM accelerometer map."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
BASE_TOOL = REPO / "tools/run_ground_up_torso_com_signed_response.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_MATCHED_ACCELEROMETER_MAP_PREREGISTRATION_20260715.md"
CROSSED_RESULT = REPO / "outputs/analysis/ground_up_torso_com_crossed_phase_result.json"
SIGNED_RESULT = REPO / "outputs/analysis/ground_up_torso_com_signed_response_result.json"

EXPECTED = {
    "base_tool": "6e25285e9b12b8763aac0723e16c6d5ca63cac9e1956205fd44bdff714179b4d",
    "prereg": "b0eff1cb6159077f9f6177a71d7b9073fa824322e2ee15365e280b55effd97e2",
    "crossed_result": "9c0823c7fce7bd409acbc53176c412dc45863f9c9ebaa27fa00a4f4597984ef0",
    "signed_result": "8c09ada8ce392c09fcee3cd9e7f449be5b1c50ca28b1640a4a3103755cc3b814",
}
DIRECTION = np.asarray(
    [1.1654748916625977, 0.11948448419570923, 1.0919904708862305],
    dtype=float,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("signed_response_base", BASE_TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load signed-response evaluator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_sources(base: Any) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    actual = {
        "base_tool": sha256(BASE_TOOL), "prereg": sha256(PREREG),
        "crossed_result": sha256(CROSSED_RESULT),
        "signed_result": sha256(SIGNED_RESULT),
    }
    if actual != EXPECTED:
        raise ValueError(f"matched accelerometer frozen-source mismatch: {actual}")
    crossed = json.loads(CROSSED_RESULT.read_text())
    signed = json.loads(SIGNED_RESULT.read_text())
    if crossed.get("decision") != "CROSSED_LOCALIZATION_UNRESOLVED_NO_FAMILY_SELECTED":
        raise ValueError("crossed source decision mismatch")
    if signed.get("decision") != "MIXED_SIGN_NO_POLICY_FAMILY_SELECTED":
        raise ValueError("signed source decision mismatch")
    _manifest, _full_result, selected = base.load_sources()
    if len(selected) != 36:
        raise ValueError(f"expected 36 traces, got {len(selected)}")
    return crossed, signed, selected


def sensor_contract(model: Any) -> dict[str, Any]:
    sensor = model.sensor("accelerometer")
    sensor_id = int(sensor.id)
    address = int(model.sensor_adr[sensor_id])
    dimension = int(model.sensor_dim[sensor_id])
    object_id = int(model.sensor_objid[sensor_id])
    site_name = model.site(object_id).name
    return {
        "name": sensor.name, "id": sensor_id, "address": address,
        "dimension": dimension, "object_id": object_id, "site_name": site_name,
    }


def contract(output: Path) -> int:
    base = load_base()
    _crossed, _signed, selected = load_sources(base)
    jax, _mujoco, env = base.initialize_environment()

    checks: dict[str, bool] = {}
    checks["cpu_only"] = jax.default_backend() == "cpu" and all(
        device.platform == "cpu" for device in jax.devices()
    )
    sensor = sensor_contract(env.mj_model)
    checks["accelerometer_name_address_dimension_exact"] = (
        sensor["name"] == "accelerometer" and sensor["address"] == 6
        and sensor["dimension"] == 3 and sensor["site_name"] == "imu"
    )
    planned: set[tuple[Any, ...]] = set()
    schemas_valid = True
    finite_states = True
    home = np.asarray(env._default_actuator, dtype=float)
    init_q = np.asarray(env._init_q, dtype=float)
    for item in selected:
        rows = base.load_trace(item)
        key = f"{item['arm']}_{item['step']}"
        for tick in base.FORK_TICKS:
            qpos, qvel, ctrl = base.source_state(rows, tick, init_q, home)
            schemas_valid = schemas_valid and (
                qpos.shape == (31,) and qvel.shape == (30,) and ctrl.shape == (14,)
                and len(rows[tick]["obs_state"]) == 115
            )
            finite_states = finite_states and all(
                np.isfinite(array).all() for array in (qpos, qvel, ctrl)
            )
            planned.add((
                key, item["fit"], round(float(item["command_x"]), 3), int(tick)
            ))
    checks["selected_36_trace_schemas_exact"] = len(selected) == 36 and schemas_valid
    checks["complete_144_state_index"] = len(planned) == 144
    checks["all_source_states_finite"] = finite_states

    base_ipos = np.asarray(env.mj_model.body_ipos).copy()
    negative = base.model_with_com(_mujoco, env.mj_model, -0.05)
    positive = base.model_with_com(_mujoco, env.mj_model, 0.05)
    negative_delta = np.asarray(negative.body_ipos) - base_ipos
    positive_delta = np.asarray(positive.body_ipos) - base_ipos
    checks["body2_x_only_com_mutations_exact"] = (
        np.count_nonzero(negative_delta) == 1
        and np.count_nonzero(positive_delta) == 1
        and abs(float(negative_delta[2, 0]) + 0.05) <= 1e-12
        and abs(float(positive_delta[2, 0]) - 0.05) <= 1e-12
        and np.array_equal(np.asarray(env.mj_model.body_ipos), base_ipos)
    )
    checks["formal_sensor_cells_not_executed"] = True

    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_TORSO_COM_MATCHED_ACCELEROMETER_CONTRACT"
        if not failed else "FAIL_TORSO_COM_MATCHED_ACCELEROMETER_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_matched_accelerometer_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "details": {
            "tool_sha256": sha256(Path(__file__)), "selected_traces": len(selected),
            "planned_cells": len(planned), "sensor": sensor,
            "devices": [str(device) for device in jax.devices()],
            "source_hashes": EXPECTED,
        },
        "execution": {
            "cpu_only": True, "formal_cells_executed": 0,
            "dynamic_steps_executed": 0, "actor_calls_executed": 0,
            "training": False, "robot_or_rdk": False,
        },
        "authority": {
            "formal_144_cell_static_sensor_map_if_pass": True,
            "dynamic_steps": False, "actor_forks": False, "training": False,
            "gpu_or_igpu": False, "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


def forward_accelerometer(
    mujoco: Any, model: Any, qpos: np.ndarray, qvel: np.ndarray,
    ctrl: np.ndarray, address: int,
) -> np.ndarray:
    data = mujoco.MjData(model)
    mujoco.mj_setConst(model, data)
    data.qpos[:] = qpos
    data.qvel[:] = qvel
    data.ctrl[:] = ctrl
    mujoco.mj_forward(model, data)
    return np.asarray(data.sensordata[address : address + 3], dtype=float).copy()


def classify(norm_h: float, cosine: float | None, center_ratio: float | None) -> str:
    if norm_h < 0.25 * float(np.linalg.norm(DIRECTION)):
        return "WEAK_SIGNAL"
    if center_ratio is None or center_ratio > 0.25:
        return "NONLINEAR_CENTER"
    if cosine is None or cosine < 0.80:
        return "DIRECTION_ROTATED"
    return "FIXED_DIRECTION_COMPATIBLE"


def counts(cells: list[dict[str, Any]]) -> dict[str, int]:
    names = (
        "WEAK_SIGNAL", "NONLINEAR_CENTER", "DIRECTION_ROTATED",
        "FIXED_DIRECTION_COMPATIBLE",
    )
    return {name: sum(cell["classification"] == name for cell in cells) for name in names}


def study(contract_path: Path, output: Path, markdown: Path) -> int:
    contract_payload = json.loads(contract_path.read_text())
    if contract_payload.get("status") != "PASS_TORSO_COM_MATCHED_ACCELEROMETER_CONTRACT":
        raise ValueError("passing matched-accelerometer contract required")
    if contract_payload["details"]["tool_sha256"] != sha256(Path(__file__)):
        raise ValueError("matched-accelerometer tool changed after contract")

    base = load_base()
    _crossed, _signed, selected = load_sources(base)
    _jax, mujoco, env = base.initialize_environment()
    sensor = sensor_contract(env.mj_model)
    address = int(sensor["address"])
    home = np.asarray(env._default_actuator, dtype=float)
    init_q = np.asarray(env._init_q, dtype=float)
    direction_norm = float(np.linalg.norm(DIRECTION))

    cells: list[dict[str, Any]] = []
    for trace_index, item in enumerate(selected, start=1):
        rows = base.load_trace(item)
        key = f"{item['arm']}_{item['step']}"
        print(
            f"[{trace_index}/36] {key} {item['fit']} x={item['command_x']}",
            flush=True,
        )
        for tick in base.FORK_TICKS:
            qpos, qvel, ctrl = base.source_state(rows, tick, init_q, home)
            nominal_model = copy.copy(env.mj_model)
            negative_model = base.model_with_com(mujoco, env.mj_model, -0.05)
            positive_model = base.model_with_com(mujoco, env.mj_model, 0.05)
            nominal = forward_accelerometer(
                mujoco, nominal_model, qpos, qvel, ctrl, address
            )
            negative = forward_accelerometer(
                mujoco, negative_model, qpos, qvel, ctrl, address
            )
            positive = forward_accelerometer(
                mujoco, positive_model, qpos, qvel, ctrl, address
            )
            saved = np.asarray(rows[tick]["obs_state"][3:6], dtype=float)
            half_direction = (positive - negative) / 2.0
            center_residual = (positive + negative) / 2.0 - nominal
            norm_h = float(np.linalg.norm(half_direction))
            norm_r = float(np.linalg.norm(center_residual))
            cosine = (
                float(np.dot(half_direction, DIRECTION) / (norm_h * direction_norm))
                if norm_h > 0.0 else None
            )
            magnitude_ratio = norm_h / direction_norm
            center_ratio = norm_r / norm_h if norm_h > 0.0 else None
            classification = classify(norm_h, cosine, center_ratio)
            cells.append({
                "policy": key, "arm": item["arm"], "step": int(item["step"]),
                "fit": item["fit"], "command_x": float(item["command_x"]),
                "tick": int(tick), "classification": classification,
                "accelerometer_nominal_m_s2": nominal.tolist(),
                "accelerometer_negative_m_s2": negative.tolist(),
                "accelerometer_positive_m_s2": positive.tolist(),
                "saved_observation_accelerometer_m_s2": saved.tolist(),
                "physical_half_direction_m_s2": half_direction.tolist(),
                "center_residual_m_s2": center_residual.tolist(),
                "half_direction_norm_m_s2": norm_h,
                "center_residual_norm_m_s2": norm_r,
                "direction_cosine_to_reset": cosine,
                "magnitude_ratio_to_reset": magnitude_ratio,
                "center_ratio": center_ratio,
                "nominal_saved_max_abs_error_m_s2": float(np.max(np.abs(nominal - saved))),
                "tick0_direction_max_abs_error_m_s2": (
                    float(np.max(np.abs(half_direction - DIRECTION))) if tick == 0 else None
                ),
            })
    if len(cells) != 144:
        raise ValueError(f"matched accelerometer cell count mismatch: {len(cells)}")

    nominal_error = max(cell["nominal_saved_max_abs_error_m_s2"] for cell in cells)
    tick0_error = max(
        cell["tick0_direction_max_abs_error_m_s2"]
        for cell in cells if cell["tick"] == 0
    )
    finite = all(
        np.isfinite(np.asarray(cell[key], dtype=float)).all()
        for cell in cells
        for key in (
            "accelerometer_nominal_m_s2", "accelerometer_negative_m_s2",
            "accelerometer_positive_m_s2", "physical_half_direction_m_s2",
            "center_residual_m_s2",
        )
    )
    validity = {
        "all_values_finite": finite,
        "nominal_saved_max_abs_error_m_s2": nominal_error,
        "nominal_saved_tolerance_m_s2": 1e-3,
        "tick0_direction_max_abs_error_m_s2": tick0_error,
        "tick0_direction_tolerance_m_s2": 1e-3,
        "valid": finite and nominal_error <= 1e-3 and tick0_error <= 1e-3,
    }

    tick_summaries = {}
    for tick in base.FORK_TICKS:
        subset = [cell for cell in cells if cell["tick"] == tick]
        row_counts = counts(subset)
        fixed_tick = (
            row_counts["FIXED_DIRECTION_COMPATIBLE"] >= 27
            and row_counts["WEAK_SIGNAL"] <= 3
            and row_counts["NONLINEAR_CENTER"] <= 3
            and row_counts["DIRECTION_ROTATED"] <= 3
        )
        tick_summaries[str(tick)] = {
            "cells": len(subset), "counts": row_counts,
            "classification": "FIXED_COMPATIBLE_TICK" if fixed_tick else "NON_FIXED_TICK",
            "half_direction_norm_range_m_s2": [
                min(cell["half_direction_norm_m_s2"] for cell in subset),
                max(cell["half_direction_norm_m_s2"] for cell in subset),
            ],
            "direction_cosine_range": [
                min(cell["direction_cosine_to_reset"] for cell in subset),
                max(cell["direction_cosine_to_reset"] for cell in subset),
            ],
            "center_ratio_range": [
                min(cell["center_ratio"] for cell in subset),
                max(cell["center_ratio"] for cell in subset),
            ],
        }

    if not validity["valid"]:
        status = "INVALID_MATCHED_ACCELEROMETER_READBACK"
        decision = "INVALID_MATCHED_ACCELEROMETER_READBACK"
    else:
        status = "PASS_TORSO_COM_MATCHED_ACCELEROMETER_MAP_COMPLETE"
        if all(
            tick_summaries[str(tick)]["classification"] == "FIXED_COMPATIBLE_TICK"
            for tick in base.FORK_TICKS
        ):
            decision = "SUPPORT_PREREGISTERED_FINE_GRAINED_COUPLING_MAP"
        elif (
            tick_summaries["0"]["classification"] == "FIXED_COMPATIBLE_TICK"
            and all(
                tick_summaries[str(tick)]["counts"]["WEAK_SIGNAL"] >= 27
                for tick in (24, 32, 40)
            )
        ):
            decision = "SUPPORT_PREREGISTERED_TEMPORAL_SENSOR_INFORMATION_STUDY"
        elif (
            tick_summaries["0"]["classification"] == "FIXED_COMPATIBLE_TICK"
            and any(
                tick_summaries[str(tick)]["counts"]["DIRECTION_ROTATED"]
                + tick_summaries[str(tick)]["counts"]["NONLINEAR_CENTER"] >= 18
                for tick in (24, 32, 40)
            )
        ):
            decision = "SUPPORT_PREREGISTERED_MATCHED_SENSOR_ACTOR_RESPONSE_STUDY"
        else:
            decision = "MATCHED_ACCELEROMETER_MAP_UNRESOLVED_NO_FAMILY_SELECTED"

    payload = {
        "schema_version": "ground_up_torso_com_matched_accelerometer_map.v1",
        "status": status, "decision": decision, "validity": validity,
        "aggregate_counts": counts(cells), "tick_summaries": tick_summaries,
        "cells": cells,
        "sources": {
            "contract_sha256": sha256(contract_path),
            "crossed_result_sha256": sha256(CROSSED_RESULT),
            "signed_result_sha256": sha256(SIGNED_RESULT),
            "base_tool_sha256": sha256(BASE_TOOL),
        },
        "thresholds": {
            "weak_signal_ratio": 0.25, "center_ratio_maximum": 0.25,
            "direction_cosine_minimum": 0.80, "fixed_tick_minimum_cells": 27,
            "fixed_tick_maximum_each_other_class": 3,
            "nominal_readback_tolerance_m_s2": 1e-3,
            "tick0_anchor_tolerance_m_s2": 1e-3,
        },
        "execution": {
            "cpu_only": True, "formal_cells": len(cells),
            "mj_forward_calls": len(cells) * 3, "dynamic_steps": 0,
            "actor_calls": 0, "training": False, "robot_or_rdk": False,
            "p_value": None,
        },
        "authority": {
            "next_preregistration_only": True, "dynamic_steps": False,
            "actor_forks": False, "training": False, "gpu_or_igpu": False,
            "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Ground-Up Torso-COM Matched Accelerometer-Map Result", "",
        f"status: `{status}`", f"decision: `{decision}`", "",
        "| tick | fixed compatible | weak | nonlinear center | rotated | tick class |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for tick in base.FORK_TICKS:
        row = tick_summaries[str(tick)]
        c = row["counts"]
        lines.append(
            f"| {tick} | {c['FIXED_DIRECTION_COMPATIBLE']} | {c['WEAK_SIGNAL']} | "
            f"{c['NONLINEAR_CENTER']} | {c['DIRECTION_ROTATED']} | "
            f"`{row['classification']}` |"
        )
    lines.extend([
        "", "Validity:", "",
        f"- nominal-vs-saved maximum error: {nominal_error:.17g} m/s^2;",
        f"- tick-zero direction maximum error: {tick0_error:.17g} m/s^2;",
        f"- all values finite: {str(finite).lower()}.", "",
        "No p-value or training reward is used. The result authorizes at most "
        "the next read-only preregistration named by the frozen decision.", "",
    ])
    markdown.write_text("\n".join(lines))
    print(json.dumps({
        "status": status, "decision": decision,
        "aggregate": payload["aggregate_counts"], "validity": validity,
    }, sort_keys=True))
    return 0 if status == "PASS_TORSO_COM_MATCHED_ACCELEROMETER_MAP_COMPLETE" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("contract", "study"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.mode == "contract":
        return contract(args.output)
    if args.contract is None or args.markdown is None:
        parser.error("study mode requires --contract and --markdown")
    return study(args.contract, args.output, args.markdown)


if __name__ == "__main__":
    raise SystemExit(main())
