#!/usr/bin/env python3
"""Embed and verify the frozen positive-context command endpoint transform."""

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
from run_t156_three_way_positive_router_transform import initializer_map


PREREG = ANALYSIS / "t162_exact_command_endpoint_transform_preregistration.json"
RESULT = ANALYSIS / "t162_exact_command_endpoint_transform_result.json"
MARKDOWN = ANALYSIS / "T162_EXACT_COMMAND_ENDPOINT_TRANSFORM_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t162_exact_command_endpoint_transform_v1"
)
STEPS = ("1003520", "2007040")


def transform(
    source: Path,
    destination: Path,
    endpoint_command_x_m_s: float,
) -> dict[str, Any]:
    before = onnx.load(source)
    model = copy.deepcopy(before)
    centering = [
        (index, node)
        for index, node in enumerate(model.graph.node)
        if node.op_type == "Sub"
        and list(node.input) == ["t17_source_obs", "obs_mean"]
        and list(node.output) == ["obs_centered"]
    ]
    if len(centering) != 1:
        raise RuntimeError("T162 actor observation centering node changed")
    center_index, center_node = centering[0]
    center_node.input[0] = "t162_policy_obs"

    additions = {
        "t162_gather_command_index": np.asarray([6], dtype=np.int64),
        "t162_scatter_command_index": np.asarray([[6]], dtype=np.int64),
        "t162_endpoint_command": np.asarray(
            [[endpoint_command_x_m_s]], dtype=np.float32
        ),
    }
    for name, value in additions.items():
        model.graph.initializer.append(numpy_helper.from_array(value, name))

    inserted = [
        helper.make_node(
            "MatMul",
            ["calibration_context", "positive_router_coefficient"],
            ["t162_positive_router_linear"],
            name="t162_positive_router_matmul",
        ),
        helper.make_node(
            "Add",
            ["t162_positive_router_linear", "positive_router_intercept"],
            ["t162_positive_router_score"],
            name="t162_positive_router_add",
        ),
        helper.make_node(
            "GreaterOrEqual",
            ["t162_positive_router_score", "positive_router_zero"],
            ["t162_positive_condition"],
            name="t162_positive_router_gate",
        ),
        helper.make_node(
            "Gather",
            ["t17_source_obs", "t162_gather_command_index"],
            ["t162_external_command"],
            name="t162_gather_external_command",
            axis=1,
        ),
        helper.make_node(
            "Greater",
            ["t162_external_command", "deadband_abs_limit"],
            ["t162_positive_moving_command"],
            name="t162_positive_moving_gate",
        ),
        helper.make_node(
            "And",
            ["t162_positive_condition", "t162_positive_moving_command"],
            ["t162_rewrite_condition"],
            name="t162_rewrite_gate",
        ),
        helper.make_node(
            "Where",
            [
                "t162_rewrite_condition",
                "t162_endpoint_command",
                "t162_external_command",
            ],
            ["t162_policy_command"],
            name="t162_select_policy_command",
        ),
        helper.make_node(
            "ScatterElements",
            [
                "t17_source_obs",
                "t162_scatter_command_index",
                "t162_policy_command",
            ],
            ["t162_policy_obs"],
            name="t162_scatter_policy_command",
            axis=1,
        ),
    ]
    for offset, node in enumerate(inserted):
        model.graph.node.insert(center_index + offset, node)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)

    after = onnx.load(destination)
    before_nodes = list(before.graph.node)
    after_nodes = list(after.graph.node)
    expected_center = copy.deepcopy(before_nodes[center_index])
    expected_center.input[0] = "t162_policy_obs"
    source_nodes_exact = True
    old_index = 0
    for new_index, node in enumerate(after_nodes):
        if center_index <= new_index < center_index + len(inserted):
            continue
        expected = (
            expected_center
            if old_index == center_index
            else before_nodes[old_index]
        )
        source_nodes_exact &= (
            node.SerializeToString() == expected.SerializeToString()
        )
        old_index += 1
    before_initializers = {
        item.name: item.SerializeToString()
        for item in before.graph.initializer
    }
    after_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    initializers = initializer_map(after)
    return {
        "source": receipt(source),
        "transformed": receipt(destination),
        "endpoint_command_x_m_s": endpoint_command_x_m_s,
        "eight_nodes_inserted": (
            len(after_nodes) == len(before_nodes) + len(inserted)
        ),
        "actor_observation_rewire_exact": (
            list(expected_center.input)
            == ["t162_policy_obs", "obs_mean"]
        ),
        "all_source_nodes_otherwise_byte_exact": (
            source_nodes_exact and old_index == len(before_nodes)
        ),
        "existing_initializers_byte_exact": all(
            after_initializers.get(name) == value
            for name, value in before_initializers.items()
        ),
        "three_initializers_added": (
            set(after_initializers) - set(before_initializers)
            == set(additions)
        ),
        "command_index_exact": np.array_equal(
            numpy_helper.to_array(
                initializers["t162_gather_command_index"]
            ),
            additions["t162_gather_command_index"],
        )
        and np.array_equal(
            numpy_helper.to_array(
                initializers["t162_scatter_command_index"]
            ),
            additions["t162_scatter_command_index"],
        ),
        "endpoint_exact": np.array_equal(
            numpy_helper.to_array(initializers["t162_endpoint_command"]),
            additions["t162_endpoint_command"],
        ),
        "abi_exact": abi(before) == abi(after),
    }


