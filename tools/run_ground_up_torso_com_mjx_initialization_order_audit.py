#!/usr/bin/env python3
"""Contract and run the preregistered MJX initialization-order audit."""

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
BASE_TOOL = REPO / "tools/run_ground_up_torso_com_signed_response.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_MJX_INITIALIZATION_ORDER_AUDIT_PREREGISTRATION_20260715.md"
MANIFEST = REPO / "outputs/analysis/ground_up_torso_com_full_obs_replay_manifest.json"
INVALID_RESULT = REPO / "outputs/analysis/ground_up_torso_com_exact_mjx_accelerometer_map_result.json"

EXPECTED_HASHES = {
    "base_tool": "6e25285e9b12b8763aac0723e16c6d5ca63cac9e1956205fd44bdff714179b4d",
    "prereg": "065e53d7be27c41b3c0c40c3cadcf11b6f7af9320a5a569b7c6c07b7e2a55aeb",
    "manifest": "ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07",
    "invalid_result": "23b4ad8444fc4eaa9dd83dcffb64b3b070431f3b424a83d71bf9a5b2a5ffcf3b",
}
TRACE_HASHES = {
    "NOMINAL": "e4a2452df4beaa703553bcb6b3f4e206d9e104258a48212ffe2d4f4541f1dd7c",
    "TORSO_COM_X_NEG": "e8ce3e5c559fcce85937c35118b6d55272ede022fd9c344dd033b5a5f058184d",
    "TORSO_COM_X_POS": "f18442447991fdd5c2be1caf0a08a966ec35e8b65173f86c518185b21a641c53",
}
ORACLE = {
    "NOMINAL": np.asarray([-11.879271507263184, 0.8971166610717773, 29.650177001953125]),
    "TORSO_COM_X_NEG": np.asarray([-13.04679012298584, 0.7727481126785278, 28.672449111938477]),
    "TORSO_COM_X_POS": np.asarray([-10.715840339660645, 1.0117170810699463, 30.856430053710938]),
}
DIRECTION = np.asarray([1.1654748916625977, 0.11948448419570923, 1.0919904708862305])
INVALID_HALF_DIRECTION = np.asarray([1.1723289489746094, 0.11886221170425415, 1.0786018371582031])
TOLERANCE = 1e-3
REPRODUCTION_TOLERANCE = 1e-6
VARIANT_NAMES = (
    "FRESH_INIT_REFERENCE",
    "LIVE_FORWARD_REPRODUCTION",
    "LIVE_ZERO_WARMSTART",
    "LIVE_FRESH_IMPL",
    "LIVE_ZERO_WARMSTART_FRESH_IMPL",
    "FRESH_PRIMARY_COPY",
    "FRESH_PRIMARY_COPY_ZERO_WARMSTART",
)
PRIMARY_FIELDS = (
    "time", "qpos", "qvel", "act", "history", "qacc_warmstart",
    "plugin_state", "ctrl", "qfrc_applied", "xfrc_applied", "eq_active",
    "mocap_pos", "mocap_quat", "userdata",
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
        raise RuntimeError("cannot load signed-response environment source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_trace_paths() -> dict[str, Path]:
    manifest = json.loads(MANIFEST.read_text())
    selected: dict[str, Path] = {}
    for item in manifest["traces"]:
        if (
            item["arm"] == "A05_DIRECT" and int(item["step"]) == 1003520
            and item["fit"] == "p30" and round(float(item["command_x"]), 3) == 0.074
        ):
            condition = item["condition"]
            if condition in TRACE_HASHES:
                if item["sha256"] != TRACE_HASHES[condition]:
                    raise ValueError(f"manifest trace hash mismatch: {condition}")
                selected[condition] = Path(item["path"])
    if set(selected) != set(TRACE_HASHES):
        raise ValueError(f"frozen trace identity mismatch: {sorted(selected)}")
    return selected


def sensor_contract(model: Any) -> dict[str, Any]:
    sensor = model.sensor("accelerometer")
    sensor_id = int(sensor.id)
    object_id = int(model.sensor_objid[sensor_id])
    return {
        "name": sensor.name,
        "id": sensor_id,
        "address": int(model.sensor_adr[sensor_id]),
        "dimension": int(model.sensor_dim[sensor_id]),
        "object_id": object_id,
        "site_name": model.site(object_id).name,
    }


def models_and_reset(base: Any) -> tuple[Any, Any, Any, Any, Any, Any]:
    jax, _mujoco, env = base.initialize_environment()
    jp = jax.numpy
    nominal = env.mjx_model
    body_id = int(env.mj_model.body("trunk_assembly").id)
    negative_ipos = nominal.body_ipos.at[body_id, 0].add(-0.05)
    positive_ipos = nominal.body_ipos.at[body_id, 0].add(0.05)
    negative = nominal.replace(body_ipos=negative_ipos)
    positive = nominal.replace(body_ipos=positive_ipos)
    qpos = jp.asarray(env._init_q)
    qvel = jp.zeros(nominal.nv)
    ctrl = jp.asarray(env._default_actuator)
    return jax, env, nominal, negative, positive, (qpos, qvel, ctrl)


def run_contract(output: Path) -> int:
    base = load_base()
    source_paths = {
        "base_tool": BASE_TOOL, "prereg": PREREG, "manifest": MANIFEST,
        "invalid_result": INVALID_RESULT,
    }
    actual_hashes = {name: sha256(path) for name, path in source_paths.items()}
    traces = frozen_trace_paths()
    trace_hashes = {name: sha256(path) for name, path in traces.items()}
    jax, env, nominal, negative, positive, reset = models_and_reset(base)
    from mujoco import mjx

    checks: dict[str, bool] = {}
    checks["frozen_source_hashes_exact"] = actual_hashes == EXPECTED_HASHES
    checks["frozen_trace_hashes_exact"] = trace_hashes == TRACE_HASHES
    checks["cpu_only"] = (
        os.environ.get("CUDA_VISIBLE_DEVICES") == ""
        and os.environ.get("JAX_PLATFORMS") == "cpu"
        and jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    body_id = int(env.mj_model.body("trunk_assembly").id)
    base_ipos = np.asarray(nominal.body_ipos)
    negative_delta = np.asarray(negative.body_ipos) - base_ipos
    positive_delta = np.asarray(positive.body_ipos) - base_ipos
    checks["trunk_body2_massive"] = body_id == 2 and float(env.mj_model.body_mass[body_id]) > 0.0
    checks["body2_x_only_com_mutations_exact"] = bool(
        np.count_nonzero(negative_delta) == 1 and np.count_nonzero(positive_delta) == 1
        and negative_delta[2, 0] == np.asarray(-0.05, dtype=negative_delta.dtype)
        and positive_delta[2, 0] == np.asarray(0.05, dtype=positive_delta.dtype)
    )
    sensor = sensor_contract(env.mj_model)
    checks["accelerometer_identity_exact"] = (
        sensor["name"] == "accelerometer" and sensor["address"] == 6
        and sensor["dimension"] == 3 and sensor["site_name"] == "imu"
    )
    qpos, qvel, ctrl = reset
    checks["home_reset_shapes_finite"] = (
        np.asarray(qpos).shape == (int(nominal.nq),)
        and np.asarray(qvel).shape == (int(nominal.nv),)
        and np.asarray(ctrl).shape == (int(nominal.nu),)
        and all(np.isfinite(np.asarray(value)).all() for value in reset)
    )
    data = mjx.make_data(nominal)
    data_fields = set(data.__dataclass_fields__)
    checks["all_frozen_mjx_data_fields_available"] = (
        set(PRIMARY_FIELDS).issubset(data_fields)
        and {"_impl", "sensordata"}.issubset(data_fields)
    )
    source = Path(__file__).read_text()
    checks["seven_variants_and_field_list_frozen_in_source"] = (
        len(VARIANT_NAMES) == 7 and len(set(VARIANT_NAMES)) == 7
        and all(f'"{name}"' in source for name in VARIANT_NAMES)
        and all(f'"{field}"' in source for field in PRIMARY_FIELDS)
    )
    checks["formal_variant_sensor_reads_zero"] = True
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_TORSO_COM_MJX_INITIALIZATION_ORDER_CONTRACT"
        if not failed else "FAIL_TORSO_COM_MJX_INITIALIZATION_ORDER_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_mjx_initialization_order_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "details": {
            "tool_sha256": sha256(Path(__file__)), "source_hashes": actual_hashes,
            "trace_hashes": trace_hashes, "sensor": sensor,
            "body_id": body_id, "body_mass_kg": float(env.mj_model.body_mass[body_id]),
            "data_fields": sorted(data_fields), "variant_names": list(VARIANT_NAMES),
            "primary_fields": list(PRIMARY_FIELDS),
            "devices": [str(device) for device in jax.devices()],
        },
        "execution": {
            "cpu_only": True, "formal_variant_sensor_reads": 0,
            "dynamic_steps": 0, "actor_calls": 0, "training": False,
            "robot_or_rdk": False,
        },
        "authority": {
            "seven_variant_tick0_audit_if_pass": True, "dynamic_steps": False,
            "actor_calls": False, "training": False, "gpu_or_igpu": False,
            "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


def read_accelerometer(jax: Any, data: Any, address: int) -> np.ndarray:
    return np.asarray(jax.device_get(data.sensordata[address : address + 3]), dtype=float)


def fresh_branch_data(mjx: Any, model: Any, reset: tuple[Any, Any, Any]) -> Any:
    qpos, qvel, ctrl = reset
    data = mjx.make_data(model).replace(qpos=qpos, qvel=qvel, ctrl=ctrl)
    return mjx.forward(model, data)


def branch_variants(
    mjx: Any, mjx_env: Any, model: Any, live: Any,
    reset: tuple[Any, Any, Any],
) -> dict[str, Any]:
    qpos, qvel, ctrl = reset
    fresh = mjx.make_data(model)
    copied = {field: getattr(live, field) for field in PRIMARY_FIELDS}
    primary = fresh.replace(**copied)
    return {
        "FRESH_INIT_REFERENCE": mjx_env.init(model, qpos=qpos, qvel=qvel, ctrl=ctrl),
        "LIVE_FORWARD_REPRODUCTION": mjx.forward(model, live),
        "LIVE_ZERO_WARMSTART": mjx.forward(
            model, live.replace(qacc_warmstart=live.qacc_warmstart * 0)
        ),
        "LIVE_FRESH_IMPL": mjx.forward(model, live.replace(_impl=fresh._impl)),
        "LIVE_ZERO_WARMSTART_FRESH_IMPL": mjx.forward(
            model,
            live.replace(
                qacc_warmstart=live.qacc_warmstart * 0, _impl=fresh._impl
            ),
        ),
        "FRESH_PRIMARY_COPY": mjx.forward(model, primary),
        "FRESH_PRIMARY_COPY_ZERO_WARMSTART": mjx.forward(
            model, primary.replace(qacc_warmstart=primary.qacc_warmstart * 0)
        ),
    }


def select_decision(matches: dict[str, bool]) -> str:
    if matches["LIVE_FORWARD_REPRODUCTION"]:
        return "INVALID_LIVE_REPRODUCTION_MISMATCH"
    warm = matches["LIVE_ZERO_WARMSTART"]
    impl = matches["LIVE_FRESH_IMPL"]
    if warm != impl:
        return "QACC_WARMSTART_SUFFICIENT" if warm else "MJX_IMPL_SUFFICIENT"
    if not warm and matches["LIVE_ZERO_WARMSTART_FRESH_IMPL"]:
        return "WARMSTART_AND_IMPL_JOINTLY_SUFFICIENT"
    if warm and impl:
        return "MULTIPLE_SINGLE_FIELD_RESETS_SUFFICIENT"
    if matches["FRESH_PRIMARY_COPY"] or matches["FRESH_PRIMARY_COPY_ZERO_WARMSTART"]:
        return "FRESH_DERIVED_DATA_REQUIRED"
    return "FULL_FRESH_INITIALIZATION_REQUIRED_OR_UNRESOLVED"


def run_audit(contract_path: Path, output: Path, markdown: Path) -> int:
    contract = json.loads(contract_path.read_text())
    if contract.get("status") != "PASS_TORSO_COM_MJX_INITIALIZATION_ORDER_CONTRACT":
        raise ValueError("passing initialization-order contract required")
    if contract["details"]["tool_sha256"] != sha256(Path(__file__)):
        raise ValueError("audit tool changed after contract")

    base = load_base()
    jax, env, nominal, negative, positive, reset = models_and_reset(base)
    from mujoco import mjx
    from mujoco_playground._src import mjx_env

    sensor = sensor_contract(env.mj_model)
    address = int(sensor["address"])
    fresh_nominal = fresh_branch_data(mjx, nominal, reset)
    live_nominal = fresh_branch_data(mjx, nominal, reset)
    nominal_value = read_accelerometer(jax, fresh_nominal, address)
    branch_data = {
        "TORSO_COM_X_NEG": branch_variants(mjx, mjx_env, negative, live_nominal, reset),
        "TORSO_COM_X_POS": branch_variants(mjx, mjx_env, positive, live_nominal, reset),
    }
    cells: list[dict[str, Any]] = []
    matches: dict[str, bool] = {}
    finite = bool(np.isfinite(nominal_value).all())
    for name in VARIANT_NAMES:
        negative_value = read_accelerometer(jax, branch_data["TORSO_COM_X_NEG"][name], address)
        positive_value = read_accelerometer(jax, branch_data["TORSO_COM_X_POS"][name], address)
        finite = finite and bool(np.isfinite(negative_value).all() and np.isfinite(positive_value).all())
        negative_error = float(np.max(np.abs(negative_value - ORACLE["TORSO_COM_X_NEG"])))
        positive_error = float(np.max(np.abs(positive_value - ORACLE["TORSO_COM_X_POS"])))
        combined_error = max(negative_error, positive_error)
        half_direction = (positive_value - negative_value) / 2.0
        direction_error = float(np.max(np.abs(half_direction - DIRECTION)))
        match = combined_error <= TOLERANCE
        matches[name] = match
        cells.append({
            "variant": name,
            "classification": "MATCH_ENDPOINT_ORACLE" if match else "MISS_ENDPOINT_ORACLE",
            "negative_accelerometer_m_s2": negative_value.tolist(),
            "positive_accelerometer_m_s2": positive_value.tolist(),
            "negative_endpoint_max_abs_error_m_s2": negative_error,
            "positive_endpoint_max_abs_error_m_s2": positive_error,
            "combined_endpoint_max_abs_error_m_s2": combined_error,
            "half_direction_m_s2": half_direction.tolist(),
            "half_direction_max_abs_error_m_s2": direction_error,
        })

    live_cell = next(cell for cell in cells if cell["variant"] == "LIVE_FORWARD_REPRODUCTION")
    reproduction_error = float(np.max(np.abs(
        np.asarray(live_cell["half_direction_m_s2"]) - INVALID_HALF_DIRECTION
    )))
    validity = {
        "fresh_nominal_matches_oracle": float(np.max(np.abs(nominal_value - ORACLE["NOMINAL"]))) <= TOLERANCE,
        "fresh_init_reference_matches_endpoints": matches["FRESH_INIT_REFERENCE"],
        "live_forward_misses_endpoint_oracle": not matches["LIVE_FORWARD_REPRODUCTION"],
        "live_forward_reproduces_prior_invalid_half_direction": reproduction_error <= REPRODUCTION_TOLERANCE,
        "all_sensor_values_finite": finite,
        "model_mutation_contract_passed": bool(contract["checks"]["body2_x_only_com_mutations_exact"]),
        "cpu_only_contract_passed": bool(contract["checks"]["cpu_only"]),
    }
    valid = all(validity.values())
    decision = select_decision(matches) if valid else "INVALID_MJX_INITIALIZATION_ORDER_AUDIT"
    status = "PASS_VALID_MJX_INITIALIZATION_ORDER_AUDIT" if valid else decision
    payload = {
        "schema_version": "ground_up_torso_com_mjx_initialization_order_audit.v1",
        "status": status, "decision": decision,
        "effective_sample_size": 1, "endpoint_tolerance_m_s2": TOLERANCE,
        "reproduction_tolerance_m_s2": REPRODUCTION_TOLERANCE,
        "nominal_accelerometer_m_s2": nominal_value.tolist(),
        "nominal_max_abs_error_m_s2": float(np.max(np.abs(nominal_value - ORACLE["NOMINAL"]))),
        "prior_invalid_half_direction_reproduction_error_m_s2": reproduction_error,
        "validity": validity, "matches": matches, "cells": cells,
        "inputs": {
            "contract": str(contract_path), "contract_sha256": sha256(contract_path),
            "tool_sha256": sha256(Path(__file__)), "source_hashes": EXPECTED_HASHES,
            "trace_hashes": TRACE_HASHES,
        },
        "execution": {
            "cpu_only": True, "formal_endpoint_vectors": 14,
            "dynamic_steps": 0, "actor_calls": 0, "training": False,
            "robot_or_rdk": False,
        },
        "authority": {
            "selected_mechanism_only": valid, "rerun_144_cell_map": False,
            "dynamic_steps": False, "actor_calls": False, "training": False,
            "gpu_or_igpu": False, "robot_or_rdk": False,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    rows = "\n".join(
        f"| `{cell['variant']}` | `{cell['classification']}` | "
        f"{cell['negative_endpoint_max_abs_error_m_s2']:.9g} | "
        f"{cell['positive_endpoint_max_abs_error_m_s2']:.9g} | "
        f"{cell['half_direction_max_abs_error_m_s2']:.9g} |"
        for cell in cells
    )
    markdown.write_text(
        "# Ground-Up Torso-COM MJX Initialization-Order Audit Result\n\n"
        f"status: `{status}`\n\n"
        f"decision: `{decision}`\n\n"
        "This is one deterministic tick-zero reset state (effective n=1); it is a methods audit, not a statistical result.\n\n"
        "| variant | endpoint class | NEG max error | POS max error | half-direction error |\n"
        "|---|---:|---:|---:|---:|\n" + rows + "\n\n"
        f"Fresh nominal maximum error: `{payload['nominal_max_abs_error_m_s2']:.9g}` m/s^2. "
        f"Prior-invalid reproduction error: `{reproduction_error:.9g}` m/s^2.\n\n"
        "The decision selects only the named initialization mechanism for a separately preregistered correction. "
        "It does not authorize the 144-cell map, policy work, training, hardware, or deployment.\n"
    )
    print(json.dumps({"status": status, "decision": decision, "matches": matches}, sort_keys=True))
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
