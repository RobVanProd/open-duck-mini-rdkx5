#!/usr/bin/env python3
"""Run T114B's read-only ONNX step-zero attribution."""

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
import run_t109_always_on_expert_transform as t109  # noqa: E402


PREREG = ANALYSIS / "t114b_step_zero_attribution_preregistration.json"
OUTPUT = ANALYSIS / "t114b_step_zero_attribution_result.json"
MARKDOWN = ANALYSIS / "T114B_STEP_ZERO_ATTRIBUTION_RESULT_20260729.md"


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T114B_STEP_ZERO_READ_ONLY_ATTRIBUTION"
        or value.get("failed_checks")
        or common.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T114B preregistration identity changed")
    for name, item in value["sources"].items():
        t20.verify_receipt(item, name)
    for name, item in value["assets"].items():
        t20.verify_receipt(item, name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-attribution", action="store_true")
    args = parser.parse_args()
    if not args.read_only_attribution:
        raise PermissionError("T114B requires --read-only-attribution")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T114B result: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T114B execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    expected_path = Path(prereg["assets"]["expected_transform"]["path"])
    cpu_path = Path(prereg["assets"]["cpu_step_zero_export"]["path"])
    hosted_path = Path(prereg["assets"]["hosted_step_zero_export"]["path"])
    expected = onnx.load(expected_path)
    hosted = onnx.load(hosted_path)
    differing_nodes = [
        index
        for index, (left, right) in enumerate(
            zip(expected.graph.node, hosted.graph.node, strict=True)
        )
        if left.SerializeToString() != right.SerializeToString()
    ]
    normalized = copy.deepcopy(expected)
    normalized.graph.node[27].name = ""
    chain = t98.compare_random_chain(expected_path, hosted_path, steps=256)
    checks = {
        "cpu_and_hosted_export_byte_exact": (
            common.sha256(cpu_path) == common.sha256(hosted_path)
        ),
        "node_count_equal": (
            len(expected.graph.node) == len(hosted.graph.node)
        ),
        "abi_equal": t109.graph_abi(expected) == t109.graph_abi(hosted),
        "initializers_equal": (
            t109.initializer_map(expected) == t109.initializer_map(hosted)
        ),
        "only_node_27_differs": differing_nodes == [27],
        "node_27_contract_exact": (
            expected.graph.node[27].op_type == "Identity"
            and hosted.graph.node[27].op_type == "Identity"
            and expected.graph.node[27].name
            == "t109_always_on_negative_adapter"
            and hosted.graph.node[27].name == ""
            and list(expected.graph.node[27].input)
            == list(hosted.graph.node[27].input)
            == ["negative_adapter_location"]
            and list(expected.graph.node[27].output)
            == list(hosted.graph.node[27].output)
            == ["conditional_adapter_location"]
        ),
        "clearing_node_name_makes_protobuf_exact": (
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
        "schema_version": "open_duck.t114b_step_zero_attribution_result.v1",
        "status": (
            "PASS_T114B_STEP_ZERO_READ_ONLY_ATTRIBUTION"
            if passed
            else "HOLD_T114B_STEP_ZERO_READ_ONLY_ATTRIBUTION"
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
            "PROTOBUF_NODE_NAME_ONLY_CPU_HOSTED_EXPORTS_BYTE_EXACT"
            if passed
            else "UNRESOLVED_STEP_ZERO_MISMATCH"
        ),
        "hashes": {
            "expected_transform": common.sha256(expected_path),
            "cpu_step_zero_export": common.sha256(cpu_path),
            "hosted_step_zero_export": common.sha256(hosted_path),
        },
        "node_differences": differing_nodes,
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
                "# T114B step-zero attribution result",
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
