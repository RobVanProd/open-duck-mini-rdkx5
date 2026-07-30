#!/usr/bin/env python3
"""Compose T170 nominal heads into the frozen T164-final deployment graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
    verify,
)


PREREG = ANALYSIS / "t172_t170_postexport_composition_preregistration.json"
RESULT = ANALYSIS / "t172_t170_postexport_composition_result.json"
MARKDOWN = ANALYSIS / "T172_T170_POSTEXPORT_COMPOSITION_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t172_t170_postexport_composition_v1"
)
SOURCE_NAMES = [
    "negative_adapter_weight",
    "negative_adapter_bias",
]
DESTINATION_NAMES = [
    "nominal_condition_negative_adapter_weight",
    "nominal_condition_negative_adapter_bias",
]
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]


def arrays(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: numpy_helper.to_array(item).copy()
        for item in model.graph.initializer
    }


def replace(model: onnx.ModelProto, name: str, value: np.ndarray) -> None:
    for index, item in enumerate(model.graph.initializer):
        if item.name == name:
            model.graph.initializer[index].CopyFrom(
                numpy_helper.from_array(value, name=name)
            )
            return
    raise KeyError(name)


def transform(raw_path: Path, base_path: Path, destination: Path) -> dict[str, Any]:
    raw = onnx.load(raw_path)
    base = onnx.load(base_path)
    raw_values = arrays(raw)
    base_values = arrays(base)
    before = base.SerializeToString()
    for source, target in zip(SOURCE_NAMES, DESTINATION_NAMES, strict=True):
        replace(base, target, raw_values[source])
    onnx.checker.check_model(base)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(base, destination)
    after_values = arrays(base)
    changed = sorted(
        name
        for name in base_values
        if not np.array_equal(base_values[name], after_values[name])
    )
    source_binding = {
        target: bool(np.array_equal(after_values[target], raw_values[source]))
        for source, target in zip(SOURCE_NAMES, DESTINATION_NAMES, strict=True)
    }
    return {
        "raw": receipt(raw_path),
        "base": receipt(base_path),
        "transformed": receipt(destination),
        "changed_initializers": changed,
        "expected_changed_initializers": (
            [] if before == base.SerializeToString() else sorted(DESTINATION_NAMES)
        ),
        "source_binding": source_binding,
        "all_source_bindings_exact": all(source_binding.values()),
        "nodes_byte_exact": all(
            left.SerializeToString() == right.SerializeToString()
            for left, right in zip(
                onnx.load(base_path).graph.node,
                base.graph.node,
                strict=True,
            )
        ),
        "initializer_names_exact": set(base_values) == set(after_values),
        "all_other_initializers_exact": all(
            np.array_equal(base_values[name], after_values[name])
            for name in base_values
            if name not in DESTINATION_NAMES
        ),
        "all_initializers_finite": all(
            np.all(np.isfinite(value)) for value in after_values.values()
        ),
        "model_byte_exact_to_base": before == base.SerializeToString(),
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


def route(base_values: dict[str, np.ndarray], context: np.ndarray) -> str:
    negative = float(
        (
            context @ base_values["conditional_path_router_coefficient"]
            + base_values["conditional_path_router_intercept"]
        ).reshape(-1)[0]
    )
    positive = float(
        (
            context @ base_values["positive_router_coefficient"]
            + base_values["positive_router_intercept"]
        ).reshape(-1)[0]
    )
    if positive >= 0.0:
        return "positive_expert"
    if negative >= 0.0:
        return "negative_expert"
    return "nominal_expert"


def inference_contract(
    composed: Path,
    base: Path,
    contexts: list[dict[str, Any]],
    seed: int,
) -> dict[str, Any]:
    actual_session = make_session(composed)
    base_session = make_session(base)
    base_values = arrays(onnx.load(base))
    rng = np.random.default_rng(seed)
    rows = []
    total_samples = 0
    for context_row in contexts:
        context = np.asarray(context_row["context"], np.float32).reshape(1, 64)
        active_route = route(base_values, context)
        for command in (0.0, 0.074, 0.077, 0.080):
            exact = True
            finite = True
            action_changed = False
            for _ in range(8):
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
                actual = actual_session.run(OUTPUT_NAMES, feed)
                expected = base_session.run(OUTPUT_NAMES, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(actual, expected, strict=True)
                )
                finite &= all(
                    np.all(np.isfinite(value)) for value in actual
                )
                action_changed |= not np.array_equal(actual[0], expected[0])
                total_samples += 1
            rows.append(
                {
                    "condition_id": context_row["condition_id"],
                    "condition_index": context_row["condition_index"],
                    "fit_id": context_row["fit_id"],
                    "context_sha256": context_row["context_sha256"],
                    "active_route": active_route,
                    "command_x_m_s": command,
                    "samples": 8,
                    "all_outputs_bit_exact_to_base": bool(exact),
                    "all_outputs_finite": bool(finite),
                    "continuous_action_changed": bool(action_changed),
                }
            )
    y_negative = [
        row for row in rows if row["condition_id"] == "TORSO_COM_Y_NEG"
    ]
    return {
        "provider": actual_session.get_providers()[0],
        "samples": total_samples,
        "rows": rows,
        "all_outputs_finite": all(row["all_outputs_finite"] for row in rows),
        "all_inactive_routes_bit_exact": all(
            row["all_outputs_bit_exact_to_base"]
            for row in rows
            if row["active_route"] != "nominal_expert"
        ),
        "all_x0_outputs_bit_exact": all(
            row["all_outputs_bit_exact_to_base"]
            for row in rows
            if row["command_x_m_s"] == 0.0
        ),
        "both_y_negative_contexts_route_nominal": (
            len(
                {
                    (row["fit_id"], row["context_sha256"])
                    for row in y_negative
                }
            )
            == 2
            and all(
                row["active_route"] == "nominal_expert"
                for row in y_negative
            )
        ),
        "both_y_negative_fits_bind_changed_moving_action": all(
            any(
                row["fit_id"] == fit_id
                and row["command_x_m_s"] > 0.0
                and row["continuous_action_changed"]
                for row in y_negative
            )
            for fit_id in ("p30", "p31_34")
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T172 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T172 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T172_T170_POSTEXPORT_COMPOSITION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T172 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, graph in enumerate(prereg["graphs"]):
        verify(graph["raw"], f"graphs[{index}].raw")
        verify(graph["base"], f"graphs[{index}].base")

    WORK.mkdir(parents=True)
    outputs = []
    started = time.time()
    for graph in prereg["graphs"]:
        step_value = int(graph["step"])
        destination = WORK / str(step_value) / "t170_composed.onnx"
        structure = transform(
            Path(graph["raw"]["path"]),
            Path(graph["base"]["path"]),
            destination,
        )
        inference = inference_contract(
            destination,
            Path(graph["base"]["path"]),
            prereg["contexts"],
            int(prereg["inference"]["seed"]) + step_value,
        )
        outputs.append(
            {
                "step": step_value,
                "structure": structure,
                "inference": inference,
            }
        )

    zero = next(row for row in outputs if row["step"] == 0)
    trained = [row for row in outputs if row["step"] > 0]
    checks = {
        "three_graphs": len(outputs) == 3,
        "step_zero_model_byte_exact_to_t164_final": (
            zero["structure"]["model_byte_exact_to_base"]
            and zero["structure"]["changed_initializers"] == []
        ),
        "trained_graphs_change_only_nominal_pair": all(
            row["structure"]["changed_initializers"]
            == sorted(DESTINATION_NAMES)
            and row["structure"]["expected_changed_initializers"]
            == sorted(DESTINATION_NAMES)
            for row in trained
        ),
        "all_source_bindings_exact": all(
            row["structure"]["all_source_bindings_exact"] for row in outputs
        ),
        "all_nodes_byte_exact": all(
            row["structure"]["nodes_byte_exact"] for row in outputs
        ),
        "all_other_initializers_exact": all(
            row["structure"]["all_other_initializers_exact"]
            for row in outputs
        ),
        "all_initializer_names_exact": all(
            row["structure"]["initializer_names_exact"] for row in outputs
        ),
        "all_initializers_finite": all(
            row["structure"]["all_initializers_finite"] for row in outputs
        ),
        "all_inactive_routes_bit_exact": all(
            row["inference"]["all_inactive_routes_bit_exact"]
            for row in outputs
        ),
        "all_x0_outputs_bit_exact": all(
            row["inference"]["all_x0_outputs_bit_exact"] for row in outputs
        ),
        "both_y_negative_contexts_route_nominal": all(
            row["inference"]["both_y_negative_contexts_route_nominal"]
            for row in outputs
        ),
        "all_outputs_finite": all(
            row["inference"]["all_outputs_finite"] for row in outputs
        ),
        "cpu_only": all(
            row["inference"]["provider"] == "CPUExecutionProvider"
            for row in outputs
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t172_t170_postexport_composition_result.v1"
        ),
        "status": (
            "PASS_T172_T170_POSTEXPORT_COMPOSITION"
            if not failed
            else "HOLD_T172_T170_POSTEXPORT_COMPOSITION"
        ),
        "decision": (
            "EARN_T173_T170_TARGETED_Y_NEGATIVE_MATRIX_"
            "PREREGISTRATION_ONLY"
            if not failed
            else "HOLD_T170_BEHAVIOR_AND_AUDIT_COMPOSITION"
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
            "targeted_y_negative_preregistration": not failed,
            "behavior_matrix": False,
            "training": False,
            "full_r2": False,
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
        "# T172 T170 post-export composition result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Step zero is byte-exact to T164 final; trained graphs replace "
        "only the nominal adapter pair.\n"
        "- X-negative / positive routes and x=0 outputs remain bit-exact.\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n",
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
