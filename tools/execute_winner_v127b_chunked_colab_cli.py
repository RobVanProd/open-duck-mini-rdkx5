#!/usr/bin/env python3
"""Reconstruct exact V127 package chunks and run the frozen launcher."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path("/content/winner-v127-hosted-20260724.tar.gz")
LAUNCHER = Path("/content/launch_winner_v127_constrained_colab.py")
PACKAGE_BYTES = 91_368_425
PACKAGE_SHA256 = (
    "43ae2e4d7dbed79f00024b0681ab29016147522eb6034000714d9bf729f6e6ea"
)
LAUNCHER_SHA256 = (
    "7947aa8798d415e257a143cdfc3a25addc8b068985e06758727c918edad9cfbf"
)
CHUNKS = [
    (
        "winner-v127-hosted-20260724.tar.gz.part000",
        25_165_824,
        "5e838461b9c24daec9fbc0abb27347a852c244f5438a0006b213cfe28660befc",
    ),
    (
        "winner-v127-hosted-20260724.tar.gz.part001",
        25_165_824,
        "bb5b04bf558e5f81760210509a3f1d2647d100514c56aec8559d667d8cbdb418",
    ),
    (
        "winner-v127-hosted-20260724.tar.gz.part002",
        25_165_824,
        "8458335fd742119e352f4fe590e205f7f1156090f7b97b5478f90846ec4a52dd",
    ),
    (
        "winner-v127-hosted-20260724.tar.gz.part003",
        15_870_953,
        "cd85be7150efd7d80419cb95a203a26722789d214822a969fff37fb64946694d",
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
        raise RuntimeError(f"V127b requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        PACKAGE,
        Path("/content/winner_v127_work"),
        Path("/content/winner_v127_launch"),
        Path("/content/winner_v127_result.json"),
        Path("/content/winner_v127_artifacts.tar.gz"),
        Path("/content/winner_v127_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"V127b no-retry path exists: {path}")
    chunk_paths = []
    for name, expected_bytes, expected_hash in CHUNKS:
        path = Path("/content") / name
        if (
            not path.is_file()
            or path.stat().st_size != expected_bytes
            or sha256(path) != expected_hash
        ):
            raise ValueError(f"V127 upload chunk changed: {name}")
        chunk_paths.append(path)
    temporary = PACKAGE.with_suffix(PACKAGE.suffix + ".tmp")
    with temporary.open("wb") as destination:
        for path in chunk_paths:
            with path.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    destination.write(block)
    temporary.replace(PACKAGE)
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
        or sha256(LAUNCHER) != LAUNCHER_SHA256
    ):
        raise ValueError("V127 reconstructed launch inputs changed")
    print(gpu.stdout.strip())
    command = [
        sys.executable,
        str(LAUNCHER),
        "--package",
        str(PACKAGE),
        "--hosted-gpu-authorized",
    ]
    completed = subprocess.run(command, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"V127 frozen launcher returned {completed.returncode}"
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
