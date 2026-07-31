#!/usr/bin/env python3
"""Audit nested-window behavior and supersede overstated COM decode claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from run_ground_up_torso_com_observability_decode import (
    canonical_manifest,
    fold_definitions,
    parse_trace,
    ridge_projection,
    sha256,
)


def predict(x: np.ndarray, labels: np.ndarray, fold: dict) -> np.ndarray:
    train, test = fold["train"], fold["test"]
    projection = ridge_projection(x[train], x[test], 1.0)
    return np.argmax(projection @ np.eye(3)[labels[train]], axis=1)


def weight_norms(x: np.ndarray, labels: np.ndarray, fold: dict) -> list[float]:
    train = fold["train"]
    mean = np.mean(x[train], axis=0)
    std = np.std(x[train], axis=0)
    std = np.where(std == 0.0, 1.0, std)
    design = (x[train] - mean) / std
    design = np.column_stack([design, np.ones(design.shape[0])])
    regularizer = np.eye(design.shape[1])
    regularizer[-1, -1] = 0.0
    weights = np.linalg.solve(
        design.T @ design + regularizer,
        design.T @ np.eye(3)[labels[train]],
    )
    ticks = x.shape[1] // 6
    return [float(np.linalg.norm(weights[6 * tick : 6 * (tick + 1)])) for tick in range(ticks)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    result = json.loads(args.result.read_text())
    root = args.trace_root.resolve()
    _, manifest = canonical_manifest(root)
    samples = [
        parse_trace(root / item["path"], root, prereg["source"]["minimum_trace_ticks"])
        for item in manifest
    ]
    class_index = {name: index for index, name in enumerate(prereg["classes"])}
    labels = np.asarray([class_index[item["class_name"]] for item in samples])
    folds = fold_definitions(samples, prereg)
    tick0 = np.stack([item["obs"][0] for item in samples])

    windows = {}
    prefix_exact = True
    standardization_exact = True
    for ticks in prereg["windows_ticks"]:
        x = np.stack([item["obs"][:ticks].reshape(-1) for item in samples])
        prefix_exact = prefix_exact and np.array_equal(x[:, :6], tick0)
        full_accuracy = []
        tick0_accuracy = []
        last_accuracy = []
        for fold in folds:
            train, test = fold["train"], fold["test"]
            full_accuracy.append(float(np.mean(predict(x, labels, fold) == labels[test])))
            tick0_accuracy.append(
                float(np.mean(predict(x[:, :6], labels, fold) == labels[test]))
            )
            last_accuracy.append(
                float(np.mean(predict(x[:, -6:], labels, fold) == labels[test]))
            )
            standardization_exact = standardization_exact and np.array_equal(
                np.mean(x[train, :6], axis=0), np.mean(tick0[train], axis=0)
            ) and np.array_equal(
                np.std(x[train, :6], axis=0), np.std(tick0[train], axis=0)
            )
        windows[str(ticks)] = {
            "full_prefix_minimum_fold_accuracy": min(full_accuracy),
            "tick0_only_minimum_fold_accuracy": min(tick0_accuracy),
            "last_tick_only_minimum_fold_accuracy": min(last_accuracy),
        }

    command_zero = next(
        fold
        for fold in folds
        if fold["family"] == "command_x" and float(fold["held_out"]) == 0.0
    )
    coefficient_audit = {}
    for ticks in (1, 2, 4, 8, 16):
        x = np.stack([item["obs"][:ticks].reshape(-1) for item in samples])
        test = command_zero["test"]
        pred = predict(x, labels, command_zero)
        coefficient_audit[str(ticks)] = {
            "held_out_command_x": 0.0,
            "accuracy": float(np.mean(pred == labels[test])),
            "weight_norm_by_tick": weight_norms(x, labels, command_zero),
        }

    unique_by_class = {}
    for name, index in class_index.items():
        unique_by_class[name] = int(np.unique(tick0[labels == index], axis=0).shape[0])

    checks = {
        "source_result_reproduced": result["decision"]
        == "PASS_INSTANTANEOUS_IMU_COM_DECODE",
        "all_windows_are_exact_tick0_prefixes": prefix_exact,
        "tick0_standardization_identical_at_every_window": standardization_exact,
        "one_unique_tick0_vector_per_class": unique_by_class
        == {"NEG": 1, "NOMINAL": 1, "POS": 1},
        "tick0_only_probe_perfect_for_every_window": all(
            row["tick0_only_minimum_fold_accuracy"] == 1.0 for row in windows.values()
        ),
        "full_prefix_probe_is_nonmonotone": [
            windows[str(ticks)]["full_prefix_minimum_fold_accuracy"]
            for ticks in prereg["windows_ticks"]
        ]
        != sorted(
            windows[str(ticks)]["full_prefix_minimum_fold_accuracy"]
            for ticks in prereg["windows_ticks"]
        ),
        "n2_full_prefix_regresses_while_tick0_is_preserved": windows["2"][
            "full_prefix_minimum_fold_accuracy"
        ]
        < 1.0
        and windows["2"]["tick0_only_minimum_fold_accuracy"] == 1.0,
        "permutation_units_not_independent": len(np.unique(tick0, axis=0)) == 3
        and tick0.shape[0] == 144,
    }
    failed = [name for name, value in checks.items() if not value]
    status = (
        "PASS_TORSO_COM_DECODE_INTERPRETATION_CORRECTION"
        if not failed
        else "FAIL_TORSO_COM_DECODE_INTERPRETATION_CORRECTION"
    )
    payload = {
        "schema_version": "ground_up_torso_com_decode_interpretation_correction.v1",
        "status": status,
        "decision": "SUPERSEDE_DECODE_SELECTION_NO_ARM_FAMILY_SELECTED"
        if not failed
        else "INVALID_EVIDENCE",
        "checks": checks,
        "failed_checks": failed,
        "source_result_sha256": sha256(args.result),
        "source_preregistration_sha256": sha256(args.preregistration),
        "effective_tick0_prototypes": 3,
        "nominal_trace_rows": 144,
        "permutation_p_value_interpretable": False,
        "windows": windows,
        "command_zero_coefficient_audit": coefficient_audit,
        "preserved_measurement": (
            "Under the deterministic reset protocol, tick-zero accelerometer is an exact function of COM class and is inside the actor input."
        ),
        "invalidated_inferences": [
            "family-wise statistical significance from 144 non-independent tick-zero duplicates",
            "N>1 prefix accuracy as a monotone measure of information availability",
            "history or memory is not selected",
            "objective or exploitation study is selected next",
        ],
        "cause": (
            "The fixed all-feature ridge reallocates regularized weight from the preserved tick-zero separator onto later command-dependent nuisance dimensions; construction and standardization preserve tick zero exactly."
        ),
        "authority": {
            "preregister_full_observation_cpu_replay_and_sensitivity_contract": not failed,
            "objective_study_selected": False,
            "memory_selected": False,
            "policy_training": False,
            "gpu_or_igpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Torso-COM Decode Interpretation Correction",
        "",
        f"status: `{status}`",
        f"decision: `{payload['decision']}`",
        "",
        "| N | full prefix min acc | tick-0-only min acc | last-tick-only min acc |",
        "|---:|---:|---:|---:|",
    ]
    for ticks in prereg["windows_ticks"]:
        row = windows[str(ticks)]
        lines.append(
            f"| {ticks} | {row['full_prefix_minimum_fold_accuracy']:.6f} | "
            f"{row['tick0_only_minimum_fold_accuracy']:.6f} | "
            f"{row['last_tick_only_minimum_fold_accuracy']:.6f} |"
        )
    lines.extend([
        "",
        payload["preserved_measurement"],
        "",
        payload["cause"],
        "",
        "The 1/1001 permutation value is withdrawn as an inferential claim because the 144 tick-zero rows reduce to three deterministic class prototypes. The N>1 table cannot select or reject memory. No objective, optimizer, memory, estimator, explicit-COM, or range-narrowing route is selected.",
        "",
    ])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": payload["decision"], "failed_checks": failed}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
