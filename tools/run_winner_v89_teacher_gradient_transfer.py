#!/usr/bin/env python3
"""Run the frozen Winner-v89 teacher-gradient transfer diagnostic on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import build_winner_v89_teacher_gradient_transfer_preregistration as builder  # noqa: E402
import run_winner_v81_pitch_action_head_continuation as v81  # noqa: E402
import run_winner_v86_residual_pitch_causal as v86  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v89_teacher_gradient_transfer_preregistration.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
PITCH_INDICES = (2, 3, 4, 11, 12, 13)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    frozen = value.get("frozen_source", {})
    diagnostic = value.get("diagnostic", {})
    if (
        value.get("schema_version")
        != "winner_v89.teacher_gradient_transfer_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V89_TEACHER_GRADIENT_TRANSFER_DIAGNOSTIC"
        or frozen.get("checkpoint_labels_updates") != {"half": 705, "final": 755}
        or frozen.get("teacher_configurations") != 12
        or frozen.get("teacher_episodes_per_checkpoint") != 24
        or frozen.get("groups") != list(builder.GROUPS)
        or diagnostic.get("folds_per_checkpoint") != 12
        or diagnostic.get("teacher_gradient_evaluations") != 48
        or diagnostic.get("optimizer_step_or_parameter_commit") is not False
        or value.get("execution_now")
        != {
            "stage2_rollout_episodes": 0,
            "gradient_evaluations": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v89 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v89 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v89 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v89 source manifest changed")


def group_alignment(
    train_gradient: Mapping[str, Any],
    heldout_gradient: Mapping[str, Any],
    keys: Sequence[str],
) -> dict[str, float | bool | int]:
    train = np.concatenate(
        [np.asarray(train_gradient[key], dtype=np.float64).reshape(-1) for key in keys]
    )
    heldout = np.concatenate(
        [np.asarray(heldout_gradient[key], dtype=np.float64).reshape(-1) for key in keys]
    )
    dot = float(np.dot(train, heldout))
    train_norm = float(np.linalg.norm(train))
    heldout_norm = float(np.linalg.norm(heldout))
    cosine = dot / (train_norm * heldout_norm) if train_norm > 0 and heldout_norm > 0 else 0.0
    return {
        "elements": int(train.size),
        "train_norm": train_norm,
        "heldout_norm": heldout_norm,
        "dot": dot,
        "cosine": cosine,
        "strictly_positive_transfer": dot > 0.0,
    }


def evaluate_endpoint(
    *,
    label: str,
    update: int,
    training_work_root: Path,
    playground_root: Path,
    canonical_fit: Path,
    smoke: Any,
    gate: Any,
    v85: Any,
    full: Any,
    training: Any,
    v20: Any,
    v21: Any,
    v29: Any,
    jax: Any,
    jnp: Any,
    mujoco: Any,
    population: Sequence[Mapping[str, Any]],
    calibrator_design: Mapping[str, Any],
    observer_type: Any,
    teacher_ids: Sequence[str],
    teacher_table: Mapping[str, np.ndarray],
) -> dict[str, Any]:
    checkpoint_path, _ = v85.checkpoint_paths(training_work_root, label)
    snapshot = v85.load_snapshot_for_reviewed_gate(checkpoint_path)
    v85.validate_snapshot_for_reviewed_gate(snapshot)
    scene = playground_root / smoke.SCENE_RELATIVE
    batch_np, episodes, _ = v20.stage2_rollout(
        smoke=smoke,
        full=full,
        training=training,
        mujoco=mujoco,
        scene=scene,
        population=population,
        preregistration=calibrator_design,
        observer_type=observer_type,
        canonical_fit=canonical_fit,
        parameters=snapshot["parameters"],
        update_index=update,
    )
    full.validate_stage2_masks(batch_np, episodes)
    receipt = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=update
    )
    identifiers = [str(row["id"]) for row in population]
    selected = set(teacher_ids)
    selected_environment = np.asarray([name in selected for name in identifiers], dtype=bool)
    if len(teacher_ids) != 12 or int(np.count_nonzero(selected_environment)) != 24:
        raise ValueError("Winner-v89 teacher population changed")
    observations = jnp.asarray(batch_np["observations"], dtype=jnp.float32)
    previous_actions = jnp.asarray(batch_np["previous_actions"], dtype=jnp.float32)
    valid_mask = np.asarray(batch_np["valid_mask"], dtype=np.float32)
    raw_teacher = np.zeros_like(batch_np["previous_actions"], dtype=np.float32)
    for environment, name in enumerate(identifiers):
        if name in selected:
            raw_teacher[environment, :, :] = np.asarray(
                teacher_table[name], dtype=np.float32
            )
    bounded_teacher = jnp.asarray(
        training.bounded_action(jnp.asarray(raw_teacher), previous_actions),
        dtype=jnp.float32,
    )
    before = v21.joint_trainable_parameters(snapshot["parameters"])
    recurrent_keys = tuple(v20.RECURRENT_CORE_KEYS)
    action_keys = tuple(v21.POLICY_HEAD_KEYS)
    combined_keys = recurrent_keys + action_keys
    inactive_keys = tuple(
        key for key in v21.JOINT_TRAINABLE_KEYS if key not in set(combined_keys)
    )

    def masked_loss(values: Mapping[str, Any], mask: Any) -> Any:
        actions = v29.deterministic_bounded_actions(
            values, observations, previous_actions
        )[1]
        error = actions - bounded_teacher
        denominator = jnp.sum(mask)
        return jnp.sum(jnp.square(error) * mask) / denominator

    gradient_function = jax.jit(jax.value_and_grad(masked_loss))
    rows: list[dict[str, Any]] = []
    all_inactive_zero = True
    for heldout in teacher_ids:
        train_environment = selected_environment & np.asarray(
            [name != heldout for name in identifiers], dtype=bool
        )
        heldout_environment = np.asarray(
            [name == heldout for name in identifiers], dtype=bool
        )
        train_mask = np.zeros((*valid_mask.shape, 14), dtype=np.float32)
        heldout_mask = np.zeros_like(train_mask)
        train_mask[..., list(PITCH_INDICES)] = (
            train_environment[:, None] & (valid_mask > 0.0)
        )[..., None]
        heldout_mask[..., list(PITCH_INDICES)] = (
            heldout_environment[:, None] & (valid_mask > 0.0)
        )[..., None]
        train_loss, train_gradient = gradient_function(before, jnp.asarray(train_mask))
        heldout_loss, heldout_gradient = gradient_function(
            before, jnp.asarray(heldout_mask)
        )
        train_loss_value = float(train_loss.block_until_ready())
        heldout_loss_value = float(heldout_loss.block_until_ready())
        train_gradient_np = {
            key: np.asarray(value) for key, value in train_gradient.items()
        }
        heldout_gradient_np = {
            key: np.asarray(value) for key, value in heldout_gradient.items()
        }
        inactive_zero = all(
            np.count_nonzero(train_gradient_np[key]) == 0
            and np.count_nonzero(heldout_gradient_np[key]) == 0
            for key in inactive_keys
        )
        all_inactive_zero = all_inactive_zero and inactive_zero
        groups = {
            "recurrent_core": group_alignment(
                train_gradient_np, heldout_gradient_np, recurrent_keys
            ),
            "action_head": group_alignment(
                train_gradient_np, heldout_gradient_np, action_keys
            ),
            "combined_policy": group_alignment(
                train_gradient_np, heldout_gradient_np, combined_keys
            ),
        }
        rows.append(
            {
                "heldout_configuration_id": heldout,
                "train_selected_elements": int(np.sum(train_mask, dtype=np.float64)),
                "heldout_selected_elements": int(
                    np.sum(heldout_mask, dtype=np.float64)
                ),
                "train_loss": train_loss_value,
                "heldout_loss": heldout_loss_value,
                "inactive_gradients_exact_zero": inactive_zero,
                "groups": groups,
            }
        )
    summaries: dict[str, Any] = {}
    for group in builder.GROUPS:
        aligned = sum(
            row["groups"][group]["strictly_positive_transfer"] for row in rows
        )
        summaries[group] = {
            "strictly_positive_folds": int(aligned),
            "nonpositive_folds": int(len(rows) - aligned),
            "all_12_strictly_positive": aligned == 12,
            "dot_sum": float(sum(row["groups"][group]["dot"] for row in rows)),
            "cosine_mean": float(
                np.mean([row["groups"][group]["cosine"] for row in rows])
            ),
            "minimum_dot": float(min(row["groups"][group]["dot"] for row in rows)),
            "maximum_dot": float(max(row["groups"][group]["dot"] for row in rows)),
        }
    recurrent_coherent = summaries["recurrent_core"]["all_12_strictly_positive"]
    action_coherent = summaries["action_head"]["all_12_strictly_positive"]
    combined_coherent = summaries["combined_policy"]["all_12_strictly_positive"]
    if combined_coherent and recurrent_coherent and action_coherent:
        mechanism = "joint"
    elif recurrent_coherent and not action_coherent:
        mechanism = "recurrent_only"
    elif action_coherent and not recurrent_coherent:
        mechanism = "action_only"
    else:
        mechanism = None
    finite = all(
        math.isfinite(value)
        for row in rows
        for value in (
            row["train_loss"],
            row["heldout_loss"],
            *[
                metric
                for group in row["groups"].values()
                for metric in (
                    group["train_norm"],
                    group["heldout_norm"],
                    group["dot"],
                    group["cosine"],
                )
            ],
        )
    )
    return {
        "label": label,
        "update": update,
        "snapshot_sha256": sha256(checkpoint_path),
        "episode_receipt_sha256": receipt,
        "rollout_episodes": len(episodes),
        "teacher_episodes": int(np.count_nonzero(selected_environment)),
        "folds": rows,
        "group_summaries": summaries,
        "selected_endpoint_mechanism": mechanism,
        "all_inactive_gradients_exact_zero": all_inactive_zero,
        "all_values_finite": finite,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--gradient-transfer-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.gradient_transfer_authorized:
        raise PermissionError(
            "Winner-v89 requires --offline-cpu-only --gradient-transfer-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v89 evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v29_prefix_right_pitch_anchor as v29

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v89 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    smoke, gate, v85 = v86.configured_v85()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v89 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v89 canonical P30 fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = full.training_population(full_design, domain)
    v80 = v81.v80_module()
    teacher_ids = tuple(v80.TRAINING_TEACHER_IDS)
    teacher_table = v80.complete_teacher_table()
    endpoints = [
        evaluate_endpoint(
            label=label,
            update=update,
            training_work_root=args.training_work_root,
            playground_root=args.playground_root,
            canonical_fit=args.canonical_fit,
            smoke=smoke,
            gate=gate,
            v85=v85,
            full=full,
            training=training,
            v20=v20,
            v21=v21,
            v29=v29,
            jax=jax,
            jnp=jnp,
            mujoco=mujoco,
            population=population,
            calibrator_design=calibrator_design,
            observer_type=observer_type,
            teacher_ids=teacher_ids,
            teacher_table=teacher_table,
        )
        for label, update in (("half", 705), ("final", 755))
    ]
    selected_endpoint = next(
        (
            row
            for row in endpoints
            if row["selected_endpoint_mechanism"] in {"joint", "recurrent_only"}
        ),
        None,
    )
    selected_checkpoint = selected_endpoint["label"] if selected_endpoint else None
    selected_mechanism = (
        selected_endpoint["selected_endpoint_mechanism"] if selected_endpoint else None
    )
    if selected_mechanism is not None:
        classification = "TEACHER_GRADIENT_TRANSFER_COHERENT"
        decision = "PREREGISTER_SELECTED_TEACHER_GRADIENT_CPU_STEP_PROOF"
    else:
        classification = "STATIC_TEACHER_GRADIENT_NONTRANSFERABLE"
        decision = "PREREGISTER_OUTCOME_ALIGNED_MECHANISM_DIAGNOSTIC"
    checks = {
        "two_exact_80_episode_rollouts": all(
            row["rollout_episodes"] == 80 for row in endpoints
        ),
        "exact_24_teacher_episodes_both_endpoints": all(
            row["teacher_episodes"] == 24 for row in endpoints
        ),
        "exact_12_folds_both_endpoints": all(
            len(row["folds"]) == 12 for row in endpoints
        ),
        "all_inactive_gradients_exact_zero": all(
            row["all_inactive_gradients_exact_zero"] for row in endpoints
        ),
        "all_values_finite": all(row["all_values_finite"] for row in endpoints),
        "no_optimizer_step_or_parameter_commit": True,
        "no_snapshot_or_onnx_written": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v89 diagnostic invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v89.teacher_gradient_transfer_result.v1",
        "status": "PASS_WINNER_V89_TEACHER_GRADIENT_TRANSFER_DIAGNOSTIC",
        "classification": classification,
        "decision": decision,
        "selected_source_checkpoint_for_step_proof": selected_checkpoint,
        "selected_gradient_group_for_step_proof": selected_mechanism,
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": [],
        "endpoints": endpoints,
        "execution": {
            "stage2_rollout_episodes": 160,
            "gradient_evaluations": 48,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": preregistration["authority"],
        "sources": preregistration["sources"],
        "source_manifest_sha256": preregistration["source_manifest_sha256"],
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"classification={classification}")
    print(f"selected_checkpoint={selected_checkpoint}")
    print(f"selected_gradient_group={selected_mechanism}")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
