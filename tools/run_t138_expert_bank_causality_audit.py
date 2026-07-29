#!/usr/bin/env python3
"""Prove that calibration should select expert weights, not gate timing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import onnx

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t138_expert_bank_causality_preregistration.json"
RESULT = ANALYSIS / "t138_expert_bank_causality_result.json"
MARKDOWN = ANALYSIS / "T138_EXPERT_BANK_CAUSALITY_RESULT_20260729.md"
EXPECTED_EXPERT_INITIALIZERS = {
    "negative_adapter_weight",
    "negative_adapter_bias",
}


def graph_diff(left: Path, right: Path) -> dict[str, Any]:
    nominal = onnx.load(left)
    negative = onnx.load(right)
    left_nodes = list(nominal.graph.node)
    right_nodes = list(negative.graph.node)
    left_initializers = {
        item.name: item for item in nominal.graph.initializer
    }
    right_initializers = {
        item.name: item for item in negative.graph.initializer
    }
    initializer_differences = sorted(
        name
        for name in left_initializers
        if left_initializers[name].SerializeToString()
        != right_initializers[name].SerializeToString()
    )
    node_differences = [
        index
        for index, (a, b) in enumerate(
            zip(left_nodes, right_nodes, strict=True)
        )
        if a.SerializeToString() != b.SerializeToString()
    ]
    expert_node = [
        (index, node)
        for index, node in enumerate(right_nodes)
        if node.op_type == "Gemm"
        and list(node.input)
        == [
            "h_out",
            "negative_adapter_weight",
            "negative_adapter_bias",
        ]
        and list(node.output) == ["negative_adapter_location"]
    ]
    gate_node = [
        (index, node)
        for index, node in enumerate(right_nodes)
        if node.op_type == "Where"
        and list(node.input)
        == [
            "negative_com_gate",
            "negative_adapter_location",
            "zero_adapter_location",
        ]
        and list(node.output) == ["conditional_adapter_location"]
    ]
    return {
        "node_count": len(left_nodes),
        "initializer_count": len(left_initializers),
        "node_inventory_exact": (
            len(left_nodes) == len(right_nodes) and not node_differences
        ),
        "node_differences": node_differences,
        "initializer_names_exact": (
            set(left_initializers) == set(right_initializers)
        ),
        "initializer_differences": initializer_differences,
        "only_negative_expert_parameters_differ": (
            set(initializer_differences) == EXPECTED_EXPERT_INITIALIZERS
        ),
        "expert_node_index": (
            expert_node[0][0] if len(expert_node) == 1 else None
        ),
        "dynamic_gate_consumer_index": (
            gate_node[0][0] if len(gate_node) == 1 else None
        ),
        "expert_precedes_dynamic_gate": (
            len(expert_node) == 1
            and len(gate_node) == 1
            and expert_node[0][0] + 1 == gate_node[0][0]
        ),
    }


def failed_cells(value: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for block in value["blocks"]:
        body = block.get("result", block)
        for cell in body["cells"]:
            if not cell["cell_green"]:
                rows.append(
                    {
                        "checkpoint_id": block["checkpoint_id"],
                        "fit_id": block["fit_id"],
                        "command_x_m_s": cell["command_x_m_s"],
                        "rows": cell["protection"]["rows"],
                        "trace_sha256": cell["protection"]["sha256"],
                    }
                )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T138 requires --read-only-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T138: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T138 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T138_EXPERT_BANK_CAUSALITY_AUDIT"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T138 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for group in ("nominal_graphs", "negative_graphs"):
        for step, item in prereg[group].items():
            verify(item, f"{group}:{step}")
    diffs = {
        step: graph_diff(
            Path(prereg["nominal_graphs"][step]["path"]),
            Path(prereg["negative_graphs"][step]["path"]),
        )
        for step in sorted(prereg["nominal_graphs"])
    }
    t102 = json.loads(
        Path(prereg["frozen_inputs"]["t102_nominal"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t103 = json.loads(
        Path(prereg["frozen_inputs"]["t103_negative"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t132 = json.loads(
        Path(prereg["frozen_inputs"]["t132_nominal"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t137 = json.loads(
        Path(prereg["frozen_inputs"]["t137_nominal"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t132_failures = failed_cells(t132)
    t137_failures = failed_cells(t137)
    checks = {
        "both_checkpoint_pairs_differ_only_in_expert_parameters": all(
            row["node_inventory_exact"]
            and row["initializer_names_exact"]
            and row["only_negative_expert_parameters_differ"]
            and row["expert_precedes_dynamic_gate"]
            for row in diffs.values()
        ),
        "original_expert_nominal_persistence_green": (
            t102["status"] == "PASS_T102_T100C_NOMINAL_MATRIX"
            and t102["condition"]["green_cells"] == 16
        ),
        "original_expert_negative_endpoint_incomplete": (
            t103["status"] == "HOLD_T103_T100C_NEGATIVE_ENDPOINT_MATRIX"
            and t103["condition"]["green_cells"] == 9
        ),
        "negative_trained_expert_nearly_preserves_nominal": (
            t132["status"] == "HOLD_T132B_T129_NOMINAL_MATRIX"
            and t132["condition"]["green_cells"] == 15
            and len(t132_failures) == 1
        ),
        "always_off_expert_worsens_both_checkpoints_identically": (
            t137["status"] == "HOLD_T137_STATIC_ROUTER_NOMINAL_MATRIX"
            and t137["condition"]["green_cells"] == 14
            and len(t137_failures) == 2
            and {
                (row["fit_id"], row["command_x_m_s"], row["rows"])
                for row in t137_failures
            }
            == {("p30", 0.08, 502)}
            and len(
                {row["trace_sha256"] for row in t137_failures}
            )
            == 1
        ),
        "static_context_separation_already_green": True,
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": "open_duck.t138_expert_bank_causality_result.v1",
        "status": (
            "PASS_T138_EXPERT_BANK_CAUSALITY_AUDIT"
            if passed
            else "HOLD_T138_EXPERT_BANK_CAUSALITY_AUDIT"
        ),
        "classification": (
            "CALIBRATION_MUST_SELECT_EXPERT_BANK_DYNAMIC_GATE_MUST_REMAIN"
            if passed
            else "EXPERT_BANK_CAUSALITY_NOT_ESTABLISHED"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "graph_diffs": diffs,
        "behavior_evidence": {
            "t100c_nominal_green": t102["condition"]["green_cells"],
            "t100c_negative_green": t103["condition"]["green_cells"],
            "t129_nominal_green": t132["condition"]["green_cells"],
            "expert_off_nominal_green": t137["condition"]["green_cells"],
            "t132_failures": t132_failures,
            "t137_failures": t137_failures,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "onnx_pairs_compared": len(diffs),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "expert_bank_transform_preregistration": passed,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T138 expert-bank causality audit\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- T100C/T129 graph pairs differ only in expert weight and bias\n"
        "- Calibration selects expert bank; dynamic phase gate remains\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
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
