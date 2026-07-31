"""Training-only static support-target teacher selected by Winner-v42.

The privileged configuration identifier is used only to assemble stopped
teacher labels.  It is never an actor input and this module exports no ONNX
state.  Supervision is limited to the six pitch-chain elements actually varied
and tested by Winner-v42.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

import jax
import jax.numpy as jnp
import numpy as np

import winner_v12_calibrator_training as training


CONFIGURATION_IDS = (
    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
    "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
    "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
    "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15",
)
PITCH_ACTION_INDICES = (2, 3, 4, 11, 12, 13)
MIRROR_MATRIX = np.asarray(
    [
        [-1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ],
    dtype=np.float32,
)


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def expand_coordinates(coordinates: Any) -> np.ndarray:
    values = np.asarray(coordinates, dtype=np.float32)
    if values.shape != (3,) or not np.all(np.isfinite(values)):
        raise ValueError("Winner-v43 teacher coordinate shape changed")
    action = np.zeros((training.ACTION_SIZE,), dtype=np.float32)
    action[np.asarray(PITCH_ACTION_INDICES, dtype=np.int64)] = values @ MIRROR_MATRIX.T
    if np.any(np.abs(action) > 1.0):
        raise ValueError("Winner-v43 teacher target exceeds normalized action range")
    return action


def load_teacher_table(result: Mapping[str, Any]) -> dict[str, np.ndarray]:
    if (
        result.get("schema_version") != "winner_v42.static_target_teacher_table_result.v1"
        or result.get("status") != "PASS_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        or result.get("decision") != "AUTHORIZE_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT_ONLY"
        or result.get("summary", {}).get("configuration_pass_count") != 15
        or result.get("summary", {}).get("configuration_hold_ids") != []
        or result.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v42 does not authorize the Winner-v43 teacher")
    rows = result.get("configuration_results")
    if not isinstance(rows, list) or [row.get("configuration_id") for row in rows] != list(CONFIGURATION_IDS):
        raise ValueError("Winner-v43 teacher configuration set changed")
    public_table = result.get("teacher_table")
    if not isinstance(public_table, Mapping) or set(public_table) != set(CONFIGURATION_IDS):
        raise ValueError("Winner-v43 public teacher table changed")
    table: dict[str, np.ndarray] = {}
    for row in rows:
        configuration_id = row["configuration_id"]
        public = public_table[configuration_id]
        if (
            row.get("shared_support_pass_count", 0) <= 0
            or row.get("selected_kind") != "shared_support_pass"
            or row.get("selected_replay_exact") is not True
            or public.get("shared_support_pass") is not True
            or public.get("candidate_index") != row.get("selected_candidate_index")
            or public.get("coordinates") != row.get("selected_coordinates")
            or public.get("coordinates_sha256") != row.get("selected_coordinates_sha256")
        ):
            raise ValueError("Winner-v43 selected teacher row changed")
        action = expand_coordinates(public["coordinates"])
        replays = row.get("selected_replay_results")
        if not isinstance(replays, list) or len(replays) != 2:
            raise ValueError("Winner-v43 selected replay evidence changed")
        expected_hash = array_sha256(action)
        if any(
            replay.get("support_pass") is not True
            or replay.get("terminal") is not None
            or replay.get("raw_target_sha256") != expected_hash
            for replay in replays
        ):
            raise ValueError("Winner-v43 selected raw target is not replay-bound")
        action.setflags(write=False)
        table[configuration_id] = action
    return table


def build_teacher_batch(
    configuration_ids: Sequence[str],
    previous_actions: Any,
    valid_mask: Any,
    table: Mapping[str, np.ndarray],
) -> tuple[jax.Array, jax.Array, jax.Array]:
    """Return raw targets, graph-bounded stopped targets, and pitch-only mask."""

    previous = jnp.asarray(previous_actions, dtype=jnp.float32)
    valid = np.asarray(valid_mask, dtype=np.float32)
    if (
        previous.ndim != 3
        or previous.shape[-1] != training.ACTION_SIZE
        or valid.shape != previous.shape[:2]
        or len(configuration_ids) != previous.shape[0]
        or not np.all(np.isfinite(valid))
        or np.any((valid != 0.0) & (valid != 1.0))
    ):
        raise ValueError("Winner-v43 teacher batch shape or validity mask changed")
    identifiers = [str(item) for item in configuration_ids]
    selected = set(CONFIGURATION_IDS)
    if set(identifiers) & selected != selected:
        raise ValueError("Winner-v43 teacher batch omits a selected configuration")
    if any(identifiers.count(name) != 2 for name in CONFIGURATION_IDS):
        raise ValueError("Winner-v43 selected configurations are not two-plant pairs")
    if set(table) != selected:
        raise ValueError("Winner-v43 teacher table key set changed")

    raw = np.zeros(previous.shape, dtype=np.float32)
    mask = np.zeros(previous.shape, dtype=np.float32)
    pitch = np.asarray(PITCH_ACTION_INDICES, dtype=np.int64)
    for environment, configuration_id in enumerate(identifiers):
        if configuration_id not in selected:
            continue
        target = np.asarray(table[configuration_id], dtype=np.float32)
        if target.shape != (training.ACTION_SIZE,) or not np.all(np.isfinite(target)):
            raise ValueError("Winner-v43 teacher table value changed")
        raw[environment, :, :] = target
        mask[environment][:, pitch] = valid[environment, :, None]
    raw_jax = jax.lax.stop_gradient(jnp.asarray(raw, dtype=jnp.float32))
    bounded = jax.lax.stop_gradient(training.bounded_action(raw_jax, previous))
    return raw_jax, bounded, jnp.asarray(mask, dtype=jnp.float32)


def static_target_teacher_loss(
    candidate_actions: Any,
    configuration_ids: Sequence[str],
    previous_actions: Any,
    valid_mask: Any,
    table: Mapping[str, np.ndarray],
) -> tuple[jax.Array, dict[str, jax.Array]]:
    candidate = jnp.asarray(candidate_actions, dtype=jnp.float32)
    raw, bounded, mask = build_teacher_batch(
        configuration_ids, previous_actions, valid_mask, table
    )
    if candidate.shape != bounded.shape:
        raise ValueError("Winner-v43 candidate action shape changed")
    denominator = jnp.sum(mask)
    if float(denominator) <= 0.0:
        raise ValueError("Winner-v43 teacher mask is empty")
    error = candidate - bounded
    selected_abs = jnp.where(mask > 0.0, jnp.abs(error), jnp.float32(0.0))
    loss = jnp.sum(jnp.square(error) * mask) / denominator
    return loss, {
        "static_target_teacher_loss": loss,
        "selected_elements": denominator,
        "maximum_selected_action_delta": jnp.max(selected_abs),
        "raw_target_max_abs": jnp.max(jnp.abs(raw)),
        "bounded_target_max_abs": jnp.max(jnp.abs(bounded)),
    }


def combine_objective(
    baseline_loss: jax.Array,
    teacher_loss: jax.Array,
    teacher_scale: Any,
    *,
    enabled: bool,
) -> jax.Array:
    """Add the teacher only when explicitly enabled; disabled is exact."""

    if not enabled:
        return baseline_loss
    scale = jnp.asarray(teacher_scale, dtype=jnp.float32)
    if scale.ndim != 0:
        raise ValueError("Winner-v43 teacher scale must be scalar")
    return baseline_loss + scale * teacher_loss
