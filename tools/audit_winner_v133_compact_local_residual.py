#!/usr/bin/env python3
"""Falsify a compact local residual on the V131 robust teacher traces."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from audit_winner_v132_robust_teacher_dataset import (  # noqa: E402
    directory_sha256,
    load_rows,
    restore_like,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v133_compact_local_residual_preregistration_v3.json"
)
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V132_RESULT = ANALYSIS / "winner_v132_robust_teacher_dataset_audit.json"
OUTPUT = ANALYSIS / "winner_v133_compact_local_residual_audit_v3.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V133_COMPACT_LOCAL_RESIDUAL_AUDIT_V3_20260724.md"
)
STD_FLOOR = 1e-6
RADIUS_FRACTION = 0.5
NONZERO_FLOOR = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fold_key(plant: str, command: float) -> str:
    return f"{plant}_x{command:.3f}"


def metrics(target: np.ndarray, prediction: np.ndarray) -> dict:
    corrected = np.abs(target) > NONZERO_FLOOR
    preserved = ~corrected
    if np.any(corrected):
        corrected_baseline = float(np.mean(np.square(target[corrected])))
        corrected_mse = float(
            np.mean(np.square(prediction[corrected] - target[corrected]))
        )
    else:
        corrected_baseline = 0.0
        corrected_mse = 0.0
    preservation_mse = float(np.mean(np.square(prediction[preserved])))
    predicted = np.abs(prediction) > NONZERO_FLOOR
    true_positive = int(np.sum(predicted & corrected))
    false_positive = int(np.sum(predicted & preserved))
    return {
        "corrected_joint_events": int(np.sum(corrected)),
        "preservation_joint_events": int(np.sum(preserved)),
        "corrected_baseline_mse": corrected_baseline,
        "corrected_mse": corrected_mse,
        "corrected_ratio_to_zero_predictor": (
            corrected_mse / corrected_baseline
            if corrected_baseline > 0.0
            else 0.0
        ),
        "preservation_mse": preservation_mse,
        "preservation_ratio_to_corrected_baseline": (
            preservation_mse / corrected_baseline
            if corrected_baseline > 0.0
            else 0.0
        ),
        "event_recall": (
            true_positive / int(np.sum(corrected))
            if np.any(corrected)
            else 1.0
        ),
        "false_positive_joint_events": false_positive,
        "prediction_linf": float(np.max(np.abs(prediction))),
        "error_linf": float(np.max(np.abs(prediction - target))),
    }


def compact_predict(
    train_x: np.ndarray,
    train_y: np.ndarray,
    test_x: np.ndarray,
) -> tuple[np.ndarray, dict]:
    mean = np.mean(train_x, axis=0)
    std = np.std(train_x, axis=0)
    active = std >= STD_FLOOR
    if not np.any(active):
        raise ValueError("V133 representation has no active features")
    train = (train_x[:, active] - mean[active]) / std[active]
    test = (test_x[:, active] - mean[active]) / std[active]
    prediction = np.zeros_like(
        np.empty((test.shape[0], train_y.shape[1]), dtype=np.float64)
    )
    centers = 0
    unsupported_joints = []
    radii = []
    for joint in range(train_y.shape[1]):
        positive = np.abs(train_y[:, joint]) > NONZERO_FLOOR
        negative = ~positive
        if not np.any(positive):
            unsupported_joints.append(joint)
            continue
        center_x = train[positive]
        center_y = train_y[positive, joint]
        negative_x = train[negative]
        if negative_x.shape[0] == 0:
            raise ValueError("V133 requires preservation rows per joint")
        distance_to_negative = np.sqrt(
            np.min(
                np.sum(
                    np.square(center_x[:, None, :] - negative_x[None, :, :]),
                    axis=2,
                ),
                axis=1,
            )
        )
        radius = RADIUS_FRACTION * distance_to_negative
        distances = np.sqrt(
            np.sum(
                np.square(test[:, None, :] - center_x[None, :, :]),
                axis=2,
            )
        )
        nearest = np.argmin(distances, axis=1)
        nearest_distance = distances[np.arange(test.shape[0]), nearest]
        inside = nearest_distance <= radius[nearest]
        prediction[inside, joint] = center_y[nearest[inside]]
        centers += int(center_x.shape[0])
        radii.extend(radius.tolist())
    return prediction, {
        "active_features": int(np.sum(active)),
        "centers": centers,
        "unsupported_joints": unsupported_joints,
        "radius_min": float(min(radii)) if radii else 0.0,
        "radius_median": float(np.median(radii)) if radii else 0.0,
        "radius_max": float(max(radii)) if radii else 0.0,
    }


def audit_representation(
    features: np.ndarray,
    target: np.ndarray,
    plants: np.ndarray,
    commands: np.ndarray,
) -> dict:
    keys = np.asarray(
        [fold_key(str(p), float(c)) for p, c in zip(plants, commands)]
    )
    predictions = np.zeros_like(target)
    fold_results = {}
    for held_out in sorted(set(keys.tolist())):
        test = keys == held_out
        train = ~test
        prediction, geometry = compact_predict(
            features[train], target[train], features[test]
        )
        predictions[test] = prediction
        fold_results[held_out] = {
            **geometry,
            **metrics(target[test], prediction),
        }
    combined = metrics(target, predictions)
    corrected_folds = [
        value
        for value in fold_results.values()
        if value["corrected_joint_events"] > 0
    ]
    qualifies = (
        combined["corrected_ratio_to_zero_predictor"] <= 0.25
        and combined["preservation_ratio_to_corrected_baseline"] <= 0.01
        and combined["event_recall"] >= 0.90
        and all(
            value["corrected_ratio_to_zero_predictor"] < 1.0
            and value["preservation_ratio_to_corrected_baseline"] <= 0.01
            for value in corrected_folds
        )
        and all(
            value["false_positive_joint_events"] == 0
            for name, value in fold_results.items()
            if name.endswith("_x0.000")
        )
    )
    return {
        "combined": combined,
        "folds": fold_results,
        "qualifies": qualifies,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V133: {path}")
    run_root = args.run_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v132 = json.loads(V132_RESULT.read_text(encoding="utf-8"))
    observed_hashes = {
        "v131_behavior_result": sha256(V131_RESULT),
        "v132_dataset_audit": sha256(V132_RESULT),
        "audit_runner": sha256(Path(__file__).resolve()),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V133_COMPACT_LOCAL_RESIDUAL_AUDIT_V3"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or v132.get("decision")
        != "NO_STATIC_LINEAR_ROBUST_TEACHER_DISTILLATION"
    ):
        raise ValueError("V133 preregistration changed")
    rows = load_rows(run_root)
    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(cpu_template))
    source_tree = restore_like(source, template)
    normalizer = source_tree[0]
    normalized_obs = (
        rows["obs"] - np.asarray(normalizer["mean"]["state"])
    ) / np.asarray(normalizer["std"]["state"])
    features = {
        "current_hidden": rows["h_out"],
        "normalized_obs_plus_h_in": np.concatenate(
            [normalized_obs, rows["h_in"]], axis=1
        ),
    }
    results = {
        name: audit_representation(
            value,
            rows["correction"],
            rows["plant"],
            rows["command"],
        )
        for name, value in features.items()
    }
    selected = next(
        (
            name
            for name in ("current_hidden", "normalized_obs_plus_h_in")
            if results[name]["qualifies"]
        ),
        None,
    )
    checks = {
        "v131_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            and v131.get("summary", {}).get("passing_cells") == 8
        ),
        "v132_valid_linear_rejection": (
            v132.get("status")
            == "PASS_WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT"
            and v132.get("decision")
            == "NO_STATIC_LINEAR_ROBUST_TEACHER_DISTILLATION"
        ),
        "dataset_exact_4800": rows["correction"].shape == (4_800, 14),
        "nonzero_corrections_are_subset_of_45_projected_events": (
            0
            < int(np.sum(np.abs(rows["correction"]) > NONZERO_FLOOR))
            <= rows["projected_joint_events"]
            == 45
        ),
        "corrected_rows_exact_17": (
            int(
                np.sum(
                    np.any(
                        np.abs(rows["correction"]) > NONZERO_FLOOR,
                        axis=1,
                    )
                )
            )
            == 17
        ),
        "all_values_finite": all(
            math.isfinite(float(value))
            for result in results.values()
            for value in result["combined"].values()
            if isinstance(value, (float, int))
        ),
        "leave_one_trace_out_only": True,
        "radius_derived_without_search": True,
        "read_only_no_training_behavior_or_hosted_compute": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        decision = "INVALID_NO_COMPACT_LOCAL_RESIDUAL"
    elif selected is not None:
        decision = f"EARN_ONE_V134_{selected.upper()}_LOCAL_RESIDUAL_CONTRACT"
    else:
        decision = "NO_COMPACT_LOCAL_RESIDUAL_FROM_NOMINAL_DATASET"
    payload = {
        "schema_version": "winner_v133.compact_local_residual_audit.v1",
        "status": (
            "PASS_WINNER_V133_COMPACT_LOCAL_RESIDUAL_AUDIT"
            if not failed
            else "INVALID_WINNER_V133_COMPACT_LOCAL_RESIDUAL_AUDIT"
        ),
        "failed_validity_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "method": {
            "validation": (
                "eight leave-one-(plant,command)-trace-out folds"
            ),
            "feature_normalization": (
                "training-fold z-score; dimensions below 1e-6 removed"
            ),
            "centers": "all nonzero per-joint teacher corrections",
            "radius": (
                "0.5 times each center's nearest zero-correction training "
                "distance; no radius search"
            ),
            "prediction": (
                "nearest same-joint center correction inside its compact "
                "radius, exact zero outside"
            ),
        },
        "thresholds": {
            "combined_corrected_ratio": "<=0.25",
            "combined_preservation_ratio": "<=0.01",
            "combined_event_recall": ">=0.90",
            "each_corrected_fold_corrected_ratio": "<1.0",
            "each_corrected_fold_preservation_ratio": "<=0.01",
            "x0_false_positive_joint_events": 0,
        },
        "representations": results,
        "selected_representation": selected,
        "decision": decision,
        "authority": {
            "v134_cpu_contract": decision.startswith("EARN_ONE_V134"),
            "formal_training": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V133 compact local residual audit\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Hidden qualifies: `{results['current_hidden']['qualifies']}`\n"
        "- Observation + recurrent state qualifies: "
        f"`{results['normalized_obs_plus_h_in']['qualifies']}`\n"
        f"- Decision: `{decision}`\n"
        "- Leave-one-trace-out CPU evidence; no training, behavior, or "
        "hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(decision)
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
