#!/usr/bin/env python3
"""Run the frozen X-positive context-router separability audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    canonical_sha256,
)
from run_t167_calibration_context_separability import (
    classifier,
    combined_classifier,
)


PREREG = (
    ANALYSIS / "t239_x_positive_router_separability_preregistration.json"
)
OUTPUT = ANALYSIS / "t239_x_positive_router_separability_result.json"
MARKDOWN = (
    ANALYSIS / "T239_X_POSITIVE_ROUTER_SEPARABILITY_RESULT_20260731.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def renamed_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "condition_id": row["condition_id"],
            "score": row["score"],
            "predicted_x_positive": row["predicted_y_negative"],
            "expected_x_positive": row["expected_y_negative"],
            "correct": row["correct"],
        }
        for row in rows
    ]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T239: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg["status"]
        != "PREREGISTERED_T239_X_POSITIVE_ROUTER_SEPARABILITY"
    ):
        raise RuntimeError("T239 preregistration status changed")
    for row in prereg["frozen_inputs"].values():
        path = Path(row["path"])
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"T239 frozen input changed: {path}")

    t167 = json.loads(
        Path(prereg["frozen_inputs"]["t167_contexts"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    cells = t167["cells"]
    positive = prereg["classifier"]["positive_condition"]
    control = prereg["classifier"]["control_condition"]
    fits = sorted({row["fit_id"] for row in cells})
    cross_fit: list[dict[str, Any]] = []
    for train_fit, test_fit in ((fits[0], fits[1]), (fits[1], fits[0])):
        value = classifier(
            [row for row in cells if row["fit_id"] == train_fit],
            [row for row in cells if row["fit_id"] == test_fit],
            positive=positive,
            control=control,
        )
        value["train_fit_id"] = train_fit
        value["test_fit_id"] = test_fit
        value["test_x_positive_true_positives"] = value.pop(
            "test_y_negative_true_positives"
        )
        value["test_rows"] = renamed_rows(value["test_rows"])
        cross_fit.append(value)

    combined = combined_classifier(
        cells, positive=positive, control=control
    )
    combined["rows"] = [
        {
            **{
                key: value
                for key, value in row.items()
                if key
                not in {"predicted_y_negative", "expected_y_negative"}
            },
            "predicted_x_positive": row["predicted_y_negative"],
            "expected_x_positive": row["expected_y_negative"],
        }
        for row in combined["rows"]
    ]
    combined["x_positive_true_positives"] = combined.pop("true_positives")

    checks = {
        "both_cross_fit_classifiers_exact": all(
            row["test_correct"] == row["test_cells"] == 20
            and row["test_x_positive_true_positives"] == 1
            and row["test_false_positives"] == 0
            and row["training_margin"] > 0.0
            for row in cross_fit
        ),
        "combined_classifier_exact_positive_margin": (
            combined["correct_cells"] == combined["cells"] == 40
            and combined["x_positive_true_positives"] == 2
            and combined["false_positives"] == 0
            and combined["margin"] > 0.0
        ),
        "home_offset_negative_rejected_by_all_classifiers": (
            all(
                not next(
                    row["predicted_x_positive"]
                    for row in classifier_row["test_rows"]
                    if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
                )
                for classifier_row in cross_fit
            )
            and all(
                not row["predicted_x_positive"]
                for row in combined["rows"]
                if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
            )
        ),
        "saved_context_only_no_simulator_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    status = (
        "PASS_T239_X_POSITIVE_ROUTER_SEPARABILITY"
        if passed
        else "HOLD_T239_X_POSITIVE_ROUTER_SEPARABILITY"
    )
    decision = (
        prereg["decision_rule"]["pass_decision"]
        if passed
        else prereg["decision_rule"]["fail_decision"]
    )
    result_basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t239_x_positive_router_separability.v1"
        ),
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "cross_fit_classifiers": cross_fit,
        "combined_classifier": combined,
        "summary": {
            "cross_fit_correct": [
                f"{row['test_correct']}/{row['test_cells']}"
                for row in cross_fit
            ],
            "cross_fit_training_margins": [
                row["training_margin"] for row in cross_fit
            ],
            "combined_correct": (
                f"{combined['correct_cells']}/{combined['cells']}"
            ),
            "combined_margin": combined["margin"],
        },
        "execution": {
            "context_rows": len(cells),
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
        "# T239 X-positive router separability result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        f"- Cross-fit correctness: "
        f"`{result['summary']['cross_fit_correct']}`\n"
        f"- Combined correctness/margin: "
        f"`{result['summary']['combined_correct']}` / "
        f"`{result['summary']['combined_margin']:.9f}`\n"
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
