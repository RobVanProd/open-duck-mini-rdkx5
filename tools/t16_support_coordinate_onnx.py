#!/usr/bin/env python3
"""Build and verify T16's exact support-coordinate ONNX conjugation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort


OBS_SIZE = 115
ACTION_SIZE = 14
HIDDEN_SIZE = 64
ACTION_SCALE_RAD = np.float32(0.25)
SUPPORT_ACTION = np.asarray(
    [
        0.0,
        0.0,
        -0.5,
        0.25,
        0.25,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.5,
        0.25,
        0.25,
    ],
    dtype=np.float32,
)
EXPECTED_INPUTS = {
    "obs": [1, OBS_SIZE],
    "previous_action": [1, ACTION_SIZE],
    "h_in": [1, HIDDEN_SIZE],
    "calibration_context": [1, HIDDEN_SIZE],
}
EXPECTED_OUTPUTS = {
    "continuous_actions": [1, ACTION_SIZE],
    "previous_action_out": [1, ACTION_SIZE],
    "h_out": [1, HIDDEN_SIZE],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def observation_delta() -> np.ndarray:
    """Return the exact source-coordinate subtraction for a final observation."""
    value = np.zeros((1, OBS_SIZE), dtype=np.float32)
    target_delta = SUPPORT_ACTION * ACTION_SCALE_RAD
    value[0, 13:27] = target_delta
    value[0, 41:55] = SUPPORT_ACTION
    value[0, 55:69] = SUPPORT_ACTION
    value[0, 69:83] = SUPPORT_ACTION
    value[0, 83:97] = target_delta
    return value


def tensor_shapes(items: Any) -> dict[str, list[int]]:
    return {
        item.name: [
            int(dimension.dim_value)
            for dimension in item.type.tensor_type.shape.dim
        ]
        for item in items
    }


def _replace_node_inputs(
    model: onnx.ModelProto,
    old: str,
    new: str,
) -> None:
    for node in model.graph.node:
        for index, name in enumerate(node.input):
            if name == old:
                node.input[index] = new


def _replace_node_values(
    model: onnx.ModelProto,
    old: str,
    new: str,
) -> None:
    for node in model.graph.node:
        for index, name in enumerate(node.input):
            if name == old:
                node.input[index] = new
        for index, name in enumerate(node.output):
            if name == old:
                node.output[index] = new


def wrap_support_coordinate(
    source: Path,
    output: Path,
) -> dict[str, Any]:
    """Conjugate a source graph into the universal-support action coordinate."""
    model = onnx.load(source)
    if tensor_shapes(model.graph.input) != EXPECTED_INPUTS:
        raise ValueError("T16 source input ABI changed")
    if tensor_shapes(model.graph.output) != EXPECTED_OUTPUTS:
        raise ValueError("T16 source output ABI changed")
    if not any(
        "continuous_actions" in node.output for node in model.graph.node
    ):
        raise ValueError("T16 source action output has no producer")
    if not any(
        "previous_action_out" in node.output for node in model.graph.node
    ):
        raise ValueError("T16 source previous-action output has no producer")

    _replace_node_inputs(model, "obs", "t16_source_obs")
    _replace_node_inputs(
        model,
        "previous_action",
        "t16_source_previous_action",
    )
    _replace_node_values(
        model,
        "continuous_actions",
        "t16_source_continuous_actions",
    )
    _replace_node_values(
        model,
        "previous_action_out",
        "t16_source_previous_action_out",
    )

    initializers = [
        numpy_helper.from_array(
            observation_delta(),
            name="t16_observation_coordinate_delta",
        ),
        numpy_helper.from_array(
            SUPPORT_ACTION[None, :],
            name="t16_support_action",
        ),
        numpy_helper.from_array(
            np.asarray([-1.0], dtype=np.float32),
            name="t16_action_min",
        ),
        numpy_helper.from_array(
            np.asarray([1.0], dtype=np.float32),
            name="t16_action_max",
        ),
    ]
    model.graph.initializer.extend(initializers)
    pre_nodes = [
        helper.make_node(
            "Sub",
            ["obs", "t16_observation_coordinate_delta"],
            ["t16_source_obs"],
            name="t16_translate_observation_to_source",
        ),
        helper.make_node(
            "Sub",
            ["previous_action", "t16_support_action"],
            ["t16_source_previous_action"],
            name="t16_translate_previous_action_to_source",
        ),
    ]
    post_nodes = [
        helper.make_node(
            "Add",
            ["t16_source_continuous_actions", "t16_support_action"],
            ["t16_shifted_continuous_actions"],
            name="t16_translate_action_from_source",
        ),
        helper.make_node(
            "Clip",
            [
                "t16_shifted_continuous_actions",
                "t16_action_min",
                "t16_action_max",
            ],
            ["continuous_actions"],
            name="t16_bound_translated_action",
        ),
        helper.make_node(
            "Add",
            ["t16_source_previous_action_out", "t16_support_action"],
            ["t16_shifted_previous_action_out"],
            name="t16_translate_state_feedback_from_source",
        ),
        helper.make_node(
            "Clip",
            [
                "t16_shifted_previous_action_out",
                "t16_action_min",
                "t16_action_max",
            ],
            ["previous_action_out"],
            name="t16_bound_translated_state_feedback",
        ),
    ]
    original_nodes = list(model.graph.node)
    del model.graph.node[:]
    model.graph.node.extend([*pre_nodes, *original_nodes, *post_nodes])
    model.producer_name = "open-duck-t16-support-coordinate"
    model.doc_string = (
        "Exact universal-support coordinate conjugation. The external ABI is "
        "unchanged; action-coordinate observation/state inputs are translated "
        "to the source frame and policy outputs are translated back."
    )
    onnx.checker.check_model(model)
    output.parent.mkdir(parents=True, exist_ok=False)
    onnx.save(model, output)
    onnx.checker.check_model(onnx.load(output))
    return {
        "source_path": str(source.resolve()),
        "source_sha256": sha256(source),
        "output_path": str(output.resolve()),
        "output_sha256": sha256(output),
        "bytes": output.stat().st_size,
        "inputs": tensor_shapes(model.graph.input),
        "outputs": tensor_shapes(model.graph.output),
        "support_action": SUPPORT_ACTION.astype(float).tolist(),
        "observation_delta_sha256": hashlib.sha256(
            observation_delta().tobytes()
        ).hexdigest(),
    }


def verify_wrapper(
    source: Path,
    wrapped: Path,
    *,
    cases: int = 256,
    seed: int = 20260726,
) -> dict[str, Any]:
    """Verify the wrapped graph against its exact source-coordinate equation."""
    source_session = ort.InferenceSession(
        str(source), providers=["CPUExecutionProvider"]
    )
    wrapped_session = ort.InferenceSession(
        str(wrapped), providers=["CPUExecutionProvider"]
    )
    source_inputs = {
        item.name: list(item.shape) for item in source_session.get_inputs()
    }
    wrapped_inputs = {
        item.name: list(item.shape) for item in wrapped_session.get_inputs()
    }
    source_outputs = {
        item.name: list(item.shape) for item in source_session.get_outputs()
    }
    wrapped_outputs = {
        item.name: list(item.shape) for item in wrapped_session.get_outputs()
    }
    if (
        source_inputs != EXPECTED_INPUTS
        or wrapped_inputs != EXPECTED_INPUTS
        or source_outputs != EXPECTED_OUTPUTS
        or wrapped_outputs != EXPECTED_OUTPUTS
    ):
        raise ValueError("T16 runtime ABI verification failed")

    rng = np.random.default_rng(seed)
    maximum_action_error = 0.0
    maximum_previous_error = 0.0
    maximum_hidden_error = 0.0
    previous_chain_exact = True
    x0_support_exact = True
    for index in range(cases):
        source_obs = rng.normal(0.0, 0.5, size=(1, OBS_SIZE)).astype(
            np.float32
        )
        source_previous = rng.uniform(
            -0.45, 0.45, size=(1, ACTION_SIZE)
        ).astype(np.float32)
        hidden = rng.normal(0.0, 0.2, size=(1, HIDDEN_SIZE)).astype(
            np.float32
        )
        context = rng.normal(0.0, 0.2, size=(1, HIDDEN_SIZE)).astype(
            np.float32
        )
        if index == 0:
            source_obs[0, 6] = 0.0
            source_previous.fill(0.0)
        else:
            source_obs[0, 6] = np.float32(0.074)
        final_obs = source_obs + observation_delta()
        final_previous = source_previous + SUPPORT_ACTION[None, :]
        source_result = source_session.run(
            None,
            {
                "obs": source_obs,
                "previous_action": source_previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        wrapped_result = wrapped_session.run(
            None,
            {
                "obs": final_obs,
                "previous_action": final_previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        expected_action = np.clip(
            source_result[0] + SUPPORT_ACTION[None, :],
            -1.0,
            1.0,
        ).astype(np.float32)
        expected_previous = np.clip(
            source_result[1] + SUPPORT_ACTION[None, :],
            -1.0,
            1.0,
        ).astype(np.float32)
        maximum_action_error = max(
            maximum_action_error,
            float(np.max(np.abs(wrapped_result[0] - expected_action))),
        )
        maximum_previous_error = max(
            maximum_previous_error,
            float(np.max(np.abs(wrapped_result[1] - expected_previous))),
        )
        maximum_hidden_error = max(
            maximum_hidden_error,
            float(np.max(np.abs(wrapped_result[2] - source_result[2]))),
        )
        previous_chain_exact &= np.array_equal(
            wrapped_result[0], wrapped_result[1]
        )
        if index == 0:
            x0_support_exact &= np.array_equal(
                wrapped_result[0],
                SUPPORT_ACTION[None, :],
            )
    return {
        "cases": cases,
        "seed": seed,
        "maximum_action_error": maximum_action_error,
        "maximum_previous_action_error": maximum_previous_error,
        "maximum_hidden_error": maximum_hidden_error,
        "previous_action_out_equals_action_bit_exact": previous_chain_exact,
        "x0_output_equals_support_action_bit_exact": x0_support_exact,
        "inputs_exact": wrapped_inputs == EXPECTED_INPUTS,
        "outputs_exact": wrapped_outputs == EXPECTED_OUTPUTS,
        "provider": wrapped_session.get_providers()[0],
    }
