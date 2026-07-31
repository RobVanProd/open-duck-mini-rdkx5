#!/usr/bin/env python3
"""Replace only T156's centroid threshold with the class-gap midpoint."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper

from run_t135_calibration_context_router_screen import classifier
from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    abi,
    canonical_sha256,
    receipt,
    verify,
)
from run_t156_three_way_positive_router_transform import (
    equivalence_contract,
    initializer_map,
)


PREREG = (
    ANALYSIS / "t156b_positive_router_gap_midpoint_preregistration.json"
)
RESULT = ANALYSIS / "t156b_positive_router_gap_midpoint_result.json"
MARKDOWN = (
    ANALYSIS / "T156B_POSITIVE_ROUTER_GAP_MIDPOINT_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t156b_positive_router_gap_midpoint_v1"
)
STEPS = ("1003520", "2007040")


def derive_gap_midpoint(
    nonpositive_rows: list[dict[str, Any]],
    positive_rows: list[dict[str, Any]],
) -> tuple[np.ndarray, float, dict[str, Any]]:
    nonpositive = [
        np.asarray(row["context"], dtype=np.float32)
        for row in nonpositive_rows
    ]
    positive = [
        np.asarray(row["context"], dtype=np.float32)
        for row in positive_rows
    ]
    coefficient, _, _ = classifier(nonpositive, positive)
    nonpositive_raw = [
        float(np.asarray(value @ coefficient, dtype=np.float32))
        for value in nonpositive
    ]
    positive_raw = [
        float(np.asarray(value @ coefficient, dtype=np.float32))
        for value in positive
    ]
    maximum_nonpositive = max(nonpositive_raw)
    minimum_positive = min(positive_raw)
    gap = minimum_positive - maximum_nonpositive
    boundary = np.float32(
        (maximum_nonpositive + minimum_positive) * 0.5
    )
    intercept = float(np.float32(-boundary))
    nonpositive_scores = [
        float(np.float32(value + intercept))
        for value in nonpositive_raw
    ]
    positive_scores = [
        float(np.float32(value + intercept))
        for value in positive_raw
    ]
    return coefficient, intercept, {
        "maximum_nonpositive_raw": maximum_nonpositive,
        "minimum_positive_raw": minimum_positive,
        "strict_class_gap": gap,
        "boundary": float(boundary),
        "intercept": intercept,
        "nonpositive_scores": nonpositive_scores,
        "positive_scores": positive_scores,
        "all_labels_exact": (
            gap > 0.0
            and all(score < 0.0 for score in nonpositive_scores)
            and all(score > 0.0 for score in positive_scores)
        ),
    }


def leave_one_fit_out(
    nonpositive_rows: list[dict[str, Any]],
    positive_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fit_ids = sorted({row["fit_id"] for row in positive_rows})
    folds = []
    for held in fit_ids:
        train_nonpositive = [
            row for row in nonpositive_rows if row["fit_id"] != held
        ]
        train_positive = [
            row for row in positive_rows if row["fit_id"] != held
        ]
        coefficient, intercept, training = derive_gap_midpoint(
            train_nonpositive,
            train_positive,
        )
        scores = []
        for row in [
            *[
                item
                for item in nonpositive_rows
                if item["fit_id"] == held
            ],
            *[
                item
                for item in positive_rows
                if item["fit_id"] == held
            ],
        ]:
            score = float(
                np.float32(
                    np.asarray(row["context"], dtype=np.float32)
                    @ coefficient
                    + intercept
                )
            )
            expected_positive = row["population"] == "com_x_positive"
            scores.append(
                {
                    "population": row["population"],
                    "score": score,
                    "expected_positive": expected_positive,
                    "label_exact": (
                        score > 0.0
                        if expected_positive
                        else score < 0.0
                    ),
                }
            )
        folds.append(
            {
                "train_fit": next(
                    fit_id for fit_id in fit_ids if fit_id != held
                ),
                "held_fit": held,
                "training_rule": training,
                "scores": scores,
                "labels_exact": all(
                    item["label_exact"] for item in scores
                ),
            }
        )
    return folds


def replace_intercept(
    source: Path,
    destination: Path,
    coefficient: np.ndarray,
    intercept: float,
) -> dict[str, Any]:
    before = onnx.load(source)
    model = copy.deepcopy(before)
    old_initializers = {
        item.name: item.SerializeToString()
        for item in before.graph.initializer
    }
    initializers = initializer_map(model)
    existing_coefficient = numpy_helper.to_array(
        initializers["positive_router_coefficient"]
    )
    coefficient_exact = np.array_equal(
        existing_coefficient,
        coefficient.reshape(64, 1).astype(np.float32),
    )
    if not coefficient_exact:
        raise RuntimeError("T156B T156 coefficient changed")
    index = next(
        i
        for i, item in enumerate(model.graph.initializer)
        if item.name == "positive_router_intercept"
    )
    old_intercept = numpy_helper.to_array(
        model.graph.initializer[index]
    ).copy()
    replacement = numpy_helper.from_array(
        np.asarray([intercept], dtype=np.float32),
        "positive_router_intercept",
    )
    del model.graph.initializer[index]
    model.graph.initializer.insert(index, replacement)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    after = onnx.load(destination)
    new_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    changed = sorted(
        name
        for name, value in old_initializers.items()
        if new_initializers.get(name) != value
    )
    return {
        "source": receipt(source),
        "transformed": receipt(destination),
        "coefficient_byte_exact": coefficient_exact,
        "old_intercept": old_intercept.astype(float).tolist(),
        "new_intercept": [float(np.float32(intercept))],
        "only_intercept_initializer_changed": (
            changed == ["positive_router_intercept"]
        ),
        "all_nodes_byte_exact": all(
            left.SerializeToString() == right.SerializeToString()
            for left, right in zip(
                before.graph.node,
                after.graph.node,
                strict=True,
            )
        ),
        "abi_exact": abi(before) == abi(after),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T156B requires --execute")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T156B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T156B execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T156B_POSITIVE_ROUTER_GAP_MIDPOINT"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T156B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for group in (
        "source_graphs",
        "positive_references",
    ):
        for step, item in prereg[group].items():
            verify(item, f"{group}:{step}")

    t135b = json.loads(
        Path(prereg["frozen_inputs"]["t135b_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t156 = json.loads(
        Path(prereg["frozen_inputs"]["t156_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    nonpositive_rows = t135b["runs"]
    positive_rows = t156["positive_contexts"]
    coefficient, intercept, classifier_result = derive_gap_midpoint(
        nonpositive_rows,
        positive_rows,
    )
    folds = leave_one_fit_out(nonpositive_rows, positive_rows)
    contexts = [*nonpositive_rows, *positive_rows]
    WORK.mkdir(parents=True)
    graphs = {}
    contracts = {}
    started = time.time()
    for step in STEPS:
        source = Path(prereg["source_graphs"][step]["path"])
        reference = Path(prereg["positive_references"][step]["path"])
        destination = WORK / step / "three_way_positive_router.onnx"
        graphs[step] = replace_intercept(
            source,
            destination,
            coefficient,
            intercept,
        )
        contracts[step] = equivalence_contract(
            Path(t156["graphs"][step]["source"]["path"]),
            reference,
            destination,
            contexts,
        )
    checks = {
        "strict_full_class_gap": (
            classifier_result["strict_class_gap"] > 0.0
        ),
        "full_gap_midpoint_labels_exact": classifier_result[
            "all_labels_exact"
        ],
        "leave_one_fit_out_gap_midpoint_labels_exact": all(
            fold["labels_exact"] for fold in folds
        ),
        "only_intercept_initializer_changed": all(
            row["only_intercept_initializer_changed"]
            and row["coefficient_byte_exact"]
            and row["all_nodes_byte_exact"]
            and row["abi_exact"]
            for row in graphs.values()
        ),
        "all_selected_source_outputs_bit_exact": all(
            row["all_selected_source_outputs_bit_exact"]
            for row in contracts.values()
        ),
        "all_feedback_finite_cpu": all(
            row["all_outputs_finite"]
            and row["all_action_feedback_bit_exact"]
            and row["cpu_only"]
            for row in contracts.values()
        ),
        "both_checkpoints_transformed": set(graphs) == set(STEPS),
        "formal_behavior_cells_zero": True,
        "calibration_optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t156b_positive_router_gap_midpoint_result.v1"
        ),
        "status": (
            "PASS_T156B_POSITIVE_ROUTER_GAP_MIDPOINT"
            if passed
            else "HOLD_T156B_POSITIVE_ROUTER_GAP_MIDPOINT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "classifier": {
            **classifier_result,
            "leave_one_fit_out": folds,
        },
        "graphs": graphs,
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "calibration_prefixes": 0,
            "graphs_transformed": len(graphs),
            "cpu_equivalence_samples": sum(
                row["samples"] for row in contracts.values()
            ),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "positive_endpoint_preregistration": passed,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T156B positive-router gap midpoint\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Frozen class gap: "
        f"`{classifier_result['strict_class_gap']:.9f}`\n"
        "- Changed graph field: positive-router intercept only\n"
        "- Behavior / calibration / optimizer / Colab / robot: "
        "`0/0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
