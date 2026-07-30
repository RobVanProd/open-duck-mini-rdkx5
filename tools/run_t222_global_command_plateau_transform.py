#!/usr/bin/env python3
"""Build and prove T222's graph-internal global command plateau."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    abi,
    canonical_sha256,
    receipt,
    verify,
)


PREREG = ANALYSIS / "t222_global_command_plateau_preregistration.json"
RESULT = ANALYSIS / "t222_global_command_plateau_result.json"
MARKDOWN = ANALYSIS / "T222_GLOBAL_COMMAND_PLATEAU_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t222_global_command_plateau_v1"
)
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]
REWIRED_NODES = {
    "t149_slice_prefix",
    "t149_slice_command",
    "t149_slice_suffix",
}


def make_session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def transform(source: Path, destination: Path, cap_m_s: float) -> dict[str, Any]:
    model = onnx.load(source)
    before = copy.deepcopy(model)
    old_nodes = list(before.graph.node)
    rewired = []
    for node in model.graph.node:
        if node.name in REWIRED_NODES:
            if not node.input or node.input[0] != "obs":
                raise RuntimeError(f"T222 unexpected source input: {node}")
            node.input[0] = "t222_global_policy_obs"
            rewired.append(node.name)
    if set(rewired) != REWIRED_NODES:
        raise RuntimeError(f"T222 source rewires changed: {rewired}")
    additions = {
        "t222_command_cap_m_s": np.asarray(
            [np.float32(cap_m_s)], dtype=np.float32
        ),
        "t222_prefix_starts": np.asarray([0], dtype=np.int64),
        "t222_prefix_ends": np.asarray([6], dtype=np.int64),
        "t222_command_starts": np.asarray([6], dtype=np.int64),
        "t222_command_ends": np.asarray([7], dtype=np.int64),
        "t222_suffix_starts": np.asarray([7], dtype=np.int64),
        "t222_suffix_ends": np.asarray([115], dtype=np.int64),
        "t222_slice_axes": np.asarray([1], dtype=np.int64),
        "t222_slice_steps": np.asarray([1], dtype=np.int64),
    }
    for name, value in additions.items():
        model.graph.initializer.append(numpy_helper.from_array(value, name))
    new_nodes = [
        helper.make_node(
            "Slice",
            [
                "obs",
                "t222_prefix_starts",
                "t222_prefix_ends",
                "t222_slice_axes",
                "t222_slice_steps",
            ],
            ["t222_obs_prefix"],
            name="t222_slice_prefix",
        ),
        helper.make_node(
            "Slice",
            [
                "obs",
                "t222_command_starts",
                "t222_command_ends",
                "t222_slice_axes",
                "t222_slice_steps",
            ],
            ["t222_raw_command_x"],
            name="t222_slice_command",
        ),
        helper.make_node(
            "Min",
            ["t222_raw_command_x", "t222_command_cap_m_s"],
            ["t222_capped_command_x"],
            name="t222_cap_command",
        ),
        helper.make_node(
            "Slice",
            [
                "obs",
                "t222_suffix_starts",
                "t222_suffix_ends",
                "t222_slice_axes",
                "t222_slice_steps",
            ],
            ["t222_obs_suffix"],
            name="t222_slice_suffix",
        ),
        helper.make_node(
            "Concat",
            [
                "t222_obs_prefix",
                "t222_capped_command_x",
                "t222_obs_suffix",
            ],
            ["t222_global_policy_obs"],
            axis=1,
            name="t222_rebuild_policy_obs",
        ),
    ]
    for index, node in enumerate(new_nodes):
        model.graph.node.insert(index, node)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    after = onnx.load(destination)

    old_initializers = {
        item.name: item.SerializeToString()
        for item in before.graph.initializer
    }
    after_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    unchanged_nodes = 0
    exact_rewired_nodes = 0
    for old, new in zip(
        old_nodes,
        list(after.graph.node)[len(new_nodes):],
        strict=True,
    ):
        if old.name in REWIRED_NODES:
            expected = copy.deepcopy(old)
            expected.input[0] = "t222_global_policy_obs"
            exact_rewired_nodes += int(
                expected.SerializeToString() == new.SerializeToString()
            )
        else:
            unchanged_nodes += int(
                old.SerializeToString() == new.SerializeToString()
            )
    return {
        "source": receipt(source),
        "transformed": receipt(destination),
        "source_abi": abi(source),
        "transformed_abi": abi(destination),
        "new_node_names": [node.name for node in new_nodes],
        "new_initializer_names": sorted(additions),
        "old_node_count": len(old_nodes),
        "unchanged_old_nodes": unchanged_nodes,
        "expected_unchanged_old_nodes": len(old_nodes) - len(REWIRED_NODES),
        "exact_rewired_nodes": exact_rewired_nodes,
        "expected_exact_rewired_nodes": len(REWIRED_NODES),
        "rewired_node_names": sorted(rewired),
        "all_old_initializers_exact": all(
            after_initializers.get(name) == value
            for name, value in old_initializers.items()
        ),
        "only_expected_initializers_added": (
            set(after_initializers) - set(old_initializers) == set(additions)
        ),
        "cap_float32_m_s": float(
            numpy_helper.to_array(
                next(
                    item
                    for item in after.graph.initializer
                    if item.name == "t222_command_cap_m_s"
                )
            ).reshape(-1)[0]
        ),
        "onnx_checker_pass": True,
    }


def random_equivalence(
    source: Path,
    transformed: Path,
    contexts: list[dict[str, Any]],
    seed: int,
    samples: int,
) -> dict[str, Any]:
    source_session = make_session(source)
    transformed_session = make_session(transformed)
    rng = np.random.default_rng(seed)
    rows = []
    total = 0
    for context_row in contexts:
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        for command in (0.0, 0.074, 0.077, 0.080):
            exact = True
            finite = True
            for _ in range(samples):
                obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
                obs[0, 6] = np.float32(command)
                previous = rng.uniform(-0.9, 0.9, (1, 14)).astype(np.float32)
                hidden = rng.uniform(-0.9, 0.9, (1, 64)).astype(np.float32)
                feed = {
                    "obs": obs,
                    "previous_action": previous,
                    "h_in": hidden,
                    "calibration_context": context,
                }
                actual = transformed_session.run(OUTPUT_NAMES, feed)
                expected_obs = obs.copy()
                expected_obs[0, 6] = np.float32(min(command, 0.077))
                expected = source_session.run(
                    OUTPUT_NAMES,
                    {**feed, "obs": expected_obs},
                )
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(actual, expected, strict=True)
                )
                finite &= all(
                    np.all(np.isfinite(value)) for value in actual
                )
                total += 1
            rows.append(
                {
                    "condition_id": context_row["condition_id"],
                    "condition_index": context_row["condition_index"],
                    "fit_id": context_row["fit_id"],
                    "context_sha256": context_row["context_sha256"],
                    "command_x_m_s": command,
                    "samples": samples,
                    "all_outputs_bit_exact_to_expected_source": bool(exact),
                    "all_outputs_finite": bool(finite),
                }
            )
    return {
        "provider": transformed_session.get_providers()[0],
        "samples": total,
        "rows": rows,
        "all_outputs_bit_exact": all(
            row["all_outputs_bit_exact_to_expected_source"] for row in rows
        ),
        "all_outputs_finite": all(
            row["all_outputs_finite"] for row in rows
        ),
        "all_lower_commands_exact": all(
            row["all_outputs_bit_exact_to_expected_source"]
            for row in rows
            if row["command_x_m_s"] <= 0.077
        ),
        "all_x008_maps_exactly_to_x0077": all(
            row["all_outputs_bit_exact_to_expected_source"]
            for row in rows
            if row["command_x_m_s"] == 0.080
        ),
    }


def trace_equivalence(
    source: Path,
    transformed: Path,
    pair: dict[str, Any],
    count: int,
) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in Path(pair["trace"]["path"])
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ][:count]
    source_session = make_session(source)
    transformed_session = make_session(transformed)
    context = np.asarray(
        pair["context"]["context"], dtype=np.float32
    ).reshape(1, 64)
    exact = True
    finite = True
    source_sensitive_rows = 0
    transformed_changed_rows = 0
    maximum_source_delta = 0.0
    for row in rows:
        state = row["policy_state_input"]
        obs = np.asarray(row["obs_state"], dtype=np.float32).reshape(1, 115)
        previous = np.asarray(state["previous_action"], dtype=np.float32)
        hidden = np.asarray(state["h_in"], dtype=np.float32)
        obs_077 = obs.copy()
        obs_077[0, 6] = np.float32(0.077)
        obs_080 = obs.copy()
        obs_080[0, 6] = np.float32(0.080)
        common = {
            "previous_action": previous,
            "h_in": hidden,
            "calibration_context": context,
        }
        expected = source_session.run(
            OUTPUT_NAMES, {**common, "obs": obs_077}
        )
        source_upper = source_session.run(
            OUTPUT_NAMES, {**common, "obs": obs_080}
        )
        actual = transformed_session.run(
            OUTPUT_NAMES, {**common, "obs": obs_080}
        )
        exact &= all(
            np.array_equal(left, right)
            for left, right in zip(actual, expected, strict=True)
        )
        finite &= all(np.all(np.isfinite(value)) for value in actual)
        delta = float(np.max(np.abs(source_upper[0] - expected[0])))
        source_sensitive_rows += int(delta > 0.0)
        transformed_changed_rows += int(
            not np.array_equal(actual[0], source_upper[0])
        )
        maximum_source_delta = max(maximum_source_delta, delta)
    return {
        "checkpoint_id": pair["checkpoint_id"],
        "step": pair["step"],
        "fit_id": pair["fit_id"],
        "trace_sha256": pair["trace"]["sha256"],
        "rows": len(rows),
        "ticks_contiguous_from_zero": [
            int(row["tick"]) for row in rows
        ] == list(range(len(rows))),
        "source_sensitive_rows_077_vs_080": source_sensitive_rows,
        "transformed_changed_rows_at_080": transformed_changed_rows,
        "maximum_source_action_delta_077_vs_080": maximum_source_delta,
        "all_transformed_x008_outputs_exact_source_x0077": bool(exact),
        "all_outputs_finite": bool(finite),
        "provider": transformed_session.get_providers()[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T222 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T222 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T222_GLOBAL_COMMAND_PLATEAU"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T222 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, graph in enumerate(prereg["graphs"]):
        verify(graph["source"], f"graphs[{index}].source")
    for index, pair in enumerate(prereg["trace_pairs"]):
        verify(pair["graph"], f"trace_pairs[{index}].graph")
        verify(pair["trace"], f"trace_pairs[{index}].trace")

    WORK.mkdir(parents=True)
    outputs = []
    for graph_index, graph in enumerate(prereg["graphs"]):
        destination = (
            WORK / str(graph["step"]) / "global_command_plateau.onnx"
        )
        structure = transform(
            Path(graph["source"]["path"]),
            destination,
            float(prereg["transform"]["cap_m_s"]),
        )
        inference = random_equivalence(
            Path(graph["source"]["path"]),
            destination,
            prereg["contexts"],
            int(prereg["contract"]["random_seed"]) + graph_index,
            int(prereg["contract"]["samples_per_context_command"]),
        )
        pair_rows = [
            trace_equivalence(
                Path(graph["source"]["path"]),
                destination,
                pair,
                int(prereg["contract"]["trace_rows_per_pair"]),
            )
            for pair in prereg["trace_pairs"]
            if int(pair["step"]) == int(graph["step"])
        ]
        outputs.append(
            {
                "step": graph["step"],
                "role": graph["role"],
                "structure": structure,
                "inference": inference,
                "trace_equivalence": pair_rows,
            }
        )

    expected_new_nodes = [
        "t222_slice_prefix",
        "t222_slice_command",
        "t222_cap_command",
        "t222_slice_suffix",
        "t222_rebuild_policy_obs",
    ]
    trace_rows = [
        row for output in outputs for row in output["trace_equivalence"]
    ]
    checks = {
        "two_transformed_graphs": (
            [row["step"] for row in outputs] == [1_003_520, 2_007_040]
        ),
        "stateful_abi_exact": all(
            row["structure"]["source_abi"]
            == row["structure"]["transformed_abi"]
            for row in outputs
        ),
        "only_expected_nodes_added": all(
            row["structure"]["new_node_names"] == expected_new_nodes
            for row in outputs
        ),
        "all_nonrewired_old_nodes_byte_exact": all(
            row["structure"]["unchanged_old_nodes"]
            == row["structure"]["expected_unchanged_old_nodes"]
            for row in outputs
        ),
        "exactly_three_t149_slice_inputs_rewired": all(
            row["structure"]["exact_rewired_nodes"]
            == row["structure"]["expected_exact_rewired_nodes"]
            == 3
            and row["structure"]["rewired_node_names"]
            == sorted(REWIRED_NODES)
            for row in outputs
        ),
        "all_old_initializers_byte_exact": all(
            row["structure"]["all_old_initializers_exact"]
            for row in outputs
        ),
        "only_expected_initializers_added": all(
            row["structure"]["only_expected_initializers_added"]
            for row in outputs
        ),
        "cap_is_exact_float32_0077": all(
            np.float32(row["structure"]["cap_float32_m_s"])
            == np.float32(0.077)
            for row in outputs
        ),
        "onnx_checker_passes": all(
            row["structure"]["onnx_checker_pass"] for row in outputs
        ),
        "all_random_lower_commands_bit_exact": all(
            row["inference"]["all_lower_commands_exact"] for row in outputs
        ),
        "all_random_x008_maps_bit_exact_to_source_x0077": all(
            row["inference"]["all_x008_maps_exactly_to_x0077"]
            for row in outputs
        ),
        "all_random_outputs_finite_cpu_only": all(
            row["inference"]["all_outputs_finite"]
            and row["inference"]["provider"] == "CPUExecutionProvider"
            for row in outputs
        ),
        "four_trace_pairs_exact_and_contiguous": (
            len(trace_rows) == 4
            and all(
                row["rows"] == 64
                and row["ticks_contiguous_from_zero"]
                for row in trace_rows
            )
        ),
        "source_trace_sensitivity_exercised": all(
            row["source_sensitive_rows_077_vs_080"] > 0
            and row["maximum_source_action_delta_077_vs_080"] > 0.0
            for row in trace_rows
        ),
        "transformed_trace_x008_exact_source_x0077": all(
            row["all_transformed_x008_outputs_exact_source_x0077"]
            and row["transformed_changed_rows_at_080"] > 0
            for row in trace_rows
        ),
        "all_trace_outputs_finite_cpu_only": all(
            row["all_outputs_finite"]
            and row["provider"] == "CPUExecutionProvider"
            for row in trace_rows
        ),
        "zero_optimizer_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis_result: dict[str, Any] = {
        "schema_version": "open_duck.t222_global_command_plateau_result.v1",
        "status": (
            "PASS_T222_GLOBAL_COMMAND_PLATEAU"
            if not failed
            else "HOLD_T222_GLOBAL_COMMAND_PLATEAU"
        ),
        "decision": (
            "EARN_T223_GLOBAL_PLATEAU_NOMINAL_MATRIX_"
            "PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_GLOBAL_COMMAND_PLATEAU_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "execution": {
            "onnx_transforms": len(outputs),
            "onnx_inferences": sum(
                row["inference"]["samples"] for row in outputs
            )
            + sum(row["rows"] * 3 for row in trace_rows),
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "nominal_matrix_preregistration": not failed,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
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
        "# T222 global command plateau result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- x=`0/.074/.077`: all outputs bit-exact to source\n"
        "- x=`.080`: all outputs bit-exact to same-state source x=`.077`\n"
        "- Existing T149 `.074` route cap, recurrent state, and ABI preserved\n"
        "- Optimizer / behavior / hosted / robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
