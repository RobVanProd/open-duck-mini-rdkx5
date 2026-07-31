#!/usr/bin/env python3
"""Run the preregistered read-only torso-COM IMU-prefix decode probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


CONDITION_TO_CLASS = {
    "TORSO_COM_X_NEG": "NEG",
    "NOMINAL": "NOMINAL",
    "TORSO_COM_X_POS": "POS",
}
ARMS = {
    "A05_DIRECT": (1003520, 2007040),
    "U05_DIRECT": (1003520, 2007040),
    "U_CURRICULUM": (512000, 1024000),
}
FITS = ("p30", "p31_34")
COMMANDS = (0.0, 0.074, 0.077, 0.08)
COMMAND_RE = re.compile(r"^x([0-9]+\.[0-9]+)_seed([0-9]+)_.*\.jsonl$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_manifest(trace_root: Path) -> tuple[str, list[dict[str, Any]]]:
    rows = []
    lines = []
    for path in sorted(trace_root.rglob("*.jsonl")):
        rel = path.relative_to(trace_root).as_posix()
        digest = sha256(path)
        size = path.stat().st_size
        rows.append({"path": rel, "sha256": digest, "bytes": size})
        # Frozen preregistration canonicalization: digest immediately followed
        # by the relative path, then one newline (matching the recorded shell
        # manifest stream used to derive trace_manifest_sha256).
        lines.append(f"{digest}{rel}\n")
    digest = hashlib.sha256("".join(lines).encode()).hexdigest()
    return digest, rows


def command_key(value: float) -> str:
    return f"{value:.3f}"


def parse_trace(path: Path, trace_root: Path, minimum_ticks: int) -> dict[str, Any]:
    rel = path.relative_to(trace_root)
    if len(rel.parts) != 5:
        raise ValueError(f"unexpected trace path depth: {rel}")
    condition, arm, step_text, fit, filename = rel.parts
    match = COMMAND_RE.match(filename)
    if match is None:
        raise ValueError(f"unexpected trace filename: {filename}")
    command = float(match.group(1))
    seed = int(match.group(2))
    step = int(step_text)
    if condition not in CONDITION_TO_CLASS:
        raise ValueError(f"unexpected condition: {condition}")
    if arm not in ARMS or step not in ARMS[arm]:
        raise ValueError(f"unexpected arm/checkpoint: {arm}/{step}")
    if fit not in FITS:
        raise ValueError(f"unexpected fit: {fit}")
    if command_key(command) not in {command_key(item) for item in COMMANDS}:
        raise ValueError(f"unexpected command: {command}")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if len(rows) < minimum_ticks:
        raise ValueError(f"trace shorter than {minimum_ticks}: {rel}")
    expected_ticks = list(range(len(rows)))
    if [int(row.get("tick", -1)) for row in rows] != expected_ticks:
        raise ValueError(f"non-contiguous ticks: {rel}")
    if any("obs_state" in row for row in rows):
        raise ValueError(f"full observation unexpectedly present: {rel}")
    obs = np.asarray([row.get("obs0_6") for row in rows], dtype=np.float64)
    if obs.shape != (len(rows), 6) or not np.all(np.isfinite(obs)):
        raise ValueError(f"invalid obs0_6: {rel}")
    return {
        "path": str(path.resolve()),
        "relative_path": rel.as_posix(),
        "condition": condition,
        "class_name": CONDITION_TO_CLASS[condition],
        "arm": arm,
        "checkpoint": step,
        "fit": fit,
        "command_x": command,
        "command_key": command_key(command),
        "seed": seed,
        "ticks": len(rows),
        "obs": obs,
    }


def confusion(y_true: np.ndarray, y_pred: np.ndarray, classes: int) -> np.ndarray:
    out = np.zeros((classes, classes), dtype=np.int64)
    for true, pred in zip(y_true, y_pred, strict=True):
        out[int(true), int(pred)] += 1
    return out


def metrics(y_true: np.ndarray, y_pred: np.ndarray, classes: int) -> dict[str, Any]:
    cm = confusion(y_true, y_pred, classes)
    recalls = []
    f1s = []
    for index in range(classes):
        tp = int(cm[index, index])
        fn = int(np.sum(cm[index, :]) - tp)
        fp = int(np.sum(cm[:, index]) - tp)
        recall = tp / (tp + fn) if tp + fn else 0.0
        precision = tp / (tp + fp) if tp + fp else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        recalls.append(recall)
        f1s.append(f1)
    return {
        "samples": int(y_true.size),
        "accuracy": float(np.mean(y_true == y_pred)),
        "macro_f1": float(np.mean(f1s)),
        "class_recall": recalls,
        "confusion": cm.tolist(),
    }


def ridge_projection(x_train: np.ndarray, x_test: np.ndarray, l2: float) -> np.ndarray:
    mean = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    std = np.where(std == 0.0, 1.0, std)
    train = (x_train - mean) / std
    test = (x_test - mean) / std
    train = np.column_stack([train, np.ones(train.shape[0])])
    test = np.column_stack([test, np.ones(test.shape[0])])
    regularizer = np.eye(train.shape[1]) * l2
    regularizer[-1, -1] = 0.0
    solved = np.linalg.solve(train.T @ train + regularizer, train.T)
    return test @ solved


def fold_definitions(samples: list[dict[str, Any]], prereg: dict) -> list[dict[str, Any]]:
    definitions = []
    for family, values in prereg["folds"].items():
        field = "command_key" if family == "command_x" else family
        for value in values:
            compare = command_key(float(value)) if family == "command_x" else value
            test = np.asarray(
                [index for index, sample in enumerate(samples) if sample[field] == compare],
                dtype=np.int64,
            )
            train = np.asarray(
                [index for index, sample in enumerate(samples) if sample[field] != compare],
                dtype=np.int64,
            )
            definitions.append(
                {
                    "family": family,
                    "held_out": value,
                    "train": train,
                    "test": test,
                }
            )
    return definitions


def validate_matrix_references(
    eval_root: Path, trace_root: Path, trace_paths: set[Path]
) -> dict[str, Any]:
    refs = []
    matrix_files = []
    for prefix in CONDITION_TO_CLASS:
        found = sorted(eval_root.glob(f"{prefix}_*.json"))
        if len(found) != 12:
            raise ValueError(f"expected 12 {prefix} matrix files, got {len(found)}")
        matrix_files.extend(found)
        for path in found:
            payload = json.loads(path.read_text())
            if len(payload.get("runs", [])) != 4:
                raise ValueError(f"matrix does not contain four cells: {path}")
            for run in payload["runs"]:
                raw = run.get("trace_jsonl")
                if not raw:
                    raise ValueError(f"matrix run omits trace path: {path}")
                candidate = Path(raw)
                marker = Path("outputs/analysis/ground_up_torso_com_behavior_eval/traces")
                try:
                    rel = candidate.relative_to(marker)
                except ValueError as exc:
                    raise ValueError(f"unexpected matrix trace reference: {raw}") from exc
                refs.append((trace_root / rel).resolve())
    if len(refs) != 144 or len(set(refs)) != 144 or set(refs) != trace_paths:
        raise ValueError("matrix-to-trace references are not an exact 144-file bijection")
    return {
        "matrix_files": len(matrix_files),
        "matrix_cells": len(refs),
        "trace_reference_bijection": True,
    }


def evaluate_window(
    x: np.ndarray,
    labels: np.ndarray,
    folds: list[dict[str, Any]],
    class_names: list[str],
    l2: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fold_rows = []
    family_truth: dict[str, list[np.ndarray]] = defaultdict(list)
    family_pred: dict[str, list[np.ndarray]] = defaultdict(list)
    projections = []
    for fold in folds:
        train, test = fold["train"], fold["test"]
        projection = ridge_projection(x[train], x[test], l2)
        scores = projection @ np.eye(len(class_names))[labels[train]]
        pred = np.argmax(scores, axis=1)
        item = metrics(labels[test], pred, len(class_names))
        item.update({"family": fold["family"], "held_out": fold["held_out"]})
        fold_rows.append(item)
        family_truth[fold["family"]].append(labels[test])
        family_pred[fold["family"]].append(pred)
        projections.append({"projection": projection, "train": train, "test": test})
    family_rows = {}
    for family in family_truth:
        family_rows[family] = metrics(
            np.concatenate(family_truth[family]),
            np.concatenate(family_pred[family]),
            len(class_names),
        )
    summary = {
        "minimum_fold_accuracy": min(row["accuracy"] for row in fold_rows),
        "folds": fold_rows,
        "families": family_rows,
        "minimum_pooled_class_recall": min(
            recall for row in family_rows.values() for recall in row["class_recall"]
        ),
    }
    return summary, projections


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Ground-Up Torso-COM Observability Decode Result",
        "",
        f"status: `{payload['status']}`",
        f"decision: `{payload['decision']}`",
        f"earliest passing window: `{payload['earliest_passing_window_ticks']}`",
        f"family-wise permutation p: `{payload['permutation']['familywise_p_value']:.9f}`",
        "",
        "| N ticks | min fold acc | arm F1 | command F1 | fit F1 | min recall | pass |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for key, row in payload["windows"].items():
        families = row["families"]
        lines.append(
            f"| {key} | {row['minimum_fold_accuracy']:.6f} | "
            f"{families['arm']['macro_f1']:.6f} | "
            f"{families['command_x']['macro_f1']:.6f} | "
            f"{families['fit']['macro_f1']:.6f} | "
            f"{row['minimum_pooled_class_recall']:.6f} | `{row['pass']}` |"
        )
    lines.extend([
        "",
        "Only exact `obs0_6` prefixes were used. No telemetry, outcome, reward, policy training, simulator replay, GPU, RDK-X5, or robot data entered the probe.",
        "",
        payload["interpretation"],
        "",
    ])
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--source-decision", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    class_names = prereg["classes"]
    class_index = {name: index for index, name in enumerate(class_names)}
    source = prereg["source"]
    trace_root = args.trace_root.resolve()
    manifest_hash, manifest_rows = canonical_manifest(trace_root)
    if manifest_hash != source["trace_manifest_sha256"]:
        raise ValueError(f"trace manifest hash mismatch: {manifest_hash}")
    if len(manifest_rows) != source["trace_count"]:
        raise ValueError("trace count mismatch")
    if sum(row["bytes"] for row in manifest_rows) != source["trace_bytes"]:
        raise ValueError("trace byte count mismatch")
    if sha256(args.source_decision) != source["decision_sha256"]:
        raise ValueError("source decision hash mismatch")

    samples = [
        parse_trace(trace_root / row["path"], trace_root, source["minimum_trace_ticks"])
        for row in manifest_rows
    ]
    if any(sample["seed"] != 167931544 for sample in samples):
        raise ValueError("seed mismatch")
    class_counts = {name: sum(s["class_name"] == name for s in samples) for name in class_names}
    if class_counts != {name: 48 for name in class_names}:
        raise ValueError(f"class counts mismatch: {class_counts}")
    matched: dict[tuple, list[int]] = defaultdict(list)
    for index, sample in enumerate(samples):
        matched[(sample["arm"], sample["checkpoint"], sample["fit"], sample["command_key"])].append(index)
    if len(matched) != 48 or any(
        sorted(samples[index]["class_name"] for index in indices) != sorted(class_names)
        for indices in matched.values()
    ):
        raise ValueError("matched triplet contract failed")
    matrix_contract = validate_matrix_references(
        args.eval_root.resolve(), trace_root, {Path(sample["path"]) for sample in samples}
    )
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CUDA_VISIBLE_DEVICES must be empty for the CPU-only probe")

    labels = np.asarray([class_index[sample["class_name"]] for sample in samples], dtype=np.int64)
    folds = fold_definitions(samples, prereg)
    if len(folds) != 9:
        raise ValueError(f"expected nine folds, got {len(folds)}")
    l2 = float(prereg["probe"]["l2"])
    windows = {}
    projection_cache = {}
    for ticks in prereg["windows_ticks"]:
        x = np.stack([sample["obs"][:ticks].reshape(-1) for sample in samples])
        summary, projections = evaluate_window(x, labels, folds, class_names, l2)
        windows[str(ticks)] = summary
        projection_cache[ticks] = projections

    rng = np.random.default_rng(prereg["permutations"]["seed"])
    null_statistics = []
    identity = np.eye(len(class_names))
    for _ in range(prereg["permutations"]["count"]):
        permuted = labels.copy()
        for indices in matched.values():
            order = np.asarray(indices, dtype=np.int64)
            permuted[order] = rng.permutation(permuted[order])
        best = 0.0
        for ticks in prereg["windows_ticks"]:
            minimum = 1.0
            for fold, cached in zip(folds, projection_cache[ticks], strict=True):
                train, test = cached["train"], cached["test"]
                pred = np.argmax(cached["projection"] @ identity[permuted[train]], axis=1)
                minimum = min(minimum, float(np.mean(permuted[test] == pred)))
            best = max(best, minimum)
        null_statistics.append(best)

    observed_max = max(row["minimum_fold_accuracy"] for row in windows.values())
    exceedances = sum(value >= observed_max for value in null_statistics)
    familywise_p = (1 + exceedances) / (1 + len(null_statistics))
    thresholds = prereg["thresholds"]
    passing = []
    for ticks in prereg["windows_ticks"]:
        row = windows[str(ticks)]
        row["checks"] = {
            "minimum_fold_accuracy": row["minimum_fold_accuracy"]
            >= thresholds["minimum_fold_accuracy"],
            "pooled_macro_f1_each_family": all(
                item["macro_f1"] >= thresholds["minimum_pooled_macro_f1_per_family"]
                for item in row["families"].values()
            ),
            "minimum_pooled_class_recall": row["minimum_pooled_class_recall"]
            >= thresholds["minimum_pooled_class_recall"],
            "familywise_permutation_p": familywise_p
            <= thresholds["maximum_familywise_permutation_p"],
        }
        row["pass"] = all(row["checks"].values())
        if row["pass"]:
            passing.append(ticks)

    earliest = min(passing) if passing else None
    if earliest == 1:
        decision = prereg["decision"]["instantaneous"]
        interpretation = (
            "The exact instantaneous gyro/accelerometer input linearly decodes COM class. "
            "This supports a separately preregistered objective/exploitation study; it does not select memory."
        )
    elif earliest is not None:
        decision = prereg["decision"]["temporal"]
        interpretation = (
            "A multi-tick gyro/accelerometer prefix is the earliest passing decode. "
            "This supports a separately preregistered memory or estimator-input arm."
        )
    else:
        decision = prereg["decision"]["none"]
        interpretation = (
            "The frozen linear probe does not decode COM from the saved six-input prefix. "
            "Because full 115-D observations were not recorded, this does not establish observation insufficiency."
        )

    checks = {
        "preregistration_status_exact": prereg["status"]
        == "PREREGISTERED_READ_ONLY_CPU_LINEAR_DECODE",
        "trace_manifest_exact": manifest_hash == source["trace_manifest_sha256"],
        "trace_count_exact": len(samples) == 144,
        "trace_bytes_exact": sum(row["bytes"] for row in manifest_rows)
        == source["trace_bytes"],
        "class_balance_exact": class_counts == {name: 48 for name in class_names},
        "matched_triplets_exact": len(matched) == 48,
        "matrix_trace_bijection_exact": matrix_contract["trace_reference_bijection"],
        "only_obs0_6_used": True,
        "all_windows_pre_fall": max(prereg["windows_ticks"])
        < min(sample["ticks"] for sample in samples),
        "cpu_only": os.environ.get("CUDA_VISIBLE_DEVICES") == "",
        "training_reward_not_used": True,
    }
    failed = [name for name, value in checks.items() if not value]
    status = "PASS_TORSO_COM_OBSERVABILITY_DECODE_EVIDENCE" if not failed else "FAIL_TORSO_COM_OBSERVABILITY_DECODE_EVIDENCE"
    payload = {
        "schema_version": "ground_up_torso_com_observability_decode_result.v1",
        "status": status,
        "decision": decision if not failed else "INVALID_EVIDENCE",
        "earliest_passing_window_ticks": earliest,
        "checks": checks,
        "failed_checks": failed,
        "inputs": {
            "preregistration": str(args.preregistration.resolve()),
            "preregistration_sha256": sha256(args.preregistration),
            "source_decision": str(args.source_decision.resolve()),
            "source_decision_sha256": sha256(args.source_decision),
        },
        "corpus": {
            "trace_root": str(trace_root),
            "trace_manifest_sha256": manifest_hash,
            "trace_files": len(samples),
            "trace_bytes": sum(row["bytes"] for row in manifest_rows),
            "class_counts": class_counts,
            "minimum_ticks": min(sample["ticks"] for sample in samples),
            **matrix_contract,
        },
        "windows": windows,
        "permutation": {
            "count": len(null_statistics),
            "seed": prereg["permutations"]["seed"],
            "observed_maximum_minimum_fold_accuracy": observed_max,
            "familywise_p_value": familywise_p,
            "null_min": float(np.min(null_statistics)),
            "null_median": float(np.median(null_statistics)),
            "null_p95": float(np.percentile(null_statistics, 95)),
            "null_max": float(np.max(null_statistics)),
            "exceedances": exceedances,
        },
        "interpretation": interpretation,
        "selection_uses_training_reward": False,
        "authority": {
            "separate_preregistration_required": True,
            "policy_training": False,
            "simulator_replay": False,
            "colab": False,
            "gpu_or_igpu": False,
            "runtime_design": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, args.output_md)
    print(json.dumps({"status": status, "decision": payload["decision"], "earliest_window": earliest, "p": familywise_p}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
