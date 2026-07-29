#!/usr/bin/env python3
"""Freeze T139's exact 16-cell negative-COM endpoint matrix."""

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


T140 = ANALYSIS / "t140_nominal_identity_reuse_result.json"
T139 = ANALYSIS / "t139_context_selected_expert_bank_result.json"
BASIS = ANALYSIS / "t103_t100c_negative_endpoint_preregistration.json"
OUTPUT = (
    ANALYSIS / "t141_expert_bank_negative_endpoint_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T141_EXPERT_BANK_NEGATIVE_ENDPOINT_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t141_expert_bank_negative_endpoint.py"
TEST = ROOT / "tests" / "test_t141_expert_bank_negative_endpoint.py"
GRAPH_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t139_context_selected_expert_bank_v1"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T141: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T141 preregistration requires clean worktree")
    t140 = json.loads(T140.read_text(encoding="utf-8"))
    t139 = json.loads(T139.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": f"T139_EXPERT_BANK_{label}",
            "step": int(step),
            **receipt(
                GRAPH_ROOT / step / "context_selected_expert_bank.onnx"
            ),
        }
        for label, step in (
            ("HALF", "1003520"),
            ("FINAL", "2007040"),
        )
    ]
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t140_nominal_identity": T140,
        "t139_transform": T139,
        "negative_basis": BASIS,
    }
    checks = {
        "t140_nominal_identity_green": (
            t140["status"] == "PASS_T140_NOMINAL_IDENTITY_REUSE"
            and t140["failed_checks"] == []
            and t140["decision"]
            == "EARN_T141_EXPERT_BANK_NEGATIVE_ENDPOINT_"
            "PREREGISTRATION_ONLY"
        ),
        "t139_transform_green": (
            t139["status"]
            == "PASS_T139_CONTEXT_SELECTED_EXPERT_BANK_TRANSFORM"
            and t139["failed_checks"] == []
        ),
        "policies_match_t139": all(
            {
                key: item[key] for key in ("path", "bytes", "sha256")
            }
            == t139["graphs"][str(item["step"])]["transformed"]
            for item in policies
        ),
        "basis_is_exact_negative_com": (
            basis["status"]
            == "PREREGISTERED_T103_T100C_NEGATIVE_ENDPOINT_MATRIX"
            and basis["condition"]
            == {
                "condition_index": 7,
                "id": "TORSO_COM_X_NEG",
                "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
            }
            and basis["matrix"]["cells"] == 16
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T141 preregistration checks failed: {failed}")
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
        )
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t141_expert_bank_negative_endpoint_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T141_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX"
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
                "EARN_T142_EXPERT_BANK_FULL_R2_REVALIDATION_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_CONTEXT_SELECTED_EXPERT_BANK",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
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
        "# T141 expert-bank negative endpoint preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: exact torso COM x = `-0.05 m`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
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
