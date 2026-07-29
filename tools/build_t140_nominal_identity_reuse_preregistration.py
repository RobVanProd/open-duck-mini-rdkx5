#!/usr/bin/env python3
"""Freeze evidence reuse for T139's exact T100C nominal branch."""

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


T139 = ANALYSIS / "t139_context_selected_expert_bank_result.json"
T102 = ANALYSIS / "t102_t100c_nominal_matrix_result.json"
T102_PREREG = ANALYSIS / "t102_t100c_nominal_matrix_preregistration.json"
OUTPUT = ANALYSIS / "t140_nominal_identity_reuse_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T140_NOMINAL_IDENTITY_REUSE_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t140_nominal_identity_reuse.py"
TEST = ROOT / "tests" / "test_t140_nominal_identity_reuse.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T140: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T140 preregistration requires clean worktree")
    t139 = json.loads(T139.read_text(encoding="utf-8"))
    t102 = json.loads(T102.read_text(encoding="utf-8"))
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t139_result": T139,
        "t102_result": T102,
        "t102_prereg": T102_PREREG,
    }
    checks = {
        "t139_selects_nominal_identity_reuse": (
            t139["status"]
            == "PASS_T139_CONTEXT_SELECTED_EXPERT_BANK_TRANSFORM"
            and t139["failed_checks"] == []
            and t139["decision"]
            == "EARN_T140_NOMINAL_IDENTITY_REUSE_PREREGISTRATION_ONLY"
        ),
        "t102_nominal_green": (
            t102["status"] == "PASS_T102_T100C_NOMINAL_MATRIX"
            and t102["condition"]["green_cells"] == 16
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "no_new_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T140 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t140_nominal_identity_reuse_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T140_NOMINAL_IDENTITY_REUSE",
        "question": (
            "Can T102's 16/16 nominal evidence be inherited without "
            "rerunning behavior because T139 is structurally and "
            "bit-exactly T100C for both nominal calibration contexts?"
        ),
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T141_EXPERT_BANK_NEGATIVE_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "REQUIRE_FRESH_NOMINAL_MATRIX",
        },
        "execution_now": {
            "inherited_behavior_cells": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_identity_reuse_audit": True,
            "negative_endpoint_preregistration": False,
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
        "# T140 nominal identity reuse preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Reuse only if T139 nominal branch is exact T100C\n"
        "- T102 source matrix is frozen 16/16\n"
        "- New behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
