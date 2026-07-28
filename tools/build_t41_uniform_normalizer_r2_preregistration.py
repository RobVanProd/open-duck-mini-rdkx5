#!/usr/bin/env python3
"""Freeze T41's sequential R2 matrix for the T39 uniform-normalizer pair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T40_RESULT = ANALYSIS / "t40_t39_exact_recovery_result.json"
T39_PREREG = (
    ANALYSIS
    / "t39_uniform_normalizer_rollback_nominal_preregistration.json"
)
T27_PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
T27_CONTRACT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
R2_SOURCE = ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json"
RUNNER = ROOT / "tools" / "run_t41_uniform_normalizer_r2.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
BASE_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T6_HELPERS = ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
T8_HELPERS = ROOT / "tools" / "run_t8_state_coherent_handoff.py"
OUTPUT = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T41_UNIFORM_NORMALIZER_R2_PREREGISTRATION_20260728.md"
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
            raise FileExistsError(f"refusing to overwrite T41 prereg: {path}")
    t40 = json.loads(T40_RESULT.read_text(encoding="utf-8"))
    t39 = json.loads(T39_PREREG.read_text(encoding="utf-8"))
    basis = json.loads(T27_PREREG.read_text(encoding="utf-8"))
    contract = json.loads(T27_CONTRACT.read_text(encoding="utf-8"))

    sys_path_added = False
    try:
        import sys

        sys.path.insert(0, str(ROOT / "tools"))
        sys_path_added = True
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            basis["conditions"],
            t39["policies"],
            basis["fits"],
            basis["commands_x_m_s"],
            int(basis["seed"]),
        )
    finally:
        if sys_path_added:
            sys.path.pop(0)

    repository_inputs = {
        "runner": RUNNER,
        "matrix_helper": MATRIX_HELPER,
        "worker": WORKER,
        "adapter": ADAPTER,
        "base_evaluator": BASE_EVALUATOR,
        "t6_helpers": T6_HELPERS,
        "t8_helpers": T8_HELPERS,
        "r2_source": R2_SOURCE,
        "t40_nominal_result": T40_RESULT,
        "t39_transform_preregistration": T39_PREREG,
        "t27_runner_contract": T27_CONTRACT,
    }
    checks = {
        "t40_nominal_all_sixteen_green": (
            t40["status"] == "PASS_T40_T39_EXACT_RECOVERY"
            and t40["condition"]["green_cells"] == 16
            and t40["condition"]["condition_green"]
            and t40["authority"]["robustness_preregistration"]
        ),
        "t39_uniform_transform_exact": (
            t39["status"]
            == "PREREGISTERED_T39_UNIFORM_NORMALIZER_ROLLBACK_NOMINAL_MATRIX"
            and t39["mechanism"]["uniform_across_checkpoints"]
            and t39["mechanism"]["changed_initializer_names"]
            == ["obs_mean", "obs_std"]
        ),
        "runner_contract_green": (
            contract["status"] == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
            and contract["failed_checks"] == []
        ),
        "conditions_exactly_unchanged_twenty": (
            len(basis["conditions"]) == 20
        ),
        "matrix_exactly_320_cells": len(plan) == 320,
        "two_policies_both_fits_four_commands": (
            len(t39["policies"]) == 2
            and len(basis["fits"]) == 2
            and len(basis["commands_x_m_s"]) == 4
        ),
        "all_policy_fit_and_sensor_assets_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in [
                *t39["policies"],
                *basis["fits"],
                basis["calibrator"],
                basis["reference_feature_table"],
            ]
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "no_robustness_cells_run": True,
        "no_training_or_colab": True,
        "no_robot_or_rdk": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t41_uniform_normalizer_r2_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T41_UNIFORM_NORMALIZER_SEQUENTIAL_R2"
            if not failed
            else "HOLD_T41_UNIFORM_NORMALIZER_R2_PREREGISTRATION"
        ),
        "question": (
            "Do both uniformly transformed T39 checkpoints pass the "
            "unchanged sequential 20-condition R2 ladder under both "
            "measured actuator fits and all four commands?"
        ),
        "policies": t39["policies"],
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "conditions": basis["conditions"],
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
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
                "the unchanged behavior, handoff, readback, rate, tracking, "
                "and duration-protection contracts."
            ),
            "pass_decision": (
                "EARN_T41_GATE5_PACKAGE_PREREGISTRATION"
            ),
            "fail_decision": (
                "STOP_T41_AT_FIRST_FAILED_R2_CONDITION_AND_ATTRIBUTE"
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
            "gate5_package_preregistration": False,
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
                "# T41 uniform-normalizer sequential R2 preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Conditions: `20` in frozen order",
                "- Cells: `16/condition`, `320 maximum`",
                "- Stop: after first complete failed condition",
                "- Both checkpoints required; no checkpoint selection",
                "- Nominal trace reuse: `NO`",
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
