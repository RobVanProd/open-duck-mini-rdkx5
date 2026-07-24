#!/usr/bin/env python3
"""Archive the completed V112 outputs after post-training inspection held."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tarfile


WORK = Path("/content/winner_v112_work")
TRAINING = WORK / "training"
MANIFEST = Path("/content/winner_v112_recovery_manifest.json")
ARCHIVE = Path("/content/winner_v112_recovery_artifacts.tar.gz")
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def step(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def main() -> int:
    for path in (MANIFEST, ARCHIVE):
        if path.exists():
            raise FileExistsError(path)
    if not TRAINING.is_dir():
        raise FileNotFoundError(TRAINING)
    checkpoints = sorted(
        (path for path in TRAINING.iterdir() if path.is_dir()), key=step
    )
    graphs = sorted(TRAINING.glob("*.onnx"), key=step)
    checkpoint_steps = [step(path) for path in checkpoints]
    onnx_steps = [step(path) for path in graphs]
    if checkpoint_steps != EXPECTED_STEPS or onnx_steps != EXPECTED_STEPS:
        raise ValueError(
            f"unexpected completed outputs: {checkpoint_steps}, {onnx_steps}"
        )
    payload = {
        "schema_version": "winner_v112.recovery_manifest.v1",
        "status": "RECOVERED_WINNER_V112_COMPLETED_TRAINING_OUTPUTS",
        "reason": (
            "The frozen runner completed all exports. Its post-training "
            "source-checkpoint inspection held because GPU Orbax restore "
            "required an explicit sharding template."
        ),
        "checkpoint_steps": checkpoint_steps,
        "onnx_steps": onnx_steps,
        "checkpoints": [
            {
                "step": step(path),
                "name": path.name,
                "directory_sha256": directory_sha256(path),
            }
            for path in checkpoints
        ],
        "onnx": [
            {
                "step": step(path),
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in graphs
        ],
        "training_log_sha256": sha256(WORK / "training.log"),
        "run_state_sha256": sha256(WORK / "run_state.json"),
        "training_retry": False,
        "training_resume": False,
        "optimizer_steps_added": 0,
        "formal_behavior_cells": 0,
        "robot_or_rdk_access": False,
    }
    MANIFEST.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary = ARCHIVE.with_suffix(ARCHIVE.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(WORK, arcname="winner_v112_peak_torque_continuation")
    temporary.replace(ARCHIVE)
    print(payload["status"])
    print(f"manifest_sha256={sha256(MANIFEST)}")
    print(f"archive_sha256={sha256(ARCHIVE)}")
    print(f"archive_bytes={ARCHIVE.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
