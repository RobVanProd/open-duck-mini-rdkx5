#!/usr/bin/env python3
"""Reconstruct and execute the exact V175 hosted package in Colab."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path("/content/winner-v175-hosted-20260725.tar.gz")
LAUNCHER = Path("/content/launch_winner_v175_tangent_colab.py")
PACKAGE_BYTES = 100_025_492
PACKAGE_SHA256 = (
    "8f9b1d8246ff16678478bc64c08af627122fe2dc29958f6e8cc189552f04ff2f"
)
LAUNCHER_SHA256 = (
    "df3dde041600031269d18c8f7dac69ae80075f68a32835aa5de460900cfc3145"
)
CHUNKS = [
    (
        "winner-v175-hosted-20260725.tar.gz.part000",
        25_165_824,
        "c5b5c12a19d156e4e45478291114f4a5e508f229b48179d10cbe7ab30cc26388",
    ),
    (
        "winner-v175-hosted-20260725.tar.gz.part001",
        25_165_824,
        "5314b6050ee975d3a6079621b14ba21d15ed180352f766ba89441ad1ae16ad0e",
    ),
    (
        "winner-v175-hosted-20260725.tar.gz.part002",
        25_165_824,
        "00c0386476e5023419869fcf67a0519519f5deb8cc51096839443c85c8d2bff8",
    ),
    (
        "winner-v175-hosted-20260725.tar.gz.part003",
        24_528_020,
        "7a08e657c70448d346dd9141bc274ac951def477c39a42e235b24c0b542e3930",
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
        raise RuntimeError(f"V175 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        PACKAGE,
        Path("/content/winner_v175_work"),
        Path("/content/winner_v175_launch"),
        Path("/content/winner_v175_result.json"),
        Path("/content/winner_v175_artifacts.tar.gz"),
        Path("/content/winner_v175_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"V175 no-retry path exists: {path}")
    chunks = []
    for name, expected_bytes, expected_hash in CHUNKS:
        path = Path("/content") / name
        if (
            not path.is_file()
            or path.stat().st_size != expected_bytes
            or sha256(path) != expected_hash
        ):
            raise ValueError(f"V175 upload chunk changed: {name}")
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
        raise ValueError("V175 reconstructed launch inputs changed")
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
            f"V175 frozen launcher returned {completed.returncode}"
        )
    for name in (
        "winner_v175_result.json",
        "winner_v175_artifacts.tar.gz",
        "winner_v175_launch_receipt.json",
    ):
        path = Path("/content") / name
        if not path.is_file():
            raise FileNotFoundError(path)
        print(name, path.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
