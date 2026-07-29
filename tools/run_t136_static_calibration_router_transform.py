#!/usr/bin/env python3
"""Replace T129's drifting per-tick gate with the frozen calibration gate."""

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
from onnx import TensorProto, helper, numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t136_static_calibration_router_preregistration.json"
RESULT = ANALYSIS / "t136_static_calibration_router_result.json"
MARKDOWN = ANALYSIS / "T136_STATIC_CALIBRATION_ROUTER_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t136_t129_static_calibration_router_v1"
)


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    import hashlib

    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify(item: dict[str, Any], name: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(item["bytes"])
        or sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"T136 frozen input changed: {name}={path}")


def abi(model: onnx.ModelProto) -> dict[str, list[int]]:
    values = list(model.graph.input) + list(model.graph.output)
    return {
        value.name: [
            int(dimension.dim_value)
            for dimension in value.type.tensor_type.shape.dim
        ]
        for value in values
    }


def transform(
    source: Path,
    destination: Path,
    coefficient: np.ndarray,
    intercept: float,
) -> dict[str, Any]:
    before = onnx.load(source)
    model = copy.deepcopy(before)
    consumers = [
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
    if len(consumers) != 1:
        raise RuntimeError(f"T136 expected one hard-gate consumer: {source}")
    index, consumer = consumers[0]
    initializers = {
        "calibration_router_coefficient": coefficient.reshape(64, 1),
        "calibration_router_intercept": np.asarray(
            [intercept], dtype=np.float32
        ),
        "calibration_router_zero": np.asarray([0.0], dtype=np.float32),
    }
    existing_names = {item.name for item in model.graph.initializer}
    if existing_names.intersection(initializers):
        raise RuntimeError("T136 initializer name collision")
    for name, value in initializers.items():
        model.graph.initializer.append(
            numpy_helper.from_array(np.asarray(value, dtype=np.float32), name)
        )
    nodes = [
        helper.make_node(
            "MatMul",
            ["calibration_context", "calibration_router_coefficient"],
            ["calibration_router_linear"],
            name="t136_calibration_router_matmul",
        ),
        helper.make_node(
            "Add",
            ["calibration_router_linear", "calibration_router_intercept"],
            ["calibration_router_score"],
            name="t136_calibration_router_add",
        ),
        helper.make_node(
            "GreaterOrEqual",
            ["calibration_router_score", "calibration_router_zero"],
            ["calibration_negative_com_gate"],
            name="t136_calibration_router_gate",
        ),
    ]
    for offset, node in enumerate(nodes):
        model.graph.node.insert(index + offset, node)
    consumer = model.graph.node[index + len(nodes)]
    consumer.input[0] = "calibration_negative_com_gate"
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True)
    onnx.save(model, destination)

    after = onnx.load(destination)
    before_nodes = list(before.graph.node)
    after_nodes = list(after.graph.node)
    unchanged_nodes = 0
    where_rewire_exact = False
    before_index = 0
    for after_index, node in enumerate(after_nodes):
        if index <= after_index < index + len(nodes):
            continue
        old = before_nodes[before_index]
        if before_index == index:
            expected = copy.deepcopy(old)
            expected.input[0] = "calibration_negative_com_gate"
            where_rewire_exact = node.SerializeToString() == expected.SerializeToString()
        else:
            unchanged_nodes += int(
                node.SerializeToString() == old.SerializeToString()
            )
        before_index += 1
    old_initializers = {
        item.name: item.SerializeToString()
        for item in before.graph.initializer
    }
    new_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    return {
        "source": receipt(source),
        "transformed": receipt(destination),
        "node_count_before": len(before_nodes),
        "node_count_after": len(after_nodes),
        "three_nodes_inserted": len(after_nodes) == len(before_nodes) + 3,
        "where_rewire_exact": where_rewire_exact,
        "all_other_nodes_byte_exact": (
            unchanged_nodes == len(before_nodes) - 1
        ),
        "existing_initializers_byte_exact": all(
            new_initializers.get(name) == value
            for name, value in old_initializers.items()
        ),
        "three_initializers_added": (
            set(new_initializers) - set(old_initializers)
            == set(initializers)
        ),
        "abi_exact": abi(before) == abi(after),
    }


def inspection_session(path: Path) -> ort.InferenceSession:
    model = onnx.load(path)
    existing = {item.name for item in model.graph.output}
    for name, data_type, shape in (
        ("calibration_negative_com_gate", TensorProto.BOOL, [1, 1]),
        ("calibration_router_score", TensorProto.FLOAT, [1, 1]),
        ("negative_adapter_location", TensorProto.FLOAT, [1, 14]),
        ("conditional_adapter_location", TensorProto.FLOAT, [1, 14]),
    ):
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(name, data_type, shape)
            )
    return ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"]
    )


