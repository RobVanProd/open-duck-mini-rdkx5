#!/usr/bin/env python3
"""Execute the frozen Winner-v122 launcher inside one Colab L4 session."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


PACKAGE = Path("/content/winner-v122-hosted-20260724.tar.gz")
LAUNCHER = Path("/content/launch_winner_v122_episode_peak_colab.py")
PACKAGE_BYTES = 91_222_310
PACKAGE_SHA256 = (
    "2ea6bf726c21831137dfbc321c099a166b21bf8b3485038489d80d2a00fe1562"
)
LAUNCHER_SHA256 = (
    "933871c0814ad0238b1a302aee9ae484a0ecd9ac60b2a8a5c3552739f33fb597"
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
        raise RuntimeError(f"Winner-v122 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        Path("/content/winner_v122_work"),
        Path("/content/winner_v122_launch"),
        Path("/content/winner_v122_result.json"),
        Path("/content/winner_v122_artifacts.tar.gz"),
        Path("/content/winner_v122_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"Winner-v122 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
        or sha256(LAUNCHER) != LAUNCHER_SHA256
    ):
        raise ValueError("Winner-v122 uploaded launch inputs changed")
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
            f"Winner-v122 frozen launcher returned {completed.returncode}"
        )
    for name in (
        "winner_v122_result.json",
        "winner_v122_artifacts.tar.gz",
        "winner_v122_launch_receipt.json",
    ):
        path = Path("/content") / name
        if not path.is_file():
            raise FileNotFoundError(path)
        print(name, path.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
