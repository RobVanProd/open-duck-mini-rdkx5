#!/usr/bin/env python3
"""Freeze the T28 16-cell floor-friction falsifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
TRANSFORM_PREREG = ANALYSIS / "t28_t23_action_margin_preregistration.json"
TRANSFORM_CONTRACT = (
    ANALYSIS / "t28_t23_action_margin_transform_contract.json"
)
T27_PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
T27_RESULT = ANALYSIS / "t27_t23_robustness_matrix_result.json"
T27_RUNNER_CONTRACT = (
    ANALYSIS / "t27_t23_robustness_runner_contract.json"
)
RUNNER = ROOT / "tools" / "run_t28_t23_action_margin_condition.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
OUTPUT = (
    ANALYSIS
    / "t28_t23_action_margin_condition_preregistration.json"
)
OUTPUT_MD = (
    ANALYSIS
    / "T28_T23_ACTION_MARGIN_CONDITION_PREREGISTRATION_20260726.md"
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


def main() -> int:
    transform_prereg = json.loads(
        TRANSFORM_PREREG.read_text(encoding="utf-8")
    )
    transform = json.loads(
        TRANSFORM_CONTRACT.read_text(encoding="utf-8")
    )
    basis = json.loads(T27_PREREG.read_text(encoding="utf-8"))
    t27_result = json.loads(T27_RESULT.read_text(encoding="utf-8"))
    runner_contract = json.loads(
        T27_RUNNER_CONTRACT.read_text(encoding="utf-8")
    )
    policies = []
    for item in transform["policies"]:
        wrapped = item["wrapped"]
        path = Path(wrapped["path"])
        if sha256(path) != wrapped["sha256"]:
            raise ValueError(f"changed T28 policy: {path}")
        policies.append(
            {
                "checkpoint_id": item["checkpoint_id"],
                "step": int(item["step"]),
                **wrapped,
            }
        )
    checks = {
        "transform_preregistered": (
            transform_prereg["status"]
            == "PREREGISTERED_T28_T23_ACTION_MARGIN_REPAIR"
        ),
        "transform_contract_green": (
            transform["status"]
            == "PASS_T28_T23_ACTION_MARGIN_TRANSFORM_CONTRACT"
        ),
        "t27_runner_contract_green": (
            runner_contract["status"]
            == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
        ),
        "t27_stopped_at_condition_one": (
            t27_result["summary"]["completed_conditions"] == 1
            and t27_result["summary"]["first_failed_condition"]
            == "FLOOR_FRICTION_LO"
        ),
        "exactly_two_uniformly_wrapped_policies": len(policies) == 2,
        "condition_is_original_r2_condition_one": (
            basis["conditions"][0]
            == {
                "condition_index": 1,
                "id": "FLOOR_FRICTION_LO",
                "override": {"floor_friction": 0.5},
            }
        ),
        "runner_and_worker_present": RUNNER.is_file() and WORKER.is_file(),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t28_t23_action_margin_condition_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T28_T23_ACTION_MARGIN_CONDITION"
            if not failed_checks
            else "HOLD_T28_T23_ACTION_MARGIN_CONDITION_PREREGISTRATION"
        ),
        "question": (
            "Does the uniform exact T28 action-margin transform make both "
            "T23 checkpoints pass the complete floor-friction-0.5 condition?"
        ),
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "conditions": [basis["conditions"][0]],
        "policies": policies,
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "repository_inputs": basis["repository_inputs"],
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "maximum_cells": 16,
            "execution_order": (
                "condition -> checkpoint half/final -> fit p30/p31_34 -> "
                "command 0/.074/.077/.080"
            ),
            "condition_must_complete": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": (
                "All 16 cells pass the unchanged T27 behavior, corrected "
                "duration-protection, handoff, and exact-readback checks. "
                "Authorize preregistration of conditions 2-20 only."
            ),
            "fail": (
                "Close the exact T28 transform and attribute the first failed "
                "cell. No training is automatically earned."
            ),
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "frozen_inputs": {
            "transform_preregistration": receipt(TRANSFORM_PREREG),
            "transform_contract": receipt(TRANSFORM_CONTRACT),
            "t27_preregistration": receipt(T27_PREREG),
            "t27_result": receipt(T27_RESULT),
            "t27_runner_contract": receipt(T27_RUNNER_CONTRACT),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "authority": {
            "execute_one_cpu_condition": not failed_checks,
            "conditions_two_through_twenty": False,
            "training": False,
            "colab": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "gate5": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T28 T23 action-margin condition preregistration",
        "",
        f"status: `{payload['status']}`",
        "",
        "The frozen falsifier is exactly 16 CPU cells: both wrapped "
        "checkpoints × both measured actuator fits × x=0/.074/.077/.080 at "
        "the original R2 floor-friction-0.5 condition.",
        "",
        "All 16 must pass. Passing authorizes only preregistration of the "
        "remaining R2 conditions; failing closes this transform. No training, "
        "Gate 5, RDK-X5, robot, torque, or motion is authorized.",
        "",
    ]
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(payload["status"])
    print(f"failed_checks={failed_checks}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
