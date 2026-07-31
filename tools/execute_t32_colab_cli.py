#!/usr/bin/env python3
"""Execute T32's exact bundle in one fresh Colab L4 session."""

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
    "/content/t32-action-margin-trainthrough-hosted-20260727.tar.gz"
)
PACKAGE_BYTES = 3_459_578
PACKAGE_SHA256 = (
    "4c0ffe0e5787eb4db12a6b3112b9f895b9bb736d2526c24daf31fe74689840ed"
)
BUNDLE_NAME = "t32_action_margin_trainthrough_bundle"
PREREGISTRATION_SHA256 = (
    "1fc70fa801d0793286f9b25a4736cb5bc087c06c3258f7aeabb92c24193b06a5"
)
CPU_RESULT_SHA256 = (
    "56496de136758bbcc36e0231535a72fe9de7ac93ab157ee89bbccfaabfe5d37d"
)
PACKAGE_MANIFEST_SHA256 = (
    "3bfa9da1cc8824638817304485168cdb1e632810dee2cc7251514733478770c7"
)
DRIVER_SHA256 = (
    "a15ec26c3419d75b2b0417bfd3950947c7d1ae711a050ee33f967f8f1f1f01dd"
)
DRIVER_HELPER_SHA256 = (
    "09bbe4ab7ee42d7f77bb302d7fa8cab15b8734be97f5db80f912ad6619dd808f"
)
WORK = Path("/content/t32_work")
EXTRACT = Path("/content/t32_launch")
OUTPUT_JSON = Path("/content/t32_result.json")
OUTPUT_ARCHIVE = Path("/content/t32_artifacts.tar.gz")
RECEIPT = Path("/content/t32_launch_receipt.json")
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
        raise RuntimeError(f"T32 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (WORK, EXTRACT, OUTPUT_JSON, OUTPUT_ARCHIVE, RECEIPT):
        if path.exists():
            raise FileExistsError(f"T32 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
    ):
        raise ValueError("T32 uploaded package changed")

    EXTRACT.mkdir(parents=True)
    with tarfile.open(PACKAGE, "r:gz") as archive:
        if any(
            "/playground/.tmp/" in f"/{member.name}/"
            for member in archive.getmembers()
        ):
            raise ValueError("T32 package contains playground/.tmp")
        archive.extractall(EXTRACT, filter="data")
    bundle = EXTRACT / BUNDLE_NAME
    preregistration = (
        bundle / "t32_action_margin_trainthrough_hosted_preregistration.json"
    )
    cpu_result = bundle / "t31_action_margin_trainthrough_cpu_result.json"
    manifest = bundle / "t32_package_manifest.json"
    driver = bundle / "colab_t32_action_margin_trainthrough_continuation.py"
    helper = bundle / "colab_winner_v114_linear_torque_continuation.py"
    if (
        sha256(preregistration) != PREREGISTRATION_SHA256
        or sha256(cpu_result) != CPU_RESULT_SHA256
        or sha256(manifest) != PACKAGE_MANIFEST_SHA256
        or sha256(driver) != DRIVER_SHA256
        or sha256(helper) != DRIVER_HELPER_SHA256
    ):
        raise ValueError("T32 extracted package identity changed")

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
        raise RuntimeError(f"T32 pinned install failed: {completed.returncode}")
    observed_versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if observed_versions != EXPECTED_VERSIONS:
        raise ValueError(f"T32 software versions changed: {observed_versions}")

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
                "assert 'winner_t31_action_margin_trainthrough' in text; "
                "print('PASS_T32_HOSTED_IMPORT', Joystick.__name__)"
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
        or "PASS_T32_HOSTED_IMPORT Joystick"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T32 hosted import failed: {preflight.stdout}\n"
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
        "schema_version": "open_duck.t32_colab_launch_receipt.v1",
        "status": "STARTING_T32_HASH_FROZEN_GPU_CONTINUATION",
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
        "driver_helper_sha256": DRIVER_HELPER_SHA256,
        "hosted_import_preflight": "PASS_T32_HOSTED_IMPORT Joystick",
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
        "COMPLETED_T32_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_T32_COLAB_LAUNCH"
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
