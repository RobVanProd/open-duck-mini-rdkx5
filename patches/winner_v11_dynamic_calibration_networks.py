"""Winner-v11 calibration networks on the exact Winner-v10 action boundary.

The tensor ABI and zero-initialized response architecture are inherited from
Winner-v6.  Winner-v11 is distinct because both newly exported graphs use the
stored and inward-rounded action limits already validated by Winner-v9/v10.
No true mass, COM, inertia, or component label enters either graph.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import jax
import jax.numpy as jnp
import numpy as np

import winner_v6_dynamic_calibration_networks as base


OBS_SIZE = base.OBS_SIZE
ACTION_SIZE = base.ACTION_SIZE
HIDDEN_SIZE = base.HIDDEN_SIZE
CONTROL_DT_S = base.CONTROL_DT_S
ACTION_SCALE_RAD = base.ACTION_SCALE_RAD
CALIBRATION_TICKS = base.CALIBRATION_TICKS
AUXILIARY_RESPONSE_OBS_INDICES = base.AUXILIARY_RESPONSE_OBS_INDICES

# Exact float32 values frozen by Winner-v9 and preserved byte-for-byte by
# Winner-v10.  MAX_ACTION_DELTA is the externally stored physical boundary;
# INTERNAL_ACTION_DELTA is the inward-rounded graph implementation value.
MAX_ACTION_DELTA = np.asarray(
    [
        0.07999999076128006,
        0.059999994933605194,
        0.11999998986721039,
        0.11999998986721039,
        0.11999998986721039,
        0.03999999538064003,
        0.03999999538064003,
        0.03999999538064003,
        0.03999999538064003,
        0.03999999538064003,
        0.059999994933605194,
        0.09999998658895493,
        0.07999999076128006,
        0.09999998658895493,
    ],
    dtype=np.float32,
)
INTERNAL_ACTION_DELTA = np.asarray(
    [
        0.07999950647354126,
        0.05999951437115669,
        0.11999950557947159,
        0.11999950557947159,
        0.11999950557947159,
        0.03999951481819153,
        0.03999951481819153,
        0.03999951481819153,
        0.03999951481819153,
        0.03999951481819153,
        0.05999951437115669,
        0.09999950230121613,
        0.07999950647354126,
        0.09999950230121613,
    ],
    dtype=np.float32,
)

initialize_calibrator_parameters = base.initialize_calibrator_parameters
initialize_locomotion_adapter_parameters = base.initialize_locomotion_adapter_parameters
calibrator_auxiliary_prediction = base.calibrator_auxiliary_prediction
validate_calibration_handoff = base.validate_calibration_handoff
onnx_initializers = base.onnx_initializers


def _bounded_action(raw_action: jax.Array, previous_action: jax.Array) -> jax.Array:
    maximum_delta = jnp.asarray(INTERNAL_ACTION_DELTA)[None, :]
    absolute_bounded = jnp.clip(raw_action, -1.0, 1.0)
    lower = jnp.maximum(previous_action - maximum_delta, -1.0)
    upper = jnp.minimum(previous_action + maximum_delta, 1.0)
    return jnp.maximum(jnp.minimum(absolute_bounded, upper), lower)


def calibrator_step(
    parameters: Mapping[str, jax.Array],
    obs: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array]:
    hidden_pre = (
        obs @ parameters["obs_weight"]
        + previous_action @ parameters["previous_action_weight"]
        + h_in @ parameters["hidden_weight"]
        + parameters["hidden_bias"]
    )
    h_out = jnp.tanh(hidden_pre)
    raw_action = jnp.tanh(
        h_out @ parameters["action_weight"] + parameters["action_bias"]
    )
    action = _bounded_action(raw_action, previous_action)
    return action, action, h_out


def protected_policy_step(
    initializers: Mapping[str, jax.Array],
    obs: jax.Array,
    previous_action: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    """Transcribe the complete Winner-v10 graph, including its final clamp."""

    source_action, _ = base.protected_policy_step(initializers, obs, previous_action)
    absolute = jnp.clip(
        source_action,
        initializers["v7_action_minimum"],
        initializers["v7_action_maximum"],
    )
    lower = previous_action - initializers["v7_safe_max_action_delta"]
    upper = previous_action + initializers["v7_safe_max_action_delta"]
    action = jnp.maximum(jnp.minimum(absolute, upper), lower)
    return action, action


def locomotion_step(
    protected_initializers: Mapping[str, jax.Array],
    adapter_parameters: Mapping[str, jax.Array],
    obs: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
    calibration_context: jax.Array,
    *,
    adapter_enabled: bool = False,
) -> tuple[jax.Array, jax.Array, jax.Array]:
    protected_action, _ = protected_policy_step(
        protected_initializers, obs, previous_action
    )
    hidden_pre = (
        obs @ adapter_parameters["obs_weight"]
        + previous_action @ adapter_parameters["previous_action_weight"]
        + h_in @ adapter_parameters["hidden_weight"]
        + calibration_context @ adapter_parameters["context_hidden_weight"]
        + adapter_parameters["hidden_bias"]
    )
    h_out = jnp.tanh(hidden_pre)
    adapter_delta = jnp.tanh(
        h_out @ adapter_parameters["hidden_action_weight"]
        + calibration_context @ adapter_parameters["context_action_weight"]
        + adapter_parameters["action_bias"]
    ) * np.float32(ACTION_SCALE_RAD)
    action = (
        _bounded_action(protected_action + adapter_delta, previous_action)
        if adapter_enabled
        else protected_action
    )
    return action, action, h_out


def _replace_initializer(model: Any, name: str, value: np.ndarray) -> None:
    from onnx import numpy_helper

    replacement = numpy_helper.from_array(np.asarray(value, np.float32), name=name)
    for index, initializer in enumerate(model.graph.initializer):
        if initializer.name == name:
            model.graph.initializer[index].CopyFrom(replacement)
            return
    raise ValueError(f"missing initializer: {name}")


def export_calibrator_onnx(
    parameters: Mapping[str, jax.Array], output_path: str | Path
) -> None:
    import onnx

    output = Path(output_path)
    base.export_calibrator_onnx(parameters, output)
    model = onnx.load(output)
    _replace_initializer(
        model, "cal_max_action_delta", INTERNAL_ACTION_DELTA[None, :]
    )
    model.graph.name = "winner_v11_dynamic_calibrator"
    model.producer_name = "open-duck-winner-v11"
    onnx.checker.check_model(model)
    onnx.save(model, output)


def export_locomotion_onnx(
    protected_path: str | Path,
    adapter_parameters: Mapping[str, jax.Array],
    output_path: str | Path,
    *,
    adapter_enabled: bool = False,
) -> None:
    import onnx

    output = Path(output_path)
    # The Winner-v10 graph consumes ``continuous_actions`` in its terminal
    # Identity node.  The inherited v6 exporter renames producers only, which
    # leaves that consumer pointing at the wrapper's later output and violates
    # ONNX topological ordering.  Give the complete protected value chain its
    # final private names before delegating to the otherwise frozen exporter.
    protected = onnx.load(Path(protected_path))
    renames = {
        "continuous_actions": "protected_continuous_actions",
        "previous_action_out": "protected_previous_action_out",
    }
    for node in protected.graph.node:
        for index, name in enumerate(node.input):
            node.input[index] = renames.get(name, name)
        for index, name in enumerate(node.output):
            node.output[index] = renames.get(name, name)
    for value in protected.graph.output:
        value.name = renames.get(value.name, value.name)
    onnx.checker.check_model(protected)
    private_source = output.with_suffix(".protected-v11-input.onnx")
    if private_source.exists():
        raise FileExistsError(f"temporary protected graph already exists: {private_source}")
    try:
        onnx.save(protected, private_source)
        base.export_locomotion_onnx(
            private_source,
            adapter_parameters,
            output,
            adapter_enabled=adapter_enabled,
        )
    finally:
        private_source.unlink(missing_ok=True)
    model = onnx.load(output)
    _replace_initializer(
        model, "v6_max_action_delta", INTERNAL_ACTION_DELTA[None, :]
    )
    model.graph.name = "winner_v11_response_conditioned_locomotion"
    model.producer_name = "open-duck-winner-v11"
    onnx.checker.check_model(model)
    onnx.save(model, output)
