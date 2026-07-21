#!/usr/bin/env python3
"""Run the single frozen Winner-v12 two-stage calibrator CPU smoke."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Mapping, Sequence

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(PATCHES))
sys.path.insert(0, str(TOOLS))

import winner_v12_calibrator_training as training  # noqa: E402
import winner_v12_decomposed_backend_networks as networks  # noqa: E402
from actuator_bridge_model import (  # noqa: E402
    ActuatorBridgeModel,
    JOINT_NAMES,
    JointActuatorParams,
)


DEFAULT_CONTRACT = (
    ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_contract.json"
)
DEFAULT_OUTPUT = ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_result.json"
CALIBRATOR_PREREG = (
    ROOT / "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
)
DOMAIN_PREREG = (
    ROOT
    / "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
)
P30_FIT = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
RUNTIME_OBSERVER = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
)
REFERENCE_TABLE = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/reference/ground_up_projected_reference_feature_table.npz"
)

CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
MODEL_RELATIVE = "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml"
SCENE_RELATIVE = "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
MODEL_SHA256 = "660fa8e4ac0d977806e881d008090e7153cd0608dbee05b88f957a91bde6f655"
SCENE_SHA256 = "65324e27a3a84e2e42d1073bfc636f9cdbf6bef7b1f20c1b5a886b8fd58fcc71"
P30_FIT_LF_SHA256 = "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b"
PLAYGROUND_RECEIPT_LF_SHA256 = (
    "628c35fab95e41a2fa82ae2255e0109502d72632c7ad408bf7e1294f5eb1c196"
)
PROTECTED_POLICY_HASHES = {
    "half": "cf001269908d86e47eaa145ffda1d87e946a314ecf51056dc086c4cf10164ab6",
    "final": "d52b63241340d9d56671b95c58bb0fc72af0998fd47d4684719f6cd44f244a10",
}
SMOKE_SEED = 120120
SMOKE_ENVIRONMENTS = 16
SMOKE_TICKS = 250
PHYSICS_SUBSTEPS = 10
CONTROL_DT_S = 0.02
ACTION_SCALE_RAD = 0.25
CURRENT_NM_PER_A = 0.784532
TORQUE_LIMIT_NM = 1.91229675
CURRENT_LIMIT_A = 2.5
OVERCURRENT_A = 2.0
OVERCURRENT_TRIP_TICKS = 100
MINIMUM_BASE_Z_M = 0.1
MAXIMUM_ABS_TILT_RAD = 0.35
FINAL_GYRO_LIMIT_RAD_S = 0.05
FINAL_GYRO_WINDOW_TICKS = 50
TERMINAL_BONUS = 250.0
HOME_RAD = np.asarray(
    [
        0.002,
        0.053,
        -0.630,
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
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
FIT_KEYS = {
    "P30_ALL_JOINT": "fit_p30",
    "P31_34_PITCH_WITH_P30_NONPITCH": "fit_p31_34",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def tree_sha256(value: Mapping[str, Any]) -> str:
    manifest = {
        key: {
            "shape": list(np.asarray(item).shape),
            "dtype": str(np.asarray(item).dtype),
            "sha256": array_sha256(item),
        }
        for key, item in sorted(value.items())
    }
    return canonical_sha256(manifest)


def git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout)
    return completed.stdout.rstrip("\r\n")


def git_bytes(root: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.decode(errors="replace"))
    return completed.stdout


def porcelain_paths(output: str) -> set[str]:
    paths: set[str] = set()
    for line in output.rstrip("\r\n").splitlines():
        if len(line) < 4:
            raise ValueError(f"invalid git porcelain status line: {line!r}")
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def validate_playground_tree(root: Path) -> dict[str, Any]:
    receipt_path = root / "winner_v7_playground_composition_receipt.json"
    if lf_sha256(receipt_path) != PLAYGROUND_RECEIPT_LF_SHA256:
        raise ValueError("Playground composition receipt identity mismatch")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("base_commit") != CONTROL_COMMIT:
        raise ValueError("Playground composition receipt commit mismatch")
    composed_hashes = dict(receipt.get("composed_file_hashes") or {})
    if not composed_hashes:
        raise ValueError("Playground composition receipt has no file hashes")
    overridden = {
        MODEL_RELATIVE: MODEL_SHA256,
        SCENE_RELATIVE: SCENE_SHA256,
    }
    checked = {}
    for relative, expected in composed_hashes.items():
        expected = overridden.get(relative, expected)
        observed = sha256(root / relative)
        if observed != expected:
            raise ValueError(f"composed Playground file drift: {relative}")
        checked[relative] = observed
    for relative, expected in overridden.items():
        if relative not in checked:
            observed = sha256(root / relative)
            if observed != expected:
                raise ValueError(f"Winner-v10 XML drift: {relative}")
            checked[relative] = observed
    observed_paths = porcelain_paths(git_output(root, "status", "--porcelain=v1"))
    expected_paths = set(composed_hashes) | {receipt_path.name}
    for relative, expected in overridden.items():
        head_bytes = git_bytes(root, "show", f"{CONTROL_COMMIT}:{relative}")
        if sha256_bytes(head_bytes) != expected:
            expected_paths.add(relative)
    if observed_paths != expected_paths:
        raise ValueError(
            "Playground tree contains unexpected dirty/untracked files: "
            f"missing={sorted(expected_paths - observed_paths)}, "
            f"extra={sorted(observed_paths - expected_paths)}"
        )
    return {
        "receipt_canonical_lf_sha256": lf_sha256(receipt_path),
        "receipt_hash_mode": "lf",
        "base_commit": receipt["base_commit"],
        "patches": receipt.get("patches_in_order"),
        "checked_file_count": len(checked),
        "checked_files_sha256": canonical_sha256(checked),
        "git_status_paths": sorted(observed_paths),
    }


def validate_software_versions(contract: Mapping[str, Any]) -> dict[str, Any]:
    import jax
    import jaxlib
    import mujoco
    import onnx
    import onnxruntime

    observed = {
        "python": platform.python_version(),
        "jax": jax.__version__,
        "jaxlib": jaxlib.__version__,
        "mujoco": mujoco.__version__,
        "onnx": onnx.__version__,
        "onnxruntime": onnxruntime.__version__,
        "numpy": np.__version__,
    }
    expected = dict(contract.get("software_versions") or {})
    if observed != expected:
        raise ValueError(
            f"software version mismatch: expected={expected}, observed={observed}"
        )
    return {"expected": expected, "observed": observed, "exact": True}


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
            [
                q_abs[0] ** 2,
                matrix[2, 1] - matrix[1, 2],
                matrix[0, 2] - matrix[2, 0],
                matrix[1, 0] - matrix[0, 1],
            ],
            [
                matrix[2, 1] - matrix[1, 2],
                q_abs[1] ** 2,
                matrix[1, 0] + matrix[0, 1],
                matrix[0, 2] + matrix[2, 0],
            ],
            [
                matrix[0, 2] - matrix[2, 0],
                matrix[1, 0] + matrix[0, 1],
                q_abs[2] ** 2,
                matrix[2, 1] + matrix[1, 2],
            ],
            [
                matrix[1, 0] - matrix[0, 1],
                matrix[0, 2] + matrix[2, 0],
                matrix[2, 1] + matrix[1, 2],
                q_abs[3] ** 2,
            ],
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
    if sensor_id < 0:
        raise ValueError(f"missing sensor: {name}")
    start = int(model.sensor_adr[sensor_id])
    dimension = int(model.sensor_dim[sensor_id])
    return np.asarray(
        data.sensordata[start : start + dimension], dtype=np.float64
    ).copy()


def contact_state(mujoco: Any, model: Any, data: Any) -> tuple[int, int]:
    floor = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor"))
    feet = (
        int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "left_foot_bottom_tpu")),
        int(
            mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "right_foot_bottom_tpu")
        ),
    )
    if floor < 0 or min(feet) < 0:
        raise ValueError("contact geometry contract changed")
    pairs = {
        frozenset((int(data.contact[index].geom1), int(data.contact[index].geom2)))
        for index in range(int(data.ncon))
    }
    return tuple(int(frozenset((floor, foot)) in pairs) for foot in feet)  # type: ignore[return-value]


def update_overcurrent_streak(
    previous: np.ndarray, current_a: np.ndarray
) -> np.ndarray:
    previous = np.asarray(previous, dtype=np.int64)
    current = np.asarray(current_a, dtype=np.float64)
    if previous.shape != (training.ACTION_SIZE,) or current.shape != (
        training.ACTION_SIZE,
    ):
        raise ValueError("overcurrent arrays violate the 14-joint contract")
    return np.where(current > OVERCURRENT_A, previous + 1, 0).astype(np.int64)


def support_checks(
    *,
    contacts: tuple[int, int],
    base_z_m: float,
    roll_rad: float,
    pitch_rad: float,
    torque_nm: np.ndarray,
    current_a: np.ndarray,
    overcurrent_streak: np.ndarray,
    finite: bool,
) -> dict[str, bool]:
    torque = np.asarray(torque_nm, dtype=np.float64)
    current = np.asarray(current_a, dtype=np.float64)
    streak = np.asarray(overcurrent_streak, dtype=np.int64)
    if (
        torque.shape != (training.ACTION_SIZE,)
        or current.shape != (training.ACTION_SIZE,)
        or streak.shape != (training.ACTION_SIZE,)
    ):
        raise ValueError("support arrays violate the 14-joint contract")
    return {
        "both_contacts": contacts == (1, 1),
        "base_z": float(base_z_m) >= MINIMUM_BASE_Z_M,
        "roll_pitch": max(abs(float(roll_rad)), abs(float(pitch_rad)))
        <= MAXIMUM_ABS_TILT_RAD,
        "torque": bool(np.all(torque <= TORQUE_LIMIT_NM)),
        "current": bool(np.all(current <= CURRENT_LIMIT_A)),
        "overcurrent_streak": bool(np.all(streak < OVERCURRENT_TRIP_TICKS)),
        "finite": bool(finite),
    }


def support_boundary_canary() -> dict[str, bool]:
    zeros = np.zeros(training.ACTION_SIZE, dtype=np.float64)
    streak_99 = np.full(training.ACTION_SIZE, 99, dtype=np.int64)
    baseline = {
        "contacts": (1, 1),
        "base_z_m": MINIMUM_BASE_Z_M,
        "roll_rad": MAXIMUM_ABS_TILT_RAD,
        "pitch_rad": -MAXIMUM_ABS_TILT_RAD,
        "torque_nm": np.full(training.ACTION_SIZE, TORQUE_LIMIT_NM),
        "current_a": np.full(training.ACTION_SIZE, CURRENT_LIMIT_A),
        "overcurrent_streak": streak_99,
        "finite": True,
    }

    def passed(**changes: Any) -> bool:
        values = dict(baseline)
        values.update(changes)
        return all(support_checks(**values).values())

    exactly_two = np.full(training.ACTION_SIZE, OVERCURRENT_A, dtype=np.float64)
    above_two = exactly_two.copy()
    above_two[0] = np.nextafter(OVERCURRENT_A, math.inf)
    return {
        "inclusive_boundaries_pass": passed(),
        "missing_left_contact_fails": not passed(contacts=(0, 1)),
        "missing_right_contact_fails": not passed(contacts=(1, 0)),
        "base_below_by_one_ulp_fails": not passed(
            base_z_m=np.nextafter(MINIMUM_BASE_Z_M, -math.inf)
        ),
        "roll_above_by_one_ulp_fails": not passed(
            roll_rad=np.nextafter(MAXIMUM_ABS_TILT_RAD, math.inf)
        ),
        "pitch_below_by_one_ulp_fails": not passed(
            pitch_rad=np.nextafter(-MAXIMUM_ABS_TILT_RAD, -math.inf)
        ),
        "torque_above_by_one_ulp_fails": not passed(
            torque_nm=np.full(
                training.ACTION_SIZE,
                np.nextafter(TORQUE_LIMIT_NM, math.inf),
            )
        ),
        "current_above_by_one_ulp_fails": not passed(
            current_a=np.full(
                training.ACTION_SIZE,
                np.nextafter(CURRENT_LIMIT_A, math.inf),
            )
        ),
        "overcurrent_99_passes": passed(),
        "overcurrent_100_fails": not passed(
            overcurrent_streak=np.full(
                training.ACTION_SIZE, OVERCURRENT_TRIP_TICKS, dtype=np.int64
            )
        ),
        "strict_two_amp_does_not_increment": np.array_equal(
            update_overcurrent_streak(np.ones(14, dtype=np.int64), exactly_two),
            zeros.astype(np.int64),
        ),
        "one_ulp_above_two_amp_increments": np.array_equal(
            update_overcurrent_streak(np.zeros(14, dtype=np.int64), above_two),
            np.asarray([1, *([0] * 13)], dtype=np.int64),
        ),
        "nonfinite_fails": not passed(finite=False),
    }


def apply_configuration(model: Any, configuration: Mapping[str, Any]) -> None:
    body_id = 2
    if model.body(body_id).name != "trunk_assembly":
        raise ValueError("Winner-v12 torso identity mismatch")
    allowed = {
        "id",
        "sampling_role",
        "optional_configuration_semantics",
        "resulting_torso_mass_kg",
        "inertia_validity_contractions",
        "all_link_mass_scale",
        "torso_mass_add_kg",
        "torso_com_offset_m",
        "torso_inertia_tensor_kg_m2",
    }
    if set(configuration) - allowed:
        raise ValueError("configuration contains an uncontracted field")
    nominal_mass = np.asarray(model.body_mass, dtype=np.float64).copy()
    nominal_ipos = np.asarray(model.body_ipos, dtype=np.float64).copy()
    nominal_iquat = np.asarray(model.body_iquat, dtype=np.float64).copy()
    model.body_mass[:] = nominal_mass * float(configuration["all_link_mass_scale"])
    model.body_mass[body_id] += float(configuration["torso_mass_add_kg"])
    if float(model.body_mass[body_id]) <= 0.0:
        raise ValueError("nonpositive configured torso mass")
    model.body_ipos[body_id] = nominal_ipos[body_id] + np.asarray(
        configuration["torso_com_offset_m"], dtype=np.float64
    )
    tensor = np.asarray(configuration["torso_inertia_tensor_kg_m2"], dtype=np.float64)
    if tensor.shape != (3, 3) or not np.allclose(
        tensor, tensor.T, rtol=0.0, atol=1.0e-12
    ):
        raise ValueError("configured inertia tensor is invalid")
    principal, eigenvectors = np.linalg.eigh(tensor)
    if np.any(principal <= 0.0) or principal[2] >= principal[0] + principal[1]:
        raise ValueError("configured inertia is not positive triangle-valid")
    if np.linalg.det(eigenvectors) < 0.0:
        eigenvectors[:, 2] *= -1.0
    model.body_inertia[body_id] = principal
    model.body_iquat[body_id] = quat_mul_wxyz(
        nominal_iquat[body_id], mat_to_quat_wxyz(eigenvectors)
    )


def load_runtime_observer(canonical_fit: Path) -> type[Any]:
    spec = importlib.util.spec_from_file_location(
        "winner_v12_runtime_observer", RUNTIME_OBSERVER
    )
    if spec is None or spec.loader is None:
        raise ImportError(RUNTIME_OBSERVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module.P30_FIT_HASH != P30_FIT_LF_SHA256:
        raise ValueError("runtime observer P30 hash changed")
    # Construct once here so a path/hash incompatibility stops before simulation.
    module.FittedBridgeObserver(canonical_fit, HOME_RAD)
    return module.FittedBridgeObserver


def plant_parameters(
    preregistration: Mapping[str, Any], plant: str
) -> list[JointActuatorParams]:
    if plant not in FIT_KEYS:
        raise ValueError(f"unsupported plant: {plant}")
    per_joint = preregistration["hidden_configuration_domain"][
        "continuous_training_domain"
    ]["actuator"]["per_joint"]
    fit_key = FIT_KEYS[plant]
    return [
        JointActuatorParams(
            delay_ticks=int(per_joint[name][fit_key]["delay_ticks"]),
            tau_s=float(per_joint[name][fit_key]["tau_s"]),
            velocity_limit_rad_s=float(
                per_joint[name][fit_key]["velocity_limit_rad_s"]
            ),
            gain_ratio=float(per_joint[name][fit_key]["gain_ratio"]),
        )
        for name in JOINT_NAMES
    ]


def bounded_action_numpy(raw: np.ndarray, previous: np.ndarray) -> np.ndarray:
    raw = np.asarray(raw, dtype=np.float32)
    previous = np.asarray(previous, dtype=np.float32)
    delta = np.asarray(networks.INTERNAL_ACTION_DELTA, dtype=np.float32)
    absolute = np.clip(raw, -1.0, 1.0)
    lower = np.maximum(previous - delta, -1.0)
    upper = np.minimum(previous + delta, 1.0)
    return np.maximum(np.minimum(absolute, upper), lower).astype(np.float32)


class Episode:
    """One classic-MuJoCo calibration episode with a hidden physical plant."""

    def __init__(
        self,
        mujoco: Any,
        scene: Path,
        configuration: Mapping[str, Any],
        plant: str,
        preregistration: Mapping[str, Any],
        observer_type: type[Any],
        canonical_fit: Path,
    ) -> None:
        self.mujoco = mujoco
        self.model = mujoco.MjModel.from_xml_path(str(scene))
        actuator_names = tuple(
            mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, index)
            for index in range(self.model.nu)
        )
        if actuator_names != tuple(JOINT_NAMES):
            raise ValueError(f"actuator order mismatch: {actuator_names}")
        if self.model.nu != training.ACTION_SIZE:
            raise ValueError("action dimension changed")
        apply_configuration(self.model, configuration)
        self.data = mujoco.MjData(self.model)
        # The ordering is intentional: recompute constants on default MjData,
        # then load the exact home keyframe.
        mujoco.mj_setConst(self.model, self.data)
        key_id = int(mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_KEY, "home"))
        if key_id < 0:
            raise ValueError("home keyframe missing")
        key_ctrl = np.asarray(self.model.key_ctrl[key_id], dtype=np.float64)
        if not np.array_equal(key_ctrl, HOME_RAD):
            raise ValueError("home keyframe control changed")
        self.data.qpos[:] = self.model.key_qpos[key_id]
        self.data.qvel[:] = 0.0
        self.data.ctrl[:] = HOME_RAD
        mujoco.mj_forward(self.model, self.data)
        self.qpos_addresses = np.asarray(
            [
                int(self.model.jnt_qposadr[self.model.joint(name).id])
                for name in JOINT_NAMES
            ],
            dtype=np.int64,
        )
        self.qvel_addresses = np.asarray(
            [
                int(self.model.jnt_dofadr[self.model.joint(name).id])
                for name in JOINT_NAMES
            ],
            dtype=np.int64,
        )
        self.backlash_addresses = []
        for name in JOINT_NAMES:
            joint_id = int(
                mujoco.mj_name2id(
                    self.model, mujoco.mjtObj.mjOBJ_JOINT, f"{name}_backlash"
                )
            )
            self.backlash_addresses.append(
                None if joint_id < 0 else int(self.model.jnt_qposadr[joint_id])
            )
        self.plant = plant
        self.bridge = ActuatorBridgeModel(
            plant_parameters(preregistration, plant),
            initial_target=HOME_RAD,
            home_target=HOME_RAD,
        )
        self.observer = observer_type(canonical_fit, HOME_RAD)
        zero = np.zeros(training.ACTION_SIZE, dtype=np.float32)
        self.history = [zero.copy() for _ in range(4)]
        self.overcurrent_streak = np.zeros(training.ACTION_SIZE, dtype=np.int64)
        self.gyro_xy_norms: list[float] = []
        self.valid_ticks = 0
        self.maximum_abs_tilt = 0.0
        self.minimum_base_z = float(self.data.qpos[2])
        self.maximum_torque_nm = 0.0
        self.maximum_current_a = 0.0
        self.maximum_observer_physical_separation_rad = 0.0
        self.initial_contacts = contact_state(mujoco, self.model, self.data)

    @property
    def previous_action(self) -> np.ndarray:
        return self.history[0].copy()

    def joint_position(self) -> np.ndarray:
        position = np.asarray(
            self.data.qpos[self.qpos_addresses], dtype=np.float64
        ).copy()
        for index, address in enumerate(self.backlash_addresses):
            if address is not None:
                position[index] += float(self.data.qpos[address])
        return position

    def observation(self) -> np.ndarray:
        gyro = sensor_vector(self.mujoco, self.model, self.data, "gyro")
        accelerometer = sensor_vector(
            self.mujoco, self.model, self.data, "accelerometer"
        )
        contacts = np.asarray(
            contact_state(self.mujoco, self.model, self.data), dtype=np.float32
        )
        parts = (
            gyro,
            accelerometer,
            np.zeros(7, dtype=np.float64),
            self.joint_position() - HOME_RAD,
            np.asarray(self.data.qvel[self.qvel_addresses], dtype=np.float64) * 0.05,
            self.history[1],
            self.history[2],
            self.history[3],
            self.observer.value,
            contacts,
            np.asarray([1.0, 0.0], dtype=np.float64),
            np.zeros(14, dtype=np.float64),
        )
        observation = np.concatenate(parts).astype(np.float32)
        if observation.shape != (training.OBS_SIZE,):
            raise ValueError(f"observation shape changed: {observation.shape}")
        if not np.all(np.isfinite(observation)):
            raise FloatingPointError("nonfinite observation")
        return observation

    def _validity(self) -> tuple[bool, dict[str, Any]]:
        state_arrays = {
            "qpos": np.asarray(self.data.qpos),
            "qvel": np.asarray(self.data.qvel),
            "actuator_force": np.asarray(self.data.actuator_force),
            "sensordata": np.asarray(self.data.sensordata),
            "ctrl": np.asarray(self.data.ctrl),
        }
        nonfinite = [
            name
            for name, value in state_arrays.items()
            if not np.all(np.isfinite(value))
        ]
        if nonfinite:
            raise FloatingPointError(f"nonfinite MuJoCo transition state: {nonfinite}")
        contacts = contact_state(self.mujoco, self.model, self.data)
        roll, pitch = roll_pitch_wxyz(np.asarray(self.data.qpos[3:7], dtype=np.float64))
        torque = np.abs(np.asarray(self.data.actuator_force, dtype=np.float64))
        current = torque / CURRENT_NM_PER_A
        self.overcurrent_streak = update_overcurrent_streak(
            self.overcurrent_streak, current
        )
        gyro_xy_norm = float(
            np.linalg.norm(
                sensor_vector(self.mujoco, self.model, self.data, "gyro")[:2]
            )
        )
        self.gyro_xy_norms.append(gyro_xy_norm)
        self.minimum_base_z = min(self.minimum_base_z, float(self.data.qpos[2]))
        self.maximum_abs_tilt = max(self.maximum_abs_tilt, abs(roll), abs(pitch))
        self.maximum_torque_nm = max(self.maximum_torque_nm, float(np.max(torque)))
        self.maximum_current_a = max(self.maximum_current_a, float(np.max(current)))
        checks = support_checks(
            contacts=contacts,
            base_z_m=float(self.data.qpos[2]),
            roll_rad=roll,
            pitch_rad=pitch,
            torque_nm=torque,
            current_a=current,
            overcurrent_streak=self.overcurrent_streak,
            finite=True,
        )
        return all(checks.values()), {
            "checks": checks,
            "contacts": list(contacts),
            "base_z_m": float(self.data.qpos[2]),
            "roll_rad": roll,
            "pitch_rad": pitch,
            "gyro_xy_norm_rad_s": gyro_xy_norm,
            "maximum_torque_nm": float(np.max(torque)),
            "maximum_current_a": float(np.max(current)),
            "maximum_overcurrent_streak_ticks": int(np.max(self.overcurrent_streak)),
        }

    def step(
        self, action: np.ndarray
    ) -> tuple[bool, np.ndarray | None, dict[str, Any]]:
        action = np.asarray(action, dtype=np.float32)
        if action.shape != (training.ACTION_SIZE,) or not np.all(np.isfinite(action)):
            raise ValueError("invalid realized action")
        expected = bounded_action_numpy(action, self.previous_action)
        if not np.array_equal(action, expected):
            raise ValueError("realized action violates graph boundary")
        sent_target = HOME_RAD + action.astype(np.float64) * ACTION_SCALE_RAD
        applied_target = self.bridge.step(sent_target, CONTROL_DT_S)
        observed_target = self.observer.step(sent_target, CONTROL_DT_S)
        if not np.all(np.isfinite(applied_target)) or not np.all(
            np.isfinite(observed_target)
        ):
            raise FloatingPointError("nonfinite bridge or observer target")
        self.maximum_observer_physical_separation_rad = max(
            self.maximum_observer_physical_separation_rad,
            float(np.max(np.abs(observed_target - applied_target))),
        )
        self.data.ctrl[:] = applied_target
        for _ in range(PHYSICS_SUBSTEPS):
            self.mujoco.mj_step(self.model, self.data)
        valid, evidence = self._validity()
        evidence.update(
            {
                "sent_target_sha256": array_sha256(sent_target),
                "physical_applied_target_sha256": array_sha256(applied_target),
                "fixed_p30_observer_target_sha256": array_sha256(observed_target),
            }
        )
        if not valid:
            return False, None, evidence
        self.history = [action.copy(), *self.history[:3]]
        self.valid_ticks += 1
        return True, self.observation(), evidence

    def summary(self) -> dict[str, Any]:
        final_window = self.gyro_xy_norms[-FINAL_GYRO_WINDOW_TICKS:]
        return {
            "plant": self.plant,
            "initial_contacts": list(self.initial_contacts),
            "valid_ticks": self.valid_ticks,
            "minimum_base_z_m": self.minimum_base_z,
            "maximum_abs_tilt_rad": self.maximum_abs_tilt,
            "maximum_torque_nm": self.maximum_torque_nm,
            "maximum_current_a": self.maximum_current_a,
            "maximum_overcurrent_streak_ticks": int(np.max(self.overcurrent_streak)),
            "maximum_final_window_gyro_xy_norm_rad_s": (
                max(final_window) if final_window else math.inf
            ),
            "maximum_fixed_observer_physical_separation_rad": (
                self.maximum_observer_physical_separation_rad
            ),
        }


def prng_for(
    stage: int, environment: int
) -> tuple[np.random.Generator, dict[str, Any]]:
    sequence = np.random.SeedSequence([SMOKE_SEED, stage, environment])
    receipt = {
        "algorithm": "NumPy PCG64",
        "seed_sequence_entropy": [SMOKE_SEED, stage, environment],
        "seed_sequence_state_u32": sequence.generate_state(4).astype(int).tolist(),
    }
    return np.random.Generator(np.random.PCG64(sequence)), receipt


def stage1_rollout(
    mujoco: Any,
    scene: Path,
    population: Sequence[Mapping[str, Any]],
    preregistration: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]], dict[str, Any]]:
    shape = (SMOKE_ENVIRONMENTS, SMOKE_TICKS)
    observations = np.zeros((*shape, training.OBS_SIZE), dtype=np.float32)
    previous_actions = np.zeros((*shape, training.ACTION_SIZE), dtype=np.float32)
    realized_actions = np.zeros((*shape, training.ACTION_SIZE), dtype=np.float32)
    targets = np.zeros((*shape, int(training.AUXILIARY_INDICES.size)), dtype=np.float32)
    valid_mask = np.zeros(shape, dtype=np.float32)
    receipts: list[dict[str, Any]] = []
    ternary_counts: Counter[int] = Counter()
    chain_exact = True
    observer_slot_exact = True
    for environment, configuration in enumerate(population):
        plant = PLANTS[environment % 2]
        rng, rng_receipt = prng_for(1, environment)
        episode = Episode(
            mujoco,
            scene,
            configuration,
            plant,
            preregistration,
            observer_type,
            canonical_fit,
        )
        if episode.initial_contacts != (1, 1):
            raise ValueError(
                f"{configuration['id']} does not start with both feet loaded"
            )
        terminal = None
        for tick in range(SMOKE_TICKS):
            observation = episode.observation()
            previous = episode.previous_action
            ternary = rng.integers(0, 3, size=training.ACTION_SIZE) - 1
            ternary_counts.update(int(value) for value in ternary)
            raw = previous + (
                ternary.astype(np.float32)
                * np.float32(0.25)
                * np.asarray(networks.INTERNAL_ACTION_DELTA, dtype=np.float32)
            )
            realized = bounded_action_numpy(raw, previous)
            valid, next_observation, evidence = episode.step(realized)
            if not valid:
                terminal = {"tick": tick, **evidence}
                break
            if next_observation is None:
                raise AssertionError("valid transition lacks next observation")
            observations[environment, tick] = observation
            previous_actions[environment, tick] = previous
            realized_actions[environment, tick] = realized
            targets[environment, tick] = next_observation[training.AUXILIARY_INDICES]
            valid_mask[environment, tick] = 1.0
            chain_exact &= np.array_equal(episode.previous_action, realized)
            observer_slot_exact &= np.array_equal(
                next_observation[83:97], episode.observer.value.astype(np.float32)
            )
        receipts.append(
            {
                "environment": environment,
                "configuration_id": configuration["id"],
                "configuration_sha256": canonical_sha256(configuration),
                "plant": plant,
                "prng": rng_receipt,
                "terminal": terminal,
                "episode": episode.summary(),
            }
        )
    if not np.any(valid_mask):
        raise ValueError("stage 1 collected no valid transitions")
    valid_targets = targets[valid_mask.astype(bool)].astype(np.float64)
    target_mean64 = np.mean(valid_targets, axis=0, dtype=np.float64)
    empirical_std64 = np.std(valid_targets, axis=0, dtype=np.float64, ddof=0)
    target_std64 = np.maximum(empirical_std64, 1.0e-6)
    normalization = {
        "population": "all valid Stage-1 smoke transitions only",
        "heldout_rows": 0,
        "dtype": "float64 population mean/std (ddof=0), floor 1e-6, cast float32",
        "valid_rows": int(np.sum(valid_mask)),
        "mean_float64_sha256": array_sha256(target_mean64),
        "empirical_std_float64_sha256": array_sha256(empirical_std64),
        "floored_std_float64_sha256": array_sha256(target_std64),
        "floored_fields": int(np.sum(empirical_std64 < 1.0e-6)),
        "mean": target_mean64.astype(np.float32),
        "std": target_std64.astype(np.float32),
    }
    return (
        {
            "observations": observations,
            "previous_actions": previous_actions,
            "realized_actions": realized_actions,
            "targets": targets,
            "valid_mask": valid_mask,
        },
        receipts,
        {
            "ternary_counts": {str(key): ternary_counts[key] for key in (-1, 0, 1)},
            "realized_action_chain_exact": bool(chain_exact),
            "fixed_p30_observer_slot_exact": bool(observer_slot_exact),
            "normalization": normalization,
        },
    )


def stage2_rollout(
    mujoco: Any,
    scene: Path,
    population: Sequence[Mapping[str, Any]],
    preregistration: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    parameters: Mapping[str, Any],
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]], np.ndarray]:
    import jax.numpy as jnp

    shape = (SMOKE_ENVIRONMENTS, SMOKE_TICKS)
    hidden = np.zeros((*shape, training.HIDDEN_SIZE), dtype=np.float32)
    raw_samples = np.zeros((*shape, training.ACTION_SIZE), dtype=np.float32)
    old_log_probability = np.zeros(shape, dtype=np.float32)
    values = np.zeros(shape, dtype=np.float32)
    rewards = np.zeros(shape, dtype=np.float32)
    sample_mask = np.zeros(shape, dtype=np.float32)
    valid_transition_mask = np.zeros(shape, dtype=np.float32)
    done = np.zeros(shape, dtype=np.float32)
    observation_bank: list[np.ndarray] = []
    receipts: list[dict[str, Any]] = []
    for environment, configuration in enumerate(population):
        plant = PLANTS[environment % 2]
        rng, rng_receipt = prng_for(2, environment)
        episode = Episode(
            mujoco,
            scene,
            configuration,
            plant,
            preregistration,
            observer_type,
            canonical_fit,
        )
        if episode.initial_contacts != (1, 1):
            raise ValueError(
                f"{configuration['id']} does not start with both feet loaded"
            )
        h_in = np.zeros(training.HIDDEN_SIZE, dtype=np.float32)
        terminal = None
        for tick in range(SMOKE_TICKS):
            observation = episode.observation()
            previous = episode.previous_action
            h_out, _ = training.response_step(
                parameters,
                jnp.asarray(observation),
                jnp.asarray(previous),
                jnp.asarray(h_in),
                jnp.zeros((training.ACTION_SIZE,), dtype=jnp.float32),
            )
            epsilon = rng.normal(0.0, 1.0, training.ACTION_SIZE).astype(np.float32)
            action, raw, log_probability, value = training.sample_stage2_action(
                parameters,
                h_out,
                jnp.asarray(previous),
                jnp.asarray(epsilon),
            )
            action_np = np.asarray(action, dtype=np.float32)
            valid, _, evidence = episode.step(action_np)
            hidden[environment, tick] = np.asarray(h_out, dtype=np.float32)
            raw_samples[environment, tick] = np.asarray(raw, dtype=np.float32)
            old_log_probability[environment, tick] = float(log_probability)
            values[environment, tick] = float(value)
            sample_mask[environment, tick] = 1.0
            observation_bank.append(observation.copy())
            if not valid:
                # The failure-causing action is an attempted PPO transition.  It
                # receives reward zero and done=1, while its invalid next state
                # is never committed or used as a Stage-1 auxiliary target.
                done[environment, tick] = 1.0
                terminal = {"tick": tick, **evidence}
                break
            rewards[environment, tick] = 1.0
            valid_transition_mask[environment, tick] = 1.0
            h_in = np.asarray(h_out, dtype=np.float32)
        summary = episode.summary()
        settled = bool(
            episode.valid_ticks == SMOKE_TICKS
            and summary["maximum_final_window_gyro_xy_norm_rad_s"]
            <= FINAL_GYRO_LIMIT_RAD_S
        )
        if settled:
            rewards[environment, SMOKE_TICKS - 1] += np.float32(TERMINAL_BONUS)
        if episode.valid_ticks == SMOKE_TICKS:
            done[environment, SMOKE_TICKS - 1] = 1.0
        receipts.append(
            {
                "environment": environment,
                "configuration_id": configuration["id"],
                "configuration_sha256": canonical_sha256(configuration),
                "plant": plant,
                "prng": rng_receipt,
                "terminal": terminal,
                "terminal_success_bonus_applied": settled,
                "episode": summary,
            }
        )
    if not np.any(valid_transition_mask):
        raise ValueError("stage 2 collected no valid transitions")
    advantages = np.zeros(shape, dtype=np.float32)
    returns = np.zeros(shape, dtype=np.float32)
    for environment in range(SMOKE_ENVIRONMENTS):
        count = int(np.sum(sample_mask[environment]))
        gae = np.float32(0.0)
        for tick in range(count - 1, -1, -1):
            nonterminal = np.float32(1.0 - done[environment, tick])
            next_value = values[environment, tick + 1] if tick + 1 < count else 0.0
            delta = (
                rewards[environment, tick]
                + np.float32(training.PPO_GAMMA) * np.float32(next_value) * nonterminal
                - values[environment, tick]
            )
            gae = delta + (
                np.float32(training.PPO_GAMMA)
                * np.float32(training.PPO_GAE_LAMBDA)
                * nonterminal
                * gae
            )
            advantages[environment, tick] = gae
            returns[environment, tick] = gae + values[environment, tick]
    valid_advantages = advantages[sample_mask.astype(bool)].astype(np.float64)
    advantage_mean = float(np.mean(valid_advantages, dtype=np.float64))
    advantage_std = max(
        float(np.std(valid_advantages, dtype=np.float64, ddof=0)), 1.0e-6
    )
    advantages = np.where(
        sample_mask > 0,
        (advantages - np.float32(advantage_mean)) / np.float32(advantage_std),
        np.float32(0.0),
    ).astype(np.float32)
    if len(observation_bank) < SMOKE_TICKS:
        raise ValueError("fewer than 250 valid observations for ONNX chain check")
    return (
        {
            "hidden": hidden,
            "raw_samples": raw_samples,
            "old_log_probability": old_log_probability,
            "returns": returns,
            "advantages": advantages,
            "valid_mask": sample_mask,
            "valid_transition_mask": valid_transition_mask,
            "done": done,
        },
        receipts,
        np.asarray(observation_bank[:SMOKE_TICKS], dtype=np.float32),
    )


def save_restore_checkpoint(
    path: Path,
    parameters: Mapping[str, Any],
    stage1_adam: Mapping[str, Any],
    stage2_adam: Mapping[str, Any],
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    arrays: dict[str, np.ndarray] = {
        f"parameter.{key}": np.asarray(value)
        for key, value in sorted(parameters.items())
    }
    arrays["stage1_adam.count"] = np.asarray(stage1_adam["count"])
    arrays["stage2_adam.count"] = np.asarray(stage2_adam["count"])
    for label, state in (("stage1", stage1_adam), ("stage2", stage2_adam)):
        for moment in ("m", "v"):
            for key, value in sorted(state[moment].items()):
                arrays[f"{label}_adam.{moment}.{key}"] = np.asarray(value)
    arrays["target_mean"] = np.asarray(target_mean, dtype=np.float32)
    arrays["target_std"] = np.asarray(target_std, dtype=np.float32)
    np.savez_compressed(path, **arrays)
    with np.load(path, allow_pickle=False) as loaded:
        restored = {name: loaded[name].copy() for name in loaded.files}
    exact = set(restored) == set(arrays) and all(
        np.array_equal(restored[name], value) for name, value in arrays.items()
    )
    restored_parameters = {
        key.removeprefix("parameter."): value
        for key, value in restored.items()
        if key.startswith("parameter.")
    }
    return restored_parameters, {
        "all_train_state_arrays_bit_exact": bool(exact),
        "array_count": len(arrays),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def onnx_contract(
    graph: Path,
    parameters: Mapping[str, Any],
    observations: np.ndarray,
) -> dict[str, Any]:
    import jax.numpy as jnp
    import onnx
    from onnx import numpy_helper
    import onnxruntime as ort

    model = onnx.load(graph)
    onnx.checker.check_model(model)
    inputs = [
        {
            "name": value.name,
            "shape": [
                dimension.dim_value for dimension in value.type.tensor_type.shape.dim
            ],
        }
        for value in model.graph.input
    ]
    outputs = [
        {
            "name": value.name,
            "shape": [
                dimension.dim_value for dimension in value.type.tensor_type.shape.dim
            ],
        }
        for value in model.graph.output
    ]
    expected_inputs = [
        {"name": "obs", "shape": [1, 115]},
        {"name": "previous_action", "shape": [1, 14]},
        {"name": "h_in", "shape": [1, 64]},
    ]
    expected_outputs = [
        {"name": "calibration_actions", "shape": [1, 14]},
        {"name": "previous_action_out", "shape": [1, 14]},
        {"name": "h_out", "shape": [1, 64]},
    ]
    inventory = [initializer.name for initializer in model.graph.initializer]
    inventory.extend(node.name for node in model.graph.node)
    inventory.extend(value for node in model.graph.node for value in node.input)
    inventory.extend(value for node in model.graph.node for value in node.output)
    folded_inventory = "\n".join(inventory).lower()
    forbidden = (
        "auxiliary",
        "training_only",
        "log_std",
        "value_weight",
        "value_bias",
        "epsilon",
        "ternary",
        "configuration",
        "inertia",
        "mass",
        "com_",
    )
    forbidden_present = [token for token in forbidden if token in folded_inventory]
    session = ort.InferenceSession(str(graph), providers=["CPUExecutionProvider"])
    previous_jax = np.zeros((1, training.ACTION_SIZE), dtype=np.float32)
    hidden_jax = np.zeros((1, training.HIDDEN_SIZE), dtype=np.float32)
    previous_ort = previous_jax.copy()
    hidden_ort = hidden_jax.copy()
    maximum_error = 0.0
    state_equals_action = True
    all_chain_outputs_finite = True
    for observation in observations:
        if not np.all(np.isfinite(observation)):
            raise FloatingPointError("nonfinite ONNX contract observation")
        action_jax, previous_out_jax, hidden_out_jax = networks.calibrator_step(
            parameters,
            jnp.asarray(observation[None, :]),
            jnp.asarray(previous_jax),
            jnp.asarray(hidden_jax),
        )
        ort_outputs = session.run(
            None,
            {
                "obs": observation[None, :],
                "previous_action": previous_ort,
                "h_in": hidden_ort,
            },
        )
        expected = (
            np.asarray(action_jax, dtype=np.float32),
            np.asarray(previous_out_jax, dtype=np.float32),
            np.asarray(hidden_out_jax, dtype=np.float32),
        )
        for observed, reference in zip(ort_outputs, expected):
            pair_finite = bool(
                np.all(np.isfinite(observed)) and np.all(np.isfinite(reference))
            )
            all_chain_outputs_finite &= pair_finite
            if not pair_finite:
                raise FloatingPointError("nonfinite JAX or ONNX chain output")
            error = float(np.max(np.abs(np.asarray(observed) - reference)))
            if not math.isfinite(error):
                raise FloatingPointError("nonfinite JAX/ONNX comparison error")
            maximum_error = max(
                maximum_error,
                error,
            )
        state_equals_action &= np.array_equal(ort_outputs[0], ort_outputs[1])
        previous_jax = expected[1]
        hidden_jax = expected[2]
        previous_ort = np.asarray(ort_outputs[1], dtype=np.float32)
        hidden_ort = np.asarray(ort_outputs[2], dtype=np.float32)
    initializer_finite = all(
        np.all(np.isfinite(numpy_helper.to_array(initializer)))
        for initializer in model.graph.initializer
    )
    return {
        "path": str(graph),
        "sha256": sha256(graph),
        "bytes": graph.stat().st_size,
        "inputs": inputs,
        "outputs": outputs,
        "abi_exact": inputs == expected_inputs and outputs == expected_outputs,
        "initializer_count": len(model.graph.initializer),
        "all_initializers_finite": bool(initializer_finite),
        "all_chain_outputs_finite": bool(all_chain_outputs_finite),
        "forbidden_training_or_privileged_tokens": forbidden_present,
        "training_only_tensors_absent": not forbidden_present,
        "chain_ticks": int(len(observations)),
        "jax_onnx_max_abs_error": maximum_error,
        "jax_onnx_at_most_1e_7": maximum_error <= 1.0e-7,
        "previous_action_out_equals_action_bit_exact": bool(state_equals_action),
    }


def force_range_contract(mujoco: Any, scene: Path) -> dict[str, Any]:
    model = mujoco.MjModel.from_xml_path(str(scene))
    ranges = np.asarray(model.actuator_forcerange, dtype=np.float64)
    limited = np.asarray(model.actuator_forcelimited, dtype=bool)
    represented = float(np.max(np.abs(ranges)))
    return {
        "actuator_count": int(model.nu),
        "all_force_limited": bool(np.all(limited)),
        "force_ranges_nm": ranges.tolist(),
        "maximum_absolute_represented_nm": represented,
        "independent_threshold_nm": TORQUE_LIMIT_NM,
        "all_ranges_within_independent_threshold": bool(
            np.all(np.abs(ranges) <= TORQUE_LIMIT_NM)
        ),
    }


def observer_plant_canary(
    preregistration: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
) -> dict[str, Any]:
    p30_observer = observer_type(canonical_fit, HOME_RAD)
    p31_observer = observer_type(canonical_fit, HOME_RAD)
    p30_plant = ActuatorBridgeModel(
        plant_parameters(preregistration, PLANTS[0]), HOME_RAD, HOME_RAD
    )
    p31_plant = ActuatorBridgeModel(
        plant_parameters(preregistration, PLANTS[1]), HOME_RAD, HOME_RAD
    )
    generator, _ = prng_for(99, 0)
    previous = np.zeros(training.ACTION_SIZE, dtype=np.float32)
    observer_exact = True
    maximum_plant_separation = 0.0
    for _ in range(128):
        raw = previous + generator.uniform(-0.15, 0.15, training.ACTION_SIZE).astype(
            np.float32
        )
        action = bounded_action_numpy(raw, previous)
        target = HOME_RAD + action.astype(np.float64) * ACTION_SCALE_RAD
        observer_exact &= np.array_equal(
            p30_observer.step(target), p31_observer.step(target)
        )
        maximum_plant_separation = max(
            maximum_plant_separation,
            float(np.max(np.abs(p30_plant.step(target) - p31_plant.step(target)))),
        )
        previous = action
    return {
        "identical_sent_targets": True,
        "fixed_p30_observer_bit_exact_across_hidden_plant_choice": bool(observer_exact),
        "hidden_physical_plants_are_distinct": maximum_plant_separation > 0.0,
        "maximum_hidden_plant_separation_rad": maximum_plant_separation,
    }


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("status") != "PASS_WINNER_V12_CALIBRATOR_CPU_SMOKE_CONTRACT":
        raise ValueError("smoke contract is not passed/frozen")
    if contract.get("decision") != "AUTHORIZE_ONE_WINNER_V12_CPU_SMOKE_ONLY":
        raise ValueError("smoke authority changed")
    for item in contract["sources"].values():
        path = ROOT / item["path"]
        observed = lf_sha256(path) if item["hash_mode"] == "lf" else sha256(path)
        if observed != item["sha256"]:
            raise ValueError(f"source hash mismatch: {item['path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.work_root.exists():
        raise FileExistsError(f"refusing to reuse smoke work root: {args.work_root}")
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite smoke result: {args.output}")
    args.work_root.mkdir(parents=True)
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    validate_contract(contract)
    software_versions = validate_software_versions(contract)
    if sha256(args.policy_half) != PROTECTED_POLICY_HASHES["half"]:
        raise ValueError("protected half policy hash mismatch")
    if sha256(args.policy_final) != PROTECTED_POLICY_HASHES["final"]:
        raise ValueError("protected final policy hash mismatch")
    protected_before = {
        "half": sha256(args.policy_half),
        "final": sha256(args.policy_final),
    }
    if git_output(args.playground_root, "rev-parse", "HEAD") != CONTROL_COMMIT:
        raise ValueError("Playground commit mismatch")
    playground_receipt = validate_playground_tree(args.playground_root)
    model_path = args.playground_root / MODEL_RELATIVE
    scene_path = args.playground_root / SCENE_RELATIVE
    if sha256(model_path) != MODEL_SHA256 or sha256(scene_path) != SCENE_SHA256:
        raise ValueError("Winner-v10 XML/scene hash mismatch")
    if lf_sha256(P30_FIT) != P30_FIT_LF_SHA256:
        raise ValueError("P30 fit canonical hash mismatch")
    canonical_fit = args.work_root / "fixed_target_p30_actuator_fit_lf.json"
    canonical_fit.write_bytes(P30_FIT.read_bytes().replace(b"\r\n", b"\n"))
    if sha256(canonical_fit) != P30_FIT_LF_SHA256:
        raise AssertionError("canonical P30 fit reconstruction failed")
    observer_type = load_runtime_observer(canonical_fit)

    preregistration = json.loads(CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN_PREREG.read_text(encoding="utf-8"))
    population = domain["evaluation_matrix"]["fixed_anchors"][:SMOKE_ENVIRONMENTS]
    expected_ids = contract["smoke_population"]["configuration_ids"]
    if [row["id"] for row in population] != expected_ids:
        raise ValueError("smoke population drifted")
    if any(row["id"].startswith("HELDOUT") for row in population):
        raise ValueError("heldout configuration entered smoke training")

    import jax
    import jax.numpy as jnp
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v12 smoke requires CPU-only JAX")
    action_bound_probe_rng = np.random.default_rng(120120)
    bound_exact = True
    for _ in range(256):
        raw = action_bound_probe_rng.uniform(-1.5, 1.5, 14).astype(np.float32)
        previous = action_bound_probe_rng.uniform(-1.0, 1.0, 14).astype(np.float32)
        bound_exact &= np.array_equal(
            bounded_action_numpy(raw, previous),
            np.asarray(
                training.bounded_action(jnp.asarray(raw), jnp.asarray(previous))
            ),
        )

    initial_parameters = training.initialize_training_parameters()
    locomotion_adapter = networks.initialize_locomotion_adapter_parameters()
    initial_parameter_hash = tree_sha256(initial_parameters)
    locomotion_adapter_hash = tree_sha256(locomotion_adapter)
    initial_action_hash = tree_sha256(
        {key: initial_parameters[key] for key in training.DEPLOYABLE_ACTION_KEYS}
    )

    stage1_batch_np, stage1_episodes, stage1_rollout_evidence = stage1_rollout(
        mujoco,
        scene_path,
        population,
        preregistration,
        observer_type,
        canonical_fit,
    )
    normalization = stage1_rollout_evidence.pop("normalization")
    target_mean = np.asarray(normalization.pop("mean"), dtype=np.float32)
    target_std = np.asarray(normalization.pop("std"), dtype=np.float32)
    stage1_batch = {key: jnp.asarray(value) for key, value in stage1_batch_np.items()}
    stage1_before = training.stage1_parameters(initial_parameters)
    stage1_adam_before = training.adam_initialize(stage1_before)
    stage1_loss_grad = jax.value_and_grad(training.stage1_loss)
    stage1_loss_before, stage1_gradients = stage1_loss_grad(
        stage1_before,
        stage1_batch,
        jnp.asarray(target_mean),
        jnp.asarray(target_std),
    )
    stage1_after, stage1_adam_after = training.adam_step(
        stage1_before,
        stage1_gradients,
        stage1_adam_before,
        learning_rate=training.STAGE1_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    after_stage1 = training.merge_stage1(initial_parameters, stage1_after)
    stage1_loss_after = training.stage1_loss(
        stage1_after,
        stage1_batch,
        jnp.asarray(target_mean),
        jnp.asarray(target_std),
    )
    stage1_deltas = training.leaf_max_abs_delta(stage1_before, stage1_after)
    stage1_gradient_max = {
        key: float(np.max(np.abs(np.asarray(value))))
        for key, value in stage1_gradients.items()
    }
    action_after_stage1_hash = tree_sha256(
        {key: after_stage1[key] for key in training.DEPLOYABLE_ACTION_KEYS}
    )

    stage2_batch_np, stage2_episodes, onnx_observations = stage2_rollout(
        mujoco,
        scene_path,
        population,
        preregistration,
        observer_type,
        canonical_fit,
        after_stage1,
    )
    stage2_batch = {key: jnp.asarray(value) for key, value in stage2_batch_np.items()}
    stage2_before = training.stage2_parameters(after_stage1)
    stage2_adam_before = training.adam_initialize(stage2_before)

    def stage2_objective(parameters: Mapping[str, Any]):
        return training.stage2_ppo_loss(
            parameters,
            stage2_batch,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    (stage2_loss_before, stage2_metrics_before), stage2_gradients = jax.value_and_grad(
        stage2_objective, has_aux=True
    )(stage2_before)
    stage2_after, stage2_adam_after = training.adam_step(
        stage2_before,
        stage2_gradients,
        stage2_adam_before,
        learning_rate=training.STAGE2_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    stage2_after = training.clamp_stage2_parameters(stage2_after)
    final_parameters = training.merge_stage2(after_stage1, stage2_after)
    stage2_loss_after, stage2_metrics_after = stage2_objective(stage2_after)
    stage2_deltas = training.leaf_max_abs_delta(stage2_before, stage2_after)
    encoder_before_stage2_hash = tree_sha256(
        {key: after_stage1[key] for key in training.ENCODER_AUXILIARY_KEYS}
    )
    encoder_after_stage2_hash = tree_sha256(
        {key: final_parameters[key] for key in training.ENCODER_AUXILIARY_KEYS}
    )

    checkpoint_path = args.work_root / "winner_v12_calibrator_smoke_checkpoint.npz"
    restored_parameters, checkpoint = save_restore_checkpoint(
        checkpoint_path,
        final_parameters,
        stage1_adam_after,
        stage2_adam_after,
        target_mean,
        target_std,
    )
    restored_exact = set(restored_parameters) == set(final_parameters) and all(
        np.array_equal(restored_parameters[key], np.asarray(final_parameters[key]))
        for key in final_parameters
    )
    graph_path = args.work_root / "winner_v12_calibrator_after_smoke.onnx"
    networks.export_calibrator_onnx(
        training.deployable_parameters(restored_parameters), graph_path
    )
    graph = onnx_contract(
        graph_path,
        training.deployable_parameters(restored_parameters),
        onnx_observations,
    )
    protected_after = {
        "half": sha256(args.policy_half),
        "final": sha256(args.policy_final),
    }
    stage1_valid = int(np.sum(stage1_batch_np["valid_mask"]))
    stage2_samples = int(np.sum(stage2_batch_np["valid_mask"]))
    stage2_valid = int(np.sum(stage2_batch_np["valid_transition_mask"]))
    terminal_transition_encoding_exact = True
    for environment, episode in enumerate(stage2_episodes):
        sample_count = int(np.sum(stage2_batch_np["valid_mask"][environment]))
        valid_count = int(np.sum(stage2_batch_np["valid_transition_mask"][environment]))
        done_indices = np.flatnonzero(stage2_batch_np["done"][environment])
        if episode["terminal"] is None:
            terminal_transition_encoding_exact &= bool(
                sample_count == valid_count == SMOKE_TICKS
                and np.array_equal(done_indices, np.asarray([SMOKE_TICKS - 1]))
            )
        else:
            terminal_tick = int(episode["terminal"]["tick"])
            terminal_transition_encoding_exact &= bool(
                sample_count == valid_count + 1 == terminal_tick + 1
                and np.array_equal(done_indices, np.asarray([terminal_tick]))
                and stage2_batch_np["valid_transition_mask"][environment, terminal_tick]
                == 0.0
                and stage2_batch_np["valid_mask"][environment, terminal_tick] == 1.0
            )
    plant_counts = Counter(row["plant"] for row in stage1_episodes)
    support_canary = support_boundary_canary()
    checks = {
        "software_versions_exact": software_versions["exact"],
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "exact_16_by_250_population": len(population) == SMOKE_ENVIRONMENTS
        and stage1_batch_np["valid_mask"].shape == (SMOKE_ENVIRONMENTS, SMOKE_TICKS),
        "population_includes_com_x_neg": "COM_X_NEG" in expected_ids,
        "no_heldout_population": not any(
            identifier.startswith("HELDOUT") for identifier in expected_ids
        ),
        "balanced_hidden_plants": plant_counts == Counter({PLANTS[0]: 8, PLANTS[1]: 8}),
        "all_initial_contacts_loaded": all(
            row["episode"]["initial_contacts"] == [1, 1]
            for row in stage1_episodes + stage2_episodes
        ),
        "action_boundary_numpy_jax_bit_exact": bool(bound_exact),
        "realized_action_chain_exact": stage1_rollout_evidence[
            "realized_action_chain_exact"
        ],
        "fixed_p30_observer_slot_exact": stage1_rollout_evidence[
            "fixed_p30_observer_slot_exact"
        ],
        "stage1_has_valid_transitions": stage1_valid > 0,
        "stage2_has_valid_transitions": stage2_valid > 0,
        "stage2_has_attempted_samples": stage2_samples >= stage2_valid > 0,
        "stage2_terminal_actions_retained_with_done": bool(
            terminal_transition_encoding_exact
        ),
        "support_boundary_canary_all_exact": all(support_canary.values()),
        "stage1_parameters_finite": training.finite_tree(stage1_after)
        and training.finite_tree(stage1_gradients),
        "stage1_losses_finite": math.isfinite(float(stage1_loss_before))
        and math.isfinite(float(stage1_loss_after)),
        "stage1_previous_action_gradient_nonzero": stage1_gradient_max[
            "previous_action_weight"
        ]
        > 0.0,
        "stage1_auxiliary_action_gradient_nonzero": stage1_gradient_max[
            "auxiliary_action_weight"
        ]
        > 0.0,
        "stage1_action_head_bit_exact": initial_action_hash == action_after_stage1_hash,
        "stage1_single_adam_update": int(stage1_adam_after["count"]) == 1,
        "stage2_parameters_finite": training.finite_tree(stage2_after)
        and training.finite_tree(stage2_gradients),
        "stage2_losses_metrics_finite": training.finite_tree(
            {
                "before": stage2_loss_before,
                "after": stage2_loss_after,
                **stage2_metrics_before,
                **{
                    f"after_{key}": value for key, value in stage2_metrics_after.items()
                },
            }
        ),
        "every_stage2_leaf_changed": all(
            stage2_deltas[key] > 0.0 for key in training.stage2_parameters(after_stage1)
        ),
        "stage2_encoder_auxiliary_bit_exact": encoder_before_stage2_hash
        == encoder_after_stage2_hash,
        "stage2_single_adam_update": int(stage2_adam_after["count"]) == 1,
        "log_std_clamp_respected": bool(
            np.all(
                np.asarray(stage2_after["training_only_log_std"])
                >= training.LOG_STD_MIN
            )
            and np.all(
                np.asarray(stage2_after["training_only_log_std"])
                <= training.LOG_STD_MAX
            )
        ),
        "all_parameters_finite": training.finite_tree(final_parameters),
        "checkpoint_all_state_bit_exact": checkpoint["all_train_state_arrays_bit_exact"]
        and restored_exact,
        "protected_policies_bit_exact_and_unused": protected_before
        == protected_after
        == PROTECTED_POLICY_HASHES,
        "locomotion_adapter_bit_exact_and_unused": tree_sha256(locomotion_adapter)
        == locomotion_adapter_hash,
        "onnx_abi_exact": graph["abi_exact"],
        "onnx_initializers_finite": graph["all_initializers_finite"],
        "onnx_chain_outputs_finite": graph["all_chain_outputs_finite"],
        "onnx_training_only_tensors_absent": graph["training_only_tensors_absent"],
        "onnx_jax_error_at_most_1e_7": graph["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph[
            "previous_action_out_equals_action_bit_exact"
        ],
    }
    fixed_observer_canary = observer_plant_canary(
        preregistration, observer_type, canonical_fit
    )
    checks["hidden_plant_does_not_select_observer"] = bool(
        fixed_observer_canary["fixed_p30_observer_bit_exact_across_hidden_plant_choice"]
        and fixed_observer_canary["hidden_physical_plants_are_distinct"]
    )
    force_ranges = force_range_contract(mujoco, scene_path)
    checks["xml_force_ranges_inside_independent_torque_limit"] = bool(
        force_ranges["actuator_count"] == 14
        and force_ranges["all_force_limited"]
        and force_ranges["all_ranges_within_independent_threshold"]
    )
    failed = [name for name, passed in checks.items() if not passed]
    passed = not failed
    payload = {
        "schema_version": "winner_v12.calibrator_cpu_smoke_result.v1",
        "status": (
            "PASS_WINNER_V12_CALIBRATOR_CPU_SMOKE"
            if passed
            else "HOLD_WINNER_V12_CALIBRATOR_CPU_SMOKE"
        ),
        "decision": (
            "AUTHORIZE_FULL_CALIBRATOR_TRAINING_PREREGISTRATION_ONLY"
            if passed
            else "STOP_WINNER_V12_CALIBRATOR_IMPLEMENTATION"
        ),
        "contract": {
            "path": str(args.contract),
            "canonical_lf_sha256": lf_sha256(args.contract),
            "hash_mode": "lf",
        },
        "environment": {
            "software_versions": software_versions,
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "mujoco_version": mujoco.__version__,
            "playground_commit": CONTROL_COMMIT,
            "model_sha256": sha256(model_path),
            "scene_sha256": sha256(scene_path),
            "composition_receipt": playground_receipt,
        },
        "execution": {
            "optimizer_updates": {"stage1": 1, "stage2": 1},
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "protected_policy_inference_calls": 0,
            "robot_or_rdk_access": 0,
            "retry_count": 0,
        },
        "smoke_population": {
            "configuration_ids": expected_ids,
            "configuration_hashes": [canonical_sha256(row) for row in population],
            "plant_counts": dict(plant_counts),
        },
        "prng_contract": {
            "root_seed": SMOKE_SEED,
            "derivation": "SeedSequence([120120, stage_id, environment_index]) -> PCG64",
            "stage1_id": 1,
            "stage2_id": 2,
        },
        "normalization": normalization,
        "stage1": {
            "valid_transitions": stage1_valid,
            "loss_before": float(stage1_loss_before),
            "loss_after": float(stage1_loss_after),
            "gradient_max_abs_by_leaf": stage1_gradient_max,
            "parameter_max_abs_delta_by_leaf": stage1_deltas,
            "rollout": stage1_rollout_evidence,
            "episodes": stage1_episodes,
        },
        "stage2": {
            "attempted_transition_samples": stage2_samples,
            "valid_transitions": stage2_valid,
            "terminal_invalid_transition_samples": stage2_samples - stage2_valid,
            "loss_before": float(stage2_loss_before),
            "loss_after": float(stage2_loss_after),
            "metrics_before": {
                key: float(value) for key, value in stage2_metrics_before.items()
            },
            "metrics_after": {
                key: float(value) for key, value in stage2_metrics_after.items()
            },
            "parameter_max_abs_delta_by_leaf": stage2_deltas,
            "episodes": stage2_episodes,
        },
        "parameter_hashes": {
            "initial_all": initial_parameter_hash,
            "after_stage1": tree_sha256(after_stage1),
            "final_all": tree_sha256(final_parameters),
            "final_deployable": tree_sha256(
                training.deployable_parameters(final_parameters)
            ),
            "locomotion_adapter_unchanged": locomotion_adapter_hash,
        },
        "fixed_observer_hidden_plant_canary": fixed_observer_canary,
        "support_boundary_canary": support_canary,
        "force_range_contract": force_ranges,
        "checkpoint": checkpoint,
        "onnx": graph,
        "checks": checks,
        "failed_checks": failed,
        "protected_policies": protected_after,
        "authority": {
            "full_training_executed": False,
            "formal_behavior_evaluation_executed": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate prospective full-calibrator training preregistration"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": failed,
                "stage1_valid_transitions": stage1_valid,
                "stage2_valid_transitions": stage2_valid,
                "stage2_attempted_transition_samples": stage2_samples,
                "onnx_jax_max_abs_error": graph["jax_onnx_max_abs_error"],
                "result_sha256": sha256(args.output),
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
