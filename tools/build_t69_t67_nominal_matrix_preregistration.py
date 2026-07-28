#!/usr/bin/env python3
"""Freeze T67's 16-cell corrected nominal behavior matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
TRANSFORM = ANALYSIS / "t68_t67_postexport_result.json"
T27_PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
T27_RUNNER_CONTRACT = (
    ANALYSIS / "t27_t23_robustness_runner_contract.json"
)
RUNNER = ROOT / "tools" / "run_t69_t67_nominal_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
TEST = ROOT / "tests" / "test_t69_t67_nominal_matrix.py"
OUTPUT = ANALYSIS / "t69_t67_nominal_matrix_preregistration.json"
OUTPUT_MD = ANALYSIS / "T69_T67_NOMINAL_MATRIX_PREREGISTRATION_20260728.md"


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
    for path in (OUTPUT, OUTPUT_MD):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T69: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T69 preregistration requires a clean worktree")
    transform = json.loads(TRANSFORM.read_text(encoding="utf-8"))
    basis = json.loads(T27_PREREG.read_text(encoding="utf-8"))
    runner_contract = json.loads(
        T27_RUNNER_CONTRACT.read_text(encoding="utf-8")
    )
    policies = []
    for checkpoint_id, step_value in (
        ("T67_ENDPOINT_CORE_HALF", 1_003_520),
        ("T67_ENDPOINT_CORE_FINAL", 2_007_040),
    ):
        wrapped = transform["deployments"][str(step_value)]["wrapped"]
        path = Path(wrapped["path"])
        if sha256(path) != wrapped["sha256"]:
            raise ValueError(f"changed T69 policy: {path}")
        policies.append(
            {
                "checkpoint_id": checkpoint_id,
                "step": step_value,
                **wrapped,
            }
        )
    default_condition = basis["conditions"][1]
    checks = {
        "t68_transform_green": (
            transform["status"] == "PASS_T68_T67_POSTEXPORT_TRANSFORM"
            and transform["decision"]
            == "EARN_T69_NOMINAL_MATRIX_PREREGISTRATION"
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
        "runner_worker_adapter_test_present": all(
            path.is_file() for path in (RUNNER, WORKER, ADAPTER, TEST)
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    payload: dict[str, Any] = {
        "schema_version": "open_duck.t69_t67_nominal_matrix_preregistration.v1",
        "status": (
            "PREREGISTERED_T69_T67_NOMINAL_MATRIX"
            if not failed
            else "HOLD_T69_T67_NOMINAL_MATRIX_PREREGISTRATION"
        ),
        "question": (
            "Do both T67 endpoint-core checkpoints pass every command and "
            "both measured actuator fits under exact default dynamics?"
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
                "default condition -> endpoint-core half/final -> fit p30/"
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
                "EARN_T70_T67_R2_REVALIDATION_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_T67_ENDPOINT_CORE_CONTINUATION",
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "frozen_inputs": {
            "t68_transform": receipt(TRANSFORM),
            "t27_preregistration": receipt(T27_PREREG),
            "t27_runner_contract": receipt(T27_RUNNER_CONTRACT),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
            "test": receipt(TEST),
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "execute_one_cpu_nominal_matrix": not failed,
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
                "# T69 T67 nominal matrix preregistration",
                "",
                f"- Status: `{payload['status']}`",
                "- Cells: `16`",
                "- Policies: endpoint-core half + final, both required",
                "- Fits: `P30 / P31-34`",
                "- Commands: `0 / .074 / .077 / .080 m/s`",
                "- Training/Colab/Gate5/robot authority: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
