#!/usr/bin/env python3
"""Apply and verify T106's exact continuous hidden-expert gate transform."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t106_soft_gate_transform_preregistration.json"
OUTPUT = ANALYSIS / "t106_soft_gate_transform_result.json"
MARKDOWN = ANALYSIS / "T106_SOFT_GATE_TRANSFORM_RESULT_20260728.md"
DEFAULT_WORK_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t106_soft_gate_transform_v1"
)
AUDIT_OUTPUTS = {
    "hidden_gate_score": (TensorProto.FLOAT, [1, 1]),
    "negative_adapter_location": (TensorProto.FLOAT, [1, 14]),
    "soft_negative_com_weight": (TensorProto.FLOAT, [1, 1]),
    "conditional_adapter_location": (TensorProto.FLOAT, [1, 14]),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(value: Mapping[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T106 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value.get("status") != "PREREGISTERED_T106_SOFT_GATE_TRANSFORM"
        or value.get("failed_checks")
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T106 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    for step, item in value["policies"].items():
        verify_receipt(item, f"policy:{step}")
    for index, item in enumerate(value["trace_population"]):
        verify_receipt(item["trace"], f"trace:{index}")
    return value


def initializer_map(model: onnx.ModelProto) -> dict[str, str]:
    return {
        value.name: hashlib.sha256(
            numpy_helper.to_array(value).tobytes()
        ).hexdigest()
        for value in model.graph.initializer
    }


def graph_abi(model: onnx.ModelProto) -> dict[str, list[Any]]:
    def values(items: Any) -> list[Any]:
        return [
            {
                "name": item.name,
                "dtype": item.type.tensor_type.elem_type,
                "shape": [
                    dimension.dim_value
                    for dimension in item.type.tensor_type.shape.dim
                ],
            }
            for item in items
        ]

    return {"inputs": values(model.graph.input), "outputs": values(model.graph.output)}


def transform(source: Path, output: Path) -> dict[str, Any]:
    model = onnx.load(source)
    original = copy.deepcopy(model)
    gate_indices = [
        index
        for index, node in enumerate(model.graph.node)
        if node.op_type == "GreaterOrEqual"
        and list(node.input) == ["hidden_gate_score", "hidden_gate_zero"]
        and list(node.output) == ["negative_com_gate"]
    ]
    where_indices = [
        index
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
    if len(gate_indices) != 1 or len(where_indices) != 1:
        raise RuntimeError(
            f"T106 source topology changed: gate={gate_indices}, "
            f"where={where_indices}"
        )
    gate_index = gate_indices[0]
    where_index = where_indices[0]
    model.graph.node[gate_index].CopyFrom(
        helper.make_node(
            "Sigmoid",
            ["hidden_gate_score"],
            ["soft_negative_com_weight"],
            name="t106_soft_negative_com_weight",
        )
    )
    model.graph.node[where_index].CopyFrom(
        helper.make_node(
            "Mul",
            ["negative_adapter_location", "soft_negative_com_weight"],
            ["conditional_adapter_location"],
            name="t106_soft_negative_adapter",
        )
    )
    onnx.checker.check_model(model)
    onnx.save(model, output)
    reloaded = onnx.load(output)
    return {
        "source": receipt(source),
        "output": receipt(output),
        "node_count_before": len(original.graph.node),
        "node_count_after": len(reloaded.graph.node),
        "gate_node_index": gate_index,
        "mixture_node_index": where_index,
        "abi_exact": graph_abi(original) == graph_abi(reloaded),
        "initializers_exact": (
            initializer_map(original) == initializer_map(reloaded)
        ),
        "replacement_exact": (
            reloaded.graph.node[gate_index].op_type == "Sigmoid"
            and list(reloaded.graph.node[gate_index].input)
            == ["hidden_gate_score"]
            and list(reloaded.graph.node[gate_index].output)
            == ["soft_negative_com_weight"]
            and reloaded.graph.node[where_index].op_type == "Mul"
            and list(reloaded.graph.node[where_index].input)
            == [
                "negative_adapter_location",
                "soft_negative_com_weight",
            ]
            and list(reloaded.graph.node[where_index].output)
            == ["conditional_adapter_location"]
        ),
        "hard_gate_nodes_remaining": sum(
            node.op_type in {"GreaterOrEqual", "Where"}
            and (
                "negative_com_gate" in node.input
                or "negative_com_gate" in node.output
            )
            for node in reloaded.graph.node
        ),
    }


def instrument(source: Path, output: Path) -> None:
    model = onnx.load(source)
    existing = {item.name for item in model.graph.output}
    for name, (dtype, shape) in AUDIT_OUTPUTS.items():
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(name, dtype, shape)
            )
    onnx.checker.check_model(model)
    onnx.save(model, output)


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


def feed(row: dict[str, Any]) -> dict[str, np.ndarray]:
    state = row["policy_state_input"]
    return {
        "obs": np.asarray(row["obs_state"], np.float32)[None, :],
        "previous_action": np.asarray(
            state["previous_action"], np.float32
        ),
        "h_in": np.asarray(state["h_in"], np.float32),
        "calibration_context": np.zeros((1, 64), np.float32),
    }


def selected_rows(path: Path, ticks: list[Any]) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    wanted = {int(value) for value in ticks if value != "last"}
    wanted.add(int(rows[-1]["tick"]))
    return [row for row in rows if int(row["tick"]) in wanted]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--work-root", type=Path, default=DEFAULT_WORK_ROOT
    )
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T106 output: {path}")
    prereg = load_preregistration()
    work_root = args.work_root.resolve()
    work_root.mkdir(parents=True)
    transforms: dict[str, Any] = {}
    hard_sessions: dict[str, ort.InferenceSession] = {}
    soft_sessions: dict[str, ort.InferenceSession] = {}
    audit_sessions: dict[str, ort.InferenceSession] = {}
    for step, item in prereg["policies"].items():
        source = Path(item["path"])
        target = work_root / step / "action_margin_soft_gate.onnx"
        target.parent.mkdir(parents=True)
        transforms[step] = transform(source, target)
        audit_path = target.with_name("action_margin_soft_gate_audit.onnx")
        instrument(target, audit_path)
        hard_sessions[step] = session(source)
        soft_sessions[step] = session(target)
        audit_sessions[step] = session(audit_path)

    formula_errors: list[float] = []
    recurrent_errors: list[float] = []
    previous_action_errors: list[float] = []
    step0_errors: list[float] = []
    x0_errors: list[float] = []
    moving_deltas = {"1003520": [], "2007040": []}
    weights: list[float] = []
    sampled_rows = 0
    for item in prereg["trace_population"]:
        step = str(item["step"])
        hard = hard_sessions[step]
        soft = soft_sessions[step]
        audit = audit_sessions[step]
        audit_names = [value.name for value in audit.get_outputs()]
        for row in selected_rows(
            Path(item["trace"]["path"]),
            prereg["contract"]["sample_ticks"],
        ):
            inputs = feed(row)
            hard_action, hard_previous, hard_hidden = hard.run(
                ["continuous_actions", "previous_action_out", "h_out"],
                inputs,
            )
            soft_action, soft_previous, soft_hidden = soft.run(
                ["continuous_actions", "previous_action_out", "h_out"],
                inputs,
            )
            values = dict(
                zip(audit_names, audit.run(None, inputs), strict=True)
            )
            score = values["hidden_gate_score"]
            head = values["negative_adapter_location"]
            weight = values["soft_negative_com_weight"]
            mixture = values["conditional_adapter_location"]
            expected_weight = 1.0 / (1.0 + np.exp(-score))
            formula_errors.append(
                max(
                    float(np.max(np.abs(weight - expected_weight))),
                    float(np.max(np.abs(mixture - head * weight))),
                )
            )
            weights.extend(weight.ravel().tolist())
            recurrent_errors.append(
                float(np.max(np.abs(soft_hidden - hard_hidden)))
            )
            previous_action_errors.append(
                float(np.max(np.abs(soft_previous - soft_action)))
            )
            delta = float(np.max(np.abs(soft_action - hard_action)))
            if step == "0":
                step0_errors.append(delta)
            elif float(item["command_x_m_s"]) == 0.0:
                x0_errors.append(delta)
            else:
                moving_deltas[step].append(delta)
            sampled_rows += 1

    checks = {
        "all_three_graphs_transformed": len(transforms) == 3,
        "all_node_counts_preserved": all(
            item["node_count_before"] == item["node_count_after"]
            for item in transforms.values()
        ),
        "all_graph_abis_exact": all(
            item["abi_exact"] for item in transforms.values()
        ),
        "all_initializers_exact": all(
            item["initializers_exact"] for item in transforms.values()
        ),
        "all_replacements_exact": all(
            item["replacement_exact"] for item in transforms.values()
        ),
        "all_hard_gate_nodes_removed": all(
            item["hard_gate_nodes_remaining"] == 0
            for item in transforms.values()
        ),
        "analytic_soft_mixture_exact": max(formula_errors, default=0.0)
        <= prereg["contract"]["maximum_formula_error"],
        "soft_weight_strictly_between_zero_and_one": (
            min(weights, default=0.5) > 0.0
            and max(weights, default=0.5) < 1.0
        ),
        "recurrent_hidden_unchanged": max(
            recurrent_errors, default=0.0
        )
        <= 1.0e-7,
        "previous_action_out_equals_final_action": max(
            previous_action_errors, default=0.0
        )
        <= 1.0e-7,
        "step_zero_outputs_exact": max(step0_errors, default=0.0)
        <= prereg["contract"]["maximum_step0_output_error"],
        "x0_outputs_exact": max(x0_errors, default=0.0)
        <= prereg["contract"]["maximum_x0_hard_vs_soft_output_error"],
        "half_moving_actions_change_materially": max(
            moving_deltas["1003520"], default=0.0
        )
        > prereg["contract"]["minimum_moving_postupdate_action_delta"],
        "final_moving_actions_change_materially": max(
            moving_deltas["2007040"], default=0.0
        )
        > prereg["contract"]["minimum_moving_postupdate_action_delta"],
        "all_metrics_finite": all(
            np.isfinite(value)
            for value in [
                *formula_errors,
                *recurrent_errors,
                *previous_action_errors,
                *step0_errors,
                *x0_errors,
                *moving_deltas["1003520"],
                *moving_deltas["2007040"],
                *weights,
            ]
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t106_soft_gate_transform_result.v1",
        "status": (
            "PASS_T106_SOFT_GATE_TRANSFORM"
            if not failed
            else "HOLD_T106_SOFT_GATE_TRANSFORM"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if not failed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "transforms": transforms,
        "metrics": {
            "sampled_rows": sampled_rows,
            "maximum_formula_error": max(formula_errors, default=0.0),
            "soft_weight_minimum": min(weights, default=0.0),
            "soft_weight_maximum": max(weights, default=0.0),
            "maximum_recurrent_hidden_error": max(
                recurrent_errors, default=0.0
            ),
            "maximum_step0_action_error": max(
                step0_errors, default=0.0
            ),
            "maximum_x0_action_error": max(x0_errors, default=0.0),
            "maximum_half_moving_action_delta": max(
                moving_deltas["1003520"], default=0.0
            ),
            "maximum_final_moving_action_delta": max(
                moving_deltas["2007040"], default=0.0
            ),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "graphs_transformed": len(transforms),
            "sampled_trace_rows": sampled_rows,
            "behavior_cells": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "interpretation": {
            "hosted_run_earned": False,
            "behavior_rerun_earned": False,
            "gate5_open": False,
        },
        "authority": {
            "t107_nominal_preregistration": not failed,
            "behavior": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T106 continuous gate transform result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Sampled frozen rows: `{sampled_rows}`",
                (
                    "- Soft-weight range: "
                    f"`{value['metrics']['soft_weight_minimum']:.6f}` to "
                    f"`{value['metrics']['soft_weight_maximum']:.6f}`"
                ),
                (
                    "- Half/final maximum moving action delta: "
                    f"`{value['metrics']['maximum_half_moving_action_delta']:.6f} / "
                    f"{value['metrics']['maximum_final_moving_action_delta']:.6f}`"
                ),
                "- Behavior / training / Colab / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
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
