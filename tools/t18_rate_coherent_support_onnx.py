#!/usr/bin/env python3
"""Build and verify T18's rate-coherent support-centered ONNX graph."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort

from t17_support_homeomorphism_onnx import (
    ACTION_SCALE_RAD,
    ACTION_SIZE,
    CONTRACT_TOLERANCE,
    EXPECTED_INPUTS,
    EXPECTED_OUTPUTS,
    HIDDEN_SIZE,
    OBS_SIZE,
    SUPPORT_ACTION,
    forward_action,
    forward_observation,
    inverse_action,
    inverse_observation,
    sha256,
    tensor_shapes,
    wrap_support_homeomorphism,
)


CONTROL_DT_S = np.float32(0.02)
RATE_LIMITS_RAD_S = np.asarray(
    [
        1.0,
        0.75,
        1.5,
        1.5,
        1.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.75,
        1.25,
        1.0,
        1.25,
    ],
    dtype=np.float32,
)
MAX_ACTION_DELTA = (
    RATE_LIMITS_RAD_S * CONTROL_DT_S / ACTION_SCALE_RAD
).astype(np.float32)


def rate_project(
    target_action: np.ndarray,
    previous_action: np.ndarray,
) -> np.ndarray:
    """Apply the frozen physical rate vector in normalized action units."""
    target = np.asarray(target_action, dtype=np.float32)
    previous = np.asarray(previous_action, dtype=np.float32)
    delta = MAX_ACTION_DELTA.reshape(
        (1,) * (target.ndim - 1) + (-1,)
    )
    lower = np.maximum(
        previous - delta, np.float32(-1.0)
    ).astype(np.float32)
    upper = np.minimum(
        previous + delta, np.float32(1.0)
    ).astype(np.float32)
    return np.clip(target, lower, upper).astype(np.float32)


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


def wrap_rate_coherent_support(
    source: Path,
    output: Path,
) -> dict[str, Any]:
    """Compose T17 with the frozen physical final-action rate transition."""
    base = output.parent / "base" / "support_homeomorphism.onnx"
    base_receipt = wrap_support_homeomorphism(source, base)
    model = onnx.load(base)
    if tensor_shapes(model.graph.input) != EXPECTED_INPUTS:
        raise ValueError("T18 base input ABI changed")
    if tensor_shapes(model.graph.output) != EXPECTED_OUTPUTS:
        raise ValueError("T18 base output ABI changed")
    _replace_node_values(
        model,
        "continuous_actions",
        "t18_unprojected_continuous_actions",
    )
    _replace_node_values(
        model,
        "previous_action_out",
        "t18_unprojected_previous_action_out",
    )
    model.graph.initializer.extend(
        [
            numpy_helper.from_array(
                MAX_ACTION_DELTA[None, :],
                name="t18_max_action_delta",
            ),
            numpy_helper.from_array(
                np.asarray([-1.0], dtype=np.float32),
                name="t18_action_min",
            ),
            numpy_helper.from_array(
                np.asarray([1.0], dtype=np.float32),
                name="t18_action_max",
            ),
        ]
    )
    model.graph.node.extend(
        [
            helper.make_node(
                "Sub",
                ["previous_action", "t18_max_action_delta"],
                ["t18_rate_lower_raw"],
                name="t18_rate_lower_raw",
            ),
            helper.make_node(
                "Clip",
                [
                    "t18_rate_lower_raw",
                    "t18_action_min",
                    "t18_action_max",
                ],
                ["t18_rate_lower"],
                name="t18_bound_rate_lower",
            ),
            helper.make_node(
                "Add",
                ["previous_action", "t18_max_action_delta"],
                ["t18_rate_upper_raw"],
                name="t18_rate_upper_raw",
            ),
            helper.make_node(
                "Clip",
                [
                    "t18_rate_upper_raw",
                    "t18_action_min",
                    "t18_action_max",
                ],
                ["t18_rate_upper"],
                name="t18_bound_rate_upper",
            ),
            helper.make_node(
                "Max",
                [
                    "t18_unprojected_continuous_actions",
                    "t18_rate_lower",
                ],
                ["t18_rate_lower_projected"],
                name="t18_project_final_action_lower",
            ),
            helper.make_node(
                "Min",
                ["t18_rate_lower_projected", "t18_rate_upper"],
                ["continuous_actions"],
                name="t18_project_final_action_upper",
            ),
            helper.make_node(
                "Identity",
                ["continuous_actions"],
                ["previous_action_out"],
                name="t18_feed_realized_action_back",
            ),
        ]
    )
    model.producer_name = "open-duck-t18-rate-coherent-support"
    model.doc_string = (
        "T17 bounded support-centered homeomorphism followed by the frozen "
        "full measured physical rate transition. The realized final action "
        "is returned as previous_action_out."
    )
    onnx.checker.check_model(model)
    onnx.save(model, output)
    onnx.checker.check_model(onnx.load(output))
    return {
        "source_path": str(source.resolve()),
        "source_sha256": sha256(source),
        "base": base_receipt,
        "output_path": str(output.resolve()),
        "output_sha256": sha256(output),
        "bytes": output.stat().st_size,
        "inputs": tensor_shapes(model.graph.input),
        "outputs": tensor_shapes(model.graph.output),
        "support_action": SUPPORT_ACTION.astype(float).tolist(),
        "rate_limits_rad_s": RATE_LIMITS_RAD_S.astype(float).tolist(),
        "maximum_action_delta": MAX_ACTION_DELTA.astype(float).tolist(),
    }


def verify_wrapper(
    source: Path,
    wrapped: Path,
    *,
    cases: int = 256,
    seed: int = 20260726,
) -> dict[str, Any]:
    """Verify T18 against T17 plus the frozen physical rate equation."""
    base = wrapped.parent / "base" / "support_homeomorphism.onnx"
    if not base.is_file():
        raise FileNotFoundError(base)
    base_session = ort.InferenceSession(
        str(base), providers=["CPUExecutionProvider"]
    )
    wrapped_session = ort.InferenceSession(
        str(wrapped), providers=["CPUExecutionProvider"]
    )
    wrapped_inputs = {
        item.name: list(item.shape) for item in wrapped_session.get_inputs()
    }
    wrapped_outputs = {
        item.name: list(item.shape) for item in wrapped_session.get_outputs()
    }
    if (
        wrapped_inputs != EXPECTED_INPUTS
        or wrapped_outputs != EXPECTED_OUTPUTS
    ):
        raise ValueError("T18 runtime ABI verification failed")

    rng = np.random.default_rng(seed)
    maximum_action_error = 0.0
    maximum_previous_error = 0.0
    maximum_hidden_error = 0.0
    maximum_rate_excess = 0.0
    previous_chain_exact = True
    x0_support_exact = True
    output_bounds_exact = True
    for index in range(cases):
        source_obs = rng.normal(0.0, 0.4, size=(1, OBS_SIZE)).astype(
            np.float32
        )
        source_obs[0, 83:97] = (
            np.asarray(
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
            + rng.uniform(
                -0.20, 0.20, size=(ACTION_SIZE,)
            ).astype(np.float32)
        )
        source_previous = rng.uniform(
            -0.90, 0.90, size=(1, ACTION_SIZE)
        ).astype(np.float32)
        if index == 0:
            source_obs[0, 6] = 0.0
            source_previous.fill(0.0)
        else:
            source_obs[0, 6] = np.float32(0.074)
        final_obs = forward_observation(source_obs)
        final_previous = forward_action(source_previous)
        hidden = rng.normal(0.0, 0.2, size=(1, HIDDEN_SIZE)).astype(
            np.float32
        )
        context = rng.normal(0.0, 0.2, size=(1, HIDDEN_SIZE)).astype(
            np.float32
        )
        feeds = {
            "obs": final_obs,
            "previous_action": final_previous,
            "h_in": hidden,
            "calibration_context": context,
        }
        base_result = base_session.run(None, feeds)
        wrapped_result = wrapped_session.run(None, feeds)
        expected = rate_project(base_result[0], final_previous)
        maximum_action_error = max(
            maximum_action_error,
            float(np.max(np.abs(wrapped_result[0] - expected))),
        )
        maximum_previous_error = max(
            maximum_previous_error,
            float(np.max(np.abs(wrapped_result[1] - expected))),
        )
        maximum_hidden_error = max(
            maximum_hidden_error,
            float(np.max(np.abs(wrapped_result[2] - base_result[2]))),
        )
        realized_rate_excess = (
            np.abs(wrapped_result[0] - final_previous)
            - MAX_ACTION_DELTA[None, :]
        )
        maximum_rate_excess = max(
            maximum_rate_excess,
            float(np.max(np.maximum(realized_rate_excess, 0.0))),
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
        )
        if np.max(
            np.abs(
                inverse_action(final_previous) - source_previous
            )
        ) > CONTRACT_TOLERANCE:
            raise RuntimeError("T18 action-coordinate roundtrip changed")
        if np.max(
            np.abs(
                inverse_observation(final_obs) - source_obs
            )
        ) > CONTRACT_TOLERANCE:
            raise RuntimeError("T18 observation-coordinate roundtrip changed")
    return {
        "cases": cases,
        "seed": seed,
        "contract_tolerance": CONTRACT_TOLERANCE,
        "maximum_action_error": maximum_action_error,
        "maximum_previous_action_error": maximum_previous_error,
        "maximum_hidden_error": maximum_hidden_error,
        "maximum_normalized_rate_excess": maximum_rate_excess,
        "previous_action_out_equals_action_bit_exact": previous_chain_exact,
        "x0_output_equals_support_action_bit_exact": x0_support_exact,
        "output_bounds_exact": output_bounds_exact,
        "inputs_exact": wrapped_inputs == EXPECTED_INPUTS,
        "outputs_exact": wrapped_outputs == EXPECTED_OUTPUTS,
        "provider": wrapped_session.get_providers()[0],
    }
