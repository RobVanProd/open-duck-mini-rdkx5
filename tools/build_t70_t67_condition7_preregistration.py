#!/usr/bin/env python3
"""Freeze T67's causal R2 condition-7 revalidation screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T69_RESULT = ANALYSIS / "t69_t67_nominal_matrix_result.json"
T69_PREREG = ANALYSIS / "t69_t67_nominal_matrix_preregistration.json"
T41_PREREG = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
T54_ATTRIBUTION = ANALYSIS / "t54_t53_condition7_failure_attribution.json"
RUNNER = ROOT / "tools" / "run_t70_t67_condition7.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
TEST = ROOT / "tests" / "test_t70_t67_condition7.py"
OUTPUT = ANALYSIS / "t70_t67_condition7_preregistration.json"
MARKDOWN = ANALYSIS / "T70_T67_CONDITION7_PREREGISTRATION_20260728.md"


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
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T70: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T70 preregistration requires a clean worktree")
    t69_result = json.loads(T69_RESULT.read_text(encoding="utf-8"))
    t69 = json.loads(T69_PREREG.read_text(encoding="utf-8"))
    t41 = json.loads(T41_PREREG.read_text(encoding="utf-8"))
    t54 = json.loads(T54_ATTRIBUTION.read_text(encoding="utf-8"))
    condition = t41["conditions"][6]
    policies = t69["policies"]
    checks = {
        "t69_nominal_persistence_green": (
            t69_result["status"] == "PASS_T69_T67_NOMINAL_MATRIX"
            and t69_result["decision"]
            == "EARN_T70_T67_R2_REVALIDATION_PREREGISTRATION"
            and t69_result["condition"]["green_cells"] == 16
        ),
        "condition_is_exact_prior_blocker": (
            condition
            == {
                "condition_index": 7,
                "id": "TORSO_COM_X_NEG",
                "override": {
                    "torso_com_offset_m": [-0.05, 0.0, 0.0]
                },
            }
        ),
        "t54_attribution_identifies_same_boundary": (
            t54["status"]
            == "PASS_T54_T53_CONDITION7_FAILURE_ATTRIBUTION"
            and t54["decision"]
            == "EARN_T55_DYNAMIC_SINGLE_SUPPORT_CURRICULUM_CPU_"
            "CONTRACT_PREREGISTRATION_ONLY"
        ),
        "exactly_two_t67_persistent_endpoints": (
            len(policies) == 2
            and {item["step"] for item in policies}
            == {1_003_520, 2_007_040}
        ),
        "all_policy_fit_and_sensor_assets_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in [
                *policies,
                *t69["fits"],
                t69["calibrator"],
                t69["reference_feature_table"],
            ]
        ),
        "runner_inputs_present": all(
            path.is_file()
            for path in (RUNNER, WORKER, ADAPTER, MATRIX_HELPER, TEST)
        ),
        "behavior_not_run": True,
        "training_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t70_t67_condition7_preregistration.v1",
        "status": (
            "PREREGISTERED_T70_T67_CONDITION7"
            if not failed
            else "HOLD_T70_T67_CONDITION7_PREREGISTRATION"
        ),
        "question": (
            "Does endpoint-stratified recurrent-core continuation repair the "
            "exact R2 torso-COM-x-negative boundary that stopped T52, at "
            "both persistent checkpoints, both measured fits, and all "
            "commands?"
        ),
        "causal_ordering": (
            "Run the prior failed condition before spending CPU on the full "
            "remaining R2 ladder; a failure closes T67 immediately."
        ),
        "condition": condition,
        "conditions": [condition],
        "policies": policies,
        "fits": t69["fits"],
        "commands_x_m_s": t69["commands_x_m_s"],
        "seed": t69["seed"],
        "calibrator": t69["calibrator"],
        "reference_feature_table": t69["reference_feature_table"],
        "playground": t69["playground"],
        "support_handoff": t69["support_handoff"],
        "behavior_contract": t69["behavior_contract"],
        "protection_contract": t69["protection_contract"],
        "repository_inputs": t69["repository_inputs"],
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "maximum_cells": 16,
            "cpu_only": True,
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "decision_rule": {
            "pass": "All 16 condition-7 cells are green.",
            "pass_decision": (
                "EARN_T71_T67_R2_REMAINDER_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_T67_ENDPOINT_CORE_CONTINUATION",
            "no_retry": True,
            "no_checkpoint_selection": True,
            "both_checkpoints_required": True,
        },
        "frozen_inputs": {
            "t69_result": receipt(T69_RESULT),
            "t69_preregistration": receipt(T69_PREREG),
            "t41_r2_source": receipt(T41_PREREG),
            "t54_attribution": receipt(T54_ATTRIBUTION),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
            "matrix_helper": receipt(MATRIX_HELPER),
            "test": receipt(TEST),
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
            "execute_one_condition7_matrix": not failed,
            "r2_remainder_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
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
                "# T70 T67 condition-7 preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Boundary: `TORSO_COM_X_NEG = -0.05 m`",
                "- Cells: `16`",
                "- Both checkpoints/fits/all commands required",
                "- Training/Colab/Gate5/robot: `0/0/0/0`",
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
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
