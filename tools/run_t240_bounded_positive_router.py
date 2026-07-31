#!/usr/bin/env python3
"""Run the preregistered bounded positive-router score audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    canonical_sha256,
)


PREREG = ANALYSIS / "t240_bounded_positive_router_preregistration.json"
OUTPUT = ANALYSIS / "t240_bounded_positive_router_result.json"
MARKDOWN = ANALYSIS / "T240_BOUNDED_POSITIVE_ROUTER_RESULT_20260731.md"
POSITIVE = "TORSO_COM_X_POS"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def router_parameters(path: Path) -> tuple[np.ndarray, np.float32]:
    model = onnx.load(path, load_external_data=True)
    values = {
        item.name: numpy_helper.to_array(item)
        for item in model.graph.initializer
    }
    return (
        np.asarray(values["positive_router_coefficient"], dtype=np.float32),
        np.asarray(
            values["positive_router_intercept"], dtype=np.float32
        ).reshape(-1)[0],
    )


def float32_score(
    context: list[float],
    coefficient: np.ndarray,
    intercept: np.float32,
) -> np.float32:
    return np.float32(
        np.matmul(
            np.asarray(context, dtype=np.float32),
            np.asarray(coefficient, dtype=np.float32),
        ).reshape(-1)[0]
        + intercept
    )


def derive_upper(rows: list[dict[str, Any]]) -> np.float32:
    positive_scores = [
        np.float32(row["score"])
        for row in rows
        if row["condition_id"] == POSITIVE
    ]
    false_positive_scores = [
        np.float32(row["score"])
        for row in rows
        if row["condition_id"] != POSITIVE and row["score"] >= 0.0
    ]
    if len(positive_scores) != 1 or not false_positive_scores:
        raise RuntimeError("T240 training-fit score geometry changed")
    high_positive = max(positive_scores)
    low_false_positive = min(false_positive_scores)
    return np.float32(
        np.float32(high_positive + low_false_positive) / np.float32(2.0)
    )


def classify(
    rows: list[dict[str, Any]], upper: np.float32
) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for row in rows:
        score = np.float32(row["score"])
        predicted = bool(score >= np.float32(0.0) and score <= upper)
        expected = row["condition_id"] == POSITIVE
        values.append(
            {
                **row,
                "predicted_x_positive": predicted,
                "expected_x_positive": expected,
                "correct": predicted == expected,
            }
        )
    return values


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T240: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if prereg["status"] != "PREREGISTERED_T240_BOUNDED_POSITIVE_ROUTER":
        raise RuntimeError("T240 preregistration status changed")
    for row in prereg["frozen_inputs"].values():
        path = Path(row["path"])
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"T240 frozen input changed: {path}")

    graph_parameters = {
        row["role"]: router_parameters(Path(row["path"]))
        for row in prereg["graphs"]
    }
    coefficient, intercept = graph_parameters["half"]
    t167 = json.loads(
        Path(prereg["frozen_inputs"]["t167_contexts"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    scored = [
        {
            "condition_id": row["condition_id"],
            "fit_id": row["fit_id"],
            "score": float(
                float32_score(row["context"], coefficient, intercept)
            ),
        }
        for row in t167["cells"]
    ]
    fits = sorted({row["fit_id"] for row in scored})
    cross_fit: list[dict[str, Any]] = []
    for train_fit, test_fit in ((fits[0], fits[1]), (fits[1], fits[0])):
        train = [row for row in scored if row["fit_id"] == train_fit]
        test = [row for row in scored if row["fit_id"] == test_fit]
        upper = derive_upper(train)
        classified = classify(test, upper)
        cross_fit.append(
            {
                "train_fit_id": train_fit,
                "test_fit_id": test_fit,
                "upper_bound": float(upper),
                "correct": sum(row["correct"] for row in classified),
                "cells": len(classified),
                "true_positives": sum(
                    row["predicted_x_positive"]
                    and row["expected_x_positive"]
                    for row in classified
                ),
                "false_positives": sum(
                    row["predicted_x_positive"]
                    and not row["expected_x_positive"]
                    for row in classified
                ),
                "rows": classified,
            }
        )

    positive_scores = [
        np.float32(row["score"])
        for row in scored
        if row["condition_id"] == POSITIVE
    ]
    false_positive_scores = [
        np.float32(row["score"])
        for row in scored
        if row["condition_id"] != POSITIVE and row["score"] >= 0.0
    ]
    maximum_positive = max(positive_scores)
    minimum_false_positive = min(false_positive_scores)
    combined_upper = np.float32(
        np.float32(maximum_positive + minimum_false_positive)
        / np.float32(2.0)
    )
    combined_rows = classify(scored, combined_upper)
    combined = {
        "lower_bound": 0.0,
        "upper_bound": float(combined_upper),
        "maximum_positive_score": float(maximum_positive),
        "minimum_false_positive_score": float(minimum_false_positive),
        "lower_margin": float(min(positive_scores)),
        "upper_separation_margin": float(
            minimum_false_positive - maximum_positive
        ),
        "correct": sum(row["correct"] for row in combined_rows),
        "cells": len(combined_rows),
        "true_positives": sum(
            row["predicted_x_positive"] and row["expected_x_positive"]
            for row in combined_rows
        ),
        "false_positives": sum(
            row["predicted_x_positive"] and not row["expected_x_positive"]
            for row in combined_rows
        ),
        "rows": combined_rows,
    }
    parameters_exact = (
        np.array_equal(
            graph_parameters["half"][0], graph_parameters["final"][0]
        )
        and graph_parameters["half"][1] == graph_parameters["final"][1]
    )
    checks = {
        "both_graph_router_parameters_bit_exact": parameters_exact,
        "both_cross_fit_classifiers_exact": all(
            row["correct"] == row["cells"] == 20
            and row["true_positives"] == 1
            and row["false_positives"] == 0
            for row in cross_fit
        ),
        "combined_classifier_exact": (
            combined["correct"] == combined["cells"] == 40
            and combined["true_positives"] == 2
            and combined["false_positives"] == 0
        ),
        "positive_lower_and_upper_margins_strictly_positive": (
            combined["lower_margin"] > 0.0
            and combined["upper_separation_margin"] > 0.0
        ),
        "home_offset_negative_rejected": all(
            not row["predicted_x_positive"]
            for row in combined_rows
            if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
        ),
        "saved_context_only_no_simulator_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    status = (
        "PASS_T240_BOUNDED_POSITIVE_ROUTER"
        if passed
        else "HOLD_T240_BOUNDED_POSITIVE_ROUTER"
    )
    decision = (
        prereg["decision_rule"]["pass_decision"]
        if passed
        else prereg["decision_rule"]["fail_decision"]
    )
    result_basis: dict[str, Any] = {
        "schema_version": "open_duck.t240_bounded_positive_router.v1",
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "cross_fit": cross_fit,
        "combined": combined,
        "execution": {
            "context_rows": len(scored),
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "router_transform_preregistration": passed,
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
        "# T240 bounded positive-router result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        f"- Cross-fit correctness: "
        f"`{[f'{row['correct']}/{row['cells']}' for row in cross_fit]}`\n"
        f"- Combined: `{combined['correct']}/{combined['cells']}`; upper "
        f"bound `{combined['upper_bound']:.9f}`; separation margin "
        f"`{combined['upper_separation_margin']:.9f}`\n"
        "- Simulator/behavior/training/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={decision}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
