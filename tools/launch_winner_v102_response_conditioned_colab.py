#!/usr/bin/env python3
"""Verify, install, and launch the one frozen Winner-v102 Colab run."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import tarfile


PACKAGE_SHA256 = "cbb6dd1ef5c68e013cbc8e0a29bdbb014cff476064f2ac763aedfeeba6b28017"
PACKAGE_BYTES = 59_176_688
PREREGISTRATION_SHA256 = (
    "819b89d80dcd03b30e88e3596e55c343c14c753575b1797996a9107867b388fe"
)
PACKAGE_CONTRACT_SHA256 = (
    "d4218997ab5bc75745c32c3e4b29adda82e5e7846adce82db0e52016c3909ea0"
)
BUNDLE_NAME = "winner_v102_hosted_bundle"
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
    parser.add_argument("--work-root", type=Path, default=Path("/content/winner_v102_work"))
    parser.add_argument(
        "--extract-root", type=Path, default=Path("/content/winner_v102_launch")
    )
    parser.add_argument(
        "--output-json", type=Path, default=Path("/content/winner_v102_result.json")
    )
    parser.add_argument(
        "--output-archive",
        type=Path,
        default=Path("/content/winner_v102_artifacts.tar.gz"),
    )
    parser.add_argument(
        "--launch-receipt",
        type=Path,
        default=Path("/content/winner_v102_launch_receipt.json"),
    )
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("Winner-v102 requires --hosted-gpu-authorized")
    package = args.package.resolve()
    for path in (
        args.work_root,
        args.extract_root,
        args.output_json,
        args.output_archive,
        args.launch_receipt,
    ):
        if path.exists():
            raise FileExistsError(f"Winner-v102 no-retry path exists: {path}")
    if package.stat().st_size != PACKAGE_BYTES or sha256(package) != PACKAGE_SHA256:
        raise ValueError("Winner-v102 uploaded package changed")

    args.extract_root.mkdir(parents=True)
    with tarfile.open(package, "r:gz") as archive:
        archive.extractall(args.extract_root, filter="data")
    bundle = args.extract_root / BUNDLE_NAME
    preregistration = (
        bundle
        / "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
    )
    if sha256(preregistration) != PREREGISTRATION_SHA256:
        raise ValueError("Winner-v102 extracted preregistration changed")

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
        raise RuntimeError(f"Winner-v102 pinned software install failed: {completed.returncode}")
    observed_versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if observed_versions != EXPECTED_VERSIONS:
        raise ValueError(
            f"Winner-v102 software versions changed: {observed_versions}"
        )

    driver = bundle / "colab_winner_v102_response_conditioned_curriculum.py"
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
        "schema_version": "winner_v102.colab_launch_receipt.v1",
        "status": "STARTING_WINNER_V102_HASH_FROZEN_GPU_CURRICULUM",
        "package": {
            "bytes": PACKAGE_BYTES,
            "sha256": PACKAGE_SHA256,
        },
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "package_contract_sha256": PACKAGE_CONTRACT_SHA256,
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
        "COMPLETED_WINNER_V102_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_WINNER_V102_COLAB_LAUNCH"
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
