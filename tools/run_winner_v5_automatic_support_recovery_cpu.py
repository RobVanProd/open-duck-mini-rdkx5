#!/usr/bin/env python3
"""Run the frozen winner-v5 automatic support-recovery validation on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v5_automatic_support_recovery_preregistration.json"
DEFAULT_OUTPUT = ROOT / "outputs/analysis/winner_v5_automatic_support_recovery_result.json"
JOINT_NAMES = (
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee",
    "left_ankle", "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee",
    "right_ankle",
)
HOME_RAD = np.asarray(
    [
        0.002, 0.053, -0.63, 1.368, -0.784, 0.0, 0.0,
        0.0, 0.0, -0.003, -0.065, 0.635, 1.379, -0.796,
    ],
    dtype=np.float64,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout)
    return completed.stdout.strip()


def mat_to_quat_wxyz(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float64)
    q_abs = np.sqrt(
        np.maximum(
            np.asarray(
                [
                    1.0 + matrix[0, 0] + matrix[1, 1] + matrix[2, 2],
                    1.0 + matrix[0, 0] - matrix[1, 1] - matrix[2, 2],
                    1.0 - matrix[0, 0] + matrix[1, 1] - matrix[2, 2],
                    1.0 - matrix[0, 0] - matrix[1, 1] + matrix[2, 2],
                ],
                dtype=np.float64,
            ),
            0.0,
        )
    )
    candidates = np.asarray(
        [
            [q_abs[0] ** 2, matrix[2, 1] - matrix[1, 2], matrix[0, 2] - matrix[2, 0], matrix[1, 0] - matrix[0, 1]],
            [matrix[2, 1] - matrix[1, 2], q_abs[1] ** 2, matrix[1, 0] + matrix[0, 1], matrix[0, 2] + matrix[2, 0]],
            [matrix[0, 2] - matrix[2, 0], matrix[1, 0] + matrix[0, 1], q_abs[2] ** 2, matrix[2, 1] + matrix[1, 2]],
            [matrix[1, 0] - matrix[0, 1], matrix[0, 2] + matrix[2, 0], matrix[2, 1] + matrix[1, 2], q_abs[3] ** 2],
        ],
        dtype=np.float64,
    )
    candidates /= 2.0 * np.maximum(q_abs[:, None], 0.1)
    quaternion = candidates[int(np.argmax(q_abs))]
    quaternion /= np.linalg.norm(quaternion)
    return -quaternion if quaternion[0] < 0.0 else quaternion


def quat_mul_wxyz(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    w1, x1, y1, z1 = np.asarray(left, dtype=np.float64)
    w2, x2, y2, z2 = np.asarray(right, dtype=np.float64)
    result = np.asarray(
        [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ],
        dtype=np.float64,
    )
    return result / np.linalg.norm(result)


def roll_pitch_wxyz(quaternion: np.ndarray) -> tuple[float, float]:
    w, x, y, z = (float(value) for value in quaternion)
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
    return roll, pitch


def sensor_vector(mujoco: Any, model: Any, data: Any, name: str) -> np.ndarray:
    sensor_id = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SENSOR, name))
    start = int(model.sensor_adr[sensor_id])
    dimension = int(model.sensor_dim[sensor_id])
    return np.asarray(data.sensordata[start : start + dimension], dtype=np.float64).copy()


def contact_state(mujoco: Any, model: Any, data: Any) -> tuple[int, int]:
    floor = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor"))
    feet = (
        int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "left_foot_bottom_tpu")),
        int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "right_foot_bottom_tpu")),
    )
    pairs = {
        frozenset((int(data.contact[index].geom1), int(data.contact[index].geom2)))
        for index in range(int(data.ncon))
    }
    return tuple(int(frozenset((floor, foot)) in pairs) for foot in feet)  # type: ignore[return-value]


def apply_configuration(model: Any, configuration: Mapping[str, Any]) -> None:
    body_id = 2
    if model.body(body_id).name != "trunk_assembly":
        raise ValueError("winner-v5 torso identity mismatch")
    nominal_mass = np.asarray(model.body_mass, dtype=np.float64).copy()
    nominal_ipos = np.asarray(model.body_ipos, dtype=np.float64).copy()
    nominal_iquat = np.asarray(model.body_iquat, dtype=np.float64).copy()
    model.body_mass[:] = nominal_mass * float(configuration["all_link_mass_scale"])
    model.body_mass[body_id] += float(configuration["torso_mass_add_kg"])
    model.body_ipos[body_id] = nominal_ipos[body_id] + np.asarray(
        configuration["torso_com_offset_m"], dtype=np.float64
    )
    tensor = np.asarray(configuration["torso_inertia_tensor_kg_m2"], dtype=np.float64)
    principal, eigenvectors = np.linalg.eigh(tensor)
    if np.linalg.det(eigenvectors) < 0.0:
        eigenvectors[:, 2] *= -1.0
    model.body_inertia[body_id] = principal
    model.body_iquat[body_id] = quat_mul_wxyz(
        nominal_iquat[body_id], mat_to_quat_wxyz(eigenvectors)
    )


def make_model_data(
    mujoco: Any, scene: Path, configuration: Mapping[str, Any] | None,
    episode_qpos: np.ndarray | None,
) -> tuple[Any, Any, int]:
    model = mujoco.MjModel.from_xml_path(str(scene))
    actuator_names = tuple(
        mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, index)
        for index in range(model.nu)
    )
    if actuator_names != JOINT_NAMES:
        raise ValueError(f"actuator order mismatch: {actuator_names}")
    key_id = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "home"))
    if configuration is not None:
        apply_configuration(model, configuration)
    data = mujoco.MjData(model)
    # Critical prospective fix: recompute model constants before loading the
    # episode pose. The completed winner-v4 gate used the opposite order.
    mujoco.mj_setConst(model, data)
    data.qpos[:] = model.key_qpos[key_id] if episode_qpos is None else episode_qpos
    data.qvel[:] = 0.0
    data.ctrl[:] = HOME_RAD
    mujoco.mj_forward(model, data)
    return model, data, key_id


def actuator_params(contract: Mapping[str, Any], fit: str) -> list[Any]:
    sys.path.insert(0, str(ROOT / "tools"))
    from actuator_bridge_model import JointActuatorParams

    return [
        JointActuatorParams(**contract["actuator_plants"]["per_joint"][name][fit])
        for name in JOINT_NAMES
    ]


def simulate_cell(
    mujoco: Any, scene: Path, contract: Mapping[str, Any],
    configuration: Mapping[str, Any], shared_qpos: np.ndarray,
    fit: str, sensor_case: Mapping[str, Any],
) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "tools"))
    from actuator_bridge_model import ActuatorBridgeModel

    model, data, _ = make_model_data(mujoco, scene, configuration, shared_qpos)
    controller = contract["controller"]
    bridge = ActuatorBridgeModel(
        actuator_params(contract, fit), initial_target=HOME_RAD, home_target=HOME_RAD
    )
    target = HOME_RAD.copy()
    triggered = False
    decision_gyro = [math.nan, math.nan]
    minimum_base_z = math.inf
    maximum_abs_tilt = 0.0
    contact_failure_ticks = 0
    final_window_gyro: list[float] = []
    tick_count = int(contract["experiment"]["tick_count"])
    substeps = int(contract["experiment"]["physics_substeps_per_tick"])
    gyro_step = float(contract["controller"]["gyro_quantization_step_rad_s"])
    bias = np.asarray(sensor_case["gyro_bias_rad_s_xy"], dtype=np.float64)
    for tick in range(tick_count):
        if tick == int(controller["decision_tick"]):
            gyro = sensor_vector(mujoco, model, data, "gyro")[:2] + bias
            gyro = np.rint(gyro / gyro_step) * gyro_step
            decision_gyro = gyro.tolist()
            triggered = bool(float(gyro[1]) < float(controller["pitch_trigger_rad_s"]))
            if triggered:
                for index, delta in controller["sagittal_target_delta_rad"].items():
                    target[int(index)] += float(delta)
                if float(gyro[0]) < float(controller["lateral_trigger_rad_s"]):
                    for index, delta in controller["lateral_target_delta_rad"].items():
                        target[int(index)] += float(delta)
        data.ctrl[:] = bridge.step(target if triggered else HOME_RAD, 0.02)
        for _ in range(substeps):
            mujoco.mj_step(model, data)
        roll, pitch = roll_pitch_wxyz(np.asarray(data.qpos[3:7], dtype=np.float64))
        minimum_base_z = min(minimum_base_z, float(data.qpos[2]))
        maximum_abs_tilt = max(maximum_abs_tilt, abs(roll), abs(pitch))
        contact_failure_ticks += int(contact_state(mujoco, model, data) != (1, 1))
        if tick >= tick_count - int(contract["pass_requirements"]["final_window_ticks"]):
            final_window_gyro.append(
                float(np.linalg.norm(sensor_vector(mujoco, model, data, "gyro")[:2]))
            )
    final_roll, final_pitch = roll_pitch_wxyz(np.asarray(data.qpos[3:7], dtype=np.float64))
    maximum_final_gyro = max(final_window_gyro)
    requirements = contract["pass_requirements"]
    checks = {
        "minimum_base_z": minimum_base_z >= float(requirements["minimum_base_z_m"]),
        "maximum_abs_tilt": maximum_abs_tilt <= float(requirements["maximum_abs_tilt_rad"]),
        "two_foot_contact": contact_failure_ticks == 0,
        "final_gyro": maximum_final_gyro <= float(requirements["maximum_final_gyro_rad_s"]),
    }
    return {
        "configuration_id": configuration["id"],
        "fit": fit,
        "sensor_case": sensor_case["id"],
        "triggered": triggered,
        "decision_gyro_rad_s_xy": decision_gyro,
        "minimum_base_z_m": minimum_base_z,
        "maximum_abs_tilt_rad": maximum_abs_tilt,
        "contact_failure_ticks": contact_failure_ticks,
        "maximum_final_window_gyro_rad_s": maximum_final_gyro,
        "final_base_z_m": float(data.qpos[2]),
        "final_roll_rad": final_roll,
        "final_pitch_rad": final_pitch,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    if contract["status"] != "PREREGISTERED_WINNER_V5_AUTOMATIC_SUPPORT_RECOVERY_NOT_RUN":
        raise ValueError("winner-v5 contract is not preregistered/not-run")
    if sha256(Path(__file__)) != contract["sources"]["job"]["sha256"]:
        raise ValueError("winner-v5 job hash mismatch")
    expected_commit = contract["sources"]["playground"]["commit"]
    if git_output(args.playground_root, "rev-parse", "HEAD") != expected_commit:
        raise ValueError("Playground commit mismatch")
    if git_output(args.playground_root, "status", "--porcelain"):
        raise ValueError("Playground checkout is not clean")

    import mujoco

    scene = args.playground_root / contract["sources"]["playground"]["scene"]
    if sha256(scene) != contract["sources"]["playground"]["scene_sha256"]:
        raise ValueError("scene hash mismatch")
    model, data, _ = make_model_data(mujoco, scene, None, None)
    for _ in range(int(contract["experiment"]["nominal_settle_ticks"])):
        data.ctrl[:] = HOME_RAD
        for _ in range(int(contract["experiment"]["physics_substeps_per_tick"])):
            mujoco.mj_step(model, data)
    shared_qpos = np.asarray(data.qpos, dtype=np.float64).copy()
    shared_roll, shared_pitch = roll_pitch_wxyz(shared_qpos[3:7])
    if float(shared_qpos[2]) < 0.1 or max(abs(shared_roll), abs(shared_pitch)) > 0.1:
        raise ValueError("corrected nominal shared pose is not upright")

    cells = []
    for configuration in contract["validation_population"]:
        for fit in contract["actuator_plants"]["fit_order"]:
            for sensor_case in contract["sensor_cases"]:
                cells.append(
                    simulate_cell(
                        mujoco, scene, contract, configuration, shared_qpos,
                        fit, sensor_case,
                    )
                )
    expected_cells = (
        len(contract["validation_population"])
        * len(contract["actuator_plants"]["fit_order"])
        * len(contract["sensor_cases"])
    )
    if len(cells) != expected_cells:
        raise AssertionError((len(cells), expected_cells))
    failed = [cell for cell in cells if not cell["pass"]]
    passed = not failed
    payload = {
        "schema_version": "winner_v5.automatic_support_recovery_result.v1",
        "status": "PASS_WINNER_V5_AUTOMATIC_SUPPORT_RECOVERY" if passed else "HOLD_WINNER_V5_AUTOMATIC_SUPPORT_RECOVERY",
        "decision": "AUTHORIZE_RESPONSE_PROFILE_REDESIGN_ONLY" if passed else "CLOSE_AUTOMATIC_SUPPORT_RECOVERY_RULE",
        "contract": {"path": str(args.contract), "sha256": sha256(args.contract)},
        "environment": {
            "backend": f"MuJoCo {mujoco.__version__} CPU double precision",
            "playground_commit": expected_commit,
            "shared_nominal_qpos": shared_qpos.tolist(),
            "shared_nominal_roll_rad": shared_roll,
            "shared_nominal_pitch_rad": shared_pitch,
        },
        "counts": {
            "configurations": len(contract["validation_population"]),
            "cells": len(cells),
            "triggered": sum(bool(cell["triggered"]) for cell in cells),
            "passed": sum(bool(cell["pass"]) for cell in cells),
            "failed": len(failed),
        },
        "worst": {
            "minimum_base_z_m": min(float(cell["minimum_base_z_m"]) for cell in cells),
            "maximum_abs_tilt_rad": max(float(cell["maximum_abs_tilt_rad"]) for cell in cells),
            "maximum_contact_failure_ticks": max(int(cell["contact_failure_ticks"]) for cell in cells),
            "maximum_final_window_gyro_rad_s": max(float(cell["maximum_final_window_gyro_rad_s"]) for cell in cells),
        },
        "cells": cells,
        "authority": contract["authority"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "counts": payload["counts"], "worst": payload["worst"], "sha256": sha256(args.output)}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
