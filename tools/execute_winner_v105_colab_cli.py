#!/usr/bin/env python3
"""Execute the frozen Winner-v105 launcher inside one Colab L4 session."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path(
    "/content/winner-v105-response-conditioned-hosted-20260723.tar.gz"
)
LAUNCHER = Path("/content/launch_winner_v105_response_conditioned_colab.py")
PACKAGE_BYTES = 59_201_279
PACKAGE_SHA256 = "30db9b47433543eeeff6e4db6548cd6479916a803891d3aafacd1b63f105be70"
LAUNCHER_SHA256 = "292a1cc152d9d2762b26c5d490388f7c35d8b5514959bbc950cc76cf9e10e122"


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
        raise RuntimeError(f"Winner-v105 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        Path("/content/winner_v105_work"),
        Path("/content/winner_v105_launch"),
        Path("/content/winner_v105_result.json"),
        Path("/content/winner_v105_artifacts.tar.gz"),
        Path("/content/winner_v105_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"Winner-v105 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
        or sha256(LAUNCHER) != LAUNCHER_SHA256
    ):
        raise ValueError("Winner-v105 uploaded launch inputs changed")
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
            f"Winner-v105 frozen launcher returned {completed.returncode}"
        )
    for name in (
        "winner_v105_result.json",
        "winner_v105_artifacts.tar.gz",
        "winner_v105_launch_receipt.json",
    ):
        path = Path("/content") / name
        if not path.is_file():
            raise FileNotFoundError(path)
        print(name, path.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
