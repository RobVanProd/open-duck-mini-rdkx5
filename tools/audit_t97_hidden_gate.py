#!/usr/bin/env python3
"""Run T97's preregistered read-only live-hidden gate falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t97_hidden_gate_preregistration.json"
RESULT = ANALYSIS / "t97_hidden_gate_result.json"
MARKDOWN = ANALYSIS / "T97_HIDDEN_GATE_RESULT_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(item: dict[str, Any], label: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(item["bytes"])
        or sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"T97 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T97_HIDDEN_GATE_FALSIFIER"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T97 preregistration identity changed")
    for label, item in value["inputs"].items():
        verify_receipt(item, label)
    for index, item in enumerate(value["traces"]):
        verify_receipt(item["trace"], f"trace:{index}")
    return value


def read_selected_rows(
    item: dict[str, Any], ticks: set[int], label: int
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    with Path(item["trace"]["path"]).open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            tick = int(row["tick"])
            if tick not in ticks:
                continue
            hidden = np.asarray(
                row["policy_state_output"]["h_out"][0], dtype=np.float64
            )
            if hidden.shape != (64,) or not np.all(np.isfinite(hidden)):
                raise RuntimeError("T97 hidden feature is invalid")
            selected.append(
                {
                    "checkpoint_id": item["checkpoint_id"],
                    "fit_id": item["fit_id"],
                    "command_x_m_s": float(item["command_x_m_s"]),
                    "population": item["population"],
                    "tick": tick,
                    "label": int(label),
                    "hidden": hidden,
                }
            )
    if {row["tick"] for row in selected} != ticks:
        raise RuntimeError(
            f"T97 trace ended before frozen ticks: {item['trace']['path']}"
        )
    return selected


def fit_ridge(train: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    x = np.stack([row["hidden"] for row in train])
    y = np.asarray([row["label"] for row in train], dtype=np.float64)
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale = np.where(scale > 1.0e-8, scale, 1.0)
    z = (x - mean) / scale
    design = np.concatenate([z, np.ones((len(z), 1))], axis=1)
    penalty = np.eye(design.shape[1], dtype=np.float64)
    penalty[-1, -1] = 0.0
    weights = np.linalg.solve(
        design.T @ design + penalty,
        design.T @ y,
    )
    return {"mean": mean, "scale": scale, "weights": weights}


def predict(
    model: dict[str, np.ndarray], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    x = np.stack([row["hidden"] for row in rows])
    z = (x - model["mean"]) / model["scale"]
    design = np.concatenate([z, np.ones((len(z), 1))], axis=1)
    scores = design @ model["weights"]
    return [
        {
            **{key: value for key, value in row.items() if key != "hidden"},
            "score": float(score),
            "prediction": 1 if score >= 0.0 else -1,
            "correct": bool((1 if score >= 0.0 else -1) == row["label"]),
        }
        for row, score in zip(rows, scores, strict=True)
    ]


def metrics(rows: Iterable[dict[str, Any]]) -> dict[str, float | int]:
    values = list(rows)
    positive = [row for row in values if row["label"] == 1]
    negative = [row for row in values if row["label"] == -1]
    recall = sum(row["prediction"] == 1 for row in positive) / len(positive)
    specificity = (
        sum(row["prediction"] == -1 for row in negative) / len(negative)
    )
    return {
        "rows": len(values),
        "accuracy": sum(row["correct"] for row in values) / len(values),
        "negative_com_recall": recall,
        "nominal_specificity": specificity,
        "balanced_accuracy": (recall + specificity) / 2.0,
    }


def folds(
    rows: list[dict[str, Any]], fields: tuple[str, ...]
) -> list[dict[str, Any]]:
    keys = sorted({tuple(row[field] for field in fields) for row in rows})
    output = []
    for key in keys:
        test = [
            row
            for row in rows
            if tuple(row[field] for field in fields) == key
        ]
        train = [
            row
            for row in rows
            if tuple(row[field] for field in fields) != key
        ]
        predicted = predict(fit_ridge(train), test)
        output.append(
            {
                "held_out": {
                    field: value for field, value in zip(fields, key, strict=True)
                },
                "metrics": metrics(predicted),
                "predictions": predicted,
            }
        )
    return output


def family_result(
    rows: list[dict[str, Any]], fields: tuple[str, ...]
) -> dict[str, Any]:
    values = folds(rows, fields)
    predictions = [
        prediction
        for fold in values
        for prediction in fold["predictions"]
    ]
    return {
        "fields": list(fields),
        "folds": values,
        "aggregate": metrics(predictions),
        "minimum_fold_balanced_accuracy": min(
            fold["metrics"]["balanced_accuracy"] for fold in values
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T97 requires --read-only-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T97 result: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T97 execution requires a clean worktree")

    prereg = load_preregistration()
    tick_set = {int(value) for value in prereg["population"]["ticks"]}
    rows: list[dict[str, Any]] = []
    for item in prereg["traces"]:
        rows.extend(
            read_selected_rows(
                item,
                tick_set,
                int(prereg["population"]["labels"][item["population"]]),
            )
        )
    families = {
        "checkpoint": family_result(rows, ("checkpoint_id",)),
        "fit": family_result(rows, ("fit_id",)),
        "command": family_result(rows, ("command_x_m_s",)),
        "exact_group": family_result(
            rows, ("checkpoint_id", "fit_id", "command_x_m_s")
        ),
    }
    thresholds = prereg["thresholds"]
    group_tick8 = [
        row
        for fold in families["exact_group"]["folds"]
        for row in fold["predictions"]
        if row["tick"] == 8
    ]
    tick8_metrics = metrics(group_tick8)
    checks = {
        "sample_population_exact": (
            len(rows) == prereg["population"]["sample_count"]
            and sum(row["label"] == 1 for row in rows) == len(rows) // 2
            and sum(row["label"] == -1 for row in rows) == len(rows) // 2
        ),
        "all_family_balanced_accuracies_pass": all(
            family["aggregate"]["balanced_accuracy"]
            >= thresholds["minimum_each_family_balanced_accuracy"]
            for family in families.values()
        ),
        "all_fold_balanced_accuracies_pass": all(
            family["minimum_fold_balanced_accuracy"]
            >= thresholds["minimum_each_fold_balanced_accuracy"]
            for family in families.values()
        ),
        "tick8_negative_recall_pass": (
            tick8_metrics["negative_com_recall"]
            >= thresholds["minimum_group_holdout_tick8_negative_recall"]
        ),
        "tick8_nominal_specificity_pass": (
            tick8_metrics["nominal_specificity"]
            >= thresholds["minimum_group_holdout_tick8_nominal_specificity"]
        ),
        "no_optimizer_simulator_hosted_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": "open_duck.t97_hidden_gate_result.v1",
        "status": (
            "PASS_T97_HIDDEN_GATE_FALSIFIER"
            if passed
            else "HOLD_T97_HIDDEN_GATE_FALSIFIER"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "families": families,
        "tick8_exact_group_holdout": tick8_metrics,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "trace_rows_read": len(rows),
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t98_cpu_contract_preregistration": passed,
            "training": False,
            "hosted_compute": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T97 live-hidden expert-gate result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Failed checks: `{failed}`",
                *[
                    (
                        f"- {name} balanced accuracy: "
                        f"`{family['aggregate']['balanced_accuracy']:.6f}`; "
                        "minimum fold: "
                        f"`{family['minimum_fold_balanced_accuracy']:.6f}`"
                    )
                    for name, family in families.items()
                ],
                (
                    "- Tick-8 exact-group negative recall / nominal "
                    f"specificity: `{tick8_metrics['negative_com_recall']:.6f}"
                    f" / {tick8_metrics['nominal_specificity']:.6f}`"
                ),
                "- Optimizer / simulator / hosted / robot: `0 / 0 / 0 / 0`",
                f"- Result SHA-256: `{result['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
