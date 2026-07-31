#!/usr/bin/env python3
"""Freeze T46's sequential R2 conditions 4-20."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T45_RESULT = (
    ANALYSIS / "t45_uniform_final_base_qualification_result.json"
)
T45_PREREG = (
    ANALYSIS
    / "t45_uniform_final_base_qualification_preregistration.json"
)
T41_PREREG = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
RUNNER = ROOT / "tools" / "run_t46_uniform_final_base_r2_remainder.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
BASE_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T6_HELPERS = ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
T8_HELPERS = ROOT / "tools" / "run_t8_state_coherent_handoff.py"
OUTPUT = (
    ANALYSIS
    / "t46_uniform_final_base_r2_remainder_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T46_UNIFORM_FINAL_BASE_R2_REMAINDER_PREREGISTRATION_20260728.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            raise FileExistsError(f"refusing to overwrite T46 prereg: {path}")
    t45_result = json.loads(T45_RESULT.read_text(encoding="utf-8"))
    t45 = json.loads(T45_PREREG.read_text(encoding="utf-8"))
    t41 = json.loads(T41_PREREG.read_text(encoding="utf-8"))
    conditions = t41["conditions"][3:]
    policies = t45["policies"]
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            conditions,
            policies,
            t45["fits"],
            t45["commands_x_m_s"],
            int(t45["seed"]),
        )
    finally:
        sys.path.pop(0)
    repository_inputs = {
        "runner": RUNNER,
        "matrix_helper": MATRIX_HELPER,
        "worker": WORKER,
        "adapter": ADAPTER,
        "base_evaluator": BASE_EVALUATOR,
        "t6_helpers": T6_HELPERS,
        "t8_helpers": T8_HELPERS,
        "t45_result": T45_RESULT,
        "t45_preregistration": T45_PREREG,
        "t41_r2_source": T41_PREREG,
    }
    checks = {
        "t45_all_forty_eight_green": (
            t45_result["status"]
            == "PASS_T45_UNIFORM_FINAL_BASE_QUALIFICATION"
            and t45_result["decision"]
            == "EARN_T45_R2_CONDITIONS_4_TO_20_PREREGISTRATION"
            and t45_result["summary"]["completed_cells"] == 48
            and t45_result["summary"]["green_cells"] == 48
            and t45_result["authority"][
                "later_robustness_preregistration"
            ]
        ),
        "conditions_are_exactly_r2_four_through_twenty": (
            len(conditions) == 17
            and [item["condition_index"] for item in conditions]
            == list(range(4, 21))
            and conditions == t41["conditions"][3:]
        ),
        "policies_are_exact_t45_distinct_endpoints": (
            policies == t45["policies"]
            and policies[0]["sha256"] != policies[1]["sha256"]
        ),
        "matrix_exactly_272_cells": len(plan) == 272,
        "all_policy_fit_and_sensor_assets_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in [
                *policies,
                *t45["fits"],
                t45["calibrator"],
                t45["reference_feature_table"],
            ]
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "behavior_cells_zero": True,
        "training_or_colab_zero": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t46_uniform_final_base_r2_remainder_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T46_UNIFORM_FINAL_BASE_R2_REMAINDER"
            if not failed
            else "HOLD_T46_UNIFORM_FINAL_BASE_R2_REMAINDER_PREREGISTRATION"
        ),
        "question": (
            "Do both T45 uniform-final-base checkpoints pass unchanged "
            "R2 conditions 4-20 under both measured actuator fits and "
            "all four commands?"
        ),
        "prior_qualification": {
            **receipt(T45_RESULT),
            "formal_cells": 48,
            "green_cells": 48,
            "conditions": [1, 2, 3],
        },
        "policies": policies,
        "fits": t45["fits"],
        "calibrator": t45["calibrator"],
        "reference_feature_table": t45["reference_feature_table"],
        "playground": t45["playground"],
        "conditions": conditions,
        "commands_x_m_s": t45["commands_x_m_s"],
        "seed": t45["seed"],
        "support_handoff": t45["support_handoff"],
        "behavior_contract": t45["behavior_contract"],
        "protection_contract": t45["protection_contract"],
        "matrix": {
            "conditions": 17,
            "condition_indices": list(range(4, 21)),
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells_per_condition": 16,
            "maximum_cells": 272,
            "plan_sha256": hashlib.sha256(
                json.dumps(
                    plan,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
            "strictly_sequential_conditions": True,
            "complete_each_16_cell_condition_before_decision": True,
            "stop_after_first_failed_condition": True,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "reuse_prior_condition_evidence": False,
        },
        "decision_rule": {
            "pass": (
                "All 272 cells across conditions 4-20 are green; combined "
                "with T45 this completes the unchanged 320-cell R2 ladder."
            ),
            "pass_decision": (
                "EARN_T46_GATE5_PACKAGE_PREREGISTRATION"
            ),
            "fail_decision": (
                "STOP_T46_AT_FIRST_FAILED_R2_CONDITION_AND_ATTRIBUTE"
            ),
            "no_retry": True,
            "no_checkpoint_selection": True,
        },
        "repository_inputs": {
            name: receipt(path)
            for name, path in repository_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_272_cell_cpu_remainder": not failed,
            "gate5_package_preregistration": False,
            "policy_promotion": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5_hardware": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
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
                "# T46 uniform final-base R2 remainder",
                "",
                f"- Status: `{value['status']}`",
                "- Prior qualification: T45 conditions 1-3, `48/48`",
                "- New conditions: R2 `4-20` in frozen order",
                "- Cells: `16/condition`, `272 maximum`",
                "- Stop after first complete failed condition",
                "- Both checkpoints required; no checkpoint selection",
                "- Training / Colab / Gate 5 / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(
        "contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
