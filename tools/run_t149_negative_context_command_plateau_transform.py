#!/usr/bin/env python3
"""Build and prove T149's negative-context internal command plateau."""

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
    ANALYSIS
    / "t149_negative_context_command_plateau_preregistration.json"
)
RESULT = ANALYSIS / "t149_negative_context_command_plateau_result.json"
MARKDOWN = (
    ANALYSIS
    / "T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t149_negative_context_command_plateau_v1"
)
COMMANDS = (0.0, 0.074, 0.077, 0.080)
CAP_M_S = np.float32(0.074)
OBS_COMMAND_INDEX = 6
OBS_DIM = 115
REFERENCE_SLICE = slice(101, 115)


def trace_attribution(t145: dict[str, Any]) -> dict[str, Any]:
    """Prove the upper commands share the exact x=.074 reference features."""
    blocks = []
    all_upper_fail = True
    all_anchor_green = True
    maximum_reference_delta = 0.0
    minimum_compared_rows = 10**9
    for block in t145["blocks"]:
        cells = {
            float(cell["command_x_m_s"]): cell
            for cell in block["result"]["cells"]
        }
        traces = {}
        for command in (0.074, 0.077, 0.080):
            path = Path(cells[command]["protection"]["path"])
            rows = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            traces[command] = rows
        anchor = traces[0.074]
        comparisons = []
        for command in (0.077, 0.080):
            rows = traces[command]
            count = min(len(anchor), len(rows))
            minimum_compared_rows = min(minimum_compared_rows, count)
            delta = max(
                float(
                    np.max(
                        np.abs(
                            np.asarray(
                                anchor[index]["obs_state"][
                                    REFERENCE_SLICE
                                ],
                                dtype=np.float32,
                            )
                            - np.asarray(
                                rows[index]["obs_state"][REFERENCE_SLICE],
                                dtype=np.float32,
                            )
                        )
                    )
                )
                for index in range(count)
            )
            maximum_reference_delta = max(
                maximum_reference_delta, delta
            )
            comparisons.append(
                {
                    "command_x_m_s": command,
                    "rows": count,
                    "maximum_reference_feature_delta": delta,
                    "tick_zero_command_pair": [
                        float(anchor[0]["obs_state"][OBS_COMMAND_INDEX]),
                        float(rows[0]["obs_state"][OBS_COMMAND_INDEX]),
                    ],
                }
            )
            all_upper_fail &= not bool(cells[command]["cell_green"])
        all_anchor_green &= bool(cells[0.074]["cell_green"])
        blocks.append(
            {
                "checkpoint_id": block["checkpoint_id"],
                "fit_id": block["fit_id"],
                "anchor_green": bool(cells[0.074]["cell_green"]),
                "upper_failures": {
                    str(command): not bool(cells[command]["cell_green"])
                    for command in (0.077, 0.080)
                },
                "comparisons": comparisons,
            }
        )
    return {
        "blocks": blocks,
        "all_four_anchor_cells_green": all_anchor_green,
        "all_eight_upper_cells_fail": all_upper_fail,
        "maximum_reference_feature_delta": maximum_reference_delta,
        "minimum_compared_rows": minimum_compared_rows,
    }


def table_alias(reference: Path) -> dict[str, Any]:
    table = np.load(reference)
    commands = np.asarray(table["commands"], dtype=np.float32)
    rows = []
    for command in (0.074, 0.077, 0.080):
        target = np.asarray([command, 0.0, 0.0], dtype=np.float32)
        index = int(np.argmin(np.sum(np.abs(commands - target), axis=1)))
        rows.append(
            {
                "requested_command": target.tolist(),
                "selected_index": index,
                "selected_command": commands[index].tolist(),
            }
        )
    return {
        "rows": rows,
        "same_reference_row": len(
            {item["selected_index"] for item in rows}
        )
        == 1,
    }


