#!/usr/bin/env python3
"""Run the frozen Winner-v87 linear pitch-head feasibility audit on CPU."""

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

import build_winner_v87_pitch_head_linear_feasibility_preregistration as builder  # noqa: E402
import run_winner_v81_pitch_action_head_continuation as v81  # noqa: E402
import run_winner_v86_residual_pitch_causal as v86  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v87_pitch_head_linear_feasibility_preregistration.json"
V84_RESULT = ANALYSIS / "winner_v84_negative_gradient_pitch_head_continuation_result.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
PITCH_INDICES = builder.PITCH_INDICES


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    frozen = value.get("frozen_source", {})
    fit = value.get("fit", {})
    if (
        value.get("schema_version")
        != "winner_v87.pitch_head_linear_feasibility_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V87_PITCH_HEAD_LINEAR_FEASIBILITY"
        or value.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_TWO_ENDPOINT_LINEAR_FEASIBILITY_AUDIT_ONLY"
        or frozen.get("checkpoint_labels_updates") != {"half": 705, "final": 755}
        or frozen.get("pitch_indices") != list(PITCH_INDICES)
        or frozen.get("teacher_configuration_count") != 16
        or frozen.get("teacher_episodes_per_checkpoint") != 32
        or fit.get("solver") != "numpy.linalg.lstsq"
        or fit.get("rcond") is not None
        or fit.get("cross_validation_fits_per_checkpoint") != 16
        or fit.get("hyperparameter_search") is not False
        or value.get("execution_now")
        != {
            "stage2_rollout_episodes": 0,
            "least_squares_fits": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v87 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v87 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v87 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v87 source manifest changed")


def fit_float32_head(design: np.ndarray, targets: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    coefficients, residuals, rank, singular = np.linalg.lstsq(
        np.asarray(design, dtype=np.float64),
        np.asarray(targets, dtype=np.float64),
        rcond=None,
    )
    repeated = np.linalg.lstsq(
        np.asarray(design, dtype=np.float64),
        np.asarray(targets, dtype=np.float64),
        rcond=None,
    )[0]
    if not np.array_equal(coefficients, repeated):
        raise ValueError("Winner-v87 repeated least-squares solve changed")
    deployed = np.asarray(coefficients, dtype=np.float32)
    metrics = {
        "rows": int(design.shape[0]),
        "columns": int(design.shape[1]),
        "rank": int(rank),
        "residual_sum_squares": [float(value) for value in residuals],
        "singular_value_max": float(np.max(singular)),
        "singular_value_min": float(np.min(singular)),
        "condition_number": (
            float(np.max(singular) / np.min(singular))
            if float(np.min(singular)) > 0.0
            else None
        ),
        "coefficient_max_abs_float32": float(np.max(np.abs(deployed))),
        "repeat_solve_bit_exact": True,
    }
    return deployed, metrics


def error_metrics(
    predicted: np.ndarray, target: np.ndarray, selector: np.ndarray
) -> dict[str, float | int]:
    error = np.asarray(predicted, dtype=np.float64) - np.asarray(target, dtype=np.float64)
    chosen = error[np.asarray(selector, dtype=bool)]
    if chosen.ndim != 2 or chosen.shape[1] != len(PITCH_INDICES) or chosen.size == 0:
        raise ValueError("Winner-v87 metric selection changed")
    square = np.square(chosen)
    return {
        "elements": int(chosen.size),
        "mse": float(np.mean(square)),
        "rms": float(np.sqrt(np.mean(square))),
        "mean_abs": float(np.mean(np.abs(chosen))),
        "maximum_abs": float(np.max(np.abs(chosen))),
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
    v29: Any,
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
    if int(np.asarray(snapshot["optimizer"]["count"])) != update:
        raise ValueError(f"Winner-v87 {label} optimizer count changed")
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
    episode_receipt_sha256 = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=update
    )
    identifiers = [str(row["id"]) for row in population]
    selected_ids = set(teacher_ids)
    selected_environment = np.asarray(
        [name in selected_ids for name in identifiers], dtype=bool
    )
    if (
        len(population) != 80
        or int(np.count_nonzero(selected_environment)) != 32
        or any(identifiers.count(name) != 2 for name in teacher_ids)
    ):
        raise ValueError("Winner-v87 teacher population changed")

    observations = np.asarray(batch_np["observations"], dtype=np.float32)
    previous_actions = np.asarray(batch_np["previous_actions"], dtype=np.float32)
    valid_mask = np.asarray(batch_np["valid_mask"], dtype=np.float32)
    hidden_jax, source_bounded_jax = v29.deterministic_bounded_actions(
        snapshot["parameters"], observations, previous_actions
    )
    hidden = np.asarray(hidden_jax, dtype=np.float32)
    source_bounded = np.asarray(source_bounded_jax, dtype=np.float32)
    raw_teacher = np.zeros_like(previous_actions)
    for environment, name in enumerate(identifiers):
        if name in selected_ids:
            raw_teacher[environment, :, :] = np.asarray(
                teacher_table[name], dtype=np.float32
            )
    maximum_teacher_abs = float(
        np.max(np.abs(raw_teacher[selected_environment][:, :, list(PITCH_INDICES)]))
    )
    if not maximum_teacher_abs < 1.0:
        raise ValueError("Winner-v87 teacher target leaves tanh domain")
    bounded_teacher = np.asarray(
        training.bounded_action(raw_teacher, previous_actions), dtype=np.float32
    )
    selector = selected_environment[:, None] & (valid_mask > 0.0)
    pitch = list(PITCH_INDICES)
    design_all = np.concatenate(
        [hidden.astype(np.float64), np.ones((*hidden.shape[:2], 1), dtype=np.float64)],
        axis=-1,
    )
    target_logits = np.arctanh(raw_teacher[..., pitch].astype(np.float64))
    full_coefficients, full_fit = fit_float32_head(
        design_all[selector], target_logits[selector]
    )
    raw_source = np.tanh(
        hidden @ np.asarray(snapshot["parameters"]["action_weight"], dtype=np.float32)
        + np.asarray(snapshot["parameters"]["action_bias"], dtype=np.float32)
    ).astype(np.float32)
    raw_full = raw_source.copy()
    raw_full[..., pitch] = np.tanh(
        hidden @ full_coefficients[:-1, :] + full_coefficients[-1, :]
    ).astype(np.float32)
    bounded_full = np.asarray(
        training.bounded_action(raw_full, previous_actions), dtype=np.float32
    )

    source_metrics = error_metrics(
        source_bounded[..., pitch], bounded_teacher[..., pitch], selector
    )
    full_metrics = error_metrics(
        bounded_full[..., pitch], bounded_teacher[..., pitch], selector
    )
    fold_rows: list[dict[str, Any]] = []
    fold_square_sum = 0.0
    fold_elements = 0
    fold_maximum = 0.0
    all_repeat_exact = bool(full_fit["repeat_solve_bit_exact"])
    for heldout in teacher_ids:
        train_environment = selected_environment & np.asarray(
            [name != heldout for name in identifiers], dtype=bool
        )
        heldout_environment = np.asarray(
            [name == heldout for name in identifiers], dtype=bool
        )
        train_selector = train_environment[:, None] & (valid_mask > 0.0)
        heldout_selector = heldout_environment[:, None] & (valid_mask > 0.0)
        coefficients, fit = fit_float32_head(
            design_all[train_selector], target_logits[train_selector]
        )
        raw_fold = raw_source.copy()
        raw_fold[..., pitch] = np.tanh(
            hidden @ coefficients[:-1, :] + coefficients[-1, :]
        ).astype(np.float32)
        bounded_fold = np.asarray(
            training.bounded_action(raw_fold, previous_actions), dtype=np.float32
        )
        metrics = error_metrics(
            bounded_fold[..., pitch], bounded_teacher[..., pitch], heldout_selector
        )
        fold_square_sum += float(metrics["mse"]) * int(metrics["elements"])
        fold_elements += int(metrics["elements"])
        fold_maximum = max(fold_maximum, float(metrics["maximum_abs"]))
        all_repeat_exact = all_repeat_exact and bool(fit["repeat_solve_bit_exact"])
        fold_rows.append(
            {
                "heldout_configuration_id": heldout,
                "fit": fit,
                "bounded_pitch_error": metrics,
            }
        )
    cross_mse = fold_square_sum / fold_elements
    cross_metrics = {
        "elements": fold_elements,
        "mse": cross_mse,
        "rms": math.sqrt(cross_mse),
        "maximum_abs": fold_maximum,
    }
    feasible = (
        float(full_metrics["mse"]) < float(source_metrics["mse"])
        and float(cross_metrics["mse"]) < float(source_metrics["mse"])
    )
    all_values = [
        maximum_teacher_abs,
        *[float(value) for value in source_metrics.values()],
        *[float(value) for value in full_metrics.values()],
        *[float(value) for value in cross_metrics.values()],
    ]
    return {
        "label": label,
        "update": update,
        "snapshot_sha256": sha256(checkpoint_path),
        "episode_receipt_sha256": episode_receipt_sha256,
        "rollout_episodes": len(episodes),
        "teacher_episodes": int(np.count_nonzero(selected_environment)),
        "teacher_configuration_ids": list(teacher_ids),
        "maximum_abs_raw_teacher_pitch": maximum_teacher_abs,
        "source_bounded_pitch_error": source_metrics,
        "full_fit": full_fit,
        "full_fit_bounded_pitch_error": full_metrics,
        "leave_one_configuration_out": {
            "folds": fold_rows,
            "aggregate_bounded_pitch_error": cross_metrics,
        },
        "repeat_solves_bit_exact": all_repeat_exact,
        "all_values_finite": all(math.isfinite(value) for value in all_values),
        "endpoint_feasible": feasible,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--linear-feasibility-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.linear_feasibility_authorized:
        raise PermissionError(
            "Winner-v87 requires --offline-cpu-only --linear-feasibility-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v87 evidence")

    import jax
    import mujoco
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v20_joint_recurrent_support as v20
    import winner_v29_prefix_right_pitch_anchor as v29

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v87 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v84_result = json.loads(V84_RESULT.read_text(encoding="utf-8"))
    if (
        v84_result.get("status")
        != "PASS_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION"
    ):
        raise ValueError("Winner-v87 source continuation changed")
    smoke, gate, v85 = v86.configured_v85()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v87 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v87 canonical P30 fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = full.training_population(full_design, domain)
    v80 = v81.v80_module()
    teacher_ids = tuple(v80.TRAINING_TEACHER_IDS)
    teacher_table = v80.complete_teacher_table()
    if len(teacher_ids) != 16 or any(name not in teacher_table for name in teacher_ids):
        raise ValueError("Winner-v87 teacher table changed")

    endpoint_rows = [
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
            v29=v29,
            mujoco=mujoco,
            population=population,
            calibrator_design=calibrator_design,
            observer_type=observer_type,
            teacher_ids=teacher_ids,
            teacher_table=teacher_table,
        )
        for label, update in (("half", 705), ("final", 755))
    ]
    feasible = {row["label"]: bool(row["endpoint_feasible"]) for row in endpoint_rows}
    next_source = "half" if feasible["half"] else ("final" if feasible["final"] else None)
    classification = (
        "LINEAR_PITCH_HEAD_FEASIBLE"
        if next_source is not None
        else "FROZEN_HIDDEN_LINEAR_PITCH_HEAD_INSUFFICIENT"
    )
    checks = {
        "two_exact_source_checkpoints": [row["update"] for row in endpoint_rows]
        == [705, 755],
        "two_exact_80_episode_rollouts": all(
            row["rollout_episodes"] == 80 for row in endpoint_rows
        ),
        "exact_teacher_population_per_checkpoint": all(
            row["teacher_episodes"] == 32
            and len(row["teacher_configuration_ids"]) == 16
            for row in endpoint_rows
        ),
        "all_targets_strictly_inside_tanh_domain": all(
            row["maximum_abs_raw_teacher_pitch"] < 1.0 for row in endpoint_rows
        ),
        "full_design_matrix_rank_and_singular_values_recorded": all(
            row["full_fit"]["rank"] > 0
            and row["full_fit"]["singular_value_max"] > 0.0
            and row["full_fit"]["singular_value_min"] >= 0.0
            for row in endpoint_rows
        ),
        "repeat_solves_bit_exact": all(
            row["repeat_solves_bit_exact"] for row in endpoint_rows
        ),
        "all_values_finite": all(row["all_values_finite"] for row in endpoint_rows),
        "no_snapshot_or_onnx_written": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v87 diagnostic invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v87.pitch_head_linear_feasibility_result.v1",
        "status": "PASS_WINNER_V87_PITCH_HEAD_LINEAR_FEASIBILITY_AUDIT",
        "decision": (
            "PREREGISTER_EXACT_FITTED_PITCH_HEAD_PROOF"
            if next_source is not None
            else "PREREGISTER_RECURRENT_REPRESENTATION_DIAGNOSTIC"
        ),
        "classification": classification,
        "next_source_checkpoint_for_mechanism_proof": next_source,
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": [],
        "endpoints": endpoint_rows,
        "execution": {
            "stage2_rollout_episodes": sum(row["rollout_episodes"] for row in endpoint_rows),
            "least_squares_fits": 34,
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
    print(f"next_source={next_source}")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