def inference_contract(
    source: Path,
    transformed: Path,
    contexts: list[dict[str, Any]],
    endpoint_command_x_m_s: float,
    seed: int,
) -> dict[str, Any]:
    source_session = ort.InferenceSession(
        str(source), providers=["CPUExecutionProvider"]
    )
    transformed_session = ort.InferenceSession(
        str(transformed), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(seed)
    rows = []
    all_exact = True
    all_finite = True
    for context_row in contexts:
        positive = context_row["population"] == "com_x_positive"
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        for command in (-0.08, 0.0, 0.074, 0.077, 0.08):
            expected_command = (
                endpoint_command_x_m_s
                if positive and command > 0.001
                else command
            )
            exact = True
            finite = True
            for _ in range(32):
                obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
                obs[0, 6] = np.float32(command)
                previous_action = rng.uniform(
                    -0.9, 0.9, (1, 14)
                ).astype(np.float32)
                hidden = rng.uniform(-0.9, 0.9, (1, 64)).astype(np.float32)
                transformed_outputs = transformed_session.run(
                    None,
                    {
                        "obs": obs,
                        "previous_action": previous_action,
                        "h_in": hidden,
                        "calibration_context": context,
                    },
                )
                reference_obs = obs.copy()
                reference_obs[0, 6] = np.float32(expected_command)
                reference_outputs = source_session.run(
                    None,
                    {
                        "obs": reference_obs,
                        "previous_action": previous_action,
                        "h_in": hidden,
                        "calibration_context": context,
                    },
                )
                exact &= all(
                    np.array_equal(actual, expected)
                    for actual, expected in zip(
                        transformed_outputs, reference_outputs
                    )
                )
                finite &= all(
                    np.all(np.isfinite(output))
                    for output in transformed_outputs
                )
            rows.append(
                {
                    "population": context_row["population"],
                    "fit_id": context_row["fit_id"],
                    "external_command_x_m_s": command,
                    "expected_policy_command_x_m_s": expected_command,
                    "samples": 32,
                    "all_outputs_bit_exact": bool(exact),
                    "all_outputs_finite": bool(finite),
                }
            )
            all_exact &= exact
            all_finite &= finite
    return {
        "provider": transformed_session.get_providers()[0],
        "rows": rows,
        "samples": sum(row["samples"] for row in rows),
        "all_outputs_bit_exact": bool(all_exact),
        "all_outputs_finite": bool(all_finite),
        "x0_source_exact": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["external_command_x_m_s"] == 0.0
        ),
        "nonpositive_context_source_exact": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["population"] != "com_x_positive"
        ),
        "positive_moving_endpoint_exact": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["population"] == "com_x_positive"
            and row["external_command_x_m_s"] > 0.001
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T162 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T162 execution requires a clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T162_EXACT_COMMAND_ENDPOINT_TRANSFORM"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T162 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for item in prereg["source_graphs"]:
        verify(item)

    contexts = prereg["contexts"]
    outputs = []
    started = time.time()
    for graph in prereg["source_graphs"]:
        step = str(graph["step"])
        endpoint = float(
            prereg["endpoint_command_by_step_x_m_s"][step]
        )
        destination = WORK / step / "command_endpoint_router.onnx"
        structure = transform(
            Path(graph["path"]),
            destination,
            endpoint,
        )
        inference = inference_contract(
            Path(graph["path"]),
            destination,
            contexts,
            endpoint,
            int(prereg["inference"]["seed"]) + int(step),
        )
        outputs.append(
            {
                "step": int(step),
                "structure": structure,
                "inference": inference,
            }
        )

    checks = {
        "two_graphs": len(outputs) == 2,
        "all_eight_nodes_inserted": all(
            row["structure"]["eight_nodes_inserted"] for row in outputs
        ),
        "all_actor_rewires_exact": all(
            row["structure"]["actor_observation_rewire_exact"]
            for row in outputs
        ),
        "all_source_nodes_otherwise_byte_exact": all(
            row["structure"]["all_source_nodes_otherwise_byte_exact"]
            for row in outputs
        ),
        "all_existing_initializers_byte_exact": all(
            row["structure"]["existing_initializers_byte_exact"]
            for row in outputs
        ),
        "all_three_initializers_added": all(
            row["structure"]["three_initializers_added"]
            for row in outputs
        ),
        "all_abis_exact": all(
            row["structure"]["abi_exact"] for row in outputs
        ),
        "all_outputs_bit_exact": all(
            row["inference"]["all_outputs_bit_exact"] for row in outputs
        ),
        "all_outputs_finite": all(
            row["inference"]["all_outputs_finite"] for row in outputs
        ),
        "all_x0_source_exact": all(
            row["inference"]["x0_source_exact"] for row in outputs
        ),
        "all_nonpositive_context_source_exact": all(
            row["inference"]["nonpositive_context_source_exact"]
            for row in outputs
        ),
        "all_positive_moving_endpoint_exact": all(
            row["inference"]["positive_moving_endpoint_exact"]
            for row in outputs
        ),
        "cpu_only": all(
            row["inference"]["provider"] == "CPUExecutionProvider"
            for row in outputs
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_T162_EXACT_COMMAND_ENDPOINT_TRANSFORM"
        if not failed
        else "HOLD_T162_EXACT_COMMAND_ENDPOINT_TRANSFORM"
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t162_exact_command_endpoint_transform_result.v1"
        ),
        "status": status,
        "decision": (
            "EARN_T163_COMMAND_ENDPOINT_POSITIVE_MATRIX_PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_COMMAND_ENDPOINT_REPLAY_REPAIR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "execution": {
            "inference_samples": sum(
                row["inference"]["samples"] for row in outputs
            ),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "positive_matrix_preregistration": not failed,
            "behavior_matrix": False,
            "full_r2": False,
            "training": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T162 exact command-endpoint transform result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Exact inference samples: "
        f"`{value['execution']['inference_samples']}`\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
