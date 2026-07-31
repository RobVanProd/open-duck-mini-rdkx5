#!/usr/bin/env python3
"""Build and prove T247's calibrated home-negative half-adapter route."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Mapping

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
    sha256,
)


PREREG = (
    ANALYSIS / "t247_home_negative_half_adapter_route_preregistration.json"
)
RESULT = ANALYSIS / "t247_home_negative_half_adapter_route_result.json"
MARKDOWN = (
    ANALYSIS / "T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE_RESULT_20260731.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t247_home_negative_half_adapter_route_v1"
)
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]
WEIGHT = "nominal_condition_negative_adapter_weight"
BIAS = "nominal_condition_negative_adapter_bias"


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T247 input: {path}")


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


def initializer_values(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: numpy_helper.to_array(item)
        for item in model.graph.initializer
    }


def transform(
    source: Path,
    destination: Path,
    half_values: dict[str, np.ndarray],
) -> dict[str, Any]:
    model = onnx.load(source)
    before = copy.deepcopy(model)
    additions = {
        "t247_home_negative_half_adapter_weight": np.asarray(
            half_values[WEIGHT], dtype=np.float32
        ),
        "t247_home_negative_half_adapter_bias": np.asarray(
            half_values[BIAS], dtype=np.float32
        ),
    }
    for name, value in additions.items():
        model.graph.initializer.append(numpy_helper.from_array(value, name))
    target = next(
        node
        for node in model.graph.node
        if list(node.output) == ["nominal_dynamic_conditional_adapter"]
    )
    if (
        target.op_type != "Where"
        or len(target.input) != 3
        or target.input[1] != "t234_command_selected_adapter_location"
    ):
        raise RuntimeError("T247 nominal dynamic target changed")
    target.input[1] = "t247_home_negative_selected_adapter_location"
    new_nodes = [
        helper.make_node(
            "Gemm",
            [
                "h_out",
                "t247_home_negative_half_adapter_weight",
                "t247_home_negative_half_adapter_bias",
            ],
            ["t247_home_negative_half_adapter_location"],
            name="t247_home_negative_half_adapter",
        ),
        helper.make_node(
            "Where",
            [
                "t243_home_negative_tail_condition",
                "t247_home_negative_half_adapter_location",
                "t234_command_selected_adapter_location",
            ],
            ["t247_home_negative_selected_adapter_location"],
            name="t247_select_home_negative_half_adapter",
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
        node.name: node.SerializeToString()
        for node in before.graph.node
    }
    after_nodes = {
        node.name: node.SerializeToString() for node in after.graph.node
    }
    changed_old = sorted(
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
        "transformed": receipt(destination),
        "source_abi": abi(before),
        "transformed_abi": abi(after),
        "added_nodes": [node.name for node in new_nodes],
        "added_initializers": sorted(additions),
        "changed_old_nodes": changed_old,
        "all_old_initializers_byte_exact": all(
            after_initializers.get(name) == value
            for name, value in before_initializers.items()
        ),
        "only_expected_initializers_added": (
            set(after_initializers) - set(before_initializers)
            == set(additions)
        ),
        "onnx_checker_pass": True,
    }


def random_contract(
    source: Path,
    transformed: Path,
    half_source: Path,
    contexts: list[dict[str, Any]],
    commands: list[float],
    samples: int,
    seed: int,
    role: str,
) -> dict[str, Any]:
    source_session = session(source)
    transformed_session = session(transformed)
    half_session = session(half_source)
    rng = np.random.default_rng(seed)
    rows = []
    for context_row in contexts:
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        tail = context_row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
        for command in commands:
            exact = True
            finite = True
            changed = 0
            for _ in range(samples):
                feed = {
                    "obs": rng.normal(
                        0.0, 0.25, (1, 115)
                    ).astype(np.float32),
                    "previous_action": rng.uniform(
                        -0.9, 0.9, (1, 14)
                    ).astype(np.float32),
                    "h_in": rng.uniform(
                        -0.9, 0.9, (1, 64)
                    ).astype(np.float32),
                    "calibration_context": context,
                }
                feed["obs"][0, 6] = np.float32(command)
                actual = transformed_session.run(OUTPUT_NAMES, feed)
                source_values = source_session.run(OUTPUT_NAMES, feed)
                expected = (
                    half_session.run(OUTPUT_NAMES, feed)
                    if tail
                    else source_values
                )
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(actual, expected, strict=True)
                )
                finite &= all(
                    np.all(np.isfinite(value)) for value in actual
                )
                changed += int(
                    not np.array_equal(actual[0], source_values[0])
                )
            rows.append(
                {
                    "condition_id": context_row["condition_id"],
                    "fit_id": context_row["fit_id"],
                    "command_x_m_s": command,
                    "tail": tail,
                    "samples": samples,
                    "all_outputs_bit_exact": bool(exact),
                    "all_outputs_finite": bool(finite),
                    "continuous_action_changed_samples": changed,
                }
            )
    return {
        "role": role,
        "provider": transformed_session.get_providers()[0],
        "rows": rows,
        "samples": len(rows) * samples,
        "all_outputs_bit_exact": all(
            row["all_outputs_bit_exact"] for row in rows
        ),
        "all_outputs_finite": all(
            row["all_outputs_finite"] for row in rows
        ),
        "all_non_tail_exact_source": all(
            row["all_outputs_bit_exact"] for row in rows if not row["tail"]
        ),
        "all_tail_exact_half_source": all(
            row["all_outputs_bit_exact"] for row in rows if row["tail"]
        ),
        "tail_changed_samples": sum(
            row["continuous_action_changed_samples"]
            for row in rows
            if row["tail"]
        ),
    }


def trace_contract(
    final_source: Path,
    transformed: Path,
    half_source: Path,
    trace: Path,
    context: list[float],
) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in trace.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    final_session = session(final_source)
    transformed_session = session(transformed)
    half_session = session(half_source)
    context_value = np.asarray(context, dtype=np.float32).reshape(1, 64)
    source_replay_exact = True
    transformed_exact_half = True
    finite = True
    changed_rows = 0
    maximum_action_delta = 0.0
    for row in rows:
        state = row["policy_state_input"]
        feed = {
            "obs": np.asarray(
                row["obs_state"], dtype=np.float32
            ).reshape(1, 115),
            "h_in": np.asarray(state["h_in"], dtype=np.float32),
            "previous_action": np.asarray(
                state["previous_action"], dtype=np.float32
            ),
            "calibration_context": context_value,
        }
        source_values = final_session.run(OUTPUT_NAMES, feed)
        actual = transformed_session.run(OUTPUT_NAMES, feed)
        expected = half_session.run(OUTPUT_NAMES, feed)
        replay = np.asarray(row["policy_raw_action"], dtype=np.float32)
        source_replay_exact &= np.array_equal(
            source_values[0].reshape(-1), replay
        )
        transformed_exact_half &= all(
            np.array_equal(left, right)
            for left, right in zip(actual, expected, strict=True)
        )
        finite &= all(np.all(np.isfinite(value)) for value in actual)
        delta = float(
            np.max(np.abs(actual[0].reshape(-1) - replay))
        )
        changed_rows += int(delta > 0.0)
        maximum_action_delta = max(maximum_action_delta, delta)
    return {
        "trace": receipt(trace),
        "rows": len(rows),
        "ticks_contiguous_from_zero": [
            int(row["tick"]) for row in rows
        ]
        == list(range(len(rows))),
        "source_replay_exact": bool(source_replay_exact),
        "transformed_exact_half_source": bool(transformed_exact_half),
        "all_outputs_finite": bool(finite),
        "continuous_action_changed_rows": changed_rows,
        "maximum_continuous_action_delta": maximum_action_delta,
        "provider": transformed_session.get_providers()[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T247 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T247 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T247 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for graph in prereg["graphs"]:
        verify(graph["source"])
    verify(prereg["half_adapter_source"])
    verify(prereg["failed_final_trace"])

    started = time.time()
    half_path = Path(prereg["half_adapter_source"]["path"])
    half_values = initializer_values(onnx.load(half_path))
    outputs = []
    for index, graph in enumerate(prereg["graphs"]):
        destination = (
            WORK
            / "graphs"
            / str(graph["step"])
            / "home_negative_half_adapter_route.onnx"
        )
        structure = transform(
            Path(graph["source"]["path"]),
            destination,
            half_values,
        )
        inference = random_contract(
            Path(graph["source"]["path"]),
            destination,
            half_path,
            prereg["contexts"],
            prereg["contract"]["commands_x_m_s"],
            int(prereg["contract"]["samples_per_context_command"]),
            int(prereg["contract"]["random_seed"]) + index,
            graph["role"],
        )
        outputs.append(
            {
                "step": graph["step"],
                "role": graph["role"],
                "structure": structure,
                "inference": inference,
            }
        )
    final_output = next(row for row in outputs if row["role"] == "final")
    context = next(
        row["context"]
        for row in prereg["contexts"]
        if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
        and row["fit_id"] == "p30"
    )
    trace = trace_contract(
        Path(
            next(
                row["source"]["path"]
                for row in prereg["graphs"]
                if row["role"] == "final"
            )
        ),
        Path(final_output["structure"]["transformed"]["path"]),
        half_path,
        Path(prereg["failed_final_trace"]["path"]),
        context,
    )
    expected_nodes = [
        "t247_home_negative_half_adapter",
        "t247_select_home_negative_half_adapter",
    ]
    expected_initializers = [
        "t247_home_negative_half_adapter_bias",
        "t247_home_negative_half_adapter_weight",
    ]
    checks = {
        "two_transformed_graphs": (
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
        "only_expected_initializers_added": all(
            row["structure"]["added_initializers"]
            == expected_initializers
            and row["structure"]["all_old_initializers_byte_exact"]
            and row["structure"]["only_expected_initializers_added"]
            for row in outputs
        ),
        "only_nominal_dynamic_input_changed": all(
            row["structure"]["changed_old_nodes"] == [""]
            for row in outputs
        ),
        "onnx_checker_passes": all(
            row["structure"]["onnx_checker_pass"] for row in outputs
        ),
        "random_contract_exact": (
            all(
                row["inference"]["all_outputs_bit_exact"]
                and row["inference"]["all_non_tail_exact_source"]
                and row["inference"]["all_tail_exact_half_source"]
                and row["inference"]["all_outputs_finite"]
                and row["inference"]["provider"] == "CPUExecutionProvider"
                for row in outputs
            )
            and next(
                row["inference"]["tail_changed_samples"]
                for row in outputs
                if row["role"] == "half"
            )
            == 0
            and next(
                row["inference"]["tail_changed_samples"]
                for row in outputs
                if row["role"] == "final"
            )
            > 0
        ),
        "failed_final_trace_maps_exactly_to_half": (
            trace["rows"] == 231
            and trace["ticks_contiguous_from_zero"]
            and trace["source_replay_exact"]
            and trace["transformed_exact_half_source"]
            and trace["all_outputs_finite"]
            and trace["continuous_action_changed_rows"] > 0
            and trace["maximum_continuous_action_delta"] > 0.0
            and trace["provider"] == "CPUExecutionProvider"
        ),
        "zero_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t247_home_negative_half_adapter_route_result.v1"
        ),
        "status": (
            "PASS_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE"
            if not failed
            else "HOLD_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if not failed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "failed_final_trace_contract": trace,
        "execution": {
            "onnx_transforms": 2,
            "onnx_inferences": sum(
                row["inference"]["samples"] * 3 for row in outputs
            )
            + trace["rows"] * 3,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "behavior_matrix_preregistration": not failed,
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
        "# T247 home-negative half-adapter route result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
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
