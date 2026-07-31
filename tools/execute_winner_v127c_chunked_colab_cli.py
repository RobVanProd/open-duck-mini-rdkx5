#!/usr/bin/env python3
"""Reconstruct exact V127c chunks and run the cwd-corrected launcher."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path("/content/winner-v127c-hosted-20260724.tar.gz")
LAUNCHER = Path("/content/launch_winner_v127_constrained_colab.py")
PACKAGE_BYTES = 91_369_273
PACKAGE_SHA256 = (
    "27806832880000d19cb8b5e45c08e3aa50882c13cda4b2421fd7eb81ee6f2355"
)
LAUNCHER_SHA256 = (
    "7ca603aa38fee072204d2e18036c3b3f742001a3d1db265be1c089aedd0b29fa"
)
CHUNKS = [
    (
        "winner-v127c-hosted-20260724.tar.gz.part000",
        25_165_824,
        "e2f1ffc99f4dd8a55feceadb3571423a58743c22b2ccdbf9335984b720e38a06",
    ),
    (
        "winner-v127c-hosted-20260724.tar.gz.part001",
        25_165_824,
        "76597afc4b12f5677ec36120fc117891cfb3a0539e02c737c4a315d7a486d3c1",
    ),
    (
        "winner-v127c-hosted-20260724.tar.gz.part002",
        25_165_824,
        "921249498a211f160b8f78f3f4a58e07441d9ade3110e0a198d62cfdf090be15",
    ),
    (
        "winner-v127c-hosted-20260724.tar.gz.part003",
        15_871_801,
        "e20a20a202d6aa4208fde51a3e6bfac30972eee48dafb301d5a3fdec0b6750b3",
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
        raise RuntimeError(f"V127c requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        PACKAGE,
        Path("/content/winner_v127_work"),
        Path("/content/winner_v127_launch"),
        Path("/content/winner_v127_result.json"),
        Path("/content/winner_v127_artifacts.tar.gz"),
        Path("/content/winner_v127_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"V127c no-retry path exists: {path}")
    chunks = []
    for name, expected_bytes, expected_hash in CHUNKS:
        path = Path("/content") / name
        if (
            not path.is_file()
            or path.stat().st_size != expected_bytes
            or sha256(path) != expected_hash
        ):
            raise ValueError(f"V127c upload chunk changed: {name}")
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
        raise ValueError("V127c reconstructed launch inputs changed")
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
            f"V127c frozen launcher returned {completed.returncode}"
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
