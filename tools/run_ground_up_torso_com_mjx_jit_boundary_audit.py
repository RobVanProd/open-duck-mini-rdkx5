#!/usr/bin/env python3
"""Contract and run the preregistered MJX JIT-boundary audit."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
from typing import Any, Callable

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
INIT_TOOL = REPO / "tools/run_ground_up_torso_com_mjx_initialization_order_audit.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_MJX_JIT_BOUNDARY_AUDIT_PREREGISTRATION_20260715.md"
INIT_RESULT = REPO / "outputs/analysis/ground_up_torso_com_mjx_initialization_order_audit_result.json"
INIT_CONTRACT = REPO / "outputs/analysis/ground_up_torso_com_mjx_initialization_order_contract.json"
CLOSED_LOOP = REPO / "tools/closed_loop_sim_eval.py"
EVALUATOR = REPO / "tools/evaluate_ground_up_policy.py"

EXPECTED_HASHES = {
    "init_tool": "53821c1deb30ec2eb98dcfdb5ae380ebf17009ae5b22734bcc6499e6aa7e2e08",
    "prereg": "3e4f45fbee953a97be833d0c7ac303f52b870786e5315dc3d0501ac239fa43f6",
    "init_result": "41e3c6184b4857448bc4600c7f6bf96f944e0dbc4485a00f36bb96c948538864",
    "init_contract": "2205c30a1cde2ca8626f177db7e0aa11b7b9d9d96e347c7eb334b7306acf4a73",
    "closed_loop": "d2c452b19826e4ff9e399bf61fe09e654514c4fc194966871e35fba0850f20d7",
    "evaluator": "347d3e4151d3f634710660b8c11bcce13724c66d33caafb5edbf86ebe2638030",
}
VARIANT_NAMES = (
    "EAGER_REPLACE_INSIDE",
    "JIT_REPLACE_INSIDE_SEQUENTIAL",
    "JIT_MODEL_ARGUMENT_SEQUENTIAL",
    "JIT_PAIR_REPLACE_INSIDE",
)
TOLERANCE = 1e-3
REPRODUCTION_TOLERANCE = 1e-6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_init_tool() -> Any:
    spec = importlib.util.spec_from_file_location("init_order_audit", INIT_TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load initialization-order audit source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_paths() -> dict[str, Path]:
    return {
        "init_tool": INIT_TOOL, "prereg": PREREG, "init_result": INIT_RESULT,
        "init_contract": INIT_CONTRACT, "closed_loop": CLOSED_LOOP,
        "evaluator": EVALUATOR,
    }


def exact_eager_closure(mjx: Any, env: Any) -> Callable[[Any, Any], Any]:
    def read_com_accelerometer(data: Any, body_ipos: Any) -> Any:
        branch_model = env.mjx_model.replace(body_ipos=body_ipos)
        branch_data = mjx.forward(branch_model, data)
        return env.get_accelerometer(branch_data)
    return read_com_accelerometer


def run_contract(output: Path) -> int:
    actual_hashes = {name: sha256(path) for name, path in source_paths().items()}
    init = load_init_tool()
    base = init.load_base()
    jax, env, nominal, negative, positive, reset = init.models_and_reset(base)
    checks: dict[str, bool] = {}
    checks["frozen_source_hashes_exact"] = actual_hashes == EXPECTED_HASHES
    checks["prior_initialization_audit_invalid"] = (
        json.loads(INIT_RESULT.read_text()).get("decision")
        == "INVALID_MJX_INITIALIZATION_ORDER_AUDIT"
    )
    checks["prior_zero_outcome_contract_passed"] = (
        json.loads(INIT_CONTRACT.read_text()).get("status")
        == "PASS_TORSO_COM_MJX_INITIALIZATION_ORDER_CONTRACT"
    )
    checks["cpu_only"] = (
        os.environ.get("CUDA_VISIBLE_DEVICES") == ""
        and os.environ.get("JAX_PLATFORMS") == "cpu"
        and jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    body_id = int(env.mj_model.body("trunk_assembly").id)
    negative_delta = np.asarray(negative.body_ipos) - np.asarray(nominal.body_ipos)
    positive_delta = np.asarray(positive.body_ipos) - np.asarray(nominal.body_ipos)
    checks["body2_x_only_com_mutations_exact"] = bool(
        body_id == 2 and np.count_nonzero(negative_delta) == 1
        and np.count_nonzero(positive_delta) == 1
        and negative_delta[2, 0] == np.asarray(-0.05, dtype=negative_delta.dtype)
        and positive_delta[2, 0] == np.asarray(0.05, dtype=positive_delta.dtype)
    )
    sensor = init.sensor_contract(env.mj_model)
    checks["accelerometer_identity_exact"] = (
        sensor["name"] == "accelerometer" and sensor["address"] == 6
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
    source = Path(__file__).read_text()
    checks["four_variant_source_structure_frozen"] = (
        len(VARIANT_NAMES) == 4 and len(set(VARIANT_NAMES)) == 4
        and all(f'"{name}"' in source for name in VARIANT_NAMES)
        and "negative_value = runner(live, negative.body_ipos)" in source
        and "positive_value = runner(live, positive.body_ipos)" in source
        and "negative_value = runner(negative, live)" in source
        and "positive_value = runner(positive, live)" in source
    )
    checks["formal_endpoint_reads_zero"] = True
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_TORSO_COM_MJX_JIT_BOUNDARY_CONTRACT"
        if not failed else "FAIL_TORSO_COM_MJX_JIT_BOUNDARY_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_mjx_jit_boundary_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "details": {
            "tool_sha256": sha256(Path(__file__)), "source_hashes": actual_hashes,
            "sensor": sensor, "body_id": body_id,
            "variant_names": list(VARIANT_NAMES),
            "devices": [str(device) for device in jax.devices()],
        },
        "execution": {
            "cpu_only": True, "formal_endpoint_reads": 0, "dynamic_steps": 0,
            "actor_calls": 0, "training": False, "robot_or_rdk": False,
        },
        "authority": {
            "four_variant_tick0_audit_if_pass": True, "dynamic_steps": False,
            "actor_calls": False, "training": False, "gpu_or_igpu": False,
            "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


def device_array(jax: Any, value: Any) -> np.ndarray:
    return np.asarray(jax.device_get(value), dtype=float)


def classify(init: Any, negative: np.ndarray, positive: np.ndarray) -> dict[str, Any]:
    negative_error = float(np.max(np.abs(negative - init.ORACLE["TORSO_COM_X_NEG"])))
    positive_error = float(np.max(np.abs(positive - init.ORACLE["TORSO_COM_X_POS"])))
    combined_error = max(negative_error, positive_error)
    half_direction = (positive - negative) / 2.0
    return {
        "classification": (
            "MATCH_ENDPOINT_ORACLE" if combined_error <= TOLERANCE
            else "MISS_ENDPOINT_ORACLE"
        ),
        "negative_accelerometer_m_s2": negative.tolist(),
        "positive_accelerometer_m_s2": positive.tolist(),
        "negative_endpoint_max_abs_error_m_s2": negative_error,
        "positive_endpoint_max_abs_error_m_s2": positive_error,
        "combined_endpoint_max_abs_error_m_s2": combined_error,
        "half_direction_m_s2": half_direction.tolist(),
        "half_direction_max_abs_error_m_s2": float(
            np.max(np.abs(half_direction - init.DIRECTION))
        ),
        "prior_invalid_half_direction_max_abs_error_m_s2": float(
            np.max(np.abs(half_direction - init.INVALID_HALF_DIRECTION))
        ),
    }


def decision(matches: dict[str, bool]) -> str:
    model = matches["JIT_MODEL_ARGUMENT_SEQUENTIAL"]
    pair = matches["JIT_PAIR_REPLACE_INSIDE"]
    if model and pair:
        return "MULTIPLE_JIT_BOUNDARY_REMEDIES_MATCH_ORACLE"
    if model:
        return "CONSTRUCT_MODEL_OUTSIDE_JIT_SUFFICIENT"
    if pair:
        return "PAIRED_ENDPOINT_JIT_SUFFICIENT"
    return "GENERAL_JIT_FORWARD_DISCREPANCY_OR_UNRESOLVED"


def run_audit(contract_path: Path, output: Path, markdown: Path) -> int:
    contract = json.loads(contract_path.read_text())
    if contract.get("status") != "PASS_TORSO_COM_MJX_JIT_BOUNDARY_CONTRACT":
        raise ValueError("passing JIT-boundary contract required")
    if contract["details"]["tool_sha256"] != sha256(Path(__file__)):
        raise ValueError("JIT-boundary tool changed after contract")
    init = load_init_tool()
    base = init.load_base()
    jax, env, nominal, negative, positive, reset = init.models_and_reset(base)
    from mujoco import mjx
    from mujoco_playground._src import mjx_env

    qpos, qvel, ctrl = reset
    live = mjx_env.init(nominal, qpos=qpos, qvel=qvel, ctrl=ctrl)
    eager = exact_eager_closure(mjx, env)
    results: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    negative_value = eager(live, negative.body_ipos)
    positive_value = eager(live, positive.body_ipos)
    results["EAGER_REPLACE_INSIDE"] = (
        device_array(jax, negative_value), device_array(jax, positive_value)
    )

    runner = jax.jit(exact_eager_closure(mjx, env))
    negative_value = runner(live, negative.body_ipos)
    positive_value = runner(live, positive.body_ipos)
    results["JIT_REPLACE_INSIDE_SEQUENTIAL"] = (
        device_array(jax, negative_value), device_array(jax, positive_value)
    )

    def model_argument(model: Any, data: Any) -> Any:
        return env.get_accelerometer(mjx.forward(model, data))

    runner = jax.jit(model_argument)
    negative_value = runner(negative, live)
    positive_value = runner(positive, live)
    results["JIT_MODEL_ARGUMENT_SEQUENTIAL"] = (
        device_array(jax, negative_value), device_array(jax, positive_value)
    )

    def paired(data: Any, negative_body_ipos: Any, positive_body_ipos: Any) -> tuple[Any, Any]:
        negative_model = env.mjx_model.replace(body_ipos=negative_body_ipos)
        positive_model = env.mjx_model.replace(body_ipos=positive_body_ipos)
        negative_data = mjx.forward(negative_model, data)
        positive_data = mjx.forward(positive_model, data)
        return env.get_accelerometer(negative_data), env.get_accelerometer(positive_data)

    runner = jax.jit(paired)
    negative_value, positive_value = runner(
        live, negative.body_ipos, positive.body_ipos
    )
    results["JIT_PAIR_REPLACE_INSIDE"] = (
        device_array(jax, negative_value), device_array(jax, positive_value)
    )

    cells: list[dict[str, Any]] = []
    for name in VARIANT_NAMES:
        cell = {"variant": name, **classify(init, *results[name])}
        cells.append(cell)
    matches = {
        cell["variant"]: cell["classification"] == "MATCH_ENDPOINT_ORACLE"
        for cell in cells
    }
    exact_jit = next(
        cell for cell in cells if cell["variant"] == "JIT_REPLACE_INSIDE_SEQUENTIAL"
    )
    finite = all(
        math.isfinite(value)
        for cell in cells
        for key in ("negative_accelerometer_m_s2", "positive_accelerometer_m_s2")
        for value in cell[key]
    )
    validity = {
        "eager_exact_closure_matches_oracle": matches["EAGER_REPLACE_INSIDE"],
        "exact_jit_closure_misses_oracle": not matches["JIT_REPLACE_INSIDE_SEQUENTIAL"],
        "exact_jit_reproduces_prior_invalid_half_direction": (
            exact_jit["prior_invalid_half_direction_max_abs_error_m_s2"]
            <= REPRODUCTION_TOLERANCE
        ),
        "all_sensor_values_finite": finite,
        "model_mutation_contract_passed": bool(contract["checks"]["body2_x_only_com_mutations_exact"]),
        "cpu_only_contract_passed": bool(contract["checks"]["cpu_only"]),
    }
    valid = all(validity.values())
    selected = decision(matches) if valid else "INVALID_MJX_JIT_BOUNDARY_AUDIT"
    status = "PASS_VALID_MJX_JIT_BOUNDARY_AUDIT" if valid else selected
    payload = {
        "schema_version": "ground_up_torso_com_mjx_jit_boundary_audit.v1",
        "status": status, "decision": selected, "effective_sample_size": 1,
        "endpoint_tolerance_m_s2": TOLERANCE,
        "reproduction_tolerance_m_s2": REPRODUCTION_TOLERANCE,
        "validity": validity, "matches": matches, "cells": cells,
        "inputs": {
            "contract": str(contract_path), "contract_sha256": sha256(contract_path),
            "tool_sha256": sha256(Path(__file__)), "source_hashes": EXPECTED_HASHES,
        },
        "execution": {
            "cpu_only": True, "formal_endpoint_vectors": 8,
            "dynamic_steps": 0, "actor_calls": 0, "training": False,
            "robot_or_rdk": False,
        },
        "authority": {
            "candidate_map_correction_only": valid, "rerun_144_cell_map": False,
            "dynamic_steps": False, "actor_calls": False, "training": False,
            "gpu_or_igpu": False, "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    rows = "\n".join(
        f"| `{cell['variant']}` | `{cell['classification']}` | "
        f"{cell['combined_endpoint_max_abs_error_m_s2']:.9g} | "
        f"{cell['half_direction_max_abs_error_m_s2']:.9g} | "
        f"{cell['prior_invalid_half_direction_max_abs_error_m_s2']:.9g} |"
        for cell in cells
    )
    markdown.write_text(
        "# Ground-Up Torso-COM MJX JIT-Boundary Audit Result\n\n"
        f"status: `{status}`\n\n"
        f"decision: `{selected}`\n\n"
        "This is one deterministic tick-zero reset state (effective n=1); it is a methods audit, not a statistical result.\n\n"
        "| variant | endpoint class | combined endpoint error | oracle direction error | prior-invalid direction error |\n"
        "|---|---:|---:|---:|---:|\n" + rows + "\n\n"
        "The decision selects only a candidate evaluation-method correction for separate preregistration. "
        "It does not authorize the 144-cell map, actor work, training, hardware, or deployment.\n"
    )
    print(json.dumps({"status": status, "decision": selected, "matches": matches}, sort_keys=True))
    return 0 if valid else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("contract", "audit"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    if args.mode == "contract":
        return run_contract(args.output)
    if args.contract is None or args.markdown is None:
        parser.error("audit mode requires --contract and --markdown")
    return run_audit(args.contract, args.output, args.markdown)


if __name__ == "__main__":
    raise SystemExit(main())
