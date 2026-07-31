#!/usr/bin/env python3
"""Freeze T92's raw-T78 COM endpoint attribution matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T91_RESULT = ANALYSIS / "t91_com_endpoint_retention_result.json"
T80_RESULT = ANALYSIS / "t80_t78_nominal_matrix_result.json"
T80_PREREG = ANALYSIS / "t80_t78_nominal_matrix_preregistration.json"
T70_RESULT = ANALYSIS / "t70_t67_condition7_result.json"
R2_BASIS = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
T27_CONTRACT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
RUNNER = ROOT / "tools" / "run_t92_raw_t78_com_attribution.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t92_raw_t78_com_attribution.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
BASE_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T6_HELPERS = ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
T8_HELPERS = ROOT / "tools" / "run_t8_state_coherent_handoff.py"
OUTPUT = ANALYSIS / "t92_raw_t78_com_attribution_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T92_RAW_T78_COM_ATTRIBUTION_PREREGISTRATION_20260728.md"
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
            raise FileExistsError(f"refusing to overwrite T92 prereg: {path}")

    t91 = json.loads(T91_RESULT.read_text(encoding="utf-8"))
    t80_result = json.loads(T80_RESULT.read_text(encoding="utf-8"))
    t80 = json.loads(T80_PREREG.read_text(encoding="utf-8"))
    t70 = json.loads(T70_RESULT.read_text(encoding="utf-8"))
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
            t80["policies"],
            t80["fits"],
            t80["commands_x_m_s"],
            int(t80["seed"]),
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
        "t91_result": T91_RESULT,
        "t80_nominal_result": T80_RESULT,
        "t80_nominal_preregistration": T80_PREREG,
        "t70_core_endpoint_result": T70_RESULT,
        "r2_basis": R2_BASIS,
        "t27_runner_contract": T27_CONTRACT,
    }
    policies = t80["policies"]
    fits = t80["fits"]
    commands = t80["commands_x_m_s"]
    checks = {
        "t91_closed_simple_endpoint_replay": (
            t91["status"]
            == "HOLD_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC"
            and t91["decision"]
            == "CLOSE_EXACT_ENDPOINT_REPLAY_AS_SUFFICIENT_MECHANISM"
            and t91["summary"]["green_cells"] == 4
        ),
        "raw_t78_nominal_outcome_exact": (
            t80_result["status"] == "HOLD_T80_T78_NOMINAL_MATRIX"
            and t80_result["condition"]["green_cells"] == 14
            and t80_result["condition"]["cells"] == 16
        ),
        "t67_core_endpoint_baseline_exact": (
            t70["status"] == "HOLD_T70_T67_CONDITION7"
            and t70["condition"]["green_cells"] == 6
            and t70["condition"]["cells"] == 16
        ),
        "condition_matches_t91_exactly": (
            t91["blocks"][0]["condition_id"] == condition["id"]
            and t91["blocks"][0]["condition_index"]
            == condition["condition_index"]
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
        "exact_raw_t78_pair": (
            [item["checkpoint_id"] for item in policies]
            == ["T78_JOINT_ADAPTER_HALF", "T78_JOINT_ADAPTER_FINAL"]
            and [item["step"] for item in policies]
            == [1_003_520, 2_007_040]
        ),
        "runner_contract_green": (
            contract["status"] == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
            and contract["failed_checks"] == []
        ),
        "matrix_exactly_sixteen_cells": len(plan) == 16,
        "all_policy_fit_and_sensor_assets_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in [
                *policies,
                *fits,
                t80["calibrator"],
                t80["reference_feature_table"],
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
            "open_duck.t92_raw_t78_com_attribution_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T92_RAW_T78_COM_ATTRIBUTION"
            if not failed
            else "HOLD_T92_RAW_T78_COM_ATTRIBUTION_PREREGISTRATION"
        ),
        "question": (
            "Did the raw T78 half/final checkpoints learn the exact "
            "COM-X-negative endpoint response and lose it only during "
            "rolling checkpoint averaging, or was it never learned?"
        ),
        "condition": condition,
        "policies": policies,
        "fits": fits,
        "calibrator": t80["calibrator"],
        "reference_feature_table": t80["reference_feature_table"],
        "playground": t80["playground"],
        "commands_x_m_s": commands,
        "seed": t80["seed"],
        "support_handoff": t80["support_handoff"],
        "behavior_contract": t80["behavior_contract"],
        "protection_contract": t80["protection_contract"],
        "baselines": {
            "t67_core_endpoint_green_cells": 6,
            "t84_rolling_endpoint_green_cells": 4,
            "raw_t78_nominal_green_cells": 14,
        },
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
            "diagnostic_only": True,
            "both_raw_checkpoints_required": True,
            "checkpoint_selection": False,
        },
        "classification_rule": {
            "full": {
                "predicate": "raw_green_cells == 16",
                "classification": (
                    "RAW_ENDPOINT_LEARNED_ROLLING_TRANSFORM_DESTROYED_IT"
                ),
                "decision": (
                    "EARN_COTRAINING_CONFLICT_CPU_FALSIFIER_"
                    "PREREGISTRATION_ONLY"
                ),
            },
            "partial": {
                "predicate": "6 < raw_green_cells < 16",
                "classification": (
                    "RAW_ENDPOINT_PARTIALLY_LEARNED_BUT_NOT_PERSISTENT"
                ),
                "decision": (
                    "EARN_SPECIALIST_CAPACITY_CPU_FALSIFIER_"
                    "PREREGISTRATION_ONLY"
                ),
            },
            "none": {
                "predicate": "raw_green_cells <= 6",
                "classification": "NO_GAIN_OVER_T67_CORE_ENDPOINT_BASELINE",
                "decision": "CLOSE_T78_ADAPTER_ENDPOINT_CONTINUATION",
            },
            "training_selection_weight": 0,
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
            "one_cpu_only_sixteen_cell_attribution": not failed,
            "successor_cpu_preregistration": False,
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
                "# T92 raw-T78 COM attribution preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Condition: `TORSO_COM_X_NEG = −0.05 m`",
                "- Policies: raw T78 half and final",
                "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`",
                "- Baselines: T67 `6/16`; T84 rolling `4/16`",
                "- Diagnostic only; no checkpoint selection",
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