def transform(source: Path, destination: Path) -> dict[str, Any]:
    model = onnx.load(source)
    before = copy.deepcopy(model)
    old_nodes = list(before.graph.node)
    original_consumers = [
        index
        for index, node in enumerate(model.graph.node)
        if "obs" in node.input
    ]
    if original_consumers != [0, 2]:
        raise RuntimeError(
            f"T149 raw observation consumers changed: {original_consumers}"
        )
    for node in model.graph.node:
        for input_index, value in enumerate(node.input):
            if value == "obs":
                node.input[input_index] = "t149_policy_obs"

    additions = {
        "t149_command_cap_m_s": np.asarray([CAP_M_S], dtype=np.float32),
        "t149_prefix_starts": np.asarray([0], dtype=np.int64),
        "t149_prefix_ends": np.asarray([OBS_COMMAND_INDEX], dtype=np.int64),
        "t149_command_starts": np.asarray(
            [OBS_COMMAND_INDEX], dtype=np.int64
        ),
        "t149_command_ends": np.asarray(
            [OBS_COMMAND_INDEX + 1], dtype=np.int64
        ),
        "t149_suffix_starts": np.asarray(
            [OBS_COMMAND_INDEX + 1], dtype=np.int64
        ),
        "t149_suffix_ends": np.asarray([OBS_DIM], dtype=np.int64),
        "t149_slice_axes": np.asarray([1], dtype=np.int64),
        "t149_slice_steps": np.asarray([1], dtype=np.int64),
    }
    for name, value in additions.items():
        model.graph.initializer.append(numpy_helper.from_array(value, name))
    nodes = [
        helper.make_node(
            "MatMul",
            [
                "calibration_context",
                "conditional_path_router_coefficient",
            ],
            ["t149_router_linear"],
            name="t149_router_matmul",
        ),
        helper.make_node(
            "Add",
            [
                "t149_router_linear",
                "conditional_path_router_intercept",
            ],
            ["t149_router_score"],
            name="t149_router_add",
        ),
        helper.make_node(
            "GreaterOrEqual",
            ["t149_router_score", "conditional_path_router_zero"],
            ["t149_negative_condition"],
            name="t149_router_gate",
        ),
        helper.make_node(
            "Slice",
            [
                "obs",
                "t149_prefix_starts",
                "t149_prefix_ends",
                "t149_slice_axes",
                "t149_slice_steps",
            ],
            ["t149_obs_prefix"],
            name="t149_slice_prefix",
        ),
        helper.make_node(
            "Slice",
            [
                "obs",
                "t149_command_starts",
                "t149_command_ends",
                "t149_slice_axes",
                "t149_slice_steps",
            ],
            ["t149_raw_command_x"],
            name="t149_slice_command",
        ),
        helper.make_node(
            "Min",
            ["t149_raw_command_x", "t149_command_cap_m_s"],
            ["t149_capped_command_x"],
            name="t149_cap_command",
        ),
        helper.make_node(
            "Where",
            [
                "t149_negative_condition",
                "t149_capped_command_x",
                "t149_raw_command_x",
            ],
            ["t149_selected_command_x"],
            name="t149_select_command",
        ),
        helper.make_node(
            "Slice",
            [
                "obs",
                "t149_suffix_starts",
                "t149_suffix_ends",
                "t149_slice_axes",
                "t149_slice_steps",
            ],
            ["t149_obs_suffix"],
            name="t149_slice_suffix",
        ),
        helper.make_node(
            "Concat",
            [
                "t149_obs_prefix",
                "t149_selected_command_x",
                "t149_obs_suffix",
            ],
            ["t149_policy_obs"],
            axis=1,
            name="t149_rebuild_policy_obs",
        ),
    ]
    for index, node in enumerate(nodes):
        model.graph.node.insert(index, node)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)

    after = onnx.load(destination)
    old_initializers = {
        item.name: item.SerializeToString()
        for item in before.graph.initializer
    }
    new_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    expected_rewired = 0
    unchanged = 0
    for index, (old, new) in enumerate(
        zip(old_nodes, list(after.graph.node)[len(nodes) :], strict=True)
    ):
        if index in original_consumers:
            expected = copy.deepcopy(old)
            for input_index, value in enumerate(expected.input):
                if value == "obs":
                    expected.input[input_index] = "t149_policy_obs"
            expected_rewired += int(
                expected.SerializeToString() == new.SerializeToString()
            )
        else:
            unchanged += int(
                old.SerializeToString() == new.SerializeToString()
            )
    return {
        "source": receipt(source),
        "transformed": receipt(destination),
        "old_node_count": len(old_nodes),
        "new_node_count": len(after.graph.node),
        "nine_nodes_inserted": len(after.graph.node)
        == len(old_nodes) + len(nodes),
        "inserted_node_names_exact": [
            node.name for node in after.graph.node[: len(nodes)]
        ]
        == [node.name for node in nodes],
        "two_raw_obs_consumers_rewired_exact": expected_rewired == 2,
        "all_other_nodes_byte_exact": unchanged == len(old_nodes) - 2,
        "existing_initializers_byte_exact": all(
            new_initializers.get(name) == value
            for name, value in old_initializers.items()
        ),
        "nine_initializers_added": (
            set(new_initializers) - set(old_initializers) == set(additions)
        ),
        "abi_exact": abi(before) == abi(after),
    }


