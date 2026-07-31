#!/usr/bin/env python3
"""Execute T78's exact bundle in one fresh Colab L4 session."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile


PACKAGE = Path(
    "/content/t78-endpoint-joint-adapter-hosted-20260728.tar.gz"
)
PACKAGE_BYTES = 4_343_395
PACKAGE_SHA256 = (
    "87fe0a160a5b35d50cf462cc43611ac00c5ef186be49b588dbf137d6d7a56f97"
)
BUNDLE_NAME = "t78_endpoint_joint_adapter_bundle"
PREREGISTRATION_SHA256 = (
    "50f45ef0b6e65072213a2b5bf4da5de37413687bc5d22c4248d669c4d068d77f"
)
CPU_RESULT_SHA256 = (
    "1c15d29d3f8dcb041d50a1502010afe4dfe7684cd8a8a2f202035248bb5e8399"
)
PACKAGE_MANIFEST_SHA256 = (
    "e4d7bb26a4952d8a5c6b9cb258889f6575d55ac41d86dd21c679365e3426e80e"
)
DRIVER_SHA256 = (
    "41a39029098ae52cb93bcb26e7fbaea967a4f0d10f70c7ab3db93ae3a8cdc927"
)
BASE_DRIVER_SHA256 = (
    "a15ec26c3419d75b2b0417bfd3950947c7d1ae711a050ee33f967f8f1f1f01dd"
)
DRIVER_HELPER_SHA256 = (
    "09bbe4ab7ee42d7f77bb302d7fa8cab15b8734be97f5db80f912ad6619dd808f"
)
WORK = Path("/content/t78_work")
EXTRACT = Path("/content/t78_launch")
OUTPUT_JSON = Path("/content/t78_result.json")
OUTPUT_ARCHIVE = Path("/content/t78_artifacts.tar.gz")
RECEIPT = Path("/content/t78_launch_receipt.json")
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
        raise RuntimeError(f"T78 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (WORK, EXTRACT, OUTPUT_JSON, OUTPUT_ARCHIVE, RECEIPT):
        if path.exists():
            raise FileExistsError(f"T78 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
    ):
        raise ValueError("T78 uploaded package changed")

    EXTRACT.mkdir(parents=True)
    with tarfile.open(PACKAGE, "r:gz") as archive:
        if any(
            "/playground/.tmp/" in f"/{member.name}/"
            for member in archive.getmembers()
        ):
            raise ValueError("T78 package contains playground/.tmp")
        archive.extractall(EXTRACT, filter="data")
    bundle = EXTRACT / BUNDLE_NAME
    preregistration = (
        bundle / "t78_endpoint_joint_adapter_hosted_preregistration.json"
    )
    cpu_result = bundle / "t77_endpoint_joint_adapter_cpu_result.json"
    manifest = bundle / "t78_package_manifest.json"
    driver = bundle / "colab_t78_endpoint_joint_adapter_continuation.py"
    base_driver = (
        bundle / "colab_t32_action_margin_trainthrough_continuation.py"
    )
    helper = bundle / "colab_winner_v114_linear_torque_continuation.py"
    if (
        sha256(preregistration) != PREREGISTRATION_SHA256
        or sha256(cpu_result) != CPU_RESULT_SHA256
        or sha256(manifest) != PACKAGE_MANIFEST_SHA256
        or sha256(driver) != DRIVER_SHA256
        or sha256(base_driver) != BASE_DRIVER_SHA256
        or sha256(helper) != DRIVER_HELPER_SHA256
    ):
        raise ValueError("T78 extracted package identity changed")

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
        raise RuntimeError(f"T78 pinned install failed: {completed.returncode}")
    observed_versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if observed_versions != EXPECTED_VERSIONS:
        raise ValueError(f"T78 software versions changed: {observed_versions}")

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "playground")
    preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from playground.open_duck_mini_v2.joystick import Joystick; "
                "from pathlib import Path; "
                "text=Path('playground/playground/open_duck_mini_v2/runner.py')"
                ".read_text(encoding='utf-8'); "
                "assert 'winner_t77_endpoint_joint_adapter_continuation' "
                "in text; "
                "print('PASS_T78_HOSTED_IMPORT', Joystick.__name__)"
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
        or "PASS_T78_HOSTED_IMPORT Joystick"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T78 hosted import failed: {preflight.stdout}\n"
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
        "schema_version": "open_duck.t78_colab_launch_receipt.v1",
        "status": "STARTING_T78_HASH_FROZEN_GPU_CONTINUATION",
        "gpu": gpu.stdout.strip(),
        "package": {
            "bytes": PACKAGE_BYTES,
            "sha256": PACKAGE_SHA256,
            "temporary_cache_absent": True,
        },
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "cpu_result_sha256": CPU_RESULT_SHA256,
        "package_manifest_sha256": PACKAGE_MANIFEST_SHA256,
        "driver_sha256": DRIVER_SHA256,
        "base_driver_sha256": BASE_DRIVER_SHA256,
        "driver_helper_sha256": DRIVER_HELPER_SHA256,
        "hosted_import_preflight": "PASS_T78_HOSTED_IMPORT Joystick",
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
        "COMPLETED_T78_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_T78_COLAB_LAUNCH"
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
