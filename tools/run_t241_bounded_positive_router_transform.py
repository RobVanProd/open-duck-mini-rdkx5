#!/usr/bin/env python3
"""Build and prove the T241 bounded positive-router ONNX transform."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    abi,
    canonical_sha256,
    receipt,
)


PREREG = (
    ANALYSIS
    / "t241_bounded_positive_router_transform_preregistration.json"
)
OUTPUT = ANALYSIS / "t241_bounded_positive_router_transform_result.json"
MARKDOWN = (
    ANALYSIS / "T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM_RESULT_20260731.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t241_bounded_positive_router_v1"
)
OUTPUT_NAMES = ["continuous_actions", "previous_action_out", "h_out"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def transform(
    source: Path, destination: Path, upper_bound: float
) -> dict[str, Any]:
    model = onnx.load(source)
    before = copy.deepcopy(model)
    upper_name = "t241_positive_router_upper_bound"
    model.graph.initializer.append(
        numpy_helper.from_array(
            np.asarray([np.float32(upper_bound)], dtype=np.float32),
            upper_name,
        )
    )
    additions: list[onnx.NodeProto] = []
    sites = [
        (
            "t162_positive_router_gate",
            "t162_positive_router_score",
            "t162_positive_condition",
            "t241_t162",
        ),
        (
            "t156_positive_router_gate",
            "t156_positive_router_score",
            "t156_positive_condition",
            "t241_t156",
        ),
    ]
    for node_name, score_name, output_name, prefix in sites:
        target = next(
            (node for node in model.graph.node if node.name == node_name),
            None,
        )
        if (
            target is None
            or target.op_type != "GreaterOrEqual"
            or list(target.input) != [score_name, "positive_router_zero"]
            or list(target.output) != [output_name]
        ):
            raise RuntimeError(f"T241 gate site changed: {node_name}")
        lower_name = f"{prefix}_positive_lower_condition"
        upper_output = f"{prefix}_positive_upper_condition"
        target.output[0] = lower_name
        additions.extend(
            [
                helper.make_node(
                    "LessOrEqual",
                    [score_name, upper_name],
                    [upper_output],
                    name=f"{prefix}_positive_upper_gate",
                ),
                helper.make_node(
                    "And",
                    [lower_name, upper_output],
                    [output_name],
                    name=f"{prefix}_bounded_positive_gate",
                ),
            ]
        )
        index = list(model.graph.node).index(target)
        for offset, added in enumerate(additions[-2:], start=1):
            model.graph.node.insert(index + offset, added)

    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    after = onnx.load(destination)
    before_by_name = {
        node.name: node.SerializeToString() for node in before.graph.node
    }
    after_by_name = {node.name: node for node in after.graph.node}
    changed = sorted(
        name
        for name, serialized in before_by_name.items()
        if after_by_name[name].SerializeToString() != serialized
    )
    before_initializers = {
        value.name for value in before.graph.initializer
    }
    after_initializers = {
        value.name for value in after.graph.initializer
    }
    return {
        "source": receipt(source),
        "transformed": receipt(destination),
        "source_abi": abi(before),
        "transformed_abi": abi(after),
        "added_nodes": [node.name for node in additions],
        "added_initializers": sorted(
            after_initializers - before_initializers
        ),
        "changed_old_nodes": changed,
        "onnx_checker_pass": True,
        "upper_bound_float32": float(np.float32(upper_bound)),
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
    rows: list[dict[str, Any]] = []
    for context_row in contexts:
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        for command in commands:
            exact = True
            finite = True
            changed_actions = 0
            for _ in range(samples):
                obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
                obs[0, 6] = np.float32(command)
                feed = {
                    "obs": obs,
                    "previous_action": rng.uniform(
                        -0.6, 0.6, (1, 14)
                    ).astype(np.float32),
                    "h_in": rng.uniform(-0.6, 0.6, (1, 64)).astype(
                        np.float32
                    ),
                    "calibration_context": context,
                }
                old = source_session.run(OUTPUT_NAMES, feed)
                new = transformed_session.run(OUTPUT_NAMES, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(old, new, strict=True)
                )
                finite &= all(np.all(np.isfinite(value)) for value in new)
                changed_actions += int(
                    not np.array_equal(old[0], new[0])
                )
            rows.append(
                {
                    "condition_id": context_row["condition_id"],
                    "fit_id": context_row["fit_id"],
                    "command_x_m_s": command,
                    "samples": samples,
                    "all_outputs_bit_exact": bool(exact),
                    "all_outputs_finite": bool(finite),
                    "changed_action_rows": changed_actions,
                }
            )
    return {
        "rows": rows,
        "samples": sum(row["samples"] for row in rows),
        "all_outputs_finite": all(row["all_outputs_finite"] for row in rows),
        "all_non_home_negative_exact": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["condition_id"] != "HOME_JOINT_OFFSET_NEG"
        ),
        "all_home_negative_x0_exact": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
            and row["command_x_m_s"] == 0.0
        ),
        "all_home_negative_moving_changed": all(
            row["changed_action_rows"] > 0
            for row in rows
            if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
            and row["command_x_m_s"] > 0.0
        ),
    }


def trace_contract(
    source: Path,
    transformed: Path,
    traces: list[dict[str, Any]],
    role: str,
    context_by_fit: dict[str, np.ndarray],
) -> dict[str, Any]:
    source_session = session(source)
    transformed_session = session(transformed)
    outputs: list[dict[str, Any]] = []
    total_rows = 0
    for item in traces:
        if item["role"] != role:
            continue
        path = Path(item["trace"]["path"])
        if sha256(path) != item["trace"]["sha256"]:
            raise RuntimeError(f"T241 frozen trace changed: {path}")
        source_exact = True
        transformed_finite = True
        changed = 0
        rows = 0
        with path.open("r", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                feed = {
                    "obs": np.asarray(
                        row["obs_state"], dtype=np.float32
                    ).reshape(1, 115),
                    "previous_action": np.asarray(
                        row["policy_state_input"]["previous_action"],
                        dtype=np.float32,
                    ),
                    "h_in": np.asarray(
                        row["policy_state_input"]["h_in"],
                        dtype=np.float32,
                    ),
                    "calibration_context": np.asarray(
                        context_by_fit[item["fit_id"]], dtype=np.float32
                    ).reshape(1, 64),
                }
                old = source_session.run(OUTPUT_NAMES, feed)
                new = transformed_session.run(OUTPUT_NAMES, feed)
                recorded = [
                    np.asarray(row["action"], dtype=np.float32).reshape(
                        1, 14
                    ),
                    np.asarray(
                        row["policy_state_output"]["previous_action_out"],
                        dtype=np.float32,
                    ),
                    np.asarray(
                        row["policy_state_output"]["h_out"],
                        dtype=np.float32,
                    ),
                ]
                source_exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(old, recorded, strict=True)
                )
                transformed_finite &= all(
                    np.all(np.isfinite(value)) for value in new
                )
                changed += int(not np.array_equal(old[0], new[0]))
                rows += 1
        total_rows += rows
        outputs.append(
            {
                "fit_id": item["fit_id"],
                "command_x_m_s": item["command_x_m_s"],
                "rows": rows,
                "source_replay_exact": bool(source_exact),
                "transformed_finite": bool(transformed_finite),
                "changed_action_rows": changed,
            }
        )
    return {
        "role": role,
        "traces": outputs,
        "rows": total_rows,
        "all_source_replay_exact": all(
            row["source_replay_exact"] for row in outputs
        ),
        "all_transformed_finite": all(
            row["transformed_finite"] for row in outputs
        ),
        "every_trace_changed": all(
            row["changed_action_rows"] > 0 for row in outputs
        ),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T241: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if prereg["status"] != (
        "PREREGISTERED_T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM"
    ):
        raise RuntimeError("T241 preregistration status changed")
    for row in prereg["frozen_inputs"].values():
        path = Path(row["path"])
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"T241 frozen input changed: {path}")
    contexts = json.loads(
        Path(prereg["frozen_inputs"]["t167_contexts"]["path"]).read_text(
            encoding="utf-8"
        )
    )["cells"]
    home_context_by_fit = {
        row["fit_id"]: np.asarray(row["context"], dtype=np.float32)
        for row in contexts
        if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
    }
    outputs: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    upper = float(prereg["transform"]["upper_bound_float32"])
    for index, graph in enumerate(prereg["graphs"]):
        destination = (
            WORK / "graphs" / str(graph["step"]) / "bounded_router.onnx"
        )
        structure = transform(Path(graph["path"]), destination, upper)
        inference = random_contract(
            Path(graph["path"]),
            destination,
            contexts,
            prereg["cpu_contract"]["commands_x_m_s"],
            int(prereg["cpu_contract"]["samples_per_context_command"]),
            int(prereg["cpu_contract"]["random_seed"]) + index,
        )
        trace_replay = trace_contract(
            Path(graph["path"]),
            destination,
            prereg["home_offset_traces"],
            graph["role"],
            home_context_by_fit,
        )
        outputs.append(
            {
                "role": graph["role"],
                "step": graph["step"],
                "structure": structure,
                "random_inference": inference,
                "trace_replay": trace_replay,
            }
        )
        traces.append(trace_replay)

    expected_nodes = set(prereg["transform"]["expected_added_nodes"])
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
        "only_expected_initializer_added": all(
            row["structure"]["added_initializers"]
            == [prereg["transform"]["expected_added_initializer"]]
            for row in outputs
        ),
        "only_expected_old_gates_changed": all(
            set(row["structure"]["changed_old_nodes"])
            == set(prereg["transform"]["expected_changed_old_nodes"])
            for row in outputs
        ),
        "upper_bound_exact": all(
            row["structure"]["upper_bound_float32"] == upper
            for row in outputs
        ),
        "random_contract_exact": all(
            row["random_inference"]["all_outputs_finite"]
            and row["random_inference"]["all_non_home_negative_exact"]
            and row["random_inference"]["all_home_negative_x0_exact"]
            and row["random_inference"][
                "all_home_negative_moving_changed"
            ]
            for row in outputs
        ),
        "failed_trace_contract_exact": all(
            row["all_source_replay_exact"]
            and row["all_transformed_finite"]
            and row["every_trace_changed"]
            and len(row["traces"]) == 6
            for row in traces
        ),
        "no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    status = (
        "PASS_T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM"
        if passed
        else "HOLD_T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM"
    )
    decision = (
        prereg["decision_rule"]["pass_decision"]
        if passed
        else prereg["decision_rule"]["fail_decision"]
    )
    result_basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t241_bounded_positive_router_transform.v1"
        ),
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "graphs": outputs,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "onnx_transforms": len(outputs),
            "random_inference_rows": sum(
                row["random_inference"]["samples"] for row in outputs
            ),
            "trace_inference_rows": sum(row["rows"] for row in traces),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "home_offset_behavior_preregistration": passed,
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
        "# T241 bounded positive-router transform result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        f"- Graphs / random rows / trace rows: "
        f"`{len(outputs)} / {result['execution']['random_inference_rows']} / "
        f"{result['execution']['trace_inference_rows']}`\n"
        "- ABI and all non-home-negative contexts: bit-exact\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={decision}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