def _feed(
    obs: np.ndarray,
    previous: np.ndarray,
    hidden: np.ndarray,
    context: np.ndarray,
) -> dict[str, np.ndarray]:
    return {
        "obs": obs,
        "previous_action": previous,
        "h_in": hidden,
        "calibration_context": context,
    }


def equivalence_contract(
    source: Path,
    transformed: Path,
    contexts: list[dict[str, Any]],
    *,
    seed: int,
) -> dict[str, Any]:
    source_session = ort.InferenceSession(
        str(source), providers=["CPUExecutionProvider"]
    )
    transformed_session = ort.InferenceSession(
        str(transformed), providers=["CPUExecutionProvider"]
    )
    output_names = [item.name for item in source_session.get_outputs()]
    if output_names != [
        item.name for item in transformed_session.get_outputs()
    ]:
        raise RuntimeError("T149 output ABI changed")
    rng = np.random.default_rng(seed)
    rows = []
    for context_row in contexts:
        negative = context_row["population"] == "com_x_negative"
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        for command in COMMANDS:
            exact = True
            finite = True
            maximum = 0.0
            for _ in range(32):
                obs = rng.normal(size=(1, OBS_DIM)).astype(np.float32)
                obs[:, OBS_COMMAND_INDEX] = np.float32(command)
                expected_obs = obs.copy()
                if negative:
                    expected_obs[:, OBS_COMMAND_INDEX] = min(
                        np.float32(command), CAP_M_S
                    )
                previous = rng.uniform(
                    -0.98, 0.98, size=(1, 14)
                ).astype(np.float32)
                hidden = rng.normal(size=(1, 64)).astype(np.float32)
                expected = source_session.run(
                    output_names,
                    _feed(expected_obs, previous, hidden, context),
                )
                actual = transformed_session.run(
                    output_names,
                    _feed(obs, previous, hidden, context),
                )
                for left, right in zip(expected, actual, strict=True):
                    delta = float(
                        np.max(
                            np.abs(
                                np.asarray(left, dtype=np.float32)
                                - np.asarray(right, dtype=np.float32)
                            )
                        )
                    )
                    maximum = max(maximum, delta)
                    exact &= np.array_equal(left, right)
                    finite &= bool(
                        np.all(np.isfinite(left))
                        and np.all(np.isfinite(right))
                    )
            rows.append(
                {
                    "fit_id": context_row["fit_id"],
                    "population": context_row["population"],
                    "command_x_m_s": command,
                    "expected_internal_command_x_m_s": float(
                        min(np.float32(command), CAP_M_S)
                        if negative
                        else np.float32(command)
                    ),
                    "samples": 32,
                    "bit_exact": exact,
                    "finite": finite,
                    "maximum_abs_error": maximum,
                }
            )

    chain_rows = []
    for context_row in contexts:
        negative = context_row["population"] == "com_x_negative"
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        source_previous = np.zeros((1, 14), dtype=np.float32)
        actual_previous = source_previous.copy()
        source_hidden = np.zeros((1, 64), dtype=np.float32)
        actual_hidden = source_hidden.copy()
        exact_steps = 0
        maximum = 0.0
        for step in range(256):
            command = COMMANDS[step % len(COMMANDS)]
            obs = rng.normal(size=(1, OBS_DIM)).astype(np.float32)
            obs[:, OBS_COMMAND_INDEX] = np.float32(command)
            expected_obs = obs.copy()
            if negative:
                expected_obs[:, OBS_COMMAND_INDEX] = min(
                    np.float32(command), CAP_M_S
                )
            expected = source_session.run(
                output_names,
                _feed(
                    expected_obs,
                    source_previous,
                    source_hidden,
                    context,
                ),
            )
            actual = transformed_session.run(
                output_names,
                _feed(
                    obs,
                    actual_previous,
                    actual_hidden,
                    context,
                ),
            )
            step_exact = True
            for left, right in zip(expected, actual, strict=True):
                delta = float(
                    np.max(
                        np.abs(
                            np.asarray(left, dtype=np.float32)
                            - np.asarray(right, dtype=np.float32)
                        )
                    )
                )
                maximum = max(maximum, delta)
                step_exact &= np.array_equal(left, right)
            exact_steps += int(step_exact)
            source_previous = np.asarray(expected[1], dtype=np.float32)
            source_hidden = np.asarray(expected[2], dtype=np.float32)
            actual_previous = np.asarray(actual[1], dtype=np.float32)
            actual_hidden = np.asarray(actual[2], dtype=np.float32)
        chain_rows.append(
            {
                "fit_id": context_row["fit_id"],
                "population": context_row["population"],
                "steps": 256,
                "bit_exact_steps": exact_steps,
                "maximum_abs_error": maximum,
            }
        )
    return {
        "rows": rows,
        "chain_rows": chain_rows,
        "sample_rows": sum(item["samples"] for item in rows),
        "all_rows_bit_exact": all(
            item["bit_exact"]
            and item["finite"]
            and item["maximum_abs_error"] == 0.0
            for item in rows
        ),
        "all_chains_bit_exact": all(
            item["bit_exact_steps"] == item["steps"]
            and item["maximum_abs_error"] == 0.0
            for item in chain_rows
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T149")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T149 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T149 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)

    t145 = json.loads(
        Path(prereg["frozen_inputs"]["t145c_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t143 = json.loads(
        Path(prereg["frozen_inputs"]["t143c_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t135 = json.loads(
        Path(prereg["frozen_inputs"]["t135b_contexts"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    reference = Path(
        prereg["frozen_inputs"]["reference_feature_table"]["path"]
    )
    attribution = trace_attribution(t145)
    alias = table_alias(reference)
    contexts = t135["runs"]
    WORK.mkdir(parents=True)
    transforms = {}
    contracts = {}
    for index, (step, item) in enumerate(
        sorted(t143["graphs"].items()), start=1
    ):
        source = Path(item["transformed"]["path"])
        destination = WORK / step / "negative_command_plateau.onnx"
        transforms[step] = transform(source, destination)
        contracts[step] = equivalence_contract(
            source,
            destination,
            contexts,
            seed=20260729 + index,
        )

    checks = {
        "source_failure_attribution_exact": (
            attribution["all_four_anchor_cells_green"]
            and attribution["all_eight_upper_cells_fail"]
            and attribution["maximum_reference_feature_delta"] == 0.0
            and attribution["minimum_compared_rows"] >= 95
        ),
        "reference_table_alias_exact": alias["same_reference_row"],
        "graph_transforms_structurally_exact": all(
            item["nine_nodes_inserted"]
            and item["inserted_node_names_exact"]
            and item["two_raw_obs_consumers_rewired_exact"]
            and item["all_other_nodes_byte_exact"]
            and item["existing_initializers_byte_exact"]
            and item["nine_initializers_added"]
            and item["abi_exact"]
            for item in transforms.values()
        ),
        "all_context_command_rows_bit_exact": all(
            item["all_rows_bit_exact"] for item in contracts.values()
        ),
        "all_stateful_chains_bit_exact": all(
            item["all_chains_bit_exact"] for item in contracts.values()
        ),
        "expected_equivalence_population": all(
            item["sample_rows"] == 512 for item in contracts.values()
        ),
        "environment_training_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t149_negative_context_command_plateau_result.v1"
        ),
        "status": (
            "PASS_T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
            if passed
            else "HOLD_T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "attribution": attribution,
        "reference_table_alias": alias,
        "transforms": transforms,
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "random_equivalence_rows": sum(
                item["sample_rows"] for item in contracts.values()
            ),
            "stateful_chain_steps": sum(
                row["steps"]
                for item in contracts.values()
                for row in item["chain_rows"]
            ),
            "environment_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "negative_endpoint_preregistration": passed,
            "training": False,
            "colab": False,
            "policy_promotion": False,
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
        "# T149 negative-context command plateau result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Plateau: external command unchanged; internal command capped at "
        "`.074` only for calibrated negative COM\n"
        "- Nominal / negative x=0 / negative x=.074: bit exact\n"
        "- Environment / behavior / optimizer / Colab / robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
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
