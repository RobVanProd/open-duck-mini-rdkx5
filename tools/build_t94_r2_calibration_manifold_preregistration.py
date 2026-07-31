#!/usr/bin/env python3
"""Freeze T94's automatic-calibration manifold screen over all R2 axes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t94_r2_calibration_manifold_preregistration_v3.json"
MARKDOWN = (
    ANALYSIS / "T94_R2_CALIBRATION_MANIFOLD_PREREGISTRATION_V3_20260728.md"
)
T7_PREREG = ANALYSIS / "t7_universal_response_support_preregistration.json"
T7_RESULT = ANALYSIS / "t7_universal_response_support_result.json"
R2 = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t94_r2_calibration_manifold.py"
T7_RUNNER = ROOT / "tools" / "run_t7_universal_response_support.py"
TEST = ROOT / "tests" / "test_t94_r2_calibration_manifold.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T94 prereg: {path}")
    t7_prereg = json.loads(T7_PREREG.read_text(encoding="utf-8"))
    t7_result = json.loads(T7_RESULT.read_text(encoding="utf-8"))
    r2 = json.loads(R2.read_text(encoding="utf-8"))
    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "t7_runner": T7_RUNNER,
        "test": TEST,
        "t7_preregistration": T7_PREREG,
        "t7_result": T7_RESULT,
        "r2_basis": R2,
        "evaluator": Path(t7_prereg["repository_inputs"]["evaluator"]["path"]),
        "closed_loop": Path(
            t7_prereg["repository_inputs"]["closed_loop"]["path"]
        ),
        "fit_p30": Path(t7_prereg["repository_inputs"]["fit_p30"]["path"]),
        "fit_p31_34": Path(
            t7_prereg["repository_inputs"]["fit_p31_34"]["path"]
        ),
        "reference_features": Path(
            t7_prereg["repository_inputs"]["reference_features"]["path"]
        ),
    }
    conditions = r2["conditions"]
    checks = {
        "t7_response_signal_is_repeatable_and_separable": (
            t7_result["status"] == "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT"
            and t7_result["global_checks"][
                "all_repeat_contexts_bit_exact"
            ]
            and t7_result["global_checks"][
                "all_signed_endpoint_separations_pass"
            ]
        ),
        "r2_inventory_exact": (
            len(conditions) == 20
            and [item["condition_index"] for item in conditions]
            == list(range(1, 21))
            and conditions[6]["id"] == "TORSO_COM_X_NEG"
            and conditions[7]["id"] == "TORSO_COM_X_POS"
        ),
        "exact_t7_calibrator_and_playground_reused": (
            Path(t7_prereg["frozen_policy"]["path"]).is_file()
            and sha256(Path(t7_prereg["frozen_policy"]["path"]))
            == t7_prereg["frozen_policy"]["sha256"]
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "calibration_only_no_locomotion_policy_selection": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t94_r2_calibration_manifold_preregistration.v3"
        ),
        "status": (
            "PREREGISTERED_T94_R2_CALIBRATION_MANIFOLD_V3"
            if not failed
            else "HOLD_T94_R2_CALIBRATION_MANIFOLD_PREREGISTRATION"
        ),
        "question": (
            "Does the already frozen 250-tick automatic calibration state "
            "repeatably identify the negative-X COM condition and actuator fit "
            "across every one-axis R2 configuration, without manual geometry?"
        ),
        "prior_attempt_invalidations": [
            receipt(
                ANALYSIS
                / "t94_r2_calibration_manifold_attempt1_invalidation.json"
            ),
            receipt(
                ANALYSIS
                / "t94_r2_calibration_manifold_attempt2_invalidation.json"
            ),
        ],
        "repository_inputs": {
            name: receipt(path) for name, path in repository_inputs.items()
        },
        "playground": t7_prereg["playground"],
        "frozen_policy": t7_prereg["frozen_policy"],
        "conditions": conditions,
        "fits": ["p30", "p31_34"],
        "matrix": {
            "conditions": 20,
            "fits": 2,
            "repeats": 1,
            "cells": 40,
            "command_x_m_s": 0.0,
            "seed": 167931544,
            "frequency_hz": 50,
            "duration_ticks": 250,
            "response_context_tick": 249,
            "partial_results_selection_weight": 0,
            "no_early_stop": True,
        },
        "prototype_contract": {
            "source": receipt(T7_RESULT),
            "configurations": [
                "NOMINAL",
                "TORSO_COM_X_NEG",
                "TORSO_COM_X_POS",
            ],
            "fits": ["p30", "p31_34"],
            "repeat": 0,
            "distance": "float64 Euclidean distance over the frozen 64-D context",
            "fit_classifier": (
                "nearest of the six frozen T7 configuration/fit prototypes; "
                "the prototype fit label is the prediction"
            ),
            "negative_com_classifier": (
                "nearest of the three same-predicted-fit T7 prototypes; "
                "negative only when TORSO_COM_X_NEG is nearest"
            ),
            "no_fitted_parameters_or_threshold_sweep": True,
        },
        "pass_contract": {
            "all_40_calibration_cells_complete_250_ticks": True,
            "all_contexts_finite": True,
            "universal_action_and_recurrent_chains_exact": True,
            "calibration_safety_matches_t7_thresholds": (
                t7_prereg["behavior_contract"]
            ),
            "six_nominal_and_com_anchor_contexts_bit_exact_to_t7": True,
            "fit_classification_accuracy": 1.0,
            "negative_com_true_positives": 2,
            "negative_com_false_positives": 0,
            "strict_positive_nearest_prototype_margin": True,
        },
        "decision_rule": {
            "pass": {
                "classification": "R2_CALIBRATION_MANIFOLD_ROUTABLE",
                "decision": (
                    "EARN_CALIBRATION_ROUTED_FIXED_EXPERT_CPU_"
                    "PREREGISTRATION_ONLY"
                ),
            },
            "fail": {
                "classification": "R2_CALIBRATION_MANIFOLD_NOT_ROUTABLE",
                "decision": "CLOSE_CALIBRATION_ROUTED_EXPERT_MECHANISM",
            },
            "training_selection_weight": 0,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "simulator_calibration_ticks": 0,
            "locomotion_policy_ticks": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "offline_calibration_screen": not failed,
            "locomotion_behavior": False,
            "hosted_training": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T94 R2 calibration-manifold preregistration v3",
                "",
                f"- Status: `{value['status']}`",
                f"- Failed checks: `{failed}`",
                "- Matrix: 20 one-axis R2 conditions × 2 actuator fits",
                "- Frozen universal calibrator: 250 ticks; no locomotion policy",
                "- Training / Colab / RDK / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"preregistered_contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
