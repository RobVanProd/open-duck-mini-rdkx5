#!/usr/bin/env python3
"""Offline actuator bridge model for Open Duck sim-to-real evaluation.

This module is intentionally pure Python/NumPy so it can be used by workstation
analysis tools without importing JAX, MuJoCo, or robot runtime packages.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np


JOINT_NAMES = [
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
]

PITCH_CHAIN_JOINTS = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


@dataclass(frozen=True)
class JointActuatorParams:
    """Parameters for one delayed / lagged / velocity-limited joint target."""

    delay_ticks: int = 0
    tau_s: float = 0.0
    velocity_limit_rad_s: float = math.inf

    def normalized(self) -> "JointActuatorParams":
        return JointActuatorParams(
            delay_ticks=max(0, int(self.delay_ticks)),
            tau_s=max(0.0, float(self.tau_s)),
            velocity_limit_rad_s=max(0.0, float(self.velocity_limit_rad_s)),
        )


class ActuatorBridgeModel:
    """Apply delay, first-order lag, and velocity limits to joint targets."""

    def __init__(
        self,
        params: Sequence[JointActuatorParams],
        initial_target: Sequence[float] | None = None,
    ) -> None:
        self.params = [param.normalized() for param in params]
        if not self.params:
            raise ValueError("ActuatorBridgeModel requires at least one joint")
        self.size = len(self.params)
        initial = (
            np.zeros(self.size, dtype=float)
            if initial_target is None
            else np.asarray(initial_target, dtype=float)
        )
        if initial.shape != (self.size,):
            raise ValueError(
                f"initial_target shape {initial.shape} does not match model size {self.size}"
            )
        self._value = initial.copy()
        self._queues: list[list[float]] = []
        for index, param in enumerate(self.params):
            self._queues.append([float(initial[index])] * (param.delay_ticks + 1))

    @property
    def value(self) -> np.ndarray:
        return self._value.copy()

    def reset(self, initial_target: Sequence[float] | None = None) -> None:
        initial = (
            np.zeros(self.size, dtype=float)
            if initial_target is None
            else np.asarray(initial_target, dtype=float)
        )
        if initial.shape != (self.size,):
            raise ValueError(
                f"initial_target shape {initial.shape} does not match model size {self.size}"
            )
        self._value = initial.copy()
        self._queues = [
            [float(initial[index])] * (param.delay_ticks + 1)
            for index, param in enumerate(self.params)
        ]

    def step(self, sent_target: Sequence[float], dt_s: float) -> np.ndarray:
        target = np.asarray(sent_target, dtype=float)
        if target.shape != (self.size,):
            raise ValueError(f"target shape {target.shape} does not match model size {self.size}")
        dt = float(dt_s) if dt_s and dt_s > 0 else 0.02
        next_value = self._value.copy()
        for index, param in enumerate(self.params):
            queue = self._queues[index]
            queue.append(float(target[index]))
            while len(queue) > param.delay_ticks + 1:
                queue.pop(0)
            delayed_target = queue[0]

            if param.tau_s > 0.0:
                alpha = 1.0 - math.exp(-dt / param.tau_s)
                desired = self._value[index] + alpha * (delayed_target - self._value[index])
            else:
                desired = delayed_target

            desired_step = desired - self._value[index]
            max_step = param.velocity_limit_rad_s * dt
            if math.isfinite(max_step):
                desired_step = max(-max_step, min(max_step, desired_step))
            next_value[index] = self._value[index] + desired_step
        self._value = next_value
        return self.value


def passthrough_params(size: int) -> list[JointActuatorParams]:
    return [JointActuatorParams() for _ in range(size)]


def load_fit_json(path: str | Path) -> dict:
    with open(path) as f:
        return json.load(f)


def params_from_fit(
    fit: Mapping,
    joint_names: Sequence[str] = JOINT_NAMES,
    source: str = "primary",
    include_unfitted_passthrough: bool = True,
) -> list[JointActuatorParams]:
    """Build per-joint bridge params from `actuator_response_fit.json`.

    The fit currently prioritizes pitch-chain joints. Non-fitted joints default
    to pass-through unless `include_unfitted_passthrough` is false.
    """

    root = fit.get(source, fit)
    joints = root.get("joints", {})
    params = []
    for joint in joint_names:
        item = joints.get(joint, {})
        combined = item.get("combined")
        if combined:
            params.append(
                JointActuatorParams(
                    delay_ticks=int(combined.get("delay_ticks", 0)),
                    tau_s=float(combined.get("tau_s", 0.0)),
                    velocity_limit_rad_s=float(
                        combined.get("velocity_limit_rad_s", math.inf)
                    ),
                ).normalized()
            )
        elif include_unfitted_passthrough:
            params.append(JointActuatorParams())
        else:
            raise KeyError(f"No fitted actuator params for joint {joint}")
    return params


def stress_params(
    joint_names: Sequence[str] = JOINT_NAMES,
    delay_ticks: int = 6,
    tau_s: float = 0.10,
    default_velocity_limit_rad_s: float = 3.2,
) -> list[JointActuatorParams]:
    """Conservative deterministic stress params from the bridge spec ranges."""

    output = []
    for joint in joint_names:
        velocity = default_velocity_limit_rad_s
        delay = delay_ticks
        if "ankle" in joint:
            velocity = min(velocity, 2.5)
            delay += 1
        elif "knee" in joint:
            velocity = min(velocity, 3.0)
        elif "hip_pitch" in joint:
            velocity = min(velocity + 0.3, 3.8)
        elif joint in {"neck_pitch", "head_pitch", "head_yaw", "head_roll"}:
            velocity = math.inf
            delay = 0
        else:
            velocity = math.inf
            delay = 0
        output.append(
            JointActuatorParams(
                delay_ticks=delay,
                tau_s=0.0 if not math.isfinite(velocity) else tau_s,
                velocity_limit_rad_s=velocity,
            ).normalized()
        )
    return output


def bridge_targets(
    sent_targets: Iterable[Sequence[float]],
    dt_s: Iterable[float],
    params: Sequence[JointActuatorParams],
) -> np.ndarray:
    targets = [np.asarray(target, dtype=float) for target in sent_targets]
    dts = list(dt_s)
    if not targets:
        return np.zeros((0, len(params)))
    model = ActuatorBridgeModel(params, initial_target=targets[0])
    output = []
    for index, target in enumerate(targets):
        dt = dts[index] if index < len(dts) else 0.02
        output.append(model.step(target, dt))
    return np.vstack(output)
