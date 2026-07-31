#!/usr/bin/env python3
"""Build and prove T243's calibration-routed low-command floor."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping

import numpy as np
import onnx
from onnx import helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t243_home_negative_low_command_floor_preregistration.json"
)
RESULT = ANALYSIS / "t243_home_negative_low_command_floor_result.json"
MARKDOWN = (
    ANALYSIS / "T243_HOME_NEGATIVE_LOW_COMMAND_FLOOR_RESULT_20260731.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t243_home_negative_low_command_floor_v1"
)
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    abi,
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
        raise RuntimeError(f"changed T243 input: {path}")


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


def transform(source: Path, destination: Path) -> dict[str, Any]:
    model = onnx.load(source)
    before = copy.deepcopy(model)
    cap = next(
        node for node in model.graph.node if node.name == "t222_cap_command"
    )
    exact = next(
        node
        for node in model.graph.node
        if node.name == "t234_exact_command_gate"
    )
    if list(cap.output) != ["t222_capped_command_x"]:
        raise RuntimeError("T243 source cap output changed")
    if (
        len(exact.input) != 2
        or exact.input[0] != "t222_raw_command_x"
        or exact.input[1] != "t234_exact_command_x_m_s"
    ):
        raise RuntimeError("T243 source exact-command gate changed")
    cap.output[0] = "t243_base_capped_command_x"
    exact.input[0] = "t222_capped_command_x"
    new_nodes = [
        helper.make_node(
            "MatMul",
            ["calibration_context", "positive_router_coefficient"],
            ["t243_home_negative_router_linear"],
            name="t243_home_negative_router_matmul",
        ),
        helper.make_node(
            "Add",
            [
                "t243_home_negative_router_linear",
                "positive_router_intercept",
            ],
            ["t243_home_negative_router_score"],
            name="t243_home_negative_router_add",
        ),
        helper.make_node(
            "Greater",
            [
                "t243_home_negative_router_score",
                "t241_positive_router_upper_bound",
            ],
            ["t243_home_negative_tail_condition"],
            name="t243_home_negative_tail_gate",
        ),
        helper.make_node(
            "Equal",
            ["t222_raw_command_x", "t234_exact_command_x_m_s"],
            ["t243_exact_low_command_condition"],
            name="t243_exact_low_command_gate",
        ),
        helper.make_node(
            "And",
            [
                "t243_home_negative_tail_condition",
                "t243_exact_low_command_condition",
            ],
            ["t243_home_negative_low_command_condition"],
            name="t243_home_negative_low_command_gate",
        ),
        helper.make_node(
            "Where",
            [
                "t243_home_negative_low_command_condition",
                "t222_command_cap_m_s",
                "t243_base_capped_command_x",
            ],
            ["t222_capped_command_x"],
            name="t243_map_home_negative_low_command",
        ),
    ]
    cap_index = list(model.graph.node).index(cap)
    for offset, node in enumerate(new_nodes, start=1):
        model.graph.node.insert(cap_index + offset, node)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    after = onnx.load(destination)

    before_nodes = {
        node.name: node.SerializeToString() for node in before.graph.node
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
        "source_abi": abi(source),
        "transformed_abi": abi(destination),
        "added_nodes": [node.name for node in new_nodes],
        "changed_old_nodes": changed_old,
        "initializers_byte_exact": (
            before_initializers == after_initializers
        ),
        "initializer_names_exact": (
            set(before_initializers) == set(after_initializers)
        ),
        "onnx_checker_pass": True,
    }


def random_contract(
    source: Path,
    transformed: Path,
    contexts: list[dict[str, Any]],
    commands: list[float],
    samples: int,
    seed: int,
) -> dict[str, Any]:
    source_session = session(source)
    transformed_session = session(transformed)
    rng = np.random.default_rng(seed)
    rows = []
    for context_row in contexts:
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        for command in commands:
            target = (
                context_row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
                and command == 0.074
            )
            exact = True
            finite = True
            changed = 0
            for _ in range(samples):
                obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
                obs[0, 6] = np.float32(command)
                feed = {
                    "obs": obs,
                    "previous_action": rng.uniform(
                        -0.9, 0.9, (1, 14)
                    ).astype(np.float32),
                    "h_in": rng.uniform(
                        -0.9, 0.9, (1, 64)
                    ).astype(np.float32),
                    "calibration_context": context,
                }
                expected_obs = obs.copy()
                if target:
                    expected_obs[0, 6] = np.float32(0.077)
                expected = source_session.run(
                    OUTPUT_NAMES, {**feed, "obs": expected_obs}
                )
                actual = transformed_session.run(OUTPUT_NAMES, feed)
                original = source_session.run(OUTPUT_NAMES, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(actual, expected, strict=True)
                )
                finite &= all(
                    np.all(np.isfinite(value)) for value in actual
                )
                changed += int(
                    not np.array_equal(actual[0], original[0])
                )
            rows.append(
                {
                    "condition_id": context_row["condition_id"],
                    "fit_id": context_row["fit_id"],
                    "command_x_m_s": command,
                    "target": target,
                    "samples": samples,
                    "all_outputs_bit_exact": bool(exact),
                    "all_outputs_finite": bool(finite),
                    "continuous_action_changed_samples": changed,
                }
            )
    return {
        "provider": transformed_session.get_providers()[0],
        "rows": rows,
        "samples": len(rows) * samples,
        "all_outputs_bit_exact": all(
            row["all_outputs_bit_exact"] for row in rows
        ),
        "all_outputs_finite": all(
            row["all_outputs_finite"] for row in rows
        ),
        "all_non_targets_exact_source": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if not row["target"]
        ),
        "all_targets_exact_source_x0077": all(
            row["all_outputs_bit_exact"] for row in rows if row["target"]
        ),
        "all_targets_action_sensitive": all(
            row["continuous_action_changed_samples"] > 0
            for row in rows
            if row["target"]
        ),
        "target_rows": sum(row["target"] for row in rows),
    }


def trace_contract(
    source: Path,
    transformed: Path,
    trace: Path,
    context: list[float],
    rows_expected: int,
) -> dict[str, Any]:
    records = [
        json.loads(line)
        for line in trace.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(records) != rows_expected:
        raise RuntimeError("T243 failed-trace row count changed")
    source_session = session(source)
    transformed_session = session(transformed)
    context_value = np.asarray(context, dtype=np.float32).reshape(1, 64)
    source_replay_exact = True
    transformed_exact_077 = True
    finite = True
    changed_rows = 0
    maximum_action_delta = 0.0
    for row in records:
        obs = np.asarray(row["obs_state"], dtype=np.float32).reshape(1, 115)
        obs_077 = obs.copy()
        obs_077[0, 6] = np.float32(0.077)
        state = row["policy_state_input"]
        common = {
            "previous_action": np.asarray(
                state["previous_action"], dtype=np.float32
            ),
            "h_in": np.asarray(state["h_in"], dtype=np.float32),
            "calibration_context": context_value,
        }
        original = source_session.run(
            OUTPUT_NAMES, {**common, "obs": obs}
        )
        expected = source_session.run(
            OUTPUT_NAMES, {**common, "obs": obs_077}
        )
        actual = transformed_session.run(
            OUTPUT_NAMES, {**common, "obs": obs}
        )
        replay = np.asarray(row["policy_raw_action"], dtype=np.float32)
        source_replay_exact &= np.array_equal(
            original[0].reshape(-1), replay
        )
        transformed_exact_077 &= all(
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
        "rows": len(records),
        "ticks_contiguous_from_zero": [
            int(row["tick"]) for row in records
        ]
        == list(range(len(records))),
        "source_replay_exact": bool(source_replay_exact),
        "transformed_exact_source_x0077": bool(transformed_exact_077),
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
        raise FileExistsError("refusing to overwrite T243 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T243 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T243_HOME_NEGATIVE_LOW_COMMAND_FLOOR"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T243 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for graph in prereg["graphs"]:
        verify(graph["source"])
    for key in ("failed_trace", "passing_trace"):
        verify(prereg["causal_evidence"][key])

    context = next(
        row["context"]
        for row in prereg["contexts"]
        if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
        and row["fit_id"] == "p30"
    )
    outputs = []
    started = time.time()
    for index, graph in enumerate(prereg["graphs"]):
        destination = (
            WORK
            / "graphs"
            / str(graph["step"])
            / "home_negative_low_command_floor.onnx"
        )
        structure = transform(Path(graph["source"]["path"]), destination)
        inference = random_contract(
            Path(graph["source"]["path"]),
            destination,
            prereg["contexts"],
            prereg["contract"]["commands_x_m_s"],
            int(prereg["contract"]["samples_per_context_command"]),
            int(prereg["contract"]["random_seed"]) + index,
        )
        trace = (
            trace_contract(
                Path(graph["source"]["path"]),
                destination,
                Path(prereg["causal_evidence"]["failed_trace"]["path"]),
                context,
                int(prereg["contract"]["failed_trace_rows"]),
            )
            if graph["role"] == "half"
            else None
        )
        outputs.append(
            {
                "step": graph["step"],
                "role": graph["role"],
                "structure": structure,
                "inference": inference,
                "failed_trace_contract": trace,
            }
        )

    expected_nodes = [
        "t243_home_negative_router_matmul",
        "t243_home_negative_router_add",
        "t243_home_negative_tail_gate",
        "t243_exact_low_command_gate",
        "t243_home_negative_low_command_gate",
        "t243_map_home_negative_low_command",
    ]
    trace_rows = [
        row["failed_trace_contract"]
        for row in outputs
        if row["failed_trace_contract"] is not None
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
        "schema_version": (
            "open_duck.t243_home_negative_low_command_floor_result.v1"
        ),
        "status": (
            "PASS_T243_HOME_NEGATIVE_LOW_COMMAND_FLOOR"
            if not failed
            else "HOLD_T243_HOME_NEGATIVE_LOW_COMMAND_FLOOR"
        ),
        "decision": (
            prereg["decision_rule"]["all_contract_checks_green"]
            if not failed
            else prereg["decision_rule"]["otherwise"]
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
        "# T243 home-negative low-command floor result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Graphs: both checkpoints transformed; recurrent ABI exact\n"
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
