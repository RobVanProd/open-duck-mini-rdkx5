#!/usr/bin/env python3
"""Verify, install, and launch the one V127 Colab continuation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile


PACKAGE_SHA256 = (
    "27806832880000d19cb8b5e45c08e3aa50882c13cda4b2421fd7eb81ee6f2355"
)
PACKAGE_BYTES = 91_369_273
PREREGISTRATION_SHA256 = (
    "a4ff39895c251fb2951ff6f67ca33d488c34bb7f6be56b1cf3a979e94373f370"
)
CPU_RESULT_SHA256 = (
    "cd728eb3cf2900f038c4134e3f603106238e960046b3482d4cd2b695b5a76ed4"
)
CPU_PREREGISTRATION_SHA256 = (
    "a77c677816714a0517c70f84c56d8c6a2b731ae135696c11b15ff51caf24bc34"
)
PACKAGE_MANIFEST_SHA256 = (
    "f16a6046addb4e7458e28f2ade9390ce1354c3a8b59ae7e858d39b4b10333c65"
)
DRIVER_SHA256 = (
    "c12799e46b6f44382d4c9f1e3cd681452bf134a5bb691426b0bfb73973fdabc2"
)
CORRECTION_SHA256 = (
    "3ed76e4cda5bbfb45a2ac9d3696ca0b0f43b6a69782614f1af7be544f9aab497"
)
BUNDLE_NAME = "winner_v127c_constrained_bundle"
EXPECTED_VERSIONS = {
    "brax": "0.14.2",
    "flax": "0.11.2",
    "jax": "0.7.2",
    "jaxlib": "0.7.2",
    "mujoco": "3.9.0",
    "mujoco-mjx": "3.9.0",
    "numpy": "2.0.2",
    "onnx": "1.22.0",
    "onnxruntime": "1.27.0",
    "optax": "0.2.5",
    "orbax-checkpoint": "0.11.25",
    "playground": "0.0.3",
}
INSTALL_REQUIREMENTS = (
    "numpy==2.0.2",
    "jax[cuda12]==0.7.2",
    "jaxlib==0.7.2",
    "brax==0.14.2",
    "flax==0.11.2",
    "optax==0.2.5",
    "orbax-checkpoint==0.11.25",
    "mujoco==3.9.0",
    "mujoco-mjx==3.9.0",
    "onnx==1.22.0",
    "onnxruntime==1.27.0",
    "playground==0.0.3",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument(
        "--work-root", type=Path, default=Path("/content/winner_v127_work")
    )
    parser.add_argument(
        "--extract-root",
        type=Path,
        default=Path("/content/winner_v127_launch"),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("/content/winner_v127_result.json"),
    )
    parser.add_argument(
        "--output-archive",
        type=Path,
        default=Path("/content/winner_v127_artifacts.tar.gz"),
    )
    parser.add_argument(
        "--launch-receipt",
        type=Path,
        default=Path("/content/winner_v127_launch_receipt.json"),
    )
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("V127 requires hosted GPU authorization")
    package = args.package.resolve()
    for path in (
        args.work_root,
        args.extract_root,
        args.output_json,
        args.output_archive,
        args.launch_receipt,
    ):
        if path.exists():
            raise FileExistsError(f"V127 no-retry path exists: {path}")
    if (
        package.stat().st_size != PACKAGE_BYTES
        or sha256(package) != PACKAGE_SHA256
    ):
        raise ValueError("V127 uploaded package changed")

    args.extract_root.mkdir(parents=True)
    with tarfile.open(package, "r:gz") as archive:
        archive.extractall(args.extract_root, filter="data")
    bundle = args.extract_root / BUNDLE_NAME
    prereg = bundle / "winner_v127c_hosted_preregistration.json"
    cpu_result = bundle / "winner_v127_constrained_cpu_result.json"
    cpu_prereg = (
        bundle / "winner_v127_constrained_cpu_preregistration.json"
    )
    manifest = bundle / "winner_v127_package_manifest.json"
    driver = bundle / "colab_winner_v127_constrained_continuation.py"
    correction = bundle / "winner_v127_pretraining_launch_correction.json"
    if (
        sha256(prereg) != PREREGISTRATION_SHA256
        or sha256(cpu_result) != CPU_RESULT_SHA256
        or sha256(cpu_prereg) != CPU_PREREGISTRATION_SHA256
        or sha256(manifest) != PACKAGE_MANIFEST_SHA256
        or sha256(driver) != DRIVER_SHA256
        or sha256(correction) != CORRECTION_SHA256
    ):
        raise ValueError("V127 extracted package identity changed")

    install = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--quiet",
        "--upgrade",
        *INSTALL_REQUIREMENTS,
    ]
    completed = subprocess.run(install, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"V127 pinned install failed: {completed.returncode}")
    observed_versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if observed_versions != EXPECTED_VERSIONS:
        raise ValueError(f"V127 software versions changed: {observed_versions}")
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "playground")
    preflight = subprocess.run(
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
        timeout=120,
    )
    if (
        preflight.returncode != 0
        or "PASS_WINNER_V127_HOSTED_IMPORT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"V127 hosted import failed: {preflight.stdout}\n"
            f"{preflight.stderr}"
        )
    command = [
        sys.executable,
        str(driver),
        "--bundle-root",
        str(bundle),
        "--work-root",
        str(args.work_root),
        "--output-json",
        str(args.output_json),
        "--output-archive",
        str(args.output_archive),
        "--hosted-gpu-authorized",
    ]
    receipt = {
        "schema_version": "winner_v127.colab_launch_receipt.v1",
        "status": "STARTING_WINNER_V127_HASH_FROZEN_GPU_CONTINUATION",
        "package": {"bytes": PACKAGE_BYTES, "sha256": PACKAGE_SHA256},
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "cpu_result_sha256": CPU_RESULT_SHA256,
        "cpu_preregistration_sha256": CPU_PREREGISTRATION_SHA256,
        "package_manifest_sha256": PACKAGE_MANIFEST_SHA256,
        "driver_sha256": DRIVER_SHA256,
        "pretraining_launch_correction_sha256": CORRECTION_SHA256,
        "software_versions": observed_versions,
        "command": command,
        "retry": False,
        "resume": False,
        "robot_or_rdk_access": False,
    }
    args.launch_receipt.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(command, text=True, check=False)
    receipt["returncode"] = result.returncode
    receipt["status"] = (
        "COMPLETED_WINNER_V127_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_WINNER_V127_COLAB_LAUNCH"
    )
    for label, path in (
        ("output_json", args.output_json),
        ("output_archive", args.output_archive),
    ):
        receipt[f"{label}_exists"] = path.is_file()
        if path.is_file():
            receipt[f"{label}_sha256"] = sha256(path)
    args.launch_receipt.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
