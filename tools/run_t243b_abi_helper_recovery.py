#!/usr/bin/env python3
"""Recover T243 without rewriting its immutable partial half graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping

import onnx


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t243b_abi_helper_recovery_preregistration.json"
RESULT = ANALYSIS / "t243b_abi_helper_recovery_result.json"
MARKDOWN = ANALYSIS / "T243B_ABI_HELPER_RECOVERY_RESULT_20260731.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t243b_abi_helper_recovery_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
import run_t243_home_negative_low_command_floor as t243  # noqa: E402
from run_t136_static_calibration_router_transform import (  # noqa: E402
    abi as model_abi,
    canonical_sha256,
    receipt,
    sha256,
)


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T243B input: {path}")


def structure_from_existing(
    source: Path, transformed: Path
) -> dict[str, Any]:
    before = onnx.load(source)
    after = onnx.load(transformed)
    onnx.checker.check_model(after)
    before_nodes = {
        node.name: node.SerializeToString() for node in before.graph.node
    }
    after_nodes = {
        node.name: node.SerializeToString() for node in after.graph.node
    }
    added = [
        node.name
        for node in after.graph.node
        if node.name not in before_nodes
    ]
    changed = sorted(
        name
        for name, value in before_nodes.items()
        if after_nodes.get(name) != value
    )
    before_initializers = {
        item.name: item.SerializeToString()
        for item in before.graph.initializer
    }
    after_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    return {
        "source": receipt(source),
        "transformed": receipt(transformed),
        "source_abi": model_abi(before),
        "transformed_abi": model_abi(after),
        "added_nodes": added,
        "changed_old_nodes": changed,
        "initializers_byte_exact": (
            before_initializers == after_initializers
        ),
        "initializer_names_exact": (
            set(before_initializers) == set(after_initializers)
        ),
        "onnx_checker_pass": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T243B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T243B execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T243B_ABI_HELPER_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T243B preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    source = json.loads(
        Path(prereg["frozen_inputs"]["t243_preregistration"]["path"])
        .read_text(encoding="utf-8")
    )
    if (
        source["preregistered_contract_sha256"]
        != prereg["source_t243_contract_sha256"]
    ):
        raise RuntimeError("T243 source contract changed")
    for graph in source["graphs"]:
        verify(graph["source"])
    for key in ("failed_trace", "passing_trace"):
        verify(source["causal_evidence"][key])

    partial = Path(
        prereg["frozen_inputs"]["partial_half_graph"]["path"]
    )
    context = next(
        row["context"]
        for row in source["contexts"]
        if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
        and row["fit_id"] == "p30"
    )
    expected_nodes = [
        "t243_home_negative_router_matmul",
        "t243_home_negative_router_add",
        "t243_home_negative_tail_gate",
        "t243_exact_low_command_gate",
        "t243_home_negative_low_command_gate",
        "t243_map_home_negative_low_command",
    ]
    original_abi = t243.abi
    t243.abi = lambda path: model_abi(onnx.load(path))
    outputs = []
    started = time.time()
    try:
        for index, graph in enumerate(source["graphs"]):
            source_path = Path(graph["source"]["path"])
            reused = graph["role"] == "half"
            if reused:
                transformed = partial
                structure = structure_from_existing(
                    source_path, transformed
                )
            else:
                transformed = (
                    WORK
                    / "graphs"
                    / str(graph["step"])
                    / "home_negative_low_command_floor.onnx"
                )
                structure = t243.transform(source_path, transformed)
            inference = t243.random_contract(
                source_path,
                transformed,
                source["contexts"],
                source["contract"]["commands_x_m_s"],
                int(source["contract"]["samples_per_context_command"]),
                int(source["contract"]["random_seed"]) + index,
            )
            trace = (
                t243.trace_contract(
                    source_path,
                    transformed,
                    Path(
                        source["causal_evidence"]["failed_trace"]["path"]
                    ),
                    context,
                    int(source["contract"]["failed_trace_rows"]),
                )
                if reused
                else None
            )
            outputs.append(
                {
                    "step": graph["step"],
                    "role": graph["role"],
                    "reused_partial_graph": reused,
                    "structure": structure,
                    "inference": inference,
                    "failed_trace_contract": trace,
                }
            )
    finally:
        t243.abi = original_abi

    trace_rows = [
        row["failed_trace_contract"]
        for row in outputs
        if row["failed_trace_contract"] is not None
    ]
    checks = {
        "exactly_one_partial_graph_reused": (
            sum(row["reused_partial_graph"] for row in outputs) == 1
            and outputs[0]["reused_partial_graph"]
            and not outputs[1]["reused_partial_graph"]
        ),
        "partial_graph_receipt_unchanged": (
            outputs[0]["structure"]["transformed"]
            == prereg["frozen_inputs"]["partial_half_graph"]
        ),
        "two_complete_graphs": (
            [row["step"] for row in outputs]
            == [1_003_520, 2_007_040]
        ),
        "stateful_abi_exact": all(
            row["structure"]["source_abi"]
            == row["structure"]["transformed_abi"]
            for row in outputs
        ),
        "only_expected_nodes_added": all(
            row["structure"]["added_nodes"] == expected_nodes
            for row in outputs
        ),
        "only_expected_old_nodes_changed": all(
            row["structure"]["changed_old_nodes"]
            == ["t222_cap_command", "t234_exact_command_gate"]
            for row in outputs
        ),
        "all_initializers_byte_exact": all(
            row["structure"]["initializers_byte_exact"]
            and row["structure"]["initializer_names_exact"]
            for row in outputs
        ),
        "onnx_checker_passes": all(
            row["structure"]["onnx_checker_pass"] for row in outputs
        ),
        "random_contract_exact": all(
            row["inference"]["all_outputs_bit_exact"]
            and row["inference"]["all_non_targets_exact_source"]
            and row["inference"]["all_targets_exact_source_x0077"]
            and row["inference"]["all_targets_action_sensitive"]
            and row["inference"]["target_rows"] == 2
            and row["inference"]["all_outputs_finite"]
            and row["inference"]["provider"] == "CPUExecutionProvider"
            for row in outputs
        ),
        "failed_trace_replay_and_mapping_exact": (
            len(trace_rows) == 1
            and trace_rows[0]["rows"] == 281
            and trace_rows[0]["ticks_contiguous_from_zero"]
            and trace_rows[0]["source_replay_exact"]
            and trace_rows[0]["transformed_exact_source_x0077"]
            and trace_rows[0]["all_outputs_finite"]
            and trace_rows[0]["continuous_action_changed_rows"] > 0
            and trace_rows[0]["maximum_continuous_action_delta"] > 0.0
            and trace_rows[0]["provider"] == "CPUExecutionProvider"
        ),
        "zero_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis_result: dict[str, Any] = {
        "schema_version": "open_duck.t243b_abi_helper_recovery_result.v1",
        "status": (
            "PASS_T243B_ABI_HELPER_RECOVERY"
            if not failed
            else "HOLD_T243B_ABI_HELPER_RECOVERY"
        ),
        "decision": (
            source["decision_rule"]["all_contract_checks_green"]
            if not failed
            else source["decision_rule"]["otherwise"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_t243_contract_sha256": prereg[
            "source_t243_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "recovery": {
            "partial_graphs_reused": 1,
            "missing_graphs_constructed": 1,
            "partial_graph_overwrites": 0,
            "abi_reporting_calls_corrected": 2,
            "source_transform_logic_changes": 0,
        },
        "execution": {
            "onnx_transforms": 1,
            "onnx_inferences": sum(
                row["inference"]["samples"] * 3 for row in outputs
            )
            + sum(row["rows"] * 3 for row in trace_rows),
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "targeted_behavior_preregistration": not failed,
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
        "# T243B ABI-helper recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Partial/new graphs: `1/1`; partial overwrites: `0`\n"
        f"- Failed checks: `{failed}`\n"
        "- Behavior/simulator/optimizer/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
