#!/usr/bin/env python3
"""Reconstruct exact V127d chunks and run the root-corrected launcher."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path("/content/winner-v127d-hosted-20260724.tar.gz")
LAUNCHER = Path("/content/launch_winner_v127_constrained_colab.py")
PACKAGE_BYTES = 91_370_527
PACKAGE_SHA256 = (
    "605ec08c135cfe5abf75e08814cf337fc6ee0e83e96c752a60b259367f25555c"
)
LAUNCHER_SHA256 = (
    "79335fcec084a5332fb9ed1e51177befbf865ec2da5d7ddaea022343b3d22534"
)
CHUNKS = [
    (
        "winner-v127d-hosted-20260724.tar.gz.part000",
        25_165_824,
        "46af71c2506746ccfbcf9abc8e08b26bd453d7f64b71c39c2788e939210fea8e",
    ),
    (
        "winner-v127d-hosted-20260724.tar.gz.part001",
        25_165_824,
        "435c7ed195971edb47bdd3635d496aca0ed66f702e8d38f1226de27bfff0ed19",
    ),
    (
        "winner-v127d-hosted-20260724.tar.gz.part002",
        25_165_824,
        "fdc48cebc75d01d7763aa52e038196a43454136296da8ebc061cd33b4a17251b",
    ),
    (
        "winner-v127d-hosted-20260724.tar.gz.part003",
        15_873_055,
        "c65ef0742d21cf33801df903aaa53745b4b5a57a68fef0ddd1705d49fa7c6e1f",
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    gpu = subprocess.run(
        ["nvidia-smi", "-L"], capture_output=True, text=True, check=False
    )
    if gpu.returncode != 0 or "L4" not in gpu.stdout:
        raise RuntimeError(f"V127d requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        PACKAGE,
        Path("/content/winner_v127_work"),
        Path("/content/winner_v127_launch"),
        Path("/content/winner_v127_result.json"),
        Path("/content/winner_v127_artifacts.tar.gz"),
        Path("/content/winner_v127_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"V127d no-retry path exists: {path}")
    chunks = []
    for name, expected_bytes, expected_hash in CHUNKS:
        path = Path("/content") / name
        if (
            not path.is_file()
            or path.stat().st_size != expected_bytes
            or sha256(path) != expected_hash
        ):
            raise ValueError(f"V127d upload chunk changed: {name}")
        chunks.append(path)
    temporary = PACKAGE.with_suffix(PACKAGE.suffix + ".tmp")
    with temporary.open("wb") as destination:
        for path in chunks:
            with path.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    destination.write(block)
    temporary.replace(PACKAGE)
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
        or sha256(LAUNCHER) != LAUNCHER_SHA256
    ):
        raise ValueError("V127d reconstructed launch inputs changed")
    print(gpu.stdout.strip())
    completed = subprocess.run(
        [
            sys.executable,
            str(LAUNCHER),
            "--package",
            str(PACKAGE),
            "--hosted-gpu-authorized",
        ],
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"V127d frozen launcher returned {completed.returncode}"
        )
    for name in (
        "winner_v127_result.json",
        "winner_v127_artifacts.tar.gz",
        "winner_v127_launch_receipt.json",
    ):
        path = Path("/content") / name
        if not path.is_file():
            raise FileNotFoundError(path)
        print(name, path.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
