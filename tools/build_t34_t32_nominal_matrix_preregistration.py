#!/usr/bin/env python3
"""Freeze T32's 16-cell corrected nominal behavior matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
TRANSFORM = ANALYSIS / "t33_t32_postexport_result.json"
T27_PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
T27_RUNNER_CONTRACT = (
    ANALYSIS / "t27_t23_robustness_runner_contract.json"
)
RUNNER = ROOT / "tools" / "run_t34_t32_nominal_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
OUTPUT = ANALYSIS / "t34_t32_nominal_matrix_preregistration.json"
OUTPUT_MD = (
    ANALYSIS / "T34_T32_NOMINAL_MATRIX_PREREGISTRATION_20260727.md"
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
    transform = json.loads(TRANSFORM.read_text(encoding="utf-8"))
    basis = json.loads(T27_PREREG.read_text(encoding="utf-8"))
    runner_contract = json.loads(
        T27_RUNNER_CONTRACT.read_text(encoding="utf-8")
    )
    policies = []
    for checkpoint_id, step in (
        ("T32_MARGIN_HALF", 1_003_520),
        ("T32_MARGIN_FINAL", 2_007_040),
    ):
        wrapped = transform["deployments"][str(step)]["wrapped"]
        path = Path(wrapped["path"])
        if sha256(path) != wrapped["sha256"]:
            raise ValueError(f"changed T34 policy: {path}")
        policies.append(
            {
                "checkpoint_id": checkpoint_id,
                "step": step,
                **wrapped,
            }
        )
    default_condition = basis["conditions"][1]
    checks = {
        "t33_transform_green": (
            transform["status"] == "PASS_T33_T32_POSTEXPORT_TRANSFORM"
            and transform["decision"]
            == "EARN_T33_NOMINAL_MATRIX_PREREGISTRATION"
        ),
        "t27_runner_contract_green": (
            runner_contract["status"]
            == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
        ),
        "exactly_two_uniformly_transformed_policies": len(policies) == 2,
        "condition_is_exact_default_floor_friction": (
            default_condition
            == {
                "condition_index": 2,
                "id": "FLOOR_FRICTION_HI",
                "override": {"floor_friction": 1.0},
            }
        ),
        "runner_and_worker_present": RUNNER.is_file() and WORKER.is_file(),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t34_t32_nominal_matrix_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T34_T32_NOMINAL_MATRIX"
            if not failed_checks
            else "HOLD_T34_T32_NOMINAL_MATRIX_PREREGISTRATION"
        ),
        "question": (
            "Do both T32 checkpoints pass all commands and both measured "
            "actuator fits under exact default dynamics?"
        ),
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "conditions": [default_condition],
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
                "default condition -> checkpoint half/final -> fit p30/"
                "p31_34 -> command 0/.074/.077/.080"
            ),
            "condition_must_complete": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": (
                "All 16 cells pass unchanged behavior, corrected duration "
                "protection, handoff, readback, action margin, and rate checks."
            ),
            "pass_decision": (
                "EARN_T32_R2_ROBUSTNESS_MATRIX_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_T32_ACTION_MARGIN_TRAINTHROUGH",
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "frozen_inputs": {
            "t33_transform": receipt(TRANSFORM),
            "t27_preregistration": receipt(T27_PREREG),
            "t27_runner_contract": receipt(T27_RUNNER_CONTRACT),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "authority": {
            "execute_one_cpu_nominal_matrix": not failed_checks,
            "robustness_preregistration": False,
            "robustness_execution": False,
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
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# T34 T32 nominal matrix preregistration",
                "",
                f"status: `{payload['status']}`",
                "",
                "Exactly 16 CPU cells: both T32 checkpoints × both measured "
                "actuator fits × x=0/.074/.077/.080 at default dynamics.",
                "",
                "All 16 must pass. No training, Gate 5, RDK-X5, robot, "
                "torque, or motion is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
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
