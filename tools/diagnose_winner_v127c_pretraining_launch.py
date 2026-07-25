#!/usr/bin/env python3
"""Read-only diagnosis of the V127c launcher before driver execution."""

from __future__ import annotations

import hashlib
import importlib.metadata
import os
from pathlib import Path
import subprocess
import sys


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
    print("bundle_exists", bundle.is_dir())
    for name, expected in EXPECTED.items():
        path = bundle / name
        observed = sha256(path) if path.is_file() else "MISSING"
        print(name, observed, observed == expected)
    for package in (
        "brax",
        "flax",
        "jax",
        "jaxlib",
        "mujoco",
        "mujoco-mjx",
        "numpy",
        "onnx",
        "onnxruntime",
        "optax",
        "orbax-checkpoint",
        "playground",
    ):
        print("version", package, importlib.metadata.version(package))
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "playground")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from playground.open_duck_mini_v2.joystick import "
                "winner_v127_dense_torque_exceedance_cost; "
                "from playground.common import "
                "winner_v127_constrained_ppo_train; "
                "print('PASS_WINNER_V127_HOSTED_IMPORT')"
            ),
        ],
        cwd=bundle,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    print("preflight_returncode", result.returncode)
    print("preflight_stdout", result.stdout)
    print("preflight_stderr", result.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
