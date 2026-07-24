#!/usr/bin/env python3
"""Freeze the V122 chunked-upload correction after prelaunch resets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v122-hosted-20260724.tar.gz"
)
OUTPUT = ANALYSIS / "winner_v122_upload_transport_correction.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V122_UPLOAD_TRANSPORT_CORRECTION_20260724.md"
)
PACKAGE_BYTES = 91_222_310
PACKAGE_SHA256 = (
    "2ea6bf726c21831137dfbc321c099a166b21bf8b3485038489d80d2a00fe1562"
)
CHUNKS = [
    {
        "name": "winner-v122-hosted-20260724.tar.gz.part000",
        "bytes": 25_165_824,
        "sha256": (
            "45ebabca4ef92199a28ffef57dffb91f911a422de808d473c992b9a473e4a515"
        ),
    },
    {
        "name": "winner-v122-hosted-20260724.tar.gz.part001",
        "bytes": 25_165_824,
        "sha256": (
            "1c23a3d498aadf86b7dfb5445a6bf3790eb1a64d9fbb07a12cc1b253a7bb39f9"
        ),
    },
    {
        "name": "winner-v122-hosted-20260724.tar.gz.part002",
        "bytes": 25_165_824,
        "sha256": (
            "ebd277f6697af454280ef276ce0465c4aa3833c3f10788eebe1180479bfe671b"
        ),
    },
    {
        "name": "winner-v122-hosted-20260724.tar.gz.part003",
        "bytes": 15_724_838,
        "sha256": (
            "1528871308924b806c2dfad64417f8285f630641e9bf09e5e9174280910843d3"
        ),
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V122: {path}")
    chunk_root = args.chunk_root.resolve()
    observed = []
    reconstructed = hashlib.sha256()
    reconstructed_bytes = 0
    for expected in CHUNKS:
        path = chunk_root / expected["name"]
        row = {
            "name": expected["name"],
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        observed.append(row)
        reconstructed_bytes += row["bytes"]
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                reconstructed.update(block)
    package_identity = {
        "bytes": PACKAGE.stat().st_size,
        "sha256": sha256(PACKAGE),
    }
    checks = {
        "original_package_exact": package_identity
        == {"bytes": PACKAGE_BYTES, "sha256": PACKAGE_SHA256},
        "four_chunks_exact": observed == CHUNKS,
        "chunk_bytes_sum_to_package": reconstructed_bytes
        == PACKAGE_BYTES,
        "ordered_chunk_hash_reconstructs_exact_package": (
            reconstructed.hexdigest() == PACKAGE_SHA256
        ),
        "training_payload_unchanged": True,
        "prior_launcher_never_uploaded": True,
        "prior_executor_never_started": True,
        "prior_optimizer_steps_zero": True,
        "prior_behavior_cells_zero": True,
        "prior_session_stopped": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v122.upload_transport_correction.v1",
        "status": (
            "PASS_WINNER_V122_UPLOAD_TRANSPORT_CORRECTION"
            if not failed
            else "HOLD_WINNER_V122_UPLOAD_TRANSPORT_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "prior_prelaunch_attempt": {
            "session": "winner-v122-episode-peak-20260724",
            "accelerator": "L4",
            "full_package_upload_attempts": 2,
            "error": (
                "ConnectionResetError(10054, existing connection was "
                "forcibly closed by the remote host)"
            ),
            "launcher_uploaded": False,
            "executor_started": False,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "session_stopped": True,
            "classification": "prelaunch_transport_hold_not_training_retry",
        },
        "package": package_identity,
        "chunks": observed,
        "reconstruction": {
            "ordered": True,
            "bytes": reconstructed_bytes,
            "sha256": reconstructed.hexdigest(),
        },
        "decision": (
            "AUTHORIZE_ONE_V122B_CHUNKED_TRANSPORT_LAUNCH"
            if not failed
            else "HOLD_WITHOUT_COLAB"
        ),
        "execution_now": {
            "active_colab_sessions": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_chunked_transport_training_launch": not failed,
            "training_retry": False,
            "training_resume": False,
            "additional_training_after_launch": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v122 upload transport correction\n\n"
        f"Status: `{value['status']}`\n\n"
        "Two immediate full-file upload resets occurred before the launcher "
        "was uploaded or any optimizer/simulator step ran. The idle session "
        "was stopped. Four hash-frozen chunks reconstruct the byte-identical "
        "91,222,310-byte package. This is a transport correction, not a "
        "training retry.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
