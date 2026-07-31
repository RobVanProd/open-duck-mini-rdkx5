#!/usr/bin/env python3
"""Run T246's read-only checkpoint-adapter causal autopsy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Mapping

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    sha256,
)


PREREG = ANALYSIS / "t246_checkpoint_adapter_autopsy_preregistration.json"
RESULT = ANALYSIS / "t246_checkpoint_adapter_autopsy_result.json"
MARKDOWN = ANALYSIS / "T246_CHECKPOINT_ADAPTER_AUTOPSY_RESULT_20260731.md"
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T246 input: {path}")


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


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def trajectory_equal(
    left: list[dict[str, Any]], right: list[dict[str, Any]]
) -> bool:
    keys = (
        "policy_raw_action",
        "qpos",
        "qvel",
        "applied_target_rad",
        "sent_target_rad",
        "body_pitch_rad",
        "body_roll_rad",
        "base_height_m",
        "foot_contacts",
    )
    return len(left) == len(right) and all(
        all(lrow[key] == rrow[key] for key in keys)
        for lrow, rrow in zip(left, right, strict=True)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T246 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T246 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T246_CHECKPOINT_ADAPTER_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T246 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for item in prereg["graphs"].values():
        verify(item)
    for role in ("half", "final"):
        for row in prereg["traces"][role]:
            verify(row["trace"])

    started = time.time()
    half_path = Path(prereg["graphs"]["half"]["path"])
    final_path = Path(prereg["graphs"]["final"]["path"])
    half_model = onnx.load(half_path)
    final_model = onnx.load(final_path)
    half_nodes = {
        node.name: node.SerializeToString()
        for node in half_model.graph.node
    }
    final_nodes = {
        node.name: node.SerializeToString()
        for node in final_model.graph.node
    }
    changed_nodes = sorted(
        name
        for name, value in half_nodes.items()
        if final_nodes.get(name) != value
    )
    half_initializers = {
        item.name: item for item in half_model.graph.initializer
    }
    final_initializers = {
        item.name: item for item in final_model.graph.initializer
    }
    changed_initializers = sorted(
        name
        for name, value in half_initializers.items()
        if final_initializers.get(name) is None
        or final_initializers[name].SerializeToString()
        != value.SerializeToString()
    )
    initializer_deltas = []
    for name in changed_initializers:
        left = numpy_helper.to_array(half_initializers[name]).astype(float)
        right = numpy_helper.to_array(final_initializers[name]).astype(float)
        initializer_deltas.append(
            {
                "name": name,
                "shape": list(left.shape),
                "maximum_absolute_delta": float(
                    np.max(np.abs(left - right))
                ),
                "rms_delta": float(
                    np.sqrt(np.mean((left - right) ** 2))
                ),
            }
        )

    half_traces = {
        float(row["command_x_m_s"]): load_rows(Path(row["trace"]["path"]))
        for row in prereg["traces"]["half"]
    }
    final_traces = {
        float(row["command_x_m_s"]): load_rows(Path(row["trace"]["path"]))
        for row in prereg["traces"]["final"]
    }
    half_plateau = all(
        trajectory_equal(half_traces[0.074], half_traces[command])
        for command in (0.077, 0.080)
    )
    final_plateau = all(
        trajectory_equal(final_traces[0.074], final_traces[command])
        for command in (0.077, 0.080)
    )

    t243 = json.loads(
        Path(prereg["frozen_inputs"]["t243_contract"]["path"])
        .read_text(encoding="utf-8")
    )
    context = np.asarray(
        next(
            row["context"]
            for row in t243["contexts"]
            if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
            and row["fit_id"] == "p30"
        ),
        dtype=np.float32,
    ).reshape(1, 64)
    half_session = session(half_path)
    final_session = session(final_path)
    source_replay_exact = True
    half_changed_rows = 0
    maximum_action_delta = 0.0
    for row in final_traces[0.077]:
        state = row["policy_state_input"]
        feed = {
            "obs": np.asarray(
                row["obs_state"], dtype=np.float32
            ).reshape(1, 115),
            "h_in": np.asarray(state["h_in"], dtype=np.float32),
            "previous_action": np.asarray(
                state["previous_action"], dtype=np.float32
            ),
            "calibration_context": context,
        }
        final_outputs = final_session.run(OUTPUT_NAMES, feed)
        half_outputs = half_session.run(OUTPUT_NAMES, feed)
        replay = np.asarray(row["policy_raw_action"], dtype=np.float32)
        source_replay_exact &= np.array_equal(
            final_outputs[0].reshape(-1), replay
        )
        delta = float(
            np.max(
                np.abs(half_outputs[0].reshape(-1) - replay)
            )
        )
        half_changed_rows += int(delta > 0.0)
        maximum_action_delta = max(maximum_action_delta, delta)

    checks = {
        "node_names_and_nodes_byte_exact": (
            set(half_nodes) == set(final_nodes) and not changed_nodes
        ),
        "initializer_names_exact": (
            set(half_initializers) == set(final_initializers)
        ),
        "exactly_two_nominal_adapter_initializers_differ": (
            changed_initializers
            == prereg["contract"]["expected_different_initializers"]
        ),
        "both_checkpoint_command_plateaus_exact": (
            half_plateau and final_plateau
        ),
        "final_failed_trace_source_replay_exact": source_replay_exact,
        "half_adapter_counterfactual_is_action_sensitive": (
            half_changed_rows > 0 and maximum_action_delta > 0.0
        ),
        "half_and_final_duration_split_exact": (
            {len(rows) for rows in half_traces.values()} == {600}
            and {len(rows) for rows in final_traces.values()} == {231}
        ),
        "cpu_only_zero_simulator_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t246_checkpoint_adapter_autopsy_result.v1"
        ),
        "status": (
            "PASS_T246_CHECKPOINT_ADAPTER_CAUSAL_SPLIT"
            if passed
            else "HOLD_T246_CHECKPOINT_ADAPTER_AUTOPSY"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graph_identity": {
            "changed_nodes": changed_nodes,
            "changed_initializers": changed_initializers,
            "initializer_deltas": initializer_deltas,
        },
        "trace_identity": {
            "half_three_command_plateau_exact": half_plateau,
            "final_three_command_plateau_exact": final_plateau,
            "half_rows_per_command": 600,
            "final_rows_per_command": 231,
            "final_source_replay_exact": source_replay_exact,
            "half_counterfactual_changed_rows": half_changed_rows,
            "half_counterfactual_maximum_action_delta": (
                maximum_action_delta
            ),
        },
        "interpretation": {
            "causal_split": (
                "the two nominal-adapter tensors are the only graph "
                "difference aligned with the half-pass/final-fall split"
            ),
            "next_mechanism": (
                "uniformly add the half adapter as a home-negative-tail "
                "expert while preserving every other route"
            ),
        },
        "execution": {
            "onnx_inferences": len(final_traces[0.077]) * 2,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "adapter_route_preregistration": passed,
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
        "# T246 checkpoint-adapter autopsy result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Changed nodes/initializers: "
        f"`{len(changed_nodes)}/{changed_initializers}`\n"
        f"- Half/final rows per moving command: `600/231`\n"
        "- Simulator/behavior/optimizer/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
