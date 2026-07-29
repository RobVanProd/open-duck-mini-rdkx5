#!/usr/bin/env python3
"""Freeze T149B's exact 16-cell negative-COM endpoint matrix."""

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


T149B = ANALYSIS / "t149b_negative_context_command_plateau_result.json"
BASIS = ANALYSIS / "t145_conditional_path_negative_endpoint_preregistration.json"
OUTPUT = ANALYSIS / "t150_negative_command_plateau_endpoint_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T150_NEGATIVE_COMMAND_PLATEAU_ENDPOINT_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t150_negative_command_plateau_endpoint.py"
TEST = ROOT / "tests/test_t150_negative_command_plateau_endpoint.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T150: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T150 preregistration requires clean worktree")
    t149 = json.loads(T149B.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": f"T149B_NEGATIVE_PLATEAU_{label}",
            "step": int(step),
            **t149["transforms"][step]["transformed"],
        }
        for label, step in (("HALF", "1003520"), ("FINAL", "2007040"))
    ]
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t149b_transform": T149B,
        "negative_basis": BASIS,
    }
    checks = {
        "t149b_transform_green": (
            t149["status"]
            == "PASS_T149B_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
            and t149["failed_checks"] == []
            and t149["decision"]
            == (
                "EARN_T150_NEGATIVE_COMMAND_PLATEAU_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "policies_match_t149b": all(
            {key: item[key] for key in ("path", "bytes", "sha256")}
            == t149["transforms"][str(item["step"])]["transformed"]
            for item in policies
        ),
        "basis_is_exact_negative_com": (
            basis["status"]
            == "PREREGISTERED_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
            and basis["condition"]
            == {
                "condition_index": 7,
                "id": "TORSO_COM_X_NEG",
                "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
            }
            and basis["matrix"]["cells"] == 16
        ),
        "nominal_identity_inherited_from_t149b": all(
            contract["all_rows_bit_exact"]
            and contract["all_chains_bit_exact"]
            for contract in t149["contracts"].values()
        ),
        "repository_inputs_present": all(
            Path(item["path"]).is_file()
            for item in basis["repository_inputs"].values()
        ),
        "frozen_inputs_present": all(path.is_file() for path in frozen.values()),
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T150 preregistration checks failed: {failed}")
    copied = {
        name: basis[name]
        for name in (
            "condition",
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
            "open_duck.t150_negative_command_plateau_endpoint_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T150_NEGATIVE_COMMAND_PLATEAU_ENDPOINT"
        ),
        **copied,
        "policies": policies,
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells": 16,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T151_COMMAND_PLATEAU_FULL_R2_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_NEGATIVE_CONTEXT_COMMAND_PLATEAU",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {name: receipt(path) for name, path in frozen.items()},
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_cpu_negative_endpoint_matrix": True,
            "full_r2_preregistration": False,
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
        "# T150 negative-command plateau endpoint preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: exact torso COM x = `-0.05 m`\n"
        "- Matrix: `2 checkpoints × 2 fits × 4 commands = 16`\n"
        "- Nominal identity inherited from T149B exact graph proof\n"
        "- Both checkpoints mandatory; no retry\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
