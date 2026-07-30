#!/usr/bin/env python3
"""Execute T194's exact package in one fresh Colab L4 session."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from typing import Any


PACKAGE = Path(
    "/content/t194-corrected-dynamic-support-20260730.tar.gz"
)
PACKAGE_BYTES = 4_340_170
PACKAGE_SHA256 = (
    "5e1ea887ec4fcfef81a82d209b033436a7e3cdf42e086fac182fa4ddf4a8c7c3"
)
BUNDLE_NAME = "t194_corrected_dynamic_reference_support_bundle"
MANIFEST_NAME = "t194_package_manifest.json"
MANIFEST_SHA256 = (
    "e839c443cc6dafe920e07c02f8a875b0ecfd484522caf6090398cc57d0ff2469"
)
WORK = Path("/content/t194_work")
EXTRACT = Path("/content/t194_launch")
OUTPUT_JSON = Path("/content/t194_result.json")
OUTPUT_ARCHIVE = Path("/content/t194_artifacts.tar.gz")
RECEIPT = Path("/content/t194_launch_receipt.json")
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


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_manifest(bundle: Path) -> dict[str, Any]:
    manifest_path = bundle / MANIFEST_NAME
    if sha256(manifest_path) != MANIFEST_SHA256:
        raise ValueError("T194 extracted manifest changed")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    members = manifest["members"]
    if (
        len(members) != manifest["member_count_excluding_manifest"]
        or canonical_sha256(members)
        != manifest["members_canonical_sha256"]
    ):
        raise ValueError("T194 manifest identity changed")
    for relative, expected in members.items():
        path = bundle / relative
        if (
            not path.is_file()
            or path.stat().st_size != expected["bytes"]
            or sha256(path) != expected["sha256"]
        ):
            raise ValueError(f"T194 bundle member changed: {relative}")
    return manifest


def main() -> int:
    gpu = subprocess.run(
        ["nvidia-smi", "-L"], capture_output=True, text=True, check=False
    )
    if gpu.returncode != 0 or "L4" not in gpu.stdout:
        raise RuntimeError(f"T194 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (WORK, EXTRACT, OUTPUT_JSON, OUTPUT_ARCHIVE, RECEIPT):
        if path.exists():
            raise FileExistsError(f"T194 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
    ):
        raise ValueError("T194 uploaded package changed")
    EXTRACT.mkdir(parents=True)
    with tarfile.open(PACKAGE, "r:gz") as archive:
        if any(
            "/playground/.tmp/" in f"/{member.name}/"
            for member in archive.getmembers()
        ):
            raise ValueError("T194 package contains playground/.tmp")
        archive.extractall(EXTRACT, filter="data")
    bundle = EXTRACT / BUNDLE_NAME
    manifest = verify_manifest(bundle)
    install = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--quiet",
            "--upgrade",
            *INSTALL_REQUIREMENTS,
        ],
        text=True,
        check=False,
    )
    if install.returncode != 0:
        raise RuntimeError(f"T194 pinned install failed: {install.returncode}")
    versions = {
        name: importlib.metadata.version(name)
        for name in EXPECTED_VERSIONS
    }
    if versions != EXPECTED_VERSIONS:
        raise ValueError(f"T194 software versions changed: {versions}")
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(bundle), str(bundle / "playground"))
    )
    preflight_source = "\n".join(
        (
            "from pathlib import Path",
            "import colab_t194_corrected_dynamic_reference_support_continuation as driver",
            "validation = driver.validate_inputs(Path('.'))",
            "assert validation['process_count'] == 1",
            "assert validation['devices']",
            "cmd = driver.runner_command(",
            "    Path('playground'), Path('out'),",
            "    Path('assets/source_checkpoint'),",
            "    Path('assets/ground_up_projected_reference_feature_table.npz'),",
            ")",
            "assert cmd.count('--winner_t193_corrected_dynamic_reference_support') == 1",
            "assert cmd.count('--winner_t98_hidden_expert_continuation') == 1",
            "assert cmd.count('--winner_t98_hidden_gate_asset_path') == 1",
            "assert cmd[cmd.index('--ppo_num_envs') + 1] == '256'",
            "assert cmd[cmd.index('--num_timesteps') + 1] == '2007040'",
            "runner = Path('playground/playground/open_duck_mini_v2/runner.py').read_text()",
            "assert 'T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT=' in runner",
            "assert 'T98_HIDDEN_EXPERT_CONTINUATION=' in runner",
            "print('PASS_T194_HOSTED_FULL_PREFLIGHT')",
        )
    )
    preflight = subprocess.run(
        [sys.executable, "-c", preflight_source],
        cwd=bundle,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if (
        preflight.returncode != 0
        or "PASS_T194_HOSTED_FULL_PREFLIGHT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T194 hosted preflight failed:\n{preflight.stdout}\n"
            f"{preflight.stderr}"
        )
    driver = bundle / "colab_t194_corrected_dynamic_reference_support_continuation.py"
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
        "schema_version": "open_duck.t194_colab_launch_receipt.v1",
        "status": "STARTING_T194_HASH_FROZEN_GPU_CONTINUATION",
        "gpu": gpu.stdout.strip(),
        "package": {"bytes": PACKAGE_BYTES, "sha256": PACKAGE_SHA256},
        "manifest_sha256": MANIFEST_SHA256,
        "member_count": manifest["member_count_excluding_manifest"],
        "software_versions": versions,
        "command": command,
        "retry": False,
        "same_run_resume": False,
        "robot_or_rdk_access": False,
    }
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    )
    result = subprocess.run(command, env=environment, text=True, check=False)
    receipt["returncode"] = result.returncode
    receipt["status"] = (
        "COMPLETED_T194_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_T194_COLAB_LAUNCH"
    )
    for name, path in (
        ("output_json", OUTPUT_JSON),
        ("output_archive", OUTPUT_ARCHIVE),
    ):
        receipt[f"{name}_exists"] = path.is_file()
        if path.is_file():
            receipt[f"{name}_sha256"] = sha256(path)
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
