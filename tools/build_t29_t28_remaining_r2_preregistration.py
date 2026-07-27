#!/usr/bin/env python3
"""Freeze the remaining 19-condition T28 R2 robustness ladder."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T27_PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
T27_RUNNER_CONTRACT = (
    ANALYSIS / "t27_t23_robustness_runner_contract.json"
)
T28_TRANSFORM = ANALYSIS / "t28_t23_action_margin_transform_contract.json"
T28_CONDITION_PREREG = (
    ANALYSIS
    / "t28_t23_action_margin_condition_preregistration.json"
)
T28_CONDITION_RESULT = (
    ANALYSIS / "t28_t23_action_margin_condition_result.json"
)
RUNNER = ROOT / "tools" / "run_t29_t28_remaining_r2_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
OUTPUT = ANALYSIS / "t29_t28_remaining_r2_preregistration.json"
OUTPUT_MD = (
    ANALYSIS / "T29_T28_REMAINING_R2_PREREGISTRATION_20260726.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def matrix_plan(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "cell_index": index,
            "condition_index": condition["condition_index"],
            "condition_id": condition["id"],
            "checkpoint_id": policy["checkpoint_id"],
            "fit_id": fit["fit_id"],
            "command_x_m_s": float(command),
        }
        for index, (condition, policy, fit, command) in enumerate(
            (
                (condition, policy, fit, command)
                for condition in payload["conditions"]
                for policy in payload["policies"]
                for fit in payload["fits"]
                for command in payload["commands_x_m_s"]
            ),
            start=1,
        )
    ]


def main() -> int:
    basis = json.loads(T27_PREREG.read_text(encoding="utf-8"))
    runner_contract = json.loads(
        T27_RUNNER_CONTRACT.read_text(encoding="utf-8")
    )
    transform = json.loads(T28_TRANSFORM.read_text(encoding="utf-8"))
    condition_prereg = json.loads(
        T28_CONDITION_PREREG.read_text(encoding="utf-8")
    )
    condition_result = json.loads(
        T28_CONDITION_RESULT.read_text(encoding="utf-8")
    )
    policies = [
        {
            "checkpoint_id": item["checkpoint_id"],
            "step": int(item["step"]),
            **item["wrapped"],
        }
        for item in transform["policies"]
    ]
    for item in policies:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T28 policy: {path}")
    conditions = basis["conditions"][1:]
    repository_inputs = dict(basis["repository_inputs"])
    repository_inputs.update(
        {
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "t28_transform_contract": receipt(T28_TRANSFORM),
            "t28_condition_preregistration": receipt(T28_CONDITION_PREREG),
            "t28_condition_result": receipt(T28_CONDITION_RESULT),
        }
    )
    checks = {
        "t27_runner_contract_green": (
            runner_contract["status"]
            == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
        ),
        "t28_transform_contract_green": (
            transform["status"]
            == "PASS_T28_T23_ACTION_MARGIN_TRANSFORM_CONTRACT"
        ),
        "t28_condition_one_green": (
            condition_result["status"]
            == "PASS_T28_T23_ACTION_MARGIN_CONDITION"
            and condition_result["condition"]["green_cells"] == 16
        ),
        "condition_one_policy_and_gate_match": (
            condition_prereg["policies"] == policies
            and condition_prereg["behavior_contract"]
            == basis["behavior_contract"]
            and condition_prereg["protection_contract"]
            == basis["protection_contract"]
        ),
        "exactly_nineteen_remaining_conditions": len(conditions) == 19,
        "remaining_indices_are_two_through_twenty": (
            [item["condition_index"] for item in conditions]
            == list(range(2, 21))
        ),
        "two_policies_two_fits_four_commands": (
            len(policies) == 2
            and len(basis["fits"]) == 2
            and len(basis["commands_x_m_s"]) == 4
        ),
        "runner_and_worker_present": RUNNER.is_file() and WORKER.is_file(),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t29_t28_remaining_r2_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T29_T28_REMAINING_R2_MATRIX"
            if not failed_checks
            else "HOLD_T29_T28_REMAINING_R2_PREREGISTRATION"
        ),
        "question": (
            "After T28 passes R2 condition 1, do both uniformly wrapped "
            "checkpoints pass original R2 conditions 2 through 20?"
        ),
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "conditions": conditions,
        "policies": policies,
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "condition_one_basis": {
            "preregistration": receipt(T28_CONDITION_PREREG),
            "result": receipt(T28_CONDITION_RESULT),
            "green_cells": 16,
        },
        "matrix": {
            "remaining_conditions": 19,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "maximum_new_cells": 304,
            "total_r2_cells_with_condition_one": 320,
            "sequential_conditions": True,
            "complete_current_sixteen_cell_condition_before_stop": True,
            "stop_after_first_failed_condition": True,
            "no_skip": True,
            "no_retry": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "all_remaining_pass": (
                "All 304 new cells pass and combine with the frozen green "
                "condition 1 to yield 320/320. Authorize only Gate 5 package "
                "preregistration."
            ),
            "first_failure": (
                "Finish that condition, stop, and attribute the failed cells. "
                "No training is automatically earned."
            ),
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "repository_inputs": repository_inputs,
        "checks": checks,
        "failed_checks": failed_checks,
        "authority": {
            "execute_remaining_cpu_matrix": not failed_checks,
            "training": False,
            "colab": False,
            "gate5_package_preregistration": False,
            "gate5_hardware": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    plan = matrix_plan(payload)
    payload["matrix"]["plan_sha256"] = hashlib.sha256(
        json.dumps(
            plan,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T29 T28 remaining R2 preregistration",
        "",
        f"status: `{payload['status']}`",
        "",
        "Condition 1 is frozen green at 16/16. T29 executes original R2 "
        "conditions 2–20 in their original order, 16 cells per condition, "
        "and stops only after completing the first failed condition.",
        "",
        "Maximum new work is 304 CPU cells. Passing all of them yields "
        "320/320 and authorizes only Gate 5 package preregistration—not "
        "hardware execution.",
        "",
        "No training, Colab, RDK-X5, robot, torque, or motion is authorized.",
        "",
    ]
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(payload["status"])
    print(f"failed_checks={failed_checks}")
    print(f"plan_sha256={payload['matrix']['plan_sha256']}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
