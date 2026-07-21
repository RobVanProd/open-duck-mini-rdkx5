"""Winner-v12 decomposed backend reference on the frozen Winner-v11 graph.

The deployable exporters and tensor ABI remain byte-for-byte the Winner-v11
implementation.  This module adds only a JAX reference for the newly introduced
response branch so a checker-only ONNX output can be compared without coupling
the result to the protected actor's cross-backend floating-point reproduction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import jax
import jax.numpy as jnp
import numpy as np

import winner_v11_dynamic_calibration_networks as base


OBS_SIZE = base.OBS_SIZE
ACTION_SIZE = base.ACTION_SIZE
HIDDEN_SIZE = base.HIDDEN_SIZE
CONTROL_DT_S = base.CONTROL_DT_S
ACTION_SCALE_RAD = base.ACTION_SCALE_RAD
CALIBRATION_TICKS = base.CALIBRATION_TICKS
AUXILIARY_RESPONSE_OBS_INDICES = base.AUXILIARY_RESPONSE_OBS_INDICES
MAX_ACTION_DELTA = base.MAX_ACTION_DELTA
INTERNAL_ACTION_DELTA = base.INTERNAL_ACTION_DELTA

initialize_calibrator_parameters = base.initialize_calibrator_parameters
initialize_locomotion_adapter_parameters = base.initialize_locomotion_adapter_parameters
calibrator_auxiliary_prediction = base.calibrator_auxiliary_prediction
validate_calibration_handoff = base.validate_calibration_handoff
onnx_initializers = base.onnx_initializers
calibrator_step = base.calibrator_step
protected_policy_step = base.protected_policy_step
locomotion_step = base.locomotion_step


def response_branch_step(
    adapter_parameters: Mapping[str, jax.Array],
    obs: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
    calibration_context: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    """Return only the new response hidden state and normalized action delta."""

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
    return h_out, adapter_delta


def export_calibrator_onnx(
    parameters: Mapping[str, jax.Array], output_path: str | Path
) -> None:
    base.export_calibrator_onnx(parameters, output_path)


def export_locomotion_onnx(
    protected_path: str | Path,
    adapter_parameters: Mapping[str, jax.Array],
    output_path: str | Path,
    *,
    adapter_enabled: bool = False,
) -> None:
    base.export_locomotion_onnx(
        protected_path,
        adapter_parameters,
        output_path,
        adapter_enabled=adapter_enabled,
    )


def assert_deployable_export_unchanged(
    v11_path: str | Path, v12_path: str | Path
) -> bool:
    """Make the no-deployable-change claim executable and byte-exact."""

    return Path(v11_path).read_bytes() == Path(v12_path).read_bytes()
