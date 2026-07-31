#!/usr/bin/env python3
"""Freeze the T167 current-handoff calibration-context separability audit."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)
from t167_response_context_eval_adapter import contract as adapter_contract


T165_PREREG = ANALYSIS / "t165_composed_full_r2_preregistration.json"
T165_RESULT = ANALYSIS / "t165_composed_full_r2_result.json"
T166_RESULT = ANALYSIS / "t166_lateral_persistence_autopsy_result.json"
T143_PREREG = ANALYSIS / "t143_conditional_forward_path_preregistration.json"
OUTPUT = (
    ANALYSIS / "t167_calibration_context_separability_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T167_CALIBRATION_CONTEXT_SEPARABILITY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
ADAPTER = ROOT / "tools" / "t167_response_context_eval_adapter.py"
RUNNER = ROOT / "tools" / "run_t167_calibration_context_separability.py"
TEST = ROOT / "tests" / "test_t167_calibration_context_separability.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T167: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T167 preregistration requires clean worktree")
    t165_prereg = json.loads(T165_PREREG.read_text(encoding="utf-8"))
    t165_result = json.loads(T165_RESULT.read_text(encoding="utf-8"))
    t166 = json.loads(T166_RESULT.read_text(encoding="utf-8"))
    t143 = json.loads(T143_PREREG.read_text(encoding="utf-8"))
    router_asset = Path(t143["frozen_inputs"]["router_asset"]["path"])
    frozen = {
        "adapter": ADAPTER,
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t143_preregistration": T143_PREREG,
        "t165_preregistration": T165_PREREG,
        "t165_result": T165_RESULT,
        "t166_result": T166_RESULT,
        "router_asset": router_asset,
    }
    adapter = adapter_contract()
    checks = {
        "t165_stopped_at_y_negative": (
            t165_result["summary"]["first_failed_condition"]
            == "TORSO_COM_Y_NEG"
        ),
        "t166_closed_simple_lateral_overlay": (
            t166["status"] == "HOLD_T166_LATERAL_PERSISTENCE_AUTOPSY"
            and t166["decision"] == "HOLD_FOR_DIFFERENT_PERSISTENCE_MECHANISM"
        ),
        "twenty_conditions_two_fits": (
            len(t165_prereg["conditions"]) == 20
            and len(t165_prereg["fits"]) == 2
        ),
        "adapter_is_diagnostic_only": (
            adapter["response_context_field_count"] == 1
        ),
        "frozen_inputs_present": all(path.is_file() for path in frozen.values()),
        "no_behavior_training_colab_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T167 preregistration checks failed: {failed}")
    value = {
        "schema_version": (
            "open_duck.t167_calibration_context_separability_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T167_CALIBRATION_CONTEXT_SEPARABILITY"
        ),
        "question": (
            "Does the exact state-coherent 250-tick calibration context "
            "contain a fit-stable signature for TORSO_COM_Y_NEG even though "
            "the current router was trained only for TORSO_COM_X_NEG?"
        ),
        "population": {
            "conditions": t165_prereg["conditions"],
            "fits": t165_prereg["fits"],
            "cells": 40,
            "command_x_m_s": 0.0,
            "calibration_ticks": 250,
            "home_return_ticks": 0,
            "diagnostic_locomotion_ticks": 1,
            "policy": t165_prereg["policies"][0],
            "calibrator": t165_prereg["calibrator"],
            "reference_feature_table": t165_prereg[
                "reference_feature_table"
            ],
            "playground": t165_prereg["playground"],
            "seed": t165_prereg["seed"],
        },
        "classifier": {
            "positive_condition": "TORSO_COM_Y_NEG",
            "control_condition": "ARMATURE_LO",
            "feature": "calibration_context[1,64]",
            "per_fit_direction": (
                "unit(TORSO_COM_Y_NEG - ARMATURE_LO) on the training fit"
            ),
            "per_fit_threshold": (
                "midpoint of training-fit positive score and maximum "
                "training-fit non-Y-negative score"
            ),
            "cross_fit_test": (
                "train on p30, classify all 20 p31_34 contexts; train on "
                "p31_34, classify all 20 p30 contexts"
            ),
            "combined_direction": (
                "unit(mean of the two per-fit Y-negative-minus-control "
                "difference vectors)"
            ),
            "combined_threshold": (
                "midpoint of minimum Y-negative score and maximum "
                "non-Y-negative score across all 40 cells"
            ),
            "no_scalar_search": True,
        },
        "decision_rule": {
            "dedicated_expert_contract_if": [
                "all 40 contexts are finite float32 [1,64]",
                "all 18 already-observed condition-1-through-9 context hashes match T165",
                "both cross-fit classifiers identify exactly one Y-negative context and zero false positives",
                "the combined classifier identifies both Y-negative contexts and zero false positives with positive margin",
            ],
            "pass_decision": (
                "EARN_T168_DEDICATED_Y_NEGATIVE_EXPERT_"
                "CPU_CONTRACT_PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_STATIC_CALIBRATION_ROUTING_FOR_Y_NEGATIVE"
            ),
        },
        "adapter_contract": adapter,
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "calibration_prefixes": 0,
            "diagnostic_locomotion_ticks": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "forty_cpu_calibration_prefixes": True,
            "forty_diagnostic_locomotion_ticks": True,
            "formal_behavior_evaluation": False,
            "expert_cpu_contract_preregistration": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T167 calibration-context separability preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Population: 20 R2 conditions × two measured actuator fits\n"
        "- Execution: 250 unscored calibration ticks plus one diagnostic "
        "locomotion tick per cell\n"
        "- Decision: cross-fit linear separability, no scalar search\n"
        "- Formal behavior / optimizer / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
