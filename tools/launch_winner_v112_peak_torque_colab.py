#!/usr/bin/env python3
"""Verify, install, and launch the one Winner-v112 Colab continuation."""

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
    "f39bea69840436b5ca8cc2a3000b6006ceaac1fa403588c94024e6caa5709401"
)
PACKAGE_BYTES = 51_971_655
PREREGISTRATION_SHA256 = (
    "44feeb999de22ab7a4ad2438eeb1db27d1c2e683b0cee6f83030e78caa344817"
)
CPU_CORRECTION_SHA256 = (
    "f319f784f0a315b3b58e24080b40eb96e8f551dd1341cec5705e9ca7c38d4ba1"
)
PACKAGE_MANIFEST_SHA256 = (
    "4a664ee60591ae1e1be7f95fe1b859d75bf4b6b7153257bd8626cdf149e07554"
)
DRIVER_SHA256 = (
    "b21a8b335119062a8b8f387491d7aec38fee30c0ad1cdceef0d00576c517becf"
)
BUNDLE_NAME = "winner_v112_peak_torque_bundle"
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
        "--work-root", type=Path, default=Path("/content/winner_v112_work")
    )
    parser.add_argument(
        "--extract-root",
        type=Path,
        default=Path("/content/winner_v112_launch"),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("/content/winner_v112_result.json"),
    )
    parser.add_argument(
        "--output-archive",
        type=Path,
        default=Path("/content/winner_v112_artifacts.tar.gz"),
    )
    parser.add_argument(
        "--launch-receipt",
        type=Path,
        default=Path("/content/winner_v112_launch_receipt.json"),
    )
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("Winner-v112 requires hosted GPU authorization")
    package = args.package.resolve()
    for path in (
        args.work_root,
        args.extract_root,
        args.output_json,
        args.output_archive,
        args.launch_receipt,
    ):
        if path.exists():
            raise FileExistsError(f"Winner-v112 no-retry path exists: {path}")
    if (
        package.stat().st_size != PACKAGE_BYTES
        or sha256(package) != PACKAGE_SHA256
    ):
        raise ValueError("Winner-v112 uploaded package changed")

    args.extract_root.mkdir(parents=True)
    with tarfile.open(package, "r:gz") as archive:
        archive.extractall(args.extract_root, filter="data")
    bundle = args.extract_root / BUNDLE_NAME
    preregistration = (
        bundle / "winner_v112_peak_torque_hosted_preregistration.json"
    )
    correction = bundle / "winner_v111_peak_torque_cpu_correction.json"
    manifest = bundle / "winner_v112_package_manifest.json"
    driver = bundle / "colab_winner_v112_peak_torque_continuation.py"
    if (
        sha256(preregistration) != PREREGISTRATION_SHA256
        or sha256(correction) != CPU_CORRECTION_SHA256
        or sha256(manifest) != PACKAGE_MANIFEST_SHA256
        or sha256(driver) != DRIVER_SHA256
    ):
        raise ValueError("Winner-v112 extracted package identity changed")

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
        raise RuntimeError(
            f"Winner-v112 pinned install failed: {completed.returncode}"
        )
    observed_versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if observed_versions != EXPECTED_VERSIONS:
        raise ValueError(
            f"Winner-v112 software versions changed: {observed_versions}"
        )
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "playground")
    preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from playground.open_duck_mini_v2.joystick import "
                "ground_up_peak_torque_exceedance_cost; "
                "print('PASS_WINNER_V112_HOSTED_IMPORT')"
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
        or "PASS_WINNER_V112_HOSTED_IMPORT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            "Winner-v112 hosted import failed: "
            f"{preflight.stdout}\n{preflight.stderr}"
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
        "schema_version": "winner_v112.colab_launch_receipt.v1",
        "status": "STARTING_WINNER_V112_HASH_FROZEN_GPU_CONTINUATION",
        "package": {
            "bytes": PACKAGE_BYTES,
            "sha256": PACKAGE_SHA256,
        },
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "cpu_correction_sha256": CPU_CORRECTION_SHA256,
        "package_manifest_sha256": PACKAGE_MANIFEST_SHA256,
        "driver_sha256": DRIVER_SHA256,
        "hosted_import_preflight": "PASS_WINNER_V112_HOSTED_IMPORT",
        "software_versions": observed_versions,
        "command": command,
        "retry": False,
        "resume": False,
        "robot_or_rdk_access": False,
    }
    args.launch_receipt.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(command, text=True, check=False)
    receipt["returncode"] = result.returncode
    receipt["status"] = (
        "COMPLETED_WINNER_V112_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_WINNER_V112_COLAB_LAUNCH"
    )
    receipt["output_json_exists"] = args.output_json.is_file()
    receipt["output_archive_exists"] = args.output_archive.is_file()
    if args.output_json.is_file():
        receipt["output_json_sha256"] = sha256(args.output_json)
    if args.output_archive.is_file():
        receipt["output_archive_sha256"] = sha256(args.output_archive)
    args.launch_receipt.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
