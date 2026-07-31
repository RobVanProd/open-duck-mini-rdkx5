#!/usr/bin/env python3
"""Build and prove T234's exact .074 paired-final adapter route."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    abi,
    canonical_sha256,
    receipt,
    verify,
)


PREREG = ANALYSIS / "t234_exact_low_command_head_route_preregistration.json"
OUTPUT = ANALYSIS / "t234_exact_low_command_head_route_result.json"
MARKDOWN = ANALYSIS / "T234_EXACT_LOW_COMMAND_HEAD_ROUTE_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t234_exact_low_command_final_head_v1"
)
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]
WEIGHT = "nominal_condition_negative_adapter_weight"
BIAS = "nominal_condition_negative_adapter_bias"


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def initializers(model: onnx.ModelProto) -> dict[str, onnx.TensorProto]:
    return {value.name: value for value in model.graph.initializer}


def replace_initializer(
    model: onnx.ModelProto,
    name: str,
    value: np.ndarray,
) -> None:
    for index, current in enumerate(model.graph.initializer):
        if current.name == name:
            model.graph.initializer[index].CopyFrom(
                numpy_helper.from_array(value, name)
            )
            return
    raise KeyError(name)


def oracle(source: Path, final: Path, destination: Path) -> dict[str, Any]:
    model = onnx.load(source)
    final_model = onnx.load(final)
    final_values = {
        name: numpy_helper.to_array(initializers(final_model)[name])
        for name in (WEIGHT, BIAS)
    }
    for name, value in final_values.items():
        replace_initializer(model, name, value)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    return receipt(destination)


def transform(
    source: Path,
    final: Path,
    destination: Path,
    command: float,
) -> dict[str, Any]:
    model = onnx.load(source)
    before = copy.deepcopy(model)
    final_model = onnx.load(final)
    final_values = {
        name: numpy_helper.to_array(initializers(final_model)[name])
        for name in (WEIGHT, BIAS)
    }
    additions = {
        "t234_exact_command_x_m_s": np.asarray(
            [np.float32(command)], dtype=np.float32
        ),
        "t234_paired_final_adapter_weight": np.asarray(
            final_values[WEIGHT], dtype=np.float32
        ),
        "t234_paired_final_adapter_bias": np.asarray(
            final_values[BIAS], dtype=np.float32
        ),
    }
    for name, value in additions.items():
        model.graph.initializer.append(numpy_helper.from_array(value, name))

    target = None
    for node in model.graph.node:
        if (
            node.op_type == "Where"
            and list(node.output) == ["nominal_dynamic_conditional_adapter"]
        ):
            target = node
            break
    if target is None:
        raise RuntimeError("T234 downstream conditional Where not found")
    if (
        len(target.input) != 3
        or target.input[1] != "nominal_condition_adapter_location"
    ):
        raise RuntimeError(f"T234 downstream Where changed: {target}")
    target.input[1] = "t234_command_selected_adapter_location"

    new_nodes = [
        helper.make_node(
            "Gemm",
            [
                "h_out",
                "t234_paired_final_adapter_weight",
                "t234_paired_final_adapter_bias",
            ],
            ["t234_paired_final_adapter_location"],
            name="t234_paired_final_head",
        ),
        helper.make_node(
            "Equal",
            ["t222_raw_command_x", "t234_exact_command_x_m_s"],
            ["t234_exact_command_gate"],
            name="t234_exact_command_gate",
        ),
        helper.make_node(
            "Where",
            [
                "t234_exact_command_gate",
                "t234_paired_final_adapter_location",
                "nominal_condition_adapter_location",
            ],
            ["t234_command_selected_adapter_location"],
            name="t234_select_paired_final_head",
        ),
    ]
    target_index = list(model.graph.node).index(target)
    for offset, node in enumerate(new_nodes):
        model.graph.node.insert(target_index + offset, node)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    after = onnx.load(destination)

    before_nodes = {
        tuple(node.output): node.SerializeToString()
        for node in before.graph.node
    }
    after_nodes = {tuple(node.output): node for node in after.graph.node}
    changed_old_nodes = []
    for outputs, serialized in before_nodes.items():
        if after_nodes[outputs].SerializeToString() != serialized:
            changed_old_nodes.append("|".join(outputs))
    return {
        "source": receipt(source),
        "paired_final": receipt(final),
        "transformed": receipt(destination),
        "source_abi": abi(source),
        "transformed_abi": abi(destination),
        "added_nodes": [node.name for node in new_nodes],
        "added_initializers": sorted(additions),
        "changed_old_nodes": sorted(changed_old_nodes),
        "onnx_checker_pass": True,
        "exact_command_float32": float(
            additions["t234_exact_command_x_m_s"][0]
        ),
    }


def random_contract(
    source: Path,
    transformed: Path,
    oracle_path: Path,
    contexts: list[dict[str, Any]],
    commands: list[float],
    samples: int,
    seed: int,
) -> dict[str, Any]:
    source_session = session(source)
    transformed_session = session(transformed)
    oracle_session = session(oracle_path)
    rng = np.random.default_rng(seed)
    rows = []
    for context_row in contexts:
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        for command in commands:
            exact = True
            finite = True
            expected_kind = (
                "paired_final_head" if command == 0.074 else "source"
            )
            expected_session = (
                oracle_session if command == 0.074 else source_session
            )
            for _ in range(samples):
                obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
                obs[0, 6] = np.float32(command)
                feed = {
                    "obs": obs,
                    "previous_action": rng.uniform(
                        -0.9, 0.9, (1, 14)
                    ).astype(np.float32),
                    "h_in": rng.uniform(-0.9, 0.9, (1, 64)).astype(
                        np.float32
                    ),
                    "calibration_context": context,
                }
                actual = transformed_session.run(OUTPUT_NAMES, feed)
                expected = expected_session.run(OUTPUT_NAMES, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(actual, expected, strict=True)
                )
                finite &= all(np.all(np.isfinite(value)) for value in actual)
            rows.append(
                {
                    "condition_id": context_row["condition_id"],
                    "fit_id": context_row["fit_id"],
                    "command_x_m_s": command,
                    "expected_kind": expected_kind,
                    "samples": samples,
                    "all_outputs_bit_exact": bool(exact),
                    "all_outputs_finite": bool(finite),
                }
            )
    return {
        "rows": rows,
        "samples": len(rows) * samples,
        "all_outputs_bit_exact": all(
            row["all_outputs_bit_exact"] for row in rows
        ),
        "all_outputs_finite": all(row["all_outputs_finite"] for row in rows),
        "all_x0074_exact_paired_final_head": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["command_x_m_s"] == 0.074
        ),
        "all_other_commands_exact_source": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["command_x_m_s"] != 0.074
        ),
    }


def trace_contract(
    source: Path,
    transformed: Path,
    oracle_path: Path,
    trace_item: dict[str, Any],
    context: list[float],
    count: int,
) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in Path(trace_item["trace"]["path"])
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ][:count]
    source_session = session(source)
    transformed_session = session(transformed)
    oracle_session = session(oracle_path)
    context_value = np.asarray(context, dtype=np.float32).reshape(1, 64)
    exact_oracle = True
    finite = True
    changed_rows = 0
    maximum_action_delta = 0.0
    for row in rows:
        state = row["policy_state_input"]
        feed = {
            "obs": np.asarray(
                row["obs_state"], dtype=np.float32
            ).reshape(1, 115),
            "previous_action": np.asarray(
                state["previous_action"], dtype=np.float32
            ),
            "h_in": np.asarray(state["h_in"], dtype=np.float32),
            "calibration_context": context_value,
        }
        actual = transformed_session.run(OUTPUT_NAMES, feed)
        expected = oracle_session.run(OUTPUT_NAMES, feed)
        old = source_session.run(OUTPUT_NAMES, feed)
        exact_oracle &= all(
            np.array_equal(left, right)
            for left, right in zip(actual, expected, strict=True)
        )
        finite &= all(np.all(np.isfinite(value)) for value in actual)
        delta = float(np.max(np.abs(actual[0] - old[0])))
        changed_rows += int(delta > 0.0)
        maximum_action_delta = max(maximum_action_delta, delta)
    return {
        "checkpoint_id": trace_item["checkpoint_id"],
        "step": trace_item["step"],
        "fit_id": trace_item["fit_id"],
        "rows": len(rows),
        "all_outputs_exact_paired_final_head_oracle": bool(exact_oracle),
        "all_outputs_finite": bool(finite),
        "changed_action_rows_from_source": changed_rows,
        "maximum_action_delta_from_source": maximum_action_delta,
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T234: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to overwrite T234 work: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T234 execution requires a clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        name: value
        for name, value in prereg.items()
        if name != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T234_EXACT_LOW_COMMAND_HEAD_ROUTE"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T234 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for index, graph in enumerate(prereg["graphs"]):
        verify(graph["source"], f"graphs[{index}].source")
    verify(prereg["paired_final_expert_source"], "paired_final_expert_source")
    for index, item in enumerate(prereg["upper_z_x0074_traces"]):
        verify(item["trace"], f"upper_z_x0074_traces[{index}]")

    WORK.mkdir(parents=True)
    final_path = Path(prereg["paired_final_expert_source"]["path"])
    outputs = []
    trace_outputs = []
    context_by_fit = {
        row["fit_id"]: row["context"]
        for row in prereg["contexts"]
        if row["condition_id"] == "TORSO_COM_Z_POS"
    }
    for graph_index, graph in enumerate(prereg["graphs"]):
        step = int(graph["step"])
        source = Path(graph["source"]["path"])
        directory = WORK / str(step)
        transformed = directory / "exact_low_command_final_head.onnx"
        oracle_path = directory / "paired_final_head_oracle.onnx"
        structure = transform(
            source,
            final_path,
            transformed,
            float(prereg["transform"]["exact_command_x_m_s"]),
        )
        oracle_receipt = oracle(source, final_path, oracle_path)
        inference = random_contract(
            source,
            transformed,
            oracle_path,
            prereg["contexts"],
            prereg["contract"]["commands_x_m_s"],
            int(prereg["contract"]["samples_per_context_command"]),
            int(prereg["contract"]["random_seed"]) + graph_index,
        )
        outputs.append(
            {
                "step": step,
                "role": graph["role"],
                "structure": structure,
                "oracle": oracle_receipt,
                "inference": inference,
            }
        )
        for trace_item in prereg["upper_z_x0074_traces"]:
            if int(trace_item["step"]) != step:
                continue
            trace_outputs.append(
                trace_contract(
                    source,
                    transformed,
                    oracle_path,
                    trace_item,
                    context_by_fit[trace_item["fit_id"]],
                    int(prereg["contract"]["trace_rows_per_pair"]),
                )
            )

    expected_nodes = {
        "t234_paired_final_head",
        "t234_exact_command_gate",
        "t234_select_paired_final_head",
    }
    expected_initializers = {
        "t234_exact_command_x_m_s",
        "t234_paired_final_adapter_bias",
        "t234_paired_final_adapter_weight",
    }
    checks = {
        "two_graphs_transformed": len(outputs) == 2,
        "abi_exact": all(
            row["structure"]["source_abi"]
            == row["structure"]["transformed_abi"]
            for row in outputs
        ),
        "only_expected_nodes_added": all(
            set(row["structure"]["added_nodes"]) == expected_nodes
            for row in outputs
        ),
        "only_expected_initializers_added": all(
            set(row["structure"]["added_initializers"])
            == expected_initializers
            for row in outputs
        ),
        "only_downstream_where_rewired": all(
            len(row["structure"]["changed_old_nodes"]) == 1
            for row in outputs
        ),
        "random_contract_exact": all(
            row["inference"]["all_outputs_bit_exact"]
            and row["inference"]["all_outputs_finite"]
            and row["inference"]["all_x0074_exact_paired_final_head"]
            and row["inference"]["all_other_commands_exact_source"]
            for row in outputs
        ),
        "four_trace_contracts_exact": (
            len(trace_outputs) == 4
            and all(
                row["all_outputs_exact_paired_final_head_oracle"]
                and row["all_outputs_finite"]
                for row in trace_outputs
            )
        ),
        "final_transform_all_commands_bit_exact_source": (
            next(
                row for row in outputs if row["role"] == "final"
            )["inference"]["all_outputs_bit_exact"]
        ),
        "no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    passed = not failed
    result_basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t234_exact_low_command_head_route_result.v1"
        ),
        "status": (
            "PASS_T234_EXACT_LOW_COMMAND_HEAD_ROUTE"
            if passed
            else "HOLD_T234_EXACT_LOW_COMMAND_HEAD_ROUTE"
        ),
        "decision": (
            prereg["decision_rule"]["all_contract_checks_green"]
            if passed
            else prereg["decision_rule"]["otherwise"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "upper_z_trace_contracts": trace_outputs,
        "interpretation": {
            "proved": (
                "exact .074 routes through the paired-final adapter head; "
                "all other commands, ABI, recurrence, deadband, and the "
                "existing .080 plateau retain their source semantics"
            ),
            "not_proved": (
                "closed-loop behavior; both transformed checkpoints remain "
                "mandatory in T235"
            ),
        },
        "execution": {
            "onnx_transforms": len(outputs),
            "random_inference_rows": sum(
                row["inference"]["samples"] for row in outputs
            ),
            "trace_inference_rows": sum(
                row["rows"] for row in trace_outputs
            ),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "nominal_behavior_preregistration": passed,
            "training": False,
            "hosted": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    result = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T234 exact low-command head route result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        f"- Random inference rows: "
        f"`{result['execution']['random_inference_rows']}`\n"
        f"- Frozen trace rows: "
        f"`{result['execution']['trace_inference_rows']}`\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