def contract(
    path: Path,
    contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    session = inspection_session(path)
    rng = np.random.default_rng(20260729)
    labels = []
    x0_exact = True
    feedback_exact = True
    finite = True
    for row in contexts:
        expected = row["population"] == "com_x_negative"
        context = np.asarray(row["context"], dtype=np.float32).reshape(1, 64)
        for command_x in (0.0, 0.074):
            obs = rng.normal(size=(1, 115)).astype(np.float32)
            obs[:, 6] = np.float32(command_x)
            feed = {
                "obs": obs,
                "previous_action": np.zeros((1, 14), dtype=np.float32),
                "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                "calibration_context": context,
            }
            (
                action,
                previous,
                hidden,
                gate,
                score,
                expert,
                conditional,
            ) = session.run(
                [
                    "continuous_actions",
                    "previous_action_out",
                    "h_out",
                    "calibration_negative_com_gate",
                    "calibration_router_score",
                    "negative_adapter_location",
                    "conditional_adapter_location",
                ],
                feed,
            )
            observed = bool(gate.reshape(-1)[0])
            labels.append(
                {
                    "fit_id": row["fit_id"],
                    "population": row["population"],
                    "command_x_m_s": command_x,
                    "expected_negative": expected,
                    "observed_negative": observed,
                    "score": float(score.reshape(-1)[0]),
                    "conditional_exact": (
                        np.array_equal(conditional, expert)
                        if expected
                        else np.array_equal(
                            conditional, np.zeros_like(conditional)
                        )
                    ),
                }
            )
            if command_x == 0.0:
                x0_exact &= bool(
                    np.array_equal(action, np.zeros_like(action))
                    and np.array_equal(previous, np.zeros_like(previous))
                )
            feedback_exact &= np.array_equal(action, previous)
            finite &= all(
                bool(np.all(np.isfinite(value)))
                for value in (action, previous, hidden, score, expert)
            )
    return {
        "labels": labels,
        "all_labels_exact": all(
            row["expected_negative"] == row["observed_negative"]
            for row in labels
        ),
        "all_conditional_outputs_exact": all(
            row["conditional_exact"] for row in labels
        ),
        "x0_action_and_feedback_exact_zero": x0_exact,
        "action_feedback_bit_exact": feedback_exact,
        "all_outputs_finite": finite,
        "cpu_provider": session.get_providers()[0] == "CPUExecutionProvider",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T136 requires --execute")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T136: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T136 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T136 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for step, item in prereg["source_graphs"].items():
        verify(item, f"source_graph:{step}")

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
    contexts = [
        {
            "fit_id": row["fit_id"],
            "population": row["population"],
            "context": row["context"],
        }
        for row in t135b["runs"]
    ]
    WORK.mkdir(parents=True)
    graphs: dict[str, Any] = {}
    contracts: dict[str, Any] = {}
    started = time.time()
    for step, item in prereg["source_graphs"].items():
        destination = WORK / step / "static_calibration_router.onnx"
        graphs[step] = transform(
            Path(item["path"]), destination, coefficient, intercept
        )
        contracts[step] = contract(destination, contexts)
    checks = {
        "all_graph_transforms_exact": all(
            all(
                row[name]
                for name in (
                    "three_nodes_inserted",
                    "where_rewire_exact",
                    "all_other_nodes_byte_exact",
                    "existing_initializers_byte_exact",
                    "three_initializers_added",
                    "abi_exact",
                )
            )
            for row in graphs.values()
        ),
        "all_calibration_labels_exact": all(
            row["all_labels_exact"] for row in contracts.values()
        ),
        "all_conditional_outputs_exact": all(
            row["all_conditional_outputs_exact"]
            for row in contracts.values()
        ),
        "all_x0_paths_exact_zero": all(
            row["x0_action_and_feedback_exact_zero"]
            for row in contracts.values()
        ),
        "all_feedback_and_finite_contracts": all(
            row["action_feedback_bit_exact"]
            and row["all_outputs_finite"]
            and row["cpu_provider"]
            for row in contracts.values()
        ),
        "both_postupdate_checkpoints_transformed": (
            {"1003520", "2007040"}.issubset(graphs)
        ),
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t136_static_calibration_router_result.v1"
        ),
        "status": (
            "PASS_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM"
            if passed
            else "HOLD_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM"
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
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "graphs_transformed": len(graphs),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "nominal_matrix_preregistration": passed,
            "behavior_evaluation": False,
            "negative_matrix": False,
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
        "# T136 static calibration-router transform\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Dynamic per-tick gate remains diagnostic but no longer routes\n"
        "- Calibration context routes the conditional expert once per episode\n"
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
