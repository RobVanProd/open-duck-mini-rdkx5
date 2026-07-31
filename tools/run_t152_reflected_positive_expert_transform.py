#!/usr/bin/env python3
"""Build and prove T152's reflected positive-COM expert graphs."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import onnx
import onnxruntime as ort
from onnx import numpy_helper

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    abi,
    canonical_sha256,
    receipt,
    verify,
)


PREREG = ANALYSIS / "t152_reflected_positive_expert_preregistration.json"
RESULT = ANALYSIS / "t152_reflected_positive_expert_result.json"
MARKDOWN = (
    ANALYSIS / "T152_REFLECTED_POSITIVE_EXPERT_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t152_reflected_positive_expert_v1"
)
STEPS = (1_003_520, 2_007_040)
REFLECTED_WEIGHT = "negative_adapter_weight"
REFLECTED_BIAS = "negative_adapter_bias"
NOMINAL_WEIGHT = "nominal_condition_negative_adapter_weight"
NOMINAL_BIAS = "nominal_condition_negative_adapter_bias"
SELECT_NODE = "t143_select_forward_path"
FORCE_TRUE = "t152_force_reflected_positive"


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T152_REFLECTED_POSITIVE_EXPERT"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T152 preregistration identity changed")
    for name, item in value["frozen_inputs"].items():
        verify(item, name)


def initializer_arrays(
    model: onnx.ModelProto,
) -> dict[str, np.ndarray]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def replace_initializer(
    model: onnx.ModelProto, name: str, value: np.ndarray
) -> None:
    matches = [
        index
        for index, item in enumerate(model.graph.initializer)
        if item.name == name
    ]
    if len(matches) != 1:
        raise RuntimeError(f"T152 expected one initializer {name}")
    model.graph.initializer[matches[0]].CopyFrom(
        numpy_helper.from_array(np.asarray(value), name)
    )


def transform(source: Path, destination: Path) -> dict[str, Any]:
    before = onnx.load(source)
    model = copy.deepcopy(before)
    arrays = initializer_arrays(before)
    required = {
        REFLECTED_WEIGHT,
        REFLECTED_BIAS,
        NOMINAL_WEIGHT,
        NOMINAL_BIAS,
    }
    if not required.issubset(arrays):
        raise RuntimeError(
            f"T152 source is missing expert tensors: {required-arrays.keys()}"
        )
    reflected = {
        REFLECTED_WEIGHT: (
            np.float32(2.0) * arrays[NOMINAL_WEIGHT]
            - arrays[REFLECTED_WEIGHT]
        ).astype(np.float32),
        REFLECTED_BIAS: (
            np.float32(2.0) * arrays[NOMINAL_BIAS]
            - arrays[REFLECTED_BIAS]
        ).astype(np.float32),
    }
    for name, value in reflected.items():
        replace_initializer(model, name, value)

    if FORCE_TRUE in arrays:
        raise RuntimeError("T152 force initializer already exists")
    model.graph.initializer.append(
        numpy_helper.from_array(
            np.asarray([True], dtype=np.bool_), FORCE_TRUE
        )
    )
    selectors = [
        node for node in model.graph.node if node.name == SELECT_NODE
    ]
    if len(selectors) != 1:
        raise RuntimeError("T152 expected one T143 selector")
    selector = selectors[0]
    if (
        selector.op_type != "Where"
        or selector.input[0] != "conditional_path_negative_condition"
    ):
        raise RuntimeError("T152 selector contract changed")
    selector.input[0] = FORCE_TRUE

    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True)
    onnx.save(model, destination)
    after = onnx.load(destination)
    after_arrays = initializer_arrays(after)

    before_nodes = list(before.graph.node)
    after_nodes = list(after.graph.node)
    node_checks = []
    for old, new in zip(before_nodes, after_nodes, strict=True):
        old_copy = copy.deepcopy(old)
        if old_copy.name == SELECT_NODE:
            old_copy.input[0] = FORCE_TRUE
        node_checks.append(old_copy.SerializeToString() == new.SerializeToString())
    unchanged_initializers = [
        name
        for name in arrays
        if name not in {REFLECTED_WEIGHT, REFLECTED_BIAS}
    ]
    return {
        "source": receipt(source),
        "transformed": receipt(destination),
        "abi_exact": abi(before) == abi(after),
        "node_count_exact": len(before_nodes) == len(after_nodes),
        "all_nodes_exact_except_selector_input": all(node_checks),
        "initializer_count_delta": (
            len(after.graph.initializer) - len(before.graph.initializer)
        ),
        "new_force_initializer_exact": (
            FORCE_TRUE in after_arrays
            and after_arrays[FORCE_TRUE].dtype == np.bool_
            and after_arrays[FORCE_TRUE].shape == (1,)
            and bool(after_arrays[FORCE_TRUE][0])
        ),
        "unchanged_initializers_bit_exact": all(
            np.array_equal(arrays[name], after_arrays[name])
            for name in unchanged_initializers
        ),
        "reflected_weight_bit_exact": np.array_equal(
            reflected[REFLECTED_WEIGHT],
            after_arrays[REFLECTED_WEIGHT],
        ),
        "reflected_bias_bit_exact": np.array_equal(
            reflected[REFLECTED_BIAS],
            after_arrays[REFLECTED_BIAS],
        ),
        "weight_reflection_delta_linf": float(
            np.max(
                np.abs(
                    reflected[REFLECTED_WEIGHT].astype(np.float64)
                    - arrays[NOMINAL_WEIGHT].astype(np.float64)
                )
            )
        ),
        "bias_reflection_delta_linf": float(
            np.max(
                np.abs(
                    reflected[REFLECTED_BIAS].astype(np.float64)
                    - arrays[NOMINAL_BIAS].astype(np.float64)
                )
            )
        ),
        "selector_forced_exact": (
            len(
                [
                    node
                    for node in after.graph.node
                    if node.name == SELECT_NODE
                    and node.input[0] == FORCE_TRUE
                ]
            )
            == 1
        ),
    }


def session(path: Path) -> ort.InferenceSession:
    return ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )


def run(
    active: ort.InferenceSession,
    obs: np.ndarray,
    previous: np.ndarray,
    hidden: np.ndarray,
    context: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = active.run(
        None,
        {
            "obs": obs.astype(np.float32),
            "previous_action": previous.astype(np.float32),
            "h_in": hidden.astype(np.float32),
            "calibration_context": context.astype(np.float32),
        },
    )
    names = [item.name for item in active.get_outputs()]
    result = dict(zip(names, values, strict=True))
    return (
        np.asarray(result["continuous_actions"], dtype=np.float32),
        np.asarray(result["previous_action_out"], dtype=np.float32),
        np.asarray(result["h_out"], dtype=np.float32),
    )


def cpu_contract(
    source: Path,
    transformed: Path,
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    left = session(source)
    right = session(transformed)
    rng = np.random.default_rng(152)
    steps = int(thresholds["random_chain_steps"])
    hidden_left = np.zeros((1, 64), dtype=np.float32)
    hidden_right = hidden_left.copy()
    previous_left = np.zeros((1, 14), dtype=np.float32)
    previous_right = previous_left.copy()
    maximum_hidden_error = 0.0
    maximum_context_dependence_error = 0.0
    changed = 0
    finite = True
    for _ in range(steps):
        obs = rng.normal(0.0, 0.35, size=(1, 115)).astype(np.float32)
        obs[:, 6] = np.float32(
            rng.choice(np.asarray([0.074, 0.077, 0.080]))
        )
        context_a = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        context_b = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        source_values = run(
            left, obs, previous_left, hidden_left, context_a
        )
        reflected_a = run(
            right, obs, previous_right, hidden_right, context_a
        )
        reflected_b = run(
            right, obs, previous_right, hidden_right, context_b
        )
        changed += int(
            not np.array_equal(source_values[0], reflected_a[0])
        )
        maximum_hidden_error = max(
            maximum_hidden_error,
            float(np.max(np.abs(source_values[2] - reflected_a[2]))),
        )
        maximum_context_dependence_error = max(
            maximum_context_dependence_error,
            max(
                float(np.max(np.abs(a - b)))
                for a, b in zip(reflected_a, reflected_b, strict=True)
            ),
        )
        finite &= all(np.all(np.isfinite(value)) for value in reflected_a)
        previous_left = source_values[1]
        hidden_left = source_values[2]
        previous_right = reflected_a[1]
        hidden_right = reflected_a[2]

    x0_samples = int(thresholds["x0_samples"])
    maximum_x0_action_abs = 0.0
    x0_feedback_exact = True
    x0_hidden_exact = True
    for _ in range(x0_samples):
        obs = rng.normal(0.0, 0.35, size=(1, 115)).astype(np.float32)
        obs[:, 6] = np.float32(0.0)
        previous = rng.uniform(-0.8, 0.8, size=(1, 14)).astype(np.float32)
        hidden = rng.normal(0.0, 0.5, size=(1, 64)).astype(np.float32)
        context = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        source_values = run(left, obs, previous, hidden, context)
        reflected_values = run(right, obs, previous, hidden, context)
        maximum_x0_action_abs = max(
            maximum_x0_action_abs,
            float(np.max(np.abs(reflected_values[0]))),
        )
        x0_feedback_exact &= np.array_equal(
            reflected_values[0], reflected_values[1]
        )
        x0_hidden_exact &= np.array_equal(
            source_values[2], reflected_values[2]
        )
    return {
        "providers": right.get_providers(),
        "steps": steps,
        "finite": bool(finite),
        "moving_action_changed_steps": changed,
        "moving_action_changed_fraction": changed / steps,
        "maximum_hidden_state_error": maximum_hidden_error,
        "maximum_context_dependence_error": (
            maximum_context_dependence_error
        ),
        "x0_samples": x0_samples,
        "maximum_x0_action_abs": maximum_x0_action_abs,
        "x0_action_feedback_exact": bool(x0_feedback_exact),
        "x0_hidden_output_exact": bool(x0_hidden_exact),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    del args
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T152: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to reuse T152 work root: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T152 execution requires clean tree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    WORK.mkdir(parents=True)
    graph_contracts: dict[str, Any] = {}
    cpu_contracts: dict[str, Any] = {}
    for step in STEPS:
        source = Path(prereg["frozen_inputs"][f"source_graph_{step}"]["path"])
        destination = WORK / str(step) / "reflected_positive_expert.onnx"
        graph_contracts[str(step)] = transform(source, destination)
        cpu_contracts[str(step)] = cpu_contract(
            source, destination, prereg["thresholds"]
        )

    thresholds = prereg["thresholds"]
    checks = {
        "both_graphs_transformed": sorted(graph_contracts)
        == [str(step) for step in STEPS],
        "graph_structure_exact": all(
            row["abi_exact"]
            and row["node_count_exact"]
            and row["all_nodes_exact_except_selector_input"]
            and row["initializer_count_delta"] == 1
            and row["new_force_initializer_exact"]
            and row["unchanged_initializers_bit_exact"]
            and row["reflected_weight_bit_exact"]
            and row["reflected_bias_bit_exact"]
            and row["selector_forced_exact"]
            for row in graph_contracts.values()
        ),
        "reflected_actions_finite_and_bound": all(
            row["providers"][0] == "CPUExecutionProvider"
            and row["finite"]
            and row["moving_action_changed_fraction"]
            >= thresholds["minimum_moving_action_changed_fraction"]
            for row in cpu_contracts.values()
        ),
        "hidden_state_path_unchanged": all(
            row["maximum_hidden_state_error"]
            == thresholds["maximum_hidden_state_error"]
            and row["x0_hidden_output_exact"]
            for row in cpu_contracts.values()
        ),
        "forced_branch_context_invariant": all(
            row["maximum_context_dependence_error"]
            == thresholds["maximum_context_dependence_error"]
            for row in cpu_contracts.values()
        ),
        "x0_exact_zero_and_feedback": all(
            row["maximum_x0_action_abs"]
            == thresholds["maximum_x0_action_abs"]
            and row["x0_action_feedback_exact"]
            for row in cpu_contracts.values()
        ),
        "no_behavior_optimizer_hosted_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t152_reflected_positive_expert_result.v1"
        ),
        "status": (
            "PASS_T152_REFLECTED_POSITIVE_EXPERT"
            if passed
            else "HOLD_T152_REFLECTED_POSITIVE_EXPERT"
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
        "mechanism": prereg["mechanism"],
        "graphs": graph_contracts,
        "cpu_contracts": cpu_contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "environment_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "positive_endpoint_preregistration": passed,
            "positive_endpoint_execution": False,
            "positive_only_training_contract": False,
            "hosted_training": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T152 reflected positive expert result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Reflection: `positive = 2*nominal - negative`\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
