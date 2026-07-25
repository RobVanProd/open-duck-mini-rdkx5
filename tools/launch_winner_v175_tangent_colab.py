#!/usr/bin/env python3
"""Verify, install, and launch the one V175 Colab continuation."""

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
    "8f9b1d8246ff16678478bc64c08af627122fe2dc29958f6e8cc189552f04ff2f"
)
PACKAGE_BYTES = 100_025_492
PREREGISTRATION_SHA256 = (
    "a6f2bd5377a2e9dd5659755a203c8900b548797ad8ca7b1455428dda41a226bc"
)
CPU_PREREGISTRATION_SHA256 = (
    "2db3c53abd91b516672c3883a6ce5ab8b072b798cc19a226684ff14cd418a25b"
)
CPU_RESULT_SHA256 = (
    "504ba613a135bab3f7be47605936d6065fc08d60d9adb74ff6d55aba7eae3411"
)
NOMINAL_RESULT_SHA256 = (
    "ef568b1fd59399926dea459f7e13db792292837cce9cf4fa67ac6dcb2104e4ed"
)
PACKAGE_MANIFEST_SHA256 = (
    "3d2b2bd0f053a81a5d3397ed3e0c1d9b0e0861da6844ebddb211fea9b7c96ea0"
)
DRIVER_SHA256 = (
    "2995ea5c0a34dede2fb4e6e5101b0aec5986d5d947d76637cffaaf978ad79b60"
)
BUNDLE_NAME = "winner_v175_tangent_bundle"
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
        "--work-root", type=Path, default=Path("/content/winner_v175_work")
    )
    parser.add_argument(
        "--extract-root",
        type=Path,
        default=Path("/content/winner_v175_launch"),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("/content/winner_v175_result.json"),
    )
    parser.add_argument(
        "--output-archive",
        type=Path,
        default=Path("/content/winner_v175_artifacts.tar.gz"),
    )
    parser.add_argument(
        "--launch-receipt",
        type=Path,
        default=Path("/content/winner_v175_launch_receipt.json"),
    )
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("V175 requires hosted GPU authorization")
    package = args.package.resolve()
    for path in (
        args.work_root,
        args.extract_root,
        args.output_json,
        args.output_archive,
        args.launch_receipt,
    ):
        if path.exists():
            raise FileExistsError(f"V175 no-retry path exists: {path}")
    if (
        package.stat().st_size != PACKAGE_BYTES
        or sha256(package) != PACKAGE_SHA256
    ):
        raise ValueError("V175 uploaded package changed")

    gpu = subprocess.run(
        ["nvidia-smi", "-L"], capture_output=True, text=True, check=False
    )
    if gpu.returncode != 0 or "L4" not in gpu.stdout:
        raise RuntimeError(f"V175 requires L4: {gpu.stdout}{gpu.stderr}")
    args.extract_root.mkdir(parents=True)
    with tarfile.open(package, "r:gz") as archive:
        archive.extractall(args.extract_root, filter="data")
    bundle = args.extract_root / BUNDLE_NAME
    prereg = bundle / "winner_v175_hosted_preregistration.json"
    cpu_prereg = (
        bundle
        / "winner_v173_lexicographic_tangent_cpu_preregistration.json"
    )
    cpu_result = (
        bundle / "winner_v173_lexicographic_tangent_cpu_result.json"
    )
    nominal_result = bundle / "winner_v174_tangent_nominal_result.json"
    manifest = bundle / "winner_v175_package_manifest.json"
    driver = bundle / "colab_winner_v175_tangent_continuation.py"
    if (
        sha256(prereg) != PREREGISTRATION_SHA256
        or sha256(cpu_prereg) != CPU_PREREGISTRATION_SHA256
        or sha256(cpu_result) != CPU_RESULT_SHA256
        or sha256(nominal_result) != NOMINAL_RESULT_SHA256
        or sha256(manifest) != PACKAGE_MANIFEST_SHA256
        or sha256(driver) != DRIVER_SHA256
    ):
        raise ValueError("V175 extracted package identity changed")

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
        raise RuntimeError(f"V175 pinned install failed: {completed.returncode}")
    observed_versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if observed_versions != EXPECTED_VERSIONS:
        raise ValueError(f"V175 software versions changed: {observed_versions}")
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
                "winner_v127_constrained_ppo_train, "
                "winner_v173_lexicographic_tangent; "
                "print('PASS_WINNER_V175_HOSTED_IMPORT')"
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
        or "PASS_WINNER_V175_HOSTED_IMPORT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"V175 hosted import failed: {preflight.stdout}\n"
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
        "schema_version": "winner_v175.colab_launch_receipt.v1",
        "status": "STARTING_WINNER_V175_HASH_FROZEN_GPU_CONTINUATION",
        "gpu": gpu.stdout.strip(),
        "package": {"bytes": PACKAGE_BYTES, "sha256": PACKAGE_SHA256},
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "cpu_preregistration_sha256": CPU_PREREGISTRATION_SHA256,
        "cpu_result_sha256": CPU_RESULT_SHA256,
        "nominal_result_sha256": NOMINAL_RESULT_SHA256,
        "package_manifest_sha256": PACKAGE_MANIFEST_SHA256,
        "driver_sha256": DRIVER_SHA256,
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
        "COMPLETED_WINNER_V175_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_WINNER_V175_COLAB_LAUNCH"
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
