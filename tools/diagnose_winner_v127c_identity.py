#!/usr/bin/env python3
"""Read-only identity check for the extracted V127c bundle."""

from __future__ import annotations

import hashlib
from pathlib import Path


EXPECTED = {
    "winner_v127c_hosted_preregistration.json": (
        "a4ff39895c251fb2951ff6f67ca33d488c34bb7f6be56b1cf3a979e94373f370"
    ),
    "winner_v127_constrained_cpu_result.json": (
        "cd728eb3cf2900f038c4134e3f603106238e960046b3482d4cd2b695b5a76ed4"
    ),
    "winner_v127_constrained_cpu_preregistration.json": (
        "a77c677816714a0517c70f84c56d8c6a2b731ae135696c11b15ff51caf24bc34"
    ),
    "winner_v127_pretraining_launch_correction.json": (
        "3ed76e4cda5bbfb45a2ac9d3696ca0b0f43b6a69782614f1af7be544f9aab497"
    ),
    "winner_v127_package_manifest.json": (
        "f16a6046addb4e7458e28f2ade9390ce1354c3a8b59ae7e858d39b4b10333c65"
    ),
    "colab_winner_v127_constrained_continuation.py": (
        "c12799e46b6f44382d4c9f1e3cd681452bf134a5bb691426b0bfb73973fdabc2"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    bundle = Path(
        "/content/winner_v127_launch/winner_v127c_constrained_bundle"
    )
    print("bundle", bundle.is_dir())
    for name, expected in EXPECTED.items():
        path = bundle / name
        observed = sha256(path) if path.is_file() else "MISSING"
        print(name, observed, observed == expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
