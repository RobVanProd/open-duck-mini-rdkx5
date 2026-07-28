#!/usr/bin/env python3
"""Freeze a diagnostic R2 remainder for the immutable T84 rolling-final."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T86 = ANALYSIS / "t86_rolling_midpoint_r2_result.json"
T88 = ANALYSIS / "t88_right_smoothed_targeted_result.json"
T87 = ANALYSIS / "t87_right_smoothed_pair_result.json"
R2_BASIS = ANALYSIS / "t86_rolling_midpoint_r2_preregistration.json"
RUNNER = ROOT / "tools" / "run_t89_terminal_final_r2_remainder.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t89_terminal_final_r2_remainder.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
OUTPUT = ANALYSIS / "t89_terminal_final_r2_remainder_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T89_TERMINAL_FINAL_R2_REMAINDER_PREREGISTRATION_20260728.md"
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


def terminal_condition_evidence(
    t86: dict[str, Any], condition: dict[str, Any]
) -> dict[str, Any]:
    blocks = [
        block
        for block in t86["blocks"]
        if block["condition_id"] == condition["id"]
        and block["checkpoint_id"] == "T84_ROLLING_FINAL"
    ]
    return {
        "condition": condition,
        "blocks": [
            {
                "fit_id": block["fit_id"],
                "manifest": block["manifest"],
                "block_green": block["result"]["block_green"],
                "cells": len(block["result"]["cells"]),
                "green_cells": sum(
                    cell["cell_green"]
                    for cell in block["result"]["cells"]
                ),
            }
            for block in blocks
        ],
        "cells": sum(
            len(block["result"]["cells"]) for block in blocks
        ),
        "green_cells": sum(
            cell["cell_green"]
            for block in blocks
            for cell in block["result"]["cells"]
        ),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T89 prereg: {path}")
    t86 = json.loads(T86.read_text(encoding="utf-8"))
    t88 = json.loads(T88.read_text(encoding="utf-8"))
    t87 = json.loads(T87.read_text(encoding="utf-8"))
    basis = json.loads(R2_BASIS.read_text(encoding="utf-8"))
    completed_conditions = [
        condition
        for condition in basis["conditions"]
        if condition["condition_index"] <= 4
    ]
    remainder = [
        condition
        for condition in basis["conditions"]
        if condition["condition_index"] >= 5
    ]
    immutable = [
        terminal_condition_evidence(t86, condition)
        for condition in completed_conditions
    ]
    final_wrapped = t87["policies"]["right_smoothed_final"]["wrapped"]
    policy = {
        **final_wrapped,
        "checkpoint_id": "T84_ROLLING_FINAL_DIAGNOSTIC",
        "step": 2_007_040,
    }

    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            remainder,
            [policy],
            basis["fits"],
            basis["commands_x_m_s"],
            int(basis["seed"]),
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
        "t86_result": T86,
        "t88_result": T88,
        "t87_result": T87,
        "r2_basis": R2_BASIS,
    }
    checks = {
        "t86_terminal_final_green_through_condition_four": (
            len(immutable) == 4
            and all(
                item["cells"] == 8
                and item["green_cells"] == 8
                and len(item["blocks"]) == 2
                and all(
                    block["block_green"]
                    and block["cells"] == 4
                    and block["green_cells"] == 4
                    for block in item["blocks"]
                )
                for item in immutable
            )
        ),
        "t88_closes_static_right_smoothing": (
            t88["status"]
            == "HOLD_T88_RIGHT_SMOOTHED_TARGETED_BEHAVIOR"
            and t88["decision"] == "CLOSE_RIGHT_SMOOTHED_ADAPTER_PAIR"
            and t88["summary"]["new_green_cells"] == 7
            and t88["summary"]["new_cells"] == 8
        ),
        "terminal_policy_byte_exact_to_t84": (
            t87["policies"]["right_smoothed_final"][
                "byte_exact_to_t84_rolling_final"
            ]
        ),
        "conditions_exactly_five_through_twenty": (
            [item["condition_index"] for item in remainder]
            == list(range(5, 21))
        ),
        "exact_128_new_diagnostic_cells": len(plan) == 128,
        "all_assets_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in [
                policy,
                *basis["fits"],
                basis["calibrator"],
                basis["reference_feature_table"],
            ]
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "zero_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t89_terminal_final_r2_remainder_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T89_TERMINAL_FINAL_R2_REMAINDER_DIAGNOSTIC"
            if not failed
            else "HOLD_T89_TERMINAL_FINAL_R2_REMAINDER_PREREGISTRATION"
        ),
        "question": (
            "Is T86's hold a persistence-source problem only, or does the "
            "otherwise-green terminal rolling-final fail a later R2 "
            "condition?"
        ),
        "interpretation": {
            "diagnostic_only": True,
            "single_checkpoint_cannot_satisfy_persistence": True,
            "cannot_promote_or_deploy": True,
            "purpose": (
                "decide whether persistence stabilization around this "
                "terminal source is worth a CPU software contract"
            ),
        },
        "policies": [policy],
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "conditions": remainder,
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "immutable_conditions_one_through_four": {
            "source_result": receipt(T86),
            "conditions": immutable,
            "cells": 32,
            "green_cells": 32,
        },
        "matrix": {
            "conditions": 16,
            "policies": 1,
            "fits": 2,
            "commands": 4,
            "cells_per_condition": 8,
            "maximum_new_cells": 128,
            "plan_sha256": hashlib.sha256(
                json.dumps(
                    plan,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
            "condition_indices": list(range(5, 21)),
            "strictly_sequential_conditions": True,
            "complete_each_eight_cell_condition_before_decision": True,
            "stop_after_first_failed_condition": True,
            "reuse_prior_condition_evidence": True,
            "checkpoint_selection": False,
        },
        "decision_rule": {
            "pass": (
                "All 128 new cells pass; combined with the 32 immutable "
                "T86 terminal-final cells, this one diagnostic graph is "
                "160/160 across R2."
            ),
            "pass_decision": (
                "EARN_T90_PERSISTENCE_STABILIZATION_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "STOP_T89_AT_FIRST_TERMINAL_FINAL_FAILURE_AND_ATTRIBUTE"
            ),
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
            "one_cpu_diagnostic_remainder": not failed,
            "persistence_stabilization_cpu_contract_preregistration": False,
            "training": False,
            "colab": False,
            "checkpoint_selection": False,
            "candidate_promotion": False,
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
                "# T89 terminal-final R2 remainder preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Purpose: diagnostic only; cannot satisfy persistence",
                "- Immutable terminal-final conditions 1-4: `32/32`",
                "- New conditions: `5-20`, `128` cells maximum",
                "- Stop: first complete failed 8-cell condition",
                "- Training/Colab/Gate5/robot: `0/0/0/0`",
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
