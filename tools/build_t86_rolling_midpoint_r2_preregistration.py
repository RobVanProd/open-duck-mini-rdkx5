#!/usr/bin/env python3
"""Freeze T86's full sequential R2 matrix for the T84 rolling pair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T85_RESULT = ANALYSIS / "t85_rolling_midpoint_nominal_result.json"
T85_PREREG = (
    ANALYSIS / "t85_rolling_midpoint_nominal_preregistration.json"
)
R2_BASIS = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
T27_CONTRACT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
R2_SOURCE = ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json"
RUNNER = ROOT / "tools" / "run_t86_rolling_midpoint_r2.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t86_rolling_midpoint_r2.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
BASE_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T6_HELPERS = ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
T8_HELPERS = ROOT / "tools" / "run_t8_state_coherent_handoff.py"
OUTPUT = ANALYSIS / "t86_rolling_midpoint_r2_preregistration.json"
MARKDOWN = ANALYSIS / "T86_ROLLING_MIDPOINT_R2_PREREGISTRATION_20260728.md"


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
            raise FileExistsError(f"refusing to overwrite T86 prereg: {path}")

    t85_result = json.loads(T85_RESULT.read_text(encoding="utf-8"))
    t85_prereg = json.loads(T85_PREREG.read_text(encoding="utf-8"))
    basis = json.loads(R2_BASIS.read_text(encoding="utf-8"))
    contract = json.loads(T27_CONTRACT.read_text(encoding="utf-8"))

    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            basis["conditions"],
            t85_prereg["policies"],
            t85_prereg["fits"],
            t85_prereg["commands_x_m_s"],
            int(t85_prereg["seed"]),
        )
    finally:
        sys.path.pop(0)

    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "matrix_helper": MATRIX_HELPER,
        "worker": WORKER,
        "adapter": ADAPTER,
        "base_evaluator": BASE_EVALUATOR,
        "t6_helpers": T6_HELPERS,
        "t8_helpers": T8_HELPERS,
        "r2_source": R2_SOURCE,
        "t85_nominal_result": T85_RESULT,
        "t85_nominal_preregistration": T85_PREREG,
        "r2_basis": R2_BASIS,
        "t27_runner_contract": T27_CONTRACT,
    }
    policies = t85_prereg["policies"]
    fits = t85_prereg["fits"]
    commands = t85_prereg["commands_x_m_s"]
    checks = {
        "t85_persistent_nominal_all_sixteen_green": (
            t85_result["status"]
            == "PASS_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
            and t85_result["condition"]["green_cells"] == 16
            and t85_result["condition"]["condition_green"]
            and t85_result["authority"]["robustness_preregistration"]
        ),
        "t85_exact_two_rolling_exports": (
            t85_prereg["status"]
            == "PREREGISTERED_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
            and [item["checkpoint_id"] for item in policies]
            == ["T84_ROLLING_HALF", "T84_ROLLING_FINAL"]
            and len({item["sha256"] for item in policies}) == 2
        ),
        "runner_contract_green": (
            contract["status"] == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
            and contract["failed_checks"] == []
        ),
        "conditions_exactly_unchanged_twenty": (
            len(basis["conditions"]) == 20
            and [item["condition_index"] for item in basis["conditions"]]
            == list(range(1, 21))
        ),
        "matrix_exactly_320_cells": len(plan) == 320,
        "two_policies_both_fits_four_commands": (
            len(policies) == 2 and len(fits) == 2 and len(commands) == 4
        ),
        "all_policy_fit_and_sensor_assets_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in [
                *policies,
                *fits,
                t85_prereg["calibrator"],
                t85_prereg["reference_feature_table"],
            ]
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "no_r2_cells_run": True,
        "no_training_or_colab": True,
        "no_robot_or_rdk": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t86_rolling_midpoint_r2_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T86_ROLLING_MIDPOINT_SEQUENTIAL_R2"
            if not failed
            else "HOLD_T86_ROLLING_MIDPOINT_R2_PREREGISTRATION"
        ),
        "question": (
            "Do both persistent T84 rolling exports pass the unchanged "
            "20-condition R2 ladder under both measured actuator fits "
            "and all four commands?"
        ),
        "policies": policies,
        "fits": fits,
        "calibrator": t85_prereg["calibrator"],
        "reference_feature_table": t85_prereg[
            "reference_feature_table"
        ],
        "playground": t85_prereg["playground"],
        "conditions": basis["conditions"],
        "commands_x_m_s": commands,
        "seed": t85_prereg["seed"],
        "support_handoff": t85_prereg["support_handoff"],
        "behavior_contract": t85_prereg["behavior_contract"],
        "protection_contract": t85_prereg["protection_contract"],
        "persistence_contract": {
            "rolling_half_definition": "mean(step0, step1003520)",
            "rolling_final_definition": (
                "mean(step1003520, step2007040)"
            ),
            "adapter_initializers_only": True,
            "coefficient": 0.5,
            "both_rolling_exports_required": True,
            "no_checkpoint_selection": True,
        },
        "matrix": {
            "conditions": 20,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells_per_condition": 16,
            "maximum_cells": 320,
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
            "reuse_nominal_evidence": False,
        },
        "decision_rule": {
            "pass": (
                "All 320 cells across all 20 conditions are green under "
                "the unchanged behavior, handoff, readback, rate, "
                "tracking, and duration-protection contracts."
            ),
            "pass_decision": (
                "EARN_T86_GATE5_DEPLOYMENT_READINESS_PACKAGE_"
                "PREREGISTRATION"
            ),
            "fail_decision": (
                "STOP_T86_AT_FIRST_FAILED_R2_CONDITION_AND_ATTRIBUTE"
            ),
            "training_reward_selection_weight": 0,
            "no_retry": True,
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
            "one_sequential_cpu_r2_matrix": not failed,
            "additional_training": False,
            "colab": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5_deployment_readiness_package_preregistration": False,
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
                "# T86 rolling-midpoint sequential R2 preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Conditions: `20` in the original frozen order",
                "- Cells: `16/condition`, `320 maximum`",
                "- Stop: after the first complete failed condition",
                "- Both rolling exports required; no checkpoint selection",
                "- Nominal trace reuse: `NO`",
                "- Training / Colab / Gate 5 / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
