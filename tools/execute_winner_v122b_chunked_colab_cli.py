#!/usr/bin/env python3
"""Reconstruct and execute the frozen V122 launcher in one Colab L4."""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
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
CHUNKS = [
    (
        Path("/content/winner-v122-hosted-20260724.tar.gz.part000"),
        25_165_824,
        "45ebabca4ef92199a28ffef57dffb91f911a422de808d473c992b9a473e4a515",
    ),
    (
        Path("/content/winner-v122-hosted-20260724.tar.gz.part001"),
        25_165_824,
        "1c23a3d498aadf86b7dfb5445a6bf3790eb1a64d9fbb07a12cc1b253a7bb39f9",
    ),
    (
        Path("/content/winner-v122-hosted-20260724.tar.gz.part002"),
        25_165_824,
        "ebd277f6697af454280ef276ce0465c4aa3833c3f10788eebe1180479bfe671b",
    ),
    (
        Path("/content/winner-v122-hosted-20260724.tar.gz.part003"),
        15_724_838,
        "1528871308924b806c2dfad64417f8285f630641e9bf09e5e9174280910843d3",
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
        raise RuntimeError(f"Winner-v122 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (
        PACKAGE,
        Path("/content/winner_v122_work"),
        Path("/content/winner_v122_launch"),
        Path("/content/winner_v122_result.json"),
        Path("/content/winner_v122_artifacts.tar.gz"),
        Path("/content/winner_v122_launch_receipt.json"),
    ):
        if path.exists():
            raise FileExistsError(f"Winner-v122 no-retry path exists: {path}")
    for path, expected_bytes, expected_sha in CHUNKS:
        if (
            path.stat().st_size != expected_bytes
            or sha256(path) != expected_sha
        ):
            raise ValueError(f"Winner-v122 upload chunk changed: {path.name}")
    with PACKAGE.open("xb") as output:
        for path, _expected_bytes, _expected_sha in CHUNKS:
            with path.open("rb") as stream:
                shutil.copyfileobj(stream, output)
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
        or sha256(LAUNCHER) != LAUNCHER_SHA256
    ):
        raise ValueError("Winner-v122 reconstructed launch inputs changed")
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
