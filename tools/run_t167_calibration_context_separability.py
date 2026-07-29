#!/usr/bin/env python3
"""Run the frozen T167 current-handoff calibration-context audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

import numpy as np  # noqa: E402

from run_t136_static_calibration_router_transform import (  # noqa: E402
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)
import t167_response_context_eval_adapter as adapter  # noqa: E402


PREREG = (
    ANALYSIS / "t167_calibration_context_separability_preregistration.json"
)
RESULT = ANALYSIS / "t167_calibration_context_separability_result.json"
MARKDOWN = (
    ANALYSIS / "T167_CALIBRATION_CONTEXT_SEPARABILITY_RESULT_20260729.md"
)


def array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(value, dtype=np.float32).tobytes()
    ).hexdigest()


def expected_t165_hashes(
    result: dict[str, Any],
) -> dict[tuple[str, str], str]:
    values: dict[tuple[str, str], str] = {}
    for block in result["blocks"]:
        coordinate = (block["condition_id"], block["fit_id"])
        observed = {
            cell["handoff"]["context_sha256"]
            for cell in block["result"]["cells"]
        }
        if len(observed) != 1:
            raise RuntimeError(f"T167 T165 context changed across commands: {coordinate}")
        value = next(iter(observed))
        previous = values.setdefault(coordinate, value)
        if previous != value:
            raise RuntimeError(
                f"T167 T165 context changed across checkpoints: {coordinate}"
            )
    return values


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
        raise RuntimeError("T167 zero/invalid per-fit direction")
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
        predicted = score >= threshold
        expected = row["condition_id"] == positive
        rows.append(
            {
                "condition_id": row["condition_id"],
                "score": score,
                "predicted_y_negative": predicted,
                "expected_y_negative": expected,
                "correct": predicted == expected,
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
        "test_y_negative_true_positives": sum(
            row["predicted_y_negative"] and row["expected_y_negative"]
            for row in rows
        ),
        "test_false_positives": sum(
            row["predicted_y_negative"] and not row["expected_y_negative"]
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
    differences = []
    for rows in by_fit.values():
        difference = np.asarray(
            rows[positive]["context"], dtype=np.float64
        ) - np.asarray(rows[control]["context"], dtype=np.float64)
        difference /= np.linalg.norm(difference)
        differences.append(difference)
    direction = np.mean(differences, axis=0)
    norm = float(np.linalg.norm(direction))
    if not np.isfinite(norm) or norm <= 0.0:
        raise RuntimeError("T167 zero/invalid combined direction")
    direction /= norm
    rows = []
    for row in cells:
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
                "expected_y_negative": row["condition_id"] == positive,
            }
        )
    minimum_positive = min(
        row["score"] for row in rows if row["expected_y_negative"]
    )
    maximum_negative = max(
        row["score"] for row in rows if not row["expected_y_negative"]
    )
    threshold = 0.5 * (minimum_positive + maximum_negative)
    for row in rows:
        row["predicted_y_negative"] = row["score"] >= threshold
        row["correct"] = (
            row["predicted_y_negative"] == row["expected_y_negative"]
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
            row["predicted_y_negative"] and row["expected_y_negative"]
            for row in rows
        ),
        "false_positives": sum(
            row["predicted_y_negative"] and not row["expected_y_negative"]
            for row in rows
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T167: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T167 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        name: value
        for name, value in prereg.items()
        if name != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T167_CALIBRATION_CONTEXT_SEPARABILITY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T167 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    if adapter.contract() != prereg["adapter_contract"]:
        raise RuntimeError("T167 adapter contract changed")

    t165 = json.loads(
        Path(prereg["frozen_inputs"]["t165_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    expected_hashes = expected_t165_hashes(t165)
    population = prereg["population"]
    policy = Path(population["policy"]["path"])
    calibrator = Path(population["calibrator"]["path"])
    playground = Path(population["playground"]["path"])
    reference = Path(population["reference_feature_table"]["path"])
    module = adapter.load_module()
    cells = []
    started = time.time()
    for condition in population["conditions"]:
        for fit_item in population["fits"]:
            fit = json.loads(
                Path(fit_item["path"]).read_text(encoding="utf-8")
            )
            result = module.run_closed_loop_sim(
                module.ClosedLoopConfig(
                    policy_path=policy,
                    fit=fit,
                    playground_root=playground,
                    command_x=0.0,
                    duration_s=0.02,
                    bridge_mode="fitted",
                    expected_observation_dim=115,
                    expected_action_dim=14,
                    task="flat_terrain_backlash",
                    seed=int(population["seed"]),
                    eval_role="diagnostic",
                    reset_mode="home-support",
                    policy_obs_input_name="obs",
                    policy_action_output_name="continuous_actions",
                    policy_state_input_names=("h_in", "previous_action"),
                    policy_state_output_names=("h_out", "previous_action_out"),
                    policy_context_input_name="calibration_context",
                    policy_graph_authoritative_output=True,
                    response_calibrator_path=calibrator,
                    response_calibrator_sha256=population["calibrator"][
                        "sha256"
                    ],
                    response_calibration_ticks=250,
                    response_home_return_ticks=0,
                    response_preserve_handoff_state=True,
                    policy_applied_target_observation=True,
                    eval_dynamics_override=condition["override"],
                    reference_feature_table_path=reference,
                    reference_start_phase=0,
                )
            )
            mode = (result.get("modes") or {}).get("fitted") or {}
            audit = mode.get("response_calibration") or {}
            context = np.asarray(audit.get("context_value"), dtype=np.float32)
            if context.shape != (1, 64) or not np.all(np.isfinite(context)):
                raise RuntimeError(
                    f"T167 invalid context: {condition['id']}:{fit_item['fit_id']}"
                )
            context_hash = array_sha256(context)
            if context_hash != audit.get("context_sha256"):
                raise RuntimeError("T167 context output/hash mismatch")
            cells.append(
                {
                    "condition_index": condition["condition_index"],
                    "condition_id": condition["id"],
                    "override": condition["override"],
                    "fit_id": fit_item["fit_id"],
                    "context": context.reshape(64).astype(float).tolist(),
                    "context_sha256": context_hash,
                    "t165_expected_sha256": expected_hashes.get(
                        (condition["id"], fit_item["fit_id"])
                    ),
                    "t165_hash_matches": (
                        expected_hashes.get(
                            (condition["id"], fit_item["fit_id"])
                        )
                        in (None, context_hash)
                    ),
                    "response_handoff_enabled": bool(audit.get("enabled")),
                    "calibration_ticks": audit.get("calibration_ticks"),
                    "home_return_ticks": audit.get("home_return_ticks"),
                    "diagnostic_result_status": result.get("status"),
                }
            )
            print(
                json.dumps(
                    {
                        "condition": condition["id"],
                        "fit": fit_item["fit_id"],
                        "context_sha256": context_hash,
                        "completed": len(cells),
                        "total": 40,
                    }
                ),
                flush=True,
            )

    positive = prereg["classifier"]["positive_condition"]
    control = prereg["classifier"]["control_condition"]
    fits = [item["fit_id"] for item in population["fits"]]
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
    combined = combined_classifier(cells, positive=positive, control=control)

    router = json.loads(
        Path(prereg["frozen_inputs"]["router_asset"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    old_coefficient = np.asarray(router["coefficient"], dtype=np.float64)
    old_intercept = float(router["intercept"])
    existing_router = []
    for row in cells:
        score = float(
            np.dot(np.asarray(row["context"], dtype=np.float64), old_coefficient)
            + old_intercept
        )
        existing_router.append(
            {
                "condition_id": row["condition_id"],
                "fit_id": row["fit_id"],
                "score": score,
                "negative_x_path": score >= 0.0,
            }
        )

    prior_cells = [row for row in cells if row["condition_index"] <= 9]
    checks = {
        "forty_finite_contexts": (
            len(cells) == 40
            and all(
                len(row["context"]) == 64
                and all(np.isfinite(row["context"]))
                for row in cells
            )
        ),
        "all_eighteen_prior_hashes_match": (
            len(prior_cells) == 18
            and all(row["t165_hash_matches"] for row in prior_cells)
        ),
        "both_cross_fit_classifiers_exact": all(
            row["test_correct"] == row["test_cells"] == 20
            and row["test_y_negative_true_positives"] == 1
            and row["test_false_positives"] == 0
            and row["training_margin"] > 0.0
            for row in cross_fit
        ),
        "combined_classifier_exact_positive_margin": (
            combined["correct_cells"] == combined["cells"] == 40
            and combined["true_positives"] == 2
            and combined["false_positives"] == 0
            and combined["margin"] > 0.0
        ),
        "diagnostic_only_no_formal_behavior_optimizer_colab_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    summary = {
        "contexts": len(cells),
        "prior_hash_matches": sum(
            row["t165_hash_matches"] for row in prior_cells
        ),
        "prior_hash_cells": len(prior_cells),
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
        "existing_router_y_negative_x_path_count": sum(
            row["negative_x_path"]
            for row in existing_router
            if row["condition_id"] == positive
        ),
        "existing_router_false_x_path_count": sum(
            row["negative_x_path"]
            for row in existing_router
            if row["condition_id"] != "TORSO_COM_X_NEG"
        ),
        "wall_seconds": time.time() - started,
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t167_calibration_context_separability_result.v1"
        ),
        "status": (
            "PASS_T167_CALIBRATION_CONTEXT_SEPARABILITY"
            if passed
            else "HOLD_T167_CALIBRATION_CONTEXT_SEPARABILITY"
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
        "cells": cells,
        "cross_fit_classifiers": cross_fit,
        "combined_classifier": combined,
        "existing_router": existing_router,
        "execution": {
            "calibration_prefixes": len(cells),
            "calibration_ticks": len(cells) * 250,
            "diagnostic_locomotion_ticks": len(cells),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": prereg["authority"],
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T167 calibration-context separability result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Prior T165 hashes: `{summary['prior_hash_matches']}/"
        f"{summary['prior_hash_cells']}`\n"
        f"- Cross-fit correctness: `{summary['cross_fit_correct']}`\n"
        f"- Combined correctness/margin: `{summary['combined_correct']}` / "
        f"`{summary['combined_margin']:.9f}`\n"
        f"- Existing X-negative router selects Y-negative: "
        f"`{summary['existing_router_y_negative_x_path_count']}/2`\n"
        "- Formal behavior / optimizer / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(value["decision"])
    print(json.dumps(summary, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
