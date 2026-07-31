#!/usr/bin/env python3
"""Run T114C's read-only protobuf field-presence recovery."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import onnx


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import build_t112_always_on_trainthrough_preregistration as common  # noqa: E402
import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402


PREREG = ANALYSIS / "t114c_protobuf_presence_recovery_preregistration.json"
OUTPUT = ANALYSIS / "t114c_protobuf_presence_recovery_result.json"
MARKDOWN = ANALYSIS / "T114C_PROTOBUF_PRESENCE_RECOVERY_RESULT_20260729.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-recovery", action="store_true")
    args = parser.parse_args()
    if not args.read_only_recovery:
        raise PermissionError("T114C requires --read-only-recovery")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T114C result: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T114C recovery requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T114C_PROTOBUF_PRESENCE_RECOVERY"
        or prereg["failed_checks"]
        or common.canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T114C preregistration identity changed")
    for name, item in prereg["sources"].items():
        t20.verify_receipt(item, name)
    for name, item in prereg["assets"].items():
        t20.verify_receipt(item, name)

    expected_path = Path(prereg["assets"]["expected_transform"]["path"])
    cpu_path = Path(prereg["assets"]["cpu_step_zero_export"]["path"])
    hosted_path = Path(prereg["assets"]["hosted_step_zero_export"]["path"])
    expected = onnx.load(expected_path)
    hosted = onnx.load(hosted_path)
    normalized = copy.deepcopy(expected)
    normalized.graph.node[27].ClearField("name")
    chain = t98.compare_random_chain(expected_path, hosted_path, steps=256)
    checks = {
        "cpu_and_hosted_export_byte_exact": (
            common.sha256(cpu_path) == common.sha256(hosted_path)
        ),
        "clearfield_makes_protobuf_byte_exact": (
            normalized.SerializeToString() == hosted.SerializeToString()
        ),
        "random_recurrent_chain_bit_exact": (
            chain["steps"] == 256
            and chain["bit_exact_steps"] == 256
            and chain["maximum_abs_error"] == 0.0
        ),
        "no_optimizer_behavior_hosted_or_hardware": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": "open_duck.t114c_protobuf_presence_recovery_result.v1",
        "status": (
            "PASS_T114C_PROTOBUF_PRESENCE_RECOVERY"
            if passed
            else "HOLD_T114C_PROTOBUF_PRESENCE_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "classification": (
            "PROTOBUF_FIELD_PRESENCE_ONLY_T113_VALIDATED"
            if passed
            else "UNRESOLVED_PROTOBUF_DIFFERENCE"
        ),
        "hashes": {
            "expected_transform": common.sha256(expected_path),
            "cpu_step_zero_export": common.sha256(cpu_path),
            "hosted_step_zero_export": common.sha256(hosted_path),
        },
        "random_chain": chain,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "nominal_preregistration_authorized": passed,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = common.canonical_sha256(result)
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T114C protobuf presence recovery result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Classification: `{result['classification']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Random recurrent chain exact: "
                    f"`{chain['bit_exact_steps']}/{chain['steps']}`"
                ),
                "- Optimizer / behavior / hosted / robot: 0 / 0 / 0 / 0",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
