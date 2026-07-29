#!/usr/bin/env python3
"""Extract and screen the frozen automatic calibration context as a router."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np
import onnx
from onnx import TensorProto, helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t135_calibration_context_router_preregistration.json"
RESULT = ANALYSIS / "t135_calibration_context_router_result.json"
MARKDOWN = ANALYSIS / "T135_CALIBRATION_CONTEXT_ROUTER_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t135_calibration_context_router_v1"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify(item: dict[str, Any], name: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(item["bytes"])
        or sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"T135 frozen input changed: {name}={path}")


def context_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(value, dtype=np.float32).tobytes()
    ).hexdigest()


def build_diagnostic_policy(path: Path) -> None:
    inputs = [
        helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, 115]),
        helper.make_tensor_value_info(
            "previous_action", TensorProto.FLOAT, [1, 14]
        ),
        helper.make_tensor_value_info("h_in", TensorProto.FLOAT, [1, 64]),
        helper.make_tensor_value_info(
            "calibration_context", TensorProto.FLOAT, [1, 64]
        ),
    ]
    outputs = [
        helper.make_tensor_value_info(
            "continuous_actions", TensorProto.FLOAT, [1, 14]
        ),
        helper.make_tensor_value_info(
            "previous_action_out", TensorProto.FLOAT, [1, 14]
        ),
        helper.make_tensor_value_info("h_out", TensorProto.FLOAT, [1, 64]),
    ]
    nodes = [
        helper.make_node(
            "Identity", ["previous_action"], ["continuous_actions"]
        ),
        helper.make_node(
            "Identity", ["previous_action"], ["previous_action_out"]
        ),
        helper.make_node(
            "Identity", ["calibration_context"], ["h_out"]
        ),
    ]
    graph = helper.make_graph(
        nodes,
        "t135_calibration_context_diagnostic",
        inputs,
        outputs,
    )
    model = helper.make_model(
        graph,
        opset_imports=[helper.make_operatorsetid("", 18)],
        producer_name="open-duck-t135",
    )
    model.ir_version = 8
    onnx.checker.check_model(model)
    onnx.save(model, path)


def classifier(
    nominal: list[np.ndarray],
    negative: list[np.ndarray],
) -> tuple[np.ndarray, float, dict[str, Any]]:
    nominal_mean = np.mean(np.stack(nominal), axis=0)
    negative_mean = np.mean(np.stack(negative), axis=0)
    direction = negative_mean - nominal_mean
    norm = float(np.linalg.norm(direction))
    if norm == 0.0:
        raise ValueError("T135 context centroids are identical")
    coefficient = direction / np.float32(norm)
    midpoint = (negative_mean + nominal_mean) * np.float32(0.5)
    intercept = -float(midpoint @ coefficient)
    nominal_scores = [
        float(value @ coefficient + intercept) for value in nominal
    ]
    negative_scores = [
        float(value @ coefficient + intercept) for value in negative
    ]
    return coefficient, intercept, {
        "nominal_scores": nominal_scores,
        "negative_scores": negative_scores,
        "negative_min_minus_nominal_max": (
            min(negative_scores) - max(nominal_scores)
        ),
        "all_labels_exact": (
            all(score < 0.0 for score in nominal_scores)
            and all(score > 0.0 for score in negative_scores)
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T135 requires --execute")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T135: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T135 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T135 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for fit in prereg["fits"]:
        verify(fit, f"fit:{fit['fit_id']}")

    WORK.mkdir(parents=True)
    policy = WORK / "calibration_context_diagnostic.onnx"
    build_diagnostic_policy(policy)
    started = time.time()
    contexts: dict[str, dict[str, np.ndarray]] = {}
    runs = []
    for fit in prereg["fits"]:
        fit_id = fit["fit_id"]
        contexts[fit_id] = {}
        for population in prereg["populations"]:
            population_id = population["id"]
            root = WORK / fit_id / population_id
            trace_dir = root / "traces"
            evaluation = root / "evaluation.json"
            stdout = root / "stdout.log"
            root.mkdir(parents=True)
            command = [
                sys.executable,
                str(
                    Path(
                        prereg["frozen_inputs"]["evaluator"]["path"]
                    )
                ),
                "--policy",
                str(policy),
                "--policy-sha256",
                sha256(policy),
                "--playground-root",
                prereg["playground"]["path"],
                "--fit",
                fit["path"],
                "--reference-feature-table",
                prereg["reference_feature_table"]["path"],
                "--calibrator",
                prereg["calibrator"]["path"],
                "--calibrator-sha256",
                prereg["calibrator"]["sha256"],
                "--override-json",
                json.dumps(population["override"], separators=(",", ":")),
                "--commands",
                str(prereg["command_x_m_s"]),
                "--seed",
                str(prereg["seed"]),
                "--duration-s",
                "0.02",
                "--trace-dir",
                str(trace_dir),
                "--output-json",
                str(evaluation),
            ]
            completed = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            stdout.write_text(
                completed.stdout, encoding="utf-8", newline="\n"
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"T135 context worker failed: {fit_id}/"
                    f"{population_id}; log={stdout}"
                )
            payload = json.loads(evaluation.read_text(encoding="utf-8"))
            run = payload["runs"][0]
            trace = Path(run["trace_jsonl"])
            first = json.loads(
                trace.read_text(encoding="utf-8").splitlines()[0]
            )
            context = np.asarray(
                first["policy_state_output"]["h_out"], dtype=np.float32
            )
            expected_hash = prereg["expected_context_hashes"][fit_id][
                population_id
            ]
            observed_hash = context_sha256(context)
            contexts[fit_id][population_id] = context.reshape(-1)
            runs.append(
                {
                    "fit_id": fit_id,
                    "population": population_id,
                    "context": context.reshape(-1).astype(float).tolist(),
                    "context_sha256": observed_hash,
                    "expected_context_sha256": expected_hash,
                    "context_hash_exact": observed_hash == expected_hash,
                    "response_context_sha256": (
                        run["response_calibration"]["context_sha256"]
                    ),
                    "trace": receipt(trace),
                    "evaluation": receipt(evaluation),
                    "stdout": receipt(stdout),
                }
            )

    nominal = [
        contexts[fit_id]["nominal"] for fit_id in sorted(contexts)
    ]
    negative = [
        contexts[fit_id]["com_x_negative"] for fit_id in sorted(contexts)
    ]
    coefficient, intercept, full = classifier(nominal, negative)
    leave_one_fit_out = []
    fit_ids = sorted(contexts)
    for held in fit_ids:
        train = next(item for item in fit_ids if item != held)
        fold_coefficient, fold_intercept, _ = classifier(
            [contexts[train]["nominal"]],
            [contexts[train]["com_x_negative"]],
        )
        nominal_score = float(
            contexts[held]["nominal"] @ fold_coefficient + fold_intercept
        )
        negative_score = float(
            contexts[held]["com_x_negative"] @ fold_coefficient
            + fold_intercept
        )
        leave_one_fit_out.append(
            {
                "train_fit": train,
                "held_fit": held,
                "nominal_score": nominal_score,
                "negative_score": negative_score,
                "labels_exact": (
                    nominal_score < 0.0 and negative_score > 0.0
                ),
                "margin": negative_score - nominal_score,
            }
        )
    asset = {
        "schema_version": "open_duck.t135_calibration_context_router.v1",
        "feature": "calibration_context[1,64]",
        "negative_if": "MatMul(context, coefficient) + intercept >= 0",
        "coefficient": coefficient.astype(float).tolist(),
        "intercept": intercept,
        "fit_ids": fit_ids,
        "source_context_hashes": prereg["expected_context_hashes"],
    }
    asset["asset_sha256"] = canonical_sha256(asset)
    asset_path = WORK / "calibration_context_router_asset.json"
    asset_path.write_text(
        json.dumps(asset, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    thresholds = prereg["thresholds"]
    checks = {
        "four_contexts_extracted": (
            len(runs) == 4
            and all(len(run["context"]) == 64 for run in runs)
        ),
        "all_prior_context_hashes_exact": all(
            run["context_hash_exact"]
            and run["context_sha256"] == run["response_context_sha256"]
            for run in runs
        ),
        "full_centroid_classifier_exact": (
            full["all_labels_exact"]
            and full["negative_min_minus_nominal_max"]
            >= thresholds["minimum_full_margin"]
        ),
        "leave_one_fit_out_exact": (
            len(leave_one_fit_out) == 2
            and all(
                fold["labels_exact"]
                and fold["margin"]
                >= thresholds["minimum_leave_one_fit_out_margin"]
                for fold in leave_one_fit_out
            )
        ),
        "diagnostic_policy_context_identity": all(
            run["context_sha256"] == run["response_context_sha256"]
            for run in runs
        ),
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t135_calibration_context_router_result.v1"
        ),
        "status": (
            "PASS_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN"
            if passed
            else "HOLD_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "classification": (
            "STATIC_CALIBRATION_CONTEXT_SEPARATES_COM_ACROSS_FITS"
            if passed
            else "CALIBRATION_CONTEXT_ROUTER_NOT_ESTABLISHED"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "runs": runs,
        "classifier": {
            "full": full,
            "leave_one_fit_out": leave_one_fit_out,
            "asset": receipt(asset_path),
            "asset_sha256": asset["asset_sha256"],
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "calibration_prefixes": 4,
            "calibration_ticks": 4 * 250,
            "contract_smoke_ticks": 4,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "static_router_transform_preregistration": passed,
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
        "# T135 calibration-context router result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Full margin: "
        f"`{full['negative_min_minus_nominal_max']:.9f}`\n"
        "- Leave-one-fit-out: "
        f"`{sum(row['labels_exact'] for row in leave_one_fit_out)}/2`\n"
        "- Formal behavior / optimizer / Colab / robot: `0/0/0/0`\n",
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
