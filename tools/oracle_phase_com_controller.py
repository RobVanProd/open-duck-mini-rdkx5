#!/usr/bin/env python3
"""Small auditable oracle phase/contact COM residual used only in CPU simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


CONTACT_MODES = ("left_stance", "right_stance", "double_support", "transition")
FEATURE_NAMES = (
    "constant",
    "phase_sin",
    "phase_cos",
    "support_relative_com_x",
    "com_vx_error",
    "pitch",
    "pitch_rate",
    "support_relative_com_y",
    "com_vy",
    "roll",
    "roll_rate",
)
CORRECTED_JOINT_INDICES = (2, 3, 4, 11, 12, 13)


def contact_mode(contacts: Sequence[bool]) -> str:
    left, right = bool(contacts[0]), bool(contacts[1])
    if left and right:
        return "double_support"
    if left:
        return "left_stance"
    if right:
        return "right_stance"
    return "transition"


def support_centroid(
    contacts: Sequence[bool], foot_positions: np.ndarray
) -> np.ndarray:
    feet = np.asarray(foot_positions, dtype=np.float64)
    mask = np.asarray(contacts, dtype=bool)
    if feet.shape != (2, 3):
        raise ValueError(f"foot_positions shape {feet.shape} != (2, 3)")
    selected = feet[mask]
    if selected.size == 0:
        selected = feet
    return np.mean(selected, axis=0)


def feature_vector(
    *,
    phase_fraction: float,
    contacts: Sequence[bool],
    foot_positions: np.ndarray,
    whole_body_com: np.ndarray,
    whole_body_com_velocity: np.ndarray,
    command_x: float,
    pitch: float,
    pitch_rate: float,
    roll: float,
    roll_rate: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    centroid = support_centroid(contacts, foot_positions)
    com = np.asarray(whole_body_com, dtype=np.float64)
    velocity = np.asarray(whole_body_com_velocity, dtype=np.float64)
    relative = com - centroid
    angle = float(phase_fraction) * 2.0 * np.pi
    features = np.asarray(
        [
            1.0,
            np.sin(angle),
            np.cos(angle),
            relative[0],
            velocity[0] - float(command_x),
            float(pitch),
            float(pitch_rate),
            relative[1],
            velocity[1],
            float(roll),
            float(roll_rate),
        ],
        dtype=np.float64,
    )
    return features, {
        "contact_mode": contact_mode(contacts),
        "support_centroid_m": centroid.tolist(),
        "support_relative_com_m": relative.tolist(),
    }


def load_controller(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if payload.get("schema_version") != "oracle_phase_com_controller.v1":
        raise ValueError("unexpected oracle controller schema")
    if payload.get("feature_names") != list(FEATURE_NAMES):
        raise ValueError("oracle controller feature order mismatch")
    if payload.get("corrected_joint_indices") != list(CORRECTED_JOINT_INDICES):
        raise ValueError("oracle controller joint order mismatch")
    for sign in ("negative", "positive"):
        banks = payload.get("coefficient_banks", {}).get(sign, {})
        if set(banks) != set(CONTACT_MODES):
            raise ValueError(f"oracle controller contact banks mismatch: {sign}")
        for mode in CONTACT_MODES:
            values = np.asarray(banks[mode], dtype=np.float64)
            if values.shape != (len(CORRECTED_JOINT_INDICES), len(FEATURE_NAMES)):
                raise ValueError(f"oracle coefficient shape mismatch: {sign}/{mode}")
    return payload


def evaluate_controller(
    payload: Mapping[str, Any],
    *,
    endpoint_offset_m: float,
    mode: str,
    features: np.ndarray,
    action_dim: int = 14,
) -> tuple[np.ndarray, dict[str, Any]]:
    residual = np.zeros(action_dim, dtype=np.float32)
    if abs(float(endpoint_offset_m)) < 1e-12:
        return residual, {"endpoint_bank": "nominal_zero", "unclipped_corrected": [0.0] * 6}
    sign = "negative" if float(endpoint_offset_m) < 0.0 else "positive"
    mean = np.asarray(payload["feature_normalization"][sign][mode]["mean"], dtype=np.float64)
    scale = np.asarray(payload["feature_normalization"][sign][mode]["scale"], dtype=np.float64)
    normalized = np.asarray(features, dtype=np.float64).copy()
    normalized[1:] = (normalized[1:] - mean[1:]) / scale[1:]
    normalized[0] = 1.0
    coefficients = np.asarray(payload["coefficient_banks"][sign][mode], dtype=np.float64)
    unscaled = coefficients @ normalized
    scaled = unscaled * float(payload["selected_global_scale"])
    limit = float(payload["residual_normalized_limit"])
    clipped = np.clip(scaled, -limit, limit).astype(np.float32)
    residual[np.asarray(CORRECTED_JOINT_INDICES, dtype=int)] = clipped
    return residual, {
        "endpoint_bank": sign,
        "normalized_features": normalized.tolist(),
        "unclipped_corrected": scaled.tolist(),
    }


def project_combined_action(
    *,
    base_action: np.ndarray,
    residual_action: np.ndarray,
    previous_final_action: np.ndarray,
    actual_position_rad: np.ndarray,
    default_position_rad: np.ndarray,
    action_scale_rad: float,
    max_action_delta: np.ndarray,
    actual_centered_guard_rad: float,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    raw = np.clip(
        np.asarray(base_action, dtype=np.float64)
        + np.asarray(residual_action, dtype=np.float64),
        -1.0,
        1.0,
    )
    rate_bounded = np.clip(
        raw,
        np.asarray(previous_final_action, dtype=np.float64) - max_action_delta,
        np.asarray(previous_final_action, dtype=np.float64) + max_action_delta,
    )
    guard_low = (
        np.asarray(actual_position_rad, dtype=np.float64)
        - float(actual_centered_guard_rad)
        - np.asarray(default_position_rad, dtype=np.float64)
    ) / float(action_scale_rad)
    guard_high = (
        np.asarray(actual_position_rad, dtype=np.float64)
        + float(actual_centered_guard_rad)
        - np.asarray(default_position_rad, dtype=np.float64)
    ) / float(action_scale_rad)
    final = np.clip(rate_bounded, guard_low, guard_high).astype(np.float32)
    return final, {
        "raw_combined_action": raw.astype(np.float32),
        "rate_bounded_action": rate_bounded.astype(np.float32),
        "guard_low_action": guard_low.astype(np.float32),
        "guard_high_action": guard_high.astype(np.float32),
    }
