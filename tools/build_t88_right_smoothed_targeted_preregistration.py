#!/usr/bin/env python3
"""Freeze T88's targeted behavior falsifier for the T87 pair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T87 = ANALYSIS / "t87_right_smoothed_pair_result.json"
T85 = ANALYSIS / "t85_rolling_midpoint_nominal_result.json"
T86 = ANALYSIS / "t86_rolling_midpoint_r2_result.json"
R2_BASIS = ANALYSIS / "t86_rolling_midpoint_r2_preregistration.json"
RUNNER = ROOT / "tools" / "run_t88_right_smoothed_targeted.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t88_right_smoothed_targeted.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
OUTPUT = ANALYSIS / "t88_right_smoothed_targeted_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T88_RIGHT_SMOOTHED_TARGETED_PREREGISTRATION_20260728.md"
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


def final_blocks(
    result: dict[str, Any], condition_id: str
) -> list[dict[str, Any]]:
    return [
        block
        for block in result["blocks"]
        if block["condition_id"] == condition_id
        and block["checkpoint_id"] == "T84_ROLLING_FINAL"
    ]


def immutable_evidence(
    source_path: Path,
    result: dict[str, Any],
    condition: dict[str, Any],
) -> dict[str, Any]:
    blocks = final_blocks(result, condition["id"])
    return {
        "condition": condition,
        "source_result": receipt(source_path),
        "checkpoint_id": "T84_ROLLING_FINAL",
        "blocks": [
            {
                "fit_id": block["fit_id"],
                "manifest": block["manifest"],
                "block_green": block["result"]["block_green"],
                "green_cells": sum(
                    cell["cell_green"]
                    for cell in block["result"]["cells"]
                ),
                "cells": len(block["result"]["cells"]),
            }
            for block in blocks
        ],
        "green_cells": sum(
            cell["cell_green"]
            for block in blocks
            for cell in block["result"]["cells"]
        ),
        "cells": sum(
            len(block["result"]["cells"]) for block in blocks
        ),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T88 prereg: {path}")
    t87 = json.loads(T87.read_text(encoding="utf-8"))
    t85 = json.loads(T85.read_text(encoding="utf-8"))
    t86 = json.loads(T86.read_text(encoding="utf-8"))
    basis = json.loads(R2_BASIS.read_text(encoding="utf-8"))
    conditions = [
        condition
        for condition in basis["conditions"]
        if condition["condition_index"] in (2, 4)
    ]
    evidence = [
        immutable_evidence(T85, t85, conditions[0]),
        immutable_evidence(T86, t86, conditions[1]),
    ]
    half = t87["policies"]["right_smoothed_half"]["wrapped"]
    final = t87["policies"]["right_smoothed_final"]["wrapped"]
    policy = {
        **half,
        "checkpoint_id": "T87_RIGHT_SMOOTHED_HALF",
        "step": 1_003_520,
    }

    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            conditions,
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
        "t87_result": T87,
        "t85_result": T85,
        "t86_result": T86,
        "r2_basis": R2_BASIS,
    }
    checks = {
        "t87_transform_green": (
            t87["status"] == "PASS_T87_RIGHT_SMOOTHED_ADAPTER_PAIR"
            and t87["failed_checks"] == []
        ),
        "exact_nominal_and_failed_conditions": (
            [item["condition_index"] for item in conditions] == [2, 4]
            and [item["id"] for item in conditions]
            == ["FLOOR_FRICTION_HI", "JOINT_FRICTIONLOSS_HI"]
        ),
        "exact_sixteen_new_cells": len(plan) == 16,
        "immutable_final_evidence_is_two_green_eight_cell_blocks": (
            len(evidence) == 2
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
                for item in evidence
            )
        ),
        "immutable_final_policy_sha_exact": (
            final["sha256"]
            == next(
                item["sha256"]
                for item in basis["policies"]
                if item["checkpoint_id"] == "T84_ROLLING_FINAL"
            )
        ),
        "all_assets_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in [
                policy,
                final,
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
            "open_duck.t88_right_smoothed_targeted_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T88_RIGHT_SMOOTHED_TARGETED_BEHAVIOR"
            if not failed
            else "HOLD_T88_RIGHT_SMOOTHED_TARGETED_PREREGISTRATION"
        ),
        "question": (
            "Does the changed T87 half retain nominal behavior and repair "
            "the exact joint-friction-high failure while the byte-exact "
            "final retains its already audited cells?"
        ),
        "policies": [policy],
        "terminal_final_policy": {
            **final,
            "checkpoint_id": "T87_RIGHT_SMOOTHED_FINAL",
            "byte_exact_to_t84_rolling_final": True,
        },
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "conditions": conditions,
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "immutable_terminal_evidence": evidence,
        "matrix": {
            "changed_policies": 1,
            "immutable_policies": 1,
            "conditions": 2,
            "fits": 2,
            "commands": 4,
            "new_cells_per_condition": 8,
            "maximum_new_cells": 16,
            "combined_cells_per_condition": 16,
            "combined_cells": 32,
            "plan_sha256": hashlib.sha256(
                json.dumps(
                    plan,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
            "condition_order": [2, 4],
            "complete_each_condition_before_decision": True,
            "stop_after_first_failed_condition": True,
            "no_new_final_cells": True,
            "no_checkpoint_selection": True,
        },
        "decision_rule": {
            "pass": (
                "The changed half passes all 16 new cells and combines "
                "with 16 hash-verified immutable final cells for 32/32."
            ),
            "pass_decision": (
                "EARN_T89_RIGHT_SMOOTHED_PAIR_FULL_R2_"
                "REVALIDATION_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_RIGHT_SMOOTHED_ADAPTER_PAIR",
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
            "one_targeted_cpu_matrix": not failed,
            "full_r2_preregistration": False,
            "training": False,
            "colab": False,
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
                "# T88 right-smoothed targeted behavior preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- New cells: `16` (changed half only)",
                "- Immutable final cells: `16` from exact T85/T86 receipts",
                "- Conditions: nominal `2`, failed `4`",
                "- Pass: combined `32/32`; no retry",
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
