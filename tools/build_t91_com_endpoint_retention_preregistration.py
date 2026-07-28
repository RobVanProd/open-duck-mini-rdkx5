#!/usr/bin/env python3
"""Freeze T91's COM-X-negative endpoint-retention diagnostic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T90_RESULT = ANALYSIS / "t90_r2_endpoint_exposure_audit.json"
T85_RESULT = ANALYSIS / "t85_rolling_midpoint_nominal_result.json"
T85_PREREG = (
    ANALYSIS / "t85_rolling_midpoint_nominal_preregistration.json"
)
T86_RESULT = ANALYSIS / "t86_rolling_midpoint_r2_result.json"
T89_RESULT = ANALYSIS / "t89_terminal_final_r2_remainder_result.json"
R2_BASIS = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
T27_CONTRACT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
RUNNER = ROOT / "tools" / "run_t91_com_endpoint_retention.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t91_com_endpoint_retention.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
BASE_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T6_HELPERS = ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
T8_HELPERS = ROOT / "tools" / "run_t8_state_coherent_handoff.py"
OUTPUT = ANALYSIS / "t91_com_endpoint_retention_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T91_COM_ENDPOINT_RETENTION_PREREGISTRATION_20260728.md"
)


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
            raise FileExistsError(f"refusing to overwrite T91 prereg: {path}")

    t90 = json.loads(T90_RESULT.read_text(encoding="utf-8"))
    t85_result = json.loads(T85_RESULT.read_text(encoding="utf-8"))
    t85_prereg = json.loads(T85_PREREG.read_text(encoding="utf-8"))
    t86 = json.loads(T86_RESULT.read_text(encoding="utf-8"))
    t89 = json.loads(T89_RESULT.read_text(encoding="utf-8"))
    basis = json.loads(R2_BASIS.read_text(encoding="utf-8"))
    contract = json.loads(T27_CONTRACT.read_text(encoding="utf-8"))
    condition = next(
        item
        for item in basis["conditions"]
        if item["condition_index"] == 7
    )

    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            [condition],
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
        "t90_exposure_audit": T90_RESULT,
        "t85_nominal_result": T85_RESULT,
        "t85_nominal_preregistration": T85_PREREG,
        "t86_r2_result": T86_RESULT,
        "t89_terminal_result": T89_RESULT,
        "r2_basis": R2_BASIS,
        "t27_runner_contract": T27_CONTRACT,
    }
    policies = t85_prereg["policies"]
    fits = t85_prereg["fits"]
    commands = t85_prereg["commands_x_m_s"]
    checks = {
        "t90_earned_only_this_diagnostic": (
            t90["status"] == "PASS_T90_R2_ENDPOINT_EXPOSURE_AUDIT"
            and t90["decision"]
            == "EARN_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC_"
            "PREREGISTRATION_ONLY"
            and not t90["interpretation"]["hosted_run_earned"]
        ),
        "t85_nominal_pair_green": (
            t85_result["status"]
            == "PASS_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
            and t85_result["condition"]["green_cells"] == 16
            and t85_result["condition"]["condition_green"]
        ),
        "prior_failures_exact": (
            t86["status"] == "HOLD_T86_ROLLING_MIDPOINT_R2"
            and t86["summary"]["first_failed_condition"]
            == "JOINT_FRICTIONLOSS_HI"
            and t89["status"]
            == "HOLD_T89_TERMINAL_FINAL_R2_REMAINDER"
            and t89["summary"]["first_failed_condition"] == "ARMATURE_HI"
        ),
        "condition_is_exact_com_x_negative": (
            condition
            == {
                "condition_index": 7,
                "id": "TORSO_COM_X_NEG",
                "override": {
                    "torso_com_offset_m": [-0.05, 0.0, 0.0],
                },
            }
        ),
        "runner_contract_green": (
            contract["status"] == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
            and contract["failed_checks"] == []
        ),
        "matrix_exactly_sixteen_cells": len(plan) == 16,
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
        "no_behavior_run_during_preregistration": True,
        "no_training_or_colab": True,
        "no_robot_or_rdk": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t91_com_endpoint_retention_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC"
            if not failed
            else "HOLD_T91_COM_ENDPOINT_RETENTION_PREREGISTRATION"
        ),
        "question": (
            "Do both T84 rolling exports retain the exact "
            "torso-COM-X-negative endpoint that occupied one full T78 "
            "training stratum?"
        ),
        "condition": condition,
        "policies": policies,
        "fits": fits,
        "calibrator": t85_prereg["calibrator"],
        "reference_feature_table": t85_prereg[
            "reference_feature_table"
        ],
        "playground": t85_prereg["playground"],
        "commands_x_m_s": commands,
        "seed": t85_prereg["seed"],
        "support_handoff": t85_prereg["support_handoff"],
        "behavior_contract": t85_prereg["behavior_contract"],
        "protection_contract": t85_prereg["protection_contract"],
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells": 16,
            "plan_sha256": hashlib.sha256(
                json.dumps(
                    plan,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "diagnostic_only": True,
        },
        "decision_rule": {
            "pass": (
                "All 16 cells are green under the unchanged frozen "
                "behavior and protection contract."
            ),
            "pass_decision": (
                "EARN_T92_FULL_R2_ENDPOINT_REPLAY_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_EXACT_ENDPOINT_REPLAY_AS_SUFFICIENT_MECHANISM"
            ),
            "no_retry": True,
            "training_selection_weight": 0,
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
            "one_cpu_only_sixteen_cell_diagnostic": not failed,
            "full_endpoint_cpu_contract_preregistration": False,
            "additional_training": False,
            "colab": False,
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
                "# T91 COM-endpoint retention diagnostic preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Condition: `TORSO_COM_X_NEG`, exact `[-.05, 0, 0] m`",
                "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`",
                "- Pass: all `16/16` green",
                (
                    "- Pass earns only a full-R2 endpoint-replay CPU "
                    "contract preregistration"
                ),
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
