#!/usr/bin/env python3
"""Build nominal-dynamic / negative-always-on calibration routing."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np
import onnx
import onnxruntime as ort
from onnx import helper, numpy_helper

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    abi,
    canonical_sha256,
    receipt,
    verify,
)


PREREG = (
    ANALYSIS / "t143_conditional_forward_path_preregistration.json"
)
RESULT = ANALYSIS / "t143_conditional_forward_path_result.json"
MARKDOWN = (
    ANALYSIS / "T143_CONDITIONAL_FORWARD_PATH_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t143_conditional_forward_path_v1"
)


def initializer_map(model: onnx.ModelProto) -> dict[str, onnx.TensorProto]:
    return {item.name: item for item in model.graph.initializer}


def always_on_reference(source: Path, destination: Path) -> dict[str, Any]:
    model = onnx.load(source)
    candidates = [
        (index, node)
        for index, node in enumerate(model.graph.node)
        if node.op_type == "Where"
        and list(node.input)
        == [
            "negative_com_gate",
            "negative_adapter_location",
            "zero_adapter_location",
        ]
        and list(node.output) == ["conditional_adapter_location"]
    ]
    if len(candidates) != 1:
        raise RuntimeError("T143 always-on source gate changed")
    index, old = candidates[0]
    replacement = helper.make_node(
        "Identity",
        ["negative_adapter_location"],
        ["conditional_adapter_location"],
        name="t143_negative_always_on_reference",
    )
    del model.graph.node[index]
    model.graph.node.insert(index, replacement)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    return {
        "source": receipt(source),
        "reference": receipt(destination),
        "replacement_index": index,
        "source_where": {
            "inputs": list(old.input),
            "outputs": list(old.output),
        },
        "identity_exact": (
            list(replacement.input) == ["negative_adapter_location"]
            and list(replacement.output) == ["conditional_adapter_location"]
        ),
    }


def transform(
    nominal_source: Path,
    negative_source: Path,
    destination: Path,
    coefficient: np.ndarray,
    intercept: float,
) -> dict[str, Any]:
    nominal = onnx.load(nominal_source)
    negative = onnx.load(negative_source)
    model = copy.deepcopy(negative)
    nominal_initializers = initializer_map(nominal)
    negative_initializers = initializer_map(negative)
    differences = {
        name
        for name in nominal_initializers
        if nominal_initializers[name].SerializeToString()
        != negative_initializers[name].SerializeToString()
    }
    if differences != {
        "negative_adapter_weight",
        "negative_adapter_bias",
    }:
        raise RuntimeError(f"T143 source difference changed: {differences}")
    expert_nodes = [
        (index, node)
        for index, node in enumerate(model.graph.node)
        if node.op_type == "Gemm"
        and list(node.input)
        == [
            "h_out",
            "negative_adapter_weight",
            "negative_adapter_bias",
        ]
        and list(node.output) == ["negative_adapter_location"]
    ]
    dynamic_nodes = [
        (index, node)
        for index, node in enumerate(model.graph.node)
        if node.op_type == "Where"
        and list(node.input)
        == [
            "negative_com_gate",
            "negative_adapter_location",
            "zero_adapter_location",
        ]
        and list(node.output) == ["conditional_adapter_location"]
    ]
    if (
        len(expert_nodes) != 1
        or len(dynamic_nodes) != 1
        or expert_nodes[0][0] + 1 != dynamic_nodes[0][0]
    ):
        raise RuntimeError("T143 expert/dynamic topology changed")
    expert_index, expert_node = expert_nodes[0]
    dynamic_index, dynamic_node = dynamic_nodes[0]
    expert_node.output[0] = "negative_condition_adapter_location"
    dynamic_node.input[1] = "nominal_condition_adapter_location"
    dynamic_node.output[0] = "nominal_dynamic_conditional_adapter"
    additions = {
        "nominal_condition_negative_adapter_weight": numpy_helper.to_array(
            nominal_initializers["negative_adapter_weight"]
        ),
        "nominal_condition_negative_adapter_bias": numpy_helper.to_array(
            nominal_initializers["negative_adapter_bias"]
        ),
        "conditional_path_router_coefficient": coefficient.reshape(64, 1),
        "conditional_path_router_intercept": np.asarray(
            [intercept], dtype=np.float32
        ),
        "conditional_path_router_zero": np.asarray(
            [0.0], dtype=np.float32
        ),
    }
    for name, value in additions.items():
        model.graph.initializer.append(
            numpy_helper.from_array(np.asarray(value, dtype=np.float32), name)
        )
    before_dynamic = [
        helper.make_node(
            "Gemm",
            [
                "h_out",
                "nominal_condition_negative_adapter_weight",
                "nominal_condition_negative_adapter_bias",
            ],
            ["nominal_condition_adapter_location"],
            name="t143_nominal_expert",
        ),
        helper.make_node(
            "MatMul",
            ["calibration_context", "conditional_path_router_coefficient"],
            ["conditional_path_router_linear"],
            name="t143_context_router_matmul",
        ),
        helper.make_node(
            "Add",
            [
                "conditional_path_router_linear",
                "conditional_path_router_intercept",
            ],
            ["conditional_path_router_score"],
            name="t143_context_router_add",
        ),
        helper.make_node(
            "GreaterOrEqual",
            [
                "conditional_path_router_score",
                "conditional_path_router_zero",
            ],
            ["conditional_path_negative_condition"],
            name="t143_context_router_gate",
        ),
    ]
    for offset, node in enumerate(before_dynamic):
        model.graph.node.insert(dynamic_index + offset, node)
    selected = helper.make_node(
        "Where",
        [
            "conditional_path_negative_condition",
            "negative_condition_adapter_location",
            "nominal_dynamic_conditional_adapter",
        ],
        ["conditional_adapter_location"],
        name="t143_select_forward_path",
    )
    model.graph.node.insert(
        dynamic_index + len(before_dynamic) + 1, selected
    )
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)

    after = onnx.load(destination)
    old_nodes = list(negative.graph.node)
    new_nodes = list(after.graph.node)
    old_initializers = {
        item.name: item.SerializeToString()
        for item in negative.graph.initializer
    }
    new_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    unchanged = 0
    expert_exact = False
    dynamic_exact = False
    old_index = 0
    inserted_indices = set(
        range(dynamic_index, dynamic_index + len(before_dynamic))
    ) | {dynamic_index + len(before_dynamic) + 1}
    for new_index, node in enumerate(new_nodes):
        if new_index in inserted_indices:
            continue
        old = old_nodes[old_index]
        if old_index == expert_index:
            expected = copy.deepcopy(old)
            expected.output[0] = "negative_condition_adapter_location"
            expert_exact = (
                node.SerializeToString() == expected.SerializeToString()
            )
        elif old_index == dynamic_index:
            expected = copy.deepcopy(old)
            expected.input[1] = "nominal_condition_adapter_location"
            expected.output[0] = "nominal_dynamic_conditional_adapter"
            dynamic_exact = (
                node.SerializeToString() == expected.SerializeToString()
            )
        else:
            unchanged += int(
                node.SerializeToString() == old.SerializeToString()
            )
        old_index += 1
    return {
        "nominal_source": receipt(nominal_source),
        "negative_source": receipt(negative_source),
        "transformed": receipt(destination),
        "source_differences": sorted(differences),
        "five_nodes_inserted": len(new_nodes) == len(old_nodes) + 5,
        "expert_output_rewire_exact": expert_exact,
        "dynamic_nominal_gate_rewire_exact": dynamic_exact,
        "all_other_nodes_byte_exact": unchanged == len(old_nodes) - 2,
        "existing_initializers_byte_exact": all(
            new_initializers.get(name) == value
            for name, value in old_initializers.items()
        ),
        "five_initializers_added": (
            set(new_initializers) - set(old_initializers) == set(additions)
        ),
        "abi_exact": abi(negative) == abi(after) == abi(nominal),
    }


def equivalence_contract(
    nominal_source: Path,
    negative_always_on: Path,
    transformed: Path,
    contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    nominal_session = ort.InferenceSession(
        str(nominal_source), providers=["CPUExecutionProvider"]
    )
    negative_session = ort.InferenceSession(
        str(negative_always_on), providers=["CPUExecutionProvider"]
    )
    transformed_session = ort.InferenceSession(
        str(transformed), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260729)
    rows = []
    for context_row in contexts:
        negative_condition = (
            context_row["population"] == "com_x_negative"
        )
        selected = (
            negative_session if negative_condition else nominal_session
        )
        exact = True
        finite = True
        feedback = True
        samples = 0
        for command_x in (0.0, 0.074, 0.077, 0.08):
            for _ in range(16):
                feed = {
                    "obs": rng.normal(size=(1, 115)).astype(np.float32),
                    "previous_action": rng.uniform(
                        -0.98, 0.98, size=(1, 14)
                    ).astype(np.float32),
                    "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                    "calibration_context": np.asarray(
                        context_row["context"], dtype=np.float32
                    ).reshape(1, 64),
                }
                feed["obs"][:, 6] = np.float32(command_x)
                expected = selected.run(None, feed)
                actual = transformed_session.run(None, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(expected, actual, strict=True)
                )
                finite &= all(
                    bool(np.all(np.isfinite(value))) for value in actual
                )
                feedback &= np.array_equal(actual[0], actual[1])
                samples += 1
        rows.append(
            {
                "fit_id": context_row["fit_id"],
                "population": context_row["population"],
                "selected_source": (
                    "T129_negative_expert_always_on"
                    if negative_condition
                    else "T100C_nominal_dynamic_gate"
                ),
                "samples": samples,
                "all_outputs_bit_exact": exact,
                "all_outputs_finite": finite,
                "action_feedback_bit_exact": feedback,
            }
        )
    return {
        "rows": rows,
        "all_selected_source_outputs_bit_exact": all(
            row["all_outputs_bit_exact"] for row in rows
        ),
        "all_outputs_finite": all(
            row["all_outputs_finite"] for row in rows
        ),
        "all_action_feedback_bit_exact": all(
            row["action_feedback_bit_exact"] for row in rows
        ),
        "samples": sum(row["samples"] for row in rows),
        "cpu_only": all(
            session.get_providers()[0] == "CPUExecutionProvider"
            for session in (
                nominal_session,
                negative_session,
                transformed_session,
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T143 requires --execute")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T143: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T143 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T143_CONDITIONAL_FORWARD_PATH_TRANSFORM"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T143 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for group in ("nominal_graphs", "negative_graphs"):
        for step, item in prereg[group].items():
            verify(item, f"{group}:{step}")
    t135b = json.loads(
        Path(prereg["frozen_inputs"]["t135b_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    asset = json.loads(
        Path(prereg["frozen_inputs"]["router_asset"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    coefficient = np.asarray(asset["coefficient"], dtype=np.float32)
    intercept = float(asset["intercept"])
    WORK.mkdir(parents=True)
    graphs = {}
    references = {}
    contracts = {}
    started = time.time()
    for step in sorted(prereg["nominal_graphs"]):
        nominal = Path(prereg["nominal_graphs"][step]["path"])
        negative = Path(prereg["negative_graphs"][step]["path"])
        reference_path = (
            WORK / step / "negative_always_on_reference.onnx"
        )
        transformed_path = (
            WORK / step / "conditional_forward_path.onnx"
        )
        references[step] = always_on_reference(
            negative, reference_path
        )
        graphs[step] = transform(
            nominal,
            negative,
            transformed_path,
            coefficient,
            intercept,
        )
        contracts[step] = equivalence_contract(
            nominal,
            reference_path,
            transformed_path,
            t135b["runs"],
        )
    checks = {
        "all_always_on_references_exact": all(
            row["identity_exact"] for row in references.values()
        ),
        "all_graph_transforms_exact": all(
            all(
                row[name]
                for name in (
                    "five_nodes_inserted",
                    "expert_output_rewire_exact",
                    "dynamic_nominal_gate_rewire_exact",
                    "all_other_nodes_byte_exact",
                    "existing_initializers_byte_exact",
                    "five_initializers_added",
                    "abi_exact",
                )
            )
            for row in graphs.values()
        ),
        "all_selected_source_outputs_bit_exact": all(
            row["all_selected_source_outputs_bit_exact"]
            for row in contracts.values()
        ),
        "all_feedback_finite_cpu": all(
            row["all_outputs_finite"]
            and row["all_action_feedback_bit_exact"]
            and row["cpu_only"]
            for row in contracts.values()
        ),
        "both_checkpoints_transformed": (
            set(graphs) == {"1003520", "2007040"}
        ),
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t143_conditional_forward_path_result.v1"
        ),
        "status": (
            "PASS_T143_CONDITIONAL_FORWARD_PATH_TRANSFORM"
            if passed
            else "HOLD_T143_CONDITIONAL_FORWARD_PATH_TRANSFORM"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "graphs": graphs,
        "always_on_references": references,
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "graphs_transformed": len(graphs),
            "cpu_equivalence_samples": sum(
                row["samples"] for row in contracts.values()
            ),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "nominal_identity_reuse_preregistration": passed,
            "negative_endpoint_preregistration": False,
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
        "# T143 conditional forward-path transform\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Nominal: exact T100C dynamic gate\n"
        "- Negative COM: exact T129 always-on training path\n"
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
