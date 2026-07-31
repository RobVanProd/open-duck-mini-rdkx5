#!/usr/bin/env python3
"""Execute the frozen Winner-v119 launcher inside one Colab L4 session."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path("/content/winner-v119-hosted-20260724.tar.gz")
LAUNCHER = Path("/content/launch_winner_v119_transition_colab.py")
PACKAGE_BYTES = 75_205_640
PACKAGE_SHA256 = (
    "c3a6372ed3dbf908d061606a22948df4321ed5dae4937be14efda46c1f8b06f7"
)
LAUNCHER_SHA256 = (
    "38fa509a29d20836d40d3e11e0158383e2b143a60dae6563f7a89fbbffe635bb"
)


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
        raise RuntimeError(f"Winner-v119 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        Path("/content/winner_v119_work"),
        Path("/content/winner_v119_launch"),
        Path("/content/winner_v119_result.json"),
        Path("/content/winner_v119_artifacts.tar.gz"),
        Path("/content/winner_v119_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"Winner-v119 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
        or sha256(LAUNCHER) != LAUNCHER_SHA256
    ):
        raise ValueError("Winner-v119 uploaded launch inputs changed")
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
            f"Winner-v119 frozen launcher returned {completed.returncode}"
        )
    for name in (
        "winner_v119_result.json",
        "winner_v119_artifacts.tar.gz",
        "winner_v119_launch_receipt.json",
    ):
        path = Path("/content") / name
        if not path.is_file():
            raise FileNotFoundError(path)
        print(name, path.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
