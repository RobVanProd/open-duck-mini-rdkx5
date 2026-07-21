"""Explicit gradient composition for the Winner-v21 two-update proof."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping

import jax
import jax.numpy as jnp
import numpy as np

import winner_v21_predictor_preserving_joint_support as v21


FROZEN_PREDICTOR_SCALE = np.float32(8.393629541414427e-11)
SNAPSHOT_SCHEMA = "winner_v21.predictor_preserving_snapshot.v1"


def compose_gradients(
    ppo_gradients: Mapping[str, Any], predictor_gradients: Mapping[str, Any]
) -> dict[str, jax.Array]:
    """Return the exact per-leaf gradient consumed by the optimizer."""

    expected = set(v21.JOINT_TRAINABLE_KEYS)
    if set(ppo_gradients) != expected or set(predictor_gradients) != expected:
        raise ValueError("Winner-v21 v2 gradient tree schema changed")
    scale = jnp.asarray(FROZEN_PREDICTOR_SCALE, dtype=jnp.float32)
    return {
        key: jnp.asarray(ppo_gradients[key], dtype=jnp.float32)
        + scale * jnp.asarray(predictor_gradients[key], dtype=jnp.float32)
        for key in v21.JOINT_TRAINABLE_KEYS
    }


def _array_manifest_sha256(arrays: Mapping[str, np.ndarray]) -> str:
    manifest = [
        {
            "name": name,
            "dtype": str(np.asarray(value).dtype),
            "shape": list(np.asarray(value).shape),
            "sha256": hashlib.sha256(
                np.ascontiguousarray(value).tobytes()
            ).hexdigest(),
        }
        for name, value in sorted(arrays.items())
    ]
    return hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def save_snapshot(
    path: Path,
    parameters: Mapping[str, Any],
    optimizer: Mapping[str, Any],
    metadata: Mapping[str, Any],
    target_mean: Any,
    target_std: Any,
) -> dict[str, Any]:
    """Atomically save all parameters and the twelve-leaf optimizer state."""

    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    parameter_keys = tuple(sorted(parameters))
    optimizer_keys = tuple(v21.JOINT_TRAINABLE_KEYS)
    if set(optimizer.get("m", {})) != set(optimizer_keys) or set(
        optimizer.get("v", {})
    ) != set(optimizer_keys):
        raise ValueError("Winner-v21 optimizer tree schema changed")
    arrays: dict[str, np.ndarray] = {
        "target_mean": np.asarray(target_mean),
        "target_std": np.asarray(target_std),
        "optimizer.count": np.asarray(optimizer["count"]),
        **{
            f"parameter.{name}": np.asarray(parameters[name])
            for name in parameter_keys
        },
        **{
            f"optimizer.m.{name}": np.asarray(optimizer["m"][name])
            for name in optimizer_keys
        },
        **{
            f"optimizer.v.{name}": np.asarray(optimizer["v"][name])
            for name in optimizer_keys
        },
    }
    protected = {
        **dict(metadata),
        "schema_version": SNAPSHOT_SCHEMA,
        "parameter_keys": list(parameter_keys),
        "optimizer_keys": list(optimizer_keys),
        "state_payload_sha256": _array_manifest_sha256(arrays),
    }
    protected["metadata_payload_sha256"] = hashlib.sha256(
        json.dumps(protected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    arrays["metadata_json"] = np.asarray(
        json.dumps(protected, allow_nan=False, sort_keys=True, separators=(",", ":"))
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
    ) as stream:
        temp_path = Path(stream.name)
        np.savez_compressed(stream, **arrays)
    temp_path.replace(path)
    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
        "completed_updates": protected.get("completed_updates"),
        "state_payload_sha256": protected["state_payload_sha256"],
        "metadata_payload_sha256": protected["metadata_payload_sha256"],
    }


def load_snapshot(path: Path) -> dict[str, Any]:
    """Read and verify a Winner-v21 twelve-leaf optimizer snapshot."""

    with np.load(path, allow_pickle=False) as archive:
        if len(archive.files) != len(set(archive.files)):
            raise ValueError("Winner-v21 snapshot contains duplicate members")
        arrays = {name: archive[name].copy() for name in archive.files}
    metadata_array = np.asarray(arrays.pop("metadata_json", None))
    if metadata_array.shape != () or metadata_array.dtype.kind != "U":
        raise ValueError("Winner-v21 snapshot metadata layout changed")
    metadata = json.loads(str(metadata_array.item()))
    if metadata.get("schema_version") != SNAPSHOT_SCHEMA:
        raise ValueError("Winner-v21 snapshot schema changed")
    metadata_hash = metadata.pop("metadata_payload_sha256", None)
    if metadata_hash != hashlib.sha256(
        json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest():
        raise ValueError("Winner-v21 snapshot metadata digest changed")
    if metadata.pop("state_payload_sha256", None) != _array_manifest_sha256(arrays):
        raise ValueError("Winner-v21 snapshot state digest changed")
    parameter_keys = tuple(metadata.pop("parameter_keys", ()))
    optimizer_keys = tuple(metadata.pop("optimizer_keys", ()))
    if optimizer_keys != v21.JOINT_TRAINABLE_KEYS:
        raise ValueError("Winner-v21 snapshot optimizer key order changed")
    expected = {
        "target_mean",
        "target_std",
        "optimizer.count",
        *(f"parameter.{name}" for name in parameter_keys),
        *(f"optimizer.m.{name}" for name in optimizer_keys),
        *(f"optimizer.v.{name}" for name in optimizer_keys),
    }
    if set(arrays) != expected:
        raise ValueError("Winner-v21 snapshot member schema changed")
    return {
        "parameters": {
            name: arrays[f"parameter.{name}"] for name in parameter_keys
        },
        "optimizer": {
            "count": arrays["optimizer.count"],
            "m": {name: arrays[f"optimizer.m.{name}"] for name in optimizer_keys},
            "v": {name: arrays[f"optimizer.v.{name}"] for name in optimizer_keys},
        },
        "metadata": metadata,
        "target_mean": arrays["target_mean"],
        "target_std": arrays["target_std"],
    }
