#!/usr/bin/env python3
"""Run frozen T130D attribution of T129's optional ONNX node-name delta."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import onnx
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402
import run_t112_always_on_trainthrough_cpu_contract as t112  # noqa: E402


PREREG = ANALYSIS / "t130d_step_zero_node_name_preregistration.json"
RESULT = ANALYSIS / "t130d_step_zero_node_name_result.json"
MARKDOWN = ANALYSIS / "T130D_STEP_ZERO_NODE_NAME_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t130d_step_zero_node_name_recovery"
)


def verify_file_receipt(item: dict[str, Any], name: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(item["bytes"])
        or t20.sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"T130D frozen input changed: {name}={path}")


def abi(path: Path) -> dict[str, dict[str, list[int]]]:
    session = ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )
    return {
        "inputs": {
            item.name: list(item.shape) for item in session.get_inputs()
        },
        "outputs": {
            item.name: list(item.shape) for item in session.get_outputs()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T130D requires --read-only-authorized")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T130D: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T130D execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T130D_STEP_ZERO_NODE_NAME_RECOVERY"
        or prereg["failed_checks"]
        or t20.canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T130D preregistration changed")
    for name, item in prereg["sources"].items():
        verify_file_receipt(item, name)
    for name, item in prereg["policies"].items():
        verify_file_receipt(item, name)

    expected_path = Path(prereg["policies"]["expected_transform"]["path"])
    cpu_path = Path(prereg["policies"]["cpu_exporter_step_zero"]["path"])
    hosted_path = Path(prereg["policies"]["hosted_step_zero"]["path"])
    expected = onnx.load(expected_path)
    hosted = onnx.load(hosted_path)
    frozen = prereg["expected_difference"]

    initializer_equal = (
        len(expected.graph.initializer) == len(hosted.graph.initializer)
        and all(
            left.SerializeToString() == right.SerializeToString()
            for left, right in zip(
                expected.graph.initializer,
                hosted.graph.initializer,
                strict=True,
            )
        )
    )
    node_diff_indices = [
        index
        for index, (left, right) in enumerate(
            zip(expected.graph.node, hosted.graph.node, strict=True)
        )
        if left.SerializeToString() != right.SerializeToString()
    ]
    target_index = frozen["node_index"]
    left_node = expected.graph.node[target_index]
    right_node = hosted.graph.node[target_index]
    normalized = onnx.ModelProto()
    normalized.CopyFrom(expected)
    normalized.graph.node[target_index].ClearField("name")

    WORK.mkdir(parents=True)
    t112.INSPECTION = WORK / "inspection"
    cases = t98.trace_cases(
        {
            "assets": {
                "t97_preregistration": prereg["sources"][
                    "trace_population"
                ]
            }
        }
    )
    trace = t112.trace_equivalence(expected_path, hosted_path, cases)
    chain = t98.compare_random_chain(expected_path, hosted_path)
    expected_abi = abi(expected_path)
    cpu_abi = abi(cpu_path)
    hosted_abi = abi(hosted_path)
    facts = {
        "hosted_cpu_exporter_byte_exact": (
            hosted_path.read_bytes() == cpu_path.read_bytes()
        ),
        "source_bytes": {
            "expected": expected_path.stat().st_size,
            "hosted": hosted_path.stat().st_size,
            "difference": (
                expected_path.stat().st_size - hosted_path.stat().st_size
            ),
        },
        "initializer_count": {
            "expected": len(expected.graph.initializer),
            "hosted": len(hosted.graph.initializer),
        },
        "initializers_bit_exact": initializer_equal,
        "node_count": {
            "expected": len(expected.graph.node),
            "hosted": len(hosted.graph.node),
        },
        "node_diff_indices": node_diff_indices,
        "differing_node": {
            "index": target_index,
            "expected_name": left_node.name,
            "hosted_name": right_node.name,
            "op_type": left_node.op_type,
            "inputs": list(left_node.input),
            "outputs": list(left_node.output),
            "all_fields_except_name_exact": (
                list(left_node.input) == list(right_node.input)
                and list(left_node.output) == list(right_node.output)
                and left_node.op_type == right_node.op_type
                and left_node.domain == right_node.domain
                and list(left_node.attribute) == list(right_node.attribute)
                and left_node.doc_string == right_node.doc_string
                and left_node.overload == right_node.overload
            ),
        },
        "complete_model_byte_exact_after_clearing_optional_name": (
            normalized.SerializeToString() == hosted.SerializeToString()
        ),
        "abi": {
            "expected": expected_abi,
            "cpu_exporter": cpu_abi,
            "hosted": hosted_abi,
        },
        "trace": trace,
        "random_chain": chain,
    }
    checks = {
        "hosted_matches_cpu_exporter_byte_exact": facts[
            "hosted_cpu_exporter_byte_exact"
        ],
        "all_initializers_bit_exact": (
            facts["initializer_count"]
            == {"expected": 27, "hosted": 27}
            and facts["initializers_bit_exact"]
        ),
        "only_preregistered_node_diff": (
            facts["node_count"] == {"expected": 37, "hosted": 37}
            and facts["node_diff_indices"] == [target_index]
            and facts["differing_node"]
            == {
                "index": target_index,
                "expected_name": frozen["expected_name"],
                "hosted_name": frozen["hosted_name"],
                "op_type": frozen["op_type"],
                "inputs": frozen["inputs"],
                "outputs": frozen["outputs"],
                "all_fields_except_name_exact": True,
            }
        ),
        "complete_model_exact_after_optional_name_clear": facts[
            "complete_model_byte_exact_after_clearing_optional_name"
        ],
        "abi_bit_exact": (
            expected_abi == cpu_abi == hosted_abi
            and expected_abi["inputs"]
            == {
                "obs": [1, 115],
                "previous_action": [1, 14],
                "h_in": [1, 64],
            }
            and expected_abi["outputs"]
            == {
                "continuous_actions": [1, 14],
                "previous_action_out": [1, 14],
                "h_out": [1, 64],
            }
        ),
        "trace_rows_bit_exact": (
            trace["rows"] == frozen["trace_rows_bit_exact"]
            and trace["bit_exact_rows"] == trace["rows"]
            and trace["maximum_abs_error"] == 0.0
            and trace["always_on_identity_rows"] == trace["rows"]
        ),
        "random_chain_bit_exact": (
            chain["steps"] == frozen["random_chain_steps_bit_exact"]
            and chain["bit_exact_steps"] == chain["steps"]
            and chain["maximum_abs_error"] == 0.0
        ),
        "no_optimizer_behavior_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t130d_step_zero_node_name_result.v1"
        ),
        "status": (
            "PASS_T130D_STEP_ZERO_NODE_NAME_RECOVERY"
            if passed
            else "HOLD_T130D_STEP_ZERO_NODE_NAME_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "classification": (
            "OPTIONAL_ONNX_NODE_NAME_METADATA_ONLY"
            if passed
            else "UNRESOLVED_STEP_ZERO_MISMATCH"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "facts": facts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "postexport_preregistration": passed,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T130D step-zero node-name result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        "- Trace / recurrent chain exact: "
        f"`{trace['bit_exact_rows']}/{trace['rows']} / "
        f"{chain['bit_exact_steps']}/{chain['steps']}`\n"
        "- Optimizer / behavior / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
