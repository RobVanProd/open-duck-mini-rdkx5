#!/usr/bin/env python3
"""Run the frozen Winner-v88 flat-transport representation diagnostic."""

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

import build_winner_v88_flat_transport_representation_preregistration as builder  # noqa: E402
import run_winner_v81_pitch_action_head_continuation as v81  # noqa: E402
import run_winner_v86_residual_pitch_causal as v86  # noqa: E402
import run_winner_v87_pitch_head_linear_feasibility as v87  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v88_flat_transport_representation_preregistration.json"
V87_RESULT = ANALYSIS / "winner_v87_pitch_head_linear_feasibility_result.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
PITCH_INDICES = (2, 3, 4, 11, 12, 13)
FAMILIES = builder.FAMILIES


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    frozen = value.get("frozen_source", {})
    equation = value.get("equation_boundary", {})
    fit = value.get("fit", {})
    if (
        value.get("schema_version")
        != "winner_v88.flat_transport_representation_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V88_FLAT_TRANSPORT_REPRESENTATION_DIAGNOSTIC"
        or frozen.get("checkpoint_labels_updates") != {"half": 705, "final": 755}
        or frozen.get("selected_teacher_configurations") != 12
        or frozen.get("selected_teacher_episodes_per_checkpoint") != 24
        or equation.get("rho_or_q_selected_or_searched") is not False
        or equation.get("policy_architecture_changed") is not False
        or fit.get("families") != list(FAMILIES)
        or fit.get("cross_validation")
        != "12 leave-one-configuration-out folds per family/endpoint"
        or fit.get("total_least_squares_fits") != 78
        or fit.get("hyperparameter_or_rho_q_search") is not False
        or value.get("execution_now")
        != {
            "stage2_rollout_episodes": 0,
            "least_squares_fits": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v88 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v88 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v88 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v88 source manifest changed")


def causal_prefix_mean(values: np.ndarray, valid_mask: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    valid = np.asarray(valid_mask, dtype=np.float32)
    weighted = values * valid[..., None]
    cumulative = np.cumsum(weighted.astype(np.float64), axis=1)
    counts = np.cumsum(valid.astype(np.float64), axis=1)[..., None]
    mean = np.divide(cumulative, np.maximum(counts, 1.0))
    mean[valid <= 0.0] = 0.0
    return np.asarray(mean, dtype=np.float32)


def standardized_design(
    features: np.ndarray, train_selector: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = np.asarray(features[train_selector], dtype=np.float64)
    mean = np.asarray(np.mean(rows, axis=0), dtype=np.float32)
    std = np.asarray(np.std(rows, axis=0), dtype=np.float32)
    std = np.where(std < np.float32(1.0e-6), np.float32(1.0), std).astype(
        np.float32
    )
    normalized = (
        (np.asarray(features, dtype=np.float32) - mean) / std
    ).astype(np.float32)
    design = np.concatenate(
        [normalized, np.ones((*normalized.shape[:2], 1), dtype=np.float32)], axis=-1
    )
    return design, mean, std


def score_family(
    *,
    features: np.ndarray,
    identifiers: Sequence[str],
    teacher_ids: Sequence[str],
    selected_environment: np.ndarray,
    valid_mask: np.ndarray,
    target_logits: np.ndarray,
    raw_source: np.ndarray,
    bounded_teacher: np.ndarray,
    previous_actions: np.ndarray,
    training: Any,
) -> dict[str, Any]:
    selector = selected_environment[:, None] & (valid_mask > 0.0)
    design, mean, std = standardized_design(features, selector)
    coefficients, full_fit = v87.fit_float32_head(
        design[selector], target_logits[selector]
    )
    raw_full = raw_source.copy()
    raw_full[..., list(PITCH_INDICES)] = np.tanh(
        design @ coefficients
    ).astype(np.float32)
    bounded_full = np.asarray(
        training.bounded_action(raw_full, previous_actions), dtype=np.float32
    )
    full_metrics = v87.error_metrics(
        bounded_full[..., list(PITCH_INDICES)],
        bounded_teacher[..., list(PITCH_INDICES)],
        selector,
    )
    folds: list[dict[str, Any]] = []
    square_sum = 0.0
    elements = 0
    maximum = 0.0
    repeats_exact = bool(full_fit["repeat_solve_bit_exact"])
    for heldout in teacher_ids:
        train_environment = selected_environment & np.asarray(
            [name != heldout for name in identifiers], dtype=bool
        )
        heldout_environment = np.asarray(
            [name == heldout for name in identifiers], dtype=bool
        )
        train_selector = train_environment[:, None] & (valid_mask > 0.0)
        heldout_selector = heldout_environment[:, None] & (valid_mask > 0.0)
        fold_design, fold_mean, fold_std = standardized_design(features, train_selector)
        fold_coefficients, fit = v87.fit_float32_head(
            fold_design[train_selector], target_logits[train_selector]
        )
        raw_fold = raw_source.copy()
        raw_fold[..., list(PITCH_INDICES)] = np.tanh(
            fold_design @ fold_coefficients
        ).astype(np.float32)
        bounded_fold = np.asarray(
            training.bounded_action(raw_fold, previous_actions), dtype=np.float32
        )
        metrics = v87.error_metrics(
            bounded_fold[..., list(PITCH_INDICES)],
            bounded_teacher[..., list(PITCH_INDICES)],
            heldout_selector,
        )
        square_sum += float(metrics["mse"]) * int(metrics["elements"])
        elements += int(metrics["elements"])
        maximum = max(maximum, float(metrics["maximum_abs"]))
        repeats_exact = repeats_exact and bool(fit["repeat_solve_bit_exact"])
        folds.append(
            {
                "heldout_configuration_id": heldout,
                "standardization_mean_sha256": hashlib.sha256(
                    fold_mean.tobytes(order="C")
                ).hexdigest(),
                "standardization_std_sha256": hashlib.sha256(
                    fold_std.tobytes(order="C")
                ).hexdigest(),
                "fit": fit,
                "bounded_pitch_error": metrics,
            }
        )
    aggregate_mse = square_sum / elements
    return {
        "feature_columns_without_intercept": int(features.shape[-1]),
        "standardization_mean_sha256": hashlib.sha256(mean.tobytes(order="C")).hexdigest(),
        "standardization_std_sha256": hashlib.sha256(std.tobytes(order="C")).hexdigest(),
        "full_fit": full_fit,
        "full_fit_bounded_pitch_error": full_metrics,
        "leave_one_configuration_out": {
            "folds": folds,
            "aggregate_bounded_pitch_error": {
                "elements": elements,
                "mse": aggregate_mse,
                "rms": math.sqrt(aggregate_mse),
                "maximum_abs": maximum,
            },
        },
        "repeat_solves_bit_exact": repeats_exact,
    }


def evaluate_endpoint(
    *,
    label: str,
    update: int,
    expected_source_mse: float,
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
        raise ValueError("Winner-v88 teacher population changed")
    observations = np.asarray(batch_np["observations"], dtype=np.float32)
    previous_actions = np.asarray(batch_np["previous_actions"], dtype=np.float32)
    valid_mask = np.asarray(batch_np["valid_mask"], dtype=np.float32)
    hidden_jax, source_bounded_jax = v29.deterministic_bounded_actions(
        snapshot["parameters"], observations, previous_actions
    )
    hidden = np.asarray(hidden_jax, dtype=np.float32)
    source_bounded = np.asarray(source_bounded_jax, dtype=np.float32)
    raw_source = np.tanh(
        hidden @ np.asarray(snapshot["parameters"]["action_weight"], dtype=np.float32)
        + np.asarray(snapshot["parameters"]["action_bias"], dtype=np.float32)
    ).astype(np.float32)
    raw_teacher = np.zeros_like(previous_actions)
    for environment, name in enumerate(identifiers):
        if name in selected:
            raw_teacher[environment, :, :] = np.asarray(
                teacher_table[name], dtype=np.float32
            )
    bounded_teacher = np.asarray(
        training.bounded_action(raw_teacher, previous_actions), dtype=np.float32
    )
    selector = selected_environment[:, None] & (valid_mask > 0.0)
    target_logits = np.arctanh(
        raw_teacher[..., list(PITCH_INDICES)].astype(np.float64)
    )
    source_metrics = v87.error_metrics(
        source_bounded[..., list(PITCH_INDICES)],
        bounded_teacher[..., list(PITCH_INDICES)],
        selector,
    )
    prefix_mean = causal_prefix_mean(observations, valid_mask)
    features = {
        "current_observation": observations,
        "flat_transport_basis": np.concatenate([observations, prefix_mean], axis=-1),
        "hidden_plus_flat_transport": np.concatenate(
            [hidden, observations, prefix_mean], axis=-1
        ),
    }
    family_rows = {
        family: score_family(
            features=features[family],
            identifiers=identifiers,
            teacher_ids=teacher_ids,
            selected_environment=selected_environment,
            valid_mask=valid_mask,
            target_logits=target_logits,
            raw_source=raw_source,
            bounded_teacher=bounded_teacher,
            previous_actions=previous_actions,
            training=training,
        )
        for family in FAMILIES
    }
    for row in family_rows.values():
        full_mse = row["full_fit_bounded_pitch_error"]["mse"]
        heldout_mse = row["leave_one_configuration_out"][
            "aggregate_bounded_pitch_error"
        ]["mse"]
        row["viable"] = bool(full_mse < source_metrics["mse"] and heldout_mse < source_metrics["mse"])
    current = family_rows["current_observation"]
    flat = family_rows["flat_transport_basis"]
    current_heldout = current["leave_one_configuration_out"][
        "aggregate_bounded_pitch_error"
    ]["mse"]
    flat_heldout = flat["leave_one_configuration_out"][
        "aggregate_bounded_pitch_error"
    ]["mse"]
    flat_selected = bool(flat["viable"] and flat_heldout < current_heldout)
    selected_family = (
        "flat_transport_basis"
        if flat_selected
        else (
            "current_observation"
            if current["viable"]
            else (
                "hidden_plus_flat_transport"
                if family_rows["hidden_plus_flat_transport"]["viable"]
                else None
            )
        )
    )
    finite_values = [float(source_metrics["mse"])]
    for row in family_rows.values():
        finite_values.extend(
            [
                float(row["full_fit_bounded_pitch_error"]["mse"]),
                float(
                    row["leave_one_configuration_out"][
                        "aggregate_bounded_pitch_error"
                    ]["mse"]
                ),
            ]
        )
    return {
        "label": label,
        "update": update,
        "snapshot_sha256": sha256(checkpoint_path),
        "episode_receipt_sha256": receipt,
        "rollout_episodes": len(episodes),
        "teacher_episodes": int(np.count_nonzero(selected_environment)),
        "teacher_configuration_ids": list(teacher_ids),
        "source_bounded_pitch_error": source_metrics,
        "v87_source_mse_reproduced_at_most_1e_12": abs(
            float(source_metrics["mse"]) - expected_source_mse
        )
        <= 1.0e-12,
        "families": family_rows,
        "flat_transport_incremental_over_current_observation": flat_heldout
        < current_heldout,
        "selected_family": selected_family,
        "all_values_finite": all(math.isfinite(value) for value in finite_values),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--representation-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.representation_diagnostic_authorized:
        raise PermissionError(
            "Winner-v88 requires --offline-cpu-only --representation-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v88 evidence")

    import jax
    import mujoco
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v20_joint_recurrent_support as v20
    import winner_v29_prefix_right_pitch_anchor as v29

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v88 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v87_result = json.loads(V87_RESULT.read_text(encoding="utf-8"))
    if sha256(V87_RESULT) != builder.V87_RESULT_SHA256:
        raise ValueError("Winner-v88 V87 source changed")
    smoke, gate, v85 = v86.configured_v85()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v88 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v88 canonical P30 fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = full.training_population(full_design, domain)
    v80 = v81.v80_module()
    teacher_ids = tuple(v80.TRAINING_TEACHER_IDS)
    teacher_table = v80.complete_teacher_table()
    expected_mse = {
        row["label"]: float(row["source_bounded_pitch_error"]["mse"])
        for row in v87_result["endpoints"]
    }
    endpoints = [
        evaluate_endpoint(
            label=label,
            update=update,
            expected_source_mse=expected_mse[label],
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
    selected_endpoint = next(
        (row for row in endpoints if row["selected_family"] is not None), None
    )
    selected_checkpoint = selected_endpoint["label"] if selected_endpoint else None
    selected_family = selected_endpoint["selected_family"] if selected_endpoint else None
    if selected_family in {"flat_transport_basis", "hidden_plus_flat_transport"}:
        classification = "FLAT_TRANSPORT_SIGNAL_SELECTED"
        decision = "PREREGISTER_FLAT_TRANSPORT_CPU_MECHANISM_PROOF"
    elif selected_family == "current_observation":
        classification = "CURRENT_OBSERVATION_SKIP_SIGNAL_SELECTED"
        decision = "PREREGISTER_CURRENT_OBSERVATION_SKIP_CPU_MECHANISM_PROOF"
    else:
        classification = "NO_LINEAR_OBSERVABLE_REPRESENTATION_SELECTED"
        decision = "REJECT_TESTED_LINEAR_REPRESENTATION_FAMILIES"
    checks = {
        "v87_source_mse_reproduced_both_endpoints": all(
            row["v87_source_mse_reproduced_at_most_1e_12"] for row in endpoints
        ),
        "two_exact_80_episode_rollouts": all(
            row["rollout_episodes"] == 80 for row in endpoints
        ),
        "exact_24_teacher_episodes_both_endpoints": all(
            row["teacher_episodes"] == 24 for row in endpoints
        ),
        "exact_three_feature_families_both_endpoints": all(
            set(row["families"]) == set(FAMILIES) for row in endpoints
        ),
        "exact_12_folds_per_family_endpoint": all(
            len(family["leave_one_configuration_out"]["folds"]) == 12
            for row in endpoints
            for family in row["families"].values()
        ),
        "all_repeat_solves_bit_exact": all(
            family["repeat_solves_bit_exact"]
            for row in endpoints
            for family in row["families"].values()
        ),
        "all_values_finite": all(row["all_values_finite"] for row in endpoints),
        "no_snapshot_or_onnx_written": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v88 diagnostic invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v88.flat_transport_representation_result.v1",
        "status": "PASS_WINNER_V88_FLAT_TRANSPORT_REPRESENTATION_DIAGNOSTIC",
        "classification": classification,
        "decision": decision,
        "selected_source_checkpoint_for_mechanism_proof": selected_checkpoint,
        "selected_feature_family_for_mechanism_proof": selected_family,
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": [],
        "endpoints": endpoints,
        "execution": {
            "stage2_rollout_episodes": 160,
            "least_squares_fits": 78,
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
    print(f"selected_family={selected_family}")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
