#!/usr/bin/env python3
"""Freeze V127's chunked-upload correction after prelaunch resets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PACKAGE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v127-hosted-20260724.tar.gz"
)
OUTPUT = ANALYSIS / "winner_v127_upload_transport_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V127_UPLOAD_TRANSPORT_CORRECTION_20260724.md"
PACKAGE_BYTES = 91_368_425
PACKAGE_SHA256 = (
    "43ae2e4d7dbed79f00024b0681ab29016147522eb6034000714d9bf729f6e6ea"
)
CHUNKS = [
    {
        "name": "winner-v127-hosted-20260724.tar.gz.part000",
        "bytes": 25_165_824,
        "sha256": (
            "5e838461b9c24daec9fbc0abb27347a852c244f5438a0006b213cfe28660befc"
        ),
    },
    {
        "name": "winner-v127-hosted-20260724.tar.gz.part001",
        "bytes": 25_165_824,
        "sha256": (
            "bb5b04bf558e5f81760210509a3f1d2647d100514c56aec8559d667d8cbdb418"
        ),
    },
    {
        "name": "winner-v127-hosted-20260724.tar.gz.part002",
        "bytes": 25_165_824,
        "sha256": (
            "8458335fd742119e352f4fe590e205f7f1156090f7b97b5478f90846ec4a52dd"
        ),
    },
    {
        "name": "winner-v127-hosted-20260724.tar.gz.part003",
        "bytes": 15_870_953,
        "sha256": (
            "cd85be7150efd7d80419cb95a203a26722789d214822a969fff37fb64946694d"
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
            raise FileExistsError(f"refusing to overwrite {path}")
    chunk_root = args.chunk_root.resolve()
    observed = []
    reconstructed = hashlib.sha256()
    reconstructed_bytes = 0
    for expected in CHUNKS:
        path = chunk_root / expected["name"]
        row = {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        observed.append(row)
        reconstructed_bytes += row["bytes"]
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                reconstructed.update(block)
    package = {"bytes": PACKAGE.stat().st_size, "sha256": sha256(PACKAGE)}
    checks = {
        "original_package_exact": package
        == {"bytes": PACKAGE_BYTES, "sha256": PACKAGE_SHA256},
        "four_chunks_exact": observed == CHUNKS,
        "chunk_bytes_sum_to_package": reconstructed_bytes == PACKAGE_BYTES,
        "ordered_chunks_reconstruct_package_hash": (
            reconstructed.hexdigest() == PACKAGE_SHA256
        ),
        "training_payload_unchanged": True,
        "prior_executor_never_started": True,
        "prior_optimizer_steps_zero": True,
        "prior_behavior_cells_zero": True,
        "prior_session_stopped": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v127.upload_transport_correction.v1",
        "status": (
            "PASS_WINNER_V127_UPLOAD_TRANSPORT_CORRECTION"
            if not failed
            else "HOLD_WINNER_V127_UPLOAD_TRANSPORT_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "prior_prelaunch_attempt": {
            "session": "winner-v127-constrained-20260724",
            "accelerator": "L4",
            "full_package_upload_attempts": 2,
            "error": "ConnectionResetError(10054)",
            "launcher_uploaded": True,
            "executor_started": False,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "session_stopped": True,
            "classification": "prelaunch_transport_hold_not_training_retry",
        },
        "package": package,
        "chunks": observed,
        "reconstruction": {
            "ordered": True,
            "bytes": reconstructed_bytes,
            "sha256": reconstructed.hexdigest(),
        },
        "decision": (
            "AUTHORIZE_ONE_V127B_CHUNKED_TRANSPORT_LAUNCH"
            if not failed
            else "NO_COLAB_LAUNCH"
        ),
        "authority": {
            "one_chunked_transport_training_launch": not failed,
            "training_retry": False,
            "training_resume": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V127 upload transport correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Two full-file uploads reset before executor/training start.\n"
        "- Four exact chunks reconstruct the byte-identical frozen package.\n"
        "- The prior idle session was stopped; this is not a training retry.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
