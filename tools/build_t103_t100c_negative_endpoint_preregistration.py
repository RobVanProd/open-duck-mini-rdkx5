#!/usr/bin/env python3
"""Freeze T100C's exact COM-X-negative endpoint matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T102_RESULT = ANALYSIS / "t102_t100c_nominal_matrix_result.json"
T102_PREREG = ANALYSIS / "t102_t100c_nominal_matrix_preregistration.json"
T101_RESULT = ANALYSIS / "t101_t100c_postexport_result.json"
R2_BASIS = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
T27_CONTRACT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
RUNNER = ROOT / "tools" / "run_t103_t100c_negative_endpoint.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t103_t100c_negative_endpoint.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
BASE_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T6_HELPERS = ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
T8_HELPERS = ROOT / "tools" / "run_t8_state_coherent_handoff.py"
OUTPUT = ANALYSIS / "t103_t100c_negative_endpoint_preregistration.json"
MARKDOWN = ANALYSIS / "T103_T100C_NEGATIVE_ENDPOINT_PREREGISTRATION_20260728.md"


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
            raise FileExistsError(f"refusing to overwrite T103 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T103 preregistration requires a clean worktree")

    t102_result = json.loads(T102_RESULT.read_text(encoding="utf-8"))
    t102 = json.loads(T102_PREREG.read_text(encoding="utf-8"))
    t101 = json.loads(T101_RESULT.read_text(encoding="utf-8"))
    basis = json.loads(R2_BASIS.read_text(encoding="utf-8"))
    contract = json.loads(T27_CONTRACT.read_text(encoding="utf-8"))
    condition = next(
        item for item in basis["conditions"] if item["condition_index"] == 7
    )
    policies = []
    for checkpoint_id, step_value in (
        ("T100C_HIDDEN_EXPERT_HALF", 1_003_520),
        ("T100C_HIDDEN_EXPERT_FINAL", 2_007_040),
    ):
        wrapped = t101["deployments"][str(step_value)]["wrapped"]
        policies.append(
            {"checkpoint_id": checkpoint_id, "step": step_value, **wrapped}
        )
    fits = t102["fits"]
    commands = t102["commands_x_m_s"]
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            [condition],
            policies,
            fits,
            commands,
            int(t102["seed"]),
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
        "t102_result": T102_RESULT,
        "t102_preregistration": T102_PREREG,
        "t101_result": T101_RESULT,
        "r2_basis": R2_BASIS,
        "t27_runner_contract": T27_CONTRACT,
    }
    checks = {
        "t102_nominal_matrix_exactly_green": (
            t102_result["status"] == "PASS_T102_T100C_NOMINAL_MATRIX"
            and t102_result["condition"]["green_cells"] == 16
            and t102_result["decision"]
            == "EARN_T103_NEGATIVE_ENDPOINT_MATRIX_PREREGISTRATION_ONLY"
        ),
        "t101_transform_green": (
            t101["status"] == "PASS_T101_T100C_POSTEXPORT_TRANSFORM"
            and t101["failed_checks"] == []
        ),
        "condition_is_exact_com_x_negative": (
            condition
            == {
                "condition_index": 7,
                "id": "TORSO_COM_X_NEG",
                "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
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
                t102["calibrator"],
                t102["reference_feature_table"],
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
        "schema_version": "open_duck.t103_t100c_negative_endpoint_preregistration.v1",
        "status": (
            "PREREGISTERED_T103_T100C_NEGATIVE_ENDPOINT_MATRIX"
            if not failed
            else "HOLD_T103_T100C_NEGATIVE_ENDPOINT_PREREGISTRATION"
        ),
        "question": (
            "Do both T100C hidden-expert checkpoints repair the exact "
            "torso-COM-X-negative endpoint under both measured fits?"
        ),
        "condition": condition,
        "policies": policies,
        "fits": fits,
        "calibrator": t102["calibrator"],
        "reference_feature_table": t102["reference_feature_table"],
        "playground": t102["playground"],
        "commands_x_m_s": commands,
        "seed": t102["seed"],
        "support_handoff": t102["support_handoff"],
        "behavior_contract": t102["behavior_contract"],
        "protection_contract": t102["protection_contract"],
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
        },
        "decision_rule": {
            "pass": (
                "All 16 cells pass the unchanged frozen behavior and "
                "protection contract."
            ),
            "pass_decision": (
                "EARN_T104_FULL_R2_REVALIDATION_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T100C_HIDDEN_EXPERT_CONTINUATION",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "repository_inputs": {
            name: receipt(path) for name, path in repository_inputs.items()
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
            "one_cpu_only_sixteen_cell_matrix": not failed,
            "full_r2_preregistration": False,
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
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T103 T100C negative-endpoint preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Condition: `TORSO_COM_X_NEG`, exact `[-.05, 0, 0] m`",
                "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`",
                "- Pass: all `16/16` green",
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
