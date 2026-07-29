#!/usr/bin/env python3
"""Recover T135 after its first exact calibration prefix completed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np

from run_t135_calibration_context_router_screen import (
    ANALYSIS,
    WORK,
    build_diagnostic_policy,
    canonical_sha256,
    classifier,
    context_sha256,
    receipt,
    sha256,
    verify,
)


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_"
    "preregistration.json"
)
RESULT = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
MARKDOWN = (
    ANALYSIS
    / "T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY_"
    "RESULT_20260729.md"
)


def load_context(trace: Path) -> tuple[np.ndarray, str]:
    first = json.loads(trace.read_text(encoding="utf-8").splitlines()[0])
    context = np.asarray(
        first["policy_state_output"]["h_out"], dtype=np.float32
    )
    trace_hash = first["policy_calibration_context_sha256"]
    if context_sha256(context) != trace_hash:
        raise RuntimeError(f"context/trace hash mismatch: {trace}")
    return context.reshape(-1), trace_hash


def run_prefix(
    prereg: dict[str, Any],
    policy: Path,
    fit: dict[str, Any],
    population: dict[str, Any],
) -> dict[str, Any]:
    fit_id = fit["fit_id"]
    population_id = population["id"]
    root = WORK / fit_id / population_id
    trace_dir = root / "traces"
    evaluation = root / "evaluation.json"
    stdout = root / "stdout.log"
    if root.exists():
        raise FileExistsError(f"refusing to overwrite recovery prefix: {root}")
    root.mkdir(parents=True)
    command = [
        sys.executable,
        prereg["frozen_inputs"]["evaluator"]["path"],
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
    stdout.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode != 0:
        raise RuntimeError(
            f"T135B worker failed: {fit_id}/{population_id}; log={stdout}"
        )
    payload = json.loads(evaluation.read_text(encoding="utf-8"))
    run = payload["runs"][0]
    trace = Path(run["trace_jsonl"])
    context, trace_hash = load_context(trace)
    return {
        "fit_id": fit_id,
        "population": population_id,
        "context": context.astype(float).tolist(),
        "context_sha256": trace_hash,
        "expected_context_sha256": prereg["expected_context_hashes"][
            fit_id
        ][population_id],
        "context_hash_exact": (
            trace_hash
            == prereg["expected_context_hashes"][fit_id][population_id]
        ),
        "trace": receipt(trace),
        "evaluation": receipt(evaluation),
        "stdout": receipt(stdout),
        "cached_from_interrupted_t135": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T135B requires --execute")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T135B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T135B execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "recovery_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T135B_INTERRUPTED_CALIBRATION_CONTEXT_"
        "ROUTER_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis) != prereg["recovery_contract_sha256"]
    ):
        raise RuntimeError("T135B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for fit in prereg["fits"]:
        verify(fit, f"fit:{fit['fit_id']}")

    policy = Path(prereg["cached_prefix"]["diagnostic_policy"]["path"])
    cached_trace = Path(prereg["cached_prefix"]["trace"]["path"])
    cached_context, cached_hash = load_context(cached_trace)
    cached = {
        "fit_id": "p30",
        "population": "nominal",
        "context": cached_context.astype(float).tolist(),
        "context_sha256": cached_hash,
        "expected_context_sha256": prereg["expected_context_hashes"]["p30"][
            "nominal"
        ],
        "context_hash_exact": (
            cached_hash
            == prereg["expected_context_hashes"]["p30"]["nominal"]
        ),
        "trace": prereg["cached_prefix"]["trace"],
        "evaluation": prereg["cached_prefix"]["evaluation"],
        "stdout": prereg["cached_prefix"]["stdout"],
        "cached_from_interrupted_t135": True,
    }
    runs = [cached]
    contexts: dict[str, dict[str, np.ndarray]] = {
        "p30": {"nominal": cached_context},
        "p31_34": {},
    }
    started = time.time()
    populations = {item["id"]: item for item in prereg["populations"]}
    fits = {item["fit_id"]: item for item in prereg["fits"]}
    for item in prereg["remaining_prefixes"]:
        run = run_prefix(
            prereg,
            policy,
            fits[item["fit_id"]],
            populations[item["population"]],
        )
        runs.append(run)
        contexts[item["fit_id"]][item["population"]] = np.asarray(
            run["context"], dtype=np.float32
        )

    fit_ids = sorted(contexts)
    nominal = [contexts[fit_id]["nominal"] for fit_id in fit_ids]
    negative = [
        contexts[fit_id]["com_x_negative"] for fit_id in fit_ids
    ]
    coefficient, intercept, full = classifier(nominal, negative)
    leave_one_fit_out = []
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
        "one_cached_three_new_prefixes": (
            len(runs) == 4
            and sum(run["cached_from_interrupted_t135"] for run in runs)
            == 1
        ),
        "four_contexts_exact": all(
            run["context_hash_exact"] and len(run["context"]) == 64
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
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t135b_interrupted_calibration_context_router_"
            "recovery_result.v1"
        ),
        "status": (
            "PASS_T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY"
            if passed
            else "HOLD_T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_"
            "RECOVERY"
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
        "recovery_contract_sha256": prereg["recovery_contract_sha256"],
        "source_t135_contract_sha256": prereg[
            "source_t135_contract_sha256"
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
            "cached_calibration_prefixes": 1,
            "new_calibration_prefixes": 3,
            "total_calibration_ticks": 4 * 250,
            "total_contract_smoke_ticks": 4,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "recovery_wall_seconds": time.time() - started,
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
        "# T135B interrupted calibration-context router recovery\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Full margin: "
        f"`{full['negative_min_minus_nominal_max']:.9f}`\n"
        "- Leave-one-fit-out: "
        f"`{sum(row['labels_exact'] for row in leave_one_fit_out)}/2`\n"
        "- Cached/new prefixes: `1/3`\n"
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
