#!/usr/bin/env python3
"""Remap a topology-bound Orbax checkpoint onto a verified CPU target tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from flax.training import orbax_utils
import jax
import numpy as np
from orbax import checkpoint as ocp


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")

    source = args.source.resolve()
    template_path = args.cpu_template.resolve()
    destination = args.destination.resolve()
    output = args.output.resolve()
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")

    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(template_path))
    restore_args = orbax_utils.restore_args_from_target(template)
    remapped = checkpointer.restore(
        str(source), item=template, restore_args=restore_args
    )
    checkpointer.save(str(destination), remapped)
    restored = checkpointer.restore(str(destination))

    remapped_leaves = jax.tree_util.tree_leaves(remapped)
    restored_leaves = jax.tree_util.tree_leaves(restored)
    same_structure = (
        jax.tree_util.tree_structure(template)
        == jax.tree_util.tree_structure(remapped)
        == jax.tree_util.tree_structure(restored)
    )
    errors = [
        float(np.max(np.abs(np.asarray(before) - np.asarray(after))))
        for before, after in zip(remapped_leaves, restored_leaves, strict=True)
    ]
    finite = all(np.all(np.isfinite(np.asarray(leaf))) for leaf in restored_leaves)
    checks = {
        "source_and_template_tree_structures_match": same_structure,
        "saved_cpu_checkpoint_restores_exactly": max(errors) == 0.0,
        "all_restored_leaves_finite": bool(finite),
        "all_restored_leaves_are_cpu_arrays": all(
            getattr(leaf, "sharding", None) is None
            or all(device.platform == "cpu" for device in leaf.sharding.device_set)
            for leaf in restored_leaves
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_CPU_CHECKPOINT_REMAP" if not failed else "FAIL_CPU_CHECKPOINT_REMAP"
    payload = {
        "schema_version": "orbax_cpu_checkpoint_remap.v1",
        "status": status,
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "rdk_access": False,
            "local_gpu_access": False,
            "colab_access": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "leaf_count": len(restored_leaves),
        "max_save_restore_error": max(errors),
        "inputs": {
            "source": str(source),
            "source_directory_sha256": sha256_directory(source),
            "cpu_template": str(template_path),
            "cpu_template_directory_sha256": sha256_directory(template_path),
        },
        "output": {
            "destination": str(destination),
            "destination_directory_sha256": sha256_directory(destination),
        },
        "interpretation": (
            "The destination is a topology remap of the protected checkpoint, not "
            "a trained or selected policy. Exactness is checked after save/restore."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
