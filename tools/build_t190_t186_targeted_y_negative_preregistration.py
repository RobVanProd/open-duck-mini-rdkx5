#!/usr/bin/env python3
"""Freeze T186's exact 16-cell Y-negative persistence matrix."""

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


T188 = ANALYSIS / "t188_t186_postexport_composition_result.json"
T188B = ANALYSIS / "t188b_step_zero_binding_recovery_result.json"
T189 = ANALYSIS / "t189_t186_nominal_matrix_result.json"
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = ANALYSIS / "t190_t186_targeted_y_negative_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T190_T186_TARGETED_Y_NEGATIVE_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t190_t186_targeted_y_negative.py"
TEST = ROOT / "tests" / "test_t190_t186_targeted_y_negative.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T190: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T190 preregistration requires clean worktree")

    t188 = json.loads(T188.read_text(encoding="utf-8"))
    t188b = json.loads(T188B.read_text(encoding="utf-8"))
    t189 = json.loads(T189.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t188["graphs"]
    }
    policies = [
        {
            "checkpoint_id": f"T186_COMPOSED_{label}",
            "step": step,
            **graph_by_step[step],
        }
        for label, step in (
            ("HALF", 1_003_520),
            ("FINAL", 2_007_040),
        )
    ]
    condition = next(
        row for row in basis["conditions"] if row["id"] == "TORSO_COM_Y_NEG"
    )
    checks = {
        "t189_nominal_matrix_green": (
            t189["status"] == "PASS_T189_T186_NOMINAL_MATRIX"
            and t189["condition"]["condition_green"]
            and t189["condition"]["green_cells"] == 16
            and t189["decision"]
            == (
                "EARN_T190_T186_TARGETED_Y_NEGATIVE_MATRIX_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "t188b_composition_recovery_green": (
            t188b["status"] == "PASS_T188B_STEP_ZERO_BINDING_RECOVERY"
            and not t188b["failed_checks"]
        ),
        "t188_all_substantive_composition_checks_green": all(
            passed
            for name, passed in t188["checks"].items()
            if name != "step_zero_model_byte_exact_to_t164_final"
        ),
        "policies_match_t188": (
            len(policies) == 2
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "basis_is_green_frozen_matrix_contract": (
            basis["status"] == "PREREGISTERED_T165_COMPOSED_FULL_R2"
            and not basis["failed_checks"]
            and basis["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
        ),
        "condition_is_exact_y_negative": (
            condition["condition_index"] == 9
            and condition["override"]
            == {"torso_com_offset_m": [0.0, -0.05, 0.0]}
        ),
        "both_checkpoints_required": True,
        "fresh_cache_required": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T190 preregistration checks failed: {failed}")

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
            "open_duck.t190_t186_targeted_y_negative_preregistration.v1"
        ),
        "status": "PREREGISTERED_T190_T186_TARGETED_Y_NEGATIVE",
        **copied,
        "condition": condition,
        "policies": policies,
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
                "EARN_T191_T186_FULL_R2_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T186_SINGLE_SUPPORT_CONTINUATION",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t188_composition": T188,
                "t188b_recovery": T188B,
                "t189_nominal_result": T189,
                "t165_matrix_basis": BASIS,
            }.items()
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
            "one_cpu_y_negative_matrix": True,
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
        "# T190 T186 targeted Y-negative preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: exact torso COM y = `-0.05 m`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Fresh cache; both checkpoints mandatory; no retry\n"
        "- Training / Colab / robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
