"""Strict, default-off runtime ABI for the protected ground-up winner.

This module contains no hardware access. It implements the external state the
115-D policy graph requires: projected-reference lookup, a fitted bridge
forward observer, and the explicit ONNX ``previous_action`` state.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import onnxruntime


JOINT_NAMES = (
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee",
    "left_ankle", "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee",
    "right_ankle",
)
POLICY_HASHES = {
    "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de",
    "0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece",
}
REFERENCE_TABLE_HASH = "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212"
FIT_HASHES = {
    "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b",
    "a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276",
}
HOME_TARGET_RAD = np.asarray(
    [
        0.002, 0.053, -0.630, 1.368, -0.784, 0.0, 0.0, 0.0, 0.0,
        -0.003, -0.065, 0.635, 1.379, -0.796,
    ],
    dtype=np.float32,
).astype(float)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _finite_vector(value: Sequence[float], size: int, label: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != (size,):
        raise ValueError(f"{label} must have shape ({size},), got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{label} contains nonfinite values")
    return array


@dataclass(frozen=True)
class JointActuatorParams:
    delay_ticks: int
    tau_s: float
    velocity_limit_rad_s: float


def _params_from_fit(fit: Mapping) -> list[JointActuatorParams]:
    joints = fit.get("primary", fit).get("joints", {})
    params = []
    for name in JOINT_NAMES:
        combined = joints.get(name, {}).get("combined")
        if combined is None:
            params.append(JointActuatorParams(0, 0.0, math.inf))
        else:
            params.append(
                JointActuatorParams(
                    max(0, int(combined.get("delay_ticks", 0))),
                    max(0.0, float(combined.get("tau_s", 0.0))),
                    max(0.0, float(combined.get("velocity_limit_rad_s", math.inf))),
                )
            )
    return params


class FittedBridgeObserver:
    """Exact delay/tau/velocity observer used by the frozen CPU evaluator."""

    def __init__(self, fit_path: str | Path, initial_target: Sequence[float]):
        self.fit_path = str(Path(fit_path).resolve())
        self.fit_sha256 = sha256_file(fit_path)
        if self.fit_sha256 not in FIT_HASHES:
            raise ValueError(f"uncontracted actuator fit SHA-256: {self.fit_sha256}")
        with open(fit_path) as handle:
            self.params = _params_from_fit(json.load(handle))
        self._value = _finite_vector(initial_target, 14, "initial_target").copy()
        home_error = float(np.max(np.abs(self._value - HOME_TARGET_RAD)))
        if home_error > 1e-7:
            raise ValueError(
                f"winner-v2 initial target differs from frozen home by {home_error} rad"
            )
        self._queues = [
            [float(self._value[index])] * (param.delay_ticks + 1)
            for index, param in enumerate(self.params)
        ]

    @property
    def value(self) -> np.ndarray:
        return self._value.copy()

    def step(self, sent_target: Sequence[float], dt_s: float = 0.02) -> np.ndarray:
        target = _finite_vector(sent_target, 14, "sent_target")
        if float(dt_s) != 0.02:
            raise ValueError(f"winner-v2 observer requires dt_s=0.02, got {dt_s}")
        next_value = self._value.copy()
        for index, param in enumerate(self.params):
            queue = self._queues[index]
            queue.append(float(target[index]))
            while len(queue) > param.delay_ticks + 1:
                queue.pop(0)
            delayed_target = queue[0]
            if param.tau_s > 0.0:
                alpha = 1.0 - math.exp(-0.02 / param.tau_s)
                desired = self._value[index] + alpha * (
                    delayed_target - self._value[index]
                )
            else:
                desired = delayed_target
            step = desired - self._value[index]
            max_step = param.velocity_limit_rad_s * 0.02
            if math.isfinite(max_step):
                step = max(-max_step, min(max_step, step))
            next_value[index] = self._value[index] + step
        self._value = next_value
        return self.value


class ProjectedReferenceTable:
    def __init__(self, path: str | Path):
        self.path = str(Path(path).resolve())
        self.sha256 = sha256_file(path)
        if self.sha256 != REFERENCE_TABLE_HASH:
            raise ValueError(f"uncontracted reference table SHA-256: {self.sha256}")
        table = np.load(path)
        self.commands = np.asarray(table["commands"], dtype=np.float32)
        self.actions = np.asarray(table["actions"], dtype=np.float32)
        if self.commands.shape != (240, 3) or self.actions.shape != (240, 27, 14):
            raise ValueError(
                f"reference table shapes are {self.commands.shape}/{self.actions.shape}"
            )

    def lookup(self, command3: Sequence[float], phase_index: int) -> np.ndarray:
        command = _finite_vector(command3, 3, "command3").astype(np.float32)
        if isinstance(phase_index, (float, np.floating)) and not float(phase_index).is_integer():
            raise ValueError(f"phase_index must be an integer, got {phase_index}")
        phase = int(phase_index) % 27
        if float(np.linalg.norm(command)) <= 0.01:
            return np.zeros(14, dtype=np.float32)
        command_index = int(np.argmin(np.sum(np.abs(self.commands - command), axis=1)))
        return self.actions[command_index, phase].copy()


def validate_winner_command(commands: Sequence[float]) -> np.ndarray:
    command = _finite_vector(commands, 7, "commands")
    if np.any(command[1:] != 0.0):
        raise ValueError("winner-v2 permits forward command only; y/yaw/head must be zero")
    x = float(command[0])
    if x != 0.0 and not 0.074 <= x <= 0.080:
        raise ValueError(f"winner-v2 forward command outside frozen band: {x}")
    return command


class WinnerV2ObservationAdapter:
    """Compose exact 115-D actor observations and own bridge observer state."""

    def __init__(
        self,
        fit_path: str | Path,
        reference_table_path: str | Path,
        initial_target: Sequence[float],
        *,
        phase_step: int = 1,
        action_filter_enabled: bool = False,
    ):
        if phase_step != 1:
            raise ValueError("winner-v2 requires one integer phase step per tick")
        if action_filter_enabled:
            raise ValueError("winner-v2 does not permit the optional action filter")
        self.observer = FittedBridgeObserver(fit_path, initial_target)
        self.reference = ProjectedReferenceTable(reference_table_path)

    def compose(
        self,
        canonical_observation_101: Sequence[float],
        commands: Sequence[float],
        phase_index: int,
    ) -> np.ndarray:
        canonical = _finite_vector(
            canonical_observation_101, 101, "canonical_observation_101"
        ).astype(np.float32)
        command = validate_winner_command(commands)
        canonical[83:97] = self.observer.value.astype(np.float32)
        reference = self.reference.lookup(command[:3], phase_index)
        result = np.concatenate([canonical, reference]).astype(np.float32)
        if result.shape != (115,) or not np.all(np.isfinite(result)):
            raise ValueError("invalid winner-v2 observation")
        return result

    def advance_sent_target(self, sent_target: Sequence[float]) -> np.ndarray:
        return self.observer.step(sent_target, 0.02)


class WinnerV2OnnxPolicy:
    """Stateful CPU-only ONNX runner with a fail-closed graph ABI."""

    def __init__(self, model_path: str | Path):
        self.onnx_model_path = str(Path(model_path).resolve())
        self.policy_sha256 = sha256_file(model_path)
        if self.policy_sha256 not in POLICY_HASHES:
            raise ValueError(f"uncontracted winner policy SHA-256: {self.policy_sha256}")
        self.ort_session = onnxruntime.InferenceSession(
            self.onnx_model_path, providers=["CPUExecutionProvider"]
        )
        if self.ort_session.get_providers() != ["CPUExecutionProvider"]:
            raise ValueError(f"non-CPU ONNX providers: {self.ort_session.get_providers()}")
        inputs = [(item.name, item.shape, item.type) for item in self.ort_session.get_inputs()]
        outputs = [(item.name, item.shape, item.type) for item in self.ort_session.get_outputs()]
        expected_inputs = [
            ("obs", [1, 115], "tensor(float)"),
            ("previous_action", [1, 14], "tensor(float)"),
        ]
        expected_outputs = [
            ("continuous_actions", [1, 14], "tensor(float)"),
            ("previous_action_out", [1, 14], "tensor(float)"),
        ]
        if inputs != expected_inputs or outputs != expected_outputs:
            raise ValueError(f"winner-v2 ONNX ABI mismatch: inputs={inputs}, outputs={outputs}")
        self.input_name = "obs"
        self.previous_action = np.zeros((1, 14), dtype=np.float32)

    def infer(self, observation: Sequence[float]) -> np.ndarray:
        obs = _finite_vector(observation, 115, "observation").astype(np.float32)[None]
        action, state = self.ort_session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": self.previous_action},
        )
        action = np.asarray(action, dtype=np.float32)
        state = np.asarray(state, dtype=np.float32)
        if action.shape != (1, 14) or state.shape != (1, 14):
            raise ValueError(f"winner-v2 output shape mismatch: {action.shape}/{state.shape}")
        if not np.all(np.isfinite(action)) or not np.all(np.isfinite(state)):
            raise ValueError("winner-v2 ONNX produced nonfinite output")
        self.previous_action = state.copy()
        return action[0].copy()
