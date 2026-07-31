#!/usr/bin/env python3
"""Execute T170's exact package in one fresh Colab L4 session."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile


PACKAGE = Path("/content/t170-eight-stratum-head-20260729.tar.gz")
PACKAGE_BYTES = 4_329_461
PACKAGE_SHA256 = (
    "1754a30f5b6bb6215f46045a6c0ebd858330c1c8134d41c53d5a37d2876753cd"
)
BUNDLE_NAME = "t170_eight_stratum_head_bundle"
PREREGISTRATION_SHA256 = (
    "0bac68fa7997fe22e071aa0307a05a5a83f974d413a805f39d5d444c251bd1bd"
)
CPU_RESULT_SHA256 = (
    "ae0bbefde5e606dfd63ca4d6ed94165aa0074b0cdf270491a277ada4a3e4ff5a"
)
DIAGNOSTIC_RESULT_SHA256 = (
    "00e379d1c458079c9f0c7f1c4be91a10fb48d8b654faf81c870bb312b7a8ceb6"
)
PACKAGE_MANIFEST_SHA256 = (
    "49672fc84ca42d9151b29c0dcbb752d543ca9bc306568fe283f16d68580d7499"
)
DRIVER_SHA256 = (
    "3b81a0db4ba3374a2341256860b78c42f4207a6d8ced8d606c4bd9395f1fa744"
)
BASE_DRIVER_SHA256 = (
    "41a39029098ae52cb93bcb26e7fbaea967a4f0d10f70c7ab3db93ae3a8cdc927"
)
T32_DRIVER_SHA256 = (
    "a15ec26c3419d75b2b0417bfd3950947c7d1ae711a050ee33f967f8f1f1f01dd"
)
HELPER_SHA256 = (
    "09bbe4ab7ee42d7f77bb302d7fa8cab15b8734be97f5db80f912ad6619dd808f"
)
WORK = Path("/content/t170_work")
EXTRACT = Path("/content/t170_launch")
OUTPUT_JSON = Path("/content/t170_result.json")
OUTPUT_ARCHIVE = Path("/content/t170_artifacts.tar.gz")
RECEIPT = Path("/content/t170_launch_receipt.json")
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
        ["nvidia-smi", "-L"], capture_output=True, text=True, check=False
    )
    if gpu.returncode != 0 or "L4" not in gpu.stdout:
        raise RuntimeError(f"T170 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (WORK, EXTRACT, OUTPUT_JSON, OUTPUT_ARCHIVE, RECEIPT):
        if path.exists():
            raise FileExistsError(f"T170 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
    ):
        raise ValueError("T170 uploaded package changed")
    EXTRACT.mkdir(parents=True)
    with tarfile.open(PACKAGE, "r:gz") as archive:
        if any(
            "/playground/.tmp/" in f"/{member.name}/"
            for member in archive.getmembers()
        ):
            raise ValueError("T170 package contains playground/.tmp")
        archive.extractall(EXTRACT, filter="data")
    bundle = EXTRACT / BUNDLE_NAME
    paths = (
        bundle / "t170_eight_stratum_head_hosted_preregistration.json",
        bundle / "t169_eight_stratum_head_continuation_cpu_result.json",
        bundle / "t169b_cpu_diagnostic_validity_result.json",
        bundle / "t170_package_manifest.json",
        bundle / "colab_t170_eight_stratum_head_continuation.py",
        bundle / "colab_t78_endpoint_joint_adapter_continuation.py",
        bundle / "colab_t32_action_margin_trainthrough_continuation.py",
        bundle / "colab_winner_v114_linear_torque_continuation.py",
    )
    observed = tuple(sha256(path) for path in paths)
    expected = (
        PREREGISTRATION_SHA256,
        CPU_RESULT_SHA256,
        DIAGNOSTIC_RESULT_SHA256,
        PACKAGE_MANIFEST_SHA256,
        DRIVER_SHA256,
        BASE_DRIVER_SHA256,
        T32_DRIVER_SHA256,
        HELPER_SHA256,
    )
    if observed != expected:
        raise ValueError("T170 extracted package identity changed")
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
        raise RuntimeError(f"T170 pinned install failed: {install.returncode}")
    versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if versions != EXPECTED_VERSIONS:
        raise ValueError(f"T170 software versions changed: {versions}")
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(bundle), str(bundle / "playground"))
    )
    preflight_source = "\n".join(
        (
            "from pathlib import Path",
            "import colab_t170_eight_stratum_head_continuation as driver",
            "validation = driver.validate_inputs(Path('.'))",
            "assert validation['process_count'] == 1",
            "assert validation['devices']",
            "cmd = driver.runner_command(",
            "    Path('playground'), Path('out'),",
            "    Path('assets/source_checkpoint'),",
            "    Path('assets/ground_up_projected_reference_feature_table.npz'),",
            ")",
            "assert cmd.count('--winner_t98_hidden_expert_continuation') == 1",
            "assert cmd.count('--winner_t98_hidden_gate_asset_path') == 1",
            "assert cmd[cmd.index('--ppo_num_envs') + 1] == '256'",
            "assert cmd[cmd.index('--num_timesteps') + 1] == '2007040'",
            "runner = Path('playground/playground/open_duck_mini_v2/runner.py').read_text()",
            "assert 'T98_HIDDEN_EXPERT_CONTINUATION=' in runner",
            "assert 'strata=8,broad=1,isolated=7,' in runner",
            "assert 'gate=fixed_live_hidden,' in runner",
            "print('PASS_T170_HOSTED_FULL_PREFLIGHT')",
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
        or "PASS_T170_HOSTED_FULL_PREFLIGHT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T170 hosted preflight failed:\n{preflight.stdout}\n"
            f"{preflight.stderr}"
        )
    driver = paths[4]
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
        "schema_version": "open_duck.t170_colab_launch_receipt.v1",
        "status": "STARTING_T170_HASH_FROZEN_GPU_CONTINUATION",
        "gpu": gpu.stdout.strip(),
        "package": {"bytes": PACKAGE_BYTES, "sha256": PACKAGE_SHA256},
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "cpu_result_sha256": CPU_RESULT_SHA256,
        "diagnostic_result_sha256": DIAGNOSTIC_RESULT_SHA256,
        "package_manifest_sha256": PACKAGE_MANIFEST_SHA256,
        "driver_sha256": DRIVER_SHA256,
        "base_driver_sha256": BASE_DRIVER_SHA256,
        "t32_driver_sha256": T32_DRIVER_SHA256,
        "helper_sha256": HELPER_SHA256,
        "software_versions": versions,
        "command": command,
        "retry": False,
        "same_run_resume": False,
        "robot_or_rdk_access": False,
    }
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n"
    )
    result = subprocess.run(command, env=environment, text=True, check=False)
    receipt["returncode"] = result.returncode
    receipt["status"] = (
        "COMPLETED_T170_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_T170_COLAB_LAUNCH"
    )
    for name, path in (
        ("output_json", OUTPUT_JSON),
        ("output_archive", OUTPUT_ARCHIVE),
    ):
        receipt[f"{name}_exists"] = path.is_file()
        if path.is_file():
            receipt[f"{name}_sha256"] = sha256(path)
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n"
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
