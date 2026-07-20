#!/usr/bin/env python3
"""Run the frozen winner-v4 zero-PPO signed-response falsification on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "outputs/analysis/winner_v4_response_pretraining_contract.json"
JOINT_NAMES = (
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
)
HOME_RAD = np.asarray(
    [
        0.002,
        0.053,
        -0.63,
        1.368,
        -0.784,
        0.0,
        0.0,
        0.0,
        0.0,
        -0.003,
        -0.065,
        0.635,
        1.379,
        -0.796,
    ],
    dtype=np.float64,
)
STAGE_TICKS = 201
TICK_COUNT = STAGE_TICKS * len(JOINT_NAMES)
SETTLE_TICKS = 250
DT_S = 0.02
SUBSTEPS = 10
MOTOR_CONSTANT_NM_PER_A = 0.784532
POSITION_STEP_RAD = 2.0 * math.pi / 4096.0
CURRENT_STEP_A = 0.0065
GYRO_STEP_RAD_S = math.pi / (180.0 * 16.0)
ACCELERATION_STEP_M_S2 = 0.01


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command}\n{completed.stdout}"
        )
    return completed.stdout


def source_bytes(relative_path: str) -> bytes:
    path = ROOT / relative_path
    if path.is_file():
        return path.read_bytes()
    completed = subprocess.run(
        ["git", "show", f"HEAD:{relative_path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise FileNotFoundError(
            f"cannot read {relative_path}: {completed.stderr.decode(errors='replace')}"
        )
    return completed.stdout


def clone_exact(repository: str, commit: str, output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"refusing existing checkout: {output}")
    run(["git", "clone", "--filter=blob:none", "--no-checkout", repository, str(output)], cwd=output.parent)
    run(["git", "checkout", "--detach", commit], cwd=output)
    actual = run(["git", "rev-parse", "HEAD"], cwd=output).strip()
    if actual != commit:
        raise ValueError(f"checkout mismatch: expected {commit}, got {actual}")


def quantize_target_rad(values: np.ndarray) -> np.ndarray:
    raw = np.trunc(4096.0 * (math.pi + values) / (2.0 * math.pi)).astype(np.int64)
    return raw.astype(np.float64) * POSITION_STEP_RAD - math.pi


def quantize_position_rad(values: np.ndarray) -> np.ndarray:
    raw = np.rint(4096.0 * (math.pi + values) / (2.0 * math.pi)).astype(np.int64)
    return raw.astype(np.float64) * POSITION_STEP_RAD - math.pi


def quantize_nearest(values: np.ndarray, step: float) -> np.ndarray:
    return np.rint(values / step) * step


def excitation(local_tick: int) -> float:
    return 0.015 * math.sin(2.0 * math.pi * local_tick / 40.0) + 0.005 * math.sin(
        2.0 * math.pi * local_tick / 20.0
    )


def contact_state(mujoco: Any, model: Any, data: Any) -> tuple[int, int]:
    floor = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor"))
    feet = (
        int(
            mujoco.mj_name2id(
                model, mujoco.mjtObj.mjOBJ_GEOM, "left_foot_bottom_tpu"
            )
        ),
        int(
            mujoco.mj_name2id(
                model, mujoco.mjtObj.mjOBJ_GEOM, "right_foot_bottom_tpu"
            )
        ),
    )
    contact_pairs = {
        frozenset((int(data.contact[index].geom1), int(data.contact[index].geom2)))
        for index in range(int(data.ncon))
    }
    return tuple(int(frozenset((floor, foot)) in contact_pairs) for foot in feet)  # type: ignore[return-value]


def sensor_vector(mujoco: Any, model: Any, data: Any, name: str) -> np.ndarray:
    sensor_id = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SENSOR, name))
    if sensor_id < 0:
        raise ValueError(f"missing sensor {name}")
    start = int(model.sensor_adr[sensor_id])
    dimension = int(model.sensor_dim[sensor_id])
    if dimension != 3:
        raise ValueError(f"sensor {name} dimension is {dimension}, expected 3")
    return np.asarray(data.sensordata[start : start + dimension], dtype=np.float64).copy()


def write_config(path: Path) -> None:
    config = {
        "start_paused": True,
        "imu_upside_down": False,
        "phase_frequency_factor_offset": 0.0,
        "expression_features": {},
        "joints_offsets": {name: 0.0 for name in JOINT_NAMES},
    }
    path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_metadata(
    *, configuration_sha256: str, trace_sha256: str
) -> dict[str, Any]:
    del trace_sha256  # profile-v4 obtains the trace identity from the file itself.
    return {
        "schema_version": "open_duck_x5.configuration_excitation_metadata.v3",
        "frequency_hz": 50.0,
        "tick_count": TICK_COUNT,
        "max_delay_ticks": 4,
        "minimum_stage_ticks": STAGE_TICKS,
        "minimum_target_span_rad": 0.03,
        "maximum_nonexcited_target_span_rad": 1e-12,
        "maximum_target_velocity_rad_s": 0.21,
        "minimum_current_samples_per_joint": 10,
        "backend": "mock",
        "device": "mock://winner-v4-response-identifiability",
        "informational_only": True,
        "hardware_authorized": False,
        "motion_authorized": False,
        "configuration_calibration_authorized": False,
        "suspended_or_benched": False,
        "torque_off_confirmed": True,
        "telemetry_drop_count": 0,
        "configuration_sha256": configuration_sha256,
        "policy_envelope_sha256": None,
        "imu_calibration_sha256": None,
        "imu_calibration_source_sha256": None,
        "physical_home_rad": HOME_RAD.tolist(),
        "maximum_home_deviation_rad": 0.03,
        "inventory": {
            "required_servo_ids": [20, 21, 22, 23, 24, 30, 31, 32, 33, 10, 11, 12, 13, 14],
            "responding_servo_ids": [20, 21, 22, 23, 24, 30, 31, 32, 33, 10, 11, 12, 13, 14],
            "imu_present": True,
            "contacts_present": True,
        },
        "stages": [
            {
                "joint_name": name,
                "start_tick": index * STAGE_TICKS,
                "end_tick": (index + 1) * STAGE_TICKS,
            }
            for index, name in enumerate(JOINT_NAMES)
        ],
    }


def simulate_trace(
    *,
    mujoco: Any,
    scene: Path,
    fit: dict[str, Any],
    torso_x_offset_m: float,
    trace_path: Path,
) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "tools"))
    from actuator_bridge_model import ActuatorBridgeModel, params_from_fit

    model = mujoco.MjModel.from_xml_path(str(scene))
    actuator_names = tuple(
        mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, index)
        for index in range(model.nu)
    )
    if actuator_names != JOINT_NAMES:
        raise ValueError(f"actuator order mismatch: {actuator_names}")
    if not math.isclose(float(model.opt.timestep), DT_S / SUBSTEPS, abs_tol=1e-15):
        raise ValueError(f"physics timestep mismatch: {model.opt.timestep}")
    key_id = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "home"))
    if key_id < 0:
        raise ValueError("home keyframe is missing")
    home_ctrl = np.asarray(model.key_ctrl[key_id], dtype=np.float64)
    if not np.array_equal(home_ctrl, HOME_RAD):
        raise ValueError(f"home control mismatch: {home_ctrl.tolist()}")
    trunk_id = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "trunk_assembly"))
    if trunk_id != 2:
        raise ValueError(f"trunk body ID changed: {trunk_id}")
    original_ipos = float(model.body_ipos[trunk_id, 0])
    model.body_ipos[trunk_id, 0] = original_ipos + torso_x_offset_m

    data = mujoco.MjData(model)
    data.qpos[:] = model.key_qpos[key_id]
    data.qvel[:] = 0.0
    data.ctrl[:] = HOME_RAD
    mujoco.mj_setConst(model, data)
    mujoco.mj_forward(model, data)
    joint_qpos_addresses = np.asarray(
        [int(model.joint(name).qposadr[0]) for name in JOINT_NAMES], dtype=np.int64
    )

    settle_contact_failures = 0
    for _tick in range(SETTLE_TICKS):
        data.ctrl[:] = HOME_RAD
        for _ in range(SUBSTEPS):
            mujoco.mj_step(model, data)
        settle_contact_failures += int(contact_state(mujoco, model, data) != (1, 1))

    bridge = ActuatorBridgeModel(
        params_from_fit(fit, JOINT_NAMES, include_gain_ratio=True),
        initial_target=HOME_RAD,
        home_target=HOME_RAD,
    )
    contact_failures = 0
    maximum_abs_base_xy_m = 0.0
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("x", encoding="utf-8") as stream:
        for tick in range(TICK_COUNT):
            stage_index = tick // STAGE_TICKS
            local_tick = tick % STAGE_TICKS
            intended = HOME_RAD.copy()
            intended[stage_index] += excitation(local_tick)
            sent = quantize_target_rad(intended)
            applied = bridge.step(sent, DT_S)
            data.ctrl[:] = applied
            for _ in range(SUBSTEPS):
                mujoco.mj_step(model, data)

            contacts = contact_state(mujoco, model, data)
            contact_failures += int(contacts != (1, 1))
            actual = quantize_position_rad(np.asarray(data.qpos[joint_qpos_addresses]))
            current = quantize_nearest(
                np.abs(np.asarray(data.actuator_force, dtype=np.float64))
                / MOTOR_CONSTANT_NM_PER_A,
                CURRENT_STEP_A,
            )
            gyro = quantize_nearest(
                sensor_vector(mujoco, model, data, "gyro"), GYRO_STEP_RAD_S
            )
            acceleration = quantize_nearest(
                sensor_vector(mujoco, model, data, "accelerometer"),
                ACCELERATION_STEP_M_S2,
            )
            currents: list[float | None] = [None] * len(JOINT_NAMES)
            extended_index = tick % len(JOINT_NAMES)
            currents[extended_index] = float(current[extended_index])
            maximum_abs_base_xy_m = max(
                maximum_abs_base_xy_m,
                float(np.max(np.abs(np.asarray(data.qpos[:2], dtype=np.float64)))),
            )
            timestamp = 1_000_000_000 + (tick + 1) * 20_000_000
            row = {
                "schema_version": "open_duck_x5.configuration_excitation_tick.v2",
                "tick": tick,
                "timestamp_monotonic_ns": timestamp,
                "bus_total_ms": 0.0,
                "stage_joint": JOINT_NAMES[stage_index],
                "target_positions_rad": intended.tolist(),
                "actual_positions_rad": actual.tolist(),
                "present_current_a": currents,
                "gyro_rad_s": gyro.tolist(),
                "acceleration_m_s2": acceleration.tolist(),
                "foot_contacts": list(contacts),
                "imu_timestamp_monotonic_ns": timestamp,
                "contacts_timestamp_monotonic_ns": timestamp,
                "per_servo_status": ["ok"] * len(JOINT_NAMES),
                "stale": [False] * len(JOINT_NAMES),
                "imu_stale": False,
                "contacts_stale": False,
            }
            stream.write(json.dumps(row, separators=(",", ":")) + "\n")
    return {
        "actuator_names": list(actuator_names),
        "home_ctrl": home_ctrl.tolist(),
        "trunk_body_id": trunk_id,
        "trunk_ipos_x_before_m": original_ipos,
        "trunk_ipos_x_after_m": float(model.body_ipos[trunk_id, 0]),
        "settle_contact_failure_ticks": settle_contact_failures,
        "excitation_contact_failure_ticks": contact_failures,
        "maximum_abs_base_xy_m": maximum_abs_base_xy_m,
    }


def extract_context(profile: dict[str, Any], fields: list[str]) -> np.ndarray:
    values: list[float] = []
    for field in fields:
        parts = field.split(".")
        group = parts[0]
        if group == "joint_response" and len(parts) == 3:
            _group, name, metric = parts
            values.append(float(profile[group][name][metric]))
        elif group == "body_response" and len(parts) == 2:
            _group, metric = parts
            values.append(float(profile[group][metric]))
        else:
            raise ValueError(f"unsupported response field: {field}")
    context = np.asarray(values, dtype=np.float32)
    if context.shape != (73,) or not np.all(np.isfinite(context)):
        raise ValueError("response context is not 73 finite float32 values")
    return context


def run_experiment(args: argparse.Namespace) -> dict[str, Any]:
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    expected_job_sha = contract["sources"]["job"]["sha256"]
    if sha256_path(Path(__file__).resolve()) != expected_job_sha:
        raise ValueError("job source differs from preregistration")
    if args.work.exists():
        raise FileExistsError(f"refusing existing work directory: {args.work}")
    args.work.mkdir(parents=True)

    playground = args.work / "playground"
    runtime = args.work / "runtime"
    clone_exact(
        contract["sources"]["playground"]["repository"],
        contract["sources"]["playground"]["commit"],
        playground,
    )
    clone_exact(
        contract["sources"]["runtime_review"]["repository"],
        contract["sources"]["runtime_review"]["commit"],
        runtime,
    )

    runtime_hashes = {
        "configuration_collector_sha256": sha256_path(
            runtime / "src/open_duck_x5/configuration_collector.py"
        ),
        "configuration_profile_sha256": sha256_path(
            runtime / "src/open_duck_x5/configuration_profile.py"
        ),
        "response_context_review_sha256": sha256_path(
            runtime / "src/open_duck_x5/response_context_review.py"
        ),
    }
    if runtime_hashes != contract["sources"]["runtime_code"]:
        raise ValueError(f"runtime source hashes differ: {runtime_hashes}")
    review_path = runtime / contract["sources"]["runtime_review"]["path"]
    if sha256_path(review_path) != contract["sources"]["runtime_review"]["sha256"]:
        raise ValueError("runtime review artifact hash differs")

    interface = json.loads(source_bytes(contract["sources"]["interface"]["path"]))
    interface_bytes = source_bytes(contract["sources"]["interface"]["path"])
    if sha256_bytes(interface_bytes) != contract["sources"]["interface"]["sha256"]:
        raise ValueError("interface artifact hash differs")
    policy_fields = list(interface["response_context"]["flatten_order"])

    sys.path.insert(0, str(runtime / "src"))
    from open_duck_x5.configuration_profile import build_automatic_configuration_profile
    from open_duck_x5.response_context_review import RESPONSE_CONTEXT_FIELDS

    runtime_fields = list(RESPONSE_CONTEXT_FIELDS)
    if policy_fields != runtime_fields:
        raise ValueError("policy and runtime response field orders differ")

    import mujoco

    if getattr(mujoco, "__version__", None) != "3.9.0":
        raise ValueError(f"MuJoCo version must be 3.9.0, got {mujoco.__version__}")

    scene = playground / contract["sources"]["playground"]["scene"]
    config_path = args.work / "duck_config.json"
    write_config(config_path)
    config_sha = sha256_path(config_path)

    fits: dict[str, dict[str, Any]] = {}
    fit_hashes: dict[str, str] = {}
    for source in contract["sources"]["actuator_fits"]:
        payload = source_bytes(source["path"])
        digest = sha256_bytes(payload)
        if digest != source["sha256"]:
            raise ValueError(f"actuator fit hash differs: {source['id']} {digest}")
        fits[source["id"]] = json.loads(payload)
        fit_hashes[source["id"]] = digest

    runs: list[dict[str, Any]] = []
    for fit_id, fit in fits.items():
        for offset in (-0.05, 0.05):
            for repeat in range(2):
                run_id = f"{fit_id}_x{offset:+.2f}_repeat{repeat}"
                run_dir = args.work / "runs" / run_id
                run_dir.mkdir(parents=True)
                trace_path = run_dir / "trace.jsonl"
                simulation = simulate_trace(
                    mujoco=mujoco,
                    scene=scene,
                    fit=fit,
                    torso_x_offset_m=offset,
                    trace_path=trace_path,
                )
                metadata_path = run_dir / "metadata.json"
                metadata = build_metadata(
                    configuration_sha256=config_sha,
                    trace_sha256=sha256_path(trace_path),
                )
                metadata_path.write_text(
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                profile = build_automatic_configuration_profile(
                    trace_path=trace_path,
                    metadata_path=metadata_path,
                    configuration_path=config_path,
                )
                profile_path = run_dir / "profile.json"
                profile_path.write_text(
                    json.dumps(profile, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                context = extract_context(profile, runtime_fields)
                runs.append(
                    {
                        "id": run_id,
                        "fit": fit_id,
                        "torso_x_offset_m": offset,
                        "repeat": repeat,
                        "context": context.tolist(),
                        "context_sha256": sha256_bytes(context.tobytes()),
                        "trace_sha256": sha256_path(trace_path),
                        "metadata_sha256": sha256_path(metadata_path),
                        "profile_sha256": sha256_path(profile_path),
                        "simulation": simulation,
                    }
                )

    repeat_checks: dict[str, bool] = {}
    signed_checks: dict[str, dict[str, Any]] = {}
    for fit_id in fits:
        by_offset: dict[float, list[dict[str, Any]]] = {}
        for offset in (-0.05, 0.05):
            selected = [
                row
                for row in runs
                if row["fit"] == fit_id and row["torso_x_offset_m"] == offset
            ]
            by_offset[offset] = selected
            repeat_checks[f"{fit_id}_x{offset:+.2f}"] = (
                selected[0]["context_sha256"] == selected[1]["context_sha256"]
            )
        negative = np.asarray(by_offset[-0.05][0]["context"], dtype=np.float32)
        positive = np.asarray(by_offset[0.05][0]["context"], dtype=np.float32)
        different = np.flatnonzero(negative.view(np.uint32) != positive.view(np.uint32))
        signed_checks[fit_id] = {
            "not_bit_identical": bool(different.size),
            "different_field_count": int(different.size),
            "different_field_indices": different.tolist(),
            "maximum_absolute_difference": float(np.max(np.abs(positive - negative))),
            "negative_context_sha256": by_offset[-0.05][0]["context_sha256"],
            "positive_context_sha256": by_offset[0.05][0]["context_sha256"],
        }

    checks = {
        "cpu_only_no_cuda_visible": os.environ.get("CUDA_VISIBLE_DEVICES") == "",
        "mujoco_version_exact": mujoco.__version__ == "3.9.0",
        "source_hashes_exact": True,
        "policy_runtime_field_order_exact": policy_fields == runtime_fields,
        "run_population_exact": len(runs) == 8,
        "all_contexts_73_finite_float32": all(
            len(row["context"]) == 73
            and np.all(np.isfinite(np.asarray(row["context"], dtype=np.float32)))
            for row in runs
        ),
        "all_repeats_bit_exact": all(repeat_checks.values()),
        "both_signed_pairs_noncollapsed": all(
            row["not_bit_identical"] for row in signed_checks.values()
        ),
        "both_feet_contact_every_settle_tick": all(
            row["simulation"]["settle_contact_failure_ticks"] == 0 for row in runs
        ),
        "both_feet_contact_every_excitation_tick": all(
            row["simulation"]["excitation_contact_failure_ticks"] == 0 for row in runs
        ),
        "training_steps_zero": True,
        "formal_behavior_cells_zero": True,
        "robot_or_hardware_touched": False,
    }
    passed = all(checks.values())
    return {
        "schema_version": "open_duck_mini.winner_v4_response_identifiability_result.v1",
        "status": (
            "PASS_RESPONSE73_SIGNED_IDENTIFIABILITY_CPU_CONTRACT"
            if passed
            else "HOLD_RESPONSE73_PRETRAINING_FALSIFICATION_FAILED"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_ZERO_PPO_POLICY_IMPLEMENTATION_CONTRACT"
            if passed
            else "DO_NOT_IMPLEMENT_OR_TRAIN_RESPONSE73"
        ),
        "contract": {
            "path": str(CONTRACT_PATH.relative_to(ROOT)),
            "sha256": sha256_path(CONTRACT_PATH),
        },
        "environment": {
            "python": sys.version,
            "platform": sys.platform,
            "mujoco": mujoco.__version__,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "sources": {
            "runtime_commit": contract["sources"]["runtime_review"]["commit"],
            "playground_commit": contract["sources"]["playground"]["commit"],
            "runtime_hashes": runtime_hashes,
            "actuator_fit_hashes": fit_hashes,
            "scene_sha256": sha256_path(scene),
            "job_sha256": sha256_path(Path(__file__).resolve()),
        },
        "support_mode": contract["support_mode"],
        "checks": checks,
        "repeat_checks": repeat_checks,
        "signed_endpoint_checks": signed_checks,
        "runs": runs,
        "authority": {
            "training": False,
            "gpu_or_igpu": False,
            "runtime_implementation": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "gate5_or_deployment": False,
            "robot_clearance": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(f"refusing existing output: {args.output}")
    result = run_experiment(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"status={result['status']} output={args.output} "
        f"sha256={sha256_path(args.output)}"
    )
    return 0 if result["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
