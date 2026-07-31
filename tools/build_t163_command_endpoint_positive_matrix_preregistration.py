#!/usr/bin/env python3
"""Freeze T162's exact 16-cell positive-COM behavior matrix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T160 = ANALYSIS / "t160_mechanics_positive_endpoint_result.json"
T161 = ANALYSIS / "t161_command_endpoint_replay_autopsy.json"
T162 = ANALYSIS / "t162_exact_command_endpoint_transform_result.json"
BASIS = ANALYSIS / "t145_conditional_path_negative_endpoint_preregistration.json"
OUTPUT = ANALYSIS / "t163_command_endpoint_positive_matrix_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T163_COMMAND_ENDPOINT_POSITIVE_MATRIX_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t163_command_endpoint_positive_matrix.py"
TEST = ROOT / "tests" / "test_t163_command_endpoint_positive_matrix.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T163: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T163 preregistration requires clean worktree")
    t160 = json.loads(T160.read_text(encoding="utf-8"))
    t161 = json.loads(T161.read_text(encoding="utf-8"))
    t162 = json.loads(T162.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    graph_by_step = {
        str(row["step"]): row["structure"]["transformed"]
        for row in t162["graphs"]
    }
    policies = [
        {
            "checkpoint_id": f"T162_ENDPOINT_{label}",
            "step": int(step),
            **graph_by_step[step],
        }
        for label, step in (("HALF", "1003520"), ("FINAL", "2007040"))
    ]
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t160_endpoint_hold": T160,
        "t161_replay_autopsy": T161,
        "t162_graph_contract": T162,
        "endpoint_basis": BASIS,
    }
    checks = {
        "t160_mechanics_endpoint_is_frozen_hold": (
            t160["status"] == "HOLD_T160_MECHANICS_POSITIVE_ENDPOINT"
            and t160["condition"]["green_cells"] == 10
        ),
        "t161_algebraic_screen_green": (
            t161["status"]
            == "PASS_T161_COMMAND_ENDPOINT_REPLAY_AUTOPSY"
            and not t161["failed_checks"]
        ),
        "t162_exact_graph_contract_green": (
            t162["status"]
            == "PASS_T162_EXACT_COMMAND_ENDPOINT_TRANSFORM"
            and not t162["failed_checks"]
            and all(t162["checks"].values())
        ),
        "policies_match_t162": (
            len(policies) == 2
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "basis_is_compatible_endpoint_matrix": (
            basis["status"]
            == "PREREGISTERED_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
            and basis["matrix"]["cells"] == 16
            and basis["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
        ),
        "reference_slot_stays_external": True,
        "fresh_cache_required": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T163 preregistration checks failed: {failed}")
    copied = {
        name: basis[name]
        for name in (
            "fits",
            "calibrator",
            "reference_feature_table",
            "playground",
            "commands_x_m_s",
            "seed",
            "support_handoff",
            "behavior_contract",
            "protection_contract",
            "repository_inputs",
        )
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t163_command_endpoint_positive_matrix_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T163_COMMAND_ENDPOINT_POSITIVE_MATRIX"
        ),
        **copied,
        "condition": {
            "condition_index": 8,
            "id": "TORSO_COM_X_POS",
            "override": {"torso_com_offset_m": [0.05, 0.0, 0.0]},
        },
        "policies": policies,
        "reference_slot": {
            "external_command_reference_preserved": True,
            "actor_command_coordinate_rewritten_only": True,
            "reason": (
                "T162 proved graph-coordinate exactness, not full endpoint "
                "trajectory replay. T163 is the direct behavior falsifier."
            ),
        },
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells": 16,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "fresh_cache": True,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T164_COMMAND_ENDPOINT_FULL_R2_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_COMMAND_ENDPOINT_REPLAY_REPAIR",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_positive_matrix": True,
            "full_r2": False,
            "training": False,
            "colab": False,
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
        "# T163 command-endpoint positive matrix preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: exact torso COM x = `+0.05 m`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Fresh cache; both checkpoints mandatory; no retry\n"
        "- External reference-action slot remains command-faithful\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
