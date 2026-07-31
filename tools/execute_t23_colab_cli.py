#!/usr/bin/env python3
"""Execute the exact T23 bundle inside one Colab L4 session."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile


PACKAGE = Path("/content/t23-support-trainthrough-hosted-20260726.tar.gz")
PACKAGE_BYTES = 134_645_185
PACKAGE_SHA256 = (
    "2ba7612ef2984623f60abac0b4d41efdf18ae711f5f848003b4f125013d658e8"
)
BUNDLE_NAME = "t23_support_trainthrough_bundle"
PREREGISTRATION_SHA256 = (
    "3c716c93cb1806ffa5bfb342bc4a6ad2afc0215efcd75852d9acb6ac5f9c4578"
)
CPU_RESULT_SHA256 = (
    "5525dc271ccb543103462a38d9fd808c40d52ed61164edb8376dbe81bd6a3189"
)
PACKAGE_MANIFEST_SHA256 = (
    "05a1f221b4b674d585de57d7309e64d8240a3920e29530219835014912cbbfbb"
)
DRIVER_SHA256 = (
    "17d4be227e6073bc3208c2e193d53e902386a18671ace4eb37351accba684029"
)
DRIVER_HELPER_SHA256 = (
    "09bbe4ab7ee42d7f77bb302d7fa8cab15b8734be97f5db80f912ad6619dd808f"
)
WORK = Path("/content/t23_work")
EXTRACT = Path("/content/t23_launch")
OUTPUT_JSON = Path("/content/t23_result.json")
OUTPUT_ARCHIVE = Path("/content/t23_artifacts.tar.gz")
RECEIPT = Path("/content/t23_launch_receipt.json")
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
    gpu = subprocess.run(
        ["nvidia-smi", "-L"],
        capture_output=True,
        text=True,
        check=False,
    )
    if gpu.returncode != 0 or "L4" not in gpu.stdout:
        raise RuntimeError(f"T23 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (WORK, EXTRACT, OUTPUT_JSON, OUTPUT_ARCHIVE, RECEIPT):
        if path.exists():
            raise FileExistsError(f"T23 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
    ):
        raise ValueError("T23 uploaded package changed")

    EXTRACT.mkdir(parents=True)
    with tarfile.open(PACKAGE, "r:gz") as archive:
        archive.extractall(EXTRACT, filter="data")
    bundle = EXTRACT / BUNDLE_NAME
    preregistration = (
        bundle / "t23_support_trainthrough_hosted_preregistration.json"
    )
    cpu_result = bundle / "t22_corrected_one_update_cpu_result.json"
    manifest = bundle / "t23_package_manifest.json"
    driver = bundle / "colab_t23_support_trainthrough_continuation.py"
    helper = bundle / "colab_winner_v114_linear_torque_continuation.py"
    if (
        sha256(preregistration) != PREREGISTRATION_SHA256
        or sha256(cpu_result) != CPU_RESULT_SHA256
        or sha256(manifest) != PACKAGE_MANIFEST_SHA256
        or sha256(driver) != DRIVER_SHA256
        or sha256(helper) != DRIVER_HELPER_SHA256
    ):
        raise ValueError("T23 extracted package identity changed")

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
        raise RuntimeError(f"T23 pinned install failed: {completed.returncode}")
    observed_versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if observed_versions != EXPECTED_VERSIONS:
        raise ValueError(f"T23 software versions changed: {observed_versions}")

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "playground")
    preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from playground.common.t19_support_trainthrough import "
                "SupportPrefixWrapper, SOURCE_RATE_LIMITS_RAD_S; "
                "print('PASS_T23_HOSTED_IMPORT', "
                "len(SOURCE_RATE_LIMITS_RAD_S))"
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
        or "PASS_T23_HOSTED_IMPORT 14"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T23 hosted import failed: {preflight.stdout}\n"
            f"{preflight.stderr}"
        )
    command = [
        sys.executable,
        str(driver),
        "--bundle-root",
        str(bundle),
        "--work-root",
        str(WORK),
        "--output-json",
        str(OUTPUT_JSON),
        "--output-archive",
        str(OUTPUT_ARCHIVE),
        "--hosted-gpu-authorized",
    ]
    receipt = {
        "schema_version": "open_duck.t23_colab_launch_receipt.v1",
        "status": "STARTING_T23_HASH_FROZEN_GPU_CONTINUATION",
        "gpu": gpu.stdout.strip(),
        "package": {
            "bytes": PACKAGE_BYTES,
            "sha256": PACKAGE_SHA256,
        },
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "cpu_result_sha256": CPU_RESULT_SHA256,
        "package_manifest_sha256": PACKAGE_MANIFEST_SHA256,
        "driver_sha256": DRIVER_SHA256,
        "driver_helper_sha256": DRIVER_HELPER_SHA256,
        "hosted_import_preflight": "PASS_T23_HOSTED_IMPORT 14",
        "software_versions": observed_versions,
        "command": command,
        "retry": False,
        "resume": False,
        "robot_or_rdk_access": False,
    }
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        command,
        env=environment,
        text=True,
        check=False,
    )
    receipt["returncode"] = result.returncode
    receipt["status"] = (
        "COMPLETED_T23_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_T23_COLAB_LAUNCH"
    )
    receipt["output_json_exists"] = OUTPUT_JSON.is_file()
    receipt["output_archive_exists"] = OUTPUT_ARCHIVE.is_file()
    if OUTPUT_JSON.is_file():
        receipt["output_json_sha256"] = sha256(OUTPUT_JSON)
    if OUTPUT_ARCHIVE.is_file():
        receipt["output_archive_sha256"] = sha256(OUTPUT_ARCHIVE)
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
