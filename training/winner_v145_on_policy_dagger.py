"""One-step on-policy DAgger from the V140 shadow-oracle trajectory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

import winner_v134_full_actor_teacher_distillation as v134


ACTION_SIZE = v134.ACTION_SIZE
HIDDEN_SIZE = v134.HIDDEN_SIZE
OBS_SIZE = v134.OBS_SIZE
STD_BACKTRACK_LIMIT = v134.STD_BACKTRACK_LIMIT
ARMIJO_FRACTION = v134.ARMIJO_FRACTION

loss_components = v134.loss_components
freeze_scale_gradients = v134.freeze_scale_gradients
gradient_norm = v134.gradient_norm
apply_gradient = v134.apply_gradient
deployed_actions = v134.deployed_actions


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _oracle_joint_masks(run_root: Path, keys: list[str]) -> np.ndarray:
    by_key = {}
    for trace_path in sorted(run_root.resolve().glob("traces/*_final_*.jsonl")):
        records = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        for record in records:
            mask = np.zeros(ACTION_SIZE, dtype=np.bool_)
            mask[
                np.asarray(
                    record["exact_torque_oracle"][
                        "projected_joint_indices"
                    ],
                    dtype=np.int64,
                )
            ] = True
            by_key[f"{trace_path.name}:{int(record['tick']):03d}"] = mask
    if set(by_key) != set(keys):
        raise ValueError("V145 teacher mask keys do not match V134 rows")
    return np.stack([by_key[key] for key in keys])


def load_shadow_dataset(trace_path: Path) -> dict[str, Any]:
    records = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    if len(records) != 600:
        raise ValueError("V145 shadow trace must contain 600 rows")
    mask = np.zeros((len(records), ACTION_SIZE), dtype=np.bool_)
    oracle_action = []
    for index, record in enumerate(records):
        oracle = record["exact_torque_oracle"]
        mask[
            index,
            np.asarray(
                oracle["projected_joint_indices"], dtype=np.int64
            ),
        ] = True
        oracle_action.append(
            np.asarray(oracle["final_action"], dtype=np.float32)
        )
    return {
        "obs": np.asarray(
            [record["obs_state"] for record in records], dtype=np.float32
        ),
        "previous_action": np.asarray(
            [
                record["policy_state_input"]["previous_action"][0]
                for record in records
            ],
            dtype=np.float32,
        ),
        "h_in": np.asarray(
            [
                record["policy_state_input"]["h_in"][0]
                for record in records
            ],
            dtype=np.float32,
        ),
        "recorded_base_action": np.asarray(
            [record["policy_base_action"] for record in records],
            dtype=np.float32,
        ),
        "recorded_h_out": np.asarray(
            [
                record["policy_state_output"]["h_out"][0]
                for record in records
            ],
            dtype=np.float32,
        ),
        "oracle_action": np.stack(oracle_action),
        "joint_mask": mask,
        "manifest": {
            "path": str(trace_path.resolve()),
            "rows": len(records),
            "sha256": _sha256(trace_path),
        },
    }


def build_aggregated_dataset(
    *,
    teacher_root: Path,
    shadow_trace: Path,
    teacher_baseline_action: np.ndarray,
    teacher_baseline_hidden: np.ndarray,
    shadow_baseline_action: np.ndarray,
    shadow_baseline_hidden: np.ndarray,
) -> dict[str, Any]:
    teacher = v134.load_teacher_dataset(teacher_root)
    teacher_mask = _oracle_joint_masks(teacher_root, teacher["keys"])
    shadow = load_shadow_dataset(shadow_trace)
    if teacher_baseline_action.shape != (4_800, ACTION_SIZE):
        raise ValueError("V145 teacher baseline action shape changed")
    if teacher_baseline_hidden.shape != (4_800, HIDDEN_SIZE):
        raise ValueError("V145 teacher baseline hidden shape changed")
    if shadow_baseline_action.shape != (600, ACTION_SIZE):
        raise ValueError("V145 shadow baseline action shape changed")
    if shadow_baseline_hidden.shape != (600, HIDDEN_SIZE):
        raise ValueError("V145 shadow baseline hidden shape changed")
    teacher_target = np.where(
        teacher_mask,
        teacher["target_action"],
        teacher_baseline_action,
    ).astype(np.float32)
    shadow_target = np.where(
        shadow["joint_mask"],
        shadow["oracle_action"],
        shadow_baseline_action,
    ).astype(np.float32)
    joint_mask = np.concatenate(
        [teacher_mask, shadow["joint_mask"]], axis=0
    )
    corrected = np.any(joint_mask, axis=1)
    correction_weight = float(np.sum(~corrected) / np.sum(corrected))
    weights = np.where(corrected, correction_weight, 1.0).astype(np.float32)
    return {
        "obs": np.concatenate([teacher["obs"], shadow["obs"]], axis=0),
        "previous_action": np.concatenate(
            [teacher["previous_action"], shadow["previous_action"]], axis=0
        ),
        "h_in": np.concatenate(
            [teacher["h_in"], shadow["h_in"]], axis=0
        ),
        "base_action": np.concatenate(
            [teacher_baseline_action, shadow_baseline_action], axis=0
        ),
        "target_action": np.concatenate(
            [teacher_target, shadow_target], axis=0
        ),
        "target_h_out": np.concatenate(
            [teacher_baseline_hidden, shadow_baseline_hidden], axis=0
        ),
        "weights": weights,
        "corrected": corrected,
        "joint_mask": joint_mask,
        "source": np.asarray(
            ["teacher"] * 4_800 + ["shadow"] * 600, dtype=object
        ),
        "correction_weight": correction_weight,
        "teacher_manifest": teacher["manifest"],
        "shadow_manifest": shadow["manifest"],
        "shadow_recorded_base_action": shadow["recorded_base_action"],
        "shadow_recorded_h_out": shadow["recorded_h_out"],
    }


def interpolate_policy(
    source: Any,
    candidate: Any,
    alpha: float,
) -> Any:
    def interpolate(left, right):
        left_np = np.asarray(left)
        right_np = np.asarray(right)
        value = (
            left_np.astype(np.float64)
            + float(alpha)
            * (
                right_np.astype(np.float64)
                - left_np.astype(np.float64)
            )
        ).astype(left_np.dtype)
        return jnp.asarray(value)

    return jax.tree_util.tree_map(interpolate, source, candidate)
