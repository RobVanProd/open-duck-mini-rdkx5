#!/usr/bin/env python3
"""Build and verify T17's bounded support-centered ONNX homeomorphism."""

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
FLOAT32_EPSILON = float(np.finfo(np.float32).eps)
CONTRACT_TOLERANCE = 32.0 * FLOAT32_EPSILON
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
HOME_ACTION_RAD = np.asarray(
    [
        0.002,
        0.053,
        -0.630,
        1.368,
        -0.784,
        0.0,
        0.0,
        0.0,
        0.0,
        -0.003,
        -0.065,
        0.635,
        1.379,
        -0.796,
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


def forward_action(source_action: np.ndarray) -> np.ndarray:
    """Map source action coordinates into the support-centered action box."""
    source = np.asarray(source_action, dtype=np.float32)
    support = SUPPORT_ACTION.reshape((1,) * (source.ndim - 1) + (-1,))
    upper_slope = np.float32(1.0) - support
    lower_slope = np.float32(1.0) + support
    slope = np.where(source >= np.float32(0.0), upper_slope, lower_slope)
    return (support + source * slope).astype(np.float32)


def inverse_action(final_action: np.ndarray) -> np.ndarray:
    """Map support-centered action coordinates back to source coordinates."""
    final = np.asarray(final_action, dtype=np.float32)
    support = SUPPORT_ACTION.reshape((1,) * (final.ndim - 1) + (-1,))
    upper_slope = np.float32(1.0) - support
    lower_slope = np.float32(1.0) + support
    slope = np.where(final >= support, upper_slope, lower_slope)
    return ((final - support) / slope).astype(np.float32)


def observation_parameters() -> dict[str, np.ndarray]:
    """Return elementwise center/base/slopes for the observation inverse."""
    center = np.zeros((1, OBS_SIZE), dtype=np.float32)
    base = np.zeros((1, OBS_SIZE), dtype=np.float32)
    upper = np.ones((1, OBS_SIZE), dtype=np.float32)
    lower = np.ones((1, OBS_SIZE), dtype=np.float32)
    support_rad = SUPPORT_ACTION * ACTION_SCALE_RAD

    center[0, 13:27] = support_rad
    upper[0, 13:27] = np.float32(1.0) - SUPPORT_ACTION
    lower[0, 13:27] = np.float32(1.0) + SUPPORT_ACTION
    for start in (41, 55, 69):
        center[0, start : start + ACTION_SIZE] = SUPPORT_ACTION
        upper[0, start : start + ACTION_SIZE] = (
            np.float32(1.0) - SUPPORT_ACTION
        )
        lower[0, start : start + ACTION_SIZE] = (
            np.float32(1.0) + SUPPORT_ACTION
        )
    center[0, 83:97] = HOME_ACTION_RAD + support_rad
    base[0, 83:97] = HOME_ACTION_RAD
    upper[0, 83:97] = np.float32(1.0) - SUPPORT_ACTION
    lower[0, 83:97] = np.float32(1.0) + SUPPORT_ACTION
    return {
        "center": center,
        "base": base,
        "upper_slope": upper,
        "lower_slope": lower,
    }


def inverse_observation(final_obs: np.ndarray) -> np.ndarray:
    """Map a final observation into the source policy coordinate."""
    final = np.asarray(final_obs, dtype=np.float32)
    parameters = observation_parameters()
    slope = np.where(
        final >= parameters["center"],
        parameters["upper_slope"],
        parameters["lower_slope"],
    )
    return (
        parameters["base"]
        + (final - parameters["center"]) / slope
    ).astype(np.float32)


def forward_observation(source_obs: np.ndarray) -> np.ndarray:
    """Construct the physical observation conjugate to a source observation."""
    source = np.asarray(source_obs, dtype=np.float32)
    parameters = observation_parameters()
    delta = source - parameters["base"]
    slope = np.where(
        delta >= np.float32(0.0),
        parameters["upper_slope"],
        parameters["lower_slope"],
    )
    return (parameters["center"] + delta * slope).astype(np.float32)


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


def _inverse_nodes(
    *,
    value: str,
    prefix: str,
    center: str,
    base: str,
    upper: str,
    lower: str,
    output: str,
) -> list[onnx.NodeProto]:
    return [
        helper.make_node(
            "GreaterOrEqual",
            [value, center],
            [f"{prefix}_upper_half"],
            name=f"{prefix}_select_half",
        ),
        helper.make_node(
            "Where",
            [f"{prefix}_upper_half", upper, lower],
            [f"{prefix}_slope"],
            name=f"{prefix}_select_slope",
        ),
        helper.make_node(
            "Sub",
            [value, center],
            [f"{prefix}_centered"],
            name=f"{prefix}_subtract_center",
        ),
        helper.make_node(
            "Div",
            [f"{prefix}_centered", f"{prefix}_slope"],
            [f"{prefix}_source_delta"],
            name=f"{prefix}_divide_slope",
        ),
        helper.make_node(
            "Add",
            [f"{prefix}_source_delta", base],
            [output],
            name=f"{prefix}_add_source_base",
        ),
    ]


def _forward_nodes(
    *,
    value: str,
    prefix: str,
    output: str,
) -> list[onnx.NodeProto]:
    return [
        helper.make_node(
            "GreaterOrEqual",
            [value, "t17_action_zero"],
            [f"{prefix}_upper_half"],
            name=f"{prefix}_select_half",
        ),
        helper.make_node(
            "Where",
            [
                f"{prefix}_upper_half",
                "t17_action_upper_slope",
                "t17_action_lower_slope",
            ],
            [f"{prefix}_slope"],
            name=f"{prefix}_select_slope",
        ),
        helper.make_node(
            "Mul",
            [value, f"{prefix}_slope"],
            [f"{prefix}_scaled"],
            name=f"{prefix}_scale",
        ),
        helper.make_node(
            "Add",
            [f"{prefix}_scaled", "t17_support_action"],
            [output],
            name=f"{prefix}_add_support_center",
        ),
    ]


def wrap_support_homeomorphism(
    source: Path,
    output: Path,
) -> dict[str, Any]:
    """Conjugate a source graph with the bounded support-centered map."""
    model = onnx.load(source)
    if tensor_shapes(model.graph.input) != EXPECTED_INPUTS:
        raise ValueError("T17 source input ABI changed")
    if tensor_shapes(model.graph.output) != EXPECTED_OUTPUTS:
        raise ValueError("T17 source output ABI changed")

    _replace_node_inputs(model, "obs", "t17_source_obs")
    _replace_node_inputs(
        model,
        "previous_action",
        "t17_source_previous_action",
    )
    _replace_node_values(
        model,
        "continuous_actions",
        "t17_source_continuous_actions",
    )
    _replace_node_values(
        model,
        "previous_action_out",
        "t17_source_previous_action_out",
    )

    parameters = observation_parameters()
    initializers = [
        numpy_helper.from_array(
            parameters["center"], name="t17_observation_center"
        ),
        numpy_helper.from_array(
            parameters["base"], name="t17_observation_source_base"
        ),
        numpy_helper.from_array(
            parameters["upper_slope"],
            name="t17_observation_upper_slope",
        ),
        numpy_helper.from_array(
            parameters["lower_slope"],
            name="t17_observation_lower_slope",
        ),
        numpy_helper.from_array(
            SUPPORT_ACTION[None, :], name="t17_support_action"
        ),
        numpy_helper.from_array(
            np.zeros((1, ACTION_SIZE), dtype=np.float32),
            name="t17_action_source_base",
        ),
        numpy_helper.from_array(
            np.float32(1.0)[None]
            - SUPPORT_ACTION[None, :],
            name="t17_action_upper_slope",
        ),
        numpy_helper.from_array(
            np.float32(1.0)[None]
            + SUPPORT_ACTION[None, :],
            name="t17_action_lower_slope",
        ),
        numpy_helper.from_array(
            np.asarray([0.0], dtype=np.float32),
            name="t17_action_zero",
        ),
    ]
    model.graph.initializer.extend(initializers)
    pre_nodes = [
        *_inverse_nodes(
            value="obs",
            prefix="t17_observation_inverse",
            center="t17_observation_center",
            base="t17_observation_source_base",
            upper="t17_observation_upper_slope",
            lower="t17_observation_lower_slope",
            output="t17_source_obs",
        ),
        *_inverse_nodes(
            value="previous_action",
            prefix="t17_previous_action_inverse",
            center="t17_support_action",
            base="t17_action_source_base",
            upper="t17_action_upper_slope",
            lower="t17_action_lower_slope",
            output="t17_source_previous_action",
        ),
    ]
    post_nodes = [
        *_forward_nodes(
            value="t17_source_continuous_actions",
            prefix="t17_continuous_action_forward",
            output="continuous_actions",
        ),
        *_forward_nodes(
            value="t17_source_previous_action_out",
            prefix="t17_previous_action_forward",
            output="previous_action_out",
        ),
    ]
    original_nodes = list(model.graph.node)
    del model.graph.node[:]
    model.graph.node.extend([*pre_nodes, *original_nodes, *post_nodes])
    model.producer_name = "open-duck-t17-support-homeomorphism"
    model.doc_string = (
        "Bounded support-centered action homeomorphism. Per joint it is the "
        "unique continuous map that is affine on each side of source zero "
        "and sends source -1/0/+1 to final -1/support/+1."
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
        "home_action_rad": HOME_ACTION_RAD.astype(float).tolist(),
    }


def verify_wrapper(
    source: Path,
    wrapped: Path,
    *,
    cases: int = 256,
    seed: int = 20260726,
) -> dict[str, Any]:
    """Verify the wrapper against the frozen bounded-map equations."""
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
        raise ValueError("T17 runtime ABI verification failed")

    rng = np.random.default_rng(seed)
    maximum_action_error = 0.0
    maximum_previous_error = 0.0
    maximum_hidden_error = 0.0
    maximum_observation_roundtrip_error = 0.0
    maximum_action_roundtrip_error = 0.0
    previous_chain_exact = True
    x0_support_exact = True
    output_bounds_exact = True
    for index in range(cases):
        source_obs = rng.normal(0.0, 0.4, size=(1, OBS_SIZE)).astype(
            np.float32
        )
        source_obs[0, 83:97] = (
            HOME_ACTION_RAD
            + rng.uniform(
                -0.20, 0.20, size=(ACTION_SIZE,)
            ).astype(np.float32)
        )
        source_previous = rng.uniform(
            -0.95, 0.95, size=(1, ACTION_SIZE)
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
        final_obs = forward_observation(source_obs)
        final_previous = forward_action(source_previous)
        source_equivalent_obs = inverse_observation(final_obs)
        source_equivalent_previous = inverse_action(final_previous)
        source_result = source_session.run(
            None,
            {
                "obs": source_equivalent_obs,
                "previous_action": source_equivalent_previous,
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
        expected_action = forward_action(source_result[0])
        expected_previous = forward_action(source_result[1])
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
        maximum_observation_roundtrip_error = max(
            maximum_observation_roundtrip_error,
            float(np.max(np.abs(source_equivalent_obs - source_obs))),
        )
        maximum_action_roundtrip_error = max(
            maximum_action_roundtrip_error,
            float(
                np.max(
                    np.abs(source_equivalent_previous - source_previous)
                )
            ),
        )
        previous_chain_exact &= np.array_equal(
            wrapped_result[0], wrapped_result[1]
        )
        x0_support_exact &= index != 0 or np.array_equal(
            wrapped_result[0],
            SUPPORT_ACTION[None, :],
        )
        output_bounds_exact &= bool(
            np.all(wrapped_result[0] >= np.float32(-1.0))
            and np.all(wrapped_result[0] <= np.float32(1.0))
            and np.all(wrapped_result[1] >= np.float32(-1.0))
            and np.all(wrapped_result[1] <= np.float32(1.0))
        )
    return {
        "cases": cases,
        "seed": seed,
        "float32_epsilon": FLOAT32_EPSILON,
        "contract_tolerance": CONTRACT_TOLERANCE,
        "maximum_action_error": maximum_action_error,
        "maximum_previous_action_error": maximum_previous_error,
        "maximum_hidden_error": maximum_hidden_error,
        "maximum_observation_roundtrip_error": (
            maximum_observation_roundtrip_error
        ),
        "maximum_action_roundtrip_error": maximum_action_roundtrip_error,
        "previous_action_out_equals_action_bit_exact": previous_chain_exact,
        "x0_output_equals_support_action_bit_exact": x0_support_exact,
        "output_bounds_exact": output_bounds_exact,
        "inputs_exact": wrapped_inputs == EXPECTED_INPUTS,
        "outputs_exact": wrapped_outputs == EXPECTED_OUTPUTS,
        "provider": wrapped_session.get_providers()[0],
    }
