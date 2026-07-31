#!/usr/bin/env python3
"""Execute the frozen Winner-v114 launcher inside one Colab L4 session."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path(
    "/content/winner-v114-linear-torque-hosted-20260724.tar.gz"
)
LAUNCHER = Path("/content/launch_winner_v114_linear_torque_colab.py")
PACKAGE_BYTES = 64_522_613
PACKAGE_SHA256 = (
    "3f64c637f4395f7b131da6d252b4d3001aff62d65c23015f5708b6b059f4ddd5"
)
LAUNCHER_SHA256 = (
    "f5e0e5a13c4d7b8d6f455bd40caddcc8b40f9afa4e9db0f296bdb74d63ac2101"
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
        raise RuntimeError(f"Winner-v114 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        Path("/content/winner_v114_work"),
        Path("/content/winner_v114_launch"),
        Path("/content/winner_v114_result.json"),
        Path("/content/winner_v114_artifacts.tar.gz"),
        Path("/content/winner_v114_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"Winner-v114 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
        or sha256(LAUNCHER) != LAUNCHER_SHA256
    ):
        raise ValueError("Winner-v114 uploaded launch inputs changed")
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
            f"Winner-v114 frozen launcher returned {completed.returncode}"
        )
    for name in (
        "winner_v114_result.json",
        "winner_v114_artifacts.tar.gz",
        "winner_v114_launch_receipt.json",
    ):
        path = Path("/content") / name
        if not path.is_file():
            raise FileNotFoundError(path)
        print(name, path.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
