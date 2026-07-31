#!/usr/bin/env python3
"""Recover T247's reporting checks without new inference or simulation."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
from typing import Any

import onnx

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    sha256,
)


PREREG = ANALYSIS / "t247b_reporting_recovery_preregistration.json"
RESULT = ANALYSIS / "t247b_reporting_recovery_result.json"
MARKDOWN = ANALYSIS / "T247B_REPORTING_RECOVERY_RESULT_20260731.md"
TARGET_OUTPUT = ("nominal_dynamic_conditional_adapter",)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T247B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T247B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T247B_REPORTING_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T247B preregistration changed")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256(path) != item["sha256"]
        ):
            raise RuntimeError(f"changed T247B input: {path}")
    source = json.loads(
        Path(prereg["frozen_inputs"]["t247_result"]["path"])
        .read_text(encoding="utf-8")
    )

    structural_rows = []
    for graph in source["graphs"]:
        before = onnx.load(graph["structure"]["source"]["path"])
        after = onnx.load(graph["structure"]["transformed"]["path"])
        before_nodes = {
            tuple(node.output): node for node in before.graph.node
        }
        after_nodes = {
            tuple(node.output): node for node in after.graph.node
        }
        old_outputs = set(before_nodes)
        added_outputs = set(after_nodes) - old_outputs
        changed_outputs = []
        for outputs in old_outputs:
            expected = before_nodes[outputs]
            if outputs == TARGET_OUTPUT:
                expected = copy.deepcopy(expected)
                expected.input[1] = (
                    "t247_home_negative_selected_adapter_location"
                )
            if (
                expected.SerializeToString()
                != after_nodes[outputs].SerializeToString()
            ):
                changed_outputs.append(list(outputs))
        structural_rows.append(
            {
                "role": graph["role"],
                "source_target_name_is_empty": (
                    before_nodes[TARGET_OUTPUT].name == ""
                ),
                "source_target_input": before_nodes[TARGET_OUTPUT].input[1],
                "transformed_target_input": after_nodes[TARGET_OUTPUT].input[
                    1
                ],
                "added_outputs": sorted(
                    [list(outputs) for outputs in added_outputs]
                ),
                "unexpected_changed_old_outputs": changed_outputs,
                "all_old_outputs_present": old_outputs.issubset(
                    set(after_nodes)
                ),
            }
        )

    trace = source["failed_final_trace_contract"]
    checks = {
        "target_is_unnamed_where_in_both_sources": all(
            row["source_target_name_is_empty"] for row in structural_rows
        ),
        "only_target_input_rewired_exactly": all(
            row["source_target_input"]
            == "t234_command_selected_adapter_location"
            and row["transformed_target_input"]
            == "t247_home_negative_selected_adapter_location"
            and not row["unexpected_changed_old_outputs"]
            and row["all_old_outputs_present"]
            for row in structural_rows
        ),
        "only_two_expected_new_outputs": all(
            row["added_outputs"]
            == [
                ["t247_home_negative_half_adapter_location"],
                ["t247_home_negative_selected_adapter_location"],
            ]
            for row in structural_rows
        ),
        "random_mapping_equivalence_and_finiteness_green": all(
            graph["inference"]["all_outputs_bit_exact"]
            and graph["inference"]["all_non_tail_exact_source"]
            and graph["inference"]["all_tail_exact_half_source"]
            and graph["inference"]["all_outputs_finite"]
            for graph in source["graphs"]
        ),
        "real_failed_trace_sensitive_and_exact": (
            trace["rows"] == 231
            and trace["source_replay_exact"]
            and trace["transformed_exact_half_source"]
            and trace["continuous_action_changed_rows"] == 24
            and trace["maximum_continuous_action_delta"] > 0.0
        ),
        "all_other_original_contract_checks_green": all(
            passed
            for name, passed in source["checks"].items()
            if name
            not in {
                "only_nominal_dynamic_input_changed",
                "random_contract_exact",
            }
        ),
        "zero_new_inference_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis_result: dict[str, Any] = {
        "schema_version": "open_duck.t247b_reporting_recovery_result.v1",
        "status": (
            "PASS_T247B_REPORTING_RECOVERY"
            if passed
            else "HOLD_T247B_REPORTING_RECOVERY"
        ),
        "decision": (
            "EARN_T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX_"
            "PREREGISTRATION_ONLY"
            if passed
            else "CLOSE_HOME_NEGATIVE_HALF_ADAPTER_ROUTE_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "structural_rows": structural_rows,
        "classification": {
            "unnamed_node_check": (
                "recovered by unique output-tuple comparison"
            ),
            "random_sensitivity_check": (
                "reporting-only; exact mapping is green and the real "
                "failed trace changes 24 actions"
            ),
            "selection_weight": 0,
        },
        "execution": {
            "onnx_inferences": 0,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "behavior_matrix_preregistration": passed,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T247B reporting recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Real failed-trace changed rows: `24/231`\n"
        "- New inference/behavior/optimizer/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
