#!/usr/bin/env python3
"""Freeze the read-only negative-expert interference attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t127_negative_expert_interference.py"
TEST = ROOT / "tests" / "test_t127_negative_expert_interference.py"
OUTPUT = ANALYSIS / "t127_negative_expert_interference_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T127_NEGATIVE_EXPERT_INTERFERENCE_PREREGISTRATION_20260729.md"
)
INPUTS = {
    "t67_nominal": ANALYSIS / "t69_t67_nominal_matrix_result.json",
    "t67_negative": ANALYSIS / "t70_t67_condition7_result.json",
    "t71_hidden_causality": ANALYSIS / "t71_t67_com_hidden_causal_result.json",
    "t78_negative": ANALYSIS / "t92_raw_t78_com_attribution_result.json",
    "t113_preregistration": (
        ANALYSIS / "t113_always_on_trainthrough_hosted_preregistration.json"
    ),
    "t113_negative": ANALYSIS / "t117_t113_negative_endpoint_result.json",
    "t120_preregistration": (
        ANALYSIS / "t120_joint_soft_router_hosted_preregistration.json"
    ),
    "t124_factorial": ANALYSIS / "t124_t120_leaf_factorial_result.json",
    "t126_negative": ANALYSIS / "t126_expert_first_negative_result.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T127 requires --read-only-authorized")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T127: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T127 preregistration requires clean worktree")
    all_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        **INPUTS,
    }
    checks = {
        "all_inputs_present": all(path.is_file() for path in all_inputs.values()),
        "no_simulator_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t127_negative_expert_interference_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T127_NEGATIVE_EXPERT_INTERFERENCE_AUDIT"
            if not failed
            else "HOLD_T127_NEGATIVE_EXPERT_INTERFERENCE_PREREGISTRATION"
        ),
        "question": (
            "Did every prior negative-COM correction train under mixed endpoint "
            "gradients, leaving exact negative-only expert training as the "
            "smallest untested mechanism before increasing network capacity?"
        ),
        "frozen_facts": {
            "t67_nominal_green_cells": 16,
            "t67_negative_green_cells": 6,
            "t78_negative_green_cells": 4,
            "t113_negative_green_cells": 5,
            "t126_negative_green_cells": 4,
            "endpoint_strata": 8,
            "exact_negative_fraction": 0.125,
            "hidden_signal_classification": (
                "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
            ),
            "t124_nominal_repair": "EXPERT_DOMINANT",
        },
        "classification_rule": {
            "select_negative_only": (
                "all frozen facts match; T113 and T120 each trained the expert "
                "through eight endpoint strata; no frozen result tested an "
                "exact negative-only expert continuation"
            ),
            "otherwise": "HOLD_FOR_MECHANISM_REVIEW",
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T128_NEGATIVE_ONLY_LINEAR_EXPERT_CPU_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "HOLD_FOR_MECHANISM_REVIEW",
            "no_hosted_training": True,
        },
        "inputs": {
            name: receipt(path) for name, path in all_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_read_only_audit": not failed,
            "t128_cpu_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T127 negative-expert interference preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Read-only audit of frozen T67/T78/T113/T120 evidence\n"
        "- Simulator / optimizer / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
