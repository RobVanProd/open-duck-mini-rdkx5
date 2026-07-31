#!/usr/bin/env python3
"""Run the preregistered T233 upper-Z context separability falsifier."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t233_upper_z_context_separability_preregistration.json"
OUTPUT = ANALYSIS / "t233_upper_z_context_separability_result.json"
MARKDOWN = ANALYSIS / "T233_UPPER_Z_CONTEXT_SEPARABILITY_RESULT_20260730.md"


def classifier(
    train_rows: list[dict[str, Any]],
    test_rows: list[dict[str, Any]],
    *,
    positive: str,
    control: str,
) -> dict[str, Any]:
    train = {row["condition_id"]: row for row in train_rows}
    direction = np.asarray(train[positive]["context"], dtype=np.float64)
    direction -= np.asarray(train[control]["context"], dtype=np.float64)
    norm = float(np.linalg.norm(direction))
    if not np.isfinite(norm) or norm <= 0.0:
        raise RuntimeError("T233 zero/invalid per-fit direction")
    direction /= norm
    train_scores = {
        row["condition_id"]: float(
            np.dot(np.asarray(row["context"], dtype=np.float64), direction)
        )
        for row in train_rows
    }
    positive_score = train_scores[positive]
    maximum_negative = max(
        score
        for condition, score in train_scores.items()
        if condition != positive
    )
    threshold = 0.5 * (positive_score + maximum_negative)
    rows = []
    for row in test_rows:
        score = float(
            np.dot(np.asarray(row["context"], dtype=np.float64), direction)
        )
        expected = row["condition_id"] == positive
        predicted = score >= threshold
        rows.append(
            {
                "condition_id": row["condition_id"],
                "fit_id": row["fit_id"],
                "score": score,
                "expected_upper_z": expected,
                "predicted_upper_z": predicted,
                "correct": expected == predicted,
            }
        )
    return {
        "direction": direction.astype(float).tolist(),
        "direction_norm_before_unit": norm,
        "positive_training_score": positive_score,
        "maximum_negative_training_score": maximum_negative,
        "training_margin": positive_score - maximum_negative,
        "threshold": threshold,
        "test_rows": rows,
        "test_correct": sum(row["correct"] for row in rows),
        "test_cells": len(rows),
        "true_positives": sum(
            row["predicted_upper_z"] and row["expected_upper_z"]
            for row in rows
        ),
        "false_positives": sum(
            row["predicted_upper_z"] and not row["expected_upper_z"]
            for row in rows
        ),
    }


def combined_classifier(
    cells: list[dict[str, Any]],
    *,
    positive: str,
    control: str,
) -> dict[str, Any]:
    by_fit = {
        fit: {row["condition_id"]: row for row in cells if row["fit_id"] == fit}
        for fit in sorted({row["fit_id"] for row in cells})
    }
    directions = []
    for rows in by_fit.values():
        direction = np.asarray(
            rows[positive]["context"], dtype=np.float64
        ) - np.asarray(rows[control]["context"], dtype=np.float64)
        direction /= np.linalg.norm(direction)
        directions.append(direction)
    direction = np.mean(directions, axis=0)
    norm = float(np.linalg.norm(direction))
    if not np.isfinite(norm) or norm <= 0.0:
        raise RuntimeError("T233 zero/invalid combined direction")
    direction /= norm
    rows = []
    for row in cells:
        expected = row["condition_id"] == positive
        rows.append(
            {
                "condition_id": row["condition_id"],
                "fit_id": row["fit_id"],
                "score": float(
                    np.dot(
                        np.asarray(row["context"], dtype=np.float64),
                        direction,
                    )
                ),
                "expected_upper_z": expected,
            }
        )
    minimum_positive = min(
        row["score"] for row in rows if row["expected_upper_z"]
    )
    maximum_negative = max(
        row["score"] for row in rows if not row["expected_upper_z"]
    )
    threshold = 0.5 * (minimum_positive + maximum_negative)
    for row in rows:
        row["predicted_upper_z"] = row["score"] >= threshold
        row["correct"] = (
            row["predicted_upper_z"] == row["expected_upper_z"]
        )
    return {
        "direction": direction.astype(float).tolist(),
        "threshold": threshold,
        "minimum_positive_score": minimum_positive,
        "maximum_negative_score": maximum_negative,
        "margin": minimum_positive - maximum_negative,
        "rows": rows,
        "correct_cells": sum(row["correct"] for row in rows),
        "cells": len(rows),
        "true_positives": sum(
            row["predicted_upper_z"] and row["expected_upper_z"]
            for row in rows
        ),
        "false_positives": sum(
            row["predicted_upper_z"] and not row["expected_upper_z"]
            for row in rows
        ),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T233: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        name: value
        for name, value in prereg.items()
        if name != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T233_UPPER_Z_CONTEXT_SEPARABILITY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T233 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)

    t167 = json.loads(
        Path(prereg["frozen_inputs"]["t167_contexts"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    cells = t167["cells"]
    positive = prereg["population"]["positive_condition"]
    control = prereg["population"]["control_condition"]
    fits = prereg["population"]["fits"]
    cross_fit = []
    for train_fit, test_fit in ((fits[0], fits[1]), (fits[1], fits[0])):
        value = classifier(
            [row for row in cells if row["fit_id"] == train_fit],
            [row for row in cells if row["fit_id"] == test_fit],
            positive=positive,
            control=control,
        )
        value["train_fit_id"] = train_fit
        value["test_fit_id"] = test_fit
        cross_fit.append(value)
    combined = combined_classifier(
        cells, positive=positive, control=control
    )
    checks = {
        "forty_finite_contexts_reused": (
            len(cells) == 40
            and all(
                len(row["context"]) == 64
                and np.all(np.isfinite(row["context"]))
                for row in cells
            )
        ),
        "both_cross_fit_classifiers_exact": all(
            row["test_correct"] == row["test_cells"] == 20
            and row["true_positives"] == 1
            and row["false_positives"] == 0
            and row["training_margin"] > 0.0
            for row in cross_fit
        ),
        "combined_classifier_exact_positive_margin": (
            combined["correct_cells"] == combined["cells"] == 40
            and combined["true_positives"] == 2
            and combined["false_positives"] == 0
            and combined["margin"] > 0.0
        ),
        "no_simulator_behavior_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    passed = not failed
    summary = {
        "contexts": len(cells),
        "cross_fit_correct": [
            f"{row['test_correct']}/{row['test_cells']}" for row in cross_fit
        ],
        "cross_fit_training_margins": [
            row["training_margin"] for row in cross_fit
        ],
        "combined_correct": (
            f"{combined['correct_cells']}/{combined['cells']}"
        ),
        "combined_margin": combined["margin"],
        "combined_true_positives": combined["true_positives"],
        "combined_false_positives": combined["false_positives"],
    }
    result_basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t233_upper_z_context_separability_result.v1"
        ),
        "status": (
            "PASS_T233_UPPER_Z_CONTEXT_SEPARABILITY"
            if passed
            else "HOLD_T233_UPPER_Z_CONTEXT_SEPARABILITY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "cross_fit_classifiers": cross_fit,
        "combined_classifier": combined,
        "interpretation": {
            "route_semantics": (
                "a future upper-Z expert can be selected from the existing "
                "automatic calibration context and remain exactly off on all "
                "38 non-upper-Z context cells"
                if passed
                else (
                    "the startup context cannot safely isolate upper-Z; "
                    "static routing is closed"
                )
            ),
            "selection_scope": (
                "separability only; no correction head, policy behavior, or "
                "training is authorized by this result"
            ),
        },
        "execution": {
            "context_rows": len(cells),
            "simulator_calls": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "route_cpu_contract_preregistration": passed,
            "behavior": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    result = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T233 upper-Z context separability result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        f"- Cross-fit correctness: `{summary['cross_fit_correct']}`\n"
        f"- Combined correctness/margin: `{summary['combined_correct']}` / "
        f"`{summary['combined_margin']:.9f}`\n"
        "- Simulator/behavior/training/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(json.dumps(summary, allow_nan=False, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
