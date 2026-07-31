#!/usr/bin/env python3
"""Execute the frozen Winner-v112 launcher inside one Colab L4 session."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path("/content/winner-v112-peak-torque-hosted-20260724.tar.gz")
LAUNCHER = Path("/content/launch_winner_v112_peak_torque_colab.py")
PACKAGE_BYTES = 51_971_655
PACKAGE_SHA256 = (
    "f39bea69840436b5ca8cc2a3000b6006ceaac1fa403588c94024e6caa5709401"
)
LAUNCHER_SHA256 = (
    "6f4a1715b29bbf714de2ac48769702fe22f9b837e33ad5e6af6940b0824dc988"
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
        raise RuntimeError(f"Winner-v112 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        Path("/content/winner_v112_work"),
        Path("/content/winner_v112_launch"),
        Path("/content/winner_v112_result.json"),
        Path("/content/winner_v112_artifacts.tar.gz"),
        Path("/content/winner_v112_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"Winner-v112 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
        or sha256(LAUNCHER) != LAUNCHER_SHA256
    ):
        raise ValueError("Winner-v112 uploaded launch inputs changed")
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
            f"Winner-v112 frozen launcher returned {completed.returncode}"
        )
    for name in (
        "winner_v112_result.json",
        "winner_v112_artifacts.tar.gz",
        "winner_v112_launch_receipt.json",
    ):
        path = Path("/content") / name
        if not path.is_file():
            raise FileNotFoundError(path)
        print(name, path.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
